# 개요

한국(KR) 주가 데이터를 가져오는 스크립트입니다.


## KR Day 데이터
네이버에서 한국 주식의 일자별 시세를 가져오는 스크립트입니다.

## KR Minute 데이터
네이버에서 한국 주식의 분단위 시세를 가져오는 스크립트입니다.


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
- 현재 프로젝트 경로를 기반으로 `ymarket.service` 생성
- 매 평일 18:00에 실행되는 `ymarket.timer` 등록 및 시작

## 수동 실행

필요한 경우 Docker Compose를 사용하여 즉시 실행할 수 있습니다.

```bash
docker compose run --rm app
```

## 볼륨 구성

- `/srv/ymarket`: 수집된 데이터(`day`, `minute` 폴더)가 저장되는 호스트 경로입니다.
