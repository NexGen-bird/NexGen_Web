// NEXGEN Study Centre - Main JavaScript File
// Handles interactive functionality across the application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components when DOM is loaded
    initializeComponents();
    setupEventListeners();
    setupFormValidation();
});

// Initialize various components
function initializeComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
}

// Setup global event listeners
function setupEventListeners() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Auto-hide alerts after 5 seconds
    // const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    // alerts.forEach(alert => {
    //     setTimeout(() => {
    //         const bsAlert = new bootstrap.Alert(alert);
    //         bsAlert.close();
    //     }, 5000);
    // });

    // WhatsApp integration helpers
    setupWhatsAppIntegration();
}

// Form validation and enhancements
function setupFormValidation() {
    // Custom form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Focus on first invalid field
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
            form.classList.add('was-validated');
        });
    });

    // Real-time validation feedback
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.checkValidity()) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            } else {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
            }
        });
    });

    // Phone number formatting
    const phoneInputs = document.querySelectorAll('input[type="tel"], input[name*="phone"], input[name*="contact"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function() {
            // Remove non-numeric characters except +
            let value = this.value.replace(/[^\d+]/g, '');
            
            // Format Indian mobile numbers
            // if (value.length === 10 && !value.startsWith('+')) {
            //     value = '+91' + value;
            // }
            
            this.value = value;
        });
    });
}

// WhatsApp Integration Functions
function setupWhatsAppIntegration() {
    // Add WhatsApp floating button if not presentfpop
    // addWhatsAppFloat();
    
    // Setup WhatsApp share buttons
    const whatsappButtons = document.querySelectorAll('.btn-whatsapp, [data-whatsapp]');
    whatsappButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Add loading state
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="loading-spinner"></span> Sending...';
            this.disabled = true;
            
            // Re-enable after 2 seconds
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
            }, 2000);
        });
    });
}

// function addWhatsAppFloat() {
//     // Add floating WhatsApp button for general inquiries
//     const whatsappFloat = document.createElement('a');
//     whatsappFloat.href = 'https://wa.me/919594897959?text=Hello%20NEXGEN%20Study%20Centre,%20I%20need%20assistance.';
//     whatsappFloat.target = '_blank';
//     whatsappFloat.className = 'whatsapp-float';
//     whatsappFloat.innerHTML = '<i class="fab fa-whatsapp"></i>';
//     whatsappFloat.title = 'Chat with us on WhatsApp';
    
//     // Only add if not already present
//     if (!document.querySelector('.whatsapp-float')) {
//         document.body.appendChild(whatsappFloat);
//     }
// }

// Utility Functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    }).format(amount);
}

function formatDate(date, options = {}) {
    const defaultOptions = {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    };
    return new Date(date).toLocaleDateString('en-IN', { ...defaultOptions, ...options });
}

function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '1100';
        document.body.appendChild(toastContainer);
    }

    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();

    // Remove toast element after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Dashboard specific functions
function initializeDashboardCharts() {
    // This function is called from dashboard.html template
    // Charts are initialized there using Chart.js
    console.log('Dashboard charts initialization handled in template');
}

// Age calculation for admission form
function calculateAge() {
    const birthDate = document.getElementById('date_of_birth');
    const ageDisplay = document.getElementById('ageDisplay');
    
    if (birthDate && ageDisplay && birthDate.value) {
        const birth = new Date(birthDate.value);
        const today = new Date();
        let age = today.getFullYear() - birth.getFullYear();
        const monthDiff = today.getMonth() - birth.getMonth();
        
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
            age--;
        }
        
        ageDisplay.value = age + ' years';
    }
}

// Transaction form enhancements
function calculateEndDate() {
    const startDate = document.getElementById('start_date');
    const endDate = document.getElementById('end_date');
    const plan = document.getElementById('plan');
    
    if (startDate && endDate && plan && startDate.value) {
        const start = new Date(startDate.value);
        let end = new Date(start);
        
        switch(plan.value) {
            case 'Monthly':
                end.setMonth(end.getMonth() + 1);
                break;
            case 'Quarterly':
                end.setMonth(end.getMonth() + 3);
                break;
            case 'Half Yearly':
                end.setMonth(end.getMonth() + 6);
                break;
            case 'Yearly':
                end.setFullYear(end.getFullYear() + 1);
                break;
            case 'Day':
                end.setDate(end.getDate() + 1);
                break;
            case 'Weekend':
                end.setDate(end.getDate() + 2);
                break;
        }
        
        endDate.value = end.toISOString().split('T')[0];
    }
}

function calculateFinalAmount() {
    const amountField = document.getElementById('amount');
    const discountField = document.getElementById('discount');
    const finalAmountDisplay = document.getElementById('finalAmountDisplay');
    
    if (amountField && finalAmountDisplay) {
        const amount = parseFloat(amountField.value) || 0;
        const discount = parseFloat(discountField?.value) || 0;
        const finalAmount = amount - discount;
        
        finalAmountDisplay.value = formatCurrency(finalAmount);
    }
}

// Search and filter functions
function filterTable(searchInputId, tableSelector) {
    const searchInput = document.getElementById(searchInputId);
    const table = document.querySelector(tableSelector);
    
    if (!searchInput || !table) return;
    
    const filter = searchInput.value.toUpperCase();
    const rows = table.querySelectorAll('tbody tr');

    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        let match = false;
        
        cells.forEach(cell => {
            if (cell.textContent.toUpperCase().includes(filter)) {
                match = true;
            }
        });
        
        row.style.display = match ? '' : 'none';
    });
    
    // Show "no results" message if no matches
    const visibleRows = table.querySelectorAll('tbody tr[style=""]').length;
    let noResultsRow = table.querySelector('.no-results-row');
    
    if (visibleRows === 0 && !noResultsRow) {
        noResultsRow = document.createElement('tr');
        noResultsRow.className = 'no-results-row';
        noResultsRow.innerHTML = `<td colspan="100%" class="text-center py-4 text-muted">No results found</td>`;
        table.querySelector('tbody').appendChild(noResultsRow);
    } else if (visibleRows > 0 && noResultsRow) {
        noResultsRow.remove();
    }
}

// Loading states
function showLoading(element, message = 'Loading...') {
    const originalContent = element.innerHTML;
    element.setAttribute('data-original-content', originalContent);
    element.innerHTML = `<span class="loading-spinner"></span> ${message}`;
    element.disabled = true;
}

function hideLoading(element) {
    const originalContent = element.getAttribute('data-original-content');
    if (originalContent) {
        element.innerHTML = originalContent;
        element.removeAttribute('data-original-content');
    }
    element.disabled = false;
}

// Print functionality
function printReceipt() {
    window.print();
}

// Export functionality (if needed)
function exportToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    for (let i = 0; i < rows.length; i++) {
        const row = [];
        const cols = rows[i].querySelectorAll('td, th');
        
        for (let j = 0; j < cols.length; j++) {
            let cellText = cols[j].innerText.replace(/"/g, '""');
            row.push('"' + cellText + '"');
        }
        csv.push(row.join(','));
    }
    
    // Download CSV
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

// Theme and preferences
function toggleTheme() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.body.setAttribute('data-theme', savedTheme);
}

// Initialize theme on load
loadTheme();

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + P for print (on receipt page)
    if ((e.ctrlKey || e.metaKey) && e.key === 'p' && window.location.pathname.includes('/receipt/')) {
        e.preventDefault();
        printReceipt();
    }
    
    // Escape key to close modals
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) bsModal.hide();
        });
    }
});

// Progressive Web App support
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // Service worker would be registered here for PWA functionality
        console.log('PWA support available');
    });
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
    // In production, you might want to send errors to a logging service
});

// Resize handler for responsive adjustments
let resizeTimer;
window.addEventListener('resize', function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function() {
        // Handle responsive layout adjustments
        adjustLayoutForScreenSize();
    }, 250);
});

function adjustLayoutForScreenSize() {
    const isMobile = window.innerWidth < 768;
    const cards = document.querySelectorAll('.metric-card');
    
    cards.forEach(card => {
        if (isMobile) {
            card.classList.add('mobile-layout');
        } else {
            card.classList.remove('mobile-layout');
        }
    });
}

// Initialize on load
adjustLayoutForScreenSize();

console.log('NEXGEN Study Centre - JavaScript initialized successfully');
