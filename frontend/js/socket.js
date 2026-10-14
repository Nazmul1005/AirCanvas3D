/**
 * WebSocket client with automatic reconnection.
 */

export class SocketClient {
    constructor(url, onMessage, onStatusChange) {
        this.url = url;
        this.onMessage = onMessage;
        this.onStatusChange = onStatusChange;
        
        this.socket = null;
        this.reconnectInterval = 2000;
        this.reconnectTimer = null;
        this.isIntentionallyClosed = false;
        this.status = 'disconnected';
    }
    
    /**
     * Connect to the WebSocket server.
     */
    connect() {
        this.isIntentionallyClosed = false;
        this.updateStatus('connecting');
        
        try {
            this.socket = new WebSocket(this.url);
            
            this.socket.onopen = () => {
                console.log('WebSocket connected');
                this.updateStatus('connected');
                
                // Clear any pending reconnect
                if (this.reconnectTimer) {
                    clearTimeout(this.reconnectTimer);
                    this.reconnectTimer = null;
                }
            };
            
            this.socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.onMessage(data);
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };
            
            this.socket.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
            this.socket.onclose = () => {
                console.log('WebSocket disconnected');
                this.socket = null;
                
                if (!this.isIntentionallyClosed) {
                    this.updateStatus('disconnected');
                    this.scheduleReconnect();
                }
            };
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            this.updateStatus('disconnected');
            this.scheduleReconnect();
        }
    }
    
    /**
     * Schedule a reconnection attempt.
     */
    scheduleReconnect() {
        if (this.reconnectTimer) {
            return;
        }
        
        console.log(`Reconnecting in ${this.reconnectInterval}ms...`);
        this.reconnectTimer = setTimeout(() => {
            this.reconnectTimer = null;
            this.connect();
        }, this.reconnectInterval);
    }
    
    /**
     * Update connection status.
     * @param {string} status - 'connected', 'connecting', or 'disconnected'
     */
    updateStatus(status) {
        if (this.status !== status) {
            this.status = status;
            this.onStatusChange(status);
        }
    }
    
    /**
     * Send a message to the server.
     * @param {Object} data - Data to send
     */
    send(data) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(data));
        }
    }
    
    /**
     * Disconnect from the server.
     */
    disconnect() {
        this.isIntentionallyClosed = true;
        
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
        
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
        
        this.updateStatus('disconnected');
    }
    
    /**
     * Get current connection status.
     * @returns {string}
     */
    getStatus() {
        return this.status;
    }
}
