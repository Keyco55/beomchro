// ==UserScript==
// @name         BEOMCHRO 0ms Ultra Queue Interceptor
// @namespace    https://github.com/Keyco55/beomchro
// @version      2.1.0
// @description  NOL 티켓 & 인터파크 티켓 게이트 0ms 초고속 대기열 자동 진입 엔진 (ON/OFF 컨트롤 & 실시간 조준 표시)
// @author       BEOMCHRO Team
// @match        http://localhost:8989/*
// @match        http://127.0.0.1:8989/*
// @match        file://*/*
// @match        *://nol.yanolja.com/*
// @match        *://*.yanolja.com/*
// @match        *://ticket.nol.com/*
// @match        *://*.nol.com/*
// @match        *://tickets.interpark.com/*
// @match        *://ticket.interpark.com/*
// @match        *://*.interpark.com/*
// @run-at       document-start
// @grant        none
// ==/UserScript==

(function () {
  'use strict';

  if (window.__BEOMCHRO_ACTIVE__) return;
  window.__BEOMCHRO_ACTIVE__ = true;
  window.__BEOMCHRO_VERSION__ = '2.1.0';

  let isEnabled = true;
  let hasTriggered = false;
  let observer = null;
  let hudEl = null;

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

  function findTargetButton() {
    for (const sel of GATE_BUTTON_SELECTORS) {
      const el = document.querySelector(sel);
      if (el) return el;
    }
    return null;
  }

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

  function updateTargetHighlight() {
    const target = findTargetButton();
    const statusEl = document.getElementById('beomchro-target-status');
    const guideEl = document.getElementById('beomchro-action-guide');

    if (!target) {
      const listBtns = document.querySelectorAll('.joint-rectangle-button--variant_outlined_primary, .game-cta-btn');
      if (statusEl) {
        if (listBtns.length > 0) {
          statusEl.innerHTML = `<span style="color:#38bdf8;">📋 경기 목록 화면 감지됨 (${listBtns.length}개 경기)</span>`;
          if (guideEl) guideEl.textContent = '💡 원하는 경기의 [예매하기]를 눌러 오픈 대기(게이트) 화면으로 들어가세요.';
        } else {
          statusEl.innerHTML = `<span style="color:#94a3b8;">🔍 예매 게이트 버튼 탐색 중...</span>`;
        }
      }
      return;
    }

    const btnText = (target.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 28) || '예매 버튼';
    const ready = isButtonReadyToClick(target);

    if (isEnabled && !hasTriggered) {
      target.style.outline = '3px solid #00f0ff';
      target.style.outlineOffset = '3px';
    } else if (!isEnabled) {
      target.style.outline = '2px dashed #64748b';
      target.style.outlineOffset = '3px';
    }

    if (statusEl && !hasTriggered) {
      if (!isEnabled) {
        statusEl.innerHTML = `<span style="color:#94a3b8;">⏸ 조준 일시정지됨: [${btnText}] (우측 위 ON 버튼을 켜세요)</span>`;
      } else if (!ready) {
        statusEl.innerHTML = `<span style="color:#00f0ff;">🎯 타겟 조준 완료: <strong>[${btnText}]</strong> (오픈 대기 감시 중)</span>`;
      } else {
        statusEl.innerHTML = `<span style="color:#10b981;">⚡ 버튼 오픈 감지됨: <strong>[${btnText}]</strong></span>`;
      }
    }
  }

  function createHUD() {
    if (hudEl || !document.body || document.getElementById('beomchro-hud')) return;
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
        font-family: -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', sans-serif;
        font-size: 12px;
        line-height: 1.45;
        backdrop-filter: blur(12px);
        user-select: none;
      ">
        <div style="display:flex; align-items:center; justify-content:space-between; gap:8px; margin-bottom:8px;">
          <div style="display:flex; align-items:center; gap:7px;">
            <span id="beomchro-hud-dot" style="display:inline-block; width:10px; height:10px; border-radius:50%; background:#10b981; box-shadow:0 0 10px #10b981;"></span>
            <span style="font-weight:800; font-size:13px; color:#ffffff;">⚡ BEOMCHRO 0ms 엔진</span>
          </div>
          <div style="display:flex; align-items:center; gap:5px;">
            <button id="beomchro-test-btn" type="button" style="background:rgba(255,255,255,0.1); color:#e2e8f0; border:1px solid rgba(255,255,255,0.2); border-radius:6px; padding:4px 8px; font-size:11px; font-weight:700; cursor:pointer;">🔍 작동확인</button>
            <button id="beomchro-toggle-btn" type="button" style="background:linear-gradient(135deg, #10b981, #059669); color:#fff; border:none; border-radius:6px; padding:4px 10px; font-size:11px; font-weight:800; cursor:pointer;">🟢 ON (작동중)</button>
          </div>
        </div>
        <div id="beomchro-target-status" style="background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.1); border-radius:7px; padding:6px 9px; font-size:11.5px; font-weight:600; margin-bottom:7px; color:#00f0ff;">🎯 타겟 버튼 탐색 중...</div>
        <div id="beomchro-action-guide" style="background:rgba(245,158,11,0.14); border-left:3px solid #f59e0b; border-radius:4px; padding:5px 8px; font-size:11px; color:#fde68a; font-weight:600;">✋ <strong>직접 누르거나 마우스를 올려두지 마세요!</strong><br>정각(00:00) 오픈 즉시 프로그램이 0ms로 자동 클릭합니다.</div>
      </div>
    `;
    document.body.appendChild(hudEl);

    const toggleBtn = document.getElementById('beomchro-toggle-btn');
    const testBtn = document.getElementById('beomchro-test-btn');
    const boxEl = document.getElementById('beomchro-hud-box');
    const dotEl = document.getElementById('beomchro-hud-dot');
    const guideEl = document.getElementById('beomchro-action-guide');

    toggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      isEnabled = !isEnabled;
      window.__BEOMCHRO_ACTIVE__ = isEnabled;
      if (isEnabled) {
        hasTriggered = false;
        toggleBtn.textContent = '🟢 ON (작동중)';
        toggleBtn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
        boxEl.style.borderColor = '#00f0ff';
        dotEl.style.background = '#10b981';
        guideEl.innerHTML = '✋ <strong>직접 누르거나 마우스를 올려두지 마세요!</strong><br>정각(00:00) 오픈 즉시 프로그램이 0ms로 자동 클릭합니다.';
        updateTargetHighlight();
        scanAndTrigger();
      } else {
        toggleBtn.textContent = '⚪ OFF (정지됨)';
        toggleBtn.style.background = '#475569';
        boxEl.style.borderColor = '#64748b';
        dotEl.style.background = '#94a3b8';
        guideEl.innerHTML = '⏸ <strong>자동 격발이 꺼져 있습니다 (수동 모드)</strong><br>다시 자동 클릭을 켜려면 우측 위 [OFF] 버튼을 눌러 ON으로 바꾸세요.';
        updateTargetHighlight();
      }
    });

    testBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      hasTriggered = false;
      updateTargetHighlight();
      const target = findTargetButton();
      const statusEl = document.getElementById('beomchro-target-status');
      if (target && statusEl) {
        const btnText = (target.textContent || '').replace(/\s+/g, ' ').trim();
        statusEl.innerHTML = `<span style="color:#fde047;">✔ 작동 점검 정상! 현재 [${btnText}] 버튼을 0ms 조준 중입니다!</span>`;
      }
    });

    updateTargetHighlight();
  }

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
      element.click();
    }
    const durationMs = (performance.now() - tStart).toFixed(3);
    const statusEl = document.getElementById('beomchro-target-status');
    const guideEl = document.getElementById('beomchro-action-guide');
    if (statusEl) statusEl.innerHTML = `<span style="color:#10b981; font-weight:800;">🔥 0ms 초고속 자동 격발 성공! (${durationMs}ms)</span>`;
    if (guideEl) guideEl.innerHTML = `🎉 <strong>오픈 즉시 자동 클릭이 완료되었습니다!</strong>`;
  }

  function scanAndTrigger() {
    updateTargetHighlight();
    if (!isEnabled || hasTriggered) return;
    const target = findTargetButton();
    if (target && isButtonReadyToClick(target)) {
      fastClick(target);
    }
  }

  observer = new MutationObserver(() => {
    if (!isEnabled) return updateTargetHighlight();
    if (!hasTriggered) {
      const target = findTargetButton();
      if (target && isButtonReadyToClick(target)) {
        fastClick(target);
        return;
      }
    }
    updateTargetHighlight();
  });

  observer.observe(document.documentElement || document, {
    childList: true,
    subtree: true,
    characterData: true,
    attributes: true,
    attributeFilter: ['disabled', 'class', 'style', 'aria-disabled']
  });

  window.addEventListener('beomchro:opened', scanAndTrigger);
  window.addEventListener('beomchro:reset', () => {
    hasTriggered = false;
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
  setInterval(updateTargetHighlight, 250);
})();
