# [TASK INSTRUCTION] BEOMCHRO 하이브리드 대기열 진입 시스템 구축 프롬프트

> **실행 지침**: 이 문서를 확인한 에이전트는 사용자의 추가 지시 없이 즉시 **BEOMCHRO (범크로)** 시스템의 모든 구성 요소를 단계별로 완전하게 구현하고 로컬 검증까지 완료하십시오.

---

## 1. 프로젝트 개요 및 명세

- **프로젝트명**: `BEOMCHRO` (놀티켓 초고속 대기열 진입 하이브리드 엔진)
- **작업 디렉토리**: `/Users/keyco/Projects/beomchro`
- **핵심 목표**: 티켓팅 오픈(00.000초) 시 인간의 신체적 반응 한계(300~400ms)를 극복하고, **0~1ms 미만**으로 대기열 진입 버튼을 격발하여 최선두 대기 순번을 선점하는 크로스 플랫폼 하이브리드 자동화 시스템 구현.
- **지원 운영체제**: **macOS** (Apple Silicon / Intel) 및 **Windows 10/11**

---

## 2. 세부 구현 요구사항

### Component 1: 모던 CLI TUI 메인 컨트롤러 (`beomchro_core.py`)
1. **ASCII Art 로고 헤더**:
   ```
   ██████╗ ███████╗ ██████╗ ███╗   ███╗ ██████╗██╗  ██╗██████╗  ██████╗ 
   ██╔══██╗██╔════╝██╔═══██╗████╗ ████║██╔════╝██║  ██║██╔══██╗██╔═══██╗
   ██████╔╝█████╗  ██║   ██║██╔████╔██║██║     ███████║██████╔╝██║   ██║
   ██╔══██╗██╔══╝  ██║   ██║██║╚██╔╝██║██║     ██╔══██║██╔══██╗██║   ██║
   ██████╔╝███████╗╚██████╔╝██║ ╚═╝ ██║╚██████╗██║  ██║██║  ██║╚██████╔╝
   ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝     ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ 
          >>> NOL-TICKET ULTRA FAST QUEUE INTERCEPTOR v2.0 <<<
   ```
2. **`rich` 기반 모던 터미널 대시보드**:
   - 실시간 밀리초(ms) 단위 시계 및 서버 시간 오차(Time Skew) 실시간 보정 표시
   - 타겟 웹사이트(놀티켓 / 로컬 시뮬레이터) 연결 상태
   - 동작 모드 선택 (1: 로컬 연습 시뮬레이터 구동, 2: 화면 픽셀 감시 모드, 3: 서버 시간 정각 자동 클릭 모드)
3. **OS 자동 감지 및 초고속 마우스 클릭 주입**:
   - **Windows**: `ctypes.windll.user32.SendInput` 기반 하드웨어 레벨 마우스 이벤트 (0.1ms 지연)
   - **macOS**: `Quartz.CoreGraphics` (`CGEventCreateMouseEvent`, `CGEventPost`) 기반 네이티브 마우스 이벤트

### Component 2: 내장 로컬 모의 연습장 & 반응속도 측정기 (`simulator/`)
- 로컬 경량 HTTP 서버 (`http://localhost:8989`) 구동 및 자동 브라우저 오픈
- **`simulator/index.html`**:
  - 실제 놀티켓 예매 페이지 1:1 복제 (공연 포스터, 날짜 선택, 회차 선택, 좌석 배치 요약)
  - '오픈 전' 비활성화된 예매하기 버튼 (회색, `disabled` 속성)
  - 5초/10초 카운트다운 타이머 후 정각 00.000초에 즉시 버튼 활성화 (파란색, `disabled` 제거)
- **`simulator/script.js`**:
  - **수동 손클릭 반응속도 측정 모드**: 사용자가 버튼 활성화 후 클릭한 지연시간(ms)을 측정하여 가상 대기열 순번 표시 (예: 320ms 소요 시 "대기 14,290번 / 예상 대기 48분")
  - **자동 트리거 벤치마크 모드**: Tampermonkey 스크립트 또는 프로그램 트리거로 0~1ms 만에 격발 시 "대기 1번 / 즉시 입장" 효과 시뮬레이션
- **`simulator/style.css`**: 세련된 다크 모드 티켓팅 UI 스타일링

### Component 3: 0ms 브라우저 인젝션 스크립트 (`beomchro_queue.user.js`)
- Tampermonkey / Violentmonkey용 유저스크립트
- `MutationObserver`를 활용하여 대상 버튼의 DOM 속성(`disabled` 제거, class 추가 등) 변화를 마이크로초 단위로 포착 즉시 `button.click()` 실행
- 로컬 시뮬레이터 URL(`http://localhost:8989/*`) 및 실제 놀티켓 티켓팅 URL 모두 매핑 지원

### Component 4: 크로스 플랫폼 실행 스크립트 & 패키지
- **`run_mac.sh`**: macOS용 원클릭 터미널 실행 스크립트 (가상환경 체크, 필요 패키지 자동 설치 후 실행)
- **`run_windows.bat`**: Windows용 원클릭 CMD 실행 배치파일
- **`requirements.txt`**: 필수 최소 패키지 (`rich`, `requests` 등)

---

## 3. Git 버전 관리 및 초기화 지침

사용자가 원격 저장소 URL(GitHub / GitLab 등)을 전달하면:
1. `git init` 수행
2. `.gitignore` 생성 (Python 가상환경, 캐시, OS 잡파일 제외)
3. 원격 저장소 연결: `git remote add origin <사용자가 제공한 URL>`
4. 최초 커밋 생성: `feat: initial commit for BEOMCHRO hybrid queue interceptor`
5. 기본 브랜치 `main` 설정

---

## 4. 자율 실행 단계 (Execution Steps)

1. [ ] 프로젝트 파일 구조 생성 (`simulator/` 포함)
2. [ ] `requirements.txt`, `.gitignore` 생성
3. [ ] `simulator/index.html`, `style.css`, `script.js` 완성
4. [ ] `beomchro_queue.user.js` (Tampermonkey 스크립트) 완성
5. [ ] `beomchro_core.py` (모던 TUI, HTTP 서버, OS 네이티브 클릭 로직) 완성
6. [ ] `run_mac.sh` 및 `run_windows.bat` 실행 스크립트 작성 (실행 권한 부여 `chmod +x`)
7. [ ] 로컬 구동 테스트 검증 (`python3 beomchro_core.py` 비동기 테스트 및 시뮬레이터 엔드포인트 응답 확인)
8. [ ] Git 초기화 및 커밋 완료 보고
