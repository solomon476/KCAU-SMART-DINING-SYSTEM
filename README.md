# KCAU SMART DINING SYSTEM 🍽️

An online cafeteria ordering and dining management system built specifically for KCA University (KCAU). The platform provides student meal discovery, cart management, checkout with simulated M-Pesa STK push, instant digital receipt generation, and authentication powered by a native **Java backend**.

---

## 🛠️ Technology Stack

- **Backend**: **Java (Java SE 17+, `Server.java`)**
  - Built using Java's built-in `com.sun.net.httpserver.HttpServer`
  - High-concurrency virtual threading via `Executors.newVirtualThreadPerTaskExecutor()`
  - Cryptographic security: **PBKDF2WithHmacSHA256** password hashing and **HMAC-SHA256 JWT** authentication
  - Persistent Storage: **Built-in JSON Database (`data/users.json`)** for permanent account storage across server reboots
  - OOP Domain Models in [`src/main/java/com/kcau/dining/model/`](src/main/java/com/kcau/dining/model/) (`MenuItem.java`, `Order.java`, `User.java`)
- **Frontend**: **HTML5, Modern Vanilla CSS, JavaScript**
  - Responsive layout optimized for mobile screens, tablets, and desktop/laptop displays
  - Interactive sliding cart dock, food category filters, live dish search
  - Modal checkout flows with M-Pesa, Airtel Money, Card, and Counter pay
  - In-app notification toast alerts

---

## 🚀 Getting Started

### Prerequisites

- **Java Development Kit (JDK) 17 or higher** (JDK 17, 21, or 25 recommended)

### Running the Java Backend

You can run the server directly using any of the following methods:

#### Method 1: Direct Java Execution (Recommended)
```bash
java Server.java
```

#### Method 2: Shell Script
```bash
chmod +x run-java.sh
./run-java.sh
```

#### Method 3: npm Scripts
```bash
npm start
```

Once started, open your browser and navigate to:
```
http://localhost:3000
```

---

## 📡 Backend REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/signup` | Register a new student/staff account with PBKDF2 hashed password |
| `POST` | `/api/login` | Authenticate user credentials and return a signed HMAC-SHA256 JWT |
| `GET` | `/api/me` | Fetch authenticated user profile using Bearer JWT token |
| `GET` | `/api/status` | Backend health check verifying the Java HTTP service status |
| `GET` | `/*` | Static file server and SPA routing for the client interface |

---

## 📁 Repository Structure

```
.
├── Server.java                 # Standalone Java HTTP Backend Server with Persistent DB
├── data/
│   └── users.json              # Persistent JSON Database for registered user accounts
├── run-java.sh                 # Shell launcher script for Java backend
├── package.json                # Project manifest configured with Java run scripts
├── vercel.json                 # Static frontend deployment configuration
├── src/
│   └── main/
│       └── java/
│           └── com/
│               └── kcau/
│                   └── dining/
│                       └── model/
│                           ├── MenuItem.java   # Food and menu item model
│                           ├── Order.java      # Order item and receipt model
│                           └── User.java       # User entity model
└── public/                     # Frontend client assets
    ├── index.html              # Modern cafeteria web application
    ├── style.css               # Responsive design system
    ├── app.js                  # Frontend interactions & API communication
    └── images/                 # Cafeteria menu images
```

---

## 🔐 User Authentication & Persistent Database

The system features real account registration, login verification, and secure password hashing:
- **Create Account**: Click **Create Account** to register with Full Name, Student ID, and Password. Accounts are permanently saved to `data/users.json`.
- **Sign In**: Log in using your registered Student ID and Password.
- **Initial Test Account**:
  - **Student ID**: `KCA/1234/23`
  - **Password**: `password123`

---

## 👤 Author

- **Solomon** — [GitHub Profile](https://github.com/solomon476)
- Repository: [KCAU-SMART-DINING-SYSTEM](https://github.com/solomon476/KCAU-SMART-DINING-SYSTEM)
