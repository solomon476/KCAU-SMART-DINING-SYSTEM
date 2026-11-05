package com.kcau.dining.handler;

import com.sun.net.httpserver.HttpExchange;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Shared HTTP, JSON serialization, and JWT cryptographic helpers for REST handlers.
 */
public class HttpHelper {

    public static final String JWT_SECRET = Optional.ofNullable(System.getenv("JWT_SECRET"))
            .orElse("super_secret_cafeteria_key");

    public static void addCorsHeaders(HttpExchange exchange) {
        exchange.getResponseHeaders().set("Access-Control-Allow-Origin", "*");
        exchange.getResponseHeaders().set("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE");
        exchange.getResponseHeaders().set("Access-Control-Allow-Headers", "Content-Type, Authorization");
    }

    public static boolean handleCorsPreflight(HttpExchange exchange) throws IOException {
        addCorsHeaders(exchange);
        if ("OPTIONS".equalsIgnoreCase(exchange.getRequestMethod())) {
            exchange.sendResponseHeaders(204, -1);
            return true;
        }
        return false;
    }

    public static void sendJson(HttpExchange exchange, int statusCode, Object data) throws IOException {
        addCorsHeaders(exchange);
        String json = toJson(data);
        byte[] bytes = json.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
        exchange.sendResponseHeaders(statusCode, bytes.length);
        try (OutputStream os = exchange.getResponseBody()) {
            os.write(bytes);
        }
    }

    public static void sendError(HttpExchange exchange, int statusCode, String message) throws IOException {
        sendJson(exchange, statusCode, Map.of("error", message));
    }

    public static Map<String, String> parseJsonBody(HttpExchange exchange) {
        Map<String, String> result = new HashMap<>();
        try {
            InputStream is = exchange.getRequestBody();
            String body = new String(is.readAllBytes(), StandardCharsets.UTF_8).trim();
            if (body.isEmpty()) return result;

            Pattern pattern = Pattern.compile("\"([^\"]+)\"\\s*:\\s*(?:\"((?:\\\\\"|[^\"])*)\"|([0-9.]+)|(true|false)|null)");
            Matcher matcher = pattern.matcher(body);
            while (matcher.find()) {
                String key = matcher.group(1);
                String value = matcher.group(2) != null ? matcher.group(2) : matcher.group(3);
                if (value == null && matcher.group(4) != null) {
                    value = matcher.group(4);
                }
                if (value != null) {
                    value = value.replace("\\\"", "\"").replace("\\\\", "\\");
                }
                result.put(key, value);
            }
        } catch (Exception ignored) {}
        return result;
    }

    public static String readRequestBody(HttpExchange exchange) {
        try {
            InputStream is = exchange.getRequestBody();
            return new String(is.readAllBytes(), StandardCharsets.UTF_8);
        } catch (Exception e) {
            return "";
        }
    }

    public static String toJson(Object obj) {
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
        if (obj instanceof List<?> list) {
            StringBuilder sb = new StringBuilder("[");
            boolean first = true;
            for (Object item : list) {
                if (!first) sb.append(",");
                first = false;
                sb.append(toJson(item));
            }
            sb.append("]");
            return sb.toString();
        }
        return "\"" + escapeJson(obj.toString()) + "\"";
    }

    public static String escapeJson(String s) {
        if (s == null) return "";
        return s.replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\b", "\\b")
                .replace("\f", "\\f")
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t");
    }

    // --- JWT Helpers ---

    public static String generateToken(Map<String, Object> claims) {
        String header = Base64.getUrlEncoder().withoutPadding()
                .encodeToString("{\"alg\":\"HS256\",\"typ\":\"JWT\"}".getBytes(StandardCharsets.UTF_8));
        String payload = Base64.getUrlEncoder().withoutPadding()
                .encodeToString(toJson(claims).getBytes(StandardCharsets.UTF_8));
        String signature = sign(header + "." + payload, JWT_SECRET);
        return header + "." + payload + "." + signature;
    }

    public static Map<String, Object> verifyToken(String token) {
        try {
            String[] parts = token.split("\\.");
            if (parts.length != 3) return null;

            String expectedSig = sign(parts[0] + "." + parts[1], JWT_SECRET);
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

            Object exp = claims.get("exp");
            if (exp instanceof Number num && Instant.now().getEpochSecond() > num.longValue()) {
                return null; // Expired
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
