package com.kcau.dining;

import com.kcau.dining.database.DatabaseConnection;
import com.kcau.dining.database.DatabaseInitializer;
import com.kcau.dining.model.MenuItem;
import com.kcau.dining.model.Order;
import com.kcau.dining.model.OrderItem;
import com.kcau.dining.model.Payment;
import com.kcau.dining.model.User;
import com.kcau.dining.service.*;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.*;

/**
 * KCAU Smart Dining System - Interactive Terminal Console Application
 * Allows testing and screenshotting all database tables, menus, orders,
 * user authentication, order placement, and kitchen status in the terminal.
 */
public class ConsoleCli {

    private static final UserService userService = new UserService();
    private static final MenuService menuService = new MenuService();
    private static final OrderService orderService = new OrderService();
    private static final PaymentService paymentService = new PaymentService();
    private static final ReportService reportService = new ReportService();

    public static void main(String[] args) {
        // 1. Ensure Database & Seed Data are ready
        DatabaseInitializer.init();

        // 2. If non-interactive flag passed, print tables and exit
        if (args != null && args.length > 0 && ("--tables".equalsIgnoreCase(args[0]) || "-t".equalsIgnoreCase(args[0]))) {
            printAllTables();
            return;
        }

        // 3. Print Welcome Banner and Complete Tables for Terminal Screenshot
        printHeader();
        printAllTables();

        // 4. Run Interactive Menu if standard input is available
        Scanner scanner = new Scanner(System.in);
        boolean running = true;

        while (running) {
            printMenuOptions();
            System.out.print("👉 Enter your choice [0-9]: ");
            String input;
            try {
                if (!scanner.hasNextLine()) break;
                input = scanner.nextLine().trim();
            } catch (Exception e) {
                break;
            }

            switch (input) {
                case "1" -> printMenuTable();
                case "2" -> printOrdersTable();
                case "3" -> printUsersTable();
                case "4" -> printPaymentsTable();
                case "5" -> testUserLogin(scanner);
                case "6" -> testPlaceOrder(scanner);
                case "7" -> testUpdateOrderStatus(scanner);
                case "8" -> printSalesReport();
                case "9" -> startWebServer(args);
                case "0", "exit", "quit", "q" -> {
                    System.out.println("\n👋 Exiting KCAU Smart Dining Terminal. Goodbye!");
                    running = false;
                }
                default -> System.out.println("⚠️ Invalid option. Please enter a number between 0 and 9.");
            }
        }
    }

    private static void printHeader() {
        System.out.println();
        System.out.println("==========================================================================================================");
        System.out.println("☕ KCAU SMART DINING SYSTEM - INTERACTIVE TERMINAL CONSOLE");
        System.out.println("🏫 KCA UNIVERSITY • DEPARTMENT OF SOFTWARE DEVELOPMENT • CAT 1");
        System.out.println("💾 Database: SQLite (data/dining.db) • Engine: OpenJDK 25");
        System.out.println("==========================================================================================================");
    }

    public static void printAllTables() {
        printUsersTable();
        printMenuTable();
        printOrdersTable();
        printPaymentsTable();
    }

    public static void printUsersTable() {
        System.out.println("\n👤 1. USERS & ROLES TABLE [SQLite: users]");
        System.out.println("+----------------+-------------------------------+--------------+----------+----------------------------+");
        System.out.printf("| %-14s | %-29s | %-12s | %-8s | %-26s |%n", "ID", "FULL NAME", "STUDENT ID", "ROLE", "CREATED AT");
        System.out.println("+----------------+-------------------------------+--------------+----------+----------------------------+");
        try (Connection conn = DatabaseConnection.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SELECT id, name, student_id, role, created_at FROM users ORDER BY role DESC")) {
            while (rs.next()) {
                System.out.printf("| %-14s | %-29s | %-12s | %-8s | %-26s |%n",
                    truncate(rs.getString("id"), 14),
                    truncate(rs.getString("name"), 29),
                    truncate(rs.getString("student_id"), 12),
                    truncate(rs.getString("role"), 8),
                    truncate(rs.getString("created_at"), 26)
                );
            }
        } catch (Exception e) {
            System.err.println("Error reading users: " + e.getMessage());
        }
        System.out.println("+----------------+-------------------------------+--------------+----------+----------------------------+");
    }

    public static void printMenuTable() {
        System.out.println("\n🍽️ 2. CAFETERIA MENU ITEMS TABLE (table manus) [SQLite: menu_items]");
        System.out.println("+--------+-----------------------+-----------+------------+-----------+------------------------------------+");
        System.out.printf("| %-6s | %-21s | %-9s | %-10s | %-9s | %-34s |%n", "FOOD ID", "DISH NAME", "CATEGORY", "PRICE (KES)", "STATUS", "DESCRIPTION");
        System.out.println("+--------+-----------------------+-----------+------------+-----------+------------------------------------+");
        try (Connection conn = DatabaseConnection.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SELECT id, name, category, price, available, description FROM menu_items ORDER BY id ASC")) {
            while (rs.next()) {
                String status = rs.getInt("available") == 1 ? "AVAILABLE" : "SOLD OUT";
                String price = String.format("KES %.2f", rs.getDouble("price"));
                System.out.printf("| %-6s | %-21s | %-9s | %-10s | %-9s | %-34s |%n",
                    truncate(rs.getString("id"), 6),
                    truncate(rs.getString("name"), 21),
                    truncate(rs.getString("category"), 9),
                    truncate(price, 10),
                    truncate(status, 9),
                    truncate(rs.getString("description"), 34)
                );
            }
        } catch (Exception e) {
            System.err.println("Error reading menu_items: " + e.getMessage());
        }
        System.out.println("+--------+-----------------------+-----------+------------+-----------+------------------------------------+");
    }

    public static void printOrdersTable() {
        System.out.println("\n🧾 3. ORDERS & LINE ITEMS TABLE [SQLite: orders & order_items]");
        System.out.println("+------------+--------------------+----------------------------+------------+-----------+------------------------------------+");
        System.out.printf("| %-10s | %-18s | %-26s | %-10s | %-9s | %-34s |%n", "ORDER ID", "CUSTOMER NAME", "DATE / TIME", "TOTAL", "STATUS", "ITEMS ORDERED");
        System.out.println("+------------+--------------------+----------------------------+------------+-----------+------------------------------------+");
        String ordersSql = "SELECT o.id, o.customer_name, o.date, o.total, o.order_status FROM orders o ORDER BY o.date DESC LIMIT 15";
        try (Connection conn = DatabaseConnection.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(ordersSql)) {
            boolean hasOrders = false;
            while (rs.next()) {
                hasOrders = true;
                String orderId = rs.getString("id");
                String itemsSummary = getItemsSummary(conn, orderId);
                String total = String.format("KES %.2f", rs.getDouble("total"));
                System.out.printf("| %-10s | %-18s | %-26s | %-10s | %-9s | %-34s |%n",
                    truncate(orderId, 10),
                    truncate(rs.getString("customer_name"), 18),
                    truncate(rs.getString("date"), 26),
                    truncate(total, 10),
                    truncate(rs.getString("order_status"), 9),
                    truncate(itemsSummary, 34)
                );
            }
            if (!hasOrders) {
                System.out.printf("| %-10s | %-18s | %-26s | %-10s | %-9s | %-34s |%n", "-", "No orders found", "-", "-", "-", "-");
            }
        } catch (Exception e) {
            System.err.println("Error reading orders: " + e.getMessage());
        }
        System.out.println("+------------+--------------------+----------------------------+------------+-----------+------------------------------------+");
    }

    public static void printPaymentsTable() {
        System.out.println("\n💳 4. PAYMENTS AUDIT LEDGER TABLE [SQLite: payments]");
        System.out.println("+--------------+------------+--------+------------+-----------+---------------+----------------------------+");
        System.out.printf("| %-12s | %-10s | %-6s | %-10s | %-9s | %-13s | %-26s |%n", "PAYMENT ID", "ORDER ID", "METHOD", "AMOUNT", "STATUS", "REFERENCE", "SETTLEMENT TIME");
        System.out.println("+--------------+------------+--------+------------+-----------+---------------+----------------------------+");
        try (Connection conn = DatabaseConnection.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SELECT id, order_id, method, amount, status, reference, created_at FROM payments ORDER BY created_at DESC LIMIT 15")) {
            boolean hasPay = false;
            while (rs.next()) {
                hasPay = true;
                String amt = String.format("KES %.2f", rs.getDouble("amount"));
                System.out.printf("| %-12s | %-10s | %-6s | %-10s | %-9s | %-13s | %-26s |%n",
                    truncate(rs.getString("id"), 12),
                    truncate(rs.getString("order_id"), 10),
                    truncate(rs.getString("method"), 6),
                    truncate(amt, 10),
                    truncate(rs.getString("status"), 9),
                    truncate(rs.getString("reference"), 13),
                    truncate(rs.getString("created_at"), 26)
                );
            }
            if (!hasPay) {
                System.out.printf("| %-12s | %-10s | %-6s | %-10s | %-9s | %-13s | %-26s |%n", "-", "-", "-", "-", "-", "-", "-");
            }
        } catch (Exception e) {
            System.err.println("Error reading payments: " + e.getMessage());
        }
        System.out.println("+--------------+------------+--------+------------+-----------+---------------+----------------------------+");
    }

    private static void printMenuOptions() {
        System.out.println("\n📋 TERMINAL CONTROL ACTIONS:");
        System.out.println("  [1] 🍽️ View Cafeteria Menus Table");
        System.out.println("  [2] 🧾 View Customer Orders Table");
        System.out.println("  [3] 👤 View Users & Roles Table");
        System.out.println("  [4] 💳 View Payments Ledger Table");
        System.out.println("  [5] 🔑 Test User Login / Authentication");
        System.out.println("  [6] 🛒 Place a New Order via Terminal");
        System.out.println("  [7] 👨‍🍳 Update Order Kitchen Status (PREPARING / READY / COLLECTED)");
        System.out.println("  [8] 📊 View Administrator Sales & Revenue Report");
        System.out.println("  [9] 🚀 Start Full Web Server (http://localhost:3000)");
        System.out.println("  [0] 🚪 Exit Terminal");
        System.out.println("----------------------------------------------------------------------------------------------------------");
    }

    private static void testUserLogin(Scanner scanner) {
        System.out.println("\n🔑 --- USER LOGIN VERIFICATION ---");
        System.out.println("Tip: You can enter Student ID (e.g. KCA/1234/23), Staff ID (STAFF/001), Admin ID (ADMIN/001), or simply role 'student', 'staff', 'admin'");
        System.out.print("Enter Student ID / Username: ");
        String username = scanner.nextLine().trim();
        if (username.isEmpty()) {
            System.out.println("❌ Username cannot be empty.");
            return;
        }

        System.out.print("Enter Password (default: password123): ");
        String password = scanner.nextLine().trim();

        try {
            User user = userService.authenticate(username, password);
            System.out.println("\n✅ ========================================================");
            System.out.println("   AUTHENTICATION SUCCESSFUL!");
            System.out.println("   Name:       " + user.getName());
            System.out.println("   Student ID: " + user.getStudentId());
            System.out.println("   Role:       " + user.getRole().toUpperCase());
            System.out.println("   Account ID: " + user.getId());
            System.out.println("==========================================================");
        } catch (Exception e) {
            System.out.println("\n❌ LOGIN FAILED: " + e.getMessage());
        }
    }

    private static void testPlaceOrder(Scanner scanner) {
        System.out.println("\n🛒 --- PLACE NEW ORDER VIA TERMINAL ---");
        System.out.print("Enter Student Registration ID (e.g. KCA/1234/23): ");
        String studentId = scanner.nextLine().trim();
        if (studentId.isEmpty()) studentId = "KCA/1234/23";

        System.out.print("Enter Customer Name (e.g. Alex Kiprop): ");
        String name = scanner.nextLine().trim();
        if (name.isEmpty()) name = "Alex Kiprop";

        printMenuTable();
        System.out.println("\nEnter food ID(s) to order (e.g. 'food-1' or 'food-1,food-2'): ");
        System.out.print("Food ID: ");
        String foodId = scanner.nextLine().trim();
        if (foodId.isEmpty()) foodId = "food-1";

        System.out.print("Quantity (e.g. 1, 2): ");
        String qtyStr = scanner.nextLine().trim();
        int qty = 1;
        try { qty = Integer.parseInt(qtyStr); } catch (Exception ignored) {}

        try {
            MenuItem item = menuService.getMenuItemById(foodId);
            if (item == null) {
                System.out.println("❌ Menu item not found with ID: " + foodId);
                return;
            }

            List<OrderItem> items = List.of(new OrderItem(item.getId(), item.getName(), qty, item.getPrice()));
            Order order = orderService.createOrder(studentId, name, items);

            // Record simulated payment
            Payment payment = paymentService.recordPayment(
                order.getOrderId(),
                "MPESA",
                order.getTotalAmount(),
                "COMPLETED",
                "MPESA-" + UUID.randomUUID().toString().substring(0, 6).toUpperCase()
            );

            System.out.println("\n🎉 ========================================================");
            System.out.println("   ORDER PLACED SUCCESSFULLY IN SQLITE!");
            System.out.println("   Order ID:        " + order.getOrderId());
            System.out.println("   Customer:        " + order.getCustomerName() + " (" + order.getUserId() + ")");
            System.out.println("   Total Charged:   KES " + String.format("%.2f", order.getTotalAmount()));
            System.out.println("   Initial Status:  " + order.getStatus());
            System.out.println("   M-Pesa Receipt:  " + payment.getReference());
            System.out.println("==========================================================");

            printOrdersTable();
        } catch (Exception e) {
            System.out.println("❌ Failed to place order: " + e.getMessage());
        }
    }

    private static void testUpdateOrderStatus(Scanner scanner) {
        System.out.println("\n👨‍🍳 --- KITCHEN STATUS UPDATE ---");
        System.out.print("Enter Order ID to update (e.g. ORD-235267): ");
        String orderId = scanner.nextLine().trim();
        if (orderId.isEmpty()) {
            System.out.println("❌ Order ID cannot be empty.");
            return;
        }

        System.out.println("Select New Status:");
        System.out.println("  [1] PREPARING (Chef cooking dish)");
        System.out.println("  [2] READY (Plated for student collection)");
        System.out.println("  [3] COLLECTED (Handed over to student)");
        System.out.print("Select [1-3]: ");
        String choice = scanner.nextLine().trim();

        String status = switch (choice) {
            case "1" -> "PREPARING";
            case "2" -> "READY";
            case "3" -> "COLLECTED";
            default -> choice.toUpperCase();
        };

        try {
            boolean updated = orderService.updateOrderStatus(orderId, status);
            if (updated) {
                System.out.println("✅ Order " + orderId + " updated to status: " + status);
                printOrdersTable();
            } else {
                System.out.println("❌ Order not found with ID: " + orderId);
            }
        } catch (Exception e) {
            System.out.println("❌ Error updating order: " + e.getMessage());
        }
    }

    private static void printSalesReport() {
        System.out.println("\n📊 --- ADMINISTRATOR SALES & REVENUE REPORT ---");
        try {
            Map<String, Object> summary = reportService.getSalesSummary();
            System.out.println("+--------------------------------------+--------------------+");
            System.out.printf("| %-36s | %-18s |%n", "METRIC", "VALUE");
            System.out.println("+--------------------------------------+--------------------+");
            System.out.printf("| %-36s | %-18s |%n", "Total Completed Orders", summary.get("totalOrders"));
            System.out.printf("| %-36s | KES %-14s |%n", "Total Gross Revenue", summary.get("totalRevenue"));
            System.out.printf("| %-36s | KES %-14s |%n", "Average Order Value", summary.get("averageOrderValue"));
            System.out.printf("| %-36s | %-18s |%n", "Pending Orders (Awaiting Chef)", summary.get("pendingOrders"));
            System.out.printf("| %-36s | %-18s |%n", "Preparing Orders (Cooking)", summary.get("preparingOrders"));
            System.out.printf("| %-36s | %-18s |%n", "Ready for Pickup", summary.get("readyOrders"));
            System.out.printf("| %-36s | %-18s |%n", "Collected Orders", summary.get("collectedOrders"));
            System.out.printf("| %-36s | %-18s |%n", "Registered Campus Users", summary.get("registeredUsers"));
            System.out.println("+--------------------------------------+--------------------+");

            List<Map<String, Object>> popularity = reportService.getItemPopularity();
            if (!popularity.isEmpty()) {
                System.out.println("\n🏆 TOP BESTSELLING DISHES:");
                for (int i = 0; i < popularity.size(); i++) {
                    Map<String, Object> dish = popularity.get(i);
                    System.out.printf("  %d. %-22s - %s portions sold (Revenue: KES %s)%n",
                        i + 1, dish.get("name"), dish.get("quantitySold"), dish.get("revenue"));
                }
            }
        } catch (Exception e) {
            System.err.println("Error calculating sales summary: " + e.getMessage());
        }
    }

    private static void startWebServer(String[] args) {
        System.out.println("\n🚀 Launching background HTTP Web Server on port 3000...");
        try {
            Server.main(args);
        } catch (Exception e) {
            System.err.println("Web server error: " + e.getMessage());
        }
    }

    private static String truncate(String val, int max) {
        if (val == null) return "";
        return (val.length() <= max) ? val : val.substring(0, Math.max(0, max - 3)) + "...";
    }

    private static String getItemsSummary(Connection conn, String orderId) {
        try (PreparedStatement pstmt = conn.prepareStatement(
                "SELECT food_name, quantity FROM order_items WHERE order_id = ?")) {
            pstmt.setString(1, orderId);
            try (ResultSet rs = pstmt.executeQuery()) {
                StringBuilder sb = new StringBuilder();
                while (rs.next()) {
                    if (sb.length() > 0) sb.append(", ");
                    sb.append(rs.getString("food_name")).append(" (").append(rs.getInt("quantity")).append(")");
                }
                return sb.toString();
            }
        } catch (Exception e) {
            return "-";
        }
    }
}

