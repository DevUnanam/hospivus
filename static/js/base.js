// Base JavaScript functionality for UrbanMD Health Network

class UrbanMD {
    constructor() {
        this.init();
    }

    init() {
        this.initPageLoader();
        this.initSidebar();
        this.initDarkMode();
        this.initNotifications();
        this.setupEventListeners();
    }

    // Initialize page loader
    initPageLoader() {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(() => {
                const loader = document.querySelector('.page-loader');
                if (loader) {
                    loader.classList.add('loaded');
                    setTimeout(() => loader.remove(), 500);
                }
            }, 500);
        });
    }

    // Initialize sidebar functionality
    initSidebar() {
        const sidebar = document.getElementById('sidebar');
        const sidebarOpen = document.getElementById('sidebar-open');
        const sidebarClose = document.getElementById('sidebar-close');

        if (sidebarOpen && sidebar) {
            sidebarOpen.addEventListener('click', () => {
                sidebar.classList.remove('sidebar-collapsed');
            });
        }

        if (sidebarClose && sidebar) {
            sidebarClose.addEventListener('click', () => {
                sidebar.classList.add('sidebar-collapsed');
            });
        }

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (event) => {
            if (!sidebar || !sidebarOpen) return;

            const isClickInsideSidebar = sidebar.contains(event.target);
            const isClickInsideSidebarOpen = sidebarOpen.contains(event.target);

            if (!isClickInsideSidebar && !isClickInsideSidebarOpen && window.innerWidth < 1024) {
                sidebar.classList.add('sidebar-collapsed');
            }
        });

        // Resize handler
        window.addEventListener('resize', () => {
            if (!sidebar) return;

            if (window.innerWidth >= 1024) {
                sidebar.classList.remove('sidebar-collapsed');
            } else {
                sidebar.classList.add('sidebar-collapsed');
            }
        });

        // Initialize sidebar state based on screen size
        if (sidebar && window.innerWidth < 1024) {
            sidebar.classList.add('sidebar-collapsed');
        }
    }

    // Dark mode is already handled in the HTML, but we can add additional functionality here
    initDarkMode() {
        // Additional dark mode functionality if needed
    }

    // Initialize notifications
    initNotifications() {
        // Placeholder for notification system
        // This will be implemented when we add real-time notifications
    }

    // Setup common event listeners
    setupEventListeners() {
        // Handle CSRF token for AJAX requests
        this.setupCSRFToken();

        // Handle form submissions with loading states
        this.setupFormHandlers();
    }

    // Setup CSRF token for AJAX requests
    setupCSRFToken() {
        // Get CSRF token from cookie
        const csrftoken = this.getCookie('csrftoken');

        // Set default headers for fetch
        if (csrftoken) {
            window.csrfToken = csrftoken;
        }
    }

    // Get cookie value by name
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Setup form handlers
    setupFormHandlers() {
        document.querySelectorAll('form[data-ajax]').forEach(form => {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleAjaxForm(form);
            });
        });
    }

    // Handle AJAX form submission
    async handleAjaxForm(form) {
        const submitBtn = form.querySelector('[type="submit"]');
        const originalText = submitBtn ? submitBtn.textContent : '';

        try {
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Loading...';
            }

            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: form.method || 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': window.csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification('success', data.message || 'Operation successful');
                if (data.redirect) {
                    window.location.href = data.redirect;
                }
            } else {
                this.showNotification('error', data.message || 'An error occurred');
            }
        } catch (error) {
            console.error('Form submission error:', error);
            this.showNotification('error', 'An unexpected error occurred');
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        }
    }

    // Show notification (basic implementation)
    showNotification(type, message) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 max-w-sm transform transition-all duration-300 translate-x-full`;

        // Set colors based on type
        const colors = {
            success: 'bg-green-500 text-white',
            error: 'bg-red-500 text-white',
            warning: 'bg-yellow-500 text-white',
            info: 'bg-blue-500 text-white'
        };

        notification.classList.add(...colors[type].split(' '));
        notification.innerHTML = `
            <div class="flex items-center">
                <span class="flex-1">${message}</span>
                <button class="ml-4 text-white hover:text-gray-200" onclick="this.parentElement.parentElement.remove()">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
        `;

        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.classList.remove('translate-x-full');
        }, 100);

        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.classList.add('translate-x-full');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }

    // Utility function to format dates
    formatDate(date, format = 'short') {
        const options = format === 'short'
            ? { month: 'short', day: 'numeric', year: 'numeric' }
            : { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };

        return new Date(date).toLocaleDateString('en-US', options);
    }

    // Utility function to format time
    formatTime(time) {
        return new Date(`2000-01-01 ${time}`).toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    }
}

// Initialize UrbanMD when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.urbanMD = new UrbanMD();
});