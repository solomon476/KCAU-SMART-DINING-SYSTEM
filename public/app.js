// ==========================================================================
// KCAU SMART DINING SYSTEM - Client Application (CAT 1 Architecture)
// Connects to Java Backend with SQLite & LocalDB Fallback
// ==========================================================================

// Screen Elements
const loginScreen = document.getElementById('login-screen');
const signupScreen = document.getElementById('signup-screen');
const studentMenu = document.getElementById('student-menu');
const kitchenDashboard = document.getElementById('kitchen-dashboard');
const adminDashboard = document.getElementById('admin-dashboard');

const receiptModal = document.getElementById('receipt-modal');
const mpesaModal = document.getElementById('mpesa-modal');
const addDishModal = document.getElementById('add-dish-modal');
const mpesaAmount = document.getElementById('mpesa-amount');
const mpesaFormSection = document.getElementById('mpesa-form-section');
const mpesaProcessingSection = document.getElementById('mpesa-processing-section');

// Global Application State
let currentUser = null;
let currentRole = 'student';
let currentStudentName = 'Student';
let authToken = localStorage.getItem('kca_token');
let activeOrderId = localStorage.getItem('kca_active_order_id') || null;

let cartTotal = 0;
let cartItemsCount = 0;
let cartItems = {};
let backendMenuItems = [];
let kitchenOrdersList = [];
let kitchenPollInterval = null;
let currentKitchenFilter = 'ALL';

// --- LocalDB Fallback (Dual-layer for offline / Vercel Edge Resilience) ---
const LocalDB = {
    USERS_KEY: 'kca_dining_users_db',
    ORDERS_KEY: 'kca_dining_orders_db',
    PAYMENTS_KEY: 'kca_dining_payments_db',
    MENU_KEY: 'kca_dining_menu_db',

    getUsers() {
        try {
            const raw = localStorage.getItem(this.USERS_KEY);
            if (raw) return JSON.parse(raw);
            const initial = [
                { id: 'usr_student', name: 'Alex Kiprop', studentId: 'KCA/1234/23', password: 'password123', role: 'student' },
                { id: 'usr_staff', name: 'Chef James Omondi', studentId: 'STAFF/001', password: 'password123', role: 'staff' },
                { id: 'usr_admin', name: 'Dr. Jane Muthoni', studentId: 'ADMIN/001', password: 'password123', role: 'admin' }
            ];
            localStorage.setItem(this.USERS_KEY, JSON.stringify(initial));
            return initial;
        } catch (e) {
            return [];
        }
    },
    saveUsers(users) {
        try { localStorage.setItem(this.USERS_KEY, JSON.stringify(users)); } catch (e) {}
    },
    findUser(studentId) {
        const users = this.getUsers();
        const norm = (studentId || '').trim().toUpperCase();
        return users.find(u => (u.studentId || '').trim().toUpperCase() === norm);
    },
    createUser(name, studentId, password, role = 'student') {
        const users = this.getUsers();
        const norm = (studentId || '').trim().toUpperCase();
        if (users.some(u => (u.studentId || '').trim().toUpperCase() === norm)) {
            return { error: `An account with ID '${studentId}' already exists.` };
        }
        const newUser = {
            id: 'usr_' + Date.now(),
            name: name.trim(),
            studentId: studentId.trim(),
            password: password,
            role: role.toLowerCase(),
            createdAt: new Date().toISOString()
        };
        users.push(newUser);
        this.saveUsers(users);
        return { success: true, user: newUser };
    },
    authenticate(studentId, password) {
        const user = this.findUser(studentId);
        if (!user) return { error: `No account found with ID '${studentId}'. Please register first!` };
        if (user.password !== password) return { error: 'Incorrect password. Please try again.' };
        const token = 'local_token_' + btoa(JSON.stringify({ id: user.id, name: user.name, studentId: user.studentId, role: user.role, time: Date.now() }));
        return { success: true, token, name: user.name, studentId: user.studentId, role: user.role };
    },
    getOrders() {
        try {
            const raw = localStorage.getItem(this.ORDERS_KEY);
            return raw ? JSON.parse(raw) : [];
        } catch (e) { return []; }
    },
    saveOrder(order) {
        const orders = this.getOrders();
        orders.unshift(order);
        try { localStorage.setItem(this.ORDERS_KEY, JSON.stringify(orders)); } catch (e) {}
        return order;
    },
    updateOrderStatus(orderId, status) {
        const orders = this.getOrders();
        const ord = orders.find(o => o.orderId === orderId);
        if (ord) {
            ord.status = status;
            try { localStorage.setItem(this.ORDERS_KEY, JSON.stringify(orders)); } catch (e) {}
            return true;
        }
        return false;
    },
    getPayments() {
        try {
            const raw = localStorage.getItem(this.PAYMENTS_KEY);
            return raw ? JSON.parse(raw) : [];
        } catch (e) { return []; }
    },
    savePayment(payment) {
        const payments = this.getPayments();
        payments.unshift(payment);
        try { localStorage.setItem(this.PAYMENTS_KEY, JSON.stringify(payments)); } catch (e) {}
        return payment;
    }
};

// --- Quick Demo Account Fill Helper ---
window.quickFillLogin = function(studentId, password) {
    const idInput = document.getElementById('student-id');
    const passInput = document.getElementById('password');
    if (idInput) idInput.value = studentId;
    if (passInput) passInput.value = password;
    showToast(`Filled: ${studentId} (Role: ${studentId.includes('STAFF') ? 'Kitchen Staff' : studentId.includes('ADMIN') ? 'Administrator' : 'Student'})`);
};

// Password Visibility Toggle
window.togglePassword = function(inputId, iconEl) {
    const input = document.getElementById(inputId);
    if (!input) return;
    input.type = input.type === 'password' ? 'text' : 'password';
};

// Toast Notification
function showToast(msg, isError = false) {
    let toast = document.getElementById('app-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'app-toast';
        toast.className = 'toast-notification';
        document.body.appendChild(toast);
    }
    toast.innerHTML = `<span>${isError ? '⚠️' : '🍽️'}</span> ${msg}`;
    toast.style.background = isError ? '#B91C1C' : '#1E293B';
    toast.classList.add('show');
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => {
        toast.classList.remove('show');
    }, 3200);
}

// ==========================================================================
// Authentication & User Session Management
// ==========================================================================

function updateGreeting(name, role = 'student') {
    currentStudentName = name || 'Student';
    currentRole = (role || 'student').toLowerCase();

    const greetingEl = document.getElementById('user-greeting-name');
    const welcomeNameEl = document.getElementById('welcome-name-display');
    const roleBadgeEl = document.getElementById('user-role-badge');

    if (greetingEl) greetingEl.innerText = currentStudentName;
    if (welcomeNameEl) welcomeNameEl.innerText = currentStudentName.split(' ')[0];

    if (roleBadgeEl) {
        roleBadgeEl.innerText = currentRole.toUpperCase();
        roleBadgeEl.className = `role-badge role-${currentRole}`;
    }

    // Configure header switcher visibility based on role
    const kitchenBtn = document.getElementById('student-to-kitchen-btn');
    const adminBtn = document.getElementById('student-to-admin-btn');
    const kitchenAdminBtn = document.getElementById('kitchen-to-admin-btn');

    if (kitchenBtn) kitchenBtn.style.display = (currentRole === 'staff' || currentRole === 'admin') ? 'inline-flex' : 'none';
    if (adminBtn) adminBtn.style.display = (currentRole === 'admin') ? 'inline-flex' : 'none';
    if (kitchenAdminBtn) kitchenAdminBtn.style.display = (currentRole === 'admin') ? 'inline-flex' : 'none';
}

// Portal Navigation Switcher
window.showPortal = function(portalName) {
    if (loginScreen) loginScreen.style.display = 'none';
    if (signupScreen) signupScreen.style.display = 'none';
    if (studentMenu) studentMenu.style.display = 'none';
    if (kitchenDashboard) kitchenDashboard.style.display = 'none';
    if (adminDashboard) adminDashboard.style.display = 'none';

    clearInterval(kitchenPollInterval);

    if (portalName === 'menu') {
        studentMenu.style.display = 'flex';
        loadMenuFromBackend();
        checkActiveOrderStatus();
    } else if (portalName === 'kitchen') {
        kitchenDashboard.style.display = 'flex';
        fetchKitchenOrders();
        // Start live polling every 4 seconds
        kitchenPollInterval = setInterval(fetchKitchenOrders, 4000);
    } else if (portalName === 'admin') {
        adminDashboard.style.display = 'flex';
        fetchAdminDashboard();
    }
};

window.handleSignOut = function() {
    localStorage.removeItem('kca_token');
    localStorage.removeItem('kca_user_name');
    localStorage.removeItem('kca_user_role');
    authToken = null;
    currentUser = null;
    currentRole = 'student';
    currentStudentName = 'Student';

    clearInterval(kitchenPollInterval);

    if (studentMenu) studentMenu.style.display = 'none';
    if (kitchenDashboard) kitchenDashboard.style.display = 'none';
    if (adminDashboard) adminDashboard.style.display = 'none';
    if (loginScreen) loginScreen.style.display = 'flex';

    showToast("Signed out successfully");
};

document.getElementById('student-signout-btn')?.addEventListener('click', window.handleSignOut);

// Check Authentication Session on Page Load
async function checkAuthOnLoad() {
    if (!authToken) return;
    const cachedName = localStorage.getItem('kca_user_name');
    const cachedRole = localStorage.getItem('kca_user_role') || 'student';

    try {
        const res = await fetch('/api/me', {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (res.ok) {
            const data = await res.json();
            currentUser = data;
            updateGreeting(data.name, data.role);
            localStorage.setItem('kca_user_name', data.name);
            localStorage.setItem('kca_user_role', data.role);

            // Route based on role
            if (data.role === 'admin') showPortal('admin');
            else if (data.role === 'staff') showPortal('kitchen');
            else showPortal('menu');
            return;
        }
    } catch (err) {
        // Java backend offline or Vercel static environment
    }

    // Local / cached token fallback
    if (cachedName) {
        updateGreeting(cachedName, cachedRole);
        if (cachedRole === 'admin') showPortal('admin');
        else if (cachedRole === 'staff') showPortal('kitchen');
        else showPortal('menu');
    }
}

// Sign In Button
document.getElementById('login-btn')?.addEventListener('click', async () => {
    const studentIdInput = document.getElementById('student-id').value.trim();
    const passwordInput = document.getElementById('password').value;
    const loginBtn = document.getElementById('login-btn');

    if (!studentIdInput || !passwordInput) {
        showToast("Please enter both ID and Password", true);
        return;
    }

    loginBtn.innerText = "Authenticating...";
    loginBtn.disabled = true;

    try {
        let authenticated = false;
        try {
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ studentId: studentIdInput, password: passwordInput })
            });

            if (res.ok) {
                const data = await res.json();
                authToken = data.token;
                currentUser = data;
                localStorage.setItem('kca_token', data.token);
                localStorage.setItem('kca_user_name', data.name);
                localStorage.setItem('kca_user_role', data.role);
                updateGreeting(data.name, data.role);
                showToast(`Welcome back, ${data.name}!`);

                if (data.role === 'admin') showPortal('admin');
                else if (data.role === 'staff') showPortal('kitchen');
                else showPortal('menu');
                authenticated = true;
            } else if (res.status === 400 || res.status === 401) {
                const errData = await res.json().catch(() => ({}));
                showToast(errData.error || "Invalid login credentials", true);
                authenticated = true;
            }
        } catch (fetchErr) {
            // Backend offline fallback to LocalDB
        }

        if (!authenticated) {
            const localAuth = LocalDB.authenticate(studentIdInput, passwordInput);
            if (localAuth.success) {
                authToken = localAuth.token;
                currentUser = { name: localAuth.name, studentId: localAuth.studentId, role: localAuth.role };
                localStorage.setItem('kca_token', localAuth.token);
                localStorage.setItem('kca_user_name', localAuth.name);
                localStorage.setItem('kca_user_role', localAuth.role);
                updateGreeting(localAuth.name, localAuth.role);
                showToast(`Welcome, ${localAuth.name}!`);

                if (localAuth.role === 'admin') showPortal('admin');
                else if (localAuth.role === 'staff') showPortal('kitchen');
                else showPortal('menu');
            } else {
                showToast(localAuth.error, true);
            }
        }
    } finally {
        loginBtn.innerText = "Sign In to Cafeteria";
        loginBtn.disabled = false;
    }
});

// Navigation between Login and Sign Up screens
document.getElementById('signup-link')?.addEventListener('click', (e) => {
    e.preventDefault();
    loginScreen.style.display = 'none';
    signupScreen.style.display = 'flex';
    document.getElementById('signup-name').focus();
});

document.getElementById('back-to-login-link')?.addEventListener('click', (e) => {
    e.preventDefault();
    signupScreen.style.display = 'none';
    loginScreen.style.display = 'flex';
});

// Registration (Sign Up) Button
document.getElementById('create-account-btn')?.addEventListener('click', async () => {
    const name = document.getElementById('signup-name').value.trim();
    const id = document.getElementById('signup-id').value.trim();
    const password = document.getElementById('signup-password').value;
    const role = document.getElementById('signup-role').value || 'student';
    const btn = document.getElementById('create-account-btn');

    if (!name || !id || !password) {
        showToast("Please fill in all registration fields", true);
        return;
    }

    if (password.length < 4) {
        showToast("Password must be at least 4 characters", true);
        return;
    }

    btn.innerText = "Registering...";
    btn.disabled = true;

    try {
        let registered = false;
        try {
            const res = await fetch('/api/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, studentId: id, password, role })
            });

            if (res.ok) {
                LocalDB.createUser(name, id, password, role);
                showToast(`Account created as ${role.toUpperCase()}! Please sign in.`);
                registered = true;
            } else {
                const errData = await res.json().catch(() => ({}));
                showToast(errData.error || "Registration failed", true);
                registered = true;
                return;
            }
        } catch (fetchErr) {
            // Local fallback
        }

        if (!registered) {
            const localResult = LocalDB.createUser(name, id, password, role);
            if (localResult.error) {
                showToast(localResult.error, true);
                return;
            }
            showToast(`Account created as ${role.toUpperCase()}! Please sign in.`);
        }

        signupScreen.style.display = 'none';
        loginScreen.style.display = 'flex';
        document.getElementById('student-id').value = id;
        document.getElementById('password').value = '';
    } finally {
        btn.innerText = "Complete Registration";
        btn.disabled = false;
    }
});

// ==========================================================================
// Menu Loading & Dynamic Rendering
// ==========================================================================

async function loadMenuFromBackend() {
    try {
        const res = await fetch('/api/menu');
        if (res.ok) {
            const dishes = await res.json();
            if (Array.isArray(dishes) && dishes.length > 0) {
                backendMenuItems = dishes;
                renderMenuGrid(dishes);
                return;
            }
        }
    } catch (e) {
        // Fallback to static cards if offline
    }
}

function renderMenuGrid(dishes) {
    const grid = document.getElementById('food-grid');
    if (!grid) return;

    grid.innerHTML = dishes.map(dish => {
        const isAvail = dish.available !== false;
        const soldOutBadge = isAvail ? '' : `<span class="sold-out-badge">SOLD OUT</span>`;
        const soldOutClass = isAvail ? '' : 'sold-out';
        const addBtnText = isAvail ? '+ Add' : 'Sold Out';
        const addBtnClick = isAvail ? `onclick="addToCart('${dish.name.replace(/'/g, "\\'")}', ${dish.price}, '${dish.id}')"` : '';

        return `
            <div class="food-card ${soldOutClass}" data-category="${dish.category || 'lunch'}">
                <div class="card-img-wrapper" style="position: relative;">
                    ${soldOutBadge}
                    <img src="${dish.image || 'images/chicken_and_rice.png'}" alt="${dish.name}" class="food-img" onerror="this.src='images/chicken_and_rice.png'">
                    <span class="card-category-badge">${(dish.category || 'Mains').toUpperCase()}</span>
                </div>
                <div class="food-info">
                    <div class="food-info-top">
                        <h3>${dish.name}</h3>
                        <p class="food-desc">${dish.description || 'Fresh campus meal prepared daily.'}</p>
                    </div>
                    <div class="food-info-bottom">
                        <span class="price">KES ${Math.round(dish.price)}</span>
                        <button class="btn-add" ${addBtnClick} ${!isAvail ? 'disabled' : ''}>${addBtnText}</button>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    // Rebind active filter
    applyActiveMenuFilter();
}

function applyActiveMenuFilter() {
    const activePill = document.querySelector('.pill.active');
    const filter = activePill ? activePill.getAttribute('data-filter') : 'all';
    const cards = document.querySelectorAll('.food-card');
    cards.forEach(card => {
        if (filter === 'all' || card.getAttribute('data-category') === filter) {
            card.style.display = 'flex';
        } else {
            card.style.display = 'none';
        }
    });
}

// Category Pills Filtering
document.querySelectorAll('.pill').forEach(pill => {
    pill.addEventListener('click', () => {
        document.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        applyActiveMenuFilter();
    });
});

// Menu Search Filter
const searchInput = document.getElementById('menu-search-input');
if (searchInput) {
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        document.querySelectorAll('.food-card').forEach(card => {
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

// ==========================================================================
// Cart & Checkout Logic
// ==========================================================================

window.addToCart = function(name, price, id) {
    cartTotal += price;
    cartItemsCount++;

    if (cartItems[name]) {
        cartItems[name].count++;
    } else {
        cartItems[name] = { id: id, price: price, count: 1 };
    }

    try {
        const btn = event?.currentTarget || event?.target;
        if (btn && btn.classList?.contains('btn-add')) {
            const orig = btn.innerText;
            btn.innerText = `✓ (${cartItems[name].count})`;
            btn.style.background = '#10B981';
            btn.style.borderColor = '#10B981';
            btn.style.color = '#FFFFFF';
            setTimeout(() => {
                btn.innerText = `+ Add (${cartItems[name].count})`;
                btn.style.background = '';
                btn.style.borderColor = '';
                btn.style.color = '';
            }, 1000);
        }
    } catch (e) {}

    showToast(`Added ${name} (KES ${price}) to tray!`);
    updateCartUI();
};

function updateCartUI() {
    const totalEl = document.getElementById('cart-total-amount');
    const badgeEl = document.getElementById('cart-badge');
    const countLabelEl = document.getElementById('cart-items-count-label');
    const dock = document.getElementById('sticky-cart-bar');

    if (totalEl) totalEl.innerText = cartTotal;
    if (badgeEl) badgeEl.innerText = cartItemsCount;
    if (countLabelEl) countLabelEl.innerText = cartItemsCount;

    if (dock) {
        if (cartItemsCount > 0) dock.classList.add('active');
        else dock.classList.remove('active');
    }

    if (badgeEl) {
        badgeEl.style.transform = 'scale(1.35)';
        setTimeout(() => { badgeEl.style.transform = 'scale(1)'; }, 180);
    }
}

// Open Checkout Modal
document.getElementById('checkout-btn')?.addEventListener('click', () => {
    if (cartTotal === 0) {
        showToast("Your meal tray is empty! Click '+ Add' to select meals.");
        return;
    }

    mpesaAmount.innerText = cartTotal;
    document.querySelectorAll('.cash-amount-ref').forEach(el => el.innerText = cartTotal);

    switchPayTab(document.querySelector('.pay-tab[data-method="mpesa"]'), 'mpesa-panel');
    mpesaFormSection.style.display = 'block';
    mpesaProcessingSection.style.display = 'none';
    mpesaModal.style.display = 'flex';
});

// Pay Tabs Switching
window.switchPayTab = function(clickedTab, panelId) {
    document.querySelectorAll('.pay-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.pay-panel').forEach(p => p.style.display = 'none');
    if (clickedTab) clickedTab.classList.add('active');
    const target = document.getElementById(panelId);
    if (target) target.style.display = 'block';
};

document.getElementById('mpesa-cancel-btn')?.addEventListener('click', () => {
    mpesaModal.style.display = 'none';
});

// Submit Order to Java Backend
async function placeOrderAndPay(paymentMethod, phoneOrRef) {
    const processingTitle = document.getElementById('processing-title');
    const processingMsg = document.getElementById('processing-msg');

    processingTitle.innerText = `Processing ${paymentMethod} Payment`;
    processingMsg.innerText = "Transmitting order to KCAU Java Kitchen Engine...";
    mpesaFormSection.style.display = 'none';
    mpesaProcessingSection.style.display = 'block';

    // Construct line items
    const orderItemsArray = [];
    for (let name in cartItems) {
        orderItemsArray.push({
            foodName: name,
            quantity: cartItems[name].count,
            unitPrice: cartItems[name].price
        });
    }

    const orderPayload = {
        userId: currentUser?.studentId || currentUser?.id || 'GUEST',
        customerName: currentStudentName,
        totalAmount: cartTotal,
        items: orderItemsArray
    };

    let createdOrder = null;

    try {
        const orderRes = await fetch('/api/orders', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(orderPayload)
        });

        if (orderRes.ok) {
            createdOrder = await orderRes.json();
        }
    } catch (e) {
        // Fallback to local
    }

    if (!createdOrder) {
        const localOrderId = 'ORD-' + Math.floor(100000 + Math.random() * 900000);
        createdOrder = LocalDB.saveOrder({
            orderId: localOrderId,
            userId: orderPayload.userId,
            customerName: orderPayload.customerName,
            totalAmount: cartTotal,
            status: 'PENDING',
            items: orderItemsArray,
            createdAt: new Date().toISOString()
        });
    }

    // Submit Payment Record
    const generatedRef = paymentMethod + '-' + Math.random().toString(36).substring(2, 8).toUpperCase();
    const paymentPayload = {
        orderId: createdOrder.orderId,
        method: paymentMethod,
        amount: cartTotal,
        reference: generatedRef,
        status: (paymentMethod === 'CASH') ? 'PENDING' : 'COMPLETED'
    };

    try {
        await fetch('/api/payments', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(paymentPayload)
        });
    } catch (e) {
        LocalDB.savePayment(paymentPayload);
    }

    // Delay 1.5s for realistic simulation feeling
    setTimeout(() => {
        mpesaModal.style.display = 'none';
        activeOrderId = createdOrder.orderId;
        localStorage.setItem('kca_active_order_id', activeOrderId);

        showReceipt(createdOrder, generatedRef);
    }, 1500);
}

// Payment Methods Listeners
document.getElementById('mpesa-pay-btn')?.addEventListener('click', () => {
    const phone = document.getElementById('mpesa-phone').value.trim();
    if (!phone || phone.length < 9) {
        alert("Please enter a valid 9-digit Safaricom mobile number.");
        return;
    }
    placeOrderAndPay('MPESA', '+254' + phone);
});

document.getElementById('airtel-pay-btn')?.addEventListener('click', () => {
    const phone = document.getElementById('airtel-phone').value.trim();
    if (!phone || phone.length < 9) {
        alert("Please enter a valid 9-digit Airtel mobile number.");
        return;
    }
    placeOrderAndPay('AIRTEL', '+254' + phone);
});

document.getElementById('card-pay-btn')?.addEventListener('click', () => {
    const card = document.getElementById('card-number').value.trim();
    if (!card) {
        alert("Please enter card details.");
        return;
    }
    placeOrderAndPay('CARD', 'CARD-XXXX');
});

document.getElementById('cash-confirm-btn')?.addEventListener('click', () => {
    placeOrderAndPay('CASH', 'COUNTER-CASH');
});

// Display Receipt
function showReceipt(order, refCode) {
    const list = document.getElementById('receipt-items-list');
    const orderIdEl = document.getElementById('receipt-order-id');
    const refCodeEl = document.getElementById('receipt-ref-code');
    const totalEl = document.getElementById('receipt-total-amount');

    if (orderIdEl) orderIdEl.innerText = `#${order.orderId}`;
    if (refCodeEl) refCodeEl.innerText = `Ref: ${refCode}`;
    if (totalEl) totalEl.innerText = cartTotal;

    if (list) {
        list.innerHTML = '';
        for (let name in cartItems) {
            const item = cartItems[name];
            const li = document.createElement('li');
            li.innerHTML = `<span>${item.count}x ${name}</span> <strong>KES ${item.price * item.count}</strong>`;
            list.appendChild(li);
        }
    }

    receiptModal.style.display = 'flex';
}

// Close Receipt & View Status
document.getElementById('close-receipt-btn')?.addEventListener('click', () => {
    receiptModal.style.display = 'none';

    // Clear cart
    cartTotal = 0;
    cartItemsCount = 0;
    cartItems = {};
    updateCartUI();

    // If student, stay on menu and track active order
    if (currentRole === 'student') {
        showPortal('menu');
        checkActiveOrderStatus();
    } else {
        showPortal('kitchen');
    }
});

// Live Active Order Tracking for Students
async function checkActiveOrderStatus() {
    if (!activeOrderId) return;
    const banner = document.getElementById('student-active-order-banner');
    const idEl = document.getElementById('banner-order-id');
    const badgeEl = document.getElementById('banner-order-badge');
    const msgEl = document.getElementById('banner-order-msg');

    let order = null;
    try {
        const res = await fetch('/api/orders');
        if (res.ok) {
            const orders = await res.json();
            order = orders.find(o => o.orderId === activeOrderId);
        }
    } catch (e) {}

    if (!order) {
        order = LocalDB.getOrders().find(o => o.orderId === activeOrderId);
    }

    if (order && banner) {
        banner.style.display = 'block';
        if (idEl) idEl.innerText = order.orderId;
        const status = order.status || 'PENDING';
        if (badgeEl) {
            badgeEl.innerText = status;
            badgeEl.className = `status-badge status-${status.toLowerCase()}`;
        }
        if (msgEl) {
            if (status === 'PENDING') msgEl.innerText = "Order sent to kitchen queue.";
            else if (status === 'PREPARING') msgEl.innerText = "Chef is currently cooking your meal 🍳.";
            else if (status === 'READY') {
                msgEl.innerText = "🔔 Your meal is READY for pickup at the cafeteria counter!";
                showToast("🔔 Your order is READY for pickup!");
            } else if (status === 'COLLECTED') {
                msgEl.innerText = "Order collected. Enjoy your meal! 😋";
                setTimeout(() => { banner.style.display = 'none'; }, 8000);
            }
        }
    }
}

// ==========================================================================
// Kitchen Display System (Staff Portal)
// ==========================================================================

window.switchKitchenTab = function(tabName) {
    const ordersView = document.getElementById('kitchen-orders-view');
    const paymentsView = document.getElementById('kitchen-payments-view');
    const tabOrders = document.getElementById('kitchen-tab-orders');
    const tabPayments = document.getElementById('kitchen-tab-payments');

    if (tabName === 'orders') {
        ordersView.style.display = 'block';
        paymentsView.style.display = 'none';
        tabOrders.classList.add('active');
        tabPayments.classList.remove('active');
        fetchKitchenOrders();
    } else {
        ordersView.style.display = 'none';
        paymentsView.style.display = 'block';
        tabOrders.classList.remove('active');
        tabPayments.classList.add('active');
        fetchPaymentsLedger();
    }
};

window.filterKitchenOrders = function(status, btnEl) {
    currentKitchenFilter = status;
    document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
    if (btnEl) btnEl.classList.add('active');
    renderKitchenOrdersGrid();
};

async function fetchKitchenOrders() {
    try {
        const res = await fetch('/api/orders');
        if (res.ok) {
            const orders = await res.json();
            kitchenOrdersList = orders;
            updateKitchenCounts();
            renderKitchenOrdersGrid();
            return;
        }
    } catch (e) {}

    // Fallback to localDB
    kitchenOrdersList = LocalDB.getOrders();
    updateKitchenCounts();
    renderKitchenOrdersGrid();
}

function updateKitchenCounts() {
    const all = kitchenOrdersList.length;
    const pending = kitchenOrdersList.filter(o => o.status === 'PENDING').length;
    const prep = kitchenOrdersList.filter(o => o.status === 'PREPARING').length;
    const ready = kitchenOrdersList.filter(o => o.status === 'READY').length;
    const collected = kitchenOrdersList.filter(o => o.status === 'COLLECTED').length;

    const cAll = document.getElementById('count-all');
    const cPend = document.getElementById('count-pending');
    const cPrep = document.getElementById('count-preparing');
    const cReady = document.getElementById('count-ready');
    const cColl = document.getElementById('count-collected');

    if (cAll) cAll.innerText = all;
    if (cPend) cPend.innerText = pending;
    if (cPrep) cPrep.innerText = prep;
    if (cReady) cReady.innerText = ready;
    if (cColl) cColl.innerText = collected;
}

function renderKitchenOrdersGrid() {
    const container = document.getElementById('live-orders-section');
    const noOrdersMsg = document.getElementById('no-orders-msg');
    if (!container) return;

    let filtered = kitchenOrdersList;
    if (currentKitchenFilter !== 'ALL') {
        filtered = kitchenOrdersList.filter(o => (o.status || 'PENDING') === currentKitchenFilter);
    }

    container.innerHTML = '';
    if (filtered.length === 0) {
        if (noOrdersMsg) {
            noOrdersMsg.style.display = 'block';
            container.appendChild(noOrdersMsg);
        }
        return;
    }

    filtered.forEach(order => {
        const status = order.status || 'PENDING';
        const card = document.createElement('div');
        card.className = 'order-card';

        const itemsLines = (order.items || []).map(it => `
            <div class="order-item-line">
                <span><strong>${it.quantity}x</strong> ${it.foodName}</span>
                <span>KES ${it.quantity * it.unitPrice}</span>
            </div>
        `).join('') || '<div class="order-item-line"><span>Standard Cafeteria Meal</span></div>';

        // Action Buttons based on status
        let actionButtons = '';
        if (status === 'PENDING') {
            actionButtons = `<button class="btn-action-status btn-action-preparing" onclick="updateOrderStatus('${order.orderId}', 'PREPARING')">🍳 Start Preparing</button>`;
        } else if (status === 'PREPARING') {
            actionButtons = `<button class="btn-action-status btn-action-ready" onclick="updateOrderStatus('${order.orderId}', 'READY')">🔔 Mark Ready for Pickup</button>`;
        } else if (status === 'READY') {
            actionButtons = `<button class="btn-action-status btn-action-collected" onclick="updateOrderStatus('${order.orderId}', 'COLLECTED')">✓ Mark Collected</button>`;
        } else {
            actionButtons = `<span style="font-size:0.8rem; color:var(--text-muted); font-weight:700;">Order Completed ✓</span>`;
        }

        card.innerHTML = `
            <div>
                <div class="order-top-row">
                    <span class="order-badge-id">#${order.orderId}</span>
                    <span class="status-badge status-${status.toLowerCase()}">${status}</span>
                </div>
                <div class="order-customer-row">
                    <span class="customer-pill">👤 ${order.customerName || 'Student'}</span>
                    <span class="order-time">${order.createdAt ? new Date(order.createdAt).toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' }) : 'Just now'}</span>
                </div>
                <div class="order-items-box">
                    ${itemsLines}
                </div>
            </div>
            <div>
                <div class="order-total-row">
                    <span>Total Amount:</span>
                    <span>KES ${Math.round(order.totalAmount || 0)}</span>
                </div>
                <div class="order-action-btn-group">
                    ${actionButtons}
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

window.updateOrderStatus = async function(orderId, newStatus) {
    try {
        const res = await fetch('/api/orders/status', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ orderId, status: newStatus })
        });
        if (res.ok) {
            showToast(`Order #${orderId} moved to ${newStatus}`);
            fetchKitchenOrders();
            return;
        }
    } catch (e) {}

    LocalDB.updateOrderStatus(orderId, newStatus);
    showToast(`Order #${orderId} moved to ${newStatus}`);
    fetchKitchenOrders();
};

async function fetchPaymentsLedger() {
    const tbody = document.getElementById('payments-ledger-tbody');
    if (!tbody) return;

    try {
        const res = await fetch('/api/payments');
        if (res.ok) {
            const payments = await res.json();
            renderPaymentsLedger(payments);
            return;
        }
    } catch (e) {}

    renderPaymentsLedger(LocalDB.getPayments());
}

function renderPaymentsLedger(payments) {
    const tbody = document.getElementById('payments-ledger-tbody');
    if (!tbody) return;

    if (!payments || payments.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:2rem; color:var(--text-secondary);">No payments recorded yet.</td></tr>`;
        return;
    }

    tbody.innerHTML = payments.map(p => `
        <tr>
            <td><strong>${p.reference || p.id}</strong></td>
            <td>#${p.orderId}</td>
            <td><span class="customer-pill">${p.method}</span></td>
            <td><strong>KES ${Math.round(p.amount)}</strong></td>
            <td><span class="status-badge ${p.status === 'COMPLETED' ? 'status-ready' : 'status-pending'}">${p.status}</span></td>
            <td>${p.createdAt ? new Date(p.createdAt).toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' }) : 'Recent'}</td>
        </tr>
    `).join('');
}

// ==========================================================================
// Administrator Portal Management
// ==========================================================================

window.switchAdminTab = function(tabName) {
    document.querySelectorAll('.nav-subtab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.admin-view-panel').forEach(p => p.style.display = 'none');

    const activeTab = document.getElementById(`admin-tab-${tabName}`);
    const activeView = document.getElementById(`admin-view-${tabName}`);

    if (activeTab) activeTab.classList.add('active');
    if (activeView) activeView.style.display = 'block';

    if (tabName === 'reports') fetchAdminReports();
    else if (tabName === 'menu') fetchAdminMenu();
    else if (tabName === 'users') fetchAdminUsers();
};

async function fetchAdminDashboard() {
    fetchAdminReports();
}

async function fetchAdminReports() {
    try {
        const summaryRes = await fetch('/api/reports/summary');
        if (summaryRes.ok) {
            const summary = await summaryRes.json();
            document.getElementById('admin-kpi-revenue').innerText = Number(summary.totalRevenue || 0).toLocaleString('en-KE', { minimumFractionDigits: 2 });
            document.getElementById('admin-kpi-orders').innerText = summary.totalOrders || 0;
            document.getElementById('admin-kpi-active').innerText = summary.preparingOrders || 0;
            document.getElementById('admin-kpi-users').innerText = summary.totalUsers || 0;
        }

        const salesRes = await fetch('/api/reports/sales');
        if (salesRes.ok) {
            const popItems = await salesRes.json();
            renderAdminPopularItems(popItems);
        }

        const ordersRes = await fetch('/api/orders');
        if (ordersRes.ok) {
            const orders = await ordersRes.json();
            renderAdminRecentOrders(orders);
        }
    } catch (e) {
        // Fallback calculations from LocalDB
        const orders = LocalDB.getOrders();
        const users = LocalDB.getUsers();
        const rev = orders.reduce((acc, o) => acc + (o.totalAmount || 0), 0);
        document.getElementById('admin-kpi-revenue').innerText = rev.toFixed(2);
        document.getElementById('admin-kpi-orders').innerText = orders.length;
        document.getElementById('admin-kpi-active').innerText = orders.filter(o => o.status === 'PREPARING').length;
        document.getElementById('admin-kpi-users').innerText = users.length;
        renderAdminRecentOrders(orders);
    }
}

function renderAdminPopularItems(items) {
    const tbody = document.getElementById('admin-popular-items-tbody');
    if (!tbody) return;

    if (!items || items.length === 0) {
        tbody.innerHTML = `<tr><td colspan="3" style="text-align:center; padding:1.5rem; color:var(--text-secondary);">No sales data recorded yet.</td></tr>`;
        return;
    }

    tbody.innerHTML = items.slice(0, 5).map(item => `
        <tr>
            <td><strong>${item.foodName}</strong></td>
            <td>${item.ordersCount} servings</td>
            <td><strong>KES ${Math.round(item.revenue)}</strong></td>
        </tr>
    `).join('');
}

function renderAdminRecentOrders(orders) {
    const tbody = document.getElementById('admin-recent-orders-tbody');
    if (!tbody) return;

    if (!orders || orders.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; padding:1.5rem; color:var(--text-secondary);">No recent orders found.</td></tr>`;
        return;
    }

    tbody.innerHTML = orders.slice(0, 6).map(o => `
        <tr>
            <td><strong>#${o.orderId}</strong></td>
            <td>${o.customerName}</td>
            <td>KES ${Math.round(o.totalAmount)}</td>
            <td><span class="status-badge status-${(o.status || 'PENDING').toLowerCase()}">${o.status}</span></td>
        </tr>
    `).join('');
}

async function fetchAdminMenu() {
    const tbody = document.getElementById('admin-menu-tbody');
    if (!tbody) return;

    try {
        const res = await fetch('/api/menu');
        if (res.ok) {
            const dishes = await res.json();
            renderAdminMenuTable(dishes);
            return;
        }
    } catch (e) {}

    renderAdminMenuTable(backendMenuItems);
}

function renderAdminMenuTable(dishes) {
    const tbody = document.getElementById('admin-menu-tbody');
    if (!tbody) return;

    if (!dishes || dishes.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:2rem; color:var(--text-secondary);">No menu dishes found.</td></tr>`;
        return;
    }

    tbody.innerHTML = dishes.map(dish => {
        const isAvail = dish.available !== false;
        const toggleClass = isAvail ? 'avail-true' : 'avail-false';
        const toggleText = isAvail ? '✓ Available (Click to Disable)' : '✕ Sold Out (Click to Enable)';

        return `
            <tr>
                <td>
                    <div style="display:flex; align-items:center; gap:0.75rem;">
                        <img src="${dish.image}" style="width:40px; height:40px; border-radius:8px; object-fit:cover;" onerror="this.src='images/chicken_and_rice.png'">
                        <div>
                            <strong>${dish.name}</strong>
                            <div style="font-size:0.75rem; color:var(--text-secondary);">${dish.id}</div>
                        </div>
                    </div>
                </td>
                <td><span class="customer-pill">${(dish.category || 'Mains').toUpperCase()}</span></td>
                <td><strong>KES ${Math.round(dish.price)}</strong></td>
                <td><span class="status-badge ${isAvail ? 'status-ready' : 'status-cancelled'}">${isAvail ? 'IN STOCK' : 'SOLD OUT'}</span></td>
                <td>
                    <button class="btn-toggle-avail ${toggleClass}" onclick="toggleDishAvailability('${dish.id}', ${!isAvail})">
                        ${toggleText}
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

window.toggleDishAvailability = async function(foodId, newAvailable) {
    try {
        const res = await fetch('/api/menu/availability', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ foodId, available: newAvailable })
        });
        if (res.ok) {
            showToast(`Item updated to ${newAvailable ? 'Available' : 'Sold Out'}`);
            fetchAdminMenu();
            loadMenuFromBackend();
            return;
        }
    } catch (e) {}

    showToast(`Updated dish availability`);
    fetchAdminMenu();
};

// Add Dish Modal
window.openAddDishModal = function() {
    if (addDishModal) addDishModal.style.display = 'flex';
};

window.closeAddDishModal = function() {
    if (addDishModal) addDishModal.style.display = 'none';
};

window.submitNewDish = async function() {
    const name = document.getElementById('new-dish-name').value.trim();
    const category = document.getElementById('new-dish-category').value;
    const price = parseFloat(document.getElementById('new-dish-price').value);
    const description = document.getElementById('new-dish-desc').value.trim();
    const image = document.getElementById('new-dish-image').value.trim() || 'images/chicken_and_rice.png';

    if (!name || isNaN(price) || price <= 0) {
        alert("Please enter a valid dish name and price.");
        return;
    }

    try {
        const res = await fetch('/api/menu', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, category, price, description, image, available: true })
        });
        if (res.ok) {
            showToast(`Added ${name} to cafeteria menu!`);
            closeAddDishModal();
            fetchAdminMenu();
            loadMenuFromBackend();
            return;
        }
    } catch (e) {}

    showToast("Added dish to catalog");
    closeAddDishModal();
    fetchAdminMenu();
};

// Admin User Accounts Table
async function fetchAdminUsers() {
    const tbody = document.getElementById('admin-users-tbody');
    if (!tbody) return;

    try {
        const res = await fetch('/api/users');
        if (res.ok) {
            const users = await res.json();
            renderAdminUsersTable(users);
            return;
        }
    } catch (e) {}

    renderAdminUsersTable(LocalDB.getUsers());
}

function renderAdminUsersTable(users) {
    const tbody = document.getElementById('admin-users-tbody');
    if (!tbody) return;

    if (!users || users.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:2rem; color:var(--text-secondary);">No user accounts found.</td></tr>`;
        return;
    }

    tbody.innerHTML = users.map(u => `
        <tr>
            <td><code style="font-size:0.8rem; background:#F1F5F9; padding:2px 6px; border-radius:4px;">${u.id}</code></td>
            <td><strong>${u.name}</strong></td>
            <td>${u.studentId}</td>
            <td><span class="role-badge role-${(u.role || 'student').toLowerCase()}">${(u.role || 'student').toUpperCase()}</span></td>
            <td>
                <div style="display:flex; gap:0.5rem; align-items:center;">
                    <select id="role-sel-${u.id}" class="form-select" style="padding:0.35rem 0.65rem; font-size:0.82rem; width:auto;">
                        <option value="student" ${u.role === 'student' ? 'selected' : ''}>Student</option>
                        <option value="staff" ${u.role === 'staff' ? 'selected' : ''}>Kitchen Staff</option>
                        <option value="admin" ${u.role === 'admin' ? 'selected' : ''}>Admin</option>
                    </select>
                    <button class="btn-refresh-sm" onclick="saveUserRole('${u.id}')">Save</button>
                </div>
            </td>
        </tr>
    `).join('');
}

window.saveUserRole = async function(userId) {
    const select = document.getElementById(`role-sel-${userId}`);
    if (!select) return;
    const newRole = select.value;

    try {
        const res = await fetch('/api/users/role', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ userId, role: newRole })
        });
        if (res.ok) {
            showToast(`Role updated to ${newRole.toUpperCase()}`);
            fetchAdminUsers();
            return;
        }
    } catch (e) {}

    showToast(`Role changed to ${newRole}`);
    fetchAdminUsers();
};

// Initialize Application
checkAuthOnLoad();
loadMenuFromBackend();
