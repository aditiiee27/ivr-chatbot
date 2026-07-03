// ==========================================================================
// STATE MANAGEMENT & DOM SELECTION
// ==========================================================================
const session_id = window.SESSION_ID;
let isVoiceEnabled = true;
let currentLang = 'hi'; // Default to Hindi based on screenshot
let recognition = null;
let isRecording = false;

// DOM Elements
const chatWindow = document.getElementById('chat-window');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const typingIndicator = document.getElementById('typing-indicator');
const audioPlayer = document.getElementById('tts-audio-player');
const toggleVoiceBtn = document.getElementById('toggle-voice-btn');
const sessionIdDisplay = document.getElementById('session-id-display');

// Form elements
const customerForm = document.getElementById('customer-form');
const custNameInput = document.getElementById('cust-name');
const custEmailInput = document.getElementById('cust-email');
const custPhoneInput = document.getElementById('cust-phone');
const customerStatus = document.getElementById('customer-status');
const saveCustomerBtn = document.getElementById('save-customer-btn');

const feedbackForm = document.getElementById('feedback-form');
const feedbackComments = document.getElementById('feedback-comments');
const feedbackStatus = document.getElementById('feedback-status');
const submitFeedbackBtn = document.getElementById('submit-feedback-btn');

// Diagnostics elements
const refreshDbBtn = document.getElementById('refresh-db-btn');
const tabButtons = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

// ==========================================================================
// INITIALIZATION
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
    // Show current Session ID
    sessionIdDisplay.textContent = session_id;
    
    // Initial fetch of DB diagnostics
    queryDatabaseDiagnostics();
    
    // Automatically focus on chat input
    chatInput.focus();

    // Initialize Web Speech API for voice inputs
    initSpeechRecognition();
    
    // Play the welcome voice on interaction
    const playWelcomeOnInteraction = () => {
        if (isVoiceEnabled) {
            playSpeech('/static/audio/welcome_hi.mp3');
        }
        document.removeEventListener('click', playWelcomeOnInteraction);
        document.removeEventListener('keydown', playWelcomeOnInteraction);
    };
    document.addEventListener('click', playWelcomeOnInteraction);
    document.addEventListener('keydown', playWelcomeOnInteraction);
});

// ==========================================================================
// WIDGET FLOATING OVERLAY TOGGLES
// ==========================================================================
window.openChatWidget = function() {
    const widget = document.getElementById('chat-widget');
    const trigger = document.getElementById('chat-trigger');
    
    widget.classList.remove('hidden');
    trigger.style.display = 'none';
    chatInput.focus();
};

window.closeChatWidget = function() {
    const widget = document.getElementById('chat-widget');
    const trigger = document.getElementById('chat-trigger');
    
    widget.classList.add('hidden');
    trigger.style.display = 'flex';
};

window.toggleConsoleSidebar = function() {
    const splitContainer = document.querySelector('.main-split-container');
    splitContainer.classList.toggle('console-collapsed');
};

// ==========================================================================
// SPEECH TO TEXT (STT) INPUT LOGIC
// ==========================================================================
function initSpeechRecognition() {
    window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (window.SpeechRecognition) {
        recognition = new window.SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        
        recognition.onstart = () => {
            isRecording = true;
            const micBtn = document.getElementById('voice-input-btn');
            micBtn.classList.add('listening');
            chatInput.placeholder = (currentLang === 'hi') ? "सुन रहे हैं... बोलें" : "Listening... Speak";
        };
        
        recognition.onend = () => {
            isRecording = false;
            const micBtn = document.getElementById('voice-input-btn');
            micBtn.classList.remove('listening');
            chatInput.placeholder = (currentLang === 'hi') ? "अपना जवाब लिखें या बोलें..." : "Type or speak your answer...";
        };
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            chatInput.value = transcript;
            // auto-submit form
            chatForm.dispatchEvent(new Event('submit'));
        };
        
        recognition.onerror = (event) => {
            console.error("Speech Recognition Error:", event.error);
            isRecording = false;
            const micBtn = document.getElementById('voice-input-btn');
            micBtn.classList.remove('listening');
            chatInput.placeholder = (currentLang === 'hi') ? "अपना जवाब लिखें या बोलें..." : "Type or speak your answer...";
            
            // Helpful user guidelines based on error code
            if (event.error === 'not-allowed') {
                alert("माइक्रोफ़ोन उपयोग करने की अनुमति नहीं है। कृपया अपने ब्राउज़र की सेटिंग में माइक्रोफ़ोन की अनुमति (Permission) दें।\n\nMicrophone permission was denied. Please allow microphone access in your browser settings to use voice features.");
            } else if (event.error === 'no-speech') {
                alert("कोई आवाज़ नहीं सुनी गई। कृपया माइक्रोफ़ोन के पास थोड़ा तेज़ बोलें।\n\nNo speech was detected. Please speak closer to the microphone.");
            } else if (event.error === 'network') {
                alert("नेटवर्क त्रुटि: ब्राउज़र वॉयस इनपुट के लिए इंटरनेट कनेक्शन आवश्यक है।\n\nNetwork error: Internet connection is required for browser speech transcription.");
            } else {
                alert("वॉयस इनपुट त्रुटि (Voice Input Error): " + event.error);
            }
        };
    } else {
        console.log("Speech recognition not supported in this browser.");
    }
}

window.toggleVoiceInput = function() {
    if (!recognition) {
        alert("आपका ब्राउज़र वॉयस इनपुट का समर्थन नहीं करता है। कृपया बेहतर अनुभव के लिए Google Chrome या Microsoft Edge का उपयोग करें।\n\nYour browser does not support Speech Recognition. Please use Google Chrome or Microsoft Edge for voice input.");
        return;
    }
    if (isRecording) {
        recognition.stop();
    } else {
        // Set recognition language dynamically based on active language
        recognition.lang = (currentLang === 'hi') ? 'hi-IN' : 'en-IN';
        try {
            recognition.start();
        } catch (e) {
            console.error("Failed to start speech recognition:", e);
        }
    }
};


// ==========================================================================
// VOICE RESPONSE & AUDIO PLAYER LOGIC
// ==========================================================================
toggleVoiceBtn.addEventListener('click', () => {
    isVoiceEnabled = !isVoiceEnabled;
    if (isVoiceEnabled) {
        toggleVoiceBtn.classList.add('active');
    } else {
        toggleVoiceBtn.classList.remove('active');
        audioPlayer.pause();
    }
});

// Play audio using HTML5 audio player
function playSpeech(audioUrl) {
    if (!audioUrl) return;
    
    audioPlayer.src = audioUrl;
    audioPlayer.load();
    
    audioPlayer.play()
        .then(() => {
            // Can activate visuals if needed
        })
        .catch(err => {
            console.log("Audio autoplay prevented or missing.", err);
        });
}

// Global function to allow replay button trigger
window.replayAudio = function(audioUrl) {
    playSpeech(audioUrl);
};

window.resetChat = function() {
    if (confirm("Reset current session and clear messages? / क्या आप सत्र को रीसेट करना चाहते हैं?")) {
        window.location.href = '/';
    }
};

// ==========================================================================
// QUICK ACTIONS INTERACTIVE GRID
// ==========================================================================
window.triggerQuickAction = function(action) {
    // Hide welcome screen
    const welcomeScreen = document.getElementById('welcome-screen');
    if (welcomeScreen) welcomeScreen.style.display = 'none';
    
    let queryText = "";
    if (action === 'register') {
        queryText = "शिकायत दर्ज करें";
    } else if (action === 'track') {
        queryText = "शिकायत की स्थिति जांचें";
    } else if (action === 'feedback') {
        // Expand console sidebar if collapsed
        const splitContainer = document.querySelector('.main-split-container');
        splitContainer.classList.remove('console-collapsed');
        
        const feedbackCard = document.getElementById('feedback-section-card');
        if (feedbackCard) {
            feedbackCard.scrollIntoView({ behavior: 'smooth' });
            feedbackCard.style.boxShadow = "0 0 15px rgba(255, 171, 0, 0.4)";
            setTimeout(() => { feedbackCard.style.boxShadow = ""; }, 2500);
        }
        return;
    } else if (action === 'support') {
        queryText = "हेल्पलाइन नंबर क्या है?";
    } else if (action === 'faq') {
        queryText = "अक्सर पूछे जाने वाले प्रश्न";
    } else if (action === 'services') {
        queryText = "कौन सी सेवाएं उपलब्ध हैं?";
    }
    
    if (queryText) {
        chatInput.value = queryText;
        chatForm.dispatchEvent(new Event('submit'));
    }
};

// ==========================================================================
// FORMS SUBMISSION LOGIC (AJAX POSTs)
// ==========================================================================

// 1. Link Citizen Profile
customerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const customerData = {
        name: custNameInput.value.trim(),
        email: custEmailInput.value.trim(),
        phone: custPhoneInput.value.trim()
    };
    
    saveCustomerBtn.disabled = true;
    saveCustomerBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Linking...';
    
    try {
        const response = await fetch('/api/customer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(customerData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Success: lock fields
            custNameInput.disabled = true;
            custEmailInput.disabled = true;
            custPhoneInput.disabled = true;
            
            customerStatus.classList.remove('hidden');
            customerStatus.classList.remove('error');
            customerStatus.innerHTML = `<i class="fa-solid fa-circle-check"></i> Connected Profile Row!`;
            
            saveCustomerBtn.classList.add('hidden');
            queryDatabaseDiagnostics();
        } else {
            throw new Error(data.error || 'Failed to link record.');
        }
    } catch (err) {
        console.error(err);
        saveCustomerBtn.disabled = false;
        saveCustomerBtn.innerHTML = 'प्रोफ़ाइल लिंक करें';
        
        customerStatus.classList.remove('hidden');
        customerStatus.classList.add('error');
        customerStatus.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> Error: ${err.message}`;
    }
});

// 2. Submit Session Feedback
feedbackForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const ratingInput = document.querySelector('input[name="rating"]:checked');
    if (!ratingInput) return;
    
    const rating = ratingInput.value;
    const comments = feedbackComments.value.trim();
    
    submitFeedbackBtn.disabled = true;
    submitFeedbackBtn.textContent = 'Submitting...';
    
    try {
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: session_id,
                rating: rating,
                comments: comments
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            feedbackForm.classList.add('hidden');
            feedbackStatus.classList.remove('hidden');
            queryDatabaseDiagnostics();
        } else {
            throw new Error(data.error);
        }
    } catch (err) {
        console.error(err);
        submitFeedbackBtn.disabled = false;
        submitFeedbackBtn.textContent = 'Submit Review';
        alert(`Failed to save feedback: ${err.message}`);
    }
});

// ==========================================================================
// CHAT BOT CORE FLOW
// ==========================================================================
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const messageText = chatInput.value.trim();
    if (!messageText) return;
    
    // Clear input & refocus
    chatInput.value = '';
    chatInput.focus();
    
    // Hide welcome screen if visible
    const welcomeScreen = document.getElementById('welcome-screen');
    if (welcomeScreen && welcomeScreen.style.display !== 'none') {
        welcomeScreen.style.display = 'none';
    }
    
    // Append User Message to Window
    appendMessage('user', messageText);
    
    // Show Typing Indicator
    typingIndicator.classList.remove('hidden');
    scrollChatToBottom();
    
    try {
        // Post message to Flask API with current language
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: session_id,
                message: messageText,
                lang: currentLang
            })
        });
        
        const data = await response.json();
        
        // Hide typing indicator
        typingIndicator.classList.add('hidden');
        
        if (response.ok) {
            // Append assistant text response
            appendMessage('assistant', data.response, data.audio_file);
            
            // Speak response if enabled
            if (isVoiceEnabled && data.audio_file) {
                playSpeech(data.audio_file);
            }
            
            queryDatabaseDiagnostics();
        } else {
            throw new Error(data.error || 'Server error.');
        }
    } catch (err) {
        console.error(err);
        typingIndicator.classList.add('hidden');
        const errText = "क्षमा करें, मुझे विभाग सर्वर से कनेक्ट करने में समस्या हो रही है। कृपया पुनः प्रयास करें!";
        appendMessage('assistant', errText);
    }
});

// Helper: Append bubbles
function appendMessage(role, text, audioUrl = null) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}-msg animate-fade-in`;
    
    const timeString = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const senderName = role === 'user' ? 'आप' : 'नीर सहायक';
    
    let replayBtnHtml = '';
    if (role === 'assistant' && audioUrl) {
        replayBtnHtml = `
            <button class="replay-btn" onclick="replayAudio('${audioUrl}')" title="Replay voice">
                <i class="fa-solid fa-circle-play"></i>
            </button>
        `;
    }
    
    msgDiv.innerHTML = `
        <div class="msg-bubble">
            ${text}
            ${replayBtnHtml}
        </div>
        <span class="msg-meta">${senderName} • ${timeString}</span>
    `;
    
    chatWindow.appendChild(msgDiv);
    scrollChatToBottom();
}

function scrollChatToBottom() {
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// ==========================================================================
// DEVELOPER DIAGNOSTICS & TAB LOGIC
// ==========================================================================

// Tab Switching Listener
tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        tabButtons.forEach(tb => tb.classList.remove('active'));
        tabContents.forEach(tc => tc.classList.remove('active'));
        
        btn.classList.add('active');
        const targetTabId = btn.getAttribute('data-tab');
        document.getElementById(targetTabId).classList.add('active');
    });
});

refreshDbBtn.addEventListener('click', () => {
    refreshDbBtn.innerHTML = '<i class="fa-solid fa-arrows-rotate fa-spin"></i> Querying...';
    queryDatabaseDiagnostics();
});

// Fetch SQLite rows from debug API
async function queryDatabaseDiagnostics() {
    try {
        const response = await fetch('/api/debug_db');
        const data = await response.json();
        
        if (!response.ok) throw new Error(data.error);
        
        // 1. Render Chat History DB content
        const dbChatTab = document.getElementById('db-chat');
        if (data.chats && data.chats.length > 0) {
            dbChatTab.innerHTML = data.chats.map(row => `
                <div class="db-row">
                    <div class="db-row-meta">ID: ${row.id} | Role: ${row.role}</div>
                    <div style="color: #FFF;">"${row.content}"</div>
                    ${row.audio_file ? `<div style="font-size: 0.65rem; color: #94A3B8;"><i class="fa-solid fa-volume-low"></i> Audio: ${row.audio_file}</div>` : ''}
                    <div style="font-size: 0.6rem; color: #475569;">${row.created_at}</div>
                </div>
            `).join('');
        } else {
            dbChatTab.innerHTML = '<div class="placeholder-text">chat_history table is empty.</div>';
        }
        
        // 2. Render Customers DB content
        const dbCustTab = document.getElementById('db-customers');
        if (data.customers && data.customers.length > 0) {
            dbCustTab.innerHTML = data.customers.map(row => `
                <div class="db-row">
                    <div class="db-row-meta">ID: ${row.id} | Name: ${row.name}</div>
                    <div>Email: ${row.email}</div>
                    <div>Phone: ${row.phone}</div>
                    <div style="font-size: 0.6rem; color: #475569;">${row.created_at}</div>
                </div>
            `).join('');
        } else {
            dbCustTab.innerHTML = '<div class="placeholder-text">customers table is empty.</div>';
        }
        
        // 3. Render Feedback DB content
        const dbFeedbackTab = document.getElementById('db-feedback');
        if (data.feedback && data.feedback.length > 0) {
            dbFeedbackTab.innerHTML = data.feedback.map(row => `
                <div class="db-row">
                    <div class="db-row-meta">ID: ${row.id} | Rating: ${row.rating}/5 stars</div>
                    <div style="color: #FFF;">"${row.comments}"</div>
                    <div style="font-size: 0.6rem; color: #475569;">${row.created_at}</div>
                </div>
            `).join('');
        } else {
            dbFeedbackTab.innerHTML = '<div class="placeholder-text">feedback table is empty.</div>';
        }
        
    } catch (err) {
        console.error("Diagnostic Fetch Error:", err);
        const placeholders = document.querySelectorAll('.tab-content');
        placeholders.forEach(el => {
            el.innerHTML = `<div class="placeholder-text" style="color: var(--error);">Error retrieving database: ${err.message}</div>`;
        });
    } finally {
        refreshDbBtn.innerHTML = '<i class="fa-solid fa-arrows-rotate"></i> Query SQLite Rows';
    }
}
