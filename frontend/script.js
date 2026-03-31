// Utility to show notification
function showNotification(message, type) {
    const notifElement = document.getElementById('notification');
    if (notifElement) {
        notifElement.textContent = message;
        notifElement.className = `notification ${type}`;
        
        // Hide after 3 seconds
        setTimeout(() => {
            notifElement.className = 'notification';
            notifElement.textContent = '';
        }, 3000);
    }
}

// Handle Login
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const btn = loginForm.querySelector('.btn');
        
        btn.textContent = 'Signing in...';
        btn.disabled = true;

        try {
            const response = await fetch('http://localhost:8000/login/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            
            const data = await response.json();

            if (response.ok) {
                showNotification('Login successful! Redirecting...', 'success');
                localStorage.setItem('access_token', data.access);
                localStorage.setItem('refresh_token', data.refresh);
                window.location.href = 'dashboard.html';
            } else {
                throw new Error(data.detail || 'Invalid credentials');
            }
        } catch (error) {
            showNotification(error.message || 'Login failed', 'error');
        } finally {
            btn.textContent = 'Sign In';
            btn.disabled = false;
        }
    });
}

// Handle Registration
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const role = document.getElementById('role').value;
        const btn = registerForm.querySelector('.btn');
        
        btn.textContent = 'Creating account...';
        btn.disabled = true;

        try {
            const response = await fetch('http://localhost:8000/register/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password, role })
            });
            
            const data = await response.json();

            if (response.ok) {
                showNotification('Registration successful! Please login.', 'success');
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 1500);
            } else {
                // If the error response contains form fields, format them
                let errorMsg = 'Registration failed';
                if (data && typeof data === 'object') {
                    errorMsg = Object.values(data).map(err => Array.isArray(err) ? err[0] : err).join(' ');
                }
                throw new Error(errorMsg);
            }
        } catch (error) {
            showNotification(error.message || 'Registration failed', 'error');
        } finally {
            btn.textContent = 'Sign Up';
            btn.disabled = false;
        }
    });
}
