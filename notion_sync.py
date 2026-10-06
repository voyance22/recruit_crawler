"""사람인 검색 결과를 기존 Notion 지원 기록에 신규 등록합니다."""
import os
import re
import time
from datetime import datetime
from urllib.parse import parse_qs, urlparse
from zoneinfo import ZoneInfo

import requests


def link_key(link):
    parsed = urlparse(link)
    rec_idx = parse_qs(parsed.query).get('rec_idx')
    if parsed.hostname in ('www.saramin.co.kr', 'saramin.co.kr') and rec_idx:
        return 'saramin:' + rec_idx[0]
    return link


def employment_type(job):
    text = f"{job.get('title', '')} {job.get('work_type', '')}"
    if '일경험' in text:
        return '일경험'
    if '인턴' in text:
        if re.search(r'채용\s*전환형|정규직\s*전환형', text):
            return '인턴(채용전환형)'
        if '체험형' in text:
            return '인턴(체험형)'
        return '인턴(전환 여부 미확인)'
    types = [value for value in ('계약직', '정규직') if value in text]
    return types[0] if len(types) == 1 else '확인 필요'


def role(keyword):
    if keyword in ('교육운영', '연수운영', '교육지원'):
        return '교육운영'
    if keyword in ('인사', 'HR', '채용운영'):
        return '인사'
    if keyword in ('경영지원', '총무'):
        return keyword
    return '일반행정·운영지원'


def deadline_date(text):
    # 연도가 없는 MM/DD, 상시채용, 채용시 마감에는 날짜를 추정하지 않습니다.
    match = re.search(r'(20\d{2})[./-](\d{1,2})[./-](\d{1,2})', text or '')
    if match:
        try:
            return datetime(*map(int, match.groups())).date().isoformat()
        except ValueError:
            pass
    return None


def rich_text(value):
    return [{'text': {'content': str(value or '')[:2000]}}]


class NotionSync:
    def __init__(self, token, data_source_id):
        self.data_source_id = data_source_id
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'Notion-Version': '2025-09-03',
            'Content-Type': 'application/json',
        })

    @classmethod
    def from_environment(cls):
        token = os.environ.get('NOTION_TOKEN')
        data_source_id = os.environ.get('NOTION_DATA_SOURCE_ID')
        if not token or not data_source_id:
            print('ℹ️ 노션 미연결: NOTION_TOKEN과 NOTION_DATA_SOURCE_ID를 설정하세요.')
            return None
        return cls(token, data_source_id)

    def request(self, method, path, **kwargs):
        time.sleep(0.35)
        response = self.session.request(
            method, 'https://api.notion.com/v1/' + path, timeout=20, **kwargs)
        # 페이지 생성은 자동 재시도하지 않습니다. 응답 손실로 인한 중복 등록 방지.
        response.raise_for_status()
        return response.json()

    def sync(self, jobs):
        schema = self.request('GET', f'data_sources/{self.data_source_id}')['properties']
        required = {'기업명': 'title', '지원 링크': 'url'}
        for name, expected in required.items():
            if schema.get(name, {}).get('type') != expected:
                raise ValueError(f'노션에 {name}({expected}) 속성이 필요합니다.')

        known = set()
        cursor = None
        while True:
            payload = {'page_size': 100}
            if cursor:
                payload['start_cursor'] = cursor
            data = self.request('POST', f'data_sources/{self.data_source_id}/query', json=payload)
            for page in data['results']:
                link = page.get('properties', {}).get('지원 링크', {}).get('url')
                if link:
                    known.add(link_key(link))
            if not data.get('has_more'):
                break
            cursor = data['next_cursor']

        created = skipped = 0
        today = datetime.now(ZoneInfo('Asia/Seoul')).date().isoformat()
        for job in jobs:
            link = job.get('link')
            if not link or not job.get('title'):
                continue
            key = link_key(link)
            if key in known:
                skipped += 1
                continue
            properties = {
                '기업명': {'title': rich_text(job.get('company') or job['title'])},
                '지원 링크': {'url': link},
            }

            def optional(name, kind, value):
                prop = schema.get(name, {})
                if prop.get('type') != kind:
                    return
                if kind == 'select':
                    options = {item['name'] for item in prop['select']['options']}
                    if value['name'] not in options:
                        return
                properties[name] = {kind: value}

            optional('근무지', 'rich_text', rich_text(job.get('location')))
            optional('지원 직무', 'select', {'name': role(job.get('keyword'))})
            optional('채용 형태', 'select', {'name': employment_type(job)})
            optional('공고 상태', 'select', {'name': '검토 전'})
            optional('발견일', 'date', {'start': today})
            optional('주의점', 'rich_text', rich_text(
                '검색 결과 자동 수집. 직무는 검색어 기준이며 상세 업무·지원 자격 확인 필요. '
                f"마감 원문: {job.get('deadline') or '없음'}. 연도 없는 마감일은 날짜 미등록."))
            deadline = deadline_date(job.get('deadline'))
            if deadline:
                optional('전형 마감 일시', 'date', {'start': deadline})
            details = '\n'.join([
                f"공고명: {job['title']}",
                f"검색어: {job.get('keyword')}",
                f"경력: {job.get('career')}",
                f"학력: {job.get('education')}",
                f"고용 형태 원문: {job.get('work_type')}",
                f"마감 원문: {job.get('deadline')}",
                '상세 공고를 확인해 직무·채용 형태와 마감일을 확정하세요.',
            ])
            self.request('POST', 'pages', json={
                'parent': {'type': 'data_source_id', 'data_source_id': self.data_source_id},
                'properties': properties,
                'children': [{'object': 'block', 'type': 'paragraph',
                              'paragraph': {'rich_text': rich_text(details)}}],
            })
            known.add(key)
            created += 1
        print(f'📝 노션 신규 {created}개 등록, 기존 공고 {skipped}개 건너뜀')
        return {'created': created, 'skipped': skipped}
