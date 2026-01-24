// Main JavaScript file for College Management System

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure you want to delete this item?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Star rating functionality
    const starContainers = document.querySelectorAll('.star-rating');
    starContainers.forEach(function(container) {
        const stars = container.querySelectorAll('.star');
        const input = container.querySelector('input[type="hidden"]');

        stars.forEach(function(star, index) {
            star.addEventListener('click', function() {
                const rating = index + 1;
                input.value = rating;

                stars.forEach(function(s, i) {
                    if (i < rating) {
                        s.classList.add('filled');
                    } else {
                        s.classList.remove('filled');
                    }
                });
            });

            star.addEventListener('mouseenter', function() {
                stars.forEach(function(s, i) {
                    if (i <= index) {
                        s.style.color = '#f39c12';
                    }
                });
            });

            star.addEventListener('mouseleave', function() {
                stars.forEach(function(s, i) {
                    if (!s.classList.contains('filled')) {
                        s.style.color = '#ddd';
                    } else {
                        s.style.color = '#f39c12';
                    }
                });
            });
        });
    });

    // Select all checkbox functionality for attendance
    const selectAllCheckbox = document.getElementById('select-all');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.attendance-checkbox');
            checkboxes.forEach(function(checkbox) {
                checkbox.checked = selectAllCheckbox.checked;
                updateAttendanceItem(checkbox);
            });
        });
    }

    // Individual attendance checkbox
    const attendanceCheckboxes = document.querySelectorAll('.attendance-checkbox');
    attendanceCheckboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            updateAttendanceItem(this);
        });
    });

    function updateAttendanceItem(checkbox) {
        const item = checkbox.closest('.attendance-item');
        if (item) {
            if (checkbox.checked) {
                item.classList.add('present');
                item.classList.remove('absent');
            } else {
                item.classList.add('absent');
                item.classList.remove('present');
            }
        }
    }

    // Modal functionality
    const modalTriggers = document.querySelectorAll('[data-modal]');
    modalTriggers.forEach(function(trigger) {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            const modalId = this.getAttribute('data-modal');
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.add('active');
            }
        });
    });

    const modalCloseButtons = document.querySelectorAll('.modal-close');
    modalCloseButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const modal = this.closest('.modal-overlay');
            if (modal) {
                modal.classList.remove('active');
            }
        });
    });

    // Close modal on overlay click
    const modalOverlays = document.querySelectorAll('.modal-overlay');
    modalOverlays.forEach(function(overlay) {
        overlay.addEventListener('click', function(e) {
            if (e.target === this) {
                this.classList.remove('active');
            }
        });
    });

    // Form validation
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            const requiredInputs = form.querySelectorAll('[required]');

            requiredInputs.forEach(function(input) {
                if (!input.value.trim()) {
                    isValid = false;
                    input.classList.add('error');
                    showError(input, 'This field is required');
                } else {
                    input.classList.remove('error');
                    hideError(input);
                }
            });

            if (!isValid) {
                e.preventDefault();
            }
        });
    });

    function showError(input, message) {
        let errorDiv = input.nextElementSibling;
        if (!errorDiv || !errorDiv.classList.contains('error-message')) {
            errorDiv = document.createElement('div');
            errorDiv.classList.add('error-message');
            input.parentNode.insertBefore(errorDiv, input.nextSibling);
        }
        errorDiv.textContent = message;
    }

    function hideError(input) {
        const errorDiv = input.nextElementSibling;
        if (errorDiv && errorDiv.classList.contains('error-message')) {
            errorDiv.remove();
        }
    }

    // Print functionality
    const printButtons = document.querySelectorAll('[data-print]');
    printButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            window.print();
        });
    });
});
