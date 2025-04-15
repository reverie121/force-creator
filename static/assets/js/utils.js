// Utility to get CSRF token from meta tag
function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}
// utils.js
// Debounce utility to limit rapid function calls
function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// Toggle expander icon based on collapse state
function toggleExpanderIcon(iconId, isExpanded) {
    const $icon = $(`#${iconId}`);
    if (isExpanded) {
        $icon.removeClass('fa-chevron-down').addClass('fa-chevron-up');
    } else {
        $icon.removeClass('fa-chevron-up').addClass('fa-chevron-down');
    }
}

// Debounced version for click handling
const debouncedToggleExpander = debounce((iconId) => {
    // No direct toggle here; rely on collapse events
}, 350); // Match Bootstrap's 350ms animation