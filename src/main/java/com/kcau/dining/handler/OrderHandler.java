package com.kcau.dining.handler;

import com.kcau.dining.model.Order;
import com.kcau.dining.model.OrderItem;
import com.kcau.dining.service.OrderService;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Handles HTTP requests for Order Placement, Order Retrieval, and Status Updates.
 */
public class OrderHandler implements HttpHandler {

    private final OrderService orderService = new OrderService();

    @Override
    public void handle(HttpExchange exchange) throws IOException {
        if (HttpHelper.handleCorsPreflight(exchange)) return;

        String path = exchange.getRequestURI().getPath();
        String method = exchange.getRequestMethod();

        try {
            if ("/api/orders".equals(path) && "POST".equalsIgnoreCase(method)) {
                handleCreateOrder(exchange);
            } else if ("/api/orders".equals(path) && "GET".equalsIgnoreCase(method)) {
                handleGetAllOrders(exchange);
            } else if ("/api/orders/my".equals(path) && "GET".equalsIgnoreCase(method)) {
                handleGetMyOrders(exchange);
            } else if ("/api/orders/status".equals(path) && "PUT".equalsIgnoreCase(method)) {
                handleUpdateStatus(exchange);
            } else {
                HttpHelper.sendError(exchange, 404, "Endpoint not found");
            }
        } catch (IllegalArgumentException e) {
            HttpHelper.sendError(exchange, 400, e.getMessage());
        } catch (Exception e) {
            HttpHelper.sendError(exchange, 500, "Server error: " + e.getMessage());
        }
    }

    private void handleCreateOrder(HttpExchange exchange) throws Exception {
        String body = HttpHelper.readRequestBody(exchange);

        // Extract user info
        String userId = "GUEST";
        String customerName = "Student";

        Pattern userPattern = Pattern.compile("\"userId\"\\s*:\\s*\"([^\"]*)\"");
        Matcher userMatcher = userPattern.matcher(body);
        if (userMatcher.find()) userId = userMatcher.group(1);

        Pattern namePattern = Pattern.compile("\"customerName\"\\s*:\\s*\"([^\"]*)\"");
        Matcher nameMatcher = namePattern.matcher(body);
        if (nameMatcher.find()) customerName = nameMatcher.group(1);

        // Parse items array: [{ "foodId": "food-1", "foodName": "Ugali", "quantity": 1, "unitPrice": 150 }]
        List<OrderItem> items = new ArrayList<>();
        Pattern itemPattern = Pattern.compile("\\{[^{}]*\\}");
        Matcher itemMatcher = itemPattern.matcher(body);
        while (itemMatcher.find()) {
            String itemJson = itemMatcher.group();
            if (itemJson.contains("\"foodName\"") || itemJson.contains("\"name\"")) {
                String foodId = extractString(itemJson, "foodId");
                String foodName = extractString(itemJson, "foodName");
                if (foodName.isEmpty()) foodName = extractString(itemJson, "name");

                int qty = extractInt(itemJson, "quantity", 1);
                double price = extractDouble(itemJson, "unitPrice", 0.0);
                if (price == 0.0) price = extractDouble(itemJson, "price", 0.0);

                if (!foodName.isEmpty()) {
                    items.add(new OrderItem(foodId, foodName, qty, price));
                }
            }
        }

        if (items.isEmpty()) {
            HttpHelper.sendError(exchange, 400, "Cart is empty. Please add items before placing order.");
            return;
        }

        Order order = orderService.createOrder(userId, customerName, items);
        System.out.printf("🛒 [ORDER PLACED] %s by %s for KES %.2f (%d line items)%n",
            order.getOrderId(), order.getCustomerName(), order.getTotalAmount(), items.size());

        Map<String, Object> resp = new HashMap<>();
        resp.put("message", "Order placed successfully!");
        resp.put("orderId", order.getOrderId());
        resp.put("totalAmount", order.getTotalAmount());
        resp.put("status", order.getStatus());
        resp.put("date", order.getCreatedAt().toString());
        HttpHelper.sendJson(exchange, 201, resp);
    }

    private void handleGetAllOrders(HttpExchange exchange) throws Exception {
        List<Order> orders = orderService.getAllOrders();
        HttpHelper.sendJson(exchange, 200, serializeOrders(orders));
    }

    private void handleGetMyOrders(HttpExchange exchange) throws Exception {
        String userId = null;

        // Try query param
        String query = exchange.getRequestURI().getQuery();
        if (query != null && query.contains("userId=")) {
            for (String param : query.split("&")) {
                if (param.startsWith("userId=")) {
                    userId = param.substring(7);
                }
            }
        }

        // Try auth header
        if (userId == null) {
            String authHeader = exchange.getRequestHeaders().getFirst("Authorization");
            if (authHeader != null && authHeader.startsWith("Bearer ")) {
                Map<String, Object> claims = HttpHelper.verifyToken(authHeader.substring(7).trim());
                if (claims != null && claims.containsKey("studentId")) {
                    userId = (String) claims.get("studentId");
                }
            }
        }

        if (userId == null || userId.isBlank()) {
            HttpHelper.sendError(exchange, 400, "User ID or Authorization token is required");
            return;
        }

        List<Order> orders = orderService.getOrdersByUser(userId);
        HttpHelper.sendJson(exchange, 200, serializeOrders(orders));
    }

    private void handleUpdateStatus(HttpExchange exchange) throws Exception {
        Map<String, String> body = HttpHelper.parseJsonBody(exchange);
        String orderId = body.get("orderId");
        String status = body.get("status");

        if (orderId == null || status == null) {
            HttpHelper.sendError(exchange, 400, "orderId and status are required");
            return;
        }

        boolean updated = orderService.updateOrderStatus(orderId, status);
        if (updated) {
            System.out.printf("👨‍🍳 [KITCHEN KDS UPDATE] Order %s changed status -> %s%n", orderId, status.toUpperCase());
            HttpHelper.sendJson(exchange, 200, Map.of("message", "Order status updated to " + status, "orderId", orderId, "status", status));
        } else {
            HttpHelper.sendError(exchange, 404, "Order not found");
        }
    }

    private List<Map<String, Object>> serializeOrders(List<Order> orders) {
        List<Map<String, Object>> list = new ArrayList<>();
        for (Order o : orders) {
            Map<String, Object> m = new HashMap<>();
            m.put("orderId", o.getOrderId());
            m.put("userId", o.getUserId());
            m.put("customerName", o.getCustomerName());
            m.put("totalAmount", o.getTotalAmount());
            m.put("status", o.getStatus());
            m.put("date", o.getCreatedAt().toString());

            List<Map<String, Object>> itemsList = new ArrayList<>();
            for (OrderItem item : o.getItems()) {
                Map<String, Object> im = new HashMap<>();
                im.put("foodName", item.getFoodName());
                im.put("quantity", item.getQuantity());
                im.put("unitPrice", item.getUnitPrice());
                im.put("subtotal", item.getSubtotal());
                itemsList.add(im);
            }
            m.put("items", itemsList);
            list.add(m);
        }
        return list;
    }

    private String extractString(String json, String key) {
        Pattern p = Pattern.compile("\"" + key + "\"\\s*:\\s*\"([^\"]*)\"");
        Matcher m = p.matcher(json);
        return m.find() ? m.group(1) : "";
    }

    private int extractInt(String json, String key, int def) {
        Pattern p = Pattern.compile("\"" + key + "\"\\s*:\\s*([0-9]+)");
        Matcher m = p.matcher(json);
        if (m.find()) {
            try { return Integer.parseInt(m.group(1)); } catch (Exception ignored) {}
        }
        return def;
    }

    private double extractDouble(String json, String key, double def) {
        Pattern p = Pattern.compile("\"" + key + "\"\\s*:\\s*([0-9.]+)");
        Matcher m = p.matcher(json);
        if (m.find()) {
            try { return Double.parseDouble(m.group(1)); } catch (Exception ignored) {}
        }
        return def;
    }
}
