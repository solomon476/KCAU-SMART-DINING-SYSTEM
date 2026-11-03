package com.kcau.dining.handler;

import com.kcau.dining.model.User;
import com.kcau.dining.service.UserService;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;

import java.io.IOException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Handles HTTP requests for User Registration, Authentication, Session Validation, and Role Management.
 */
public class UserHandler implements HttpHandler {

    private final UserService userService = new UserService();

    @Override
    public void handle(HttpExchange exchange) throws IOException {
        if (HttpHelper.handleCorsPreflight(exchange)) return;

        String path = exchange.getRequestURI().getPath();
        String method = exchange.getRequestMethod();

        try {
            if ("/api/signup".equals(path) && "POST".equalsIgnoreCase(method)) {
                handleSignup(exchange);
            } else if ("/api/login".equals(path) && "POST".equalsIgnoreCase(method)) {
                handleLogin(exchange);
            } else if ("/api/me".equals(path) && "GET".equalsIgnoreCase(method)) {
                handleMe(exchange);
            } else if ("/api/users".equals(path) && "GET".equalsIgnoreCase(method)) {
                handleListUsers(exchange);
            } else if ("/api/users/role".equals(path) && "PUT".equalsIgnoreCase(method)) {
                handleUpdateRole(exchange);
            } else {
                HttpHelper.sendError(exchange, 404, "Endpoint not found");
            }
        } catch (IllegalArgumentException e) {
            HttpHelper.sendError(exchange, 400, e.getMessage());
        } catch (Exception e) {
            HttpHelper.sendError(exchange, 500, "Server error: " + e.getMessage());
        }
    }

    private void handleSignup(HttpExchange exchange) throws Exception {
        Map<String, String> body = HttpHelper.parseJsonBody(exchange);
        String name = body.get("name");
        String studentId = body.get("studentId");
        String password = body.get("password");
        String role = body.getOrDefault("role", "student");

        User newUser = userService.registerUser(name, studentId, password, role);
        Map<String, Object> resp = new HashMap<>();
        resp.put("message", "Account created successfully! Please sign in.");
        resp.put("userId", newUser.getId());
        resp.put("studentId", newUser.getStudentId());
        resp.put("role", newUser.getRole());
        HttpHelper.sendJson(exchange, 201, resp);
    }

    private void handleLogin(HttpExchange exchange) throws Exception {
        Map<String, String> body = HttpHelper.parseJsonBody(exchange);
        String studentId = body.get("studentId");
        String password = body.get("password");

        User user = userService.authenticate(studentId, password);

        long expSeconds = Instant.now().plusSeconds(7 * 24 * 3600).getEpochSecond();
        Map<String, Object> claims = new HashMap<>();
        claims.put("id", user.getId());
        claims.put("name", user.getName());
        claims.put("studentId", user.getStudentId());
        claims.put("role", user.getRole());
        claims.put("exp", expSeconds);

        String token = HttpHelper.generateToken(claims);

        Map<String, Object> resp = new HashMap<>();
        resp.put("message", "Logged in successfully");
        resp.put("token", token);
        resp.put("name", user.getName());
        resp.put("studentId", user.getStudentId());
        resp.put("role", user.getRole());
        HttpHelper.sendJson(exchange, 200, resp);
    }

    private void handleMe(HttpExchange exchange) throws IOException {
        String authHeader = exchange.getRequestHeaders().getFirst("Authorization");
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            HttpHelper.sendError(exchange, 401, "No authentication token provided");
            return;
        }

        String token = authHeader.substring(7).trim();
        Map<String, Object> claims = HttpHelper.verifyToken(token);
        if (claims == null) {
            HttpHelper.sendError(exchange, 401, "Session expired or invalid token. Please log in again.");
            return;
        }

        Map<String, Object> resp = new HashMap<>();
        resp.put("id", claims.get("id"));
        resp.put("name", claims.get("name"));
        resp.put("studentId", claims.get("studentId"));
        resp.put("role", claims.getOrDefault("role", "student"));
        HttpHelper.sendJson(exchange, 200, resp);
    }

    private void handleListUsers(HttpExchange exchange) throws Exception {
        List<User> users = userService.getAllUsers();
        List<Map<String, Object>> list = new ArrayList<>();
        for (User u : users) {
            Map<String, Object> m = new HashMap<>();
            m.put("id", u.getId());
            m.put("name", u.getName());
            m.put("studentId", u.getStudentId());
            m.put("role", u.getRole());
            m.put("createdAt", u.getCreatedAt().toString());
            list.add(m);
        }
        HttpHelper.sendJson(exchange, 200, list);
    }

    private void handleUpdateRole(HttpExchange exchange) throws Exception {
        Map<String, String> body = HttpHelper.parseJsonBody(exchange);
        String userId = body.get("userId");
        String newRole = body.get("role");

        if (userId == null || newRole == null) {
            HttpHelper.sendError(exchange, 400, "userId and role are required");
            return;
        }

        boolean updated = userService.updateUserRole(userId, newRole);
        if (updated) {
            HttpHelper.sendJson(exchange, 200, Map.of("message", "User role updated successfully to " + newRole));
        } else {
            HttpHelper.sendError(exchange, 404, "User not found");
        }
    }
}
