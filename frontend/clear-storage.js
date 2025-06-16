// Clear localStorage for X-Cost frontend
// Run this in the browser console if needed

console.log('Clearing X-Cost localStorage...');

// Clear all localStorage
localStorage.clear();

// Clear all sessionStorage
sessionStorage.clear();

// Clear all cookies for the current domain
document.cookie.split(";").forEach(function(c) { 
    document.cookie = c.replace(/^ +/, "")
        .replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); 
});

console.log('Storage cleared successfully!');
console.log('Please refresh the page to restart the application.');