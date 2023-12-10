# pyrb - Python Rebalancer

![Python](https://img.shields.io/badge/Python-v3.11-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Supported Brokerages](https://img.shields.io/badge/Supported%20Brokerages-EBest-orange)

`pyrb`는 주식 포트폴리오 리밸런싱을 자동화하기 위한 커맨드라인 인터페이스(CLI) 도구입니다.
파이썬으로 제작되었으며, 증권사 API를 통해 자산 배분을 위한 매매 과정을 자동화합니다.

## 주요 기능

- 자산 배분을 위한 포트폴리오 분석
- 포트폴리오 리밸런싱을 위한 주문 실행
- 다양한 증권사 지원을 위한 플러그 앤 플레이 아키텍처
  - 현재는 EBest 증권사만 지원

## 설치 방법

Pip 혹은 Poetry로 `pyrb`를 직접 설치할 수 있습니다:

- Pip

  ```bash
  pip install pyrb
  ```

- Poetry

  ```bash
  poetry add pyrb
  ```

또는, 저장소를 클론하고 수동으로 설치하세요:

```bash
git clone https://github.com/mingi3314/pyrb.git
cd pyrb
pip install .
```

## 사용 방법

### 1. 계좌 연동하기

현재는 Ebest 계좌만 연동이 가능하며, API 연동을 위해 고유 토큰(APP_KEY, APP_SECRET)을 입력해야 합니다.
만약 아직 토큰을 발급받지 않으셨다면, 아래 링크를 참고해주세요.
<https://openapi.ebestsec.co.kr/howto-use>

아래 명령어를 입력하여 증권사 계좌를 설정해주세요.

```bash
pyrb account set
```

```bash
>>> App key: <enter your app key>
>>> App secret: <enter your app secret>
```

### 2. 실행하기

아래 예시를 따라, 올웨더 포트폴리오 전략을 사용해 포트폴리오를 리밸런싱할 수 있습니다.

```bash
pyrb asset-allocate --strategy all-weather-kr --investment-amount <amount-you-want-to-invest>
```

위 명령어를 입력하면, 시스템은 올웨더 포트폴리오를 구성하기 위해 필요한 주문을 자동으로 산출합니다.
그 후, 해당 주문들을 제출할 것인지 사용자에게 확인을 요청합니다.

사용자는 아래와 같은 주문 후보들을 검토한 후, 'y'버튼을 클릭하여 주문을 제출할 수 있습니다.

```bash
┏━━━━━━━━┳━━━━━━┳━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Symbol ┃ Side ┃ Quantity ┃ Price ┃ Total Amount ┃ Current position value ┃ Expected position value ┃
┡━━━━━━━━╇━━━━━━╇━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 379800 │ BUY  │ 378      │ 13545 │ 5120010      │ 1868930.0              │ 6988940.0               │
│ 361580 │ BUY  │ 278      │ 18265 │ 5077670      │ 1917538.0              │ 6995208.0               │
│ 411060 │ BUY  │ 370      │ 12200 │ 4514000      │ 1475979.0              │ 5989979.0               │
│ 365780 │ BUY  │ 58       │ 88755 │ 5147790      │ 1774834.0              │ 6922624.0               │
│ 308620 │ BUY  │ 476      │ 10945 │ 5209820      │ 1783768.0              │ 6993588.0               │
│ 272580 │ BUY  │ 85       │ 52995 │ 4504575      │ 1483638.0              │ 5988213.0               │
└────────┴──────┴──────────┴───────┴──────────────┴────────────────────────┴─────────────────────────┘

Do you want to place these orders? [y/N]: 
```

### 3. 포트폴리오 확인하기

다음 명령어로 포트폴리오를 확인할 수 있습니다:

```bash
pyrb portfolio
```

## 개발

이 프로젝트는 Python 3.11과 Typer를 사용하여 CLI 인터페이스로 구축되었습니다. 현재는 EBest 증권사를 특별히 지원하고 있지만, 향후 추가 증권사를 지원할 수 있도록 플러그 앤 플레이 아키텍처로 설계되었습니다.

개발 환경을 설정하기 위해, 저장소를 클론하고 종속성을 설치하세요:

```bash
git clone https://github.com/yourusername/pyrb.git
cd pyrb
poetry install --sync
```

### 테스트 실행하기

다음 명령어로 테스트를 실행할 수 있습니다:

```bash
pytest
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
