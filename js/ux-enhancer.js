/**
 * TURSAKUR Performance & UX Enhancement Module
 * Provides loading animations, performance optimizations, and better user experience
 */

class UXEnhancer {
    constructor() {
        this.loadingStates = new Set();
        this.performanceMetrics = {
            loadStartTime: performance.now(),
            dataLoadTime: null,
            renderTime: null
        };
        
        this.init();
    }
    
    init() {
        this.setupLoadingSystem();
        this.setupIntersectionObserver();
        this.setupSmoothScrolling();
        this.setupKeyboardNavigation();
        this.setupOfflineSupport();
        this.trackPerformance();
    }
    
    setupLoadingSystem() {
        // Create global loading overlay
        const loadingOverlay = document.createElement('div');
        loadingOverlay.id = 'global-loading';
        loadingOverlay.className = 'loading-overlay';
        loadingOverlay.innerHTML = `
            <div class="loading-content">
                <div class="loading-logo">
                    <img src="assets/logos/TURSAKUR-Color.png" alt="TURSAKUR" class="loading-logo-img">
                </div>
                <div class="loading-spinner">
                    <div class="spinner-ring"></div>
                    <div class="spinner-ring"></div>
                    <div class="spinner-ring"></div>
                </div>
                <div class="loading-text">Sağlık kuruluşları yükleniyor...</div>
                <div class="loading-progress">
                    <div class="progress-bar" id="loading-progress-bar"></div>
                </div>
            </div>
        `;
        document.body.appendChild(loadingOverlay);
        
        // Create skeleton loaders for cards
        this.createSkeletonLoaders();
    }
    
    createSkeletonLoaders() {
        const resultsGrid = document.getElementById('results-grid');
        if (!resultsGrid) return;
        
        // Create skeleton cards
        const skeletonHTML = Array(6).fill().map(() => `
            <div class="hospital-card skeleton-card">
                <div class="skeleton-header">
                    <div class="skeleton-title"></div>
                    <div class="skeleton-badge"></div>
                </div>
                <div class="skeleton-body">
                    <div class="skeleton-line"></div>
                    <div class="skeleton-line short"></div>
                    <div class="skeleton-line medium"></div>
                </div>
                <div class="skeleton-footer">
                    <div class="skeleton-button"></div>
                    <div class="skeleton-button secondary"></div>
                </div>
            </div>
        `).join('');
        
        resultsGrid.innerHTML = skeletonHTML;
    }
    
    showLoading(message = 'Yükleniyor...', progress = false) {
        const overlay = document.getElementById('global-loading');
        const textElement = overlay.querySelector('.loading-text');
        const progressBar = overlay.querySelector('.loading-progress');
        
        textElement.textContent = message;
        progressBar.style.display = progress ? 'block' : 'none';
        
        overlay.style.display = 'flex';
        overlay.classList.add('active');
        
        this.loadingStates.add('global');
    }
    
    hideLoading() {
        const overlay = document.getElementById('global-loading');
        
        overlay.classList.remove('active');
        
        setTimeout(() => {
            overlay.style.display = 'none';
            this.loadingStates.delete('global');
        }, 300);
    }
    
    updateLoadingProgress(percentage) {
        const progressBar = document.getElementById('loading-progress-bar');
        if (progressBar) {
            progressBar.style.width = `${percentage}%`;
        }
    }
    
    setupIntersectionObserver() {
        // Lazy loading for images and cards
        const observerOptions = {
            root: null,
            rootMargin: '50px',
            threshold: 0.1
        };
        
        this.imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        this.imageObserver.unobserve(img);
                    }
                }
            });
        }, observerOptions);
        
        // Animation observer for cards
        this.animationObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                    this.animationObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.2 });
    }
    
    observeElements() {
        // Observe images for lazy loading
        document.querySelectorAll('img[data-src]').forEach(img => {
            this.imageObserver.observe(img);
        });
        
        // Observe cards for animation
        document.querySelectorAll('.hospital-card:not(.skeleton-card)').forEach(card => {
            this.animationObserver.observe(card);
        });
    }
    
    setupSmoothScrolling() {
        // Enhanced smooth scrolling with easing
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a[href^="#"]');
            if (link) {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    this.smoothScrollTo(targetElement);
                }
            }
        });
    }
    
    smoothScrollTo(element, duration = 800) {
        const start = window.pageYOffset;
        const target = element.offsetTop - 80; // Account for header
        const distance = target - start;
        let startTime = null;
        
        const ease = (t) => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
        
        const animation = (currentTime) => {
            if (startTime === null) startTime = currentTime;
            const timeElapsed = currentTime - startTime;
            const run = ease(timeElapsed / duration) * distance + start;
            
            window.scrollTo(0, run);
            
            if (timeElapsed < duration) {
                requestAnimationFrame(animation);
            }
        };
        
        requestAnimationFrame(animation);
    }
    
    setupKeyboardNavigation() {
        // Enhanced keyboard navigation
        document.addEventListener('keydown', (e) => {
            // Quick search with Ctrl+F or Cmd+F
            if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
                e.preventDefault();
                const searchInput = document.getElementById('search-input');
                if (searchInput) {
                    searchInput.focus();
                    searchInput.select();
                }
            }
            
            // Toggle theme with Ctrl+D or Cmd+D
            if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
                e.preventDefault();
                const themeToggle = document.getElementById('theme-toggle');
                if (themeToggle) {
                    themeToggle.click();
                }
            }
            
            // Escape to clear search
            if (e.key === 'Escape') {
                const searchInput = document.getElementById('search-input');
                if (searchInput && searchInput.value) {
                    searchInput.value = '';
                    searchInput.dispatchEvent(new Event('input'));
                }
            }
        });
    }
    
    setupOfflineSupport() {
        // Offline detection and notification
        window.addEventListener('online', () => {
            this.showNotification('İnternet bağlantısı restore edildi', 'success');
        });
        
        window.addEventListener('offline', () => {
            this.showNotification('İnternet bağlantısı kesildi. Uygulama çevrimdışı modda çalışıyor.', 'warning', 5000);
        });
    }
    
    showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span class="material-symbols-outlined">
                ${type === 'success' ? 'check_circle' : type === 'warning' ? 'warning' : 'info'}
            </span>
            <span>${message}</span>
            <button class="notification-close">
                <span class="material-symbols-outlined">close</span>
            </button>
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Auto remove
        const removeNotification = () => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        };
        
        setTimeout(removeNotification, duration);
        
        // Close button
        notification.querySelector('.notification-close').addEventListener('click', removeNotification);
    }
    
    trackPerformance() {
        // Track page load performance
        window.addEventListener('load', () => {
            setTimeout(() => {
                const navigation = performance.getEntriesByType('navigation')[0];
                const loadTime = navigation.loadEventEnd - navigation.loadEventStart;
                
                console.log('Performance Metrics:', {
                    pageLoadTime: `${loadTime.toFixed(2)}ms`,
                    domContentLoaded: `${navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart}ms`,
                    firstContentfulPaint: this.getFirstContentfulPaint()
                });
                
                // Send analytics (if implemented)
                this.sendPerformanceAnalytics({
                    loadTime,
                    userAgent: navigator.userAgent,
                    timestamp: new Date().toISOString()
                });
            }, 0);
        });
    }
    
    getFirstContentfulPaint() {
        const paint = performance.getEntriesByType('paint');
        const fcp = paint.find(entry => entry.name === 'first-contentful-paint');
        return fcp ? `${fcp.startTime.toFixed(2)}ms` : 'N/A';
    }
    
    sendPerformanceAnalytics(data) {
        // Placeholder for analytics service
        if (window.gtag) {
            gtag('event', 'page_load_time', {
                value: data.loadTime,
                custom_parameter: 'tursakur_performance'
            });
        }
    }
    
    // Utility methods for better UX
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
    
    // Virtual scrolling for large datasets
    enableVirtualScrolling(container, itemHeight = 100) {
        let isScrolling = false;
        const visibleItems = Math.ceil(container.clientHeight / itemHeight) + 2;
        
        const updateVisibleItems = this.throttle(() => {
            const scrollTop = container.scrollTop;
            const startIndex = Math.floor(scrollTop / itemHeight);
            const endIndex = Math.min(startIndex + visibleItems, this.totalItems);
            
            // Update visible items logic here
            this.renderVisibleItems(startIndex, endIndex);
        }, 16); // 60fps
        
        container.addEventListener('scroll', updateVisibleItems);
    }
    
    // Progressive image loading
    loadImageProgressive(img, lowQualitySrc, highQualitySrc) {
        const lowQualityImg = new Image();
        lowQualityImg.onload = () => {
            img.src = lowQualitySrc;
            img.classList.add('loaded-low');
            
            const highQualityImg = new Image();
            highQualityImg.onload = () => {
                img.src = highQualitySrc;
                img.classList.add('loaded-high');
                img.classList.remove('loaded-low');
            };
            highQualityImg.src = highQualitySrc;
        };
        lowQualityImg.src = lowQualitySrc;
    }
}

// Initialize UX enhancer
const uxEnhancer = new UXEnhancer();

// Export for use in other modules
window.UXEnhancer = uxEnhancer;
