/**
 * VitaCare Pro - Loading Overlay Utility
 * Professional loading overlay with spinner and optional message
 */

class LoadingOverlay {
    constructor() {
        this.overlay = null;
        this.isVisible = false;
    }

    /**
     * Show loading overlay
     * @param {string} message - Optional loading message
     */
    show(message = 'Processing...') {
        if (this.isVisible) return;

        // Create overlay if it doesn't exist
        if (!this.overlay) {
            this.overlay = document.createElement('div');
            this.overlay.className = 'spinner-overlay';
            this.overlay.innerHTML = `
                <div style="text-align: center;">
                    <div class="spinner"></div>
                    <p id="loading-message" style="color: var(--accent); margin-top: 20px; font-size: 1.1em; font-weight: 600;"></p>
                </div>
            `;
            document.body.appendChild(this.overlay);
        }

        // Update message
        const messageEl = this.overlay.querySelector('#loading-message');
        if (messageEl) {
            messageEl.textContent = message;
        }

        // Show overlay
        this.overlay.style.display = 'flex';
        this.isVisible = true;

        // Prevent body scroll
        document.body.style.overflow = 'hidden';

        // Fade in animation
        setTimeout(() => {
            if (this.overlay) {
                this.overlay.style.opacity = '1';
            }
        }, 10);
    }

    /**
     * Hide loading overlay
     */
    hide() {
        if (!this.isVisible || !this.overlay) return;

        // Fade out animation
        this.overlay.style.opacity = '0';

        setTimeout(() => {
            if (this.overlay) {
                this.overlay.style.display = 'none';
            }
            this.isVisible = false;
            // Restore body scroll
            document.body.style.overflow = '';
        }, 300);
    }

    /**
     * Update loading message
     * @param {string} message - New message
     */
    updateMessage(message) {
        if (!this.overlay) return;
        const messageEl = this.overlay.querySelector('#loading-message');
        if (messageEl) {
            messageEl.textContent = message;
        }
    }

    /**
     * Show loading for a promise
     * @param {Promise} promise - Promise to wait for
     * @param {string} message - Loading message
     * @returns {Promise} The original promise
     */
    async wrap(promise, message = 'Processing...') {
        this.show(message);
        try {
            const result = await promise;
            this.hide();
            return result;
        } catch (error) {
            this.hide();
            throw error;
        }
    }
}

// Create global instance
const loading = new LoadingOverlay();

// Add CSS for fade animation if not already present
if (!document.querySelector('#loading-overlay-styles')) {
    const style = document.createElement('style');
    style.id = 'loading-overlay-styles';
    style.textContent = `
        .spinner-overlay {
            opacity: 0;
            transition: opacity 0.3s ease;
        }
    `;
    document.head.appendChild(style);
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = loading;
}
