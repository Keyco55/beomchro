#!/usr/bin/env python3
"""
BEOMCHRO v2.0 Official Visual User Manual PDF Generator
Creates a 5-page high-visibility vector PDF with TOC, Flowcharts, Architecture Diagrams,
and Step-by-Step UI Mockup Illustrations using macOS Quartz & AppKit.
"""

import sys
import shutil
from pathlib import Path
import Quartz
import AppKit
from Foundation import NSURL, NSMakeRect, NSMakePoint, NSMakeSize

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_PROJECT = PROJECT_DIR / "BEOMCHRO_사용설명서.pdf"
OUTPUT_DOWNLOADS = Path.home() / "Downloads" / "BEOMCHRO_완벽_사용설명서.pdf"

PAGE_W = 595.28
PAGE_H = 841.89
MARGIN_X = 34.0
CONTENT_W = PAGE_W - (MARGIN_X * 2)  # 527.28


# ==============================================================================
# Drawing Primitives (AppKit / Quartz Flipped Top-Left Coordinate System)
# ==============================================================================
def rgb(r, g, b, a=1.0):
    return AppKit.NSColor.colorWithCalibratedRed_green_blue_alpha_(
        r / 255.0, g / 255.0, b / 255.0, float(a)
    )


def rect(x, y, w, h, r=0.0, fill=None, stroke=None, stroke_w=1.0, dashed=False):
    r_rect = NSMakeRect(float(x), float(y), float(w), float(h))
    if r > 0:
        path = AppKit.NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(r_rect, float(r), float(r))
    else:
        path = AppKit.NSBezierPath.bezierPathWithRect_(r_rect)

    if fill is not None:
        (rgb(*fill) if isinstance(fill, tuple) else fill).setFill()
        path.fill()

    if stroke is not None:
        (rgb(*stroke) if isinstance(stroke, tuple) else stroke).setStroke()
        path.setLineWidth_(float(stroke_w))
        if dashed:
            path.setLineDash_count_phase_([4.0, 3.0], 2, 0.0)
        path.stroke()


def grad_rect(x, y, w, h, r, c1, c2, angle=0.0, stroke=None, stroke_w=1.0):
    r_rect = NSMakeRect(float(x), float(y), float(w), float(h))
    if r > 0:
        path = AppKit.NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(r_rect, float(r), float(r))
    else:
        path = AppKit.NSBezierPath.bezierPathWithRect_(r_rect)

    col1 = rgb(*c1) if isinstance(c1, tuple) else c1
    col2 = rgb(*c2) if isinstance(c2, tuple) else c2
    grad = AppKit.NSGradient.alloc().initWithStartingColor_endingColor_(col1, col2)
    grad.drawInBezierPath_angle_(path, float(angle))

    if stroke is not None:
        (rgb(*stroke) if isinstance(stroke, tuple) else stroke).setStroke()
        path.setLineWidth_(float(stroke_w))
        path.stroke()


def circle(cx, cy, radius, fill=None, stroke=None, stroke_w=1.0):
    rect(cx - radius, cy - radius, radius * 2, radius * 2, r=radius, fill=fill, stroke=stroke, stroke_w=stroke_w)


def line(x1, y1, x2, y2, color=(148, 163, 184), width=1.5, dashed=False):
    path = AppKit.NSBezierPath.bezierPath()
    path.moveToPoint_(NSMakePoint(float(x1), float(y1)))
    path.lineToPoint_(NSMakePoint(float(x2), float(y2)))
    path.setLineWidth_(float(width))
    if dashed:
        path.setLineDash_count_phase_([4.0, 3.0], 2, 0.0)
    (rgb(*color) if isinstance(color, tuple) else color).setStroke()
    path.stroke()


def arrow_right(x1, y, x2, color=(2, 132, 199), width=2.0, head=5.5):
    line(x1, y, x2 - 2, y, color=color, width=width)
    path = AppKit.NSBezierPath.bezierPath()
    path.moveToPoint_(NSMakePoint(float(x2), float(y)))
    path.lineToPoint_(NSMakePoint(float(x2 - head * 1.3), float(y - head * 0.85)))
    path.lineToPoint_(NSMakePoint(float(x2 - head * 1.3), float(y + head * 0.85)))
    path.closePath()
    (rgb(*color) if isinstance(color, tuple) else color).setFill()
    path.fill()


def arrow_down(x, y1, y2, color=(2, 132, 199), width=2.0, head=5.5):
    line(x, y1, x, y2 - 2, color=color, width=width)
    path = AppKit.NSBezierPath.bezierPath()
    path.moveToPoint_(NSMakePoint(float(x), float(y2)))
    path.lineToPoint_(NSMakePoint(float(x - head * 0.85), float(y2 - head * 1.3)))
    path.lineToPoint_(NSMakePoint(float(x + head * 0.85), float(y2 - head * 1.3)))
    path.closePath()
    (rgb(*color) if isinstance(color, tuple) else color).setFill()
    path.fill()


FONT_MAP = {
    "Light": "AppleSDGothicNeo-Light",
    "Regular": "AppleSDGothicNeo-Regular",
    "Medium": "AppleSDGothicNeo-Medium",
    "SemiBold": "AppleSDGothicNeo-SemiBold",
    "Bold": "AppleSDGothicNeo-Bold",
    "ExtraBold": "AppleSDGothicNeo-ExtraBold",
    "Heavy": "AppleSDGothicNeo-Heavy",
}


def get_font(size=10.0, weight="Regular", mono=False):
    if mono:
        name = "Menlo-Bold" if weight in ("Bold", "ExtraBold", "Heavy", "SemiBold") else "Menlo-Regular"
        f = AppKit.NSFont.fontWithName_size_(name, float(size))
        if f:
            return f
    font_name = FONT_MAP.get(weight, "AppleSDGothicNeo-Regular")
    f = AppKit.NSFont.fontWithName_size_(font_name, float(size))
    return f or AppKit.NSFont.systemFontOfSize_(float(size))


def text(s, x, y, w=500.0, h=120.0, size=10.0, weight="Regular", color=(30, 41, 59), align="left", line_spacing=2.5, mono=False):
    para = AppKit.NSMutableParagraphStyle.alloc().init()
    if align == "center":
        para.setAlignment_(AppKit.NSTextAlignmentCenter)
    elif align == "right":
        para.setAlignment_(AppKit.NSTextAlignmentRight)
    else:
        para.setAlignment_(AppKit.NSTextAlignmentLeft)
    para.setLineSpacing_(float(line_spacing))

    attrs = {
        AppKit.NSFontAttributeName: get_font(size, weight, mono=mono),
        AppKit.NSForegroundColorAttributeName: rgb(*color) if isinstance(color, tuple) else color,
        AppKit.NSParagraphStyleAttributeName: para,
    }
    ns_str = AppKit.NSString.stringWithString_(str(s))
    ns_str.drawInRect_withAttributes_(NSMakeRect(float(x), float(y), float(w), float(h)), attrs)


def badge(label, x, y, w, h, bg=(2, 132, 199), fg=(255, 255, 255), size=8.5, weight="Bold", r=None, stroke=None, mono=False):
    rad = float(h) / 2.0 if r is None else float(r)
    rect(x, y, w, h, r=rad, fill=bg, stroke=stroke, stroke_w=1.0)
    y_offset = (h - (size * 1.25)) / 2.0
    text(label, x, y + y_offset, w=w, h=h, size=size, weight=weight, color=fg, align="center", mono=mono)


def section_title(num_badge, title, subtitle, y):
    badge(num_badge, MARGIN_X, y, 64, 21, bg=(14, 165, 233), fg=(255, 255, 255), size=9.0, weight="ExtraBold", r=5)
    text(title, MARGIN_X + 72, y + 1, w=450, h=24, size=14.0, weight="ExtraBold", color=(15, 23, 42))
    if subtitle:
        text(subtitle, MARGIN_X, y + 25, w=CONTENT_W, h=20, size=9.2, weight="Medium", color=(100, 116, 139))
        line(MARGIN_X, y + 43, MARGIN_X + CONTENT_W, y + 43, color=(226, 232, 240), width=1.0)
        return y + 51
    else:
        line(MARGIN_X, y + 26, MARGIN_X + CONTENT_W, y + 26, color=(226, 232, 240), width=1.0)
        return y + 34


def draw_window_frame(x, y, w, h, title_str, dark=True):
    bg_col = (15, 23, 42) if dark else (255, 255, 255)
    bar_col = (30, 41, 59) if dark else (241, 245, 249)
    border_col = (51, 65, 85) if dark else (203, 213, 225)
    title_col = (203, 213, 225) if dark else (71, 85, 105)

    rect(x, y, w, h, r=9, fill=bg_col, stroke=border_col, stroke_w=1.2)
    rect(x, y, w, 24, r=9, fill=bar_col)
    rect(x, y + 14, w, 10, r=0, fill=bar_col)
    line(x, y + 24, x + w, y + 24, color=border_col, width=0.8)

    # Traffic lights
    circle(x + 13, y + 12, 3.8, fill=(239, 68, 68))
    circle(x + 25, y + 12, 3.8, fill=(245, 158, 11))
    circle(x + 37, y + 12, 3.8, fill=(16, 185, 129))

    text(title_str, x + 48, y + 6, w=w - 60, h=16, size=8.2, weight="SemiBold", color=title_col)


def draw_page_chrome(page_num, total_pages, right_label):
    # Subtle soft page background
    rect(0, 0, PAGE_W, PAGE_H, fill=(252, 253, 255))

    if page_num > 1:
        grad_rect(0, 0, PAGE_W, 5, 0, (2, 132, 199), (0, 210, 255), angle=0)
        text("⚡ BEOMCHRO v2.0 OFFICIAL USER GUIDE", MARGIN_X, 16, w=280, h=16, size=8.2, weight="ExtraBold", color=(2, 132, 199))
        text(right_label, MARGIN_X, 16, w=CONTENT_W, h=16, size=8.2, weight="SemiBold", color=(100, 116, 139), align="right")
        line(MARGIN_X, 32, MARGIN_X + CONTENT_W, 32, color=(226, 232, 240), width=0.8)

    # Footer
    line(MARGIN_X, PAGE_H - 36, MARGIN_X + CONTENT_W, PAGE_H - 36, color=(226, 232, 240), width=0.8)
    text("GitHub: https://github.com/Keyco55/beomchro", MARGIN_X, PAGE_H - 25, w=250, h=15, size=8.0, weight="Medium", color=(148, 163, 184))
    text("BEOMCHRO Ultra-Fast 0ms Queue Engine", MARGIN_X, PAGE_H - 25, w=CONTENT_W, h=15, size=8.0, weight="Medium", color=(148, 163, 184), align="center")
    badge(f"PAGE {page_num} / {total_pages}", MARGIN_X + CONTENT_W - 62, PAGE_H - 28, 62, 17, bg=(241, 245, 249), fg=(71, 85, 105), size=7.8, weight="Bold", r=8)


# ==============================================================================
# PAGE 1: Cover + TOC + Speed Comparison Chart + 5-Step Master Flowchart
# ==============================================================================
def render_page_1():
    draw_page_chrome(1, 5, "")

    # 1. Hero Cover Banner
    grad_rect(MARGIN_X, 26, CONTENT_W, 132, 14, (9, 14, 28), (22, 37, 68), angle=15, stroke=(0, 210, 255), stroke_w=1.2)
    # Decorative glow circles inside banner
    circle(MARGIN_X + CONTENT_W - 55, 88, 36, fill=(14, 165, 233, 0.18), stroke=(0, 240, 255, 0.45), stroke_w=1.2)
    text("⚡", MARGIN_X + CONTENT_W - 91, 65, w=72, h=50, size=34, weight="Heavy", color=(0, 240, 255), align="center")

    badge("OFFICIAL VISUAL GUIDE • ZERO-SETUP v2.0", MARGIN_X + 22, 42, 206, 19, bg=(0, 210, 255), fg=(9, 14, 28), size=8.0, weight="ExtraBold", r=9)
    text("BEOMCHRO (범크로) 완벽 사용 설명서", MARGIN_X + 22, 69, w=420, h=32, size=21.5, weight="Heavy", color=(255, 255, 255))
    text("확장프로그램 설치나 복잡한 스크립트 복사 없이, 더블클릭 한 번으로 0ms 대기열 1번을 선점하는 공식 가이드", MARGIN_X + 22, 102, w=430, h=22, size=9.6, weight="Medium", color=(186, 230, 253))
    text("지원 환경: macOS (Apple Silicon / Intel) & Windows 10/11  |  지원 브라우저: Chrome · Whale · Edge", MARGIN_X + 22, 127, w=440, h=18, size=8.3, weight="Medium", color=(148, 163, 184))

    # 2. Table of Contents (목차)
    y = 172
    text("📑 한눈에 보는 목차 (Table of Contents)", MARGIN_X, y, w=300, h=20, size=12.0, weight="ExtraBold", color=(15, 23, 42))
    text("순서대로 따라 하시면 3분 안에 모든 준비가 끝납니다.", MARGIN_X + 235, y + 2, w=290, h=18, size=8.8, weight="Medium", color=(100, 116, 139), align="right")
    y += 22

    toc_items = [
        ("PART 01", "핵심 원리 & 반응속도 비교", "수동 손클릭(340ms) vs 범크로(0ms) 대기 순번 차이", "P. 01", (2, 132, 199)),
        ("PART 02", "전체 진행 순서도 (Flowchart)", "다운로드부터 실전 격발까지 5단계 전체 흐름도", "P. 01", (2, 132, 199)),
        ("STEP 01", "프로그램 다운로드 & 압축 풀기", "GitHub에서 ZIP 파일 다운로드 및 폴더 압축 해제", "P. 02", (14, 165, 233)),
        ("STEP 02", "파이썬 설치 불필요! 환경 안내", "Mac & Windows 모두 추가 설치 없이 즉시 실행 구조", "P. 02", (14, 165, 233)),
        ("STEP 03", "운영체제별 원클릭 실행 방법", "Mac(BEOMCHRO.app) & Windows(run_windows.bat)", "P. 03", (16, 185, 129)),
        ("STEP 04", "ON/OFF 스위치 & 작동 확인법", "우측 상단 [🟢 ON/OFF] 버튼 및 타겟 조준 테두리 확인", "P. 03", (16, 185, 129)),
        ("STEP 05", "로그인 보존 & 한국시리즈 연습장", "사전 로그인 유지 및 2026 한국시리즈 7차전 자체 테스트", "P. 04", (99, 102, 241)),
        ("STEP 07", "티켓팅 당일 D-Day 실전 타임라인", "정각 행동 요령(마우스 손떼기!) 및 자주 묻는 질문(FAQ)", "P. 05", (245, 158, 11)),
    ]

    col_w = (CONTENT_W - 12) / 2.0
    row_h = 40.0
    for idx, (step_code, title, desc, pg, accent) in enumerate(toc_items):
        col = idx % 2
        row = idx // 2
        cx = MARGIN_X + col * (col_w + 12)
        cy = y + row * (row_h + 7)
        rect(cx, cy, col_w, row_h, r=7, fill=(255, 255, 255), stroke=(226, 232, 240), stroke_w=1.0)
        rect(cx, cy, 4.5, row_h, r=2, fill=accent)
        badge(step_code, cx + 11, cy + 7, 46, 14, bg=accent, fg=(255, 255, 255), size=7.2, weight="ExtraBold", r=4)
        text(title, cx + 62, cy + 5, w=col_w - 102, h=16, size=9.5, weight="Bold", color=(15, 23, 42))
        badge(pg, cx + col_w - 36, cy + 7, 29, 14, bg=(241, 245, 249), fg=(71, 85, 105), size=7.2, weight="Bold", r=4)
        text(desc, cx + 11, cy + 23, w=col_w - 18, h=14, size=7.8, weight="Medium", color=(100, 116, 139))

    # 3. PART 01: Speed Comparison Diagram
    y = 390
    y = section_title("PART 01", "왜 BEOMCHRO인가요? (반응속도 & 대기 순번 비교)", "티켓 오픈 정각(00.000초)에는 0.1초 차이로 수천 명의 대기 순번이 갈립니다.", y)

    rect(MARGIN_X, y, CONTENT_W, 134, r=10, fill=(255, 255, 255), stroke=(203, 213, 225), stroke_w=1.0)

    # Row A: Human Manual Click
    ry1 = y + 14
    badge("일반 수동 클릭", MARGIN_X + 14, ry1 + 2, 78, 20, bg=(254, 226, 226), fg=(185, 28, 28), size=8.5, weight="ExtraBold", r=5)
    # Segmented latency bar
    bx = MARGIN_X + 100
    rect(bx, ry1, 95, 24, r=4, fill=(252, 165, 165))
    text("눈으로 인지 (150ms)", bx, ry1 + 6, w=95, h=14, size=7.6, weight="Bold", color=(127, 29, 29), align="center")
    rect(bx + 98, ry1, 75, 24, r=4, fill=(248, 113, 113))
    text("뇌➔손가락 (110ms)", bx + 98, ry1 + 6, w=75, h=14, size=7.6, weight="Bold", color=(255, 255, 255), align="center")
    rect(bx + 176, ry1, 60, 24, r=4, fill=(220, 38, 38))
    text("클릭 (80ms)", bx + 176, ry1 + 6, w=60, h=14, size=7.6, weight="Bold", color=(255, 255, 255), align="center")

    rect(MARGIN_X + 344, ry1 - 2, 170, 28, r=6, fill=(254, 242, 242), stroke=(248, 113, 113), stroke_w=1.0)
    text("총 340ms 지연 ➔ 대기 14,290번", MARGIN_X + 344, ry1 + 2, w=170, h=14, size=8.5, weight="ExtraBold", color=(185, 28, 28), align="center")
    text("(예상 대기 48분 / 주요 좌석 매진)", MARGIN_X + 344, ry1 + 14, w=170, h=12, size=7.2, weight="Medium", color=(220, 38, 38), align="center")

    line(MARGIN_X + 14, y + 53, MARGIN_X + CONTENT_W - 14, y + 53, color=(241, 245, 249), width=1.0)

    # Row B: BEOMCHRO 0ms Engine
    ry2 = y + 64
    badge("BEOMCHRO 엔진", MARGIN_X + 14, ry2 + 2, 78, 20, bg=(14, 165, 233), fg=(255, 255, 255), size=8.5, weight="ExtraBold", r=5)
    # 0ms tiny bar + huge speed callout
    rect(bx, ry2, 8, 24, r=3, fill=(0, 210, 255))
    rect(bx + 14, ry2, 222, 24, r=5, fill=(240, 253, 244), stroke=(134, 239, 172), stroke_w=1.0)
    text("⚡ 버튼 활성화(disabled 해제) 즉시 0.1ms 자동 격발!", bx + 14, ry2 + 6, w=222, h=14, size=8.2, weight="ExtraBold", color=(21, 128, 61), align="center")

    grad_rect(MARGIN_X + 344, ry2 - 2, 170, 28, 6, (15, 23, 42), (30, 58, 138), angle=0, stroke=(0, 210, 255), stroke_w=1.2)
    text("총 0.1ms 격발 ➔ 대기 1번 선점!", MARGIN_X + 344, ry2 + 2, w=170, h=14, size=8.6, weight="ExtraBold", color=(0, 240, 255), align="center")
    text("(대기 시간 0초 / VIP석 즉시 입장)", MARGIN_X + 344, ry2 + 14, w=170, h=12, size=7.2, weight="Medium", color=(224, 242, 254), align="center")

    # Bottom explanation strip inside card
    rect(MARGIN_X + 10, y + 100, CONTENT_W - 20, 24, r=5, fill=(248, 250, 252))
    text("💡 핵심 원리: 브라우저 내부에 자동 장착된 MutationObserver 엔진이 버튼이 열리는 찰나(0.0001초)를 포착해 사람 대신 클릭합니다.", MARGIN_X + 18, y + 106, w=CONTENT_W - 36, h=16, size=8.3, weight="SemiBold", color=(51, 65, 85))

    # 4. PART 02: 5-Step Master Flowchart
    y = 592
    y = section_title("PART 02", "전체 진행 순서도 (5-Step Master Flowchart)", "복잡한 설정 없이 아래 5단계 순서도만 따라가면 즉시 준비가 완료됩니다.", y)

    steps = [
        ("STEP 1", "ZIP 다운로드", "GitHub 페이지에서\nDownload ZIP 클릭", (2, 132, 199)),
        ("STEP 2", "폴더 압축 해제", "다운로드된 압축파일을\n원하는 폴더에 풀기", (14, 165, 233)),
        ("STEP 3", "더블클릭 실행", "Mac: BEOMCHRO.app\nWin: run_windows.bat", (16, 185, 129)),
        ("STEP 4", "숫자 [1] 입력", "전용 브라우저 자동 실행\n& 0ms 배너 점등 확인", (99, 102, 241)),
        ("STEP 5", "정각 0ms 선점", "미리 로그인 후 대기하면\n오픈 즉시 1번 자동 진입!", (245, 158, 11)),
    ]

    box_w = 92.0
    gap = (CONTENT_W - (box_w * 5)) / 4.0
    box_h = 104.0

    for i, (st_num, st_title, st_desc, st_col) in enumerate(steps):
        bx = MARGIN_X + i * (box_w + gap)
        by = y + 4
        rect(bx, by, box_w, box_h, r=9, fill=(255, 255, 255), stroke=st_col, stroke_w=1.5)
        rect(bx, by, box_w, 24, r=9, fill=st_col)
        rect(bx, by + 14, box_w, 10, r=0, fill=st_col)
        text(st_num, bx, by + 6, w=box_w, h=14, size=8.5, weight="ExtraBold", color=(255, 255, 255), align="center")

        circle(bx + box_w / 2.0, by + 42, 11, fill=(241, 245, 249), stroke=st_col, stroke_w=1.0)
        text(str(i + 1), bx, by + 36, w=box_w, h=14, size=9.5, weight="Heavy", color=st_col, align="center")

        text(st_title, bx + 4, by + 57, w=box_w - 8, h=16, size=9.2, weight="ExtraBold", color=(15, 23, 42), align="center")
        text(st_desc, bx + 4, by + 73, w=box_w - 8, h=28, size=7.4, weight="Medium", color=(100, 116, 139), align="center", line_spacing=1.5)

        if i < 4:
            ax1 = bx + box_w + 2
            ax2 = bx + box_w + gap - 2
            arrow_right(ax1, by + box_h / 2.0, ax2, color=st_col, width=1.8, head=4.5)


# ==============================================================================
# PAGE 2: STEP 01 (GitHub Download UI Mockup) & STEP 02 (Python PATH UI Mockup)
# ==============================================================================
def render_page_2():
    draw_page_chrome(2, 5, "STEP 01 다운로드 & STEP 02 필수 환경 준비")

    y = 46
    y = section_title("STEP 01", "GitHub에서 프로그램 다운로드 및 압축 해제", "전달받은 저장소 링크에 접속해 ZIP 파일 하나로 전체 프로그램을 내려받습니다.", y)

    # Visual Mockup: GitHub Repository Page + Step Callouts
    mock_x = MARGIN_X
    mock_y = y
    mock_w = 305.0
    mock_h = 195.0
    draw_window_frame(mock_x, mock_y, mock_w, mock_h, "🌐 https://github.com/Keyco55/beomchro", dark=False)

    # Repo header inside mockup
    rect(mock_x + 12, mock_y + 34, mock_w - 24, 28, r=5, fill=(248, 250, 252), stroke=(226, 232, 240))
    text("📦 Keyco55 / beomchro", mock_x + 20, mock_y + 42, w=160, h=16, size=9.5, weight="ExtraBold", color=(15, 23, 42))
    badge("Public", mock_x + 150, mock_y + 41, 38, 15, bg=(226, 232, 240), fg=(71, 85, 105), size=7.0)

    # Green [ <> Code ] button
    code_bx = mock_x + mock_w - 92
    code_by = mock_y + 37
    rect(code_bx, code_by, 74, 22, r=5, fill=(22, 163, 74), stroke=(21, 128, 61), stroke_w=1.2)
    text("<> Code ▾", code_bx, code_by + 5, w=74, h=14, size=8.2, weight="ExtraBold", color=(255, 255, 255), align="center")
    # Callout circle (1)
    circle(code_bx - 8, code_by + 11, 9, fill=(239, 68, 68))
    text("1", code_bx - 17, code_by + 5, w=18, h=12, size=8.5, weight="Heavy", color=(255, 255, 255), align="center")

    # File list rows (dimmed)
    files = ["📁 BEOMCHRO.app", "📁 extension", "📁 simulator", "📄 run_windows.bat", "📄 BEOMCHRO_사용설명서.pdf"]
    for idx, fname in enumerate(files):
        fy = mock_y + 70 + idx * 22
        rect(mock_x + 12, fy, mock_w - 24, 20, r=0, fill=(255, 255, 255), stroke=(241, 245, 249))
        text(fname, mock_x + 20, fy + 4, w=180, h=14, size=8.0, weight="Medium", color=(71, 85, 105))

    # Dropdown menu overlay from [ <> Code ]
    dd_x = mock_x + mock_w - 158
    dd_y = mock_y + 62
    rect(dd_x, dd_y, 140, 88, r=7, fill=(255, 255, 255), stroke=(148, 163, 184), stroke_w=1.5)
    text("Clone (HTTPS)", dd_x + 10, dd_y + 8, w=120, h=12, size=7.8, weight="Bold", color=(51, 65, 85))
    rect(dd_x + 10, dd_y + 23, 120, 16, r=3, fill=(241, 245, 249))
    text("https://github.com/Keyco55...", dd_x + 14, dd_y + 26, w=112, h=12, size=6.5, color=(100, 116, 139), mono=True)
    line(dd_x, dd_y + 46, dd_x + 140, dd_y + 46, color=(226, 232, 240), width=1.0)

    # Highlighted Download ZIP button
    rect(dd_x + 6, dd_y + 53, 128, 28, r=5, fill=(239, 246, 255), stroke=(2, 132, 199), stroke_w=1.8)
    text("📥 Download ZIP", dd_x + 12, dd_y + 61, w=116, h=14, size=9.0, weight="ExtraBold", color=(2, 132, 199), align="center")
    circle(dd_x - 6, dd_y + 67, 9, fill=(239, 68, 68))
    text("2", dd_x - 15, dd_y + 61, w=18, h=12, size=8.5, weight="Heavy", color=(255, 255, 255), align="center")

    # Right Side Step Cards next to GitHub Mockup
    rx = mock_x + mock_w + 14
    rw = CONTENT_W - mock_w - 14
    step1_cards = [
        ("1단계: 저장소 주소 접속", "웹 브라우저 주소창에 아래 주소를 입력해 접속합니다.\nhttps://github.com/Keyco55/beomchro", (2, 132, 199)),
        ("2단계: [Code] ➔ [Download ZIP]", "우측 상단 초록색 [ <> Code ] 버튼(①)을 누른 뒤,\n메뉴 맨 아래 [ Download ZIP ](②)을 클릭합니다.", (22, 163, 74)),
        ("3단계: 압축 풀기 (중요!)", "다운로드된 beomchro-main.zip 파일을 우클릭하여\n바탕화면 등 찾기 쉬운 곳에 [압축 풀기] 해주세요.", (245, 158, 11)),
    ]
    for i, (st_t, st_d, st_c) in enumerate(step1_cards):
        cy = mock_y + i * 67
        rect(rx, cy, rw, 61, r=7, fill=(255, 255, 255), stroke=(226, 232, 240), stroke_w=1.0)
        rect(rx, cy, 5, 61, r=2, fill=st_c)
        text(st_t, rx + 13, cy + 8, w=rw - 20, h=16, size=9.5, weight="ExtraBold", color=(15, 23, 42))
        text(st_d, rx + 13, cy + 25, w=rw - 18, h=32, size=8.0, weight="Medium", color=(71, 85, 105), line_spacing=2.0)

    # STEP 02: Zero-Python Environment & Core Q&A Visual Guide
    y = mock_y + mock_h + 22
    y = section_title("STEP 02", "실행 전 필수 체크 & 핵심 질문 2가지 완벽 해결!", "윈도우 파이썬 미설치 컴퓨터에서도 즉시 작동하며, 가장 많이 물어보시는 2가지 질문을 먼저 확인하세요.", y)

    # 2-Column Environment Check Cards
    card_w = (CONTENT_W - 12) / 2.0
    rect(MARGIN_X, y, card_w, 72, r=8, fill=(255, 255, 255), stroke=(203, 213, 225), stroke_w=1.0)
    badge("필수 준비물 1", MARGIN_X + 12, y + 10, 68, 16, bg=(2, 132, 199), fg=(255, 255, 255), size=7.8, r=4)
    text("🌐 크롬 계열 웹 브라우저", MARGIN_X + 86, y + 10, w=160, h=18, size=10.2, weight="ExtraBold", color=(15, 23, 42))
    text("• Google Chrome (가장 권장)\n• 네이버 웨일(Whale) 또는 MS Edge\n※ 평소 사용하시는 브라우저가 깔려 있으면 준비 완료!", MARGIN_X + 12, y + 31, w=card_w - 24, h=38, size=8.0, weight="Medium", color=(71, 85, 105), line_spacing=1.8)

    cx2 = MARGIN_X + card_w + 12
    rect(cx2, y, card_w, 72, r=8, fill=(255, 255, 255), stroke=(16, 185, 129), stroke_w=1.2)
    badge("무설치 즉시 실행", cx2 + 12, y + 10, 74, 16, bg=(16, 185, 129), fg=(255, 255, 255), size=7.6, r=4)
    text("🪟 파이썬(Python) 설치 불필요!", cx2 + 92, y + 10, w=160, h=18, size=10.2, weight="ExtraBold", color=(6, 95, 70))
    text("• Windows: 파이썬이 없어도 내장 엔진으로 100% 즉시 작동!\n• Mac: BEOMCHRO.app 더블클릭 시 즉시 실행\n※ 복잡한 개발 프로그램 설치 없이 더블클릭만 하세요!", cx2 + 12, y + 31, w=card_w - 24, h=38, size=8.0, weight="Medium", color=(71, 85, 105), line_spacing=1.8)

    # Core Feedback Q1 & Q2 Visual Callout Card
    y += 84
    rect(MARGIN_X, y, CONTENT_W, 198, r=10, fill=(255, 251, 235), stroke=(245, 158, 11), stroke_w=1.4)
    badge("🔥 실전 핵심 Q&A", MARGIN_X + 14, y + 12, 92, 18, bg=(239, 68, 68), fg=(255, 255, 255), size=8.0, weight="ExtraBold", r=4)
    text("실제 사용자분들이 가장 궁금해하시는 핵심 질문 2가지! (티켓팅 전 필독)", MARGIN_X + 114, y + 13, w=395, h=18, size=9.8, weight="ExtraBold", color=(146, 64, 14))

    # Left Sub-card: Question 1 (ON/OFF & Target Check)
    q1_x = MARGIN_X + 12
    q1_y = y + 38
    q_w = (CONTENT_W - 36) / 2.0
    q_h = 148.0
    rect(q1_x, q1_y, q_w, q_h, r=8, fill=(255, 255, 255), stroke=(14, 165, 233), stroke_w=1.2)
    badge("질문 1", q1_x + 10, q1_y + 10, 42, 16, bg=(2, 132, 199), fg=(255, 255, 255), size=7.6, r=4)
    text("작동 중인지 어떻게 아나요? (ON/OFF 스위치)", q1_x + 58, q1_y + 10, w=q_w - 66, h=16, size=8.8, weight="ExtraBold", color=(15, 23, 42))
    text("우측 상단 컨트롤 박스에 직관적인 [🟢 ON / ⚪ OFF] 스위치와\n[🔍 작동확인] 버튼을 탑재했습니다!", q1_x + 12, q1_y + 31, w=q_w - 24, h=28, size=7.8, weight="SemiBold", color=(51, 65, 85), line_spacing=1.6)

    # Mini HUD illustration inside Q1 card
    rect(q1_x + 12, q1_y + 62, q_w - 24, 48, r=6, fill=(10, 14, 23), stroke=(0, 240, 255), stroke_w=1.2)
    text("⚡ BEOMCHRO v2.1", q1_x + 20, q1_y + 68, w=90, h=12, size=7.2, weight="ExtraBold", color=(255, 255, 255))
    badge("🔍 작동확인", q1_x + q_w - 118, q1_y + 67, 46, 13, bg=(30, 41, 59), fg=(226, 232, 240), size=6.5, r=3)
    badge("🟢 ON (작동중)", q1_x + q_w - 68, q1_y + 67, 50, 13, bg=(5, 150, 105), fg=(255, 255, 255), size=6.5, r=3)
    text("🎯 타겟 조준 완료: [남은시간 39:01] (파란 테두리 표시됨)", q1_x + 20, q1_y + 88, w=q_w - 40, h=14, size=7.0, weight="Bold", color=(110, 231, 183))

    text("✔ 예매 버튼 주변에 파란색 네온 테두리가 쳐져 있으면\n   100% 정상 조준된 상태입니다! ([🔍 작동확인] 클릭 시 레이저 점검)", q1_x + 12, q1_y + 115, w=q_w - 24, h=28, size=7.5, weight="Bold", color=(3, 105, 161), line_spacing=1.5)

    # Right Sub-card: Question 2 (Hands-Free at 00:00!)
    q2_x = q1_x + q_w + 12
    rect(q2_x, q1_y, q_w, q_h, r=8, fill=(255, 255, 255), stroke=(239, 68, 68), stroke_w=1.4)
    badge("질문 2", q2_x + 10, q1_y + 10, 42, 16, bg=(239, 68, 68), fg=(255, 255, 255), size=7.6, r=4)
    text("정각에 내가 누르나요? 마우스만 갖다 두나요?", q2_x + 58, q1_y + 10, w=q_w - 66, h=16, size=8.8, weight="ExtraBold", color=(185, 28, 28))
    text("정답: 둘 다 아닙니다! 마우스에서 아예 손을 떼고 계세요!", q2_x + 12, q1_y + 31, w=q_w - 24, h=16, size=8.2, weight="ExtraBold", color=(220, 38, 38))
    text("마우스 커서를 버튼 위에 올려두실 필요도 없고, 정각에 직접\n클릭하실 필요도 전혀 없습니다.", q2_x + 12, q1_y + 47, w=q_w - 24, h=26, size=7.6, weight="SemiBold", color=(51, 65, 85), line_spacing=1.5)

    rect(q2_x + 12, q1_y + 76, q_w - 24, 36, r=6, fill=(254, 242, 242), stroke=(248, 113, 113), stroke_w=1.0)
    text("✋ 직접 클릭 금지! (중복 클릭 시 대기열 튕김 위험)\n🖱️ 마우스 커서 위치 무관! (브라우저 내부 엔진이 직접 격발)", q2_x + 18, q1_y + 81, w=q_w - 36, h=26, size=7.4, weight="ExtraBold", color=(185, 28, 28), line_spacing=1.6)

    text("✔ [🟢 ON (작동중)]만 켜두고 화면만 띄워두시면 정각(00:00)\n   버튼이 열리는 찰나 프로그램이 0ms로 자동 클릭합니다!", q2_x + 12, q1_y + 116, w=q_w - 24, h=28, size=7.5, weight="Bold", color=(21, 128, 61), line_spacing=1.5)


# ==============================================================================
# PAGE 3: STEP 03 (OS Launch Mockups) & STEP 04 (TUI -> 0ms Browser HUD Diagram)
# ==============================================================================
def render_page_3():
    draw_page_chrome(3, 5, "STEP 03 프로그램 실행 & STEP 04 ON/OFF 상태창 확인")

    y = 46
    y = section_title("STEP 03", "운영체제별 원클릭 프로그램 실행 (더블클릭!)", "압축을 푼 폴더 안에서 내 컴퓨터 운영체제(Mac 또는 Windows)에 맞는 파일을 더블클릭합니다.", y)

    card_w = (CONTENT_W - 14) / 2.0
    card_h = 248.0

    # Left Card: macOS
    mx = MARGIN_X
    rect(mx, y, card_w, card_h, r=10, fill=(255, 255, 255), stroke=(14, 165, 233), stroke_w=1.4)
    grad_rect(mx, y, card_w, 30, 10, (15, 23, 42), (30, 58, 138), angle=0)
    rect(mx, y + 18, card_w, 12, r=0, fill=(15, 23, 42))
    text("🍎 macOS (맥북 / 아이맥) 실행 방법", mx + 14, y + 8, w=card_w - 28, h=16, size=10.0, weight="ExtraBold", color=(255, 255, 255))

    # Finder mockup inside macOS card
    draw_window_frame(mx + 12, y + 40, card_w - 24, 106, "📁 beomchro-main (Finder)", dark=False)
    # Highlighted BEOMCHRO.app icon row
    rect(mx + 20, y + 70, card_w - 40, 34, r=6, fill=(224, 242, 254), stroke=(2, 132, 199), stroke_w=1.5)
    rect(mx + 26, y + 75, 24, 24, r=5, fill=(15, 23, 42), stroke=(0, 210, 255), stroke_w=1.0)
    text("⚡", mx + 26, y + 79, w=24, h=18, size=12, color=(0, 240, 255), align="center")
    text("BEOMCHRO.app", mx + 56, y + 75, w=110, h=14, size=9.2, weight="ExtraBold", color=(15, 23, 42))
    text("애플리케이션 • 더블클릭 실행!", mx + 56, y + 88, w=130, h=12, size=7.4, weight="Bold", color=(2, 132, 199))
    badge("더블클릭!", mx + card_w - 76, y + 79, 50, 16, bg=(239, 68, 68), fg=(255, 255, 255), size=7.5, r=4)

    # Secondary BEOMCHRO.command row
    rect(mx + 20, y + 108, card_w - 40, 28, r=5, fill=(248, 250, 252))
    text("🐚 BEOMCHRO.command  (대체 실행 파일)", mx + 28, y + 116, w=190, h=14, size=8.0, weight="SemiBold", color=(71, 85, 105))

    # macOS Tip Box
    rect(mx + 12, y + 154, card_w - 24, 82, r=7, fill=(240, 249, 255), stroke=(186, 230, 253), stroke_w=1.0)
    text("💡 맥 최초 실행 시 보안 창이 뜰 때 해결법", mx + 20, y + 161, w=card_w - 40, h=14, size=8.6, weight="ExtraBold", color=(3, 105, 161))
    text("1. BEOMCHRO.app (또는 BEOMCHRO.command)을\n   마우스 [우클릭(두 손가락 탭)] 합니다.\n2. 메뉴에서 [열기] 클릭 ➔ 팝업창에서 [열기] 클릭!\n3. 최초 1회만 허용하면 다음부터는 더블클릭으로 즉시 열립니다.", mx + 20, y + 177, w=card_w - 36, h=55, size=7.7, weight="Medium", color=(12, 74, 110), line_spacing=1.8)

    # Right Card: Windows
    wx = MARGIN_X + card_w + 14
    rect(wx, y, card_w, card_h, r=10, fill=(255, 255, 255), stroke=(16, 185, 129), stroke_w=1.4)
    grad_rect(wx, y, card_w, 30, 10, (6, 78, 59), (16, 185, 129), angle=0)
    rect(wx, y + 18, card_w, 12, r=0, fill=(6, 78, 59))
    text("🪟 Windows 10 / 11 실행 방법 (파이썬 불필요!)", wx + 14, y + 8, w=card_w - 28, h=16, size=10.0, weight="ExtraBold", color=(255, 255, 255))

    # Explorer mockup inside Windows card
    draw_window_frame(wx + 12, y + 40, card_w - 24, 106, "📁 beomchro-main (파일 탐색기)", dark=False)
    rect(wx + 20, y + 70, card_w - 40, 34, r=6, fill=(236, 253, 245), stroke=(16, 185, 129), stroke_w=1.5)
    rect(wx + 26, y + 75, 24, 24, r=5, fill=(6, 78, 59))
    text("⚙", wx + 26, y + 79, w=24, h=18, size=12, color=(52, 211, 153), align="center")
    text("run_windows.bat", wx + 56, y + 75, w=115, h=14, size=9.2, weight="ExtraBold", color=(15, 23, 42))
    text("무설치 원클릭 실행기 • 더블클릭!", wx + 56, y + 88, w=130, h=12, size=7.4, weight="Bold", color=(5, 150, 105))
    badge("더블클릭!", wx + card_w - 76, y + 79, 50, 16, bg=(239, 68, 68), fg=(255, 255, 255), size=7.5, r=4)

    rect(wx + 20, y + 108, card_w - 40, 28, r=5, fill=(248, 250, 252))
    text("⚡ beomchro_win_native.ps1  (윈도우 내장 엔진)", wx + 28, y + 116, w=195, h=14, size=8.0, weight="SemiBold", color=(71, 85, 105))

    # Windows Tip Box
    rect(wx + 12, y + 154, card_w - 24, 82, r=7, fill=(240, 253, 244), stroke=(187, 247, 208), stroke_w=1.0)
    text("💡 파이썬 미설치 PC에서도 100% 즉시 작동합니다!", wx + 20, y + 161, w=card_w - 40, h=14, size=8.6, weight="ExtraBold", color=(22, 101, 52))
    text("1. 파이썬이 없는 윈도우 PC에서는 윈도우 기본 내장 엔진이\n   자동으로 가동되어 별도 프로그램 설치 없이 즉시 실행됩니다!\n2. 파란 보호창(SmartScreen)이 뜨면 [추가 정보] ➔ [실행] 클릭!", wx + 20, y + 177, w=card_w - 36, h=55, size=7.7, weight="Medium", color=(20, 83, 45), line_spacing=1.8)

    # STEP 04: TUI Dashboard -> Auto-Mounted 0ms Browser Diagram
    y += card_h + 22
    y = section_title("STEP 04", "숫자 [1] 입력 후 우측 상단 [🟢 ON / ⚪ OFF] 상태창 확인", "숫자 1을 누르면 한국시리즈 연습장과 실제 티켓 창이 열리며, 우측 상단에서 ON/OFF 제어가 가능합니다.", y)

    # Left Mockup: Dark Terminal TUI Dashboard
    tui_x = MARGIN_X
    tui_y = y
    tui_w = 224.0
    tui_h = 200.0
    draw_window_frame(tui_x, tui_y, tui_w, tui_h, "🐚 BEOMCHRO v2.1 Dashboard", dark=True)

    text("██ BEOMCHRO INTERCEPTOR v2.1 ██", tui_x + 10, tui_y + 31, w=tui_w - 20, h=14, size=8.0, weight="Bold", color=(0, 240, 255), mono=True)
    rect(tui_x + 10, tui_y + 47, tui_w - 20, 46, r=4, fill=(15, 23, 42), stroke=(59, 130, 246), stroke_w=0.8)
    text("• 클릭 엔진 : ACTIVE (Native)\n• 시뮬레이터: ONLINE (:8989)\n• 시간 오차 : +0.12 ms (동기화됨)", tui_x + 14, tui_y + 51, w=tui_w - 28, h=40, size=7.2, weight="Medium", color=(167, 243, 208), line_spacing=1.5, mono=True)

    # Operation Mode Box inside Terminal
    rect(tui_x + 10, tui_y + 99, tui_w - 20, 66, r=4, fill=(15, 23, 42), stroke=(234, 179, 8), stroke_w=0.9)
    rect(tui_x + 14, tui_y + 105, tui_w - 28, 17, r=3, fill=(6, 95, 70))
    text("1. 🚀 원클릭 0ms 티켓팅 브라우저 실행", tui_x + 16, tui_y + 108, w=tui_w - 32, h=13, size=7.3, weight="ExtraBold", color=(110, 231, 183))
    text("2. 🎯 화면 픽셀 색상 감시 모드\n3. ⏰ 서버 시간 정각 자동 클릭 모드\n4. ⚡ 마우스 초고속 격발 벤치마크", tui_x + 16, tui_y + 124, w=tui_w - 32, h=38, size=7.1, color=(203, 213, 225), line_spacing=1.4)

    # Prompt line at bottom of terminal
    rect(tui_x + 10, tui_y + 170, tui_w - 20, 22, r=4, fill=(30, 41, 59), stroke=(239, 68, 68), stroke_w=1.2)
    text("선택할 번호 입력 [1]:  1 ⏎ (엔터!)", tui_x + 14, tui_y + 175, w=tui_w - 28, h=14, size=7.8, weight="ExtraBold", color=(253, 224, 71))

    # Center Connector Arrow
    mid_x1 = tui_x + tui_w + 5
    mid_x2 = mid_x1 + 34
    arrow_right(mid_x1, tui_y + 100, mid_x2, color=(2, 132, 199), width=2.5, head=6)
    text("자동 장착", mid_x1 - 2, tui_y + 78, w=40, h=14, size=7.2, weight="ExtraBold", color=(2, 132, 199), align="center")

    # Right Mockup: Chrome Browser with Interactive v2.1 HUD Widget!
    br_x = mid_x2 + 5
    br_w = MARGIN_X + CONTENT_W - br_x
    br_h = 200.0
    draw_window_frame(br_x, tui_y, br_w, br_h, "🌐 Chrome (전용 티켓팅 세션)", dark=True)

    # Browser Tabs
    rect(br_x + 8, tui_y + 28, 120, 16, r=4, fill=(30, 41, 59))
    text("⚾ 한국시리즈 7차전 연습장", br_x + 12, tui_y + 31, w=112, h=12, size=6.8, weight="Bold", color=(0, 240, 255))
    rect(br_x + 132, tui_y + 28, 110, 16, r=4, fill=(15, 23, 42))
    text("🎫 NOL 티켓 한국시리즈", br_x + 136, tui_y + 31, w=102, h=12, size=6.8, color=(148, 163, 184))

    # Interactive v2.1 HUD Panel inside Browser Mockup
    hud_x = br_x + 12
    hud_y = tui_y + 50
    hud_w = br_w - 24
    rect(hud_x, hud_y, hud_w, 72, r=8, fill=(10, 14, 23), stroke=(0, 240, 255), stroke_w=1.6)
    circle(hud_x + 12, hud_y + 14, 4.0, fill=(0, 240, 255))
    text("⚡ BEOMCHRO v2.1", hud_x + 20, hud_y + 8, w=95, h=14, size=7.8, weight="ExtraBold", color=(255, 255, 255))
    badge("🔍 작동확인", hud_x + hud_w - 134, hud_y + 7, 54, 15, bg=(30, 41, 59), fg=(226, 232, 240), size=6.8, r=4)
    badge("🟢 ON (작동중)", hud_x + hud_w - 74, hud_y + 7, 66, 15, bg=(5, 150, 105), fg=(255, 255, 255), size=6.8, r=4)

    rect(hud_x + 8, hud_y + 26, hud_w - 16, 20, r=4, fill=(17, 24, 39), stroke=(51, 65, 85), stroke_w=0.8)
    text("🎯 타겟 조준 완료: [남은시간 39:01] (파란 테두리 표시중)", hud_x + 14, hud_y + 31, w=hud_w - 28, h=12, size=7.1, weight="Bold", color=(110, 231, 183))
    text("✋ 정각에 직접 누르거나 마우스 커서를 올려두지 마세요! (0ms 자동 클릭)", hud_x + 10, hud_y + 51, w=hud_w - 20, h=14, size=6.9, weight="ExtraBold", color=(253, 224, 71))

    # Explanation box below HUD inside Browser Mockup
    rect(br_x + 12, tui_y + 128, br_w - 24, 62, r=7, fill=(17, 24, 39), stroke=(16, 185, 129), stroke_w=1.1)
    text("✔ [🟢 ON / ⚪ OFF] 스위치 & [🔍 작동확인] 사용법", br_x + 20, tui_y + 134, w=br_w - 40, h=14, size=8.0, weight="ExtraBold", color=(110, 231, 183))
    text("• 우측 상단 [🟢 ON (작동중)] 버튼을 누르면 언제든 감시를 켜고 끌 수 있습니다.\n• [🔍 작동확인]을 누르면 현재 페이지의 예매 버튼을 찾아 파란 레이저로 비춰줍니다.\n• 정각에는 마우스에서 손을 떼고 화면만 켜두시면 0ms로 자동 클릭됩니다!", br_x + 20, tui_y + 149, w=br_w - 36, h=38, size=7.1, weight="Medium", color=(226, 232, 240), line_spacing=1.5)


# ==============================================================================
# PAGE 4: STEP 05 (Session Persistence Diagram) & STEP 06 (Simulator Visual Guide)
# ==============================================================================
def render_page_4():
    draw_page_chrome(4, 5, "STEP 05 로그인 영구 보존 & STEP 06 한국시리즈 실전 연습장")

    y = 46
    y = section_title("STEP 05", "사전 로그인 & 본인인증(PASS) 영구 보존 원리", "티켓팅 당일 로그인을 다시 하느라 시간을 허비하지 않도록 전용 프로필이 세션을 안전하게 보관합니다.", y)

    # Architecture Flow Diagram for Persistent Profile
    rect(MARGIN_X, y, CONTENT_W, 108, r=10, fill=(255, 255, 255), stroke=(203, 213, 225), stroke_w=1.0)

    b1_x = MARGIN_X + 14
    b_y = y + 14
    b_w = 148.0
    b_h = 80.0
    rect(b1_x, b_y, b_w, b_h, r=8, fill=(239, 246, 255), stroke=(59, 130, 246), stroke_w=1.2)
    badge("1. 사전 로그인 (최초 1회)", b1_x + 12, b_y + 10, 124, 16, bg=(37, 99, 235), fg=(255, 255, 255), size=7.6, r=4)
    text("전용 브라우저에서 놀티켓/인터파크\n로그인 및 본인인증(PASS/카카오)\n미리 완료", b1_x + 10, b_y + 32, w=b_w - 20, h=42, size=7.8, weight="SemiBold", color=(30, 58, 138), align="center", line_spacing=1.8)

    arrow_right(b1_x + b_w + 6, b_y + b_h / 2.0, b1_x + b_w + 28, color=(37, 99, 235), width=2.0)

    b2_x = b1_x + b_w + 32
    rect(b2_x, b_y, b_w + 16, b_h, r=8, fill=(245, 243, 255), stroke=(139, 92, 246), stroke_w=1.2)
    badge("2. 전용 프로필 자동 금고 저장", b2_x + 12, b_y + 10, 140, 16, bg=(124, 58, 237), fg=(255, 255, 255), size=7.6, r=4)
    text("~/.beomchro/browser_profile\n경로에 로그인 쿠키와 인증 세션이\n독립적으로 영구 저장됨", b2_x + 10, b_y + 32, w=b_w - 4, h=42, size=7.8, weight="SemiBold", color=(76, 29, 149), align="center", line_spacing=1.8)

    arrow_right(b2_x + b_w + 22, b_y + b_h / 2.0, b2_x + b_w + 44, color=(124, 58, 237), width=2.0)

    b3_x = b2_x + b_w + 48
    rect(b3_x, b_y, b_w, b_h, r=8, fill=(240, 253, 244), stroke=(16, 185, 129), stroke_w=1.2)
    badge("3. 티켓팅 당일 즉시 투입", b3_x + 12, b_y + 10, 124, 16, bg=(5, 150, 105), fg=(255, 255, 255), size=7.6, r=4)
    text("브라우저를 닫았다가 당일에 다시\n켜도 로그인이 그대로 유지되어\n즉시 예매 대기 가능!", b3_x + 10, b_y + 32, w=b_w - 20, h=42, size=7.8, weight="SemiBold", color=(6, 95, 70), align="center", line_spacing=1.8)

    # STEP 06: Simulator Practice Visual Mockup (2026 Korean Series Game 7 Gate Replica)
    y += 126
    y = section_title("STEP 06", "내장 실전 연습장(2026 한국시리즈 7차전 게이트)으로 작동 검증하기", "실제 인터파크/NOL 티켓과 100% 동일한 HTML 구조의 내장 연습장(http://localhost:8989)에서 직접 테스트하세요.", y)

    # Full-width Visual Mockup of 2026 Korean Series Game 7 Gate Simulator UI + 1st Place Result Modal
    sim_x = MARGIN_X
    sim_y = y
    sim_w = CONTENT_W
    sim_h = 285.0
    draw_window_frame(sim_x, sim_y, sim_w, sim_h, "⚡ BEOMCHRO 내장 연습장 (http://localhost:8989) — 2026 한국시리즈 7차전 KT vs 삼성", dark=True)

    # Top Control Toolbar inside Simulator
    rect(sim_x + 14, sim_y + 32, sim_w - 28, 44, r=7, fill=(30, 41, 59), stroke=(51, 65, 85), stroke_w=1.0)
    badge("화면 1: 7차전 게이트", sim_x + 22, sim_y + 42, 86, 24, bg=(65, 84, 255), fg=(255, 255, 255), size=7.4, weight="ExtraBold", r=5)

    # [5초 카운트다운] button with callout ①
    rect(sim_x + 116, sim_y + 41, 102, 26, r=5, fill=(37, 99, 235), stroke=(96, 165, 250), stroke_w=1.2)
    text("⏱️ 5초 카운트다운", sim_x + 116, sim_y + 48, w=102, h=14, size=8.0, weight="ExtraBold", color=(255, 255, 255), align="center")
    circle(sim_x + 116, sim_y + 41, 8.5, fill=(239, 68, 68))
    text("1", sim_x + 108, sim_y + 35, w=16, h=12, size=8.0, weight="Heavy", color=(255, 255, 255), align="center")

    # [즉시 오픈] button
    rect(sim_x + 224, sim_y + 41, 122, 26, r=5, fill=(234, 88, 12))
    text("⚡ 즉시 오픈 (0ms 테스트)", sim_x + 224, sim_y + 48, w=122, h=14, size=8.0, weight="ExtraBold", color=(255, 255, 255), align="center")

    # Status indicator on right of toolbar
    badge("🟢 ON (작동중) • 타겟 조준됨", sim_x + 354, sim_y + 44, 156, 20, bg=(6, 78, 59), fg=(110, 231, 183), size=7.4, weight="ExtraBold", r=10)

    # Left: Real Interpark Gate Card (White Gate Layout Replica)
    rect(sim_x + 14, sim_y + 84, 228, 186, r=8, fill=(255, 255, 255), stroke=(203, 213, 225), stroke_w=1.2)
    text("2026 KBO 포스트시즌", sim_x + 26, sim_y + 94, w=200, h=12, size=7.5, weight="Bold", color=(100, 116, 139))
    text("2026 한국시리즈 7차전 KT vs 삼성", sim_x + 26, sim_y + 108, w=204, h=18, size=10.2, weight="Heavy", color=(15, 23, 42))
    line(sim_x + 26, sim_y + 130, sim_x + 230, sim_y + 130, color=(226, 232, 240), width=1.0)
    text("• 관람일시 : 2026.11.01 (일) 14:00\n• 관람장소 : 수원 KT위즈파크\n• 버튼상태 : 남은시간 00:05 ➔ 예매하기!", sim_x + 26, sim_y + 138, w=204, h=44, size=7.6, weight="SemiBold", color=(51, 65, 85), line_spacing=1.8)

    # Glowing [남은시간 00:00 -> 예매하기] Button with Neon Target Outline!
    grad_rect(sim_x + 24, sim_y + 196, 208, 46, 8, (65, 84, 255), (37, 99, 235), angle=0, stroke=(0, 240, 255), stroke_w=2.2)
    text("예매하기 (0ms 자동 격발!)", sim_x + 24, sim_y + 205, w=208, h=16, size=10.2, weight="Heavy", color=(255, 255, 255), align="center")
    text("파란 테두리 조준 ➔ 손 떼고 있으면 자동 클릭!", sim_x + 24, sim_y + 223, w=208, h=12, size=7.1, weight="Bold", color=(224, 242, 254), align="center")
    circle(sim_x + 24, sim_y + 196, 8.5, fill=(239, 68, 68))
    text("2", sim_x + 16, sim_y + 190, w=16, h=12, size=8.0, weight="Heavy", color=(255, 255, 255), align="center")

    text("✋ 마우스를 올리거나 직접 누르지 마세요!", sim_x + 24, sim_y + 248, w=208, h=14, size=7.4, weight="ExtraBold", color=(220, 38, 38), align="center")

    # Right: Queue 1st Place Intercept Modal Box
    mod_x = sim_x + 254
    mod_y = sim_y + 84
    mod_w = sim_w - 268
    mod_h = 186.0
    rect(mod_x, mod_y, mod_w, mod_h, r=10, fill=(18, 22, 34), stroke=(0, 240, 255), stroke_w=1.8)
    rect(mod_x, mod_y, mod_w, 24, r=10, fill=(10, 14, 23))
    rect(mod_x, mod_y + 14, mod_w, 10, r=0, fill=(10, 14, 23))
    text("🎉 0ms 인터셉트 성공! (대기열 1번 진입)", mod_x + 12, mod_y + 6, w=mod_w - 24, h=14, size=7.8, weight="ExtraBold", color=(0, 240, 255))

    circle(mod_x + mod_w - 14, mod_y + 12, 8.5, fill=(239, 68, 68))
    text("3", mod_x + mod_w - 22, mod_y + 6, w=16, h=12, size=8.0, weight="Heavy", color=(255, 255, 255), align="center")

    # Queue Rank #1 Box
    grad_rect(mod_x + 16, mod_y + 34, mod_w - 32, 74, 8, (15, 23, 42), (30, 58, 138), angle=10, stroke=(0, 240, 255), stroke_w=1.0)
    text("나의 대기 순번", mod_x + 16, mod_y + 41, w=mod_w - 32, h=12, size=8.0, weight="Bold", color=(148, 163, 184), align="center")
    text("대기 1번", mod_x + 16, mod_y + 55, w=mod_w - 32, h=26, size=22.0, weight="Heavy", color=(0, 240, 255), align="center")
    text("예상 대기 시간: 0분 00초 (좌석 선택창 즉시 진입)", mod_x + 16, mod_y + 86, w=mod_w - 32, h=14, size=8.0, weight="Bold", color=(167, 243, 208), align="center")

    # Stats rows inside modal
    text("• 반응 속도 (Latency) :  0.14 ms (0ms 자동 클릭)\n• 격발 방식 (Trigger) :  BEOMCHRO 0ms 자동 격발 성공!\n• 검증 결과 (Status)  :  ★ 실전 작동 100% 정상 확인됨!", mod_x + 20, mod_y + 118, w=mod_w - 40, h=58, size=8.0, weight="Bold", color=(226, 232, 240), line_spacing=2.5)

    # Bottom 3-step practice summary strip
    py = sim_y + sim_h + 12
    rect(MARGIN_X, py, CONTENT_W, 74, r=8, fill=(240, 249, 255), stroke=(14, 165, 233), stroke_w=1.0)
    text("🎮 한국시리즈 7차전 내장 연습장 5초 검증법 (① ➔ ② ➔ ③)", MARGIN_X + 14, py + 8, w=400, h=16, size=9.6, weight="ExtraBold", color=(3, 105, 161))
    text("① 상단 [⏱️ 5초 카운트다운] 버튼을 클릭한 뒤 마우스에서 아예 손을 떼고 기다립니다.\n② [남은시간 00:05] 버튼이 00:00이 되어 [예매하기]로 열리는 찰나, 프로그램이 0ms로 자동 클릭합니다.\n③ 화면에 [나의 대기 순번: 1번] 창이 뜨면 내 컴퓨터에서 100% 완벽하게 작동 중인 것입니다!", MARGIN_X + 14, py + 26, w=CONTENT_W - 28, h=44, size=8.1, weight="SemiBold", color=(15, 23, 42), line_spacing=2.0)


# ==============================================================================
# PAGE 5: STEP 07 (D-Day Timeline Flowchart) & Modes Table + FAQ
# ==============================================================================
def render_page_5():
    draw_page_chrome(5, 5, "STEP 07 티켓팅 당일 타임라인 & 자주 묻는 질문(FAQ)")

    y = 46
    y = section_title("STEP 07", "티켓팅 당일(D-Day) 실전 타임라인 가이드", "티켓 오픈 15분 전부터 정각(00.000초)까지 아래 타임라인 순서대로만 진행하세요.", y)

    timeline = [
        ("OPEN 15분 전", "프로그램 실행 & 숫자 [1] 입력", "BEOMCHRO.app(Mac) 또는 run_windows.bat(Win)을 더블클릭해 실행한 뒤,\n키보드 숫자 [1]을 눌러 0ms 전용 브라우저를 엽니다.", (2, 132, 199), "준비 시작"),
        ("OPEN 10분 전", "사이트 접속 & 로그인/본인인증 확인", "전용 브라우저에서 놀티켓/인터파크에 접속하여 로그인이 유지되어 있는지\n확인하고, 팝업 차단 해제 및 본인인증 여부를 점검합니다.", (14, 165, 233), "세션 점검"),
        ("OPEN 3분 전", "게이트 페이지 대기 & [🟢 ON] 확인", "예매할 경기/공연 게이트 페이지([남은시간 XX:XX])를 띄워 두고,\n우측 상단 위젯이 [🟢 ON (작동중)]인지, 버튼에 파란 테두리가 있는지 확인합니다.", (16, 185, 129), "조준 완료"),
        ("정각 00.000초", "손 떼고 대기 ➔ 0ms 자동 클릭 & 1번 진입!", "직접 누르거나 마우스 커서를 올려두지 마세요! 가만히 화면만 켜두시면\n[남은시간 00:00]이 풀리는 즉시 0ms로 자동 클릭하여 대기열 1번으로 진입합니다!", (239, 68, 68), "🔥 손 떼고 대기!"),
    ]

    for i, (t_time, t_title, t_desc, t_col, t_tag) in enumerate(timeline):
        ty = y + i * 64
        # Left timeline node
        badge(t_time, MARGIN_X, ty + 14, 84, 24, bg=t_col, fg=(255, 255, 255), size=8.5, weight="ExtraBold", r=6)
        if i < 3:
            arrow_down(MARGIN_X + 42, ty + 40, ty + 76, color=t_col, width=2.0, head=4.5)

        # Right card
        cx = MARGIN_X + 96
        cw = CONTENT_W - 96
        bg_fill = (255, 245, 245) if i == 3 else (255, 255, 255)
        rect(cx, ty, cw, 54, r=8, fill=bg_fill, stroke=t_col, stroke_w=1.3 if i == 3 else 1.0)
        rect(cx, ty, 5, 54, r=2, fill=t_col)
        text(t_title, cx + 14, ty + 7, w=cw - 90, h=16, size=9.8, weight="ExtraBold", color=(15, 23, 42))
        badge(t_tag, cx + cw - 74, ty + 7, 64, 16, bg=t_col, fg=(255, 255, 255), size=7.4, weight="ExtraBold", r=4)
        text(t_desc, cx + 14, ty + 24, w=cw - 24, h=28, size=7.9, weight="Medium", color=(71, 85, 105), line_spacing=1.6)

    # Appendix 1: TUI 5 Operation Modes Summary Table
    y += 268
    y = section_title("APPENDIX", "대시보드 5가지 동작 모드 요약표", "기본적으로 [1번 모드]만 사용하시면 되며, 필요에 따라 고급 보조 모드를 함께 사용할 수 있습니다.", y)

    modes = [
        ("1번 (기본 권장)", "원클릭 0ms 티켓팅 브라우저", "0ms 엔진 자동 장착 브라우저 기동 + 한국시리즈 7차전 연습장", "★★★★★ (필수)"),
        ("2번 (보조 모드)", "화면 픽셀 색상 감시 모드", "지정한 마우스 좌표의 버튼 색상이 바뀌는 순간 하드웨어 클릭", "★★★★☆"),
        ("3번 (보조 모드)", "서버 시간 정각 자동 클릭", "서버 시간 오차(Time Skew)를 보정해 목표 시각 정각 자동 클릭", "★★★★☆"),
        ("4번 (테스트용)", "마우스 초고속 격발 벤치마크", "내 컴퓨터의 OS 네이티브 마우스 클릭 반응속도(0.1ms) 측정", "★★★☆☆"),
        ("5번 (점검용)", "시스템 종합 진단 (Doctor)", "브라우저, 마우스 엔진, 확장프로그램, 연습장 파일 상태 일괄 진단", "★★★☆☆"),
    ]

    th_y = y
    rect(MARGIN_X, th_y, CONTENT_W, 22, r=4, fill=(15, 23, 42))
    text("모드 번호", MARGIN_X + 10, th_y + 5, w=85, h=14, size=8.0, weight="ExtraBold", color=(255, 255, 255))
    text("기능 명칭", MARGIN_X + 100, th_y + 5, w=125, h=14, size=8.0, weight="ExtraBold", color=(255, 255, 255))
    text("상세 동작 설명", MARGIN_X + 228, th_y + 5, w=220, h=14, size=8.0, weight="ExtraBold", color=(255, 255, 255))
    text("추천도", MARGIN_X + 448, th_y + 5, w=72, h=14, size=8.0, weight="ExtraBold", color=(0, 240, 255), align="center")

    for idx, (m_no, m_name, m_desc, m_star) in enumerate(modes):
        ry = th_y + 22 + idx * 22
        row_bg = (240, 249, 255) if idx == 0 else ((255, 255, 255) if idx % 2 == 1 else (248, 250, 252))
        rect(MARGIN_X, ry, CONTENT_W, 22, r=0, fill=row_bg, stroke=(226, 232, 240), stroke_w=0.6)
        text(m_no, MARGIN_X + 10, ry + 5, w=85, h=14, size=7.8, weight="ExtraBold" if idx == 0 else "Bold", color=(2, 132, 199) if idx == 0 else (51, 65, 85))
        text(m_name, MARGIN_X + 100, ry + 5, w=125, h=14, size=7.8, weight="Bold", color=(15, 23, 42))
        text(m_desc, MARGIN_X + 228, ry + 5, w=220, h=14, size=7.5, weight="Medium", color=(71, 85, 105))
        text(m_star, MARGIN_X + 448, ry + 5, w=72, h=14, size=7.5, weight="ExtraBold", color=(2, 132, 199) if idx == 0 else (100, 116, 139), align="center")

    # FAQ Section at bottom
    fy = th_y + 22 + len(modes) * 22 + 16
    text("❓ 자주 묻는 질문 & 빠른 해결 (FAQ)", MARGIN_X, fy, w=300, h=18, size=11.0, weight="ExtraBold", color=(15, 23, 42))
    fy += 20

    faqs = [
        ("Q1. 숫자 1을 눌렀는데 파란불만 들어오고 작동 중인지 모르겠어요! ON/OFF가 있나요?",
         "A. 브라우저 우측 상단 위젯에 [🟢 ON (작동중) / ⚪ OFF] 버튼과 [🔍 작동확인] 버튼이 있습니다! 예매 버튼에 파란 테두리가 있으면 정상 조준된 상태입니다."),
        ("Q2. 정각(00:00)에 제가 직접 누르는 건가요, 아니면 마우스 커서만 갖다 두는 건가요?",
         "A. 둘 다 아닙니다! 마우스에서 아예 손을 떼고 가만히 계세요. [🟢 ON] 상태면 정각에 버튼이 열리는 순간 프로그램이 0ms로 자동 클릭합니다."),
        ("Q3. 윈도우 컴퓨터에 파이썬(Python)이 안 깔려 있는데 작동하나요?",
         "A. 네! run_windows.bat을 실행하면 윈도우 기본 내장 엔진이 자동으로 작동하므로 파이썬을 전혀 설치할 필요가 없습니다."),
    ]

    for idx, (q_str, a_str) in enumerate(faqs):
        cy = fy + idx * 44
        rect(MARGIN_X, cy, CONTENT_W, 40, r=6, fill=(255, 255, 255), stroke=(226, 232, 240), stroke_w=0.9)
        text(q_str, MARGIN_X + 10, cy + 5, w=CONTENT_W - 20, h=14, size=8.1, weight="ExtraBold", color=(3, 105, 161))
        text(a_str, MARGIN_X + 10, cy + 20, w=CONTENT_W - 20, h=18, size=7.5, weight="Medium", color=(71, 85, 105))


# ==============================================================================
# Main PDF Build Entry
# ==============================================================================
def generate_pdf(output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    url = NSURL.fileURLWithPath_(str(output_path))
    media_box = NSMakeRect(0, 0, PAGE_W, PAGE_H)
    pdf_ctx = Quartz.CGPDFContextCreateWithURL(url, media_box, None)

    pages = [render_page_1, render_page_2, render_page_3, render_page_4, render_page_5]

    for render_fn in pages:
        Quartz.CGPDFContextBeginPage(pdf_ctx, None)
        Quartz.CGContextSaveGState(pdf_ctx)
        # Flip coordinate system so (0, 0) is top-left
        Quartz.CGContextTranslateCTM(pdf_ctx, 0.0, PAGE_H)
        Quartz.CGContextScaleCTM(pdf_ctx, 1.0, -1.0)

        ns_ctx = AppKit.NSGraphicsContext.graphicsContextWithCGContext_flipped_(pdf_ctx, True)
        AppKit.NSGraphicsContext.setCurrentContext_(ns_ctx)

        render_fn()

        Quartz.CGContextRestoreGState(pdf_ctx)
        Quartz.CGPDFContextEndPage(pdf_ctx)

    Quartz.CGPDFContextClose(pdf_ctx)
    print(f"✔ Vector 5-Page Visual PDF generated: {output_path} ({output_path.stat().st_size:,} bytes)")


def main():
    generate_pdf(OUTPUT_PROJECT)
    try:
        shutil.copy2(OUTPUT_PROJECT, OUTPUT_DOWNLOADS)
        print(f"✔ Copied to Downloads: {OUTPUT_DOWNLOADS}")
    except Exception as e:
        print(f"ℹ️ Downloads copy will be completed outside sandbox: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
