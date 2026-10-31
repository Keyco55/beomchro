# ⚡ BEOMCHRO (범크로) v2.0
> **놀티켓 초고속 대기열 진입 하이브리드 엔진**  
> *Nol-Ticket Ultra Fast 0ms Queue Interceptor Engine*

---

## 1. 프로젝트 개요

BEOMCHRO(범크로)는 고부하 대규모 티켓팅 오픈 정각(00.000초) 시 인간의 신체적 반응 속도 한계(300~400ms)를 극복하고, **0~1ms 미만**으로 대기열 진입 버튼을 가로채 최선두 대기 순번(1번 대기)을 선점하기 위한 크로스 플랫폼 하이브리드 자동화 시스템입니다.

- **브라우저 0ms DOM 인터셉터**: `MutationObserver` 기반 마이크로초 단위 속성 변화 감지 및 격발
- **OS 네이티브 하드웨어 레벨 이벤트 주입**:
  - **macOS**: `Quartz.CoreGraphics` 네이티브 C-API 마우스 이벤트
  - **Windows**: `ctypes.windll.user32.SendInput` 기반 커널 레벨 마우스 이벤트 (0.1ms 지연)
- **밀리초(ms) 시계 & 서버 시간 오차(Time Skew) 실시간 보정**
- **1:1 놀티켓 복제 로컬 연습 시뮬레이터 & 반응속도 측정기** 내장

---

## 2. 파일 및 디렉터리 구조

```text
beomchro/
├── beomchro_core.py          # 모던 Rich TUI 메인 컨트롤러 (서버 + 네이티브 클릭 + 정각 타이머)
├── beomchro_queue.user.js    # Tampermonkey / Violentmonkey용 0ms 자동 인젝션 유저스크립트
├── run_mac.sh                # macOS 원클릭 가상환경 구성 및 실행 스크립트
├── run_windows.bat           # Windows 원클릭 실행 배치파일
├── requirements.txt          # 의존성 패키지 명세
├── .gitignore                # Git 제외 파일 목록
├── TASK_PROMPT.md            # 시스템 설계 및 구축 명세서
└── simulator/                # 1:1 놀티켓 모의 연습장 & 벤치마크 웹앱
    ├── index.html            # 놀티켓 예매 인터페이스 클론
    ├── style.css             # 네온 다크 테마 & 글래스모피즘 스타일링
    └── script.js             # 반응속도(ms) 측정 및 가상 대기열 순번 산출 엔진
```

---

## 3. 빠른 시작 (Quick Start)

### 🍎 macOS
```bash
# 원클릭 실행 (가상환경 및 패키지 자동 설치)
./run_mac.sh
```

### 🪟 Windows
```cmd
# 더블 클릭 또는 CMD에서 실행
run_windows.bat
```

---

## 4. 유저스크립트 (0ms 인젝터) 설치 방법

1. 브라우저(Chrome / Edge / Whale 등)에 **Tampermonkey** 또는 **Violentmonkey** 확장 프로그램을 설치합니다.
2. 새 스크립트 추가를 누른 후 `beomchro_queue.user.js`의 전체 내용을 복사하여 붙여넣고 저장합니다.
3. 로컬 시뮬레이터(`http://localhost:8989`) 또는 실제 놀티켓 예매 페이지에 접속하면 화면 우측 상단에 `⚡ BEOMCHRO 0ms READY` HUD 배너가 활성화됩니다.
4. 버튼이 오픈되는 순간 0.1ms 이내로 즉시 격발되어 1번 대기를 선점합니다.

---

## 5. TUI 대시보드 주요 기능

```text
1. 🚀 로컬 연습 시뮬레이터 구동 & 브라우저 열기 (http://localhost:8989)
2. 🎯 화면 픽셀 색상 감시 모드 (Pixel Color Watcher)
3. ⏰ 서버 시간 정각 자동 클릭 모드 (Exact Time Trigger)
4. ⚡ 마우스 초고속 격발 벤치마크 (0.1ms 테스트)
5. 🩺 시스템 종합 진단 (Doctor Checklist)
```

- **CLI 비대화형 실행 지원**:
  - `python3 beomchro_core.py --test-run` : 자체 진단 및 자동화 테스트
  - `python3 beomchro_core.py --mode 1 --no-browser` : 시뮬레이터 백그라운드 구동

---

## 6. 라이선스 및 면책조항

본 소프트웨어는 반응속도 벤치마크, 인터페이스 시뮬레이션 및 기술 연구 목적으로 제작되었습니다.
