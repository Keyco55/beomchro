/**
 * BEOMCHRO v2.1 Authentic NOL Ticket / Interpark Gate Simulator Core
 * Based on attached 2026 KBO Korean Series HTML pages
 */

(() => {
  'use strict';

  // 2026 KBO 한국시리즈 1~7차전 실제 일정 데이터 (첨부 HTML 기반)
  const KOREAN_SERIES_GAMES = [
    {
      id: 1,
      badge: '한국시리즈 1차전',
      title: '2026 한국시리즈 1차전 KT vs 삼성',
      dateStr: '11월 3일(화) 18:30',
      venue: '수원KT위즈파크',
      homeTeam: 'KT위즈',
      homeCode: 'kt',
      awayTeam: '삼성 라이온즈',
      awayCode: 'ss'
    },
    {
      id: 2,
      badge: '한국시리즈 2차전',
      title: '2026 한국시리즈 2차전 KT vs 삼성',
      dateStr: '11월 4일(수) 18:30',
      venue: '수원KT위즈파크',
      homeTeam: 'KT위즈',
      homeCode: 'kt',
      awayTeam: '삼성 라이온즈',
      awayCode: 'ss'
    },
    {
      id: 3,
      badge: '한국시리즈 3차전',
      title: '2026 한국시리즈 3차전 KT vs 삼성',
      dateStr: '11월 6일(금) 18:30',
      venue: '대구삼성라이온즈파크',
      homeTeam: '삼성 라이온즈',
      homeCode: 'ss',
      awayTeam: 'KT위즈',
      awayCode: 'kt'
    },
    {
      id: 4,
      badge: '한국시리즈 4차전',
      title: '2026 한국시리즈 4차전 KT vs 삼성',
      dateStr: '11월 7일(토) 14:00',
      venue: '대구삼성라이온즈파크',
      homeTeam: '삼성 라이온즈',
      homeCode: 'ss',
      awayTeam: 'KT위즈',
      awayCode: 'kt'
    },
    {
      id: 5,
      badge: '한국시리즈 5차전',
      title: '2026 한국시리즈 5차전 KT vs 삼성',
      dateStr: '11월 8일(일) 14:00',
      venue: '대구삼성라이온즈파크',
      homeTeam: '삼성 라이온즈',
      homeCode: 'ss',
      awayTeam: 'KT위즈',
      awayCode: 'kt'
    },
    {
      id: 6,
      badge: '한국시리즈 6차전',
      title: '2026 한국시리즈 6차전 KT vs 삼성',
      dateStr: '11월 10일(화) 18:30',
      venue: '수원KT위즈파크',
      homeTeam: 'KT위즈',
      homeCode: 'kt',
      awayTeam: '삼성 라이온즈',
      awayCode: 'ss'
    },
    {
      id: 7,
      badge: '한국시리즈 7차전',
      title: '2026 한국시리즈 7차전 KT vs 삼성',
      dateStr: '11월 11일(수) 18:30',
      venue: '수원KT위즈파크',
      homeTeam: 'KT위즈',
      homeCode: 'kt',
      awayTeam: '삼성 라이온즈',
      awayCode: 'ss'
    }
  ];

  // DOM References
  const tabGateView = document.getElementById('tabGateView');
  const tabListView = document.getElementById('tabListView');
  const gateViewContainer = document.getElementById('gateViewContainer');
  const listViewContainer = document.getElementById('listViewContainer');
  const btnBackToList = document.getElementById('btnBackToList');
  const nolGameList = document.getElementById('nolGameList');

  const btnCountdown5 = document.getElementById('btnCountdown5');
  const btnCountdown10 = document.getElementById('btnCountdown10');
  const btnInstantOpen = document.getElementById('btnInstantOpen');
  const btnReset = document.getElementById('btnReset');

  const gateHeadline = document.getElementById('gateHeadline');
  const gateSubDesc = document.getElementById('gateSubDesc');
  const gateMatchTitle = document.getElementById('gateMatchTitle');
  const gateMatchMeta = document.getElementById('gateMatchMeta');
  const posterSeriesBadge = document.getElementById('posterSeriesBadge');
  const posterDateVenue = document.getElementById('posterDateVenue');

  const btnBooking = document.getElementById('btn-booking');
  const bookingBtnText = document.getElementById('bookingBtnText');

  const metricOpenTime = document.getElementById('metricOpenTime');
  const metricClickTime = document.getElementById('metricClickTime');
  const metricLatency = document.getElementById('metricLatency');
  const metricQueueRank = document.getElementById('metricQueueRank');
  const benchStatusBadge = document.getElementById('benchStatusBadge');
  const historyTableBody = document.getElementById('historyTableBody');

  const queueModal = document.getElementById('queueModal');
  const modalClose = document.getElementById('modalClose');
  const modalCloseBtn2 = document.getElementById('modalCloseBtn2');
  const modalConfirmBtn = document.getElementById('modalConfirmBtn');
  const modalGameName = document.getElementById('modalGameName');
  const modalQueueNumber = document.getElementById('modalQueueNumber');
  const modalQueueWaitTime = document.getElementById('modalQueueWaitTime');
  const modalLatency = document.getElementById('modalLatency');
  const modalTriggerType = document.getElementById('modalTriggerType');
  const modalTier = document.getElementById('modalTier');
  const modalDesc = document.getElementById('modalDesc');
  const modalProgressBar = document.getElementById('modalProgressBar');

  // Simulator State
  let selectedGame = KOREAN_SERIES_GAMES[6]; // 기본: 한국시리즈 7차전
  let timerInterval = null;
  let openPerfTime = 0;
  let openDate = null;
  let isOpen = false;
  let historyCount = 0;

  function formatTimeWithMs(date) {
    if (!date) return '--:--:--.---';
    const h = String(date.getHours()).padStart(2, '0');
    const m = String(date.getMinutes()).padStart(2, '0');
    const s = String(date.getSeconds()).padStart(2, '0');
    const ms = String(date.getMilliseconds()).padStart(3, '0');
    return `${h}:${m}:${s}.${ms}`;
  }

  function formatMmSs(totalSec) {
    const s = Math.max(0, Math.ceil(totalSec));
    const mm = String(Math.floor(s / 60)).padStart(2, '0');
    const ss = String(s % 60).padStart(2, '0');
    return `${mm}:${ss}`;
  }

  // Switch between Gate View and Game List View
  function switchView(viewName) {
    if (viewName === 'gate') {
      gateViewContainer.classList.add('active');
      listViewContainer.classList.remove('active');
      tabGateView.classList.add('active');
      tabListView.classList.remove('active');
    } else {
      gateViewContainer.classList.remove('active');
      listViewContainer.classList.add('active');
      tabGateView.classList.remove('active');
      tabListView.classList.add('active');
    }
    window.dispatchEvent(new CustomEvent('beomchro:reset'));
  }

  tabGateView.addEventListener('click', () => switchView('gate'));
  tabListView.addEventListener('click', () => switchView('list'));
  btnBackToList.addEventListener('click', () => switchView('list'));

  // Render 1~7차전 Game Cards inside NOL Ticket List View
  function renderGameList() {
    nolGameList.innerHTML = KOREAN_SERIES_GAMES.map((g) => `
      <div class="nol-game-card">
        <div class="game-info-col">
          <span class="joint-product-badge joint-product-badge--variant_filled_secondary">${g.badge}</span>
          <span class="game-date-str">${g.dateStr}</span>
          <span class="game-venue-str">${g.venue}</span>
        </div>
        <div class="game-matchup-col">
          <div class="team-block">
            <div class="team-emblem ${g.homeCode}">${g.homeCode === 'kt' ? 'KT' : 'SS'}</div>
            <div>
              <span class="ha-badge home">H</span>
              <span class="team-name">${g.homeTeam}</span>
            </div>
          </div>
          <span class="vs-divider">VS</span>
          <div class="team-block">
            <div class="team-emblem ${g.awayCode}">${g.awayCode === 'kt' ? 'KT' : 'SS'}</div>
            <div>
              <span class="ha-badge away">A</span>
              <span class="team-name">${g.awayTeam}</span>
            </div>
          </div>
        </div>
        <div class="game-cta-col">
          <button type="button" class="joint-rectangle-button joint-rectangle-button--variant_outlined_primary game-cta-btn" data-game-id="${g.id}">예매하기</button>
        </div>
      </div>
    `).join('');

    nolGameList.querySelectorAll('.game-cta-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        const id = Number(btn.getAttribute('data-game-id'));
        const found = KOREAN_SERIES_GAMES.find((x) => x.id === id);
        if (found) {
          selectGameAndStartGate(found, 5);
        }
      });
    });
  }

  function selectGameAndStartGate(game, countdownSec = 5) {
    selectedGame = game;
    gateMatchTitle.textContent = game.title;
    gateMatchMeta.textContent = `${game.dateStr} • ${game.venue}`;
    if (posterSeriesBadge) posterSeriesBadge.textContent = game.badge;
    if (posterDateVenue) posterDateVenue.textContent = `2026. ${game.dateStr} | ${game.venue}`;
    switchView('gate');
    startCountdown(countdownSec);
  }

  // Reset Gate Button to "Waiting before open" state
  function resetSimulator(defaultRemainingSec = 5) {
    if (timerInterval) {
      clearInterval(timerInterval);
      timerInterval = null;
    }
    isOpen = false;
    openPerfTime = 0;
    openDate = null;

    gateHeadline.textContent = '예매는 오픈 시간부터 가능해요';
    gateHeadline.style.color = '#111827';
    gateSubDesc.textContent = '우측 상단 BEOMCHRO가 ON이면 오픈(00:00) 순간 손대지 않아도 0ms로 자동 클릭됩니다.';

    btnBooking.disabled = true;
    btnBooking.setAttribute('disabled', '');
    btnBooking.className = '_button_4ncv0_1 _primary_2p3w6_7 _disabled_2p3w6_34';
    bookingBtnText.textContent = `남은시간 ${formatMmSs(defaultRemainingSec)}`;

    metricOpenTime.textContent = '--:--:--.---';
    metricClickTime.textContent = '--:--:--.---';
    metricLatency.textContent = '-- ms';
    metricQueueRank.textContent = '대기 -- 번';
    benchStatusBadge.textContent = '오픈 대기 중';
    benchStatusBadge.className = 'status-pill';

    window.dispatchEvent(new CustomEvent('beomchro:reset'));
  }

  // Activate Booking Button at exact 00:00 (Triggers MutationObserver in 0ms!)
  function triggerOpen() {
    if (isOpen) return;
    isOpen = true;
    openPerfTime = performance.now();
    openDate = new Date();

    metricOpenTime.textContent = formatTimeWithMs(openDate);
    gateHeadline.textContent = '⚡ 예매가 오픈되었습니다!';
    gateHeadline.style.color = '#2563eb';
    gateSubDesc.textContent = '지금 바로 [예매하기] 버튼이 활성화되었습니다.';

    // Remove disabled state & _disabled_2p3w6_34 class exactly like real Interpark/NOL Gate
    btnBooking.removeAttribute('disabled');
    btnBooking.disabled = false;
    btnBooking.classList.remove('_disabled_2p3w6_34');
    bookingBtnText.textContent = '예매하기';

    window.dispatchEvent(new CustomEvent('beomchro:opened', {
      detail: { openTime: openDate.getTime(), perfTime: openPerfTime }
    }));
  }

  // Start Countdown (5s or 10s)
  function startCountdown(seconds) {
    switchView('gate');
    resetSimulator(seconds);

    const startTime = performance.now();
    const durationMs = seconds * 1000;

    gateSubDesc.textContent = `⏱️ ${seconds}초 카운트다운 진행 중... 마우스에 손을 대지 마시고 그대로 지켜보세요!`;

    timerInterval = setInterval(() => {
      const elapsed = performance.now() - startTime;
      const remainingMs = durationMs - elapsed;

      if (remainingMs <= 0) {
        clearInterval(timerInterval);
        timerInterval = null;
        triggerOpen();
      } else {
        const secFloat = (remainingMs / 1000).toFixed(2);
        const mmSs = formatMmSs(remainingMs / 1000);
        bookingBtnText.textContent = `남은시간 ${mmSs} (${secFloat}s)`;
      }
    }, 25);
  }

  // Evaluate Queue Placement
  function evaluateQueue(latency) {
    const isAutoActive = !!window.__BEOMCHRO_ACTIVE__ && latency < 15;

    if (latency <= 2.0) {
      return {
        rankFormatted: '1',
        waitTime: '즉시 입장 (0분 00초)',
        tierName: '★ 신(GOD)의 영역 — 0ms 선점 성공',
        tierClass: 'god',
        triggerType: isAutoActive ? 'BEOMCHRO 0ms 자동 격발 (ON)' : '초광속 격발',
        progressWidth: '100%',
        desc: '축하합니다! 버튼이 열리는 찰나(0ms)에 자동 가로채기가 작동하여 대기열 1번으로 즉시 입장합니다!'
      };
    } else if (latency <= 25.0) {
      const rank = Math.max(2, Math.floor(latency * 1.4));
      return {
        rankFormatted: rank.toLocaleString(),
        waitTime: '약 3초 이내 입장',
        tierName: '⚡ 최상위 0.01% 고속 진입',
        tierClass: 'pro',
        triggerType: isAutoActive ? 'BEOMCHRO 자동 격발 (ON)' : '초고속 클릭',
        progressWidth: '92%',
        desc: '25ms 이내 진입 성공! 최선두 그룹으로 원하는 구역 연석 선점이 가능합니다.'
      };
    } else if (latency <= 180.0) {
      const rank = Math.floor(latency * 28) + 250;
      return {
        rankFormatted: rank.toLocaleString(),
        waitTime: '약 3분 소요',
        tierName: '🏃 빠른 손클릭 (준프로급)',
        tierClass: 'normal',
        triggerType: '수동 마우스 클릭',
        progressWidth: '55%',
        desc: '빠른 반응속도이지만 0ms 자동화 진입자들 뒤로 대기열이 배정되었습니다.'
      };
    } else {
      const rank = Math.floor(14290 + Math.max(0, latency - 300) * 90);
      return {
        rankFormatted: rank.toLocaleString(),
        waitTime: '약 48분 이상 (매진 주의)',
        tierName: '⚠️ 일반 수동 클릭 (매진 위험)',
        tierClass: 'late',
        triggerType: '수동 손클릭 (BEOMCHRO OFF)',
        progressWidth: '15%',
        desc: '사람의 평균 손클릭 반응속도(300ms+)입니다. 우측 상단 BEOMCHRO 스위치를 [🟢 ON]으로 켜고 다시 테스트해 보세요!'
      };
    }
  }

  // Handle Gate Booking Button Click
  btnBooking.addEventListener('click', () => {
    if (!isOpen) return;

    const clickPerfTime = performance.now();
    const clickDate = new Date();
    const rawLatency = Math.max(0.02, clickPerfTime - openPerfTime);
    const latencyMs = Number(rawLatency.toFixed(2));

    metricClickTime.textContent = formatTimeWithMs(clickDate);
    metricLatency.textContent = `${latencyMs} ms`;
    benchStatusBadge.textContent = '측정 완료';
    benchStatusBadge.className = 'status-pill done';

    const result = evaluateQueue(latencyMs);
    metricQueueRank.textContent = `대기 ${result.rankFormatted}번`;

    // Update Modal
    modalGameName.textContent = `${selectedGame.title} (${selectedGame.dateStr})`;
    modalQueueNumber.textContent = `${result.rankFormatted}번`;
    modalQueueWaitTime.textContent = `예상 대기시간: ${result.waitTime}`;
    modalLatency.textContent = `${latencyMs} ms`;
    modalTriggerType.textContent = result.triggerType;
    modalTier.textContent = result.tierName;
    modalDesc.textContent = result.desc;
    if (modalProgressBar) modalProgressBar.style.width = result.progressWidth;

    queueModal.classList.add('open');

    // Add History Row
    const emptyRow = historyTableBody.querySelector('.empty-row');
    if (emptyRow) emptyRow.remove();

    const row = document.createElement('tr');
    row.innerHTML = `
      <td><strong>#${++historyCount}</strong></td>
      <td>${selectedGame.badge}</td>
      <td>${result.triggerType}</td>
      <td><strong style="color:#2563eb; font-family:monospace;">${latencyMs} ms</strong></td>
      <td><strong style="color:#059669;">대기 ${result.rankFormatted}번</strong></td>
      <td>${result.waitTime}</td>
      <td><span class="tier-tag ${result.tierClass}">${result.tierName}</span></td>
      <td style="font-family:monospace; color:#64748b;">${formatTimeWithMs(clickDate)}</td>
    `;
    historyTableBody.insertBefore(row, historyTableBody.firstChild);
  });

  // Control Bar Button Listeners
  btnCountdown5.addEventListener('click', () => startCountdown(5));
  btnCountdown10.addEventListener('click', () => startCountdown(10));
  btnInstantOpen.addEventListener('click', () => {
    switchView('gate');
    resetSimulator(0);
    setTimeout(triggerOpen, 30);
  });
  btnReset.addEventListener('click', () => resetSimulator(5));

  // Modal Close & Retry Listeners
  modalClose.addEventListener('click', () => queueModal.classList.remove('open'));
  modalCloseBtn2.addEventListener('click', () => queueModal.classList.remove('open'));
  modalConfirmBtn.addEventListener('click', () => {
    queueModal.classList.remove('open');
    startCountdown(5);
  });

  // Initialize
  renderGameList();
  resetSimulator(5);

  window.BEOMCHRO_SIMULATOR = {
    triggerOpen,
    startCountdown,
    reset: resetSimulator,
    switchView
  };
})();
