/**
 * BEOMCHRO Simulator JavaScript Core
 * High-precision Queue Reaction Benchmark
 */

(() => {
  'use strict';

  // DOM Elements
  const navTime = document.getElementById('navTime');
  const scriptStatus = document.getElementById('scriptStatus');
  const btnCountdown5 = document.getElementById('btnCountdown5');
  const btnCountdown10 = document.getElementById('btnCountdown10');
  const btnInstantOpen = document.getElementById('btnInstantOpen');
  const btnReset = document.getElementById('btnReset');
  const countdownNumber = document.getElementById('countdownNumber');
  const timerStatusDesc = document.getElementById('timerStatusDesc');

  const btnBooking = document.getElementById('btn-booking');
  const bookingBtnText = document.getElementById('bookingBtnText');
  const bookingBtnSub = document.getElementById('bookingBtnSub');

  const metricOpenTime = document.getElementById('metricOpenTime');
  const metricClickTime = document.getElementById('metricClickTime');
  const metricLatency = document.getElementById('metricLatency');
  const metricQueueRank = document.getElementById('metricQueueRank');
  const benchBadge = document.getElementById('benchBadge');
  const historyTableBody = document.getElementById('historyTableBody');

  const queueModal = document.getElementById('queueModal');
  const modalClose = document.getElementById('modalClose');
  const modalConfirmBtn = document.getElementById('modalConfirmBtn');
  const modalQueueNumber = document.getElementById('modalQueueNumber');
  const modalQueueWaitTime = document.getElementById('modalQueueWaitTime');
  const modalLatency = document.getElementById('modalLatency');
  const modalTriggerType = document.getElementById('modalTriggerType');
  const modalTier = document.getElementById('modalTier');
  const modalDesc = document.getElementById('modalDesc');

  // State
  let timerInterval = null;
  let countdownSeconds = 0;
  let openPerfTime = 0;
  let openDate = null;
  let isOpen = false;
  let historyCount = 0;

  // Format Date with milliseconds (HH:mm:ss.SSS)
  function formatTimeWithMs(date) {
    if (!date) return '--:--:--.---';
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    const ms = String(date.getMilliseconds()).padStart(3, '0');
    return `${hours}:${minutes}:${seconds}.${ms}`;
  }

  // Live Nav Clock
  function updateNavClock() {
    const now = new Date();
    navTime.textContent = formatTimeWithMs(now);
    requestAnimationFrame(updateNavClock);
  }
  requestAnimationFrame(updateNavClock);

  // Check UserScript injection
  function checkScriptInjected() {
    if (window.__BEOMCHRO_ACTIVE__) {
      scriptStatus.innerHTML = `
        <span class="dot active"></span>
        <span class="text" style="color: var(--accent-cyan); font-weight:700;">⚡ BEOMCHRO USER SCRIPT ACTIVE (0ms)</span>
      `;
    } else {
      scriptStatus.innerHTML = `
        <span class="dot inactive"></span>
        <span class="text">수동 손클릭 모드 (유저스크립트 미감지)</span>
      `;
    }
  }
  // Periodic check for late script injection
  setInterval(checkScriptInjected, 1000);
  checkScriptInjected();

  // Reset State
  function resetSimulator() {
    if (timerInterval) {
      clearInterval(timerInterval);
      timerInterval = null;
    }
    isOpen = false;
    openPerfTime = 0;
    openDate = null;

    btnBooking.disabled = true;
    btnBooking.setAttribute('disabled', 'disabled');
    btnBooking.classList.remove('active');
    btnBooking.classList.add('disabled');
    bookingBtnText.textContent = '예매 오픈 대기 중';
    bookingBtnSub.textContent = '잠시 후 정각에 버튼이 활성화됩니다';

    countdownNumber.textContent = 'READY';
    countdownNumber.style.color = 'var(--accent-cyan)';
    timerStatusDesc.textContent = '대기 중: 카운트다운 버튼을 눌러 테스트를 시작하세요.';

    metricOpenTime.textContent = '--:--:--.---';
    metricClickTime.textContent = '--:--:--.---';
    metricLatency.textContent = '-- ms';
    metricQueueRank.textContent = '대기 -- 번';
    benchBadge.textContent = '측정 대기';
    benchBadge.className = 'bench-badge';
  }

  // Open Button Activation Trigger
  function triggerOpen() {
    if (isOpen) return;
    isOpen = true;
    openPerfTime = performance.now();
    openDate = new Date();

    metricOpenTime.textContent = formatTimeWithMs(openDate);
    countdownNumber.textContent = 'OPEN!';
    countdownNumber.style.color = '#10b981';
    timerStatusDesc.textContent = '⚡ 티켓팅 오픈! 즉시 버튼을 클릭하세요!';

    // Activate Booking Button (DOM mutation triggers Tampermonkey script)
    btnBooking.removeAttribute('disabled');
    btnBooking.disabled = false;
    btnBooking.classList.remove('disabled');
    btnBooking.classList.add('active');
    bookingBtnText.textContent = '예매하기';
    bookingBtnSub.textContent = '잔여석 즉시 선점 중';

    // Dispatch custom event for automation
    window.dispatchEvent(new CustomEvent('beomchro:opened', {
      detail: { openTime: openDate.getTime(), perfTime: openPerfTime }
    }));
  }

  // Countdown Handler
  function startCountdown(seconds) {
    resetSimulator();
    countdownSeconds = seconds;
    countdownNumber.textContent = `${countdownSeconds}.00s`;
    timerStatusDesc.textContent = `${countdownSeconds}초 후 정각 00.000초에 예매하기 버튼이 활성화됩니다.`;

    const startTime = performance.now();
    const targetDurationMs = seconds * 1000;

    timerInterval = setInterval(() => {
      const elapsed = performance.now() - startTime;
      const remaining = targetDurationMs - elapsed;

      if (remaining <= 0) {
        clearInterval(timerInterval);
        timerInterval = null;
        triggerOpen();
      } else {
        const secDisplay = (remaining / 1000).toFixed(2);
        countdownNumber.textContent = `${secDisplay}s`;
        if (remaining <= 3000) {
          countdownNumber.style.color = '#ef4444';
          timerStatusDesc.textContent = '🚨 오픈 임박! 긴장하세요!';
        }
      }
    }, 20);
  }

  // Handle Booking Button Click (Reaction Measurement)
  btnBooking.addEventListener('click', (e) => {
    if (!isOpen) {
      alert('아직 티켓 오픈 전입니다! 카운트다운을 먼저 시작해주세요.');
      return;
    }

    const clickPerfTime = performance.now();
    const clickDate = new Date();
    const rawLatency = Math.max(0.01, clickPerfTime - openPerfTime);
    const latencyMs = Number(rawLatency.toFixed(2));

    metricClickTime.textContent = formatTimeWithMs(clickDate);
    metricLatency.textContent = `${latencyMs} ms`;
    benchBadge.textContent = '측정 완료';
    benchBadge.className = 'bench-badge measured';

    // Calculate Queue Placement based on latency
    const result = evaluateQueue(latencyMs, e.isTrusted);
    metricQueueRank.textContent = `대기 ${result.rankFormatted}번`;

    // Populate Modal
    modalQueueNumber.textContent = `${result.rankFormatted}번`;
    modalQueueWaitTime.textContent = `예상 대기 시간: ${result.waitTime}`;
    modalLatency.textContent = `${latencyMs} ms`;
    modalTriggerType.textContent = result.triggerType;
    modalTier.textContent = result.tierName;
    modalTier.className = `tier-${result.tierClass}`;
    modalDesc.textContent = result.desc;

    // Show Modal
    queueModal.classList.add('open');

    // Add to History
    addHistoryRow({
      index: ++historyCount,
      triggerType: result.triggerType,
      latency: latencyMs,
      rank: result.rankFormatted,
      waitTime: result.waitTime,
      tier: result.tierName,
      tierClass: result.tierClass,
      time: formatTimeWithMs(clickDate)
    });
  });

  // Queue Evaluation Logic
  function evaluateQueue(latency, isTrustedEvent) {
    const isAuto = window.__BEOMCHRO_ACTIVE__ || latency < 5;

    if (latency < 1.0) {
      return {
        rankFormatted: '1',
        waitTime: '즉시 입장 (0분 00초)',
        tierName: '신(GOD)의 영역',
        tierClass: 'god',
        triggerType: isAuto ? 'BEOMCHRO 0ms 자동 인젝션' : '초광속 인간 반응',
        desc: '0ms 극초음속 인터셉트 성공! 1번 대기로 원하는 최상급 VIP 1열 좌석 선점 확정!'
      };
    } else if (latency < 15.0) {
      const rank = Math.floor(latency * 1.5) + 1;
      return {
        rankFormatted: rank.toLocaleString(),
        waitTime: '약 5초',
        tierName: '초특급 매크로/하드웨어',
        tierClass: 'pro',
        triggerType: isAuto ? 'BEOMCHRO 자동 인젝션' : '최고속 반응',
        desc: '15ms 이내 진입! 최상위 0.01% 선두 그룹으로 VIP/R석 선점에 완벽 성공합니다.'
      };
    } else if (latency < 50.0) {
      const rank = Math.floor(latency * 8) + 15;
      return {
        rankFormatted: rank.toLocaleString(),
        waitTime: '약 30초',
        tierName: '프로 티켓터',
        tierClass: 'pro',
        triggerType: '고속 트리거',
        desc: '상위 1% 이내 대기열 진입! R석 이상 무난하게 선점 가능한 우수한 순번입니다.'
      };
    } else if (latency < 150.0) {
      const rank = Math.floor(latency * 25) + 300;
      return {
        rankFormatted: rank.toLocaleString(),
        waitTime: '약 2분 30초',
        tierName: '준프로급',
        tierClass: 'normal',
        triggerType: '빠른 손클릭',
        desc: '150ms 이내의 훌륭한 반사신경입니다. 인기 구역 진입이 가능합니다.'
      };
    } else if (latency < 300.0) {
      const rank = Math.floor(latency * 45) + 2000;
      return {
        rankFormatted: rank.toLocaleString(),
        waitTime: '약 12분',
        tierName: '일반 관람객',
        tierClass: 'normal',
        triggerType: '수동 마우스 클릭',
        desc: '평균적인 인간 반응 속도입니다. 주요 좌석은 이미 자동화 도구에 의해 매진될 확률이 높습니다.'
      };
    } else {
      const rank = Math.floor(14290 + (latency - 300) * 95);
      return {
        rankFormatted: rank.toLocaleString(),
        waitTime: '약 48분 이상 (매진 주의)',
        tierName: '지연 / 매진 위험',
        tierClass: 'late',
        triggerType: '지연된 손클릭',
        desc: '300ms 초과! 대기 1만 번대 진입으로 사실상 주요 좌석 예매가 어렵습니다. BEOMCHRO 자동 인젝터를 사용하세요!'
      };
    }
  }

  // Add History Row
  function addHistoryRow(item) {
    const emptyRow = historyTableBody.querySelector('.empty-row');
    if (emptyRow) emptyRow.remove();

    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${item.index}</td>
      <td><span style="font-size:0.8rem; color:var(--text-muted);">${item.triggerType}</span></td>
      <td><strong>${item.latency} ms</strong></td>
      <td><span style="color:var(--accent-cyan); font-weight:700;">대기 ${item.rank}번</span></td>
      <td>${item.waitTime}</td>
      <td><span class="tag ${item.tierClass}">${item.tier}</span></td>
      <td style="font-family:var(--font-mono); font-size:0.75rem; color:var(--text-muted);">${item.time}</td>
    `;
    historyTableBody.insertBefore(row, historyTableBody.firstChild);
  }

  // Modal Handlers
  modalClose.addEventListener('click', () => queueModal.classList.remove('open'));
  modalConfirmBtn.addEventListener('click', () => {
    queueModal.classList.remove('open');
    resetSimulator();
  });

  // Button Listeners
  btnCountdown5.addEventListener('click', () => startCountdown(5));
  btnCountdown10.addEventListener('click', () => startCountdown(10));
  btnInstantOpen.addEventListener('click', () => {
    resetSimulator();
    triggerOpen();
  });
  btnReset.addEventListener('click', resetSimulator);

  // Expose Global Object for Automation & Remote Inspection
  window.BEOMCHRO_SIMULATOR = {
    triggerOpen,
    startCountdown,
    reset: resetSimulator,
    getStatus: () => ({
      isOpen,
      openPerfTime,
      openDate: openDate ? openDate.toISOString() : null,
      injected: !!window.__BEOMCHRO_ACTIVE__
    })
  };
})();
