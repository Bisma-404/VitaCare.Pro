/**
 * VitaCare Pro - Toast Notification System
 * Professional toast notifications with auto-dismiss and queue management
 */

class ToastNotification {
    constructor() {
        this.container = null;
        this.toasts = [];
        this.init();
    }

    init() {
        // Create toast container if it doesn't exist
        if (!document.querySelector('.toast-container')) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        } else {
            this.container = document.querySelector('.toast-container');
        }
    }

    /**
     * Show a toast notification
     * @param {string} message - The message to display
     * @param {string} type - Type of toast: 'success', 'error', 'warning', 'info'
     * @param {number} duration - Duration in milliseconds (default: 5000)
     */
    show(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        // Icon based on type
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };

        toast.innerHTML = `
            <span class="toast-icon">${icons[type] || icons.info}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close" aria-label="Close notification">×</button>
        `;

        // Add to container
        this.container.appendChild(toast);
        this.toasts.push(toast);

        // Close button handler
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => this.dismiss(toast));

        // Auto-dismiss after duration
        if (duration > 0) {
            setTimeout(() => this.dismiss(toast), duration);
        }

        // Trigger animation
        setTimeout(() => toast.style.opacity = '1', 10);

        return toast;
    }

    /**
     * Dismiss a toast notification
     * @param {HTMLElement} toast - The toast element to dismiss
     */
    dismiss(toast) {
        if (!toast || !toast.parentElement) return;

        // Fade out animation
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(400px)';

        setTimeout(() => {
            if (toast.parentElement) {
                toast.parentElement.removeChild(toast);
            }
            this.toasts = this.toasts.filter(t => t !== toast);
        }, 300);
    }

    /**
     * Show success toast
     * @param {string} message - Success message
     * @param {number} duration - Duration in milliseconds
     */
    success(message, duration = 5000) {
        return this.show(message, 'success', duration);
    }

    /**
     * Show error toast
     * @param {string} message - Error message
     * @param {number} duration - Duration in milliseconds
     */
    error(message, duration = 7000) {
        return this.show(message, 'error', duration);
    }

    /**
     * Show warning toast
     * @param {string} message - Warning message
     * @param {number} duration - Duration in milliseconds
     */
    warning(message, duration = 6000) {
        return this.show(message, 'warning', duration);
    }

    /**
     * Show info toast
     * @param {string} message - Info message
     * @param {number} duration - Duration in milliseconds
     */
    info(message, duration = 5000) {
        return this.show(message, 'info', duration);
    }

    /**
     * Clear all toasts
     */
    clearAll() {
        this.toasts.forEach(toast => this.dismiss(toast));
    }
}

// Create global instance
const toast = new ToastNotification();

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = toast;
}
