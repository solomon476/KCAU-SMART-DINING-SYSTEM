package com.kcau.dining.database;

import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import java.time.Instant;
import java.util.Base64;
import java.util.UUID;

/**
 * Initializes the SQLite database schema and seeds initial cafeteria data.
 */
public class DatabaseInitializer {

    public static void init() {
        try (Connection conn = DatabaseConnection.getConnection();
             Statement stmt = conn.createStatement()) {

            // 1. Users table (Student ID, Name, Password Hash, Role)
            stmt.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    student_id TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'student',
                    created_at TEXT NOT NULL
                );
            """);

            // 2. Menu Items table (Food ID, Name, Description, Price, Availability, Category, Image)
            stmt.execute("""
                CREATE TABLE IF NOT EXISTS menu_items (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL,
                    category TEXT NOT NULL,
                    image TEXT,
                    available INTEGER NOT NULL DEFAULT 1
                );
            """);

            // 3. Orders table (Order ID, User ID, Customer Name, Date, Total, Order Status)
            stmt.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    customer_name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    total REAL NOT NULL,
                    order_status TEXT NOT NULL DEFAULT 'PENDING'
                );
            """);

            // 4. Order Items table (Order ID, Food ID, Food Name, Quantity, Unit Price)
            stmt.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT NOT NULL,
                    food_id TEXT NOT NULL,
                    food_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE
                );
            """);

            // 5. Payments table (Payment ID, Order ID, Method, Amount, Status, Reference, Date)
            stmt.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id TEXT PRIMARY KEY,
                    order_id TEXT NOT NULL,
                    method TEXT NOT NULL,
                    amount REAL NOT NULL,
                    status TEXT NOT NULL,
                    reference TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE
                );
            """);

            // Seed default users if table is empty
            seedDefaultUsers(conn);

            // Seed default menu items if table is empty
            seedDefaultMenu(conn);

            System.out.println("✅ SQLite Database initialized successfully: " + DatabaseConnection.getDbPath());

        } catch (Exception e) {
            System.err.println("❌ Database initialization error: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private static void seedDefaultUsers(Connection conn) throws Exception {
        try (Statement checkStmt = conn.createStatement();
             ResultSet rs = checkStmt.executeQuery("SELECT COUNT(*) AS total FROM users")) {
            if (rs.next() && rs.getInt("total") == 0) {
                String studentHash = hashPassword("password123");
                String staffHash = hashPassword("password123");
                String adminHash = hashPassword("password123");

                String sql = "INSERT INTO users (id, name, student_id, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?, ?)";
                try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
                    // Student Demo Account
                    pstmt.setString(1, "demo-student-1");
                    pstmt.setString(2, "Alex Kiprop");
                    pstmt.setString(3, "KCA/1234/23");
                    pstmt.setString(4, studentHash);
                    pstmt.setString(5, "student");
                    pstmt.setString(6, Instant.now().toString());
                    pstmt.addBatch();

                    // Dining Staff Account
                    pstmt.setString(1, "staff-1");
                    pstmt.setString(2, "Chef Beatrice (Kitchen Staff)");
                    pstmt.setString(3, "STAFF/001");
                    pstmt.setString(4, staffHash);
                    pstmt.setString(5, "staff");
                    pstmt.setString(6, Instant.now().toString());
                    pstmt.addBatch();

                    // Administrator Account
                    pstmt.setString(1, "admin-1");
                    pstmt.setString(2, "Solomon (Cafeteria Admin)");
                    pstmt.setString(3, "ADMIN/001");
                    pstmt.setString(4, adminHash);
                    pstmt.setString(5, "admin");
                    pstmt.setString(6, Instant.now().toString());
                    pstmt.addBatch();

                    pstmt.executeBatch();
                    System.out.println("🌱 Seeded initial users (Student, Dining Staff, Administrator)");
                }
            }
        }
    }

    private static void seedDefaultMenu(Connection conn) throws Exception {
        try (Statement checkStmt = conn.createStatement();
             ResultSet rs = checkStmt.executeQuery("SELECT COUNT(*) AS total FROM menu_items")) {
            if (rs.next() && rs.getInt("total") == 0) {
                String sql = "INSERT INTO menu_items (id, name, description, price, category, image, available) VALUES (?, ?, ?, ?, ?, ?, ?)";
                try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
                    Object[][] defaultDishes = {
                        {"food-1", "Chicken & Rice", "Grilled spiced chicken served with fragrant yellow rice and gravy", 150.0, "lunch", "images/chicken_and_rice.png", 1},
                        {"food-2", "Fresh Mango Juice", "Chilled, naturally squeezed local mango juice without preservatives", 80.0, "drinks", "images/fresh_juice.png", 1},
                        {"food-3", "Beef Burger & Greens", "Quarter pound seasoned beef patty in a toasted sesame bun with lettuce", 220.0, "lunch", "images/beef_burger.png", 1},
                        {"food-4", "Eggs & Brown Toast", "Two farm-fresh sunny side up eggs served with buttered toasted bread", 120.0, "breakfast", "images/eggs_toast.png", 1},
                        {"food-5", "Crisp Golden Fries", "Hand-cut seasoned potato fries deep-fried till golden crisp", 100.0, "snacks", "images/fries.png", 1},
                        {"food-6", "Fluffy Honey Pancakes", "Stack of two buttermilk pancakes drizzled with pure golden honey", 140.0, "breakfast", "images/pancakes.png", 1},
                        {"food-7", "Hot Brewed Coffee", "Rich aromatic Kenyan Arabica roasted coffee served piping hot", 70.0, "drinks", "images/coffee.png", 1},
                        {"food-8", "Ice Cold Coca-Cola", "Chilled 500ml refreshing glass bottle of original Coca-Cola", 60.0, "drinks", "images/coca_cola.png", 1}
                    };

                    for (Object[] dish : defaultDishes) {
                        pstmt.setString(1, (String) dish[0]);
                        pstmt.setString(2, (String) dish[1]);
                        pstmt.setString(3, (String) dish[2]);
                        pstmt.setDouble(4, (Double) dish[3]);
                        pstmt.setString(5, (String) dish[4]);
                        pstmt.setString(6, (String) dish[5]);
                        pstmt.setInt(7, (Integer) dish[6]);
                        pstmt.addBatch();
                    }

                    pstmt.executeBatch();
                    System.out.println("🌱 Seeded full cafeteria menu catalog into SQLite");
                }
            }
        }
    }

    public static String hashPassword(String password) {
        try {
            byte[] salt = new byte[16];
            new SecureRandom().nextBytes(salt);
            PBEKeySpec spec = new PBEKeySpec(password.toCharArray(), salt, 10000, 256);
            SecretKeyFactory skf = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
            byte[] hash = skf.generateSecret(spec).getEncoded();
            return Base64.getEncoder().encodeToString(salt) + ":" + Base64.getEncoder().encodeToString(hash);
        } catch (Exception e) {
            throw new RuntimeException("Error hashing password", e);
        }
    }

    public static boolean verifyPassword(String password, String storedHash) {
        if (password == null || storedHash == null) return false;
        try {
            String[] parts = storedHash.split(":");
            if (parts.length != 2) {
                return password.equals(storedHash) || password.trim().equals(storedHash.trim());
            }
            byte[] salt = Base64.getDecoder().decode(parts[0]);
            byte[] expectedHash = Base64.getDecoder().decode(parts[1]);

            PBEKeySpec spec = new PBEKeySpec(password.toCharArray(), salt, 10000, 256);
            SecretKeyFactory skf = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
            byte[] computedHash = skf.generateSecret(spec).getEncoded();

            if (MessageDigest.isEqual(expectedHash, computedHash)) {
                return true;
            }

            // Also test trimmed password if user had trailing/leading space
            if (!password.equals(password.trim())) {
                PBEKeySpec trimmedSpec = new PBEKeySpec(password.trim().toCharArray(), salt, 10000, 256);
                byte[] trimmedHash = skf.generateSecret(trimmedSpec).getEncoded();
                return MessageDigest.isEqual(expectedHash, trimmedHash);
            }

            return false;
        } catch (Exception e) {
            return password.equals(storedHash) || password.trim().equals(storedHash.trim());
        }
    }
}
