# ⚡ BEOMCHRO (범크로) v2.0
> **놀티켓 초고속 대기열 진입 하이브리드 엔진 & 올인원 독립 실행 프로그램**  
> *Nol-Ticket Ultra Fast 0ms Queue Interceptor Engine (Zero-Setup Standalone App)*

---

## 1. 프로젝트 개요

**BEOMCHRO (범크로)**는 대규모 티켓팅 오픈 정각(00.000초) 시 인간의 신체적 반응 속도 한계(300~400ms)를 극복하고, **0~1ms 미만**으로 대기열 진입 버튼을 가로채 최선두 대기 순번(1번 대기)을 선점하기 위한 크로스 플랫폼 자동화 시스템입니다.

### 🌟 v2.0 올인원 원클릭 혁신 (Zero-Setup)
- **확장 프로그램 수동 설치 및 스크립트 복사/붙여넣기 100% 제거**:
  - 더 이상 브라우저 웹스토어에서 Tampermonkey를 찾아 깔거나 긴 스크립트를 복사할 필요가 없습니다.
  - 프로그램을 더블클릭하면 **0ms 인터셉터 엔진(Manifest V3 Extension)이 자동 장착된 전용 브라우저가 원클릭으로 실행**됩니다.
- **로그인 및 본인인증(PASS) 영구 보존**:
  - 전용 브라우저 프로필을 사용하여 네이버/카카오 로그인 및 본인인증 상태가 브라우저를 닫아도 그대로 유지됩니다.
- **더블클릭 단일 실행 앱 & 시각 매뉴얼**:
  - **macOS**: `BEOMCHRO.app` 또는 `BEOMCHRO.command` 더블클릭 실행 지원
  - **Windows**: `run_windows.bat` 원클릭 실행 및 `build_windows.bat`를 통한 단일 `.exe` 빌드 지원
  - **공식 매뉴얼**: [`BEOMCHRO_사용설명서.pdf`](BEOMCHRO_사용설명서.pdf) (순서도, 화면 예시, 스텝별 가이드 포함)

---

## 2. 빠른 시작 가이드 (Quick Start)

### 🍎 macOS 사용자 (더블클릭 원클릭 실행)
1. 프로젝트 폴더의 **`BEOMCHRO.app`** (또는 **`BEOMCHRO.command`**)을 **더블클릭**합니다.
2. 터미널 창과 함께 대시보드가 열리며, **1번(🚀 원클릭 0ms 브라우저 실행)**을 선택합니다.
3. 크롬/웨일/엣지 브라우저가 자동으로 열리며 우측 상단에 `⚡ BEOMCHRO EXTENSION 0ms READY` 배너가 표시됩니다.

### 🪟 Windows 사용자
1. 프로젝트 폴더의 **`run_windows.bat`**를 **더블클릭**합니다.
2. 가상환경 및 필수 패키지가 자동 구성되며 TUI 대시보드가 실행됩니다.
3. 독립 실행형 `.exe` 파일이 필요한 경우 **`build_windows.bat`**를 더블클릭하면 `dist/BEOMCHRO/BEOMCHRO.exe`가 생성됩니다.

---

## 3. 핵심 아키텍처 및 동작 원리

```text
+-----------------------------------------------------------------------+
|  [BEOMCHRO.app / run_mac.sh / run_windows.bat] (원클릭 실행)          |
+-----------------------------------+-----------------------------------+
                                    |
            +-----------------------v-----------------------+
            |  BEOMCHRO TUI & Local Simulator Server (:8989)|
            +-----------------------+-----------------------+
                                    | --load-extension
            +-----------------------v-----------------------+
            |  티켓팅 전용 브라우저 세션 (Chrome / Whale / Edge)    |
            |  • Zero-Setup 0ms Interceptor Extension 자동 장착   |
            |  • 카카오 / 네이버 로그인 & 본인인증 세션 영구 보존   |
            +-----------------------+-----------------------+
                                    | MutationObserver 0ms
            +-----------------------v-----------------------+
            |  티켓 오픈 정각(00.000초) ➔ 0ms 가로채기 ➔ 대기열 1번 선점|
            +-----------------------------------------------+
```

---

## 4. 디렉터리 및 파일 구조

```text
beomchro/
├── BEOMCHRO.app/             # macOS 네이티브 더블클릭 애플리케이션 번들
│   └── Contents/
│       ├── Info.plist        # 앱 번들 메타데이터
│       ├── MacOS/BEOMCHRO    # 앱 실행 런처
│       └── Resources/        # 고해상도 앱 아이콘 (BEOMCHRO.icns)
├── BEOMCHRO.command          # macOS 더블클릭 실행 스크립트
├── BEOMCHRO.icns             # macOS 애플리케이션 공식 아이콘
│
├── extension/                # 브라우저 무설치 자동 장착 확장프로그램 (Manifest V3)
│   ├── manifest.json         # 확장프로그램 규격 설정
│   ├── content.js            # 0ms MutationObserver 자동 인터셉터 & HUD
│   └── icons/                # 16, 48, 128px 고해상도 아이콘
│
├── beomchro_launcher.py      # 설치된 브라우저 탐색 및 전용 세션 런처
├── beomchro_core.py          # 메인 컨트롤러 (서버 + 네이티브 클릭 + 정각 타이머)
├── beomchro_queue.user.js    # Tampermonkey용 대체 유저스크립트
│
├── run_mac.sh                # macOS 원클릭 터미널 런처
├── run_windows.bat           # Windows 원클릭 CMD 런처
├── build_windows_exe.py      # Windows 단일 EXE 빌드 스크립트 (PyInstaller)
├── build_windows.bat         # Windows EXE 원클릭 빌드 배치파일
├── requirements.txt          # 파이썬 패키지 의존성
│
└── simulator/                # 1:1 놀티켓 모의 연습장 & 반응속도 측정기
    ├── index.html            # 놀티켓 복제 인터페이스
    ├── style.css             # 네온 다크 테마 & 글래스모피즘 UI
    └── script.js             # 반응속도(ms) 측정 및 가상 대기열 순번 산출 엔진
```

---

## 5. TUI 대시보드 메뉴 안내

```text
1. 🚀 원클릭 0ms 티켓팅 브라우저 실행 (확장프로그램 무설치 자동 장착)
2. 🎯 화면 픽셀 색상 감시 모드 (Pixel Color Watcher)
3. ⏰ 서버 시간 정각 자동 클릭 모드 (Exact Time Trigger)
4. ⚡ 마우스 초고속 격발 벤치마크 (0.1ms 테스트)
5. 🩺 시스템 종합 진단 (Doctor Checklist)
0. ❌ 종료 (Exit)
```

---

## 6. 라이선스 및 면책조항

본 소프트웨어는 반응속도 벤치마크, 인터페이스 시뮬레이션 및 기술 연구 목적으로 제작되었습니다.
