/**
 * BEOMCHRO Manifest V3 Content Script v2.1
 * 0ms Ultra Queue Interceptor Engine with Interactive ON/OFF Control & Visual Target Lock
 */

(() => {
  'use strict';

  if (window.__BEOMCHRO_INITIALIZED__) return;
  window.__BEOMCHRO_INITIALIZED__ = true;

  // Inject execution flag into the main world page context
  try {
    const script = document.createElement('script');
    script.textContent = `
      window.__BEOMCHRO_ACTIVE__ = true;
      window.__BEOMCHRO_VERSION__ = '2.1.0';
    `;
    (document.head || document.documentElement).appendChild(script);
    script.remove();
  } catch (e) {
    // Isolated fallback
  }

  window.__BEOMCHRO_ACTIVE__ = true;
  window.__BEOMCHRO_VERSION__ = '2.1.0';

  // State
  let isEnabled = true;
  let hasTriggered = false;
  let observer = null;
  let hudEl = null;
  let lastStatusHtml = '';
  let lastGuideHtml = '';

  // Primary Gate & Booking Button Selectors (Matches real Interpark/NOL Gate DOM & Simulator)
  const GATE_BUTTON_SELECTORS = [
    '#btn-booking',
    '.buttons button[class*="_button_"]',
    '.buttons button',
    'button[class*="_button_"][class*="_primary_"]',
    '.btn-booking-action',
    '#ticketReservationBtn',
    'a.btn_reserve',
    'button.booking-btn',
    'button[data-action="book"]',
    'a[onclick*="fnBook"]',
    'a[onclick*="reserve"]'
  ];

  function syncMainWorldFlag() {
    window.__BEOMCHRO_ACTIVE__ = isEnabled;
    try {
      document.documentElement.setAttribute('data-beomchro-enabled', isEnabled ? 'true' : 'false');
    } catch (e) {}
  }
  syncMainWorldFlag();

  function setStatusHtml(statusEl, html) {
    if (statusEl && lastStatusHtml !== html) {
      lastStatusHtml = html;
      statusEl.innerHTML = html;
    }
  }

  function setGuideHtml(guideEl, html) {
    if (guideEl && lastGuideHtml !== html) {
      lastGuideHtml = html;
      guideEl.innerHTML = html;
    }
  }

  // Find target gate button on page (even while disabled before open)
  function findTargetButton() {
    for (const sel of GATE_BUTTON_SELECTORS) {
      const el = document.querySelector(sel);
      if (el) return el;
    }
    return null;
  }

  // Check if target button has transitioned from "Waiting/Disabled" to "OPEN/Enabled"
  function isButtonReadyToClick(el) {
    if (!el) return false;
    if (el.hasAttribute('disabled') || el.disabled === true) return false;
    if (el.getAttribute('aria-disabled') === 'true') return false;

    const cls = typeof el.className === 'string' ? el.className : '';
    if (/disabled/i.test(cls)) return false;

    const txt = (el.textContent || '').trim();
    if (/남은\s*시간|오픈\s*대기|오픈\s*예정|잠시\s*후/.test(txt)) return false;

    return true;
  }

  // Highlight the locked button on the page so user has 100% visual certainty (DOM-write guarded)
  function updateTargetHighlight() {
    const target = findTargetButton();
    const statusEl = document.getElementById('beomchro-target-status');
    const guideEl = document.getElementById('beomchro-action-guide');

    if (!target) {
      const listBtns = document.querySelectorAll('.joint-rectangle-button--variant_outlined_primary, .game-cta-btn');
      if (listBtns.length > 0) {
        setStatusHtml(statusEl, `<span style="color:#38bdf8;">📋 경기 목록 화면 감지됨 (${listBtns.length}개 경기)</span>`);
        if (isEnabled && !hasTriggered) {
          setGuideHtml(guideEl, '💡 원하는 경기의 <strong>[예매하기]</strong>를 눌러 오픈 대기(게이트) 화면으로 이동하세요.');
        }
      } else {
        setStatusHtml(statusEl, `<span style="color:#94a3b8;">🔍 예매 게이트 버튼 탐색 중...</span>`);
      }
      return;
    }

    const btnText = (target.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 28) || '예매 버튼';
    const ready = isButtonReadyToClick(target);

    // Apply visual target lock ring on the target button only when state changes
    const lockState = !isEnabled ? 'paused' : (hasTriggered ? 'triggered' : 'locked');
    if (target.getAttribute('data-beomchro-locked') !== lockState) {
      target.setAttribute('data-beomchro-locked', lockState);
      if (lockState === 'locked') {
        target.style.outline = '3px solid #00f0ff';
        target.style.outlineOffset = '3px';
      } else if (lockState === 'paused') {
        target.style.outline = '2px dashed #64748b';
        target.style.outlineOffset = '3px';
      } else {
        target.style.outline = '3px solid #10b981';
        target.style.outlineOffset = '3px';
      }
    }

    if (!hasTriggered) {
      if (!isEnabled) {
        setStatusHtml(statusEl, `<span style="color:#94a3b8;">⏸ 조준 일시정지됨: [${btnText}] (우측 위 ON 버튼을 켜세요)</span>`);
      } else if (!ready) {
        setStatusHtml(statusEl, `<span style="color:#00f0ff;">🎯 타겟 조준 완료: <strong>[${btnText}]</strong> (오픈 대기 감시 중)</span>`);
      } else {
        setStatusHtml(statusEl, `<span style="color:#10b981;">⚡ 버튼 오픈 감지됨: <strong>[${btnText}]</strong></span>`);
      }
    }
  }

  // Create Interactive Control Widget HUD at top-right
  function createHUD() {
    if (hudEl || !document.body) return;

    hudEl = document.createElement('div');
    hudEl.id = 'beomchro-hud';
    hudEl.innerHTML = `
      <div id="beomchro-hud-box" style="
        position: fixed;
        top: 14px;
        right: 16px;
        z-index: 2147483647;
        width: 340px;
        background: rgba(10, 14, 24, 0.96);
        border: 2px solid #00f0ff;
        box-shadow: 0 8px 30px rgba(0, 240, 255, 0.35);
        color: #f8fafc;
        padding: 12px 14px;
        border-radius: 12px;
        font-family: -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', 'Pretendard', sans-serif;
        font-size: 12px;
        line-height: 1.45;
        backdrop-filter: blur(12px);
        user-select: none;
        transition: all 0.2s ease;
      ">
        <!-- Top Row: Status Dot + Title + ON/OFF Switch -->
        <div style="display:flex; align-items:center; justify-content:space-between; gap:8px; margin-bottom:8px;">
          <div style="display:flex; align-items:center; gap:7px;">
            <span id="beomchro-hud-dot" style="display:inline-block; width:10px; height:10px; border-radius:50%; background:#10b981; box-shadow:0 0 10px #10b981; animation: beomchroPulse 1s infinite;"></span>
            <span id="beomchro-hud-title" style="font-weight:800; font-size:13px; color:#ffffff; letter-spacing:-0.2px;">⚡ BEOMCHRO 0ms 엔진</span>
          </div>
          <div style="display:flex; align-items:center; gap:5px;">
            <button id="beomchro-test-btn" type="button" style="
              background: rgba(255,255,255,0.1);
              color: #e2e8f0;
              border: 1px solid rgba(255,255,255,0.2);
              border-radius: 6px;
              padding: 4px 8px;
              font-size: 11px;
              font-weight: 700;
              cursor: pointer;
            " title="현재 버튼 조준 상태를 화면에서 확인합니다">🔍 작동확인</button>
            <button id="beomchro-toggle-btn" type="button" style="
              background: linear-gradient(135deg, #10b981, #059669);
              color: #ffffff;
              border: none;
              border-radius: 6px;
              padding: 4px 10px;
              font-size: 11px;
              font-weight: 800;
              cursor: pointer;
              box-shadow: 0 2px 8px rgba(16, 185, 129, 0.4);
            ">🟢 ON (작동중)</button>
          </div>
        </div>

        <!-- Middle Row: Live Target Lock Status -->
        <div id="beomchro-target-status" style="
          background: rgba(255, 255, 255, 0.06);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 7px;
          padding: 6px 9px;
          font-size: 11.5px;
          font-weight: 600;
          margin-bottom: 7px;
          color: #00f0ff;
        ">🎯 타겟 버튼 탐색 중...</div>

        <!-- Bottom Row: Clear User Instruction (Solves Question 2!) -->
        <div id="beomchro-action-guide" style="
          background: rgba(245, 158, 11, 0.14);
          border-left: 3px solid #f59e0b;
          border-radius: 4px;
          padding: 5px 8px;
          font-size: 11px;
          color: #fde68a;
          font-weight: 600;
        ">✋ <strong>직접 누르거나 마우스를 올려두지 마세요!</strong><br>정각(00:00) 오픈 즉시 프로그램이 0ms로 자동 클릭합니다.</div>
      </div>
      <style>
        @keyframes beomchroPulse {
          0% { opacity: 0.35; transform: scale(0.88); }
          50% { opacity: 1; transform: scale(1.15); }
          100% { opacity: 0.35; transform: scale(0.88); }
        }
        @keyframes beomchroFlash {
          0%, 100% { box-shadow: 0 0 0 4px #00f0ff, 0 0 30px #00f0ff; }
          50% { box-shadow: 0 0 0 8px #f59e0b, 0 0 50px #f59e0b; }
        }
      </style>
    `;
    document.body.appendChild(hudEl);

    // Bind ON / OFF Toggle Button
    const toggleBtn = document.getElementById('beomchro-toggle-btn');
    const testBtn = document.getElementById('beomchro-test-btn');
    const boxEl = document.getElementById('beomchro-hud-box');
    const dotEl = document.getElementById('beomchro-hud-dot');
    const guideEl = document.getElementById('beomchro-action-guide');

    if (toggleBtn) {
      toggleBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        isEnabled = !isEnabled;
        syncMainWorldFlag();

        if (isEnabled) {
          hasTriggered = false;
          toggleBtn.textContent = '🟢 ON (작동중)';
          toggleBtn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
          toggleBtn.style.boxShadow = '0 2px 8px rgba(16, 185, 129, 0.4)';
          boxEl.style.borderColor = '#00f0ff';
          dotEl.style.background = '#10b981';
          dotEl.style.boxShadow = '0 0 10px #10b981';
          dotEl.style.animation = 'beomchroPulse 1s infinite';
          guideEl.innerHTML = '✋ <strong>직접 누르거나 마우스를 올려두지 마세요!</strong><br>정각(00:00) 오픈 즉시 프로그램이 0ms로 자동 클릭합니다.';
          updateTargetHighlight();
          scanAndTrigger();
        } else {
          toggleBtn.textContent = '⚪ OFF (정지됨)';
          toggleBtn.style.background = '#475569';
          toggleBtn.style.boxShadow = 'none';
          boxEl.style.borderColor = '#64748b';
          dotEl.style.background = '#94a3b8';
          dotEl.style.boxShadow = 'none';
          dotEl.style.animation = 'none';
          guideEl.innerHTML = '⏸ <strong>자동 격발이 꺼져 있습니다 (수동 모드)</strong><br>다시 자동 클릭을 켜려면 우측 위 [OFF] 버튼을 눌러 ON으로 바꾸세요.';
          updateTargetHighlight();
        }
      });
    }

    if (testBtn) {
      testBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        hasTriggered = false;
        updateTargetHighlight();
        const target = findTargetButton();
        const statusEl = document.getElementById('beomchro-target-status');
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'center' });
          target.style.animation = 'beomchroFlash 0.6s ease 3';
          const btnText = (target.textContent || '').replace(/\s+/g, ' ').trim();
          if (statusEl) {
            statusEl.innerHTML = `<span style="color:#fde047;">✔ 작동 점검 정상! 현재 [${btnText}] 버튼을 0ms 조준 중입니다!</span>`;
          }
        } else {
          if (statusEl) {
            statusEl.innerHTML = `<span style="color:#fde047;">✔ 엔진 정상 작동 중! (예매 게이트 화면 진입 시 버튼을 자동 조준합니다)</span>`;
          }
        }
      });
    }

    updateTargetHighlight();
  }

  // High-performance Single Click Dispatcher (Compatible with React 18 & Vanilla DOM)
  function fastClick(element) {
    if (!isEnabled || hasTriggered) return;
    hasTriggered = true;

    const tStart = performance.now();

    try {
      const opts = { bubbles: true, cancelable: true, view: window, button: 0, buttons: 1 };
      element.dispatchEvent(new PointerEvent('pointerdown', opts));
      element.dispatchEvent(new MouseEvent('mousedown', opts));
      element.dispatchEvent(new PointerEvent('pointerup', { ...opts, buttons: 0 }));
      element.dispatchEvent(new MouseEvent('mouseup', { ...opts, buttons: 0 }));
      element.click();
    } catch (e) {
      try {
        element.click();
      } catch (err) {
        console.error('[BEOMCHRO] Click dispatch error:', err);
      }
    }

    const tEnd = performance.now();
    const durationMs = (tEnd - tStart).toFixed(3);

    console.log(`%c[BEOMCHRO] 🔥 0ms INTERCEPT TRIGGERED! (${durationMs}ms)`, 'background:#10b981; color:#fff; font-weight:bold; font-size:14px; padding:6px 12px; border-radius:4px;');

    const statusEl = document.getElementById('beomchro-target-status');
    const guideEl = document.getElementById('beomchro-action-guide');
    const boxEl = document.getElementById('beomchro-hud-box');
    if (statusEl) {
      statusEl.innerHTML = `<span style="color:#10b981; font-weight:800;">🔥 0ms 초고속 자동 격발 성공! (${durationMs}ms)</span>`;
    }
    if (guideEl) {
      guideEl.innerHTML = `🎉 <strong>오픈 즉시 자동 클릭이 완료되었습니다!</strong><br>다시 감시하려면 [🔍 작동확인] 또는 리셋 버튼을 누르세요.`;
    }
    if (boxEl) {
      boxEl.style.borderColor = '#10b981';
    }
  }

  // Scan page and trigger if target gate button is ready
  function scanAndTrigger() {
    updateTargetHighlight();
    if (!isEnabled || hasTriggered) return;

    const target = findTargetButton();
    if (target && isButtonReadyToClick(target)) {
      fastClick(target);
    }
  }

  // MutationObserver for 0ms reaction to attribute or text changes (Zero DOM mutation inside callback!)
  function startObserver() {
    if (observer) return;

    observer = new MutationObserver((mutations) => {
      if (!isEnabled || hasTriggered) return;

      for (let i = 0; i < mutations.length; i++) {
        const m = mutations[i];
        if (hudEl && (m.target === hudEl || hudEl.contains(m.target))) {
          continue;
        }
        const target = findTargetButton();
        if (target && isButtonReadyToClick(target)) {
          fastClick(target);
          return;
        }
      }
    });

    observer.observe(document.documentElement || document, {
      childList: true,
      subtree: true,
      characterData: true,
      attributes: true,
      attributeFilter: ['disabled', 'class', 'aria-disabled']
    });
  }

  startObserver();

  // Simulator custom events support
  window.addEventListener('beomchro:opened', () => {
    scanAndTrigger();
  });

  window.addEventListener('beomchro:reset', () => {
    hasTriggered = false;
    lastStatusHtml = '';
    const boxEl = document.getElementById('beomchro-hud-box');
    if (boxEl && isEnabled) boxEl.style.borderColor = '#00f0ff';
    updateTargetHighlight();
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      createHUD();
      scanAndTrigger();
    });
  } else {
    createHUD();
    scanAndTrigger();
  }

  // Periodic UI status refresh & fallback check (every 150ms, zero infinite loop risk)
  setInterval(() => {
    if (!hudEl && document.body) createHUD();
    if (isEnabled && !hasTriggered) {
      const target = findTargetButton();
      if (target && isButtonReadyToClick(target)) {
        fastClick(target);
        return;
      }
    }
    updateTargetHighlight();
  }, 150);

})();
