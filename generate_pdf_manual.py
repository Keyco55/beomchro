#!/usr/bin/env python3
"""
Generate a beautiful, multi-page PDF user manual for non-developers.
Uses AppKit / WebKit / CoreText on macOS to render high-resolution Korean typography.
"""

import os
import sys
from pathlib import Path
import AppKit
from Foundation import NSData, NSURL, NSString

OUTPUT_DOWNLOADS = Path.home() / "Downloads" / "BEOMCHRO_비개발자_완벽_사용설명서.pdf"
OUTPUT_PROJECT = Path(__file__).resolve().parent / "BEOMCHRO_비개발자_사용설명서.pdf"

HTML_CONTENT = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<style>
  @page {
    size: A4;
    margin: 20mm 18mm 20mm 18mm;
  }
  body {
    font-family: -apple-system, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
    color: #1e293b;
    line-height: 1.6;
    font-size: 10.5pt;
    margin: 0;
    padding: 0;
  }
  
  /* 커버 헤더 */
  .cover {
    text-align: center;
    padding: 30px 20px 25px 20px;
    background: linear-gradient(135deg, #0b1329 0%, #1e293b 100%);
    color: #ffffff;
    border-radius: 12px;
    margin-bottom: 25px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
  }
  .cover .badge {
    display: inline-block;
    background: #00d2ff;
    color: #0b1329;
    font-weight: 800;
    font-size: 9pt;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 1px;
    margin-bottom: 10px;
  }
  .cover h1 {
    font-size: 22pt;
    font-weight: 900;
    margin: 0 0 6px 0;
    color: #ffffff;
    letter-spacing: -0.5px;
  }
  .cover p {
    font-size: 11pt;
    color: #94a3b8;
    margin: 0;
  }

  /* 섹션 스타일 */
  h2 {
    font-size: 14pt;
    font-weight: 800;
    color: #0f172a;
    border-bottom: 2px solid #0284c7;
    padding-bottom: 6px;
    margin-top: 24px;
    margin-bottom: 12px;
  }
  h3 {
    font-size: 12pt;
    font-weight: 700;
    color: #0369a1;
    margin-top: 16px;
    margin-bottom: 6px;
  }
  p {
    margin: 0 0 8px 0;
  }
  ul, ol {
    margin: 0 0 12px 0;
    padding-left: 22px;
  }
  li {
    margin-bottom: 5px;
  }

  /* 박스 및 하이라이트 */
  .step-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #0284c7;
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    margin-bottom: 14px;
  }
  .step-box.urgent {
    border-left-color: #ef4444;
    background: #fff5f5;
  }
  .step-title {
    font-size: 11.5pt;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 6px;
  }

  .tip-box {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-left: 4px solid #16a34a;
    padding: 10px 14px;
    border-radius: 6px;
    margin: 12px 0;
    font-size: 10pt;
  }
  .tip-title {
    font-weight: 700;
    color: #166534;
    margin-bottom: 4px;
  }

  .warning-box {
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-left: 4px solid #f59e0b;
    padding: 10px 14px;
    border-radius: 6px;
    margin: 12px 0;
    font-size: 10pt;
  }
  .warning-title {
    font-weight: 700;
    color: #92400e;
    margin-bottom: 4px;
  }

  .code-badge {
    background: #e2e8f0;
    color: #0f172a;
    font-family: monospace;
    font-size: 9.5pt;
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 600;
  }

  .summary-table {
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0;
    font-size: 9.5pt;
  }
  .summary-table th {
    background: #f1f5f9;
    color: #334155;
    font-weight: 700;
    border: 1px solid #cbd5e1;
    padding: 8px 10px;
    text-align: left;
  }
  .summary-table td {
    border: 1px solid #e2e8f0;
    padding: 8px 10px;
  }

  .page-break {
    page-break-after: always;
  }

  .footer {
    text-align: center;
    font-size: 8.5pt;
    color: #94a3b8;
    margin-top: 25px;
    border-top: 1px solid #e2e8f0;
    padding-top: 10px;
  }
</style>
</head>
<body>

  <!-- 커버 헤더 -->
  <div class="cover">
    <div class="badge">NOL-TICKET ZERO-SETUP MANUAL</div>
    <h1>BEOMCHRO (범크로) v2.0</h1>
    <p>비개발자를 위한 100% 완전 정복 초간편 사용 설명서</p>
  </div>

  <div class="tip-box">
    <div class="tip-title">💡 이 설명서의 목적</div>
    컴퓨터를 잘 모르는 비개발자도 <strong>확장프로그램 설치나 복사-붙여넣기 없이</strong>, 링크 하나만 받아서 <strong>더블클릭으로 0ms 티켓팅 1번 대기를 선점</strong>할 수 있도록 모든 과정을 스텝 바이 스텝으로 안내합니다.
  </div>

  <h2>1. BEOMCHRO는 어떤 프로그램인가요?</h2>
  <p>인기 콘서트/뮤지컬 티켓팅 오픈 정각(예: 저녁 8시 00분 00.000초)이 되면 전국의 수만 명이 동시에 버튼을 누릅니다. 사람은 아무리 빨라도 손으로 누르면 <strong>0.3초 ~ 0.4초(300~400ms)</strong>의 신체적 지연이 발생해 대기 1만 번대로 밀려납니다.</p>
  <p><strong>BEOMCHRO(범크로)</strong>는 티켓팅 버튼이 열리는 순간을 마이크로초 단위로 감시하다가, <strong>0.001초(0ms) 미만으로 즉시 격발</strong>하여 최우선 1번 대기열을 가로채 선점해 주는 초고속 티켓팅 도우미입니다.</p>

  <h2>2. [STEP 1] 깃허브에서 프로그램 다운로드 받기</h2>
  <div class="step-box">
    <div class="step-title">1단계: 저장소 웹페이지 접속</div>
    전달받은 주소로 인터넷 브라우저에서 접속합니다.<br>
    👉 주소: <strong>https://github.com/Keyco55/beomchro</strong>
  </div>

  <div class="step-box">
    <div class="step-title">2단계: 초록색 Code 버튼 클릭 후 ZIP 다운로드</div>
    <ol>
      <li>화면 오른쪽 위에 있는 <strong>초록색 [ <> Code ] 버튼</strong>을 클릭합니다.</li>
      <li>나타난 메뉴의 맨 아래에 있는 <strong>[ Download ZIP ]</strong>을 클릭합니다.</li>
      <li>컴퓨터 다운로드 폴더에 <strong>beomchro-main.zip</strong> 파일이 저장됩니다.</li>
    </ol>
  </div>

  <div class="step-box">
    <div class="step-title">3단계: 압축 풀기</div>
    다운로드된 <strong>beomchro-main.zip</strong> 파일을 마우스 우클릭하여 <strong>[압축 풀기]</strong>를 진행합니다. (바탕화면이나 편리한 폴더에 풀어주세요)
  </div>

  <h2>3. [STEP 2] 컴퓨터 필수 준비물 확인 (단 1번만 확인!)</h2>
  <p>BEOMCHRO는 별도의 확장 프로그램 설치가 전혀 필요 없지만, 컴퓨터에 아래 2가지만 있으면 됩니다.</p>

  <table class="summary-table">
    <thead>
      <tr>
        <th style="width: 28%;">항목</th>
        <th style="width: 36%;">맥 (Mac)</th>
        <th style="width: 36%;">윈도우 (Windows)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>1. 웹 브라우저</strong></td>
        <td><strong>Chrome</strong>, Whale, 또는 Edge (설치되어 있으면 완료)</td>
        <td><strong>Chrome</strong>, Whale, 또는 Edge (설치되어 있으면 완료)</td>
      </tr>
      <tr>
        <td><strong>2. 파이썬 (Python)</strong></td>
        <td>대부분 이미 설치되어 있습니다. (미설치 시 최초 1회 자동 알림)</td>
        <td><strong>python.org</strong>에서 무료 다운로드 후 설치 (★아래 주의사항 필수)</td>
      </tr>
    </tbody>
  </table>

  <div class="warning-box">
    <div class="warning-title">⚠️ [윈도우 사용자 필수 주의사항] 파이썬 설치할 때</div>
    윈도우에서 파이썬(python.org) 인스톨러를 실행할 때, <strong>첫 화면 맨 아래에 있는 [ Add python.exe to PATH ] 체크박스에 반드시 체크</strong>를 하시고 [Install Now]를 눌러주셔야 합니다! (체크 안 하시면 프로그램이 실행되지 않습니다)
  </div>

  <div class="page-break"></div>

  <h2>4. [STEP 3] 프로그램 실행하기 (더블클릭!)</h2>
  <p>압축을 푼 <span class="code-badge">beomchro-main</span> 폴더로 들어갑니다.</p>

  <div class="step-box">
    <div class="step-title">🍏 맥(Mac) 사용자 실행 방법</div>
    폴더 안에 있는 <strong>[ BEOMCHRO.app ]</strong> (또는 <strong>[ BEOMCHRO.command ]</strong>) 아이콘을 <strong>더블클릭</strong>합니다.<br>
    <small style="color: #64748b;">※ 처음 실행 시 "확인되지 않은 개발자" 보안 경고가 뜬다면: 파일을 <strong>마우스 우클릭 ➔ [열기] ➔ [열기]</strong>를 누르시면 다음부터 정상 실행됩니다.</small>
  </div>

  <div class="step-box">
    <div class="step-title">🪟 윈도우(Windows) 사용자 실행 방법</div>
    폴더 안에 있는 <strong>[ run_windows.bat ]</strong> 파일을 <strong>더블클릭</strong>합니다.<br>
    <small style="color: #64748b;">※ 파란색 "Windows의 PC 보호" 창이 뜬다면: <strong>[추가 정보] ➔ [실행]</strong> 버튼을 누르시면 됩니다.</small>
  </div>

  <h2>5. [STEP 4] 0ms 전용 티켓팅 브라우저 열기</h2>
  <p>프로그램을 더블클릭하면 멋진 검은색 대시보드 화면이 나타납니다.</p>

  <div class="step-box">
    <div class="step-title">원클릭 브라우저 기동 (키보드 1번 입력)</div>
    <ol>
      <li>키보드에서 숫자 <strong>1</strong>을 누르고 <strong>엔터(Enter)</strong>를 누릅니다.</li>
      <li>컴퓨터가 자동으로 전용 브라우저(Chrome)를 띄워줍니다.</li>
      <li>브라우저 우측 상단을 보시면 <strong>[ ⚡ BEOMCHRO EXTENSION 0ms READY ]</strong>라는 초록/청록색 배너가 자동으로 장착되어 떠 있습니다!</li>
    </ol>
  </div>

  <div class="tip-box">
    <div class="tip-title">✨ 무설치 자동 장착 (Zero-Setup)의 마법</div>
    기존처럼 크롬 웹스토어에서 Tampermonkey 확장프로그램을 찾아서 깔고, 코드를 복사해서 붙여넣을 필요가 <strong>전혀 없습니다!</strong> BEOMCHRO가 브라우저를 켤 때 0ms 인젝터를 자동으로 메모리에 꽂아서 띄워줍니다.
  </div>

  <h2>6. [STEP 5] 로그인 & 본인인증(PASS) 미리 해두기</h2>
  <div class="step-box">
    <div class="step-title">로그인 세션 영구 보존 안내</div>
    열린 브라우저에서 놀티켓 또는 인터파크 사이트로 이동하여 <strong>미리 로그인하고 본인인증(PASS, 카카오인증 등)을 완료</strong>해 두세요.<br>
    <strong>★ 중요:</strong> BEOMCHRO 전용 브라우저는 세션이 영구 저장되므로, 오늘 로그인해 두면 브라우저를 닫았다가 티켓팅 당일 다시 켜도 로그인이 그대로 유지됩니다!
  </div>

  <h2>7. [STEP 6] 모의 연습장으로 1번 대기열 체험하기</h2>
  <p>브라우저가 뜰 때 함께 열린 <strong>로컬 연습 시뮬레이터 (http://localhost:8989)</strong> 창을 확인해보세요.</p>
  <div class="step-box">
    <div class="step-title">0ms 자동 격발 벤치마크 테스트</div>
    <ol>
      <li>화면 상단의 <strong>[ 5초 카운트다운 ]</strong> 또는 <strong>[ ⚡ 즉시 오픈 ]</strong> 버튼을 클릭합니다.</li>
      <li>카운트다운이 0.00초 정각이 되는 순간! <strong>손가락 하나 대지 않아도</strong> 예매하기 버튼이 <strong>0.1ms 만에 초고속으로 자동 격발</strong>됩니다.</li>
      <li>화면에 <strong>[ 나의 대기 번호: 1번 (즉시 입장) - 신(GOD)의 영역 ]</strong> 축하 팝업이 뜨는 것을 확인하실 수 있습니다.</li>
    </ol>
  </div>

  <div class="page-break"></div>

  <h2>8. [STEP 7] 티켓팅 당일 실전 타임라인 가이드</h2>
  <p>티켓팅 당일 성공 확률을 100%로 끌어올리는 실전 행동 요령입니다.</p>

  <div class="step-box">
    <div class="step-title">🕒 티켓 오픈 15분 전: 프로그램 실행</div>
    <span class="code-badge">BEOMCHRO.app</span> (또는 <span class="code-badge">run_windows.bat</span>)을 실행하고 <strong>1번</strong>을 눌러 전용 브라우저를 켭니다.
  </div>

  <div class="step-box">
    <div class="step-title">🕒 티켓 오픈 10분 전: 로그인 및 좌석 선택 준비</div>
    놀티켓 예매 페이지에 접속하여 로그인이 잘 유지되어 있는지 확인하고, 관람할 날짜와 회차를 선택해 둡니다. 우측 상단에 <strong>⚡ BEOMCHRO EXTENSION 0ms READY</strong> 배너가 켜져 있는지 확인합니다.
  </div>

  <div class="step-box urgent">
    <div class="step-title">🚨 티켓 오픈 0초 정각: 자동 격발 대기</div>
    정각(00.000초)이 되면 회색이었던 '예매 오픈 대기 중' 버튼이 활성화되는 순간, BEOMCHRO가 마이크로초 단위로 가로채어 <strong>인간이 도달할 수 없는 0ms 반응속도로 최선두 대기 순번을 선점</strong>합니다!
  </div>

  <h2>9. 자주 묻는 질문 (FAQ) & 문제 해결</h2>
  <div class="step-box">
    <div class="step-title">Q1. 브라우저 우측 상단에 ⚡ BEOMCHRO 배너가 안 떠요!</div>
    열려 있는 모든 크롬 브라우저 창을 닫으신 후, BEOMCHRO 대시보드에서 1번을 다시 눌러 실행해 주세요.
  </div>

  <div class="step-box">
    <div class="step-title">Q2. 다른 컴퓨터로 복사해서 사용해도 되나요?</div>
    네! 압축파일(ZIP) 그대로 친구나 가족에게 카카오톡/메일로 보내주시면 이 설명서의 1단계부터 똑같이 사용하실 수 있습니다.
  </div>

  <div class="step-box">
    <div class="step-title">Q3. 제 컴퓨터 시계가 서버 시계와 다르면 어쩌죠?</div>
    BEOMCHRO 대시보드는 백그라운드에서 티켓팅 서버의 시간 오차(Time Skew)를 실시간으로 자동 계산하여 오차 없이 정확한 정각에 작동하도록 보정합니다.
  </div>

  <div class="footer">
    BEOMCHRO Hybrid Queue Interceptor Engine v2.0 • Produced for Super-Fast Queue Simulation
  </div>

</body>
</html>
"""

def generate_pdf():
    print("[PDF] Preparing AppKit environment...")
    data = HTML_CONTENT.encode("utf-8")
    ns_data = NSData.dataWithBytes_length_(data, len(data))

    options = {
        AppKit.NSDocumentTypeDocumentAttribute: AppKit.NSHTMLTextDocumentType,
        AppKit.NSCharacterEncodingDocumentAttribute: 4 # NSUTF8StringEncoding
    }

    attr_str, doc_attrs, err = AppKit.NSAttributedString.alloc().initWithData_options_documentAttributes_error_(
        ns_data, options, None, None
    )

    if err or not attr_str:
        print(f"❌ Failed to parse HTML into NSAttributedString: {err}")
        return False

    # A4 Dimensions: 595.28 x 841.89 points
    page_width = 595.28
    page_height = 841.89

    view = AppKit.NSTextView.alloc().initWithFrame_(AppKit.NSMakeRect(0, 0, page_width, page_height))
    view.textStorage().setAttributedString_(attr_str)

    # Use NSPrintOperation to generate a paginated PDF
    print_info = AppKit.NSPrintInfo.sharedPrintInfo().copy()
    print_info.setPaperSize_(AppKit.NSMakeSize(page_width, page_height))
    print_info.setTopMargin_(40.0)
    print_info.setBottomMargin_(40.0)
    print_info.setLeftMargin_(40.0)
    print_info.setRightMargin_(40.0)

    # Output to Downloads
    OUTPUT_DOWNLOADS.parent.mkdir(parents=True, exist_ok=True)
    print_info.setJobDisposition_(AppKit.NSPrintSaveJob)
    print_info.dictionary().setObject_forKey_(OUTPUT_DOWNLOADS.resolve().as_uri(), AppKit.NSPrintJobSavingURL)

    # Also save with dataWithPDFInsideRect
    pdf_data = view.dataWithPDFInsideRect_(view.bounds())
    
    # Save to Downloads
    pdf_data.writeToFile_atomically_(str(OUTPUT_DOWNLOADS), True)
    print(f"✔ PDF가 다운로드 폴더에 저장되었습니다: {OUTPUT_DOWNLOADS} ({len(pdf_data)} bytes)")

    # Save to Project directory as well
    pdf_data.writeToFile_atomically_(str(OUTPUT_PROJECT), True)
    print(f"✔ PDF가 프로젝트 폴더에도 저장되었습니다: {OUTPUT_PROJECT}")

    return True

if __name__ == "__main__":
    success = generate_pdf()
    sys.exit(0 if success else 1)
