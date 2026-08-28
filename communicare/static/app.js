/**
 * CommuniCare Interactive AAC Studio Controller
 * Full user authentication, Google Authenticator 2FA, password recovery,
 * multi tenant caregiver isolation, voice tone studio, and reliable speech sequencing.
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements - Studio & Board
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
  const btnDemoTour = document.getElementById('btn-demo-tour');
  const presentationBanner = document.getElementById('presentation-banner');
  const btnExitPresentation = document.getElementById('btn-exit-presentation');
  const presentationRecipient = document.getElementById('presentation-recipient');

  // DOM Elements - User Profile & Dropdown
  const btnUserMenu = document.getElementById('btn-user-menu');
  const userDropdownMenu = document.getElementById('user-dropdown-menu');
  const userDisplayName = document.getElementById('user-display-name');
  const userAvatarInitials = document.getElementById('user-avatar-initials');
  const dropdownUserName = document.getElementById('dropdown-user-name');
  const dropdownUserEmail = document.getElementById('dropdown-user-email');
  const dropdown2faBadge = document.getElementById('dropdown-2fa-badge');
  const dropdownBtn2fa = document.getElementById('dropdown-btn-2fa');
  const dropdownBtnMemory = document.getElementById('dropdown-btn-memory');
  const dropdownBtnAddRecipient = document.getElementById('dropdown-btn-add-recipient');
  const dropdownBtnAuth = document.getElementById('dropdown-btn-auth');
  const dropdownAuthLabel = document.getElementById('dropdown-auth-label');
  const btnHeaderSignin = document.getElementById('btn-header-signin');
  const userProfileMenuContainer = document.getElementById('user-profile-menu-container');

  // DOM Elements - Auth Modal
  const authModal = document.getElementById('auth-modal');
  const btnCloseAuthModal = document.getElementById('btn-close-auth-modal');
  const authModalTitle = document.getElementById('auth-modal-title');
  const tabAuthLogin = document.getElementById('tab-auth-login');
  const tabAuthRegister = document.getElementById('tab-auth-register');
  const tabAuthForgot = document.getElementById('tab-auth-forgot');
  const authAlert = document.getElementById('auth-alert');
  const formAuthLogin = document.getElementById('form-auth-login');
  const loginEmail = document.getElementById('login-email');
  const loginPassword = document.getElementById('login-password');
  const login2faField = document.getElementById('login-2fa-field');
  const loginTotp = document.getElementById('login-totp');
  const formAuthRegister = document.getElementById('form-auth-register');
  const regFullname = document.getElementById('reg-fullname');
  const regEmail = document.getElementById('reg-email');
  const regPassword = document.getElementById('reg-password');
  const formAuthForgot = document.getElementById('form-auth-forgot');
  const forgotEmail = document.getElementById('forgot-email');
  const resetTokenGroup = document.getElementById('reset-token-group');
  const resetToken = document.getElementById('reset-token');
  const resetNewPassword = document.getElementById('reset-new-password');
  const btnSubmitForgot = document.getElementById('btn-submit-forgot');

  // DOM Elements - 2FA Security Modal
  const twofactorModal = document.getElementById('twofactor-modal');
  const btnClose2faModal = document.getElementById('btn-close-2fa-modal');
  const twofactorStatusBox = document.getElementById('twofactor-status-box');
  const twofactorSetupView = document.getElementById('twofactor-setup-view');
  const twofactorActiveView = document.getElementById('twofactor-active-view');
  const twofactorSecretKey = document.getElementById('twofactor-secret-key');
  const twofactorVerifyCode = document.getElementById('twofactor-verify-code');
  const btnEnable2faConfirm = document.getElementById('btn-enable-2fa-confirm');
  const btnDisable2fa = document.getElementById('btn-disable-2fa');

  // DOM Elements - Add Profile Modal
  const addProfileModal = document.getElementById('add-profile-modal');
  const btnCloseProfileModal = document.getElementById('btn-close-profile-modal');
  const addProfileForm = document.getElementById('add-profile-form');
  const newProfileName = document.getElementById('new-profile-name');
  const newProfileAge = document.getElementById('new-profile-age');
  const newProfileVocab = document.getElementById('new-profile-vocab');
  const newProfileCards = document.getElementById('new-profile-cards');
  const newProfileNotes = document.getElementById('new-profile-notes');

  // DOM Elements - Voice Settings Modal
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

  // DOM Elements - Memory Modal
  const memoryModal = document.getElementById('memory-modal');
  const btnCloseModal = document.getElementById('btn-close-modal');
  const btnCloseModalBottom = document.getElementById('btn-close-modal-bottom');
  const memoryProfileSummary = document.getElementById('memory-profile-summary');
  const learnedVocabCloud = document.getElementById('learned-vocab-cloud');
  const symbolPrefList = document.getElementById('symbol-pref-list');

  // Application State
  let currentBoard = null;
  let currentPresets = [];
  let currentRecipients = [];
  let isGenerating = false;
  let isTraceExpanded = false;
  let isSpeakingAll = false;
  let systemVoices = [];

  // Authenticated User State (defaults to null until signed in or restored)
  let currentUser = null;

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
     IN-APP TOAST NOTIFICATION SYSTEM
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

  // Request Headers with Multi-Tenant Auth Token
  function getAuthHeaders(includeContentType = true) {
    const headers = {};
    if (includeContentType) {
      headers['Content-Type'] = 'application/json';
    }
    if (currentUser && currentUser.token) {
      headers['Authorization'] = `Bearer ${currentUser.token}`;
    }
    headers['X-Caregiver-ID'] = (currentUser && currentUser.user_id) ? currentUser.user_id : 'caregiver_primary';
    return headers;
  }

  // Initialize
  initApp();

  async function initApp() {
    restoreUserSession();
    initVoiceEngine();
    await reloadCaregiverWorkspace();
    setupEventListeners();
  }

  /* =========================================================================
     AUTHENTICATION & SESSION MANAGEMENT
     ========================================================================= */
  function restoreUserSession() {
    try {
      const savedUser = localStorage.getItem('communicare_user');
      const savedToken = localStorage.getItem('communicare_token');
      if (savedUser && savedToken) {
        currentUser = JSON.parse(savedUser);
        currentUser.token = savedToken;
      } else {
        currentUser = null;
      }
    } catch (e) {
      currentUser = null;
    }

    // Check for Google OAuth access_token in URL hash
    if (window.location.hash) {
      const hashParams = new URLSearchParams(window.location.hash.substring(1));
      const accessToken = hashParams.get('access_token');
      if (accessToken) {
        window.history.replaceState(null, '', window.location.pathname);
        window.handleGoogleCredentialResponse({ credential: accessToken });
        return;
      }
    }

    updateUserUI();

    // If not signed in or explicit login request, prompt Auth Modal immediately
    const urlParams = new URLSearchParams(window.location.search);
    if (!currentUser || !currentUser.token || urlParams.get('action') === 'login') {
      switchAuthTab('login');
      authModal.classList.remove('hidden');
    }
  }

  function updateUserUI() {
    const isLoggedIn = !!(currentUser && currentUser.token);

    if (btnHeaderSignin) {
      btnHeaderSignin.classList.toggle('hidden', isLoggedIn);
    }
    if (userProfileMenuContainer) {
      userProfileMenuContainer.classList.toggle('hidden', !isLoggedIn);
    }

    if (isLoggedIn) {
      const initials = (currentUser.full_name || 'U')
        .split(' ')
        .map(p => p[0])
        .join('')
        .substring(0, 2)
        .toUpperCase() || 'U';

      if (userAvatarInitials) userAvatarInitials.textContent = initials;
      if (userDisplayName) userDisplayName.textContent = (currentUser.full_name || 'Caregiver').split(' ')[0];
      if (dropdownUserName) dropdownUserName.textContent = currentUser.full_name;
      if (dropdownUserEmail) dropdownUserEmail.textContent = currentUser.email || '';

      if (dropdown2faBadge) {
        if (currentUser.totp_enabled) {
          dropdown2faBadge.textContent = 'Active (2FA)';
          dropdown2faBadge.className = 'badge-subtle badge-active';
        } else {
          dropdown2faBadge.textContent = 'Off';
          dropdown2faBadge.className = 'badge-subtle';
        }
      }

      if (dropdownAuthLabel) {
        dropdownAuthLabel.textContent = '🚪 Sign Out / Switch Account';
      }
    } else {
      if (dropdownAuthLabel) {
        dropdownAuthLabel.textContent = '🔑 Sign In / Register';
      }
    }
  }

  function setAuthAlert(msg, type = 'error') {
    if (!msg) {
      authAlert.classList.add('hidden');
      authAlert.innerHTML = '';
      return;
    }
    authAlert.className = `auth-alert-box alert-${type}`;
    authAlert.innerHTML = msg;
    authAlert.classList.remove('hidden');
  }

  function switchAuthTab(tab) {
    setAuthAlert('');
    tabAuthLogin.classList.toggle('active', tab === 'login');
    tabAuthRegister.classList.toggle('active', tab === 'register');
    tabAuthForgot.classList.toggle('active', tab === 'forgot');

    formAuthLogin.classList.toggle('hidden', tab !== 'login');
    formAuthRegister.classList.toggle('hidden', tab !== 'register');
    formAuthForgot.classList.toggle('hidden', tab !== 'forgot');

    if (tab === 'login') {
      authModalTitle.textContent = 'Sign In to CommuniCare';
      login2faField.classList.add('hidden');
      loginTotp.value = '';
    } else if (tab === 'register') {
      authModalTitle.textContent = 'Create Caregiver Account';
    } else if (tab === 'forgot') {
      authModalTitle.textContent = 'Reset Account Password';
      resetTokenGroup.classList.add('hidden');
      btnSubmitForgot.querySelector('span').textContent = 'Request Reset Token';
    }
  }

  /* =========================================================================
     VOICE & AUDIO ENGINE
     ========================================================================= */
  function initVoiceEngine() {
    if (!('speechSynthesis' in window)) return;

    const loadVoices = () => {
      systemVoices = window.speechSynthesis.getVoices();
      if (systemVoices.length > 0 && systemVoiceSelect) {
        systemVoiceSelect.innerHTML = '<option value="">Default System Voice</option>';
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
        console.warn('Speech error:', e);
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
     WORKSPACE & DATA LOADING (ISOLATED PER USER)
     ========================================================================= */
  async function reloadCaregiverWorkspace(selectedRecipientId = null) {
    await loadRecipients(selectedRecipientId);
    await loadPresets();
  }

  async function loadRecipients(selectedId = null) {
    try {
      const res = await fetch('/api/recipients', {
        headers: getAuthHeaders(false)
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
    try {
      const res = await fetch('/api/presets', {
        headers: getAuthHeaders(false)
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
    if (currentPresets.length === 0) {
      presetsContainer.innerHTML = '<span style="font-size:0.75rem; color:var(--color-stone-gray);">No presets saved yet.</span>';
      return;
    }

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
     EVENT LISTENERS & MODAL CONTROLS
     ========================================================================= */
  function setupEventListeners() {
    // User Profile Dropdown Toggle
    btnUserMenu.addEventListener('click', (e) => {
      e.stopPropagation();
      userDropdownMenu.classList.toggle('hidden');
    });

    document.addEventListener('click', (e) => {
      if (!userDropdownMenu.contains(e.target) && !btnUserMenu.contains(e.target)) {
        userDropdownMenu.classList.add('hidden');
      }
    });

    // Dropdown Item Actions
    dropdownBtn2fa.addEventListener('click', () => {
      userDropdownMenu.classList.add('hidden');
      open2faModal();
    });

    dropdownBtnMemory.addEventListener('click', () => {
      userDropdownMenu.classList.add('hidden');
      openMemoryModal();
    });

    dropdownBtnAddRecipient.addEventListener('click', () => {
      userDropdownMenu.classList.add('hidden');
      addProfileForm.reset();
      addProfileModal.classList.remove('hidden');
      newProfileName.focus();
    });

    if (btnHeaderSignin) {
      btnHeaderSignin.addEventListener('click', () => {
        switchAuthTab('login');
        authModal.classList.remove('hidden');
      });
    }

    dropdownBtnAuth.addEventListener('click', () => {
      userDropdownMenu.classList.add('hidden');
      if (currentUser && currentUser.token) {
        // Sign Out
        localStorage.removeItem('communicare_user');
        localStorage.removeItem('communicare_token');
        currentUser = null;
        updateUserUI();
        reloadCaregiverWorkspace();
        showToast('Signed Out', 'You have been signed out to guest mode.', 'info');
      } else {
        switchAuthTab('login');
        authModal.classList.remove('hidden');
      }
    });

    const GOOGLE_CLIENT_ID = "934093627046-o3dde5hvlkgl8qtmm1fdrjoiuvabkr8t.apps.googleusercontent.com";
    let googleTokenClient = null;

    // Google OAuth 2.0 Sign In Handlers
    window.handleGoogleCredentialResponse = async function(googleResponse) {
      if (!googleResponse || !googleResponse.credential) return;

      try {
        setAuthAlert('Connecting with Google...', 'info');
        const res = await fetch('/api/auth/google', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ credential: googleResponse.credential })
        });

        const data = await res.json();
        if (!res.ok || data.status === 'error') {
          setAuthAlert(data.detail || data.message || 'Google authentication failed.');
          return;
        }

        currentUser = {
          user_id: data.user_id,
          email: data.email,
          full_name: data.full_name,
          totp_enabled: data.totp_enabled,
          token: data.token
        };
        localStorage.setItem('communicare_user', JSON.stringify(currentUser));
        localStorage.setItem('communicare_token', data.token);

        updateUserUI();
        authModal.classList.add('hidden');
        await reloadCaregiverWorkspace();
        showToast('Google Sign-In Successful', `Welcome, ${data.full_name}!`, 'success');
      } catch (err) {
        setAuthAlert(`Google sign-in error: ${err.message}`);
      }
    };

    function triggerGoogleLoginFlow() {
      // 1. Try modern OAuth2 Token Client Popup (instant Google account popup)
      if (window.google && window.google.accounts && window.google.accounts.oauth2) {
        try {
          if (!googleTokenClient) {
            googleTokenClient = window.google.accounts.oauth2.initTokenClient({
              client_id: GOOGLE_CLIENT_ID,
              scope: "openid profile email",
              callback: async (tokenResponse) => {
                if (tokenResponse && tokenResponse.access_token) {
                  await window.handleGoogleCredentialResponse({ credential: tokenResponse.access_token });
                } else if (tokenResponse && tokenResponse.error) {
                  setAuthAlert(`Google login cancelled or error: ${tokenResponse.error}`);
                }
              }
            });
          }
          googleTokenClient.requestAccessToken({ prompt: 'select_account' });
          return;
        } catch (e) {
          console.warn("OAuth2 token client error:", e);
        }
      }

      // 2. Try GSI prompt fallback
      if (window.google && window.google.accounts && window.google.accounts.id) {
        try {
          window.google.accounts.id.prompt();
          return;
        } catch (e) {
          console.warn("GSI prompt fallback error:", e);
        }
      }

      // 3. Fallback: Direct OAuth2 redirect
      const redirectUri = window.location.origin + '/app';
      const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${GOOGLE_CLIENT_ID}&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=token&scope=openid%20profile%20email&prompt=select_account`;
      window.location.href = authUrl;
    }

    const btnCustomGoogleLogin = document.getElementById('btn-custom-google-login');
    if (btnCustomGoogleLogin) {
      btnCustomGoogleLogin.addEventListener('click', (e) => {
        e.preventDefault();
        triggerGoogleLoginFlow();
      });
    }

    // Auth Modal Navigation
    tabAuthLogin.addEventListener('click', () => switchAuthTab('login'));
    tabAuthRegister.addEventListener('click', () => switchAuthTab('register'));
    tabAuthForgot.addEventListener('click', () => switchAuthTab('forgot'));
    btnCloseAuthModal.addEventListener('click', () => authModal.classList.add('hidden'));
    
    const btnContinueGuest = document.getElementById('btn-continue-guest');
    if (btnContinueGuest) {
      btnContinueGuest.addEventListener('click', () => {
        authModal.classList.add('hidden');
        showToast('Guest Demo', 'Exploring CommuniCare in demo mode. Sign in anytime to save your workspace.', 'info', 4000);
      });
    }

    authModal.addEventListener('click', (e) => {
      if (e.target === authModal) authModal.classList.add('hidden');
    });

    // Auth: Sign In Submission
    formAuthLogin.addEventListener('submit', async (e) => {
      e.preventDefault();
      setAuthAlert('');
      const email = loginEmail.value.trim();
      const password = loginPassword.value;
      const totpCode = loginTotp.value.trim();

      try {
        const res = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: email,
            password: password,
            totp_code: totpCode || null
          })
        });

        const data = await res.json();
        if (!res.ok || data.status === 'error') {
          setAuthAlert(data.detail || data.message || 'Invalid email or password.');
          return;
        }

        if (data.status === '2fa_required') {
          login2faField.classList.remove('hidden');
          loginTotp.focus();
          setAuthAlert('🔐 Please enter the 6-digit code from Google Authenticator to continue.', 'info');
          return;
        }

        if (data.status === 'success') {
          currentUser = {
            user_id: data.user_id,
            email: data.email,
            full_name: data.full_name,
            totp_enabled: data.totp_enabled,
            token: data.token
          };
          localStorage.setItem('communicare_user', JSON.stringify(currentUser));
          localStorage.setItem('communicare_token', data.token);

          updateUserUI();
          authModal.classList.add('hidden');
          await reloadCaregiverWorkspace();
          showToast('Welcome Back!', `Signed in as ${data.full_name}`, 'success');
        }
      } catch (err) {
        setAuthAlert(`Sign in error: ${err.message}`);
      }
    });

    // Auth: Sign Up (Register) Submission
    formAuthRegister.addEventListener('submit', async (e) => {
      e.preventDefault();
      setAuthAlert('');
      const name = regFullname.value.trim();
      const email = regEmail.value.trim();
      const password = regPassword.value;

      try {
        const res = await fetch('/api/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            full_name: name,
            email: email,
            password: password
          })
        });

        const data = await res.json();
        if (!res.ok) {
          setAuthAlert(data.detail || 'Could not register account.');
          return;
        }

        currentUser = {
          user_id: data.user_id,
          email: data.email,
          full_name: data.full_name,
          totp_enabled: false,
          token: data.token
        };
        localStorage.setItem('communicare_user', JSON.stringify(currentUser));
        localStorage.setItem('communicare_token', data.token);

        updateUserUI();
        authModal.classList.add('hidden');
        await reloadCaregiverWorkspace();
        showToast('Account Created', `Welcome to CommuniCare, ${data.full_name}! Your isolated workspace is ready.`, 'success', 5000);
      } catch (err) {
        setAuthAlert(`Registration error: ${err.message}`);
      }
    });

    // Auth: Forgot Password Submission
    formAuthForgot.addEventListener('submit', async (e) => {
      e.preventDefault();
      setAuthAlert('');
      const email = forgotEmail.value.trim();
      const tokenVal = resetToken.value.trim();
      const newPass = resetNewPassword.value;

      if (resetTokenGroup.classList.contains('hidden')) {
        // Step 1: Request token
        try {
          const res = await fetch('/api/auth/forgot-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email })
          });
          const data = await res.json();
          resetTokenGroup.classList.remove('hidden');
          if (data.reset_token_preview) {
            resetToken.value = data.reset_token_preview;
          }
          btnSubmitForgot.querySelector('span').textContent = 'Set New Password';
          setAuthAlert(`Password reset token generated. Paste it below and choose a new password.`, 'info');
        } catch (err) {
          setAuthAlert(`Error: ${err.message}`);
        }
      } else {
        // Step 2: Set new password
        try {
          const res = await fetch('/api/auth/reset-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              email: email,
              reset_token: tokenVal,
              new_password: newPass
            })
          });
          const data = await res.json();
          if (!res.ok) {
            setAuthAlert(data.detail || 'Could not reset password.');
            return;
          }
          switchAuthTab('login');
          showToast('Password Reset', 'Password updated successfully. Please sign in.', 'success');
        } catch (err) {
          setAuthAlert(`Reset error: ${err.message}`);
        }
      }
    });

    // 2FA Security Modal Handlers
    btnClose2faModal.addEventListener('click', () => twofactorModal.classList.add('hidden'));
    twofactorModal.addEventListener('click', (e) => {
      if (e.target === twofactorModal) twofactorModal.classList.add('hidden');
    });

    btnEnable2faConfirm.addEventListener('click', async () => {
      const code = twofactorVerifyCode.value.trim();
      if (code.length !== 6) {
        showToast('Code Required', 'Please enter a valid 6-digit code from Google Authenticator.', 'warning');
        return;
      }

      try {
        const res = await fetch('/api/auth/2fa/enable', {
          method: 'POST',
          headers: getAuthHeaders(true),
          body: JSON.stringify({ totp_code: code })
        });
        const data = await res.json();
        if (!res.ok) {
          showToast('Invalid Code', data.detail || 'Invalid 6-digit code.', 'error');
          return;
        }

        currentUser.totp_enabled = true;
        localStorage.setItem('communicare_user', JSON.stringify(currentUser));
        updateUserUI();
        open2faModal();
        showToast('2FA Activated', 'Google Authenticator 2FA is now active on your account.', 'success');
      } catch (err) {
        showToast('2FA Error', err.message, 'error');
      }
    });

    btnDisable2fa.addEventListener('click', async () => {
      try {
        const res = await fetch('/api/auth/2fa/disable', {
          method: 'POST',
          headers: getAuthHeaders(false)
        });
        if (res.ok) {
          currentUser.totp_enabled = false;
          localStorage.setItem('communicare_user', JSON.stringify(currentUser));
          updateUserUI();
          open2faModal();
          showToast('2FA Disabled', 'Two-factor authentication has been disabled.', 'info');
        }
      } catch (err) {
        showToast('Error', err.message, 'error');
      }
    });

    // Studio & Board Event Listeners
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

    // Voice Modal
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
        showToast('Voice Settings Applied', 'Your speech persona preferences have been saved.', 'success');
      } catch (e) {}
      voiceModal.classList.add('hidden');
    });

    // Memory Inspector Modal
    btnCloseModal.addEventListener('click', () => memoryModal.classList.add('hidden'));
    btnCloseModalBottom.addEventListener('click', () => memoryModal.classList.add('hidden'));
    memoryModal.addEventListener('click', (e) => {
      if (e.target === memoryModal) memoryModal.classList.add('hidden');
    });

    // Add Profile Modal
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

      const recipientId = name.toLowerCase().replace(/[^a-z0-9]/g, '_') + '_' + Math.floor(Math.random() * 1000);
      const newProfile = {
        recipient_id: recipientId,
        caregiver_id: currentUser.user_id,
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
          headers: getAuthHeaders(true),
          body: JSON.stringify(newProfile)
        });
        if (res.ok) {
          addProfileModal.classList.add('hidden');
          await loadRecipients(recipientId);
          showToast('Profile Created', `Profile for "${name}" saved to your private workspace.`, 'success');
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
     2FA MODAL SETUP & FLOW
     ========================================================================= */
  async function open2faModal() {
    twofactorVerifyCode.value = '';
    twofactorModal.classList.remove('hidden');

    try {
      const meRes = await fetch('/api/auth/me', { headers: getAuthHeaders(false) });
      const meData = await meRes.json();
      currentUser.totp_enabled = meData.totp_enabled;

      if (meData.totp_enabled) {
        twofactorStatusBox.innerHTML = `<strong>Account Status:</strong> <span style="color:#065F46; font-weight:700;">Active (Protected with 2FA)</span>`;
        twofactorSetupView.classList.add('hidden');
        twofactorActiveView.classList.remove('hidden');
      } else {
        twofactorStatusBox.innerHTML = `<strong>Account Status:</strong> <span style="color:var(--color-stone-gray);">2FA is currently Disabled</span>`;
        twofactorActiveView.classList.add('hidden');
        twofactorSetupView.classList.remove('hidden');

        // Fetch setup secret
        const setupRes = await fetch('/api/auth/2fa/setup', {
          method: 'POST',
          headers: getAuthHeaders(false)
        });
        if (setupRes.ok) {
          const setupData = await setupRes.json();
          twofactorSecretKey.textContent = setupData.totp_secret;
        }
      }
    } catch (err) {
      showToast('Error', 'Could not retrieve 2FA status.', 'error');
    }
  }

  /* =========================================================================
     BOARD GENERATION & RENDERING
     ========================================================================= */
  async function handleGenerateBoard(customMessage = null, customRecipient = null) {
    const rawMessage = customMessage || caregiverMessageInput.value.trim();
    const recipientId = customRecipient || recipientSelect.value;
    const style = styleSelect.value;

    if (!rawMessage) {
      showToast('Message Required', 'Please enter a caregiver message or select a preset.', 'warning');
      caregiverMessageInput.focus();
      return;
    }

    if (!recipientId) {
      showToast('Recipient Required', 'Please select or add a recipient profile first.', 'warning');
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
        headers: getAuthHeaders(true),
        body: JSON.stringify({
          message: rawMessage,
          recipient_id: recipientId,
          caregiver_id: currentUser.user_id,
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
      btnGenerate.innerHTML = '<span>⚡ Generate Board</span>';
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
    try {
      const res = await fetch('/api/feedback', {
        method: 'POST',
        headers: getAuthHeaders(true),
        body: JSON.stringify({
          board_id: boardId,
          recipient_id: recipientId,
          caregiver_id: currentUser.user_id,
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
    if (!recipientId) return;

    try {
      const res = await fetch(`/api/recipients/${recipientId}`, {
        headers: getAuthHeaders(false)
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
     SMOOTH AUTOMATED ADAPTIVE DEMO
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
      headers: getAuthHeaders(true),
      body: JSON.stringify({
        board_id: currentBoard ? currentBoard.board_id : 'demo',
        recipient_id: recipientSelect.value,
        caregiver_id: currentUser.user_id,
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
