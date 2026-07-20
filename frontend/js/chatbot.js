document.addEventListener('DOMContentLoaded', () => {
  // Chatbot Elements
  const chatWidget = document.getElementById('chatbot-widget');
  const chatTrigger = document.getElementById('chat-trigger');
  const chatWindow = document.getElementById('chat-window');
  const chatClose = document.getElementById('chat-close');
  const chatHistory = document.getElementById('chat-history');
  const chatInput = document.getElementById('chat-input');
  const chatSendBtn = document.getElementById('chat-send-btn');
  const typingIndicator = document.getElementById('typing-indicator');

  if (!chatWidget || !chatTrigger || !chatWindow || !chatHistory || !chatInput || !chatSendBtn) {
    return;
  }

  // Initial Welcoming Message
  const initBotGreeting = () => {
    if (chatHistory.children.length <= 1) { // includes typing indicator element
      appendMessage('bot', "Hi! I am your Google News AI Assistant. Ask me anything about Google's latest AI updates, Pixel releases, Cloud news, or Android 15 features!");
    }
  };

  // Toggle Chat Window
  chatTrigger.addEventListener('click', () => {
    const isVisible = chatWindow.style.display === 'flex';
    if (isVisible) {
      chatWindow.style.display = 'none';
    } else {
      chatWindow.style.display = 'flex';
      initBotGreeting();
      chatInput.focus();
    }
  });

  if (chatClose) {
    chatClose.addEventListener('click', () => {
      chatWindow.style.display = 'none';
    });
  }

  // Send Message Actions
  chatSendBtn.addEventListener('click', () => {
    handleUserSendMessage();
  });

  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleUserSendMessage();
    }
  });

  // Handle Send Message
  async function handleUserSendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    // 1. Clear input & Append user message
    chatInput.value = '';
    appendMessage('user', text);

    // 2. Show typing indicator
    showTypingIndicator();

    try {
      // 3. Request bot response from FastAPI backend
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: text })
      });

      if (!response.ok) throw new Error('API server error');
      
      const data = await response.json();
      
      // 4. Hide typing indicator & append bot message
      hideTypingIndicator();
      appendMessage('bot', data.response);

    } catch (error) {
      console.error(error);
      hideTypingIndicator();
      appendMessage('bot', "Sorry, I'm having trouble connecting to my brain right now. Please try again in a moment.");
    }
  }

  // Helper: Append Message Bubble to UI
  function appendMessage(sender, text) {
    const bubble = document.createElement('div');
    bubble.classList.add('chat-bubble', sender);
    bubble.textContent = text;
    
    // Insert before typing indicator to maintain it at the very bottom
    chatHistory.insertBefore(bubble, typingIndicator);
    scrollToBottom();
  }

  // Helper: Show/Hide Typing Indicator
  function showTypingIndicator() {
    typingIndicator.style.display = 'flex';
    scrollToBottom();
  }

  function hideTypingIndicator() {
    typingIndicator.style.display = 'none';
  }

  // Helper: Scroll Chat History to Bottom
  function scrollToBottom() {
    chatHistory.scrollTop = chatHistory.scrollHeight;
  }
});
