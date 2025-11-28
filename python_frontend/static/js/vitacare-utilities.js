/**
 * VitaCare Pro - Professional UI/UX Utilities
 * Toast Notifications, Loading States, Form Validation & Interactive Features
 */

// ==================== TOAST NOTIFICATION SYSTEM ====================
const VitaCareToast = {
    container: null,
    
    init() {
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            this.container.id = 'toastContainer';
            document.body.appendChild(this.container);
        }
    },
    
    show(message, type = 'info', duration = 5000) {
        this.init();
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: '✓',
            error: '✗',
            warning: '⚠',
            info: 'ℹ'
        };
        
        toast.innerHTML = `
            <span class="toast-icon">${icons[type]}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="this.parentElement.remove()">×</button>
        `;
        
        this.container.appendChild(toast);
        
        // Auto-remove after duration
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-in forwards';
            setTimeout(() => toast.remove(), 300);
        }, duration);
        
        return toast;
    },
    
    success(message, duration) {
        return this.show(message, 'success', duration);
    },
    
    error(message, duration) {
        return this.show(message, 'error', duration);
    },
    
    warning(message, duration) {
        return this.show(message, 'warning', duration);
    },
    
    info(message, duration) {
        return this.show(message, 'info', duration);
    }
};

// Global shorthand function
window.showToast = (message, type, duration) => VitaCareToast.show(message, type, duration);

// ==================== LOADING OVERLAY ====================
const VitaCareLoader = {
    overlay: null,
    
    show(message = 'Loading...') {
        if (!this.overlay) {
            this.overlay = document.createElement('div');
            this.overlay.className = 'spinner-overlay';
            this.overlay.innerHTML = `
                <div style="text-align: center;">
                    <div class="spinner"></div>
                    <p style="color: var(--accent); margin-top: 20px; font-weight: 600;">${message}</p>
                </div>
            `;
            document.body.appendChild(this.overlay);
        }
        this.overlay.style.display = 'flex';
    },
    
    hide() {
        if (this.overlay) {
            this.overlay.style.display = 'none';
        }
    }
};

window.showLoader = (message) => VitaCareLoader.show(message);
window.hideLoader = () => VitaCareLoader.hide();

// ==================== FORM VALIDATION ENHANCEMENTS ====================
const VitaCareFormValidator = {
    // Add real-time validation to input
    addValidation(inputElement, validationRules) {
        inputElement.addEventListener('blur', () => {
            this.validateField(inputElement, validationRules);
        });
        
        inputElement.addEventListener('input', () => {
            // Clear error on input
            if (inputElement.classList.contains('error')) {
                inputElement.classList.remove('error');
                const errorMsg = inputElement.parentElement.querySelector('.form-error');
                if (errorMsg) errorMsg.style.display = 'none';
            }
        });
    },
    
    validateField(inputElement, rules) {
        const value = inputElement.value.trim();
        let isValid = true;
        let errorMessage = '';
        
        // Required check
        if (rules.required && !value) {
            isValid = false;
            errorMessage = `${rules.fieldName || 'This field'} is required`;
        }
        
        // Email validation
        if (rules.email && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Please enter a valid email address';
            }
        }
        
        // Min length
        if (rules.minLength && value.length < rules.minLength) {
            isValid = false;
            errorMessage = `Minimum ${rules.minLength} characters required`;
        }
        
        // Max length
        if (rules.maxLength && value.length > rules.maxLength) {
            isValid = false;
            errorMessage = `Maximum ${rules.maxLength} characters allowed`;
        }
        
        // Number validation
        if (rules.number && value && isNaN(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid number';
        }
        
        // Min value
        if (rules.min !== undefined && parseFloat(value) < rules.min) {
            isValid = false;
            errorMessage = `Value must be at least ${rules.min}`;
        }
        
        // Max value
        if (rules.max !== undefined && parseFloat(value) > rules.max) {
            isValid = false;
            errorMessage = `Value must not exceed ${rules.max}`;
        }
        
        // Pattern matching
        if (rules.pattern && !rules.pattern.test(value)) {
            isValid = false;
            errorMessage = rules.patternMessage || 'Invalid format';
        }
        
        // Update UI
        const errorElement = inputElement.parentElement.querySelector('.form-error');
        const successElement = inputElement.parentElement.querySelector('.form-success');
        
        if (isValid && value) {
            inputElement.classList.remove('error');
            inputElement.classList.add('success');
            if (errorElement) errorElement.style.display = 'none';
            if (successElement) successElement.style.display = 'block';
        } else if (!isValid) {
            inputElement.classList.remove('success');
            inputElement.classList.add('error');
            if (errorElement) {
                errorElement.textContent = errorMessage;
                errorElement.style.display = 'block';
            }
            if (successElement) successElement.style.display = 'none';
        }
        
        return isValid;
    },
    
    // Validate entire form
    validateForm(formElement) {
        const inputs = formElement.querySelectorAll('input[data-validate], textarea[data-validate], select[data-validate]');
        let isFormValid = true;
        
        inputs.forEach(input => {
            const rules = JSON.parse(input.dataset.validate || '{}');
            if (!this.validateField(input, rules)) {
                isFormValid = false;
            }
        });
        
        return isFormValid;
    }
};

window.VitaCareFormValidator = VitaCareFormValidator;

// ==================== ANIMATED NUMBER COUNTER ====================
function animateValue(element, start, end, duration = 1000) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.round(current);
    }, 16);
}

window.animateValue = animateValue;

// ==================== RISK SCORE GAUGE ====================
function createRiskGauge(containerId, score) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Determine color based on score
    let color = '#10b981'; // green (low risk)
    let label = 'Low Risk';
    
    if (score >= 70) {
        color = '#ef4444'; // red (high risk)
        label = 'High Risk';
    } else if (score >= 40) {
        color = '#f59e0b'; // orange (medium risk)
        label = 'Medium Risk';
    }
    
    const circumference = 2 * Math.PI * 54; // radius = 54
    const offset = circumference - (score / 100) * circumference;
    
    container.innerHTML = `
        <svg width="150" height="150" class="risk-gauge">
            <circle class="gauge-background" cx="75" cy="75" r="54"></circle>
            <circle class="gauge-progress" cx="75" cy="75" r="54" 
                    style="stroke: ${color}; stroke-dasharray: ${circumference}; stroke-dashoffset: ${offset}; transform: rotate(-90deg); transform-origin: center;"></circle>
        </svg>
        <div class="gauge-text">
            <strong>${Math.round(score)}%</strong>
            <span class="gauge-label">${label}</span>
        </div>
    `;
}

window.createRiskGauge = createRiskGauge;

// ==================== SMOOTH SCROLL TO ELEMENT ====================
function smoothScrollTo(elementId, offset = 80) {
    const element = document.getElementById(elementId);
    if (element) {
        const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
        const offsetPosition = elementPosition - offset;
        
        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    }
}

window.smoothScrollTo = smoothScrollTo;

// ==================== COPY TO CLIPBOARD ====================
async function copyToClipboard(text, successMessage = 'Copied to clipboard!') {
    try {
        await navigator.clipboard.writeText(text);
        VitaCareToast.success(successMessage);
        return true;
    } catch (err) {
        VitaCareToast.error('Failed to copy');
        return false;
    }
}

window.copyToClipboard = copyToClipboard;

// ==================== CONFIRM DIALOG ====================
function confirmAction(message, onConfirm, onCancel) {
    const backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop';
    backdrop.innerHTML = `
        <div class="modal-content">
            <h3 style="margin-bottom: 20px; color: var(--text-main);">Confirm Action</h3>
            <p style="margin-bottom: 30px; color: var(--text-muted);">${message}</p>
            <div style="display: flex; gap: 15px; justify-content: flex-end;">
                <button class="btn-secondary" onclick="this.closest('.modal-backdrop').remove(); ${onCancel ? onCancel.name + '()' : ''}">Cancel</button>
                <button class="btn-danger" onclick="this.closest('.modal-backdrop').remove(); ${onConfirm.name}()">Confirm</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(backdrop);
    
    // Close on backdrop click
    backdrop.addEventListener('click', (e) => {
        if (e.target === backdrop) {
            backdrop.remove();
            if (onCancel) onCancel();
        }
    });
}

window.confirmAction = confirmAction;

// ==================== TABLE SORTING ====================
function makeSortable(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const headers = table.querySelectorAll('th.sortable');
    headers.forEach((header, index) => {
        header.addEventListener('click', () => {
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const isAscending = header.classList.contains('asc');
            
            // Remove sorting classes from all headers
            headers.forEach(h => h.classList.remove('asc', 'desc'));
            
            // Add appropriate class
            header.classList.add(isAscending ? 'desc' : 'asc');
            
            // Sort rows
            rows.sort((a, b) => {
                const aValue = a.cells[index].textContent.trim();
                const bValue = b.cells[index].textContent.trim();
                
                // Try numeric comparison
                const aNum = parseFloat(aValue);
                const bNum = parseFloat(bValue);
                
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return isAscending ? bNum - aNum : aNum - bNum;
                }
                
                // String comparison
                return isAscending ? 
                    bValue.localeCompare(aValue) : 
                    aValue.localeCompare(bValue);
            });
            
            // Reorder DOM
            rows.forEach(row => tbody.appendChild(row));
        });
    });
}

window.makeSortable = makeSortable;

// ==================== AUTO-INIT ON PAGE LOAD ====================
document.addEventListener('DOMContentLoaded', () => {
    // Initialize toast container
    VitaCareToast.init();
    
    // Add focus indicators
    document.querySelectorAll('input, select, textarea, button, a').forEach(el => {
        el.addEventListener('focus', function() {
            this.style.outline = '2px solid var(--accent)';
            this.style.outlineOffset = '2px';
        });
        el.addEventListener('blur', function() {
            this.style.outline = '';
            this.style.outlineOffset = '';
        });
    });
    
    // Animate stat values on dashboard
    document.querySelectorAll('.stat-value').forEach(el => {
        const value = parseInt(el.textContent);
        if (!isNaN(value)) {
            el.textContent = '0';
            setTimeout(() => animateValue(el, 0, value, 1500), 100);
        }
    });
    
    // Make tables sortable
    document.querySelectorAll('table').forEach(table => {
        if (table.id) makeSortable(table.id);
    });
    
    // Add ripple effect to buttons
    document.querySelectorAll('.btn, .btn-primary, .btn-secondary, .btn-danger').forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.5);
                left: ${x}px;
                top: ${y}px;
                pointer-events: none;
                animation: ripple-effect 0.6s ease-out;
            `;
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
    
    // Log success
    console.log('✨ VitaCare Pro UI Enhancements Initialized');
});

// Add ripple animation
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple-effect {
        from {
            transform: scale(0);
            opacity: 1;
        }
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    @keyframes slideOut {
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
