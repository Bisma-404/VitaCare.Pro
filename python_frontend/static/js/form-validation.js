/**
 * VitaCare Pro - Form Validation Utility
 * Real-time form validation with visual feedback
 */

class FormValidator {
    constructor(formId) {
        this.form = document.getElementById(formId);
        if (!this.form) {
            console.error(`Form with id "${formId}" not found`);
            return;
        }
        this.init();
    }

    init() {
        // Add validation on blur for all inputs
        const inputs = this.form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('input', () => {
                if (input.classList.contains('error')) {
                    this.validateField(input);
                }
            });
        });

        // Prevent submission if form is invalid
        this.form.addEventListener('submit', (e) => {
            if (!this.validateForm()) {
                e.preventDefault();
                toast.error('Please fix the errors before submitting');
            }
        });
    }

    validateField(field) {
        const value = field.value.trim();
        const type = field.type;
        const required = field.hasAttribute('required');

        // Clear previous errors
        this.clearFieldError(field);

        // Required validation
        if (required && !value) {
            this.setFieldError(field, 'This field is required');
            return false;
        }

        // Type-specific validation
        if (value) {
            switch (type) {
                case 'email':
                    if (!this.isValidEmail(value)) {
                        this.setFieldError(field, 'Please enter a valid email address');
                        return false;
                    }
                    break;
                case 'number':
                    const min = field.getAttribute('min');
                    const max = field.getAttribute('max');
                    const numValue = parseFloat(value);
                    if (isNaN(numValue)) {
                        this.setFieldError(field, 'Please enter a valid number');
                        return false;
                    }
                    if (min !== null && numValue < parseFloat(min)) {
                        this.setFieldError(field, `Value must be at least ${min}`);
                        return false;
                    }
                    if (max !== null && numValue > parseFloat(max)) {
                        this.setFieldError(field, `Value must be at most ${max}`);
                        return false;
                    }
                    break;
                case 'tel':
                    if (!this.isValidPhone(value)) {
                        this.setFieldError(field, 'Please enter a valid phone number');
                        return false;
                    }
                    break;
            }
        }

        // If we got here, field is valid
        this.setFieldSuccess(field);
        return true;
    }

    validateForm() {
        const inputs = this.form.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });

        return isValid;
    }

    setFieldError(field, message) {
        field.classList.add('error');
        field.classList.remove('success');

        // Find or create error message element
        let errorEl = field.parentElement.querySelector('.form-error');
        if (!errorEl) {
            errorEl = document.createElement('span');
            errorEl.className = 'form-error';
            field.parentElement.appendChild(errorEl);
        }
        errorEl.textContent = message;
        errorEl.style.display = 'block';
    }

    setFieldSuccess(field) {
        field.classList.remove('error');
        field.classList.add('success');
        this.clearFieldError(field);
    }

    clearFieldError(field) {
        field.classList.remove('error', 'success');
        const errorEl = field.parentElement.querySelector('.form-error');
        if (errorEl) {
            errorEl.style.display = 'none';
        }
    }

    isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    isValidPhone(phone) {
        const re = /^[\d\s\-\+\(\)]{10,}$/;
        return re.test(phone);
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FormValidator;
}
