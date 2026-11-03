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

        System.out.println("=================================================");
        System.out.println("☕ KCAU Smart Dining System - Modular Java Backend");
        System.out.printf("🚀 Server running on http://localhost:%d%n", port);
        System.out.println("📁 Serving static files from: " + PUBLIC_DIR);
        System.out.println("💾 Database: SQLite (" + DatabaseConnection.getDbPath() + ")");
        System.out.println("🔐 Security: PBKDF2 Hashing + HMAC-SHA256 JWT");
        System.out.println("📋 Roles Enabled: Student, Dining Staff, Admin");
        System.out.println("=================================================");
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
