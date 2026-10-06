# 🧑‍💻 채용공고 자동 크롤러

사람인(Saramin) 채용공고를 자동으로 수집하고, CSV 저장 및 이메일 알림까지 지원하는 파이썬 크롤러입니다.  
특정 키워드, 연봉, 회사 유형, 고용 형태 등 다양한 조건을 설정하여 원하는 채용공고만 수집할 수 있습니다.  

<br/>
<br/>

## ✨ 주요 기능
- ✅ **사람인 채용공고 자동 크롤링**
- ✅ **검색 필터 적용 가능** (연봉, 회사 유형, 고용 형태, 근무일, 재택 여부 등)
- ✅ **최대 5페이지 크롤링 (중복 제거 포함)**
- ✅ **결과 CSV 저장** (공고 제목, 회사명, 마감일, 지역, 학력, 경력, 링크 등)
- ✅ **이메일 알림 기능** (주요 공고 미리보기 + CSV 첨부)


<br/>
<br/>

## 🛠️ 설치 방법

### 1. 저장소 클론
```bash
git clone https://github.com/voyance22/recruit_crawler.git
cd recruit_crawler
```
<br/>

### 2. 가상환경 (선택)
```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```
<br/>

### 3. 패키지 설치
```bash
pip install -r requirements.txt
```
#### 📦 requirements.txt 
```bash
requests
beautifulsoup4
pandas
```


<br/>
<br/>

## 🚀 사용법

### 1. 기본 실행
```bash
python saramin_crawler.py
```
교육운영·연수운영·교육지원·인사·HR·채용운영·경영지원·총무·일반행정·행정지원·사무행정을 검색합니다. CSV 저장 후 노션 설정이 있으면 신규 공고를 등록합니다. 이메일은 설정이 모두 있을 때만 발송합니다.
<br/>

### 2. 원하는 조건으로 직접 검색
```bash
from saramin_crawler import SaraminCrawler

crawler = SaraminCrawler()

jobs = crawler.search_jobs(
    keyword="데이터 분석",
    salary_min="3000만원~",
    company_types=["대기업", "중견기업"],
    job_types=["정규직"],
    work_days=["주5일"],
    exclude_keywords=["학교"]
)
```
<br/>

### 3. 이메일 설정
이 프로젝트는 이메일 알림 기능을 위해 3가지 환경변수를 사용합니다:
- `EMAIL_SENDER` : 발신자 이메일 주소 (예: `내메일@gmail.com`)
- `EMAIL_RECEIVER` : 수신자 이메일 주소
- `EMAIL_APP_PASSWORD` : 구글 앱 비밀번호 (일반 계정 비밀번호가 아님!)

> 👉 보안상 코드에 직접 적지 말고, 환경변수 또는 GitHub Actions secrets에 저장하세요.

#### 3-1. Windows CMD
```bash
set EMAIL_SENDER=내메일@gmail.com
set EMAIL_RECEIVER=내메일@gmail.com
set EMAIL_APP_PASSWORD=앱비밀번호
```

#### 3-2. Windows PowerShell
```bash
$env:EMAIL_SENDER="내메일@gmail.com"
$env:EMAIL_RECEIVER="받는사람@gmail.com"
$env:EMAIL_APP_PASSWORD="앱비밀번호"
```

#### 3-3. Mac/Linux
```bash
export EMAIL_SENDER="내메일@gmail.com"
export EMAIL_RECEIVER="받는사람@gmail.com"
export EMAIL_APP_PASSWORD="앱비밀번호"
```

#### 3-4. GitHub Actions Secrets (현재 방식)
GitHub 저장소 → Settings → Secrets and variables → Actions → New repository secret

아래 세 가지를 등록:
- EMAIL_SENDER
- EMAIL_RECEIVER
- EMAIL_APP_PASSWORD

워크플로우에서 자동으로 사용됩니다:
```bash
name: Recruit Crawler

on:
  schedule:
    - cron: "0 0 * * *" # 매일 0시(UTC) 실행 → 한국 시간은 오전 9시
  workflow_dispatch: # 필요 시 수동 실행 버튼도 활성화

jobs:
  run-crawler:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"

      - name: Install dependencies
        run: |
          pip install requests beautifulsoup4 pandas

      - name: Run crawler
        env:
          EMAIL_SENDER: ${{ secrets.EMAIL_SENDER }}
          EMAIL_RECEIVER: ${{ secrets.EMAIL_RECEIVER }}
          EMAIL_APP_PASSWORD: ${{ secrets.EMAIL_APP_PASSWORD }}
        run: python saramin_crawler.py

```


<br/>
<br/>

## 📊 결과 예시
![csv](docs/csv_example.png)
![email01](docs/email_example.png)
![email01](docs/email_example2.png)

<br/>
<br/>

## ⚠️ 주의사항

사람인 사이트 구조나 API가 바뀌면 코드가 작동하지 않을 수 있습니다.

단기간에 과도한 요청은 차단될 수 있으므로, 크롤링 시 time.sleep(1) 을 유지하세요.

이메일 기능은 Gmail 기준이며, 타 이메일 서비스는 설정이 다를 수 있습니다.

<br/>
<br/>

## 📌 라이선스
이 프로젝트는 [MIT License](./LICENSE)를 따릅니다.


## 노션 자동 등록 설정

ChatGPT의 노션 연결과 Python 프로그램의 인증은 별개입니다.

1. https://www.notion.so/profile/integrations 에서 내부 통합을 만들고 읽기·삽입 권한을 설정합니다.
2. 등록할 `지원 기록` 데이터베이스에서 해당 통합을 연결해 접근 권한을 부여합니다.
3. `.env.example`을 `.env`로 복사해 `NOTION_TOKEN`을 입력합니다. 토큰은 채팅이나 Git에 올리지 마세요.
4. `NOTION_DATA_SOURCE_ID`를 확인합니다. 등록할 표의 데이터 소스 ID를 입력하세요. 비슷한 이름의 복사본과 구분하세요.
5. Linux/Mac에서 다음 명령으로 실행합니다.

```bash
source venv/bin/activate
set -a
source .env
set +a
python saramin_crawler.py
```

Windows PowerShell은 `.env`를 자동으로 읽지 않습니다. 환경변수로 직접 설정하세요.

```powershell
$env:NOTION_TOKEN="내부 통합 토큰"
$env:NOTION_DATA_SOURCE_ID="데이터 소스 ID"
.\venv\Scripts\python.exe saramin_crawler.py
```

GitHub Actions에서 실행하려면 저장소 Secrets에 `NOTION_TOKEN`, `NOTION_DATA_SOURCE_ID`를 추가하세요. 로컬 `.env`는 Actions에 전달되지 않습니다. 현재 변경 사항을 저장소에 반영해야 Actions에서도 적용됩니다.

노션에 필수 속성 `기업명`(제목), `지원 링크`(URL)가 있어야 합니다. 기존 `지원 기록`의 근무지·지원 직무·채용 형태·발견일·주의점·공고 상태·전형 마감 일시 속성도 형식이 맞으면 채웁니다. 기존 공고는 링크(사람인 공고 ID)로 식별해 건너뛰므로 사용자가 작성한 지원 상태나 메모를 덮어쓰지 않습니다.

직무는 검색어에 따른 임시 분류이며 적합성 평가는 아닙니다. 인턴은 전환 여부가 명시되지 않으면 `인턴(전환 여부 미확인)`으로 등록합니다. 연도 없는 마감일은 추정하지 않고 본문에 원문을 보관합니다. 우선순위와 상세 지원 자격은 원문을 확인해야 합니다. 노션 실패 시에도 CSV는 먼저 저장됩니다. Google Calendar 등록 기능은 포함하지 않습니다.

주석 처리란 Python 줄 앞의 `#`로 실행을 막는 것입니다. CSV 저장 호출은 `filename = self.save_to_csv(unique_jobs)`로 활성화했습니다. 설명용 주석은 그대로 둡니다.

실제 사람인 수집은 네트워크와 사이트 응답에 따라 달라집니다. 요청 제한시간은 20초이며 페이지 사이에 1초 대기합니다. 패키지 설치만으로 실제 사이트 연동 성공을 보장하지 않습니다.
