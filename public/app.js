// Screen Elements
const loginScreen = document.getElementById('login-screen');
const signupScreen = document.getElementById('signup-screen');
const studentMenu = document.getElementById('student-menu');
const kitchenDashboard = document.getElementById('kitchen-dashboard');
const receiptModal = document.getElementById('receipt-modal');
const mpesaModal = document.getElementById('mpesa-modal');
const mpesaAmount = document.getElementById('mpesa-amount');
const mpesaFormSection = document.getElementById('mpesa-form-section');
const mpesaProcessingSection = document.getElementById('mpesa-processing-section');

// --- Persistent Client Database (Dual-layer for Vercel & Offline Resilience) ---
const LocalDB = {
    KEY: 'kca_dining_users_db',
    getUsers() {
        try {
            const raw = localStorage.getItem(this.KEY);
            if (raw) return JSON.parse(raw);
            const initialUsers = [
                {
                    id: 'demo-1',
                    name: 'Alex Kiprop',
                    studentId: 'KCA/1234/23',
                    password: 'password123',
                    createdAt: new Date().toISOString()
                }
            ];
            localStorage.setItem(this.KEY, JSON.stringify(initialUsers));
            return initialUsers;
        } catch (e) {
            return [];
        }
    },
    saveUsers(users) {
        try {
            localStorage.setItem(this.KEY, JSON.stringify(users));
        } catch (e) {
            console.error("LocalDB save failed", e);
        }
    },
    findUser(studentId) {
        const users = this.getUsers();
        const norm = (studentId || '').trim().toUpperCase();
        return users.find(u => (u.studentId || '').trim().toUpperCase() === norm);
    },
    createUser(name, studentId, password) {
        const users = this.getUsers();
        const norm = (studentId || '').trim().toUpperCase();
        if (users.some(u => (u.studentId || '').trim().toUpperCase() === norm)) {
            return { error: `An account with Student ID '${studentId}' already exists.` };
        }
        const newUser = {
            id: 'usr_' + Date.now(),
            name: name.trim(),
            studentId: studentId.trim(),
            password: password,
            createdAt: new Date().toISOString()
        };
        users.push(newUser);
        this.saveUsers(users);
        return { success: true, user: newUser };
    },
    authenticate(studentId, password) {
        const user = this.findUser(studentId);
        if (!user) {
            return { error: `No account found with Student ID '${studentId}'. Please create an account first!` };
        }
        if (user.password !== password) {
            return { error: 'Incorrect password. Please try again.' };
        }
        const token = 'local_token_' + btoa(JSON.stringify({ id: user.id, name: user.name, studentId: user.studentId, time: Date.now() }));
        return { success: true, token, name: user.name, studentId: user.studentId };
    }
};

// --- Auth Logic ---

let currentStudentName = 'Student';
let authToken = localStorage.getItem('kca_token');

function updateGreeting(nameInput) {
    const greetingEl = document.getElementById('user-greeting-name');
    const welcomeNameEl = document.getElementById('welcome-name-display');
    if (nameInput && nameInput.trim() !== '') {
        currentStudentName = nameInput.trim();
        if (greetingEl) greetingEl.innerText = currentStudentName;
        const firstName = currentStudentName.split(' ')[0];
        if (welcomeNameEl) welcomeNameEl.innerText = firstName;
    } else {
        currentStudentName = 'Student';
        if (greetingEl) greetingEl.innerText = 'Student';
        if (welcomeNameEl) welcomeNameEl.innerText = 'Student';
    }
}

// Password visibility toggle
function togglePassword(inputId, iconEl) {
    const input = document.getElementById(inputId);
    if (!input) return;
    if (input.type === 'password') {
        input.type = 'text';
    } else {
        input.type = 'password';
    }
}

// Auto-login if token exists
async function checkAuthOnLoad() {
    if (!authToken) return;
    const cachedName = localStorage.getItem('kca_user_name');

    if (authToken.startsWith('local_token_')) {
        updateGreeting(cachedName || 'Student');
        loginScreen.style.display = 'none';
        studentMenu.style.display = 'flex';
        return;
    }

    try {
        const res = await fetch('/api/me', {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (res.ok) {
            const data = await res.json();
            updateGreeting(data.name);
            localStorage.setItem('kca_user_name', data.name);
            loginScreen.style.display = 'none';
            studentMenu.style.display = 'flex';
        } else {
            localStorage.removeItem('kca_token');
            localStorage.removeItem('kca_user_name');
            authToken = null;
        }
    } catch (err) {
        // Fallback for static hosting / offline
        if (cachedName) {
            updateGreeting(cachedName);
            loginScreen.style.display = 'none';
            studentMenu.style.display = 'flex';
        }
    }
}
checkAuthOnLoad();

// Login button handler
document.getElementById('login-btn').addEventListener('click', async () => {
    const studentIdInput = document.getElementById('student-id').value.trim();
    const passwordInput = document.getElementById('password').value;
    const loginBtn = document.getElementById('login-btn');
    
    if (!studentIdInput || !passwordInput) {
        showToast("Please enter both Student ID and Password", true);
        return;
    }

    const originalBtnText = loginBtn.innerText;
    loginBtn.innerText = "Signing In...";
    loginBtn.disabled = true;

    try {
        let loggedIn = false;
        try {
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ studentId: studentIdInput, password: passwordInput })
            });

            if (res.ok) {
                const data = await res.json();
                localStorage.setItem('kca_token', data.token);
                localStorage.setItem('kca_user_name', data.name);
                authToken = data.token;
                updateGreeting(data.name);
                loginScreen.style.display = 'none';
                studentMenu.style.display = 'flex';
                showToast(`Welcome back, ${data.name}!`);
                loggedIn = true;
            } else if (res.status === 400 || res.status === 401) {
                const data = await res.json().catch(() => ({}));
                showToast(data.error || "Incorrect credentials", true);
                loggedIn = true; // handled by server response
            }
        } catch (fetchErr) {
            // Server offline or static hosting fallback
        }

        if (!loggedIn) {
            // Local database fallback
            const authResult = LocalDB.authenticate(studentIdInput, passwordInput);
            if (authResult.success) {
                localStorage.setItem('kca_token', authResult.token);
                localStorage.setItem('kca_user_name', authResult.name);
                authToken = authResult.token;
                updateGreeting(authResult.name);
                loginScreen.style.display = 'none';
                studentMenu.style.display = 'flex';
                showToast(`Welcome, ${authResult.name}!`);
            } else {
                showToast(authResult.error, true);
            }
        }
    } finally {
        loginBtn.innerText = originalBtnText;
        loginBtn.disabled = false;
    }
});

// Navigation between Login and Sign Up
document.getElementById('signup-link').addEventListener('click', (e) => {
    e.preventDefault();
    loginScreen.style.display = 'none';
    signupScreen.style.display = 'flex';
    document.getElementById('signup-name').focus();
});

document.getElementById('back-to-login-link').addEventListener('click', (e) => {
    e.preventDefault();
    signupScreen.style.display = 'none';
    loginScreen.style.display = 'flex';
    document.getElementById('student-id').focus();
});

// Account Creation (Sign Up) handler
document.getElementById('create-account-btn').addEventListener('click', async () => {
    const signupName = document.getElementById('signup-name').value.trim();
    const signupId = document.getElementById('signup-id').value.trim();
    const signupPassword = document.getElementById('signup-password').value;
    const createBtn = document.getElementById('create-account-btn');
    
    if (!signupName || !signupId || !signupPassword) {
        showToast("Please fill in all fields to create an account", true);
        return;
    }

    if (signupPassword.length < 4) {
        showToast("Password must be at least 4 characters long", true);
        return;
    }

    const originalBtnText = createBtn.innerText;
    createBtn.innerText = "Creating Account...";
    createBtn.disabled = true;

    try {
        let created = false;
        try {
            const res = await fetch('/api/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: signupName, studentId: signupId, password: signupPassword })
            });

            if (res.ok) {
                LocalDB.createUser(signupName, signupId, signupPassword);
                showToast("Account created successfully! Please sign in.");
                created = true;
            } else if (res.status === 400 || res.status === 409) {
                const data = await res.json().catch(() => ({}));
                showToast(data.error || "An account with this ID already exists", true);
                created = true;
                return;
            }
        } catch (fetchErr) {
            // Server offline or static hosting fallback
        }

        if (!created) {
            const localResult = LocalDB.createUser(signupName, signupId, signupPassword);
            if (localResult.error) {
                showToast(localResult.error, true);
                return;
            }
            showToast("Account created in database! Please sign in.");
        }

        // Switch back to login screen with studentId pre-filled
        signupScreen.style.display = 'none';
        loginScreen.style.display = 'flex';
        document.getElementById('student-id').value = signupId;
        document.getElementById('password').value = '';
        document.getElementById('signup-name').value = '';
        document.getElementById('signup-id').value = '';
        document.getElementById('signup-password').value = '';
        document.getElementById('password').focus();
    } finally {
        createBtn.innerText = originalBtnText;
        createBtn.disabled = false;
    }
});

// Sign Out button handler
document.getElementById('student-signout-btn')?.addEventListener('click', () => {
    localStorage.removeItem('kca_token');
    localStorage.removeItem('kca_user_name');
    authToken = null;
    currentStudentName = 'Student';
    updateGreeting('Student');
    studentMenu.style.display = 'none';
    loginScreen.style.display = 'flex';
    document.getElementById('password').value = '';
    showToast("Signed out successfully");
});

// --- Toast Notification Helper ---
function showToast(msg, isError = false) {
    let toast = document.getElementById('app-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'app-toast';
        toast.className = 'toast-notification';
        document.body.appendChild(toast);
    }
    toast.innerHTML = `<span>${isError ? '⚠️' : '🍽️'}</span> ${msg}`;
    if (isError) {
        toast.style.background = '#B91C1C';
    } else {
        toast.style.background = '';
    }
    toast.classList.add('show');
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => {
        toast.classList.remove('show');
    }, 3200);
}

// --- Cart Logic ---
let cartTotal = 0;
let cartItemsCount = 0;
let cartItems = {};

function updateCartUI() {
    const totalEl = document.getElementById('cart-total-amount');
    const badgeEl = document.getElementById('cart-badge');
    const countLabelEl = document.getElementById('cart-items-count-label');
    const dock = document.getElementById('sticky-cart-bar');

    if (totalEl) totalEl.innerText = cartTotal;
    if (badgeEl) badgeEl.innerText = cartItemsCount;
    if (countLabelEl) countLabelEl.innerText = cartItemsCount;

    // Show floating dock only when items are in cart
    if (dock) {
        if (cartItemsCount > 0) {
            dock.classList.add('active');
        } else {
            dock.classList.remove('active');
        }
    }

    // Animate badge
    if (badgeEl) {
        badgeEl.style.transform = 'scale(1.35)';
        setTimeout(() => {
            badgeEl.style.transform = 'scale(1)';
        }, 200);
    }
}

function addToCart(name, price) {
    cartTotal += price;
    cartItemsCount++;

    if (cartItems[name]) {
        cartItems[name].count++;
    } else {
        cartItems[name] = { price: price, count: 1 };
    }

    // Visual button feedback
    try {
        const activeBtn = event?.currentTarget || event?.target;
        if (activeBtn && activeBtn.classList?.contains('btn-add')) {
            const originalText = activeBtn.innerText;
            activeBtn.innerText = `✓ Added (${cartItems[name].count})`;
            activeBtn.style.background = '#10B981';
            activeBtn.style.borderColor = '#10B981';
            activeBtn.style.color = '#ffffff';
            setTimeout(() => {
                activeBtn.innerText = `+ Add (${cartItems[name].count})`;
                activeBtn.style.background = '';
                activeBtn.style.borderColor = '';
                activeBtn.style.color = '';
            }, 1200);
        }
    } catch (e) {}

    showToast(`Added ${name} (KES ${price}) to tray!`);
    updateCartUI();
}

// --- Checkout Logic ---
document.getElementById('checkout-btn').addEventListener('click', () => {
    if (cartTotal === 0) {
        showToast("Your meal tray is empty! Click '+ Add' on any dish to get started.");
        return;
    }

    // Set amount in modal and cash reference
    mpesaAmount.innerText = cartTotal;
    document.querySelectorAll('.cash-amount-ref').forEach(el => el.innerText = cartTotal);

    // Reset to first tab
    switchPayTab(document.querySelector('.pay-tab[data-method="mpesa"]'), 'mpesa-panel');

    mpesaFormSection.style.display = 'block';
    mpesaProcessingSection.style.display = 'none';
    mpesaModal.style.display = 'flex';
});

// Tab switching
function switchPayTab(clickedTab, panelId) {
    // Deactivate all tabs
    document.querySelectorAll('.pay-tab').forEach(t => t.classList.remove('active'));
    // Hide all panels
    document.querySelectorAll('.pay-panel').forEach(p => p.style.display = 'none');
    // Activate clicked
    clickedTab.classList.add('active');
    document.getElementById(panelId).style.display = 'block';
}

document.getElementById('mpesa-cancel-btn').addEventListener('click', () => {
    mpesaModal.style.display = 'none';
    // Clear phone fields on cancel
    document.getElementById('mpesa-phone').value = '';
    document.getElementById('airtel-phone').value = '';
    document.getElementById('card-number').value = '';
    document.getElementById('card-expiry').value = '';
    document.getElementById('card-cvv').value = '';
});

// --- Shared receipt helper ---
function showReceipt() {
    const receiptList = document.getElementById('receipt-items-list');
    receiptList.innerHTML = '';
    for (let itemName in cartItems) {
        let item = cartItems[itemName];
        let li = document.createElement('li');
        li.innerHTML = `<span>${item.count}x ${itemName}</span> <span>KES ${item.price * item.count}</span>`;
        receiptList.appendChild(li);
    }
    document.getElementById('receipt-total-amount').innerText = cartTotal;
    receiptModal.style.display = 'flex';
}

// --- M-Pesa Pay ---
document.getElementById('mpesa-pay-btn').addEventListener('click', () => {
    const digits = document.getElementById('mpesa-phone').value.trim();
    if (!digits || digits.length < 9) {
        alert("Please enter a valid Safaricom number (9 digits after +254).");
        return;
    }

    document.getElementById('processing-title').innerText = 'Waiting for M-Pesa';
    document.getElementById('processing-msg').innerText = 'Check your phone and enter your M-PESA PIN to confirm.';
    mpesaFormSection.style.display = 'none';
    mpesaProcessingSection.style.display = 'block';

    setTimeout(() => {
        mpesaModal.style.display = 'none';
        showReceipt();
    }, 4000);
});

// --- Airtel Money Pay ---
document.getElementById('airtel-pay-btn').addEventListener('click', () => {
    const digits = document.getElementById('airtel-phone').value.trim();
    if (!digits || digits.length < 9) {
        alert("Please enter a valid Airtel number (9 digits after +254).");
        return;
    }

    document.getElementById('processing-title').innerText = 'Waiting for Airtel Money';
    document.getElementById('processing-msg').innerText = 'Check your phone and approve the Airtel Money request.';
    mpesaFormSection.style.display = 'none';
    mpesaProcessingSection.style.display = 'block';

    setTimeout(() => {
        mpesaModal.style.display = 'none';
        showReceipt();
    }, 4000);
});

// --- Card Pay ---
document.getElementById('card-pay-btn').addEventListener('click', () => {
    const cardNum = document.getElementById('card-number').value.trim();
    const expiry = document.getElementById('card-expiry').value.trim();
    const cvv = document.getElementById('card-cvv').value.trim();
    
    if (!cardNum || !expiry || !cvv) {
        alert("Please fill in all card details.");
        return;
    }

    document.getElementById('processing-title').innerText = 'Processing Card Payment';
    document.getElementById('processing-msg').innerText = 'Please wait while we process your transaction.';
    mpesaFormSection.style.display = 'none';
    mpesaProcessingSection.style.display = 'block';

    setTimeout(() => {
        mpesaModal.style.display = 'none';
        showReceipt();
    }, 4000);
});

// --- Cash Pay ---
document.getElementById('cash-confirm-btn').addEventListener('click', () => {
    document.getElementById('processing-title').innerText = 'Order Confirmed!';
    document.getElementById('processing-msg').innerText = 'Please pay KES ' + cartTotal + ' at the counter when collecting your order.';
    mpesaFormSection.style.display = 'none';
    mpesaProcessingSection.style.display = 'block';

    setTimeout(() => {
        mpesaModal.style.display = 'none';
        showReceipt();
    }, 2000);
});

document.getElementById('close-receipt-btn').addEventListener('click', () => {
    receiptModal.style.display = 'none';

    // Snapshot cart BEFORE clearing it, so kitchen sees real items
    const snapshotItems = { ...cartItems };
    const snapshotName = currentStudentName;

    // Reset cart
    cartTotal = 0;
    cartItemsCount = 0;
    cartItems = {};
    updateCartUI();

    // Build the kitchen order from snapshot
    buildKitchenOrder(snapshotItems, snapshotName);

    // Switch to kitchen dashboard
    studentMenu.style.display = 'none';
    kitchenDashboard.style.display = 'flex';
});

// --- Kitchen Dashboard: Build Order from Current Student ---
let orderCounter = Math.floor(Math.random() * 900) + 1100; // random starting order number

function buildKitchenOrder(snapshotItems, studentName) {
    const section = document.getElementById('live-orders-section');
    const noOrdersMsg = document.getElementById('no-orders-msg');

    // Clear any old orders
    section.innerHTML = '';
    section.appendChild(noOrdersMsg);

    if (!snapshotItems || Object.keys(snapshotItems).length === 0) {
        noOrdersMsg.style.display = 'block';
        return;
    }

    noOrdersMsg.style.display = 'none';

    // Build order details string
    const orderDetailParts = [];
    for (let itemName in snapshotItems) {
        const item = snapshotItems[itemName];
        orderDetailParts.push(`${item.count}x ${itemName}`);
    }

    // Create order card
    const orderNumber = orderCounter++;
    const card = document.createElement('div');
    card.className = 'order-card';
    card.innerHTML = `
        <div class="order-header">
            <h4>Order #${orderNumber}</h4>
            <span class="customer-name">${studentName}</span>
        </div>
        <p class="order-details">${orderDetailParts.join(', ')}</p>
        <button class="btn-status status-preparing" onclick="toggleOrderStatus(this)">Preparing</button>
    `;
    section.appendChild(card);
}

// --- Kitchen Dashboard Logic ---

function toggleOrderStatus(btn) {
    if (btn.classList.contains('status-preparing')) {
        btn.classList.remove('status-preparing');
        btn.classList.add('status-ready');
        btn.innerText = '✓ Ready for Pickup';
    } else {
        btn.classList.remove('status-ready');
        btn.classList.add('status-preparing');
        btn.innerText = 'Preparing';
    }
}

// Return to menu from kitchen
document.getElementById('logout-btn').addEventListener('click', () => {
    kitchenDashboard.style.display = 'none';
    studentMenu.style.display = 'flex';
});

// Category pills logic
const pills = document.querySelectorAll('.pill');
const foodCards = document.querySelectorAll('.food-card');

pills.forEach(pill => {
    pill.addEventListener('click', () => {
        pills.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');

        const filter = pill.getAttribute('data-filter');
        foodCards.forEach(card => {
            if (filter === 'all' || card.getAttribute('data-category') === filter) {
                card.style.display = 'flex';
            } else {
                card.style.display = 'none';
            }
        });
    });
});

// Live Search Filter for Laptop View
const searchInput = document.getElementById('menu-search-input');
if (searchInput) {
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        foodCards.forEach(card => {
            const title = card.querySelector('h3')?.innerText.toLowerCase() || '';
            const desc = card.querySelector('.food-desc')?.innerText.toLowerCase() || '';
            const category = card.getAttribute('data-category')?.toLowerCase() || '';
            if (!query || title.includes(query) || desc.includes(query) || category.includes(query)) {
                card.style.display = 'flex';
            } else {
                card.style.display = 'none';
            }
        });
    });
}
