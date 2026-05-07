// Auth Page Logic

function toggleForms() {
    document.getElementById('loginForm').classList.toggle('active-form');
    document.getElementById('signupForm').classList.toggle('active-form');
    clearMessage();
}

function showMessage(text, type = 'error') {
    const messageEl = document.getElementById('message');
    messageEl.textContent = text;
    messageEl.className = `message ${type}`;
    setTimeout(() => {
        messageEl.className = 'message';
    }, 5000);
}

function clearMessage() {
    document.getElementById('message').className = 'message';
}

// Login Form Handler
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;

    if (!username || !password) {
        showMessage('Please enter username and password', 'error');
        return;
    }

    try {
        const result = await login(username, password);
        showMessage('Login successful!', 'success');
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 500);
    } catch (error) {
        showMessage(error.message || 'Login failed', 'error');
    }
});

// Signup Form Handler
document.getElementById('signupForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('signupUsername').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    const passwordConfirm = document.getElementById('signupPasswordConfirm').value;

    if (!username || !password) {
        showMessage('Please enter username and password', 'error');
        return;
    }

    if (username.length < 3) {
        showMessage('Username must be at least 3 characters', 'error');
        return;
    }

    if (password.length < 6) {
        showMessage('Password must be at least 6 characters', 'error');
        return;
    }

    if (password !== passwordConfirm) {
        showMessage('Passwords do not match', 'error');
        return;
    }

    try {
        const result = await signup(username, password, email || null);
        showMessage('Account created successfully! Redirecting...', 'success');
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 500);
    } catch (error) {
        showMessage(error.message || 'Signup failed', 'error');
    }
});
