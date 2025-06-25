// Enhanced Chat Widget with Real API Integration
class BoliBazaarChat {
    constructor() {
        this.isOpen = false;
        this.sessionId = null;
        this.userId = null;
        this.authenticated = false;
        this.userInfo = null;
        this.init();
    }
    
    init() {
        this.chatToggle = document.getElementById('chat-toggle');
        this.chatContainer = document.getElementById('chat-container');
        this.chatClose = document.getElementById('chat-close');
        this.chatInput = document.getElementById('chat-input');
        this.chatSend = document.getElementById('chat-send');
        this.chatMessages = document.getElementById('chat-messages');
        
        this.bindEvents();
        this.sessionId = 'session_' + Math.random().toString(36).substr(2, 9);
    }
    
    bindEvents() {
        this.chatToggle.addEventListener('click', () => this.toggleChat());
        this.chatClose.addEventListener('click', () => this.closeChat());
        this.chatSend.addEventListener('click', () => this.sendMessage());
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
    }
    
    toggleChat() {
        this.isOpen = !this.isOpen;
        this.chatContainer.classList.toggle('active', this.isOpen);
        if (this.isOpen) {
            this.chatInput.focus();
        }
    }
    
    closeChat() {
        this.isOpen = false;
        this.chatContainer.classList.remove('active');
    }
    
    sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message) return;
        
        this.addMessage(message, 'user');
        this.chatInput.value = '';
        
        // Process message
        this.processMessage(message);
    }
    
    addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        messageDiv.innerHTML = `<div class="message-content">${content}</div>`;
        
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    async processMessage(message) {
        // Show typing indicator
        this.showTyping();
        
        // Process with real API calls
        setTimeout(async () => {
            this.hideTyping();
            await this.handleResponse(message);
        }, 1500);
    }
    
    async handleResponse(message) {
        const msgLower = message.toLowerCase();
        
        // Check for unique ID
        const idMatch = message.match(/\b\d{6}\b/);
        if (idMatch && !this.authenticated) {
            await this.verifyUser(idMatch[0]);
            return;
        }
        
        if (!this.authenticated) {
            this.addMessage('Please provide your 6-digit unique ID first. You can find it in your profile page.', 'bot');
            return;
        }
        
        // Handle authenticated requests
        if (msgLower.includes('active') || msgLower.includes('bid')) {
            await this.getActiveBids();
        } else if (msgLower.includes('place') || msgLower.includes('new bid')) {
            this.addMessage('I can help you place a new bid! Please tell me:\n\n1. Which auction ID\n2. Your bid amount\n\nExample: "Place $500 bid on auction 1"', 'bot');
        } else if (msgLower.includes('history')) {
            await this.getBidHistory();
        } else if (msgLower.includes('help')) {
            this.addMessage('I can help you with:\n\n🔍 Check Active Bids\n💰 Place New Bids\n📊 View Bid History\n⏰ Check Time Remaining\n🏆 Get Auction Details\n\nJust tell me what you\'d like to do!', 'bot');
        } else {
            // Check if user is trying to place a bid
            const bidMatch = message.match(/(\d+).*?(\d+)/g);
            if (bidMatch && (msgLower.includes('bid') || msgLower.includes('place'))) {
                await this.processBidRequest(message);
            } else {
                this.addMessage('I can help you with your bidding activities! Try asking:\n\n• "Show my active bids"\n• "Place a new bid"\n• "Check bid history"\n• "Help"\n\nWhat would you like to know?', 'bot');
            }
        }
    }
    
    async verifyUser(uniqueId) {
        try {
            const response = await fetch('/api/users/verify/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ user_id: uniqueId })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.userId = uniqueId;
                this.authenticated = true;
                this.userInfo = data.user;
                this.addMessage(`Welcome ${data.user.name}! (📧 ${data.user.username})\n\nI've verified your User ID: ${uniqueId}\n\nNow I can help you with:\n\n• Check your active bids\n• View auction details\n• Place new bids\n• Check bidding history\n• Get real-time auction updates\n\nWhat would you like to do?`, 'bot');
            } else {
                this.addMessage(`Sorry, I couldn't verify User ID: ${uniqueId}. Please check your unique ID in your profile page and try again.`, 'bot');
            }
        } catch (error) {
            this.addMessage('Sorry, there was an error verifying your ID. Please try again.', 'bot');
        }
    }
    
    async getActiveBids() {
        try {
            const response = await fetch(`/api/bids/active/?user_id=${this.userId}`);
            const data = await response.json();
            
            if (data.success && data.bids.length > 0) {
                let message = `Here are your active bids:\n\n`;
                
                data.bids.forEach(bid => {
                    const status = bid.is_winning ? '🏆 Winning' : '🔴 Outbid';
                    message += `${status} - ${bid.product_name}\n`;
                    message += `   Your Bid: $${bid.your_bid}\n`;
                    message += `   Current Highest: $${bid.current_highest}\n`;
                    message += `   Time Left: ${bid.time_remaining_formatted}\n\n`;
                });
                
                message += 'Would you like to place a higher bid on any auction?';
                this.addMessage(message, 'bot');
            } else {
                this.addMessage('You don\'t have any active bids right now. Would you like to browse available auctions?', 'bot');
            }
        } catch (error) {
            this.addMessage('Sorry, I couldn\'t fetch your active bids. Please try again.', 'bot');
        }
    }
    
    async getBidHistory() {
        try {
            const response = await fetch(`/api/bids/history/?user_id=${this.userId}&limit=5`);
            const data = await response.json();
            
            if (data.success && data.history.length > 0) {
                let message = `Your recent bidding history:\n\n`;
                
                data.history.forEach(bid => {
                    const date = new Date(bid.timestamp).toLocaleDateString();
                    const statusIcon = bid.status === 'Won' ? '🏆' : bid.status === 'Active' ? '🔵' : '🔴';
                    message += `${statusIcon} ${date} - ${bid.product_name}\n`;
                    message += `   Bid: $${bid.bid_amount} (${bid.status})\n\n`;
                });
                
                this.addMessage(message, 'bot');
            } else {
                this.addMessage('You haven\'t placed any bids yet. Would you like to start bidding?', 'bot');
            }
        } catch (error) {
            this.addMessage('Sorry, I couldn\'t fetch your bid history. Please try again.', 'bot');
        }
    }
    
    async processBidRequest(message) {
        // Extract auction ID and bid amount from message
        const numbers = message.match(/\d+/g);
        if (numbers && numbers.length >= 2) {
            const auctionId = numbers[0];
            const bidAmount = numbers[1];
            
            this.addMessage(`You want to place a bid of $${bidAmount} on auction ${auctionId}. Let me process this for you...`, 'bot');
            
            try {
                const response = await fetch('/api/bids/place/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify({
                        user_id: this.userId,
                        auction_id: auctionId,
                        bid_amount: parseFloat(bidAmount)
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    this.addMessage(`🎉 ${data.message}\n\nYour bid of $${bidAmount} is now the highest bid!`, 'bot');
                } else {
                    this.addMessage(`⚠️ ${data.error}`, 'bot');
                }
            } catch (error) {
                this.addMessage('Sorry, there was an error placing your bid. Please try again.', 'bot');
            }
        } else {
            this.addMessage('Please specify both auction ID and bid amount. Example: "Place $500 bid on auction 1"', 'bot');
        }
    }
    
    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }
    
    showTyping() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing';
        typingDiv.innerHTML = '<div class="message-content"><div class="typing-dots"><span></span><span></span><span></span></div></div>';
        typingDiv.id = 'typing-indicator';
        
        this.chatMessages.appendChild(typingDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    hideTyping() {
        const typing = document.getElementById('typing-indicator');
        if (typing) typing.remove();
    }
}

// Initialize chat when page loads
document.addEventListener('DOMContentLoaded', function() {
    new BoliBazaarChat();
});