# 주가 데이터 수집기

한국 주식 시장의 주가 데이터를 자동으로 수집하고 관리하기 위한 파이썬 기반 도구입니다.

> [!CAUTION]
> ### 법적·이용 주의사항 (중요)
> *   **목적**: 본 프로젝트는 **개인 학습 및 비영리 목적**으로만 사용하시기를 권장합니다.
> *   **설계**: Daum 주가코드 조회 및 Naver 주가 데이터(OHLCV) 수집을 위한 개인 개발 도구로 설계되었습니다.
> *   **책임**: 상업적 거래, 알고리즘 트레이딩, 영리 목적 이용 등 금융투자업법 및 서비스 이용약관 위반시 **모든 법적 책임은 사용자 본인**에게 있습니다.
> *   **권장**: KRX 정식 데이터 서비스 이용을 강력히 권장합니다.
> *   **성격**: 본 프로젝트는 공식 API가 아닌 **개인 크롤링 스크립트**입니다.

---

## 🚀 주요 기능

### 1. KR Symbol 관리
*   KOSPI 및 KOSDAQ 시장의 전 종목 심볼 정보 수집
*   데이터 수집 대상 리스트 자동 업데이트

### 2. 일별 시세 수집 (Day Data)
*   네이버 금융을 통한 한국 주식의 일자별 OHLCV 데이터 수집
*   지정된 날짜의 종가, 시가, 고가, 저가, 거래량 기록

### 3. 분 단위 시세 수집 (Minute Data)
*   일중 분 단위 시세 수집 및 데이터 중복 제거 로직 포함
*   고빈도 데이터 분석을 위한 기반 데이터 제공

---

## 📂 프로젝트 구조

```text
krx-price/
├── src/                    # 📦 핵심 비즈니스 로직
│   ├── symbol.py          # 종목 심볼 수집 및 관리
│   ├── day.py             # 일별 OHLCV 데이터 수집
│   └── minute.py          # 분 단위 데이터 수집
├── tests/                  # 🧪 테스트 스위트
│   ├── test_symbol.py     # 심볼 수집 로직 단위 테스트
│   ├── test_day.py        # 일별 데이터 수집 단위 테스트
│   ├── test_minute.py     # 분 단위 데이터 수집 단위 테스트
│   ├── test_integration.py # 실제 API 호출 통합 테스트
│   └── README.md          # 상세 테스트 가이드
├── scripts/                # 🛠️ 유틸리티 스크립트
│   ├── setup-dev.sh/bat   # 개발 환경 자동 설정
│   └── deploy.sh          # Linux 배포 및 systemd 스케줄러 설정
├── requirements.txt        # 📝 의존성 패키지 목록
├── Dockerfile             # 🐳 Docker 이미지 빌드 설정
└── docker-compose.yml     # 🚢 컨테이너 실행 및 볼륨 설정
```

---

## ⚙️ 개발 환경 설정

### 1. 자동 설정 (권장)

`setup-dev` 스크립트를 사용하여 가상환경 생성부터 의존성 설치까지 한 번에 완료할 수 있습니다.

| OS | 명령어 |
| :--- | :--- |
| **Windows** | `scripts\setup-dev.bat` |
| **Linux/macOS** | `chmod +x scripts/*.sh && ./scripts/setup-dev.sh` |

> [!NOTE]
> 스크립트 실행 후 가상환경을 활성화해야 합니다:
> *   Windows: `.venv\Scripts\activate.bat`
> *   Linux/macOS: `source .venv/bin/activate`

### 2. 수동 설정
```bash
python -m venv .venv
# (가상환경 활성화 후)
pip install -r requirements.txt
```

---

## 🧪 테스트 실행

본 프로젝트는 총 **55개의 테스트 케이스**를 포함하고 있습니다.

*   **전체 테스트 실행**: `python -m unittest discover tests -v`
*   **단위 테스트 (Mock)**: `python -m unittest tests.test_symbol tests.test_day tests.test_minute -v`
*   **통합 테스트 (Real API)**: `python -m unittest tests.test_integration -v`

---

## 🐳 Docker & 배포

이 프로젝트는 Docker 컨테이너와 호스트의 **systemd timer**를 연동하여 자동 수집 환경을 구축합니다.

### 1. 배포 및 시스템 자동화 설정 (Linux)
제공된 배포 스크립트를 통해 소스 코드 복사, Docker 빌드, 서비스/타이머 등록이 한 번에 진행됩니다. 이 프로젝트는 `systemd --user` 모드를 사용하므로 루트 권한 없이(sudo 제외) 관리 가능합니다.
```bash
# 실행 전 실행 권한 부여
chmod +x scripts/deploy.sh
# 배포 스크립트 실행
./scripts/deploy.sh
```
*   **스케줄**: 매 평일(월-금) 17:00에 자동 실행
*   **사용자 모드**: 서비스는 `~/.config/systemd/user/`에 등록되며, `loginctl enable-linger`가 자동으로 설정되어 로그아웃 후에도 타이머가 동작합니다.
*   **상태 확인**: `systemctl --user status krx-price.timer`

### 2. 수동 실행
```bash
# 호스트 사용자의 UID/GID를 연동하여 실행 (파일 권한 유지)
APP_UID=$(id -u) APP_GID=$(id -g) docker compose run --rm app
```

---

## 💾 데이터 관리

*   **저장 경로**: 호스트의 `/srv/krx-price` 경로에 데이터가 저장됩니다.
*   **디렉토리 구조**:
    *   `/srv/krx-price/day`: 일별 데이터
    *   `/srv/krx-price/minute`: 분 단위 데이터
*   **볼륨 설정**: `docker-compose.yml`을 통해 호스트 경로와 컨테이너 내부 경로가 동기화됩니다. (`APP_UID`, `APP_GID` 환경 변수를 통해 호스트 사용자의 권한으로 파일이 생성됩니다.)
