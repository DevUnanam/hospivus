// Home page specific JavaScript

class HomePage {
    constructor() {
        this.userType = document.querySelector('[data-user-type]')?.dataset.userType;
        this.init();
    }

    init() {
        // Initialize common functionality
        this.initProgressBars();
        this.initTaskCheckboxes();

        // Initialize user-type specific functionality
        switch (this.userType) {
            case 'PATIENT':
                this.initPatientDashboard();
                break;
            case 'INDIVIDUAL_PROVIDER':
                this.initProviderDashboard();
                break;
            case 'ORGANIZATION':
                this.initOrganizationDashboard();
                break;
            case 'ADMIN':
                this.initAdminDashboard();
                break;
        }
    }

    // Initialize progress bars with animation
    initProgressBars() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.width = entry.target.getAttribute('data-width');
                }
            });
        }, { threshold: 0.5 });

        // Initialize progress bars with 0 width
        document.querySelectorAll('.progress-bar').forEach(bar => {
            const width = bar.style.width;
            bar.setAttribute('data-width', width);
            bar.style.width = '0';
            bar.style.transition = 'width 1s ease-out';
            observer.observe(bar);
        });
    }

    // Initialize task checkboxes
    initTaskCheckboxes() {
        document.querySelectorAll('.task-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const label = e.target.nextElementSibling;
                const taskId = e.target.dataset.taskId;

                if (e.target.checked) {
                    label.classList.add('text-gray-400', 'dark:text-gray-500', 'line-through');
                    label.classList.remove('text-gray-700', 'dark:text-gray-300');
                    this.updateTaskStatus(taskId, 'completed');
                } else {
                    label.classList.remove('text-gray-400', 'dark:text-gray-500', 'line-through');
                    label.classList.add('text-gray-700', 'dark:text-gray-300');
                    this.updateTaskStatus(taskId, 'pending');
                }
            });
        });
    }

    // Update task status via API
    async updateTaskStatus(taskId, status) {
        if (!taskId) return;

        try {
            const response = await fetch('/api/core/update-task/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.csrfToken
                },
                body: JSON.stringify({ taskId, status })
            });

            const data = await response.json();
            if (!data.success) {
                console.error('Failed to update task status');
            }
        } catch (error) {
            console.error('Error updating task:', error);
        }
    }

    // Patient Dashboard Initialization
    initPatientDashboard() {
        this.initDoctorSearch();
        this.initAppointmentActions();
        this.initHealthMetrics();
    }

    // Initialize doctor search functionality
    initDoctorSearch() {
        const searchForm = document.getElementById('doctorSearchForm');
        const modal = document.getElementById('doctorSearchModal');
        const closeModalBtn = document.getElementById('closeModal');
        const searchResults = document.getElementById('searchResults');
        const resultsCount = document.getElementById('resultsCount');
        const loadingState = document.getElementById('loadingState');
        const noResults = document.getElementById('noResults');
        const resultsSummary = document.getElementById('resultsSummary');

        if (!searchForm) return;

        // Handle form submission
        searchForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Show modal and loading state
            modal.classList.remove('hidden');
            loadingState.classList.remove('hidden');
            searchResults.classList.add('hidden');
            noResults.classList.add('hidden');
            resultsSummary.classList.add('hidden');

            // Collect form data
            const formData = new FormData(searchForm);
            const searchParams = new URLSearchParams();

            // Add all form fields to search params
            for (let [key, value] of formData) {
                if (value) {
                    searchParams.append(key, value);
                }
            }

            try {
                // Make call to Django view
                const response = await fetch(`/api/core/doctors/search/?${searchParams.toString()}`, {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': window.csrfToken
                    }
                });

                const data = await response.json();

                // Hide loading state
                loadingState.classList.add('hidden');

                if (data.success && data.count > 0) {
                    // Show results
                    searchResults.innerHTML = data.html;
                    resultsCount.textContent = data.count;
                    resultsSummary.classList.remove('hidden');
                    searchResults.classList.remove('hidden');

                    // Attach event listeners to new elements
                    this.attachDoctorCardListeners();
                } else {
                    // Show no results state
                    noResults.classList.remove('hidden');
                }
            } catch (error) {
                console.error('Error searching doctors:', error);
                // Hide loading and show no results
                loadingState.classList.add('hidden');
                noResults.classList.remove('hidden');
                window.urbanMD.showNotification('error', 'Failed to search doctors. Please try again.');
            }
        });

        // Close modal functionality
        if (closeModalBtn) {
            closeModalBtn.addEventListener('click', () => {
                modal.classList.add('hidden');
            });
        }

        // Close modal when clicking outside
        modal?.addEventListener('click', (e) => {
            if (e.target === modal || e.target.classList.contains('bg-black/50')) {
                modal.classList.add('hidden');
            }
        });
    }

    // Attach event listeners to doctor cards
    attachDoctorCardListeners() {
        document.querySelectorAll('[data-doctor-id]').forEach(card => {
            const bookBtn = card.querySelector('.book-appointment-btn');
            const viewProfileBtn = card.querySelector('.view-profile-btn');

            if (bookBtn) {
                bookBtn.addEventListener('click', () => {
                    const doctorId = card.dataset.doctorId;
                    this.bookAppointment(doctorId);
                });
            }

            if (viewProfileBtn) {
                viewProfileBtn.addEventListener('click', () => {
                    const doctorId = card.dataset.doctorId;
                    this.viewDoctorProfile(doctorId);
                });
            }
        });
    }

    // Book appointment
    bookAppointment(doctorId) {
        window.location.href = `/appointments/book/${doctorId}/`;
    }

    // View doctor profile
    viewDoctorProfile(doctorId) {
        window.location.href = `/doctors/${doctorId}/`;
    }

    // Initialize appointment actions
    initAppointmentActions() {
        document.querySelectorAll('.appointment-action').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.preventDefault();
                const action = btn.dataset.action;
                const appointmentId = btn.dataset.appointmentId;

                switch (action) {
                    case 'video':
                        this.startVideoCall(appointmentId);
                        break;
                    case 'reschedule':
                        this.rescheduleAppointment(appointmentId);
                        break;
                    case 'cancel':
                        await this.cancelAppointment(appointmentId);
                        break;
                    case 'view':
                        this.viewAppointmentDetails(appointmentId);
                        break;
                }
            });
        });
    }

    // Start video call
    startVideoCall(appointmentId) {
        window.location.href = `/appointments/video/${appointmentId}/`;
    }

    // Reschedule appointment
    rescheduleAppointment(appointmentId) {
        window.location.href = `/appointments/reschedule/${appointmentId}/`;
    }

    // Cancel appointment
    async cancelAppointment(appointmentId) {
        if (!confirm('Are you sure you want to cancel this appointment?')) return;

        try {
            const response = await fetch(`/api/appointments/cancel/${appointmentId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': window.csrfToken,
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (data.success) {
                window.urbanMD.showNotification('success', 'Appointment cancelled successfully');
                // Reload the page or update the UI
                setTimeout(() => window.location.reload(), 1500);
            } else {
                window.urbanMD.showNotification('error', data.message || 'Failed to cancel appointment');
            }
        } catch (error) {
            console.error('Error cancelling appointment:', error);
            window.urbanMD.showNotification('error', 'An error occurred while cancelling the appointment');
        }
    }

    // View appointment details
    viewAppointmentDetails(appointmentId) {
        window.location.href = `/appointments/details/${appointmentId}/`;
    }

    // Initialize health metrics
    initHealthMetrics() {
        // Chart initialization would go here
        // For now, just animate the numbers
        document.querySelectorAll('.metric-value').forEach(element => {
            const finalValue = parseInt(element.textContent);
            const duration = 1000; // 1 second
            const increment = finalValue / (duration / 16); // 60 FPS
            let currentValue = 0;

            const updateValue = () => {
                currentValue += increment;
                if (currentValue < finalValue) {
                    element.textContent = Math.floor(currentValue);
                    requestAnimationFrame(updateValue);
                } else {
                    element.textContent = finalValue;
                }
            };

            // Start animation when element is in view
            const observer = new IntersectionObserver((entries) => {
                if (entries[0].isIntersecting) {
                    updateValue();
                    observer.disconnect();
                }
            });

            observer.observe(element);
        });
    }

    // Provider Dashboard Initialization
    initProviderDashboard() {
        this.initAppointmentCalendar();
        this.initPatientQueue();
        this.initQuickActions();
    }

    // Initialize appointment calendar for providers
    initAppointmentCalendar() {
        // Calendar initialization would go here
        // For now, handle appointment actions
        document.querySelectorAll('.provider-appointment-action').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.preventDefault();
                const action = btn.dataset.action;
                const appointmentId = btn.dataset.appointmentId;

                switch (action) {
                    case 'start':
                        await this.startAppointment(appointmentId);
                        break;
                    case 'complete':
                        await this.completeAppointment(appointmentId);
                        break;
                    case 'notes':
                        this.openAppointmentNotes(appointmentId);
                        break;
                }
            });
        });
    }

    // Start appointment
    async startAppointment(appointmentId) {
        try {
            const response = await fetch(`/api/appointments/start/${appointmentId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': window.csrfToken,
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (data.success) {
                window.urbanMD.showNotification('success', 'Appointment started');
                // Update UI or redirect
                window.location.href = `/appointments/session/${appointmentId}/`;
            }
        } catch (error) {
            console.error('Error starting appointment:', error);
            window.urbanMD.showNotification('error', 'Failed to start appointment');
        }
    }

    // Complete appointment
    async completeAppointment(appointmentId) {
        // Implementation would go here
        window.location.href = `/appointments/complete/${appointmentId}/`;
    }

    // Open appointment notes
    openAppointmentNotes(appointmentId) {
        window.location.href = `/appointments/notes/${appointmentId}/`;
    }

    // Initialize patient queue
    initPatientQueue() {
        // Real-time updates would be implemented here
        // For now, just refresh every 30 seconds
        if (document.querySelector('.patient-queue')) {
            setInterval(() => {
                this.refreshPatientQueue();
            }, 30000);
        }
    }

    // Refresh patient queue
    async refreshPatientQueue() {
        try {
            const response = await fetch('/api/appointments/queue/', {
                headers: {
                    'X-CSRFToken': window.csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (data.success && data.html) {
                const queueElement = document.querySelector('.patient-queue');
                if (queueElement) {
                    queueElement.innerHTML = data.html;
                    this.initAppointmentCalendar(); // Re-attach event listeners
                }
            }
        } catch (error) {
            console.error('Error refreshing patient queue:', error);
        }
    }

    // Initialize quick actions for providers
    initQuickActions() {
        document.querySelectorAll('.quick-action').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const action = btn.dataset.action;

                switch (action) {
                    case 'new-patient':
                        window.location.href = '/patients/new/';
                        break;
                    case 'prescriptions':
                        window.location.href = '/prescriptions/';
                        break;
                    case 'lab-results':
                        window.location.href = '/lab-results/';
                        break;
                    case 'messages':
                        window.location.href = '/messages/';
                        break;
                }
            });
        });
    }

    // Organization Dashboard Initialization
    initOrganizationDashboard() {
        this.initProviderManagement();
        this.initLocationManagement();
        this.initOrganizationStats();
    }

    // Initialize provider management
    initProviderManagement() {
        document.querySelectorAll('.provider-action').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const action = btn.dataset.action;
                const providerId = btn.dataset.providerId;

                switch (action) {
                    case 'view':
                        window.location.href = `/providers/${providerId}/`;
                        break;
                    case 'edit':
                        window.location.href = `/providers/${providerId}/edit/`;
                        break;
                    case 'schedule':
                        window.location.href = `/providers/${providerId}/schedule/`;
                        break;
                }
            });
        });
    }

    // Initialize location management
    initLocationManagement() {
        document.querySelectorAll('.location-action').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const action = btn.dataset.action;
                const locationId = btn.dataset.locationId;

                switch (action) {
                    case 'view':
                        window.location.href = `/locations/${locationId}/`;
                        break;
                    case 'edit':
                        window.location.href = `/locations/${locationId}/edit/`;
                        break;
                    case 'analytics':
                        window.location.href = `/locations/${locationId}/analytics/`;
                        break;
                }
            });
        });
    }

    // Initialize organization stats
    initOrganizationStats() {
        // Chart initialization would go here
        // For now, just handle the stats refresh
        document.querySelector('.refresh-stats')?.addEventListener('click', async (e) => {
            e.preventDefault();
            await this.refreshOrganizationStats();
        });
    }

    // Refresh organization stats
    async refreshOrganizationStats() {
        try {
            const response = await fetch('/api/organization/stats/', {
                headers: {
                    'X-CSRFToken': window.csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (data.success) {
                // Update stats in the UI
                Object.keys(data.stats).forEach(key => {
                    const element = document.querySelector(`[data-stat="${key}"]`);
                    if (element) {
                        element.textContent = data.stats[key];
                    }
                });

                window.urbanMD.showNotification('success', 'Stats updated');
            }
        } catch (error) {
            console.error('Error refreshing stats:', error);
            window.urbanMD.showNotification('error', 'Failed to refresh stats');
        }
    }

    // Admin Dashboard Initialization
    initAdminDashboard() {
        this.initSystemMonitoring();
        this.initUserManagement();
        this.initVerificationQueue();
    }

    // Initialize system monitoring
    initSystemMonitoring() {
        // Real-time monitoring would be implemented here
        // For now, just refresh every minute
        if (document.querySelector('.system-stats')) {
            setInterval(() => {
                this.refreshSystemStats();
            }, 60000);
        }
    }

    // Refresh system stats
    async refreshSystemStats() {
        try {
            const response = await fetch('/api/admin/system-stats/', {
                headers: {
                    'X-CSRFToken': window.csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (data.success) {
                // Update system stats in the UI
                Object.keys(data.stats).forEach(key => {
                    const element = document.querySelector(`[data-system-stat="${key}"]`);
                    if (element) {
                        element.textContent = data.stats[key];
                    }
                });
            }
        } catch (error) {
            console.error('Error refreshing system stats:', error);
        }
    }

    // Initialize user management
    initUserManagement() {
        document.querySelectorAll('.user-action').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.preventDefault();
                const action = btn.dataset.action;
                const userId = btn.dataset.userId;

                switch (action) {
                    case 'view':
                        window.location.href = `/admin/users/${userId}/`;
                        break;
                    case 'suspend':
                        await this.suspendUser(userId);
                        break;
                    case 'activate':
                        await this.activateUser(userId);
                        break;
                }
            });
        });
    }

    // Suspend user
    async suspendUser(userId) {
        if (!confirm('Are you sure you want to suspend this user?')) return;

        try {
            const response = await fetch(`/api/admin/users/${userId}/suspend/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': window.csrfToken,
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (data.success) {
                window.urbanMD.showNotification('success', 'User suspended successfully');
                setTimeout(() => window.location.reload(), 1500);
            }
        } catch (error) {
            console.error('Error suspending user:', error);
            window.urbanMD.showNotification('error', 'Failed to suspend user');
        }
    }

    // Activate user
    async activateUser(userId) {
        try {
            const response = await fetch(`/api/admin/users/${userId}/activate/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': window.csrfToken,
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (data.success) {
                window.urbanMD.showNotification('success', 'User activated successfully');
                setTimeout(() => window.location.reload(), 1500);
            }
        } catch (error) {
            console.error('Error activating user:', error);
            window.urbanMD.showNotification('error', 'Failed to activate user');
        }
    }

    // Initialize verification queue
    initVerificationQueue() {
        document.querySelectorAll('.verification-action').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.preventDefault();
                const action = btn.dataset.action;
                const type = btn.dataset.type;
                const id = btn.dataset.id;

                switch (action) {
                    case 'approve':
                        await this.approveVerification(type, id);
                        break;
                    case 'reject':
                        await this.rejectVerification(type, id);
                        break;
                    case 'view':
                        this.viewVerificationDetails(type, id);
                        break;
                }
            });
        });
    }

    // Approve verification
    async approveVerification(type, id) {
        try {
            const response = await fetch(`/api/admin/verify/${type}/${id}/approve/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': window.csrfToken,
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (data.success) {
                window.urbanMD.showNotification('success', 'Verification approved');
                setTimeout(() => window.location.reload(), 1500);
            }
        } catch (error) {
            console.error('Error approving verification:', error);
            window.urbanMD.showNotification('error', 'Failed to approve verification');
        }
    }

    // Reject verification
    async rejectVerification(type, id) {
        const reason = prompt('Please provide a reason for rejection:');
        if (!reason) return;

        try {
            const response = await fetch(`/api/admin/verify/${type}/${id}/reject/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': window.csrfToken,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ reason })
            });

            const data = await response.json();

            if (data.success) {
                window.urbanMD.showNotification('success', 'Verification rejected');
                setTimeout(() => window.location.reload(), 1500);
            }
        } catch (error) {
            console.error('Error rejecting verification:', error);
            window.urbanMD.showNotification('error', 'Failed to reject verification');
        }
    }

    // View verification details
    viewVerificationDetails(type, id) {
        window.location.href = `/admin/verify/${type}/${id}/`;
    }
}

// Initialize HomePage when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new HomePage();
});