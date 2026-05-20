// ==========================================
// MediCare Authentication System
// Using LocalStorage for user management
// ==========================================

// Initialize users array in LocalStorage if not exists
if (!localStorage.getItem('medAuthUsers')) {
    localStorage.setItem('medAuthUsers', JSON.stringify([]));
}

// ==========================================
// UTILITY FUNCTIONS
// ==========================================

// Show error message
function showError(message, type = 'error') {
    const errorDiv = document.getElementById('errorMessage');
    const successDiv = document.getElementById('successMessage');
    
    // Hide both first
    errorDiv.classList.remove('show');
    successDiv.classList.remove('show');
    
    if (type === 'error') {
        errorDiv.textContent = message;
        errorDiv.classList.add('show');
    } else if (type === 'success') {
        successDiv.textContent = message;
        successDiv.classList.add('show');
    } else if (type === 'info') {
        successDiv.textContent = message;
        successDiv.classList.add('show');
    }
    
    // Auto hide after 5 seconds
    setTimeout(() => {
        errorDiv.classList.remove('show');
        successDiv.classList.remove('show');
    }, 5000);
}

// Email validation
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Show loading state on button
function setButtonLoading(button, loading) {
    if (loading) {
        button.disabled = true;
        button.classList.add('loading');
        const originalText = button.querySelector('span').textContent;
        button.setAttribute('data-original-text', originalText);
        button.innerHTML = '<div class="spinner"></div>';
    } else {
        button.disabled = false;
        button.classList.remove('loading');
        const originalText = button.getAttribute('data-original-text');
        button.innerHTML = `
            <span>${originalText}</span>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="5" y1="12" x2="19" y2="12"/>
                <polyline points="12 5 19 12 12 19"/>
            </svg>
        `;
    }
}

// Get all users from LocalStorage
function getAllUsers() {
    const users = localStorage.getItem('medAuthUsers');
    return users ? JSON.parse(users) : [];
}

// Save users to LocalStorage
function saveUsers(users) {
    localStorage.setItem('medAuthUsers', JSON.stringify(users));
}

// Check if user is logged in
function checkAuth() {
    const currentUser = localStorage.getItem('currentUser');
    if (currentUser) {
        const user = JSON.parse(currentUser);
        return user;
    }
    return null;
}

// ==========================================
// SIGNUP FUNCTIONALITY
// ==========================================

function handleSignup(e) {
    e.preventDefault();
    
    // Get form elements
    const nameInput = document.getElementById('name');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const roleInput = document.querySelector('input[name="role"]:checked');
    const signupBtn = document.getElementById('signupBtn');
    
    // Get values
    const name = nameInput.value.trim();
    const email = emailInput.value.trim().toLowerCase();
    const password = passwordInput.value;
    const role = roleInput.value;
    
    // Validation
    if (!name || name.length < 2) {
        showError('Please enter a valid name (minimum 2 characters)');
        nameInput.focus();
        return;
    }
    
    if (!isValidEmail(email)) {
        showError('Please enter a valid email address');
        emailInput.focus();
        return;
    }
    
    if (!password || password.length < 6) {
        showError('Password must be at least 6 characters long');
        passwordInput.focus();
        return;
    }
    
    // Show loading
    setButtonLoading(signupBtn, true);
    
    // Simulate API delay
    setTimeout(() => {
        // Check if user already exists
        const users = getAllUsers();
        const existingUser = users.find(u => u.email === email);
        
        if (existingUser) {
            showError('An account with this email already exists. Please login.');
            setButtonLoading(signupBtn, false);
            return;
        }
        
        // Create new user object
        const newUser = {
            id: Date.now().toString(),
            name: name,
            email: email,
            password: password, // In production, this should be hashed!
            role: role,
            createdAt: new Date().toISOString()
        };
        
        // Add user to array
        users.push(newUser);
        saveUsers(users);
        
        // Show success message
        showError('Account created successfully! Redirecting to login...', 'success');
        
        // Reset form
        document.getElementById('signupForm').reset();
        setButtonLoading(signupBtn, false);
        
        // Redirect to login after 2 seconds
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 2000);
        
    }, 1500); // Simulated delay
}

// ==========================================
// LOGIN FUNCTIONALITY
// ==========================================

function handleLogin(e) {
    e.preventDefault();
    
    // Get form elements
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const loginBtn = document.getElementById('loginBtn');
    
    // Get values
    const email = emailInput.value.trim().toLowerCase();
    const password = passwordInput.value;
    
    // Validation
    if (!isValidEmail(email)) {
        showError('Please enter a valid email address');
        emailInput.focus();
        return;
    }
    
    if (!password) {
        showError('Please enter your password');
        passwordInput.focus();
        return;
    }
    
    // Show loading
    setButtonLoading(loginBtn, true);
    
    // Simulate API delay
    setTimeout(() => {
        // Find user
        const users = getAllUsers();
        const user = users.find(u => u.email === email && u.password === password);
        
        if (!user) {
            showError('Invalid email or password. Please try again.');
            setButtonLoading(loginBtn, false);
            return;
        }
        
        // Save current user session
        localStorage.setItem('currentUser', JSON.stringify(user));
        
        // Show success
        showError(`Welcome back, ${user.name}!`, 'success');
        
        // Redirect based on role
        setTimeout(() => {
            if (user.role === 'Doctor') {
                window.location.href = 'doctor-dashboard.html';
            } else {
                window.location.href = 'patient-dashboard.html';
            }
        }, 1500);
        
    }, 1500); // Simulated delay
}

// ==========================================
// LOGOUT FUNCTIONALITY
// ==========================================

function handleLogout() {
    // Clear current user
    localStorage.removeItem('currentUser');
    
    // Redirect to login
    window.location.href = 'login.html';
}

// ==========================================
// DASHBOARD FUNCTIONALITY
// ==========================================

function initializeDashboard() {
    // Check if user is logged in
    const currentUser = checkAuth();
    
    if (!currentUser) {
        // Redirect to login if not authenticated
        window.location.href = 'login.html';
        return;
    }
    
    // Get current page
    const currentPage = window.location.pathname.split('/').pop();
    
    // Verify user has access to this dashboard
    if (currentPage === 'doctor-dashboard.html' && currentUser.role !== 'Doctor') {
        window.location.href = 'patient-dashboard.html';
        return;
    }
    
    if (currentPage === 'patient-dashboard.html' && currentUser.role !== 'Patient') {
        window.location.href = 'doctor-dashboard.html';
        return;
    }
    
    // Update dashboard with user info
    const userNameElement = document.getElementById('userName');
    const userEmailElement = document.getElementById('userEmail');
    const userRoleElement = document.getElementById('userRole');
    const userAvatarElement = document.getElementById('userAvatar');
    
    if (userNameElement) userNameElement.textContent = currentUser.name;
    if (userEmailElement) userEmailElement.textContent = currentUser.email;
    if (userRoleElement) userRoleElement.textContent = currentUser.role;
    if (userAvatarElement) {
        // Set avatar initials
        const initials = currentUser.name
            .split(' ')
            .map(n => n[0])
            .join('')
            .toUpperCase()
            .substring(0, 2);
        userAvatarElement.textContent = initials;
    }
    
    // Attach logout handler
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
}

// ==========================================
// AUTO-INITIALIZE ON PAGE LOAD
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    const currentPage = window.location.pathname.split('/').pop();
    
    // Initialize dashboard if on dashboard page
    if (currentPage === 'doctor-dashboard.html' || currentPage === 'patient-dashboard.html') {
        initializeDashboard();
    }
    
    // Redirect to appropriate dashboard if already logged in and on login/signup page
    if (currentPage === 'login.html' || currentPage === 'signup.html') {
        const currentUser = checkAuth();
        if (currentUser) {
            if (currentUser.role === 'Doctor') {
                window.location.href = 'doctor-dashboard.html';
            } else {
                window.location.href = 'patient-dashboard.html';
            }
        }
    }
});