package com.kcau.dining;

import com.kcau.dining.database.DatabaseConnection;
import com.kcau.dining.database.DatabaseInitializer;
import com.kcau.dining.handler.*;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;

import java.io.File;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.URLConnection;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.Executors;

/**
 * KCAU Smart Dining System - Main Backend Server Entrypoint
 * Standalone virtual-threaded Java HTTP server coordinating SQLite database and REST endpoints.
 */
public class Server {

    private static final int DEFAULT_PORT = 3000;
    private static final Path PUBLIC_DIR = Paths.get("public").toAbsolutePath();

    public static void main(String[] args) throws IOException {
        // 1. Initialize SQLite Database Schema & Seed Data
        DatabaseInitializer.init();

        // Check if user simply wants to print database tables and exit
        if (args != null && args.length > 0 && ("--tables".equalsIgnoreCase(args[0]) || "-t".equalsIgnoreCase(args[0]) || "--show-tables".equalsIgnoreCase(args[0]))) {
            printDatabaseTables();
            return;
        }

        // 2. Determine Port
        int port = DEFAULT_PORT;
        String envPort = System.getenv("PORT");
        if (envPort != null && !envPort.isBlank()) {
            try {
                port = Integer.parseInt(envPort.trim());
            } catch (NumberFormatException ignored) {}
        } else if (args != null && args.length > 0) {
            try {
                port = Integer.parseInt(args[0].trim());
            } catch (NumberFormatException ignored) {}
        }

        HttpServer server;
        try {
            server = HttpServer.create(new InetSocketAddress(port), 0);
        } catch (IOException e) {
            int fallbackPort = (port == 3000) ? 8080 : 3001;
            System.out.printf("⚠️  Port %d unavailable, switching to port %d...%n", port, fallbackPort);
            port = fallbackPort;
            server = HttpServer.create(new InetSocketAddress(port), 0);
        }

        // 3. Register Modular Handlers
        UserHandler userHandler = new UserHandler();
        MenuHandler menuHandler = new MenuHandler();
        OrderHandler orderHandler = new OrderHandler();
        PaymentHandler paymentHandler = new PaymentHandler();
        ReportHandler reportHandler = new ReportHandler();

        // Auth & User routes
        server.createContext("/api/signup", userHandler);
        server.createContext("/api/login", userHandler);
        server.createContext("/api/me", userHandler);
        server.createContext("/api/users", userHandler);

        // Menu routes
        server.createContext("/api/menu", menuHandler);

        // Order routes
        server.createContext("/api/orders", orderHandler);

        // Payment routes
        server.createContext("/api/payments", paymentHandler);

        // Report & Analytics routes
        server.createContext("/api/reports", reportHandler);

        // System Health & Diagnostics route
        server.createContext("/api/status", new StatusHandler());

        // Static files and Single Page App (SPA) fallback
        server.createContext("/", new StaticFileHandler());

        // 4. Configure Virtual Thread Executor (Project Loom)
        server.setExecutor(Executors.newVirtualThreadPerTaskExecutor());
        server.start();

        System.out.println("==========================================================================================================");
        System.out.println("☕ KCAU SMART DINING SYSTEM - MODULAR JAVA BACKEND (OPENJDK 25 + VIRTUAL THREADS)");
        System.out.printf("🚀 Server running on http://localhost:%d%n", port);
        System.out.println("📁 Serving static files from: " + PUBLIC_DIR);
        System.out.println("💾 Database: SQLite (" + DatabaseConnection.getDbPath() + ")");
        System.out.println("🔐 Security: PBKDF2 Hashing + HMAC-SHA256 JWT");
        System.out.println("📋 Roles Enabled: Student, Dining Staff, Admin");
        System.out.println("==========================================================================================================");

        // Print full terminal ASCII tables for user screenshot & grading evidence
        printDatabaseTables();

        System.out.printf("🟢 Server listening on http://localhost:%d%n", port);
        System.out.printf("🌐 Open http://localhost:%d in your browser to access Student, Staff, and Admin portals!%n", port);
        System.out.println("📡 Incoming live HTTP requests will be logged below:");
        System.out.println("----------------------------------------------------------------------------------------------------------");
    }

    /**
     * Prints formatted ASCII tables of database entities for terminal inspection,
     * grading screenshots, and technical documentation evidence.
     */
    public static void printDatabaseTables() {
        try (java.sql.Connection conn = DatabaseConnection.getConnection();
             java.sql.Statement stmt = conn.createStatement()) {

            // 1. Users Table
            System.out.println("\n👤 1. USERS & ROLES TABLE [SQLite: users]");
            System.out.println("+----------------+-------------------------------+--------------+----------+----------------------------+");
            System.out.printf("| %-14s | %-29s | %-12s | %-8s | %-26s |%n", "ID", "FULL NAME", "STUDENT ID", "ROLE", "CREATED AT");
            System.out.println("+----------------+-------------------------------+--------------+----------+----------------------------+");
            try (java.sql.ResultSet rs = stmt.executeQuery("SELECT id, name, student_id, role, created_at FROM users ORDER BY role DESC")) {
                while (rs.next()) {
                    System.out.printf("| %-14s | %-29s | %-12s | %-8s | %-26s |%n",
                        truncate(rs.getString("id"), 14),
                        truncate(rs.getString("name"), 29),
                        truncate(rs.getString("student_id"), 12),
                        truncate(rs.getString("role"), 8),
                        truncate(rs.getString("created_at"), 26)
                    );
                }
            }
            System.out.println("+----------------+-------------------------------+--------------+----------+----------------------------+");

            // 2. Menu Items Table
            System.out.println("\n🍽️ 2. CAFETERIA MENU ITEMS TABLE [SQLite: menu_items]");
            System.out.println("+--------+-----------------------+-----------+------------+-----------+------------------------------------+");
            System.out.printf("| %-6s | %-21s | %-9s | %-10s | %-9s | %-34s |%n", "FOOD ID", "DISH NAME", "CATEGORY", "PRICE (KES)", "STATUS", "DESCRIPTION");
            System.out.println("+--------+-----------------------+-----------+------------+-----------+------------------------------------+");
            try (java.sql.ResultSet rs = stmt.executeQuery("SELECT id, name, category, price, available, description FROM menu_items ORDER BY id ASC")) {
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
            }
            System.out.println("+--------+-----------------------+-----------+------------+-----------+------------------------------------+");

            // 3. Orders & Order Items Table
            System.out.println("\n🧾 3. ORDERS & LINE ITEMS TABLE [SQLite: orders & order_items]");
            System.out.println("+------------+--------------------+----------------------------+------------+-----------+------------------------------------+");
            System.out.printf("| %-10s | %-18s | %-26s | %-10s | %-9s | %-34s |%n", "ORDER ID", "CUSTOMER NAME", "DATE / TIME", "TOTAL", "STATUS", "ITEMS ORDERED");
            System.out.println("+------------+--------------------+----------------------------+------------+-----------+------------------------------------+");
            String ordersSql = "SELECT o.id, o.customer_name, o.date, o.total, o.order_status FROM orders o ORDER BY o.date DESC LIMIT 10";
            try (java.sql.ResultSet rs = stmt.executeQuery(ordersSql)) {
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
                    System.out.printf("| %-10s | %-18s | %-26s | %-10s | %-9s | %-34s |%n", "-", "No orders yet", "-", "-", "-", "-");
                }
            }
            System.out.println("+------------+--------------------+----------------------------+------------+-----------+------------------------------------+");

            // 4. Payments Table
            System.out.println("\n💳 4. PAYMENTS AUDIT LEDGER TABLE [SQLite: payments]");
            System.out.println("+--------------+------------+--------+------------+-----------+---------------+----------------------------+");
            System.out.printf("| %-12s | %-10s | %-6s | %-10s | %-9s | %-13s | %-26s |%n", "PAYMENT ID", "ORDER ID", "METHOD", "AMOUNT", "STATUS", "REFERENCE", "SETTLEMENT TIME");
            System.out.println("+--------------+------------+--------+------------+-----------+---------------+----------------------------+");
            try (java.sql.ResultSet rs = stmt.executeQuery("SELECT id, order_id, method, amount, status, reference, created_at FROM payments ORDER BY created_at DESC LIMIT 10")) {
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
            }
            System.out.println("+--------------+------------+--------+------------+-----------+---------------+----------------------------+");

        } catch (Exception e) {
            System.err.println("Notice: Could not print database tables: " + e.getMessage());
        }
        System.out.println();
    }

    private static String truncate(String val, int max) {
        if (val == null) return "";
        return (val.length() <= max) ? val : val.substring(0, Math.max(0, max - 3)) + "...";
    }

    private static String getItemsSummary(java.sql.Connection conn, String orderId) {
        try (java.sql.PreparedStatement pstmt = conn.prepareStatement(
                "SELECT food_name, quantity FROM order_items WHERE order_id = ?")) {
            pstmt.setString(1, orderId);
            try (java.sql.ResultSet rs = pstmt.executeQuery()) {
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

    // -------------------------------------------------------------
    // Status Handler
    // -------------------------------------------------------------
    static class StatusHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (HttpHelper.handleCorsPreflight(exchange)) return;

            Map<String, Object> status = new HashMap<>();
            status.put("status", "KCAU Smart Dining Java Backend is running!");
            status.put("database", "SQLite (" + DatabaseConnection.getDbPath() + ")");
            status.put("sqliteExists", new File(DatabaseConnection.getDbPath()).exists());
            status.put("timestamp", Instant.now().toString());
            status.put("runtime", System.getProperty("java.version"));
            HttpHelper.sendJson(exchange, 200, status);
        }
    }

    // -------------------------------------------------------------
    // Static Files & SPA Fallback Handler
    // -------------------------------------------------------------
    static class StaticFileHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (HttpHelper.handleCorsPreflight(exchange)) return;

            String rawPath = exchange.getRequestURI().getPath();
            String pathStr = URLDecoder.decode(rawPath, StandardCharsets.UTF_8);

            if (pathStr.startsWith("/api/")) {
                HttpHelper.sendError(exchange, 404, "API endpoint not found");
                return;
            }

            Path requestedFile;
            if ("/".equals(pathStr) || pathStr.isBlank()) {
                requestedFile = PUBLIC_DIR.resolve("index.html").normalize();
            } else {
                String subPath = pathStr.startsWith("/") ? pathStr.substring(1) : pathStr;
                requestedFile = PUBLIC_DIR.resolve(subPath).normalize();
            }

            // Prevent path traversal
            if (!requestedFile.startsWith(PUBLIC_DIR)) {
                HttpHelper.sendError(exchange, 403, "Access Denied");
                return;
            }

            // SPA Fallback: if not found or is directory, serve index.html
            if (!Files.exists(requestedFile) || Files.isDirectory(requestedFile)) {
                requestedFile = PUBLIC_DIR.resolve("index.html").normalize();
            }

            if (!Files.exists(requestedFile)) {
                HttpHelper.sendError(exchange, 404, "Frontend file not found");
                return;
            }

            String contentType = determineContentType(requestedFile);
            exchange.getResponseHeaders().set("Content-Type", contentType);

            byte[] fileBytes = Files.readAllBytes(requestedFile);
            exchange.sendResponseHeaders(200, fileBytes.length);
            try (OutputStream os = exchange.getResponseBody()) {
                os.write(fileBytes);
            }
        }

        private String determineContentType(Path file) {
            String fileName = file.getFileName().toString().toLowerCase();
            if (fileName.endsWith(".html")) return "text/html; charset=utf-8";
            if (fileName.endsWith(".css")) return "text/css; charset=utf-8";
            if (fileName.endsWith(".js")) return "application/javascript; charset=utf-8";
            if (fileName.endsWith(".json")) return "application/json; charset=utf-8";
            if (fileName.endsWith(".png")) return "image/png";
            if (fileName.endsWith(".jpg") || fileName.endsWith(".jpeg")) return "image/jpeg";
            if (fileName.endsWith(".svg")) return "image/svg+xml";
            if (fileName.endsWith(".ico")) return "image/x-icon";
            if (fileName.endsWith(".webp")) return "image/webp";
            return URLConnection.guessContentTypeFromName(fileName);
        }
    }
}
