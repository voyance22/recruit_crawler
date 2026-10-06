# 채용공고 엑셀 수집기

서울·경기도에서 신입/경력무관/경력 필수가 아닌 인턴 공고를 수집합니다.
검색 직무는 교육운영·연수운영·교육지원·인사·HR·채용운영·경영지원·총무·일반행정·행정지원·사무행정입니다.

## 결과 보는 방법

GitHub의 Actions → 완료된 Recruit Crawler 실행 → Artifacts의 `recruitment-excel`을 다운로드하고 ZIP을 풀면 엑셀 파일이 있습니다.
`공고 목록` 시트에 회사·공고명·직무·지역·경력·채용 형태·마감 원문·원문 링크가 한 행씩 들어갑니다. 머리글 필터를 사용하고 검토 상태·메모 열에 기록하세요.
공고가 0개라도 엑셀 파일은 생성되며, 수집 로그와 함께 결과를 확인할 수 있습니다.

## 자동 실행

매일 한국 시간 오전 9시, 수동 Run workflow, 수집 코드 변경 시 실행합니다. GitHub 예약 실행은 지연될 수 있습니다.
새 실행은 진행 중인 이전 크롤러 실행을 중단합니다. 이를 위해 이 워크플로에만 Actions 쓰기 권한을 부여합니다.
노션 등록은 기본 비활성화이며 GitHub 실행에는 노션/이메일 비밀값을 전달하지 않습니다. 이미 등록된 노션 공고는 변경하거나 삭제하지 않습니다.

## 로컬 실행

```bash
git clone https://github.com/voyance22/recruit_crawler.git
cd recruit_crawler
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python saramin_crawler.py
```

Windows에서는 `venv\Scripts\python.exe -m pip install -r requirements.txt`와 `venv\Scripts\python.exe saramin_crawler.py`를 사용하세요.
결과 파일은 `output/` 폴더에 저장됩니다. 로컬에서 선택적으로 노션을 다시 사용할 때만 `.env.example`을 참고해 환경변수 `ENABLE_NOTION_SYNC=1`, `NOTION_TOKEN`, `NOTION_DATA_SOURCE_ID`를 설정하세요.

## 수집 범위와 주의점

사람인 키워드당 최대 5페이지를 수집합니다. 검색 결과 근무지에서 서울/경기 여부를, 경력 조건에서 신입/경력무관 여부를 확인합니다. 경력 필수 인턴은 제외합니다. 사이트 검색 결과의 요약 정보 기준이며 상세 공고를 전부 분석하는 것은 아닙니다.
직무는 검색어 기준의 임시 분류입니다. 연도가 없는 마감일은 원문 그대로 보관하고, 인턴 전환 여부가 명확하지 않으면 미확인으로 표시합니다. 사이트 응답 오류가 나면 로그를 확인하세요.

[원본 프로젝트](https://github.com/yujeong0411/recruit_crawler) · [MIT License](LICENSE)
