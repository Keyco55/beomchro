/**
 * BEOMCHRO Manifest V3 Content Script
 * 0ms Ultra Queue Interceptor Engine
 */

(() => {
  'use strict';

  // Inject execution flag into the main world page context
  try {
    const script = document.createElement('script');
    script.textContent = `
      window.__BEOMCHRO_ACTIVE__ = true;
      window.__BEOMCHRO_VERSION__ = '2.0.0 (Native Extension)';
      console.log('%c[BEOMCHRO] ⚡ Extension Main World Activated', 'background:#0066ff; color:#fff; font-weight:bold; padding:2px 6px; border-radius:3px;');
    `;
    (document.head || document.documentElement).appendChild(script);
    script.remove();
  } catch (e) {
    // Isolated fallback
  }

  window.__BEOMCHRO_ACTIVE__ = true;
  window.__BEOMCHRO_VERSION__ = '2.0.0 (Native Extension)';

  console.log('%c[BEOMCHRO] ⚡ 0ms Zero-Setup Queue Interceptor Active', 'background:#0066ff; color:#fff; font-weight:bold; padding:4px 8px; border-radius:4px;');

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
        top: 14px;
        right: 18px;
        z-index: 2147483647;
        background: rgba(10, 14, 23, 0.94);
        border: 1px solid #00f0ff;
        box-shadow: 0 4px 25px rgba(0, 240, 255, 0.45);
        color: #f0f4fc;
        padding: 9px 16px;
        border-radius: 9px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace;
        font-size: 12px;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 9px;
        backdrop-filter: blur(10px);
        pointer-events: none;
        transition: all 0.3s ease;
      ">
        <span style="display:inline-block; width:9px; height:9px; border-radius:50%; background:#00f0ff; box-shadow:0 0 10px #00f0ff; animation: beomchroPulse 1.2s infinite;"></span>
        <span id="beomchro-hud-text">⚡ BEOMCHRO EXTENSION 0ms READY</span>
      </div>
      <style>
        @keyframes beomchroPulse {
          0% { opacity: 0.35; transform: scale(0.85); }
          50% { opacity: 1; transform: scale(1.15); }
          100% { opacity: 0.35; transform: scale(0.85); }
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

  // Fast click dispatcher
  function fastClick(element) {
    if (hasTriggered) return;
    hasTriggered = true;

    const tStart = performance.now();

    // 1. Native click()
    try {
      element.click();
    } catch (e) {
      console.warn('[BEOMCHRO] Native click failed:', e);
    }

    // 2. Synthetic MouseEvents fallback
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

    console.log(`%c[BEOMCHRO] 🔥 INTERCEPT TRIGGERED! Delay: ${durationMs}ms`, 'background:#10b981; color:#fff; font-weight:bold; font-size:14px; padding:6px 12px; border-radius:4px;');
    updateHUD(`🔥 0ms 격발 성공! (${durationMs}ms)`, true);

    if (observer) {
      observer.disconnect();
      observer = null;
    }
  }

  function isReady(el) {
    if (!el) return false;
    if (el.hasAttribute('disabled') || el.disabled === true) return false;
    if (el.getAttribute('aria-disabled') === 'true') return false;
    if (el.classList && el.classList.contains('disabled')) return false;
    return true;
  }

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

  function startObserver() {
    if (observer || hasTriggered) return;

    observer = new MutationObserver((mutations) => {
      if (hasTriggered) return;

      for (let i = 0; i < mutations.length; i++) {
        const m = mutations[i];

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

        if (m.addedNodes.length > 0) {
          for (let j = 0; j < m.addedNodes.length; j++) {
            const node = m.addedNodes[j];
            if (node.nodeType === 1) {
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

  startObserver();

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

  function pollLoop() {
    if (hasTriggered) return;
    scanAndTrigger();
    requestAnimationFrame(pollLoop);
  }
  requestAnimationFrame(pollLoop);

})();
