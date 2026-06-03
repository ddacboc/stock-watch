# 곡괭이 워치 대시보드 — 설치 안내

트레이딩뷰엔 없는 "내 목표가까지 거리 + 관찰지표 + 매수권"을 한 화면에 모은 커스텀 대시보드입니다.
서버를 24시간 켤 필요 없이, **GitHub Actions가 3시간마다 가격을 받아 저장**하고, **GitHub Pages가 무료로 페이지를 띄웁니다.** 월 비용 사실상 0원.

## 작동 원리
- `fetch_prices.py` : 3시간마다 Finnhub 무료 API로 현재가를 받아 `data.json`에 누적
- `.github/workflows/update.yml` : 3시간 cron으로 위 스크립트를 자동 실행하고 결과를 커밋
- `index.html` : `config.json`(종목·관찰지표) + `data.json`(가격)을 읽어 표로 표시. 목표가·메모는 브라우저에 저장.
- 추이선은 별도 과거데이터 API 없이, **3시간마다 쌓인 값으로 직접** 그립니다(처음엔 짧고 점점 길어짐).

## 파일 구조 (그대로 깃 저장소에 두세요)
```
(저장소 루트)
├─ index.html
├─ config.json
├─ data.json            ← 처음엔 없어도 됨. Actions가 자동 생성
├─ fetch_prices.py
└─ .github/
   └─ workflows/
      └─ update.yml
```

## 설치 단계

### 1) 무료 Finnhub API 키 발급
1. finnhub.io 가입(무료)
2. 대시보드에서 API key 복사

### 2) GitHub 저장소 만들고 파일 올리기
1. github.com 에서 새 저장소 생성 (Public 권장 — Pages 무료)
2. 위 4개 파일을 같은 구조로 업로드 (`update.yml`은 반드시 `.github/workflows/` 안에)

### 3) API 키를 Secret으로 등록
저장소 → Settings → Secrets and variables → Actions → New repository secret
- Name: `FINNHUB_KEY`
- Secret: 발급받은 키 붙여넣기

### 4) Actions 켜고 첫 실행
1. 저장소 → Actions 탭 → 워크플로 활성화
2. `update-prices` 워크플로 → `Run workflow`(수동 실행)로 첫 데이터 생성
3. 잠시 후 `data.json`이 생기고, 이후 3시간마다 자동 갱신됨

### 5) GitHub Pages로 페이지 띄우기
저장소 → Settings → Pages → Source를 `main` 브랜치 루트로 지정 → 저장
→ 몇 분 뒤 `https://(아이디).github.io/(저장소명)/` 에서 대시보드가 열립니다.

## 쓰는 법
- 종목 행의 **목표가** 칸에 사고 싶은 가격을 입력 → 자동으로 "목표 대비 %"와 매수권(녹색)이 표시되고, 추이선에 목표 라인이 그어집니다.
- **메모** 칸에 매수 근거를 적어두면 저장됩니다.
- 티커를 누르면 Yahoo Finance 실시간 시세로 이동합니다.

## 알아둘 점
- **초단위 실시간 아님** — 3시간 주기. 분할 매수·장기 관점엔 충분합니다.
- **도쿄(6324.T 등)·스위스(LONN.SW)** 는 무료 API 미지원이라 `config.json`에서 `fetch:false`로 두었고, 화면엔 "수동"으로 표시됩니다. Yahoo 링크로 직접 확인하세요.
- 종목을 바꾸려면 `config.json`의 `rows`를 편집하면 됩니다.
- Finnhub 무료 티어는 분당 호출 제한이 있어 스크립트가 1초 간격으로 부릅니다(3시간에 한 번이라 문제 없음).
- GitHub Actions의 schedule cron은 트래픽 상황에 따라 몇 분~십몇 분 늦게 돌 수 있습니다(정상).

## 한계 / 다음 단계
- 진짜 초단위 실시간이나 도쿄·스위스 자동수집이 필요해지면 유료 데이터 피드가 필요합니다.
- 그 단계에선 이 구조 위에 데이터 소스만 교체하면 됩니다.

이 도구는 정보 정리용이며 투자자문이 아닙니다.
