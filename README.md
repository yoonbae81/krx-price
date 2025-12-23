# 개요

한국(KR) 주가 데이터를 가져오는 스크립트입니다.


## KR Day 데이터
네이버에서 한국 주식의 일자별 시세를 가져오는 스크립트입니다.

## KR Minute 데이터
네이버에서 한국 주식의 분단위 시세를 가져오는 스크립트입니다.


# 개발 환경 설정

## 자동 설정 (권장)

프로젝트는 개발 환경을 자동으로 설정하는 **`setup-dev` 스크립트**를 제공합니다.

이 스크립트는 다음 작업을 자동으로 수행합니다:
- ✅ Python 가상환경 생성 (`.venv`)
- ✅ pip 업그레이드
- ✅ 프로젝트 의존성 설치 (`requirements.txt`)
- ✅ 테스트 실행으로 설정 검증

### Windows
```bash
# 개발 환경 자동 설정
scripts\setup-dev.bat

# 가상환경 활성화
.venv\Scripts\activate.bat

# 테스트 실행
python -m unittest discover tests -v
```

### Linux/macOS
```bash
# 실행 권한 부여 (최초 1회)
chmod +x scripts/*.sh

# 개발 환경 자동 설정
./scripts/setup-dev.sh

# 가상환경 활성화
source .venv/bin/activate

# 테스트 실행
python -m unittest discover tests -v
```

## 수동 설정

`setup-dev` 스크립트를 사용하지 않고 수동으로 설정할 수도 있습니다.

1. **가상환경 생성**:
   ```bash
   python -m venv .venv
   ```

2. **가상환경 활성화**:
   - Windows: `.venv\Scripts\activate.bat`
   - Linux/macOS: `source .venv/bin/activate`

3. **의존성 설치**:
   ```bash
   pip install -r requirements.txt
   ```


# 테스트

이 프로젝트는 **55개의 테스트**를 포함합니다:
- **47개 Unit Tests**: Mock을 사용한 빠른 단위 테스트
- **8개 Integration Tests**: 실제 API를 호출하는 통합 테스트

## 테스트 실행

### 모든 테스트 실행
```bash
python -m unittest discover tests -v
```

### Unit 테스트만 실행 (빠름, 네트워크 불필요)
```bash
python -m unittest tests.test_symbol tests.test_day tests.test_minute -v
```

### Integration 테스트만 실행 (실제 API 호출)
```bash
python -m unittest tests.test_integration -v

# 또는 직접 실행
python tests/test_integration.py
```

자세한 테스트 정보는 [`tests/README.md`](tests/README.md)를 참조하세요.


# Docker & 시스템 설정

이 프로젝트는 Docker를 활용하여 데이터를 수집하며, 호스트 시스템의 **systemd timer**를 통해 정해진 시간에 자동으로 실행됩니다.

## 주요 변경 사항

- **Docker Run**: Docker 컨테이너는 상주하지 않고, 실행 시 수집 태스크를 수행한 후 즉시 종료됩니다.
- **Systemd Timer**: 기존 내부 `supercronic` 방식 대신, 외부(호스트)의 systemd timer가 실행 스케줄을 관리합니다.

## 시스템 설정 (systemd)

제공된 스크립트를 사용하여 서비스와 타이머를 자동으로 등록할 수 있습니다.

1.  **권한 부여** (필요한 경우):
    ```bash
    chmod +x scripts/setup-systemd.sh
    ```
2.  **설정 스크립트 실행**:
    ```bash
    sudo ./scripts/setup-systemd.sh
    ```

이 스크립트는 다음과 같은 작업을 수행합니다:
- 현재 프로젝트 경로를 기반으로 `krx-price.service` 생성
- 매 평일 17:00에 실행되는 `krx-price.timer` 등록 및 시작

## 수동 실행

필요한 경우 Docker Compose를 사용하여 즉시 실행할 수 있습니다.

```bash
docker compose run --rm app
```

## 볼륨 구성

- `/srv/krx-price`: 수집된 데이터(`day`, `minute` 폴더)가 저장되는 호스트 경로입니다.


# 프로젝트 구조

```
krx-price/
├── src/                    # 소스 코드
│   ├── symbol.py          # 심볼 수집
│   ├── day.py             # 일별 데이터 수집
│   └── minute.py          # 분봉 데이터 수집
├── tests/                  # 테스트 코드
│   ├── test_symbol.py     # symbol.py 단위 테스트
│   ├── test_day.py        # day.py 단위 테스트
│   ├── test_minute.py     # minute.py 단위 테스트
│   ├── test_integration.py # 통합 테스트 (실제 API)
│   └── README.md          # 테스트 문서
├── scripts/                # 유틸리티 스크립트
│   ├── setup-dev.sh/bat   # 개발 환경 설정
│   └── setup-systemd.sh   # Systemd 설정
├── requirements.txt        # Python 의존성
├── Dockerfile             # Docker 이미지 정의
└── docker-compose.yml     # Docker Compose 설정
```
