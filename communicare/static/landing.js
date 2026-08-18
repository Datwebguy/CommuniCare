/**
 * CommuniCare Landing Page Controller
 * Interactive suite tabs, live sandbox generation, and speech synthesis.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Suite Tabs Interactive Switcher
  const suiteTabs = document.querySelectorAll('.suite-tab-btn');
  const suiteContainer = document.querySelector('.suite-cards-grid');

  const SUITE_DATA = {
    memory: [
      {
        icon: '🧠',
        bg: '#EFF6FF',
        color: '#2563EB',
        name: 'Firestore Recipient State',
        body: 'Fetches individualized vocabulary constraints, age bracket, visual contrast needs, and learned preferences before reasoning begins.',
        linkText: 'View Memory Model'
      },
      {
        icon: '📊',
        bg: '#FEFCE8',
        color: '#854D0E',
        name: 'Per-User Vocab Tracking',
        body: 'Tracks historical success frequencies and reinforced vocabulary terms to prioritize familiar core words on subsequent boards.',
        linkText: 'Explore Personalization'
      },
      {
        icon: '🔒',
        bg: '#FDF2F8',
        color: '#9D174D',
        name: 'Custom Symbol Overrides',
        body: 'Persists caregiver-approved symbol mappings (e.g. customized icon for "medicine" or "quiet room") for consistent visual cues.',
        linkText: 'Symbol Mappings'
      }
    ],
    gemini: [
      {
        icon: '⚡',
        bg: '#F5F3FF',
        color: '#7C3AED',
        name: 'Gemini 2.5 Flash Reasoning',
        body: 'Deconstructs unstructured caregiver speech into core AAC communication concepts, identifying primary intent and step-by-step actions.',
        linkText: 'Test Plain Language'
      },
      {
        icon: '🎯',
        bg: '#EFF6FF',
        color: '#1D4ED8',
        name: 'Intent Classification',
        body: 'Accurately tags conversational intent (medical, hygiene, food, transition, comfort) to set appropriate context badges.',
        linkText: 'Intent Models'
      },
      {
        icon: '🧩',
        bg: '#ECFDF5',
        color: '#065F46',
        name: 'Vocabulary Pruning',
        body: 'Filters abstract adjectives and complex conjunctions, keeping only essential visual concepts tailored to the recipient capacity.',
        linkText: 'AAC Principles'
      }
    ],
    symbols: [
      {
        icon: '🎨',
        bg: '#ECFDF5',
        color: '#10B981',
        name: 'Dynamic ARASAAC Resolver',
        body: 'Queries the open ARASAAC pictogram catalog and vector illustration engine, applying clinical Fitzgerald Key color codes.',
        linkText: 'Browse ARASAAC'
      },
      {
        icon: '✨',
        bg: '#FFF7ED',
        color: '#EA580C',
        name: 'Curated High-Contrast Vectors',
        body: 'High-visibility hand-crafted SVG pictograms designed specifically for cognitive clarity and rapid recognition.',
        linkText: 'Vector Library'
      },
      {
        icon: '🛡️',
        bg: '#F8FAFC',
        color: '#475569',
        name: 'Accessible Text Fallback',
        body: 'Graceful fallback generating clear typographic cards for specialized or unrecognized vocabulary without pipeline errors.',
        linkText: 'Fallback System'
      }
    ],
    assembly: [
      {
        icon: '📐',
        bg: '#FEFCE8',
        color: '#CA8A04',
        name: 'Fitzgerald Key Standard',
        body: 'Orders cards logically by clinical syntax: Yellow (People), Green (Verbs), Orange (Nouns), Blue (Adjectives), Pink (Social).',
        linkText: 'Color Grammar'
      },
      {
        icon: '📱',
        bg: '#EFF6FF',
        color: '#2563EB',
        name: 'Balanced 3×2 Grid Canvas',
        body: 'Responsive layout engineered for clear physical printouts or touchscreen communication on iPad and tablet devices.',
        linkText: 'Board Layout'
      },
      {
        icon: '🔊',
        bg: '#F5F3FF',
        color: '#7C3AED',
        name: 'Multi-Modal Speech TTS',
        body: 'Integrated Web Speech audio enabling recipients to tap any symbol to vocalize their words aloud.',
        linkText: 'Speech Engine'
      }
    ],
    learning: [
      {
        icon: '🔄',
        bg: '#FDF2F8',
        color: '#DB2777',
        name: 'Caregiver Feedback Loop',
        body: 'One-click "Worked Well" reinforcements update Firestore state immediately, boosting confidence scores for future interactions.',
        linkText: 'Feedback Loop'
      },
      {
        icon: '📈',
        bg: '#ECFDF5',
        color: '#059669',
        name: 'Autonomous Adaptation',
        body: 'Multi-turn memory automatically selects reinforced visual symbols and tailors simplified language based on past usage.',
        linkText: '2-Turn Adaptive Demo'
      },
      {
        icon: '🗄️',
        bg: '#EFF6FF',
        color: '#1E40AF',
        name: 'Zero-Config Dual Persistence',
        body: 'Seamlessly runs on Google Cloud Firestore in production or transparent local JSON persistence in local testing.',
        linkText: 'Cloud Architecture'
      }
    ]
  };

  suiteTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      suiteTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      const tabKey = tab.getAttribute('data-tab');
      renderSuiteCards(tabKey);
    });
  });

  function renderSuiteCards(tabKey) {
    const cards = SUITE_DATA[tabKey] || SUITE_DATA.memory;
    suiteContainer.innerHTML = cards.map(c => `
      <div class="suite-product-card">
        <div>
          <div class="suite-card-icon" style="background:${c.bg}; color:${c.color};">${c.icon}</div>
          <h3 class="suite-card-name">${c.name}</h3>
          <p class="suite-card-body">${c.body}</p>
        </div>
        <a href="/app" class="link-violet">${c.linkText} &rarr;</a>
      </div>
    `).join('');
  }

  // Interactive Live Sandbox Generator
  const btnLandingGenerate = document.getElementById('btn-landing-generate');
  const landingMessageInput = document.getElementById('landing-message-input');
  const landingBoardCards = document.getElementById('landing-board-cards');

  if (btnLandingGenerate && landingMessageInput) {
    btnLandingGenerate.addEventListener('click', async () => {
      const msg = landingMessageInput.value.trim();
      if (!msg) return;

      btnLandingGenerate.disabled = true;
      btnLandingGenerate.innerHTML = '<span>⚡ Processing...</span>';

      try {
        const res = await fetch('/api/generate-board', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: msg,
            recipient_id: 'leo_care',
            simplify_style: 'core_words'
          })
        });

        if (res.ok) {
          const data = await res.json();
          renderSandboxCards(data.cards);
        }
      } catch (e) {
        console.error('Landing sandbox error:', e);
      } finally {
        btnLandingGenerate.disabled = false;
        btnLandingGenerate.innerHTML = '<span>⚡ Generate Board</span>';
      }
    });
  }

  function renderSandboxCards(cards) {
    if (!cards || cards.length === 0) return;
    landingBoardCards.innerHTML = cards.map(card => {
      const visual = card.svg_icon 
        ? card.svg_icon 
        : (card.image_url 
            ? `<img src="${card.image_url}" alt="${card.word}" style="width:48px; height:48px; object-fit:contain;" />`
            : `<div style="font-size:1.8rem;">📝</div>`);

      return `
        <div class="mini-aac-card" style="--card-border:${card.color_code};" onclick="window.speakText('${card.word}')" title="Click to speak '${card.word}'">
          <div class="mini-card-icon">${visual}</div>
          <span class="mini-card-label">${card.word}</span>
          <span style="font-size:11px; color:${card.color_code}; font-weight:700;">${card.category.toUpperCase()}</span>
        </div>
      `;
    }).join('');
  }

  // Web Speech synthesis helper
  window.speakText = function(text) {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  };
});
