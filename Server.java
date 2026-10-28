import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;

import javax.crypto.Mac;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import javax.crypto.spec.SecretKeySpec;
import java.io.*;
import java.net.InetSocketAddress;
import java.net.URLConnection;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * KCAU Smart Dining System - Java Backend Server
 * 
 * Standalone lightweight HTTP server providing full API compatibility with server.js:
 *  - POST /api/signup   (User registration with password hashing)
 *  - POST /api/login    (User authentication with HMAC-SHA256 JWT tokens)
 *  - GET  /api/me       (Current authenticated user session)
 *  - GET  /api/status   (Backend health check)
 *  - Static file server (Serves public/ directory with fallback to index.html)
 */
public class Server {

    private static final int DEFAULT_PORT = 3000;
    private static final String JWT_SECRET = Optional.ofNullable(System.getenv("JWT_SECRET"))
            .orElse("super_secret_cafeteria_key");
    private static final Path PUBLIC_DIR = Paths.get("public").toAbsolutePath();

    // In-memory user database (studentId -> User)
    private static final Map<String, User> userDatabase = new ConcurrentHashMap<>();

    static {
        // Pre-seed demo student for instant preview
        String defaultHash = PasswordUtil.hashPassword("password123");
        userDatabase.put("KCA/1234/23", new User("demo-1", "Alex Kiprop", "KCA/1234/23", defaultHash));
    }

    public static void main(String[] args) throws IOException {
        int port = DEFAULT_PORT;
        String envPort = System.getenv("PORT");
        if (envPort != null && !envPort.isBlank()) {
            try {
                port = Integer.parseInt(envPort.trim());
            } catch (NumberFormatException ignored) {}
        } else if (args.length > 0) {
            try {
                port = Integer.parseInt(args[0].trim());
            } catch (NumberFormatException ignored) {}
        }

        HttpServer server;
        try {
            server = HttpServer.create(new InetSocketAddress(port), 0);
        } catch (IOException e) {
            // If default port is taken, fallback to 8080
            int fallbackPort = (port == 3000) ? 8080 : 3001;
            System.out.printf("⚠️  Port %d unavailable, switching to port %d...%n", port, fallbackPort);
            port = fallbackPort;
            server = HttpServer.create(new InetSocketAddress(port), 0);
        }

        // Setup API routes
        server.createContext("/api/signup", new SignupHandler());
        server.createContext("/api/login", new LoginHandler());
        server.createContext("/api/me", new MeHandler());
        server.createContext("/api/status", new StatusHandler());

        // Setup Static file route & SPA fallback
        server.createContext("/", new StaticFileHandler());

        server.setExecutor(Executors.newVirtualThreadPerTaskExecutor());
        server.start();

        System.out.println("=================================================");
        System.out.println("☕ KCAU Smart Dining System - Java Backend");
        System.out.printf("🚀 Server running on http://localhost:%d%n", port);
        System.out.println("📁 Serving static files from: " + PUBLIC_DIR);
        System.out.println("🔐 JWT Authentication enabled");
        System.out.println("=================================================");
    }

    // -------------------------------------------------------------
    // Domain Models
    // -------------------------------------------------------------
    public static class User {
        private final String id;
        private final String name;
        private final String studentId;
        private final String passwordHash;
        private final Instant createdAt;

        public User(String id, String name, String studentId, String passwordHash) {
            this.id = id;
            this.name = name;
            this.studentId = studentId;
            this.passwordHash = passwordHash;
            this.createdAt = Instant.now();
        }

        public String getId() { return id; }
        public String getName() { return name; }
        public String getStudentId() { return studentId; }
        public String getPasswordHash() { return passwordHash; }
        public Instant getCreatedAt() { return createdAt; }
    }

    // -------------------------------------------------------------
    // API Handlers
    // -------------------------------------------------------------

    // POST /api/signup
    static class SignupHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            addCorsHeaders(exchange);
            if ("OPTIONS".equalsIgnoreCase(exchange.getRequestMethod())) {
                exchange.sendResponseHeaders(204, -1);
                return;
            }

            if (!"POST".equalsIgnoreCase(exchange.getRequestMethod())) {
                sendJsonResponse(exchange, 405, Map.of("error", "Method not allowed"));
                return;
            }

            Map<String, String> body = parseJsonBody(exchange);
            String name = body.get("name");
            String studentId = body.get("studentId");
            String password = body.get("password");

            if (name == null || name.isBlank() ||
                studentId == null || studentId.isBlank() ||
                password == null || password.isBlank()) {
                sendJsonResponse(exchange, 400, Map.of("error", "Please provide all required fields"));
                return;
            }

            studentId = studentId.trim();
            if (userDatabase.containsKey(studentId)) {
                sendJsonResponse(exchange, 400, Map.of("error", "An account with this Student ID already exists"));
                return;
            }

            String hashedPassword = PasswordUtil.hashPassword(password);
            String userId = UUID.randomUUID().toString();
            User newUser = new User(userId, name.trim(), studentId, hashedPassword);
            userDatabase.put(studentId, newUser);

            sendJsonResponse(exchange, 201, Map.of("message", "Account created successfully!"));
        }
    }

    // POST /api/login
    static class LoginHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            addCorsHeaders(exchange);
            if ("OPTIONS".equalsIgnoreCase(exchange.getRequestMethod())) {
                exchange.sendResponseHeaders(204, -1);
                return;
            }

            if (!"POST".equalsIgnoreCase(exchange.getRequestMethod())) {
                sendJsonResponse(exchange, 405, Map.of("error", "Method not allowed"));
                return;
            }

            Map<String, String> body = parseJsonBody(exchange);
            String studentId = body.get("studentId");
            String password = body.get("password");

            if (studentId == null || studentId.isBlank() || password == null || password.isBlank()) {
                sendJsonResponse(exchange, 400, Map.of("error", "Please provide Student ID and password"));
                return;
            }

            studentId = studentId.trim();
            User user = userDatabase.get(studentId);
            if (user == null) {
                sendJsonResponse(exchange, 401, Map.of("error", "No account found with this Student ID. Please sign up first!"));
                return;
            }

            if (!PasswordUtil.verifyPassword(password, user.getPasswordHash())) {
                sendJsonResponse(exchange, 401, Map.of("error", "Incorrect password. Please try again."));
                return;
            }

            long expSeconds = Instant.now().plusSeconds(7 * 24 * 3600).getEpochSecond();
            Map<String, Object> claims = new HashMap<>();
            claims.put("id", user.getId());
            claims.put("name", user.getName());
            claims.put("studentId", user.getStudentId());
            claims.put("exp", expSeconds);

            String token = JwtUtil.generateToken(claims, JWT_SECRET);

            Map<String, Object> resp = new HashMap<>();
            resp.put("message", "Logged in successfully");
            resp.put("token", token);
            resp.put("name", user.getName());
            sendJsonResponse(exchange, 200, resp);
        }
    }

    // GET /api/me
    static class MeHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            addCorsHeaders(exchange);
            if ("OPTIONS".equalsIgnoreCase(exchange.getRequestMethod())) {
                exchange.sendResponseHeaders(204, -1);
                return;
            }

            if (!"GET".equalsIgnoreCase(exchange.getRequestMethod())) {
                sendJsonResponse(exchange, 405, Map.of("error", "Method not allowed"));
                return;
            }

            String authHeader = exchange.getRequestHeaders().getFirst("Authorization");
            if (authHeader == null || !authHeader.startsWith("Bearer ")) {
                sendJsonResponse(exchange, 401, Map.of("error", "No token provided"));
                return;
            }

            String token = authHeader.substring(7).trim();
            Map<String, Object> claims = JwtUtil.verifyToken(token, JWT_SECRET);
            if (claims == null) {
                sendJsonResponse(exchange, 401, Map.of("error", "Session expired. Please log in again."));
                return;
            }

            Map<String, Object> resp = new HashMap<>();
            resp.put("name", claims.get("name"));
            resp.put("studentId", claims.get("studentId"));
            sendJsonResponse(exchange, 200, resp);
        }
    }

    // GET /api/status
    static class StatusHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            addCorsHeaders(exchange);
            if ("OPTIONS".equalsIgnoreCase(exchange.getRequestMethod())) {
                exchange.sendResponseHeaders(204, -1);
                return;
            }

            Map<String, Object> status = new HashMap<>();
            status.put("status", "Java Backend is running!");
            status.put("db", "in-memory");
            status.put("timestamp", Instant.now().toString());
            status.put("registeredUsers", userDatabase.size());
            sendJsonResponse(exchange, 200, status);
        }
    }

    // -------------------------------------------------------------
    // Static Files & SPA Fallback Handler
    // -------------------------------------------------------------
    static class StaticFileHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            addCorsHeaders(exchange);
            if ("OPTIONS".equalsIgnoreCase(exchange.getRequestMethod())) {
                exchange.sendResponseHeaders(204, -1);
                return;
            }

            String rawPath = exchange.getRequestURI().getPath();
            String pathStr = URLDecoder.decode(rawPath, StandardCharsets.UTF_8);

            if (pathStr.startsWith("/api/")) {
                sendJsonResponse(exchange, 404, Map.of("error", "Not Found"));
                return;
            }

            // Normalise file path inside public/
            Path requestedFile;
            if ("/".equals(pathStr) || pathStr.isBlank()) {
                requestedFile = PUBLIC_DIR.resolve("index.html").normalize();
            } else {
                String subPath = pathStr.startsWith("/") ? pathStr.substring(1) : pathStr;
                requestedFile = PUBLIC_DIR.resolve(subPath).normalize();
            }

            // Security check: prevent directory traversal outside public/
            if (!requestedFile.startsWith(PUBLIC_DIR)) {
                sendJsonResponse(exchange, 403, Map.of("error", "Access Denied"));
                return;
            }

            // If file doesn't exist, fallback to index.html (SPA routing like server.js)
            if (!Files.exists(requestedFile) || Files.isDirectory(requestedFile)) {
                requestedFile = PUBLIC_DIR.resolve("index.html").normalize();
            }

            if (!Files.exists(requestedFile)) {
                sendJsonResponse(exchange, 404, Map.of("error", "Frontend files not found"));
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

    // -------------------------------------------------------------
    // Utilities: CORS, JSON, Password, JWT
    // -------------------------------------------------------------

    private static void addCorsHeaders(HttpExchange exchange) {
        exchange.getResponseHeaders().set("Access-Control-Allow-Origin", "*");
        exchange.getResponseHeaders().set("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE");
        exchange.getResponseHeaders().set("Access-Control-Allow-Headers", "Content-Type, Authorization");
    }

    private static void sendJsonResponse(HttpExchange exchange, int statusCode, Object data) throws IOException {
        String json = toJson(data);
        byte[] bytes = json.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
        exchange.sendResponseHeaders(statusCode, bytes.length);
        try (OutputStream os = exchange.getResponseBody()) {
            os.write(bytes);
        }
    }

    private static Map<String, String> parseJsonBody(HttpExchange exchange) {
        Map<String, String> result = new HashMap<>();
        try {
            InputStream is = exchange.getRequestBody();
            String body = new String(is.readAllBytes(), StandardCharsets.UTF_8);
            Pattern pattern = Pattern.compile("\"([^\"]+)\"\\s*:\\s*(?:\"([^\"]*)\"|([0-9.]+)|(true|false)|null)");
            Matcher matcher = pattern.matcher(body);
            while (matcher.find()) {
                String key = matcher.group(1);
                String value = matcher.group(2) != null ? matcher.group(2) : matcher.group(3);
                result.put(key, value);
            }
        } catch (Exception ignored) {}
        return result;
    }

    private static String toJson(Object obj) {
        if (obj == null) return "null";
        if (obj instanceof String) return "\"" + escapeJson((String) obj) + "\"";
        if (obj instanceof Number || obj instanceof Boolean) return obj.toString();
        if (obj instanceof Map<?, ?> map) {
            StringBuilder sb = new StringBuilder("{");
            boolean first = true;
            for (Map.Entry<?, ?> entry : map.entrySet()) {
                if (!first) sb.append(",");
                first = false;
                sb.append("\"").append(escapeJson(String.valueOf(entry.getKey()))).append("\":");
                sb.append(toJson(entry.getValue()));
            }
            sb.append("}");
            return sb.toString();
        }
        return "\"" + escapeJson(obj.toString()) + "\"";
    }

    private static String escapeJson(String s) {
        if (s == null) return "";
        return s.replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\b", "\\b")
                .replace("\f", "\\f")
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t");
    }

    public static class PasswordUtil {
        private static final int ITERATIONS = 10000;
        private static final int KEY_LENGTH = 256;

        public static String hashPassword(String password) {
            try {
                byte[] salt = new byte[16];
                new SecureRandom().nextBytes(salt);
                PBEKeySpec spec = new PBEKeySpec(password.toCharArray(), salt, ITERATIONS, KEY_LENGTH);
                SecretKeyFactory skf = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
                byte[] hash = skf.generateSecret(spec).getEncoded();
                return Base64.getEncoder().encodeToString(salt) + ":" + Base64.getEncoder().encodeToString(hash);
            } catch (Exception e) {
                throw new RuntimeException("Error hashing password", e);
            }
        }

        public static boolean verifyPassword(String password, String storedHash) {
            try {
                String[] parts = storedHash.split(":");
                if (parts.length != 2) return false;
                byte[] salt = Base64.getDecoder().decode(parts[0]);
                byte[] expectedHash = Base64.getDecoder().decode(parts[1]);

                PBEKeySpec spec = new PBEKeySpec(password.toCharArray(), salt, ITERATIONS, KEY_LENGTH);
                SecretKeyFactory skf = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
                byte[] computedHash = skf.generateSecret(spec).getEncoded();

                return MessageDigest.isEqual(expectedHash, computedHash);
            } catch (Exception e) {
                return false;
            }
        }
    }

    public static class JwtUtil {
        private static final String HEADER_JSON = "{\"alg\":\"HS256\",\"typ\":\"JWT\"}";
        private static final String ENCODED_HEADER = Base64.getUrlEncoder().withoutPadding()
                .encodeToString(HEADER_JSON.getBytes(StandardCharsets.UTF_8));

        public static String generateToken(Map<String, Object> claims, String secret) {
            String payloadJson = toJson(claims);
            String encodedPayload = Base64.getUrlEncoder().withoutPadding()
                    .encodeToString(payloadJson.getBytes(StandardCharsets.UTF_8));
            String signature = sign(ENCODED_HEADER + "." + encodedPayload, secret);
            return ENCODED_HEADER + "." + encodedPayload + "." + signature;
        }

        public static Map<String, Object> verifyToken(String token, String secret) {
            try {
                String[] parts = token.split("\\.");
                if (parts.length != 3) return null;

                String expectedSig = sign(parts[0] + "." + parts[1], secret);
                if (!MessageDigest.isEqual(expectedSig.getBytes(StandardCharsets.UTF_8), parts[2].getBytes(StandardCharsets.UTF_8))) {
                    return null;
                }

                String payloadJson = new String(Base64.getUrlDecoder().decode(parts[1]), StandardCharsets.UTF_8);
                Map<String, Object> claims = new HashMap<>();
                Pattern pattern = Pattern.compile("\"([^\"]+)\"\\s*:\\s*(?:\"([^\"]*)\"|([0-9.]+)|(true|false)|null)");
                Matcher matcher = pattern.matcher(payloadJson);
                while (matcher.find()) {
                    String key = matcher.group(1);
                    if (matcher.group(2) != null) {
                        claims.put(key, matcher.group(2));
                    } else if (matcher.group(3) != null) {
                        try {
                            claims.put(key, Long.parseLong(matcher.group(3)));
                        } catch (NumberFormatException e) {
                            claims.put(key, Double.parseDouble(matcher.group(3)));
                        }
                    }
                }

                // Check expiration
                Object exp = claims.get("exp");
                if (exp instanceof Number num) {
                    if (Instant.now().getEpochSecond() > num.longValue()) {
                        return null; // Expired
                    }
                }

                return claims;
            } catch (Exception e) {
                return null;
            }
        }

        private static String sign(String data, String secret) {
            try {
                Mac hmac = Mac.getInstance("HmacSHA256");
                SecretKeySpec keySpec = new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256");
                hmac.init(keySpec);
                byte[] signedBytes = hmac.doFinal(data.getBytes(StandardCharsets.UTF_8));
                return Base64.getUrlEncoder().withoutPadding().encodeToString(signedBytes);
            } catch (Exception e) {
                throw new RuntimeException("Error signing JWT", e);
            }
        }
    }
}
