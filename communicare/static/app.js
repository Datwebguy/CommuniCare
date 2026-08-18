/**
 * CommuniCare: Interactive Frontend & Autonomous Pipeline Visualizer
 * Modern, accessible, high-contrast AAC interface with Web Speech audio.
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const caregiverMessageInput = document.getElementById('caregiver-message');
  const recipientSelect = document.getElementById('recipient-select');
  const styleSelect = document.getElementById('style-select');
  const btnGenerate = document.getElementById('btn-generate');
  const presetsContainer = document.getElementById('presets-container');
  const pipelineStepsContainer = document.getElementById('pipeline-steps');
  const pipelineTimer = document.getElementById('pipeline-timer');
  const aacCardsGrid = document.getElementById('aac-cards-grid');
  const simplifiedText = document.getElementById('simplified-text');
  const boardTitle = document.getElementById('board-title');
  const boardIntentBadge = document.getElementById('board-intent-badge');
  const adaptationAlert = document.getElementById('adaptation-alert');
  const btnSpeakAll = document.getElementById('btn-speak-all');
  const btnPrintBoard = document.getElementById('btn-print-board');
  const btnFullscreen = document.getElementById('btn-fullscreen');
  const btnMemoryView = document.getElementById('btn-memory-view');
  const btnDemoTour = document.getElementById('btn-demo-tour');
  const memoryModal = document.getElementById('memory-modal');
  const btnCloseModal = document.getElementById('btn-close-modal');
  const btnCloseModalBottom = document.getElementById('btn-close-modal-bottom');
  const memoryProfileSummary = document.getElementById('memory-profile-summary');
  const learnedVocabCloud = document.getElementById('learned-vocab-cloud');
  const symbolPrefList = document.getElementById('symbol-pref-list');
  const presentationBanner = document.getElementById('presentation-banner');
  const btnExitPresentation = document.getElementById('btn-exit-presentation');
  const presentationRecipient = document.getElementById('presentation-recipient');
  const statusText = document.getElementById('status-text');

  // Application State
  let currentBoard = null;
  let currentPresets = [];
  let isGenerating = false;

  // Initialize
  initApp();

  async function initApp() {
    await checkSystemHealth();
    await loadPresets();
    setupEventListeners();
  }

  async function checkSystemHealth() {
    try {
      const res = await fetch('/api/health');
      if (res.ok) {
        const data = await res.json();
        statusText.textContent = data.firestore_mode.includes('Cloud') 
          ? 'Cloud Run & Firestore Live' 
          : 'Local Agent Engine Ready';
      }
    } catch (e) {
      statusText.textContent = 'Agent Ready (Offline Mode)';
    }
  }

  async function loadPresets() {
    try {
      const res = await fetch('/api/presets');
      if (res.ok) {
        currentPresets = await res.json();
        renderPresets();
      }
    } catch (e) {
      console.warn('Could not load presets:', e);
    }
  }

  const PRESET_ICONS = {
    "morning_breakfast_walk": "🌅",
    "medical_checkin": "🩺",
    "school_transition": "🎒",
    "evening_bedtime": "🌙"
  };

  function renderPresets() {
    presetsContainer.innerHTML = '';
    currentPresets.forEach((p) => {
      const icon = PRESET_ICONS[p.id] || "📋";
      const pill = document.createElement('div');
      pill.className = 'preset-pill';
      pill.innerHTML = `
        <span class="preset-title">${icon} ${p.title}</span>
        <span class="preset-desc">${p.description}</span>
      `;
      pill.addEventListener('click', () => {
        caregiverMessageInput.value = p.message;
        if (p.recipient_id) {
          recipientSelect.value = p.recipient_id;
        }
        caregiverMessageInput.focus();
      });
      presetsContainer.appendChild(pill);
    });
  }

  function setupEventListeners() {
    btnGenerate.addEventListener('click', () => handleGenerateBoard());
    
    // Quick sample button in empty state
    document.addEventListener('click', (e) => {
      if (e.target && e.target.id === 'btn-quick-sample') {
        if (currentPresets.length > 0) {
          caregiverMessageInput.value = currentPresets[0].message;
          handleGenerateBoard();
        }
      }
    });

    btnSpeakAll.addEventListener('click', () => speakAllCards());
    btnPrintBoard.addEventListener('click', () => window.print());
    btnFullscreen.addEventListener('click', () => togglePresentationMode(true));
    btnExitPresentation.addEventListener('click', () => togglePresentationMode(false));
    
    // Memory Modal
    btnMemoryView.addEventListener('click', () => openMemoryModal());
    btnCloseModal.addEventListener('click', () => closeMemoryModal());
    btnCloseModalBottom.addEventListener('click', () => closeMemoryModal());
    memoryModal.addEventListener('click', (e) => {
      if (e.target === memoryModal) closeMemoryModal();
    });

    // 2-Turn Adaptive Demo Showcase
    btnDemoTour.addEventListener('click', () => runTwoTurnAdaptiveDemo());

    // Keyboard navigation (Esc to exit fullscreen)
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && document.body.classList.contains('presentation-mode')) {
        togglePresentationMode(false);
      }
    });
  }

  async function handleGenerateBoard(customMessage = null, customRecipient = null) {
    const rawMessage = customMessage || caregiverMessageInput.value.trim();
    const recipientId = customRecipient || recipientSelect.value;
    const style = styleSelect.value;

    if (!rawMessage) {
      alert('Please enter or select a caregiver message first.');
      caregiverMessageInput.focus();
      return;
    }

    if (isGenerating) return;
    isGenerating = true;
    btnGenerate.disabled = true;
    btnGenerate.innerHTML = '<span>⚡ Processing Pipeline...</span>';

    renderPipelineRunning();
    const startTime = performance.now();

    try {
      const response = await fetch('/api/generate-board', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: rawMessage,
          recipient_id: recipientId,
          simplify_style: style
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned status ${response.status}`);
      }

      const boardData = await response.json();
      currentBoard = boardData;
      
      const totalTime = ((performance.now() - startTime) / 1000).toFixed(2);
      pipelineTimer.textContent = `Completed in ${totalTime}s`;

      renderPipelineTrace(boardData.pipeline_trace);
      renderAACBoard(boardData);

    } catch (err) {
      console.error('Board generation error:', err);
      alert(`Could not generate board: ${err.message}`);
      pipelineTimer.textContent = 'Error';
    } finally {
      isGenerating = false;
      btnGenerate.disabled = false;
      btnGenerate.innerHTML = '<span>⚡ Generate AAC Board</span>';
    }
  }

  function renderPipelineRunning() {
    pipelineTimer.textContent = 'Executing...';
    const steps = [
      { num: 1, title: 'Firestore Recipient Memory', desc: 'Fetching vocabulary profile & preferences...' },
      { num: 2, title: 'Gemini Language Simplification', desc: 'Reasoning about core AAC concepts...' },
      { num: 3, title: 'ARASAAC Symbol Resolution', desc: 'Matching symbols with graceful text fallback...' },
      { num: 4, title: 'High-Contrast Board Assembly', desc: 'Applying Fitzgerald Key color standards...' },
      { num: 5, title: 'Firestore State Persistence', desc: 'Recording interaction to memory...' },
    ];

    pipelineStepsContainer.innerHTML = steps.map(s => `
      <div class="pipeline-step step-running">
        <div class="step-icon">${s.num}</div>
        <div class="step-info">
          <div class="step-title">${s.title}</div>
          <div class="step-desc">${s.desc}</div>
        </div>
      </div>
    `).join('');
  }

  function renderPipelineTrace(traceSteps) {
    if (!traceSteps || traceSteps.length === 0) return;

    pipelineStepsContainer.innerHTML = traceSteps.map(step => {
      const statusClass = step.status === 'completed' 
        ? 'step-completed' 
        : (step.status === 'fallback' ? 'step-fallback' : 'step-running');

      return `
        <div class="pipeline-step ${statusClass}">
          <div class="step-icon">${step.step_number}</div>
          <div class="step-info">
            <div class="step-title">
              ${step.step_name} 
              <span style="font-size:0.7rem; color:var(--brand-primary); font-weight:700; margin-left:6px;">(${step.duration_ms}ms)</span>
            </div>
            <div class="step-desc">${step.output_summary || step.description}</div>
          </div>
        </div>
      `;
    }).join('');
  }

  function renderAACBoard(board) {
    boardTitle.textContent = `${board.recipient_name}'s Board`;
    boardIntentBadge.textContent = board.core_intent;
    simplifiedText.textContent = board.simplified_message;

    // Show personalization indicator if adaptations occurred
    if (board.personalized_adaptations_applied && board.personalized_adaptations_applied.length > 0) {
      adaptationAlert.textContent = `✨ ${board.personalized_adaptations_applied.join(' | ')}`;
      adaptationAlert.classList.remove('hidden');
    } else {
      adaptationAlert.classList.add('hidden');
    }

    if (!board.cards || board.cards.length === 0) {
      aacCardsGrid.innerHTML = `
        <div class="empty-board-state">
          <div class="empty-icon">⚠️</div>
          <h3>No concepts extracted</h3>
          <p>Please try a more descriptive caregiver message.</p>
        </div>
      `;
      return;
    }

    aacCardsGrid.innerHTML = board.cards.map((card, index) => {
      const visualElement = card.svg_icon 
        ? card.svg_icon 
        : (card.image_url 
            ? `<img src="${card.image_url}" alt="${card.word}" loading="lazy" />`
            : `<div style="font-size:2.8rem; font-weight:800; color:${card.color_code}">📝</div>`);

      return `
        <div class="aac-card" 
             style="--card-border: ${card.color_code}; --tag-color: ${card.color_code}; --tag-bg: ${card.bg_color};"
             data-word="${card.word}"
             data-card-id="${card.id}"
             data-index="${index}"
             title="Click to speak '${card.word}'">
          
          <div class="card-category-tag">${card.category.toUpperCase()}</div>
          <div class="card-audio-hint">🔊</div>

          <div class="card-visual-wrapper">
            ${visualElement}
          </div>

          <div class="card-label">${card.word}</div>
          ${card.subtext ? `<div class="card-subtext">${card.subtext}</div>` : ''}

          <div class="card-actions-bar">
            <button class="btn-card-action" onclick="event.stopPropagation(); window.handleFeedback('${board.board_id}', '${board.recipient_id}', '${card.id}', '${card.word}', 'worked_well')">
              👍 Worked Well
            </button>
          </div>
        </div>
      `;
    }).join('');

    // Attach click to speak for all cards
    document.querySelectorAll('.aac-card').forEach(cardEl => {
      cardEl.addEventListener('click', () => {
        const word = cardEl.getAttribute('data-word');
        speakWord(word);
        
        cardEl.style.transform = 'scale(1.04)';
        setTimeout(() => { cardEl.style.transform = ''; }, 200);
      });
    });
  }

  function speakWord(text) {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  }

  async function speakAllCards() {
    if (!currentBoard || !currentBoard.cards) return;
    const cards = document.querySelectorAll('.aac-card');
    for (let i = 0; i < currentBoard.cards.length; i++) {
      const card = currentBoard.cards[i];
      const cardEl = cards[i];
      
      if (cardEl) {
        cardEl.style.boxShadow = '0 0 0 4px #2563EB';
      }
      speakWord(card.word);
      await new Promise(r => setTimeout(r, 950));
      if (cardEl) {
        cardEl.style.boxShadow = '';
      }
    }
  }

  window.handleFeedback = async function(boardId, recipientId, cardId, word, action) {
    try {
      const res = await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          board_id: boardId,
          recipient_id: recipientId,
          card_id: cardId,
          word: word,
          action: action
        })
      });

      if (res.ok) {
        alert(`Saved to memory: '${word}' reinforced for ${recipientId}.`);
      }
    } catch (e) {
      console.error('Feedback error:', e);
    }
  };

  function togglePresentationMode(enable) {
    if (enable) {
      document.body.classList.add('presentation-mode');
      presentationRecipient.textContent = `Showing Board to: ${currentBoard ? currentBoard.recipient_name : 'Recipient'}`;
      presentationBanner.classList.remove('hidden');
    } else {
      document.body.classList.remove('presentation-mode');
      presentationBanner.classList.add('hidden');
    }
  }

  async function openMemoryModal() {
    const recipientId = recipientSelect.value;
    try {
      const res = await fetch(`/api/recipients/${recipientId}`);
      if (res.ok) {
        const profile = await res.json();
        renderMemoryModal(profile);
        memoryModal.classList.remove('hidden');
      }
    } catch (e) {
      alert(`Could not load memory for ${recipientId}`);
    }
  }

  function closeMemoryModal() {
    memoryModal.classList.add('hidden');
  }

  function renderMemoryModal(profile) {
    memoryProfileSummary.innerHTML = `
      <strong style="color:var(--text-primary); font-size:1rem;">${profile.name}</strong> (${profile.age_group.toUpperCase()}) &bull; 
      Vocabulary Level: <span style="color:var(--brand-primary); font-weight:700;">${profile.vocabulary_level.toUpperCase()}</span> &bull; 
      Max Board Cards: <strong>${profile.max_board_cards}</strong><br/>
      <div style="margin-top:6px;"><em>Caregiver Notes:</em> ${profile.caregiver_notes || 'None recorded.'}</div>
    `;

    learnedVocabCloud.innerHTML = profile.learned_vocabulary.map(word => {
      const count = profile.success_history[word] || 1;
      return `
        <div class="vocab-chip">
          <span>${word.toUpperCase()}</span>
          <span class="vocab-count">${count}&times;</span>
        </div>
      `;
    }).join('');

    const prefs = Object.entries(profile.preferred_symbol_mappings);
    if (prefs.length === 0) {
      symbolPrefList.innerHTML = '<div style="color:var(--text-secondary); font-size:0.8rem;">No custom symbol overrides yet.</div>';
    } else {
      symbolPrefList.innerHTML = prefs.map(([k, v]) => `
        <div class="pref-item">
          <span><strong>${k.toUpperCase()}</strong></span>
          <span style="color:var(--brand-primary); font-weight:700;">Icon: ${v}</span>
        </div>
      `).join('');
    }
  }

  async function runTwoTurnAdaptiveDemo() {
    alert("Starting 2-Turn Adaptive Memory Demonstration:\n\nTurn 1: CommuniCare processes a morning routine message.\nFeedback: Caregiver reinforces 'medicine' & 'pancakes'.\nTurn 2: CommuniCare processes an afternoon reminder and automatically applies learned Firestore preferences!");

    recipientSelect.value = 'leo_care';
    caregiverMessageInput.value = 'Good morning Leo! Please take your medicine with a glass of water, and then we will have warm pancakes for breakfast.';
    await handleGenerateBoard();

    await new Promise(r => setTimeout(r, 1800));
    await fetch('/api/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        board_id: currentBoard ? currentBoard.board_id : 'demo',
        recipient_id: 'leo_care',
        word: 'medicine',
        action: 'worked_well',
        preferred_symbol: 'medicine'
      })
    });

    await new Promise(r => setTimeout(r, 1200));
    caregiverMessageInput.value = 'Leo, remember to take your afternoon medicine before we go for a walk.';
    await handleGenerateBoard();
  }
});
