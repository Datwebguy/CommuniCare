/**
 * CommuniCare Interactive AAC Studio Controller
 * Multi tenant caregiver isolation, customizable voice engine, sleek in-app toasts, and reliable speech sequencing.
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const caregiverSelect = document.getElementById('caregiver-select');
  const caregiverMessageInput = document.getElementById('caregiver-message');
  const recipientSelect = document.getElementById('recipient-select');
  const btnAddProfile = document.getElementById('btn-add-profile');
  const styleSelect = document.getElementById('style-select');
  const btnGenerate = document.getElementById('btn-generate');
  const presetsContainer = document.getElementById('presets-container');
  const pipelineStepsContainer = document.getElementById('pipeline-steps');
  const pipelineTimer = document.getElementById('pipeline-timer');
  const pipelineToggleHeader = document.getElementById('pipeline-toggle-header');
  const traceToggleText = document.getElementById('trace-toggle-text');
  const aacCardsGrid = document.getElementById('aac-cards-grid');
  const simplifiedBanner = document.getElementById('simplified-banner');
  const simplifiedText = document.getElementById('simplified-text');
  const boardTitle = document.getElementById('board-title');
  const boardIntentBadge = document.getElementById('board-intent-badge');
  const adaptationAlert = document.getElementById('adaptation-alert');
  const btnSpeakAll = document.getElementById('btn-speak-all');
  const btnVoiceSettings = document.getElementById('btn-voice-settings');
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

  // Add Profile Modal Elements
  const addProfileModal = document.getElementById('add-profile-modal');
  const btnCloseProfileModal = document.getElementById('btn-close-profile-modal');
  const addProfileForm = document.getElementById('add-profile-form');
  const newProfileName = document.getElementById('new-profile-name');
  const newProfileAge = document.getElementById('new-profile-age');
  const newProfileVocab = document.getElementById('new-profile-vocab');
  const newProfileCards = document.getElementById('new-profile-cards');
  const newProfileNotes = document.getElementById('new-profile-notes');

  // Voice Settings Modal Elements
  const voiceModal = document.getElementById('voice-modal');
  const btnCloseVoiceModal = document.getElementById('btn-close-voice-modal');
  const voicePersonaSelect = document.getElementById('voice-persona-select');
  const systemVoiceSelect = document.getElementById('system-voice-select');
  const voicePitchRange = document.getElementById('voice-pitch-range');
  const voicePitchLabel = document.getElementById('voice-pitch-label');
  const voiceRateRange = document.getElementById('voice-rate-range');
  const voiceRateLabel = document.getElementById('voice-rate-label');
  const voiceModeSelect = document.getElementById('voice-mode-select');
  const btnTestVoice = document.getElementById('btn-test-voice');
  const btnSaveVoice = document.getElementById('btn-save-voice');

  // Application State
  let currentBoard = null;
  let currentPresets = [];
  let currentRecipients = [];
  let isGenerating = false;
  let isTraceExpanded = true;
  let isSpeakingAll = false;
  let systemVoices = [];

  // Voice Configuration State
  let voiceConfig = {
    persona: 'female_adult',
    voiceURI: null,
    pitch: 1.05,
    rate: 0.85,
    mode: 'full_sentence_and_cards'
  };

  // Toast Container
  let toastContainer = document.querySelector('.toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container';
    document.body.appendChild(toastContainer);
  }

  /* =========================================================================
     IN-APP TOAST NOTIFICATION SYSTEM (No Native Browser Alerts)
     ========================================================================= */
  function showToast(title, message, type = 'info', duration = 4000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const ICONS = {
      info: '✨',
      success: '✓',
      warning: '⚠️',
      error: '✕'
    };

    toast.innerHTML = `
      <div class="toast-icon">${ICONS[type] || '✨'}</div>
      <div class="toast-content">
        <div class="toast-title">${title}</div>
        <div class="toast-message">${message}</div>
      </div>
    `;

    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.classList.add('toast-hide');
      setTimeout(() => {
        if (toast.parentElement) toast.parentElement.removeChild(toast);
      }, 300);
    }, duration);
  }

  // Active Caregiver ID helper
  function getActiveCaregiverId() {
    return caregiverSelect ? caregiverSelect.value : 'caregiver_primary';
  }

  // Initialize
  initApp();

  async function initApp() {
    initVoiceEngine();
    await reloadCaregiverWorkspace();
    setupEventListeners();
  }

  /* =========================================================================
     VOICE & AUDIO ENGINE
     ========================================================================= */
  function initVoiceEngine() {
    if (!('speechSynthesis' in window)) {
      console.warn('Speech synthesis not supported in this browser.');
      return;
    }

    const loadVoices = () => {
      systemVoices = window.speechSynthesis.getVoices();
      if (systemVoices.length > 0 && systemVoiceSelect) {
        systemVoiceSelect.innerHTML = '<option value="">Automatic Default Voice</option>';
        systemVoices.forEach(v => {
          const opt = document.createElement('option');
          opt.value = v.voiceURI;
          opt.textContent = `${v.name} (${v.lang})${v.default ? ' [Default]' : ''}`;
          systemVoiceSelect.appendChild(opt);
        });
      }
    };

    loadVoices();
    if (window.speechSynthesis.onvoiceschanged !== undefined) {
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }

    try {
      const saved = localStorage.getItem('communicare_voice_config');
      if (saved) {
        voiceConfig = { ...voiceConfig, ...JSON.parse(saved) };
      }
    } catch (e) {}

    updateVoiceUIFromConfig();
  }

  function updateVoiceUIFromConfig() {
    if (voicePersonaSelect) voicePersonaSelect.value = voiceConfig.persona;
    if (voicePitchRange) {
      voicePitchRange.value = voiceConfig.pitch;
      voicePitchLabel.textContent = `${Number(voiceConfig.pitch).toFixed(2)}x`;
    }
    if (voiceRateRange) {
      voiceRateRange.value = voiceConfig.rate;
      voiceRateLabel.textContent = `${Number(voiceConfig.rate).toFixed(2)}x`;
    }
    if (voiceModeSelect) voiceModeSelect.value = voiceConfig.mode;
    if (systemVoiceSelect && voiceConfig.voiceURI) {
      systemVoiceSelect.value = voiceConfig.voiceURI;
    }
  }

  const PERSONA_PRESETS = {
    child_friendly: { pitch: 1.40, rate: 0.85, genderHint: ['child', 'junior', 'zira', 'karen'] },
    female_adult: { pitch: 1.05, rate: 0.88, genderHint: ['female', 'samantha', 'victoria', 'eva', 'jenny'] },
    male_adult: { pitch: 0.85, rate: 0.85, genderHint: ['male', 'david', 'alex', 'george', 'guy'] },
    calm_sensory: { pitch: 0.95, rate: 0.72, genderHint: ['calm', 'soft', 'female', 'natural'] },
    expressive: { pitch: 1.25, rate: 0.98, genderHint: [] }
  };

  function applyPersonaPreset(personaKey) {
    const preset = PERSONA_PRESETS[personaKey];
    if (preset) {
      voiceConfig.persona = personaKey;
      voiceConfig.pitch = preset.pitch;
      voiceConfig.rate = preset.rate;
      
      if (preset.genderHint.length > 0 && systemVoices.length > 0) {
        const match = systemVoices.find(v => 
          preset.genderHint.some(h => v.name.toLowerCase().includes(h) || v.voiceURI.toLowerCase().includes(h))
        );
        if (match) {
          voiceConfig.voiceURI = match.voiceURI;
        }
      }

      updateVoiceUIFromConfig();
    }
  }

  function getSelectedSpeechVoice() {
    if (voiceConfig.voiceURI && systemVoices.length > 0) {
      const found = systemVoices.find(v => v.voiceURI === voiceConfig.voiceURI);
      if (found) return found;
    }
    const englishVoice = systemVoices.find(v => v.lang.startsWith('en'));
    return englishVoice || null;
  }

  function sanitizeTextForSpeech(text) {
    if (!text) return '';
    return text
      .replace(/[→⇒⇨➔➜]/g, ' ')
      .replace(/->|=>/g, ' ')
      .replace(/[-_]/g, ' ')
      .replace(/[•*#~|/\\<>[\]{}]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  function speakSingleWord(text, cardEl = null) {
    if (!('speechSynthesis' in window)) return Promise.resolve();
    
    const cleanText = sanitizeTextForSpeech(text);
    if (!cleanText) return Promise.resolve();

    window.speechSynthesis.cancel();
    window.speechSynthesis.resume();

    const utterance = new SpeechSynthesisUtterance(cleanText);
    window._currentUtterance = utterance;

    const voice = getSelectedSpeechVoice();
    if (voice) utterance.voice = voice;
    utterance.pitch = voiceConfig.pitch;
    utterance.rate = voiceConfig.rate;

    if (cardEl) {
      cardEl.classList.add('card-speaking');
    }

    return new Promise((resolve) => {
      let settled = false;
      const finish = () => {
        if (!settled) {
          settled = true;
          window._currentUtterance = null;
          if (cardEl) cardEl.classList.remove('card-speaking');
          resolve();
        }
      };

      utterance.onend = finish;
      utterance.onerror = (e) => {
        console.warn('Speech error/interrupted:', e);
        finish();
      };

      const safetyTimeoutMs = Math.max(3500, (cleanText.length * 160) / Math.max(0.5, voiceConfig.rate));
      setTimeout(finish, safetyTimeoutMs);

      window.speechSynthesis.speak(utterance);
    });
  }

  async function speakAllBoardSequence() {
    if (!currentBoard || !currentBoard.cards || currentBoard.cards.length === 0) return;

    if (isSpeakingAll) {
      window.speechSynthesis.cancel();
      isSpeakingAll = false;
      btnSpeakAll.innerHTML = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/></svg><span>Speak All</span>';
      document.querySelectorAll('.aac-card').forEach(c => c.classList.remove('card-speaking'));
      if (simplifiedBanner) simplifiedBanner.classList.remove('box-speaking');
      return;
    }

    isSpeakingAll = true;
    btnSpeakAll.innerHTML = '<span>⏹️ Stop Voice</span>';

    try {
      if (voiceConfig.mode === 'full_sentence_and_cards' || voiceConfig.mode === 'sentence_only') {
        if (simplifiedBanner && simplifiedText) {
          simplifiedBanner.classList.add('box-speaking');
          await speakSingleWord(simplifiedText.textContent);
          simplifiedBanner.classList.remove('box-speaking');
          await new Promise(r => setTimeout(r, 400));
        }
      }

      if (voiceConfig.mode === 'sentence_only') {
        isSpeakingAll = false;
        btnSpeakAll.innerHTML = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/></svg><span>Speak All</span>';
        return;
      }

      const cardElements = document.querySelectorAll('.aac-card');
      for (let i = 0; i < currentBoard.cards.length; i++) {
        if (!isSpeakingAll) break;

        const card = currentBoard.cards[i];
        const cardEl = cardElements[i];

        await speakSingleWord(card.word, cardEl);
        await new Promise(r => setTimeout(r, 250));
      }
    } finally {
      isSpeakingAll = false;
      btnSpeakAll.innerHTML = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/></svg><span>Speak All</span>';
      document.querySelectorAll('.aac-card').forEach(c => c.classList.remove('card-speaking'));
      if (simplifiedBanner) simplifiedBanner.classList.remove('box-speaking');
    }
  }

  /* =========================================================================
     WORKSPACE & DATA LOADING
     ========================================================================= */
  async function reloadCaregiverWorkspace(selectedRecipientId = null) {
    await loadRecipients(selectedRecipientId);
    await loadPresets();
  }

  async function loadRecipients(selectedId = null) {
    const cid = getActiveCaregiverId();
    try {
      const res = await fetch(`/api/recipients?caregiver_id=${encodeURIComponent(cid)}`, {
        headers: { 'X-Caregiver-ID': cid }
      });
      if (res.ok) {
        currentRecipients = await res.json();
        renderRecipientSelect(selectedId);
      }
    } catch (e) {
      console.warn('Could not load recipients:', e);
    }
  }

  function renderRecipientSelect(selectedId = null) {
    recipientSelect.innerHTML = '';
    if (currentRecipients.length === 0) {
      recipientSelect.innerHTML = '<option value="">No recipients in workspace</option>';
      return;
    }

    currentRecipients.forEach(r => {
      const opt = document.createElement('option');
      opt.value = r.recipient_id;
      const emoji = r.age_group === 'child' ? '👦' : (r.age_group === 'teen' ? '🧑' : '👩');
      opt.textContent = `${emoji} ${r.name} (${r.age_group.toUpperCase()} • ${r.vocabulary_level.toUpperCase()})`;
      recipientSelect.appendChild(opt);
    });

    if (selectedId) {
      recipientSelect.value = selectedId;
    }
  }

  async function loadPresets() {
    const cid = getActiveCaregiverId();
    try {
      const res = await fetch(`/api/presets?caregiver_id=${encodeURIComponent(cid)}`, {
        headers: { 'X-Caregiver-ID': cid }
      });
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
      const chip = document.createElement('button');
      chip.className = 'preset-chip';
      chip.type = 'button';
      chip.innerHTML = `${icon} ${p.title}`;
      chip.title = p.description || p.message;
      chip.addEventListener('click', () => {
        caregiverMessageInput.value = p.message;
        if (p.recipient_id && currentRecipients.some(r => r.recipient_id === p.recipient_id)) {
          recipientSelect.value = p.recipient_id;
        }
        caregiverMessageInput.focus();
      });
      presetsContainer.appendChild(chip);
    });
  }

  /* =========================================================================
     EVENT LISTENERS
     ========================================================================= */
  function setupEventListeners() {
    if (caregiverSelect) {
      caregiverSelect.addEventListener('change', () => {
        reloadCaregiverWorkspace();
      });
    }

    btnGenerate.addEventListener('click', () => handleGenerateBoard());
    
    document.addEventListener('click', (e) => {
      if (e.target && e.target.id === 'btn-quick-sample') {
        if (currentPresets.length > 0) {
          caregiverMessageInput.value = currentPresets[0].message;
          handleGenerateBoard();
        }
      }
    });

    btnSpeakAll.addEventListener('click', () => speakAllBoardSequence());
    btnPrintBoard.addEventListener('click', () => window.print());
    btnFullscreen.addEventListener('click', () => togglePresentationMode(true));
    btnExitPresentation.addEventListener('click', () => togglePresentationMode(false));
    
    pipelineToggleHeader.addEventListener('click', () => {
      isTraceExpanded = !isTraceExpanded;
      if (isTraceExpanded) {
        pipelineStepsContainer.classList.remove('hidden');
        traceToggleText.textContent = 'Hide Details';
      } else {
        pipelineStepsContainer.classList.add('hidden');
        traceToggleText.textContent = 'View Details';
      }
    });

    btnVoiceSettings.addEventListener('click', () => {
      updateVoiceUIFromConfig();
      voiceModal.classList.remove('hidden');
    });

    btnCloseVoiceModal.addEventListener('click', () => {
      voiceModal.classList.add('hidden');
    });

    voiceModal.addEventListener('click', (e) => {
      if (e.target === voiceModal) voiceModal.classList.add('hidden');
    });

    voicePersonaSelect.addEventListener('change', (e) => {
      if (e.target.value !== 'custom') {
        applyPersonaPreset(e.target.value);
      } else {
        voiceConfig.persona = 'custom';
      }
    });

    systemVoiceSelect.addEventListener('change', (e) => {
      voiceConfig.voiceURI = e.target.value || null;
      voiceConfig.persona = 'custom';
      voicePersonaSelect.value = 'custom';
    });

    voicePitchRange.addEventListener('input', (e) => {
      voiceConfig.pitch = parseFloat(e.target.value);
      voicePitchLabel.textContent = `${voiceConfig.pitch.toFixed(2)}x`;
      voiceConfig.persona = 'custom';
      voicePersonaSelect.value = 'custom';
    });

    voiceRateRange.addEventListener('input', (e) => {
      voiceConfig.rate = parseFloat(e.target.value);
      voiceRateLabel.textContent = `${voiceConfig.rate.toFixed(2)}x`;
      voiceConfig.persona = 'custom';
      voicePersonaSelect.value = 'custom';
    });

    voiceModeSelect.addEventListener('change', (e) => {
      voiceConfig.mode = e.target.value;
    });

    btnTestVoice.addEventListener('click', () => {
      speakSingleWord('Hello! CommuniCare is ready with your selected voice tone.');
    });

    btnSaveVoice.addEventListener('click', () => {
      try {
        localStorage.setItem('communicare_voice_config', JSON.stringify(voiceConfig));
        showToast('Voice Settings Saved', 'Your speech persona preferences have been applied.', 'success');
      } catch (e) {}
      voiceModal.classList.add('hidden');
    });

    btnMemoryView.addEventListener('click', () => openMemoryModal());
    btnCloseModal.addEventListener('click', () => closeMemoryModal());
    btnCloseModalBottom.addEventListener('click', () => closeMemoryModal());
    memoryModal.addEventListener('click', (e) => {
      if (e.target === memoryModal) closeMemoryModal();
    });

    btnAddProfile.addEventListener('click', () => {
      addProfileForm.reset();
      addProfileModal.classList.remove('hidden');
      newProfileName.focus();
    });
    btnCloseProfileModal.addEventListener('click', () => {
      addProfileModal.classList.add('hidden');
    });
    addProfileModal.addEventListener('click', (e) => {
      if (e.target === addProfileModal) addProfileModal.classList.add('hidden');
    });

    addProfileForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = newProfileName.value.trim();
      if (!name) return;

      const cid = getActiveCaregiverId();
      const recipientId = name.toLowerCase().replace(/[^a-z0-9]/g, '_') + '_' + Math.floor(Math.random() * 1000);
      const newProfile = {
        recipient_id: recipientId,
        caregiver_id: cid,
        name: name,
        age_group: newProfileAge.value,
        vocabulary_level: newProfileVocab.value,
        max_board_cards: parseInt(newProfileCards.value, 10),
        high_contrast_mode: true,
        color_coding_enabled: true,
        caregiver_notes: newProfileNotes.value.trim() || null,
        preferred_symbol_mappings: {},
        learned_vocabulary: [],
        success_history: {}
      };

      try {
        const res = await fetch('/api/recipients', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Caregiver-ID': cid
          },
          body: JSON.stringify(newProfile)
        });
        if (res.ok) {
          addProfileModal.classList.add('hidden');
          await loadRecipients(recipientId);
          showToast('Profile Created', `Profile for "${name}" created successfully in Firestore.`, 'success');
        }
      } catch (err) {
        showToast('Profile Error', `Failed to save profile: ${err.message}`, 'error');
      }
    });

    btnDemoTour.addEventListener('click', () => runAdaptiveDemo());

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && document.body.classList.contains('presentation-mode')) {
        togglePresentationMode(false);
      }
    });
  }

  /* =========================================================================
     BOARD GENERATION & RENDERING
     ========================================================================= */
  async function handleGenerateBoard(customMessage = null, customRecipient = null) {
    const rawMessage = customMessage || caregiverMessageInput.value.trim();
    const recipientId = customRecipient || recipientSelect.value;
    const style = styleSelect.value;
    const cid = getActiveCaregiverId();

    if (!rawMessage) {
      showToast('Message Required', 'Please enter or select a caregiver message first.', 'warning');
      caregiverMessageInput.focus();
      return;
    }

    if (!recipientId) {
      showToast('Recipient Required', 'Please select or create a care recipient profile first.', 'warning');
      return;
    }

    if (isGenerating) return;
    isGenerating = true;
    btnGenerate.disabled = true;
    btnGenerate.innerHTML = '<span>⚡ Processing...</span>';

    renderPipelineRunning();
    const startTime = performance.now();

    try {
      const response = await fetch('/api/generate-board', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Caregiver-ID': cid
        },
        body: JSON.stringify({
          message: rawMessage,
          recipient_id: recipientId,
          caregiver_id: cid,
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
      showToast('Generation Error', `Could not generate board: ${err.message}`, 'error');
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
      { num: 1, title: 'Memory Lookup', desc: 'Fetching profile...' },
      { num: 2, title: 'Simplification', desc: 'Reasoning concepts...' },
      { num: 3, title: 'Symbol Resolution', desc: 'Matching pictograms...' },
      { num: 4, title: 'Board Assembly', desc: 'Fitzgerald Key layout...' },
      { num: 5, title: 'State Persistence', desc: 'Saving memory...' },
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
              <span style="font-size:0.68rem; color:var(--color-royal-violet); font-weight:800; margin-left:4px;">(${step.duration_ms}ms)</span>
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

    document.querySelectorAll('.aac-card').forEach(cardEl => {
      cardEl.addEventListener('click', () => {
        const word = cardEl.getAttribute('data-word');
        speakSingleWord(word, cardEl);
      });
    });
  }

  window.handleFeedback = async function(boardId, recipientId, cardId, word, action) {
    const cid = getActiveCaregiverId();
    try {
      const res = await fetch('/api/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Caregiver-ID': cid
        },
        body: JSON.stringify({
          board_id: boardId,
          recipient_id: recipientId,
          caregiver_id: cid,
          card_id: cardId,
          word: word,
          action: action
        })
      });

      if (res.ok) {
        showToast('Memory Reinforced', `Reinforced '${word.toUpperCase()}' in ${recipientId}'s memory.`, 'success');
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
    const cid = getActiveCaregiverId();
    if (!recipientId) return;

    try {
      const res = await fetch(`/api/recipients/${recipientId}?caregiver_id=${encodeURIComponent(cid)}`, {
        headers: { 'X-Caregiver-ID': cid }
      });
      if (res.ok) {
        const profile = await res.json();
        renderMemoryModal(profile);
        memoryModal.classList.remove('hidden');
      }
    } catch (e) {
      showToast('Memory Error', `Could not load memory for ${recipientId}`, 'error');
    }
  }

  function closeMemoryModal() {
    memoryModal.classList.add('hidden');
  }

  function renderMemoryModal(profile) {
    memoryProfileSummary.innerHTML = `
      <strong style="color:var(--color-ink-charcoal); font-size:1rem;">${profile.name}</strong> (${profile.age_group.toUpperCase()}) &bull; 
      Vocabulary Level: <span style="color:var(--color-royal-violet); font-weight:700;">${profile.vocabulary_level.toUpperCase()}</span> &bull; 
      Max Board Cards: <strong>${profile.max_board_cards}</strong><br/>
      <div style="margin-top:6px;"><em>Caregiver Notes:</em> ${profile.caregiver_notes || 'None recorded.'}</div>
    `;

    if (!profile.learned_vocabulary || profile.learned_vocabulary.length === 0) {
      learnedVocabCloud.innerHTML = '<div style="color:var(--color-stone-gray); font-size:0.8rem;">No learned words recorded yet. Generate boards to build memory.</div>';
    } else {
      learnedVocabCloud.innerHTML = profile.learned_vocabulary.map(word => {
        const count = (profile.success_history && profile.success_history[word]) || 1;
        return `
          <div class="vocab-chip">
            <span>${word.toUpperCase()}</span>
            <span class="vocab-count">${count}&times;</span>
          </div>
        `;
      }).join('');
    }

    const prefs = Object.entries(profile.preferred_symbol_mappings || {});
    if (prefs.length === 0) {
      symbolPrefList.innerHTML = '<div style="color:var(--color-stone-gray); font-size:0.8rem;">No custom symbol overrides yet.</div>';
    } else {
      symbolPrefList.innerHTML = prefs.map(([k, v]) => `
        <div class="pref-item">
          <span><strong>${k.toUpperCase()}</strong></span>
          <span style="color:var(--color-royal-violet); font-weight:700;">Icon: ${v}</span>
        </div>
      `).join('');
    }
  }

  /* =========================================================================
     SMOOTH AUTOMATED ADAPTIVE DEMO (No Disruptive Browser Alerts)
     ========================================================================= */
  async function runAdaptiveDemo() {
    showToast('Adaptive Demo Started', 'Turn 1 of 2: Processing morning routine message for Leo...', 'info', 5000);

    if (currentRecipients.some(r => r.recipient_id === 'leo_care')) {
      recipientSelect.value = 'leo_care';
    }
    caregiverMessageInput.value = 'Good morning Leo! Please take your medicine with a glass of water, then we will have warm pancakes for breakfast.';
    await handleGenerateBoard();

    await new Promise(r => setTimeout(r, 2400));
    showToast('Reinforcing Memory', "Caregiver feedback: Reinforcing 'MEDICINE' preference in Firestore...", 'success', 4000);

    await fetch('/api/feedback', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Caregiver-ID': getActiveCaregiverId()
      },
      body: JSON.stringify({
        board_id: currentBoard ? currentBoard.board_id : 'demo',
        recipient_id: recipientSelect.value,
        caregiver_id: getActiveCaregiverId(),
        word: 'medicine',
        action: 'worked_well',
        preferred_symbol: 'medicine'
      })
    });

    await new Promise(r => setTimeout(r, 2000));
    showToast('Turn 2: Personalization', 'Processing afternoon reminder with learned preferences applied...', 'info', 5000);

    caregiverMessageInput.value = 'Leo, remember to take your afternoon medicine before we go for a walk.';
    await handleGenerateBoard();

    await new Promise(r => setTimeout(r, 1200));
    showToast('Demo Complete', '✨ Multi-Turn Personalization successfully retrieved from Firestore memory!', 'success', 6000);
  }
});
