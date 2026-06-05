document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');

    // Configure marked for Markdown parsing
    if (typeof marked !== 'undefined') {
        marked.setOptions({
            breaks: true,
            gfm: true
        });
    }

    function scrollToBottom() {
        chatBox.scrollTo({
            top: chatBox.scrollHeight,
            behavior: 'smooth'
        });
    }

    function addUserMessage(message) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message user-message';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = message;
        
        msgDiv.appendChild(contentDiv);
        chatBox.appendChild(msgDiv);
        scrollToBottom();
    }

    function addBotMessage(message, isHTML = false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message bot-message';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        if (isHTML && typeof marked !== 'undefined') {
            contentDiv.innerHTML = marked.parse(message);
        } else {
            contentDiv.textContent = message;
        }
        
        msgDiv.appendChild(contentDiv);
        chatBox.appendChild(msgDiv);
        scrollToBottom();
    }

    function addTypingIndicator() {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message bot-message typing';
        msgDiv.id = 'typing-indicator';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.className = 'typing-dot';
            typingDiv.appendChild(dot);
        }
        
        contentDiv.appendChild(typingDiv);
        msgDiv.appendChild(contentDiv);
        chatBox.appendChild(msgDiv);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    const clearBtn = document.getElementById('clear-btn');
    const exportBtn = document.getElementById('export-btn');

    async function loadHistory() {
        try {
            const response = await fetch('/api/history');
            if (response.ok) {
                const history = await response.json();
                if (history && history.length > 0) {
                    history.forEach(pair => {
                        if (pair.user) {
                            addUserMessage(pair.user);
                        }
                        if (pair.assistant) {
                            addBotMessage(pair.assistant, true);
                        }
                    });
                }
            }
        } catch (error) {
            console.error('Error loading history:', error);
        }
    }

    // Load history on startup
    loadHistory();

    if (exportBtn) {
        exportBtn.addEventListener('click', () => {
            window.location.href = '/api/export';
        });
    }

    if (clearBtn) {
        clearBtn.addEventListener('click', async () => {
            if (confirm('Are you sure you want to clear your chat history?')) {
                try {
                    const response = await fetch('/api/history/clear', {
                        method: 'POST'
                    });
                    if (response.ok) {
                        chatBox.innerHTML = `
                            <div class="message bot-message">
                                <div class="message-content">
                                    <p>Hello! I am GeminiLive, your AI assistant. How can I help you today?</p>
                                </div>
                            </div>
                        `;
                    } else {
                        alert('Failed to clear chat history on the server.');
                    }
                } catch (error) {
                    console.error('Error clearing history:', error);
                    alert('Error connecting to server to clear history.');
                }
            }
        });
    }

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const message = userInput.value.trim();
        if (!message) return;
        
        addUserMessage(message);
        userInput.value = '';
        
        addTypingIndicator();
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            removeTypingIndicator();
            
            if (response.ok) {
                addBotMessage(data.response, true);
            } else {
                addBotMessage('Sorry, I encountered an error: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error:', error);
            removeTypingIndicator();
            addBotMessage('Sorry, I could not connect to the server. Please try again later.');
        }
    });
});
