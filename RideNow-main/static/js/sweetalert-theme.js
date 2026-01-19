/**
 * SweetAlert2 Theme Configuration for RideNow
 * Removes purple colors and applies project theme colors
 */

// SweetAlert2 Theme Configuration
const sweetAlertTheme = {
    // Color scheme based on project theme
    colors: {
        primary: '#008080',      // Teal (primary brand color)
        secondary: '#1C39BB',    // Persian blue
        accent: '#98FF98',       // Mint green
        success: '#21c45d',      // Green for success
        warning: '#f59e0b',      // Amber for warnings
        error: '#ef4444',        // Red for errors
        info: '#3b82f6',         // Blue for info
        cancel: '#6b7280',       // Gray for cancel buttons
        confirm: '#008080'       // Teal for confirm buttons
    },
    
    // Default configuration for all SweetAlert calls
    defaultConfig: {
        confirmButtonColor: '#008080',
        cancelButtonColor: '#6b7280',
        buttonsStyling: true,
        customClass: {
            confirmButton: 'swal2-confirm-custom',
            cancelButton: 'swal2-cancel-custom',
            popup: 'swal2-popup-custom'
        }
    }
};

// Enhanced SweetAlert wrapper functions
window.SweetAlert = {
    // Success alert with teal confirm button
    success: (title, text, options = {}) => {
        return Swal.fire({
            title: title,
            text: text,
            icon: 'success',
            confirmButtonColor: sweetAlertTheme.colors.success,
            confirmButtonText: options.confirmText || 'OK',
            timer: options.timer || null,
            showConfirmButton: options.showConfirmButton !== false,
            ...sweetAlertTheme.defaultConfig,
            ...options
        });
    },
    
    // Error alert with red confirm button
    error: (title, text, options = {}) => {
        return Swal.fire({
            title: title,
            text: text,
            icon: 'error',
            confirmButtonColor: sweetAlertTheme.colors.error,
            confirmButtonText: options.confirmText || 'OK',
            ...sweetAlertTheme.defaultConfig,
            ...options
        });
    },
    
    // Warning alert with amber confirm button
    warning: (title, text, options = {}) => {
        return Swal.fire({
            title: title,
            text: text,
            icon: 'warning',
            confirmButtonColor: sweetAlertTheme.colors.warning,
            confirmButtonText: options.confirmText || 'OK',
            ...sweetAlertTheme.defaultConfig,
            ...options
        });
    },
    
    // Info alert with blue confirm button
    info: (title, text, options = {}) => {
        return Swal.fire({
            title: title,
            text: text,
            icon: 'info',
            confirmButtonColor: sweetAlertTheme.colors.info,
            confirmButtonText: options.confirmText || 'OK',
            ...sweetAlertTheme.defaultConfig,
            ...options
        });
    },
    
    // Confirmation dialog with teal confirm and gray cancel
    confirm: (title, text, options = {}) => {
        return Swal.fire({
            title: title,
            text: text,
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: sweetAlertTheme.colors.confirm,
            cancelButtonColor: sweetAlertTheme.colors.cancel,
            confirmButtonText: options.confirmText || 'Yes',
            cancelButtonText: options.cancelText || 'No',
            ...sweetAlertTheme.defaultConfig,
            ...options
        });
    },
    
    // Custom alert with full control
    custom: (options = {}) => {
        return Swal.fire({
            ...sweetAlertTheme.defaultConfig,
            ...options
        });
    }
};

// Add CSS to override SweetAlert2 default purple colors
const sweetAlertStyle = document.createElement('style');
sweetAlertStyle.textContent = `
    /* Override SweetAlert2 default purple colors */
    .swal2-popup {
        background-color: #ffffff !important;
    }
    
    .swal2-confirm {
        background-color: #008080 !important;
        border-color: #008080 !important;
    }
    
    .swal2-confirm:hover {
        background-color: #006666 !important;
        border-color: #006666 !important;
    }
    
    .swal2-confirm:focus {
        box-shadow: 0 0 0 3px rgba(0, 128, 128, 0.3) !important;
    }
    
    .swal2-cancel {
        background-color: #6b7280 !important;
        border-color: #6b7280 !important;
    }
    
    .swal2-cancel:hover {
        background-color: #4b5563 !important;
        border-color: #4b5563 !important;
    }
    
    .swal2-cancel:focus {
        box-shadow: 0 0 0 3px rgba(107, 114, 128, 0.3) !important;
    }
    
    /* Success icon color */
    .swal2-success .swal2-success-ring {
        border-color: #21c45d !important;
    }
    
    .swal2-success [class^=swal2-success-line] {
        background-color: #21c45d !important;
    }
    
    /* Error icon color */
    .swal2-error .swal2-error-line {
        background-color: #ef4444 !important;
    }
    
    /* Warning icon color */
    .swal2-warning {
        border-color: #f59e0b !important;
        color: #f59e0b !important;
    }
    
    /* Info icon color */
    .swal2-info {
        border-color: #3b82f6 !important;
        color: #3b82f6 !important;
    }
    
    /* Custom button classes for additional styling */
    .swal2-confirm-custom {
        font-weight: 600 !important;
        border-radius: 6px !important;
    }
    
    .swal2-cancel-custom {
        font-weight: 600 !important;
        border-radius: 6px !important;
    }
    
    .swal2-popup-custom {
        border-radius: 12px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15) !important;
    }
`;

document.head.appendChild(sweetAlertStyle);

// Make SweetAlert available globally
window.sweetAlertTheme = sweetAlertTheme;

window.showToast = (message, type) => {
    Swal.fire({
        title: message,
        icon: type,
        timer: 3000
    });
};