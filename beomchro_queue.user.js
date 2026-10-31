// ==UserScript==
// @name         BEOMCHRO 0ms Ultra Queue Interceptor
// @namespace    https://github.com/beomchro
// @version      2.0.0
// @description  놀티켓 & 로컬 시뮬레이터 마이크로초 0ms 대기열 초고속 자동 진입 엔진
// @author       BEOMCHRO Team
// @match        http://localhost:8989/*
// @match        http://127.0.0.1:8989/*
// @match        *://ticket.nol.com/*
// @match        *://*.nol.com/*
// @match        *://ticket.interpark.com/*
// @run-at       document-start
// @grant        none
// ==/UserScript==

(function () {
  'use strict';

  // Mark engine as active
  window.__BEOMCHRO_ACTIVE__ = true;
  window.__BEOMCHRO_VERSION__ = '2.0.0';

  console.log('%c[BEOMCHRO] ⚡ 0ms Queue Interceptor Engine v2.0 Initialized', 'background:#0066ff; color:#fff; font-weight:bold; padding:4px 8px; border-radius:4px;');

  // State
  let hasTriggered = false;
  let observer = null;
  let hudEl = null;

  // Supported Selectors for NOL Ticket & Local Simulator
  const TARGET_SELECTORS = [
    '#btn-booking',
    '.btn-booking-action',
    '#ticketReservationBtn',
    'a.btn_reserve',
    'button.booking-btn',
    'button[data-action="book"]',
    'a[onclick*="fnBook"]',
    'a[onclick*="reserve"]'
  ];

  // Create Lightweight HUD Banner
  function createHUD() {
    if (hudEl || !document.body) return;

    hudEl = document.createElement('div');
    hudEl.id = 'beomchro-hud';
    hudEl.innerHTML = `
      <div style="
        position: fixed;
        top: 12px;
        right: 16px;
        z-index: 999999;
        background: rgba(10, 14, 23, 0.92);
        border: 1px solid #00f0ff;
        box-shadow: 0 4px 20px rgba(0, 240, 255, 0.35);
        color: #f0f4fc;
        padding: 8px 14px;
        border-radius: 8px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace;
        font-size: 12px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 8px;
        backdrop-filter: blur(8px);
        pointer-events: none;
        transition: all 0.3s ease;
      ">
        <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#00f0ff; box-shadow:0 0 8px #00f0ff; animation: pulse 1s infinite;"></span>
        <span id="beomchro-hud-text">⚡ BEOMCHRO 0ms READY (대기 감시 중)</span>
      </div>
      <style>
        @keyframes pulse {
          0% { opacity: 0.4; transform: scale(0.9); }
          50% { opacity: 1; transform: scale(1.1); }
          100% { opacity: 0.4; transform: scale(0.9); }
        }
      </style>
    `;
    document.body.appendChild(hudEl);
  }

  // Update HUD status
  function updateHUD(text, isSuccess) {
    const textEl = document.getElementById('beomchro-hud-text');
    if (textEl) {
      textEl.textContent = text;
      if (isSuccess) {
        textEl.style.color = '#10b981';
      }
    }
  }

  // High-performance Click Dispatcher
  function fastClick(element) {
    if (hasTriggered) return;
    hasTriggered = true;

    const tStart = performance.now();

    // 1. Native click()
    try {
      element.click();
    } catch (e) {
      console.warn('[BEOMCHRO] Native click failed, trying Synthetic MouseEvents:', e);
    }

    // 2. Synthetic MouseEvents fallback (Down -> Up -> Click)
    try {
      const opts = { bubbles: true, cancelable: true, view: window, buttons: 1 };
      element.dispatchEvent(new MouseEvent('mousedown', opts));
      element.dispatchEvent(new MouseEvent('mouseup', opts));
      element.dispatchEvent(new MouseEvent('click', opts));
    } catch (e) {
      console.error('[BEOMCHRO] Synthetic dispatch error:', e);
    }

    const tEnd = performance.now();
    const durationMs = (tEnd - tStart).toFixed(3);

    console.log(`%c[BEOMCHRO] 🔥 INTERCEPT TRIGGERED! Dispatch took ${durationMs}ms`, 'background:#10b981; color:#fff; font-weight:bold; font-size:14px; padding:6px 12px; border-radius:4px;');
    updateHUD(`🔥 0ms 격발 성공! (${durationMs}ms)`, true);

    // Stop observer once triggered
    if (observer) {
      observer.disconnect();
      observer = null;
    }
  }

  // Check if an element is ready to click
  function isReady(el) {
    if (!el) return false;
    // Check disabled attribute and property
    if (el.hasAttribute('disabled') || el.disabled === true) return false;
    if (el.getAttribute('aria-disabled') === 'true') return false;
    // Check disabled class
    if (el.classList && el.classList.contains('disabled')) return false;
    return true;
  }

  // Inspect current document for targets
  function scanAndTrigger() {
    if (hasTriggered) return;

    for (const sel of TARGET_SELECTORS) {
      const el = document.querySelector(sel);
      if (el && isReady(el)) {
        fastClick(el);
        return;
      }
    }
  }

  // Ultra-fast MutationObserver
  function startObserver() {
    if (observer || hasTriggered) return;

    observer = new MutationObserver((mutations) => {
      if (hasTriggered) return;

      for (let i = 0; i < mutations.length; i++) {
        const m = mutations[i];

        // If target modified its attributes (disabled removed, class changed)
        if (m.type === 'attributes') {
          const target = m.target;
          for (const sel of TARGET_SELECTORS) {
            if (target.matches && target.matches(sel)) {
              if (isReady(target)) {
                fastClick(target);
                return;
              }
            }
          }
        }

        // If new nodes added
        if (m.addedNodes.length > 0) {
          for (let j = 0; j < m.addedNodes.length; j++) {
            const node = m.addedNodes[j];
            if (node.nodeType === 1) { // ELEMENT_NODE
              for (const sel of TARGET_SELECTORS) {
                if (node.matches && node.matches(sel) && isReady(node)) {
                  fastClick(node);
                  return;
                }
                const nested = node.querySelector && node.querySelector(sel);
                if (nested && isReady(nested)) {
                  fastClick(nested);
                  return;
                }
              }
            }
          }
        }
      }
    });

    observer.observe(document.documentElement || document, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['disabled', 'class', 'style', 'aria-disabled']
    });
  }

  // Initialization lifecycle
  startObserver();

  // Listen for custom simulator events
  window.addEventListener('beomchro:opened', () => {
    scanAndTrigger();
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

  // Secondary rapid polling (microtask / requestAnimationFrame fallback)
  function pollLoop() {
    if (hasTriggered) return;
    scanAndTrigger();
    requestAnimationFrame(pollLoop);
  }
  requestAnimationFrame(pollLoop);

})();
