/**
 * VitaCare Pro - Animated Risk Gauge Component
 * SVG-based circular progress indicator with color gradient
 */

class RiskGauge {
    /**
     * Create an animated risk gauge
     * @param {string} containerId - ID of the container element
     * @param {number} riskScore - Risk score (0-100)
     * @param {object} options - Configuration options
     */
    constructor(containerId, riskScore, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Container with id "${containerId}" not found`);
            return;
        }

        this.riskScore = Math.max(0, Math.min(100, riskScore)); // Clamp between 0-100
        this.options = {
            size: options.size || 150,
            strokeWidth: options.strokeWidth || 12,
            animationDuration: options.animationDuration || 1500,
            showLabel: options.showLabel !== false,
            label: options.label || 'Risk Score',
            ...options
        };

        this.render();
    }

    /**
     * Get color based on risk score
     * @param {number} score - Risk score (0-100)
     * @returns {string} Color hex code
     */
    getColor(score) {
        if (score >= 70) return '#ff4444'; // High risk - Red
        if (score >= 40) return '#ffaa00'; // Medium risk - Orange
        return '#44ff44'; // Low risk - Green
    }

    /**
     * Get risk level text
     * @param {number} score - Risk score (0-100)
     * @returns {string} Risk level
     */
    getRiskLevel(score) {
        if (score >= 70) return '🔴 High Risk';
        if (score >= 40) return '🟡 Medium Risk';
        return '🟢 Low Risk';
    }

    /**
     * Render the gauge
     */
    render() {
        const { size, strokeWidth } = this.options;
        const radius = (size - strokeWidth) / 2;
        const circumference = 2 * Math.PI * radius;
        const offset = circumference - (this.riskScore / 100) * circumference;
        const color = this.getColor(this.riskScore);

        this.container.innerHTML = `
            <div class="risk-gauge" style="width: ${size}px; height: ${size}px; position: relative; margin: 20px auto;">
                <svg width="${size}" height="${size}" style="transform: rotate(-90deg);">
                    <!-- Background circle -->
                    <circle
                        class="gauge-background"
                        cx="${size / 2}"
                        cy="${size / 2}"
                        r="${radius}"
                        fill="none"
                        stroke="var(--nav-bg)"
                        stroke-width="${strokeWidth}"
                    />
                    <!-- Progress circle -->
                    <circle
                        class="gauge-progress"
                        cx="${size / 2}"
                        cy="${size / 2}"
                        r="${radius}"
                        fill="none"
                        stroke="${color}"
                        stroke-width="${strokeWidth}"
                        stroke-linecap="round"
                        stroke-dasharray="${circumference}"
                        stroke-dashoffset="${circumference}"
                        style="transition: stroke-dashoffset ${this.options.animationDuration}ms ease-out, stroke 0.5s ease;"
                    />
                </svg>
                <div class="gauge-text">
                    <div style="font-size: var(--fs-3xl); font-weight: var(--fw-extrabold); color: ${color};">
                        <span id="gauge-counter-${this.container.id}">0</span>%
                    </div>
                    ${this.options.showLabel ? `<span class="gauge-label" style="font-size: var(--fs-xs); font-weight: var(--fw-medium); color: var(--text-muted); display: block; margin-top: 4px;">${this.options.label}</span>` : ''}
                </div>
                ${this.options.showRiskLevel !== false ? `
                    <div style="text-align: center; margin-top: 15px; font-weight: 600; color: ${color};">
                        ${this.getRiskLevel(this.riskScore)}
                    </div>
                ` : ''}
            </div>
        `;

        // Animate after a short delay
        setTimeout(() => this.animate(), 100);
    }

    /**
     * Animate the gauge
     */
    animate() {
        const circle = this.container.querySelector('.gauge-progress');
        const counter = this.container.querySelector(`#gauge-counter-${this.container.id}`);

        if (!circle || !counter) return;

        const { size, strokeWidth } = this.options;
        const radius = (size - strokeWidth) / 2;
        const circumference = 2 * Math.PI * radius;
        const offset = circumference - (this.riskScore / 100) * circumference;

        // Animate circle
        circle.style.strokeDashoffset = offset;

        // Animate counter
        this.animateCounter(counter, 0, this.riskScore, this.options.animationDuration);
    }

    /**
     * Animate counter from start to end
     * @param {HTMLElement} element - Counter element
     * @param {number} start - Start value
     * @param {number} end - End value
     * @param {number} duration - Animation duration in ms
     */
    animateCounter(element, start, end, duration) {
        const startTime = performance.now();
        const range = end - start;

        const updateCounter = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Easing function (ease-out)
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const current = Math.round(start + range * easeOut);

            element.textContent = current;

            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            }
        };

        requestAnimationFrame(updateCounter);
    }

    /**
     * Update the gauge with a new score
     * @param {number} newScore - New risk score (0-100)
     */
    update(newScore) {
        this.riskScore = Math.max(0, Math.min(100, newScore));
        this.render();
    }
}

/**
 * Create a risk gauge (convenience function)
 * @param {string} containerId - ID of the container element
 * @param {number} riskScore - Risk score (0-100)
 * @param {object} options - Configuration options
 * @returns {RiskGauge} RiskGauge instance
 */
function createRiskGauge(containerId, riskScore, options = {}) {
    return new RiskGauge(containerId, riskScore, options);
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { RiskGauge, createRiskGauge };
}
