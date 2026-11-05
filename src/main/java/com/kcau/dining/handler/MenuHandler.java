package com.kcau.dining.handler;

import com.kcau.dining.model.MenuItem;
import com.kcau.dining.service.MenuService;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Handles HTTP requests for Cafeteria Menu listing, item creation, and availability toggles.
 */
public class MenuHandler implements HttpHandler {

    private final MenuService menuService = new MenuService();

    @Override
    public void handle(HttpExchange exchange) throws IOException {
        if (HttpHelper.handleCorsPreflight(exchange)) return;

        String path = exchange.getRequestURI().getPath();
        String method = exchange.getRequestMethod();

        try {
            if ("/api/menu".equals(path) && "GET".equalsIgnoreCase(method)) {
                handleGetMenu(exchange);
            } else if ("/api/menu".equals(path) && "POST".equalsIgnoreCase(method)) {
                handleAddMenuItem(exchange);
            } else if ("/api/menu/availability".equals(path) && "PUT".equalsIgnoreCase(method)) {
                handleToggleAvailability(exchange);
            } else if ("/api/menu/edit".equals(path) && "PUT".equalsIgnoreCase(method)) {
                handleEditMenuItem(exchange);
            } else {
                HttpHelper.sendError(exchange, 404, "Endpoint not found");
            }
        } catch (IllegalArgumentException e) {
            HttpHelper.sendError(exchange, 400, e.getMessage());
        } catch (Exception e) {
            HttpHelper.sendError(exchange, 500, "Server error: " + e.getMessage());
        }
    }

    private void handleGetMenu(HttpExchange exchange) throws Exception {
        String query = exchange.getRequestURI().getQuery();
        boolean includeAll = query != null && query.contains("all=true");

        List<MenuItem> items = includeAll ? menuService.getAllMenuItems() : menuService.getAllMenuItems();
        List<Map<String, Object>> responseList = new ArrayList<>();

        for (MenuItem item : items) {
            Map<String, Object> map = new HashMap<>();
            map.put("id", item.getId());
            map.put("name", item.getName());
            map.put("description", item.getDescription());
            map.put("price", item.getPrice());
            map.put("category", item.getCategory());
            map.put("image", item.getImage());
            map.put("available", item.isAvailable());
            responseList.add(map);
        }

        HttpHelper.sendJson(exchange, 200, responseList);
    }

    private void handleAddMenuItem(HttpExchange exchange) throws Exception {
        Map<String, String> body = HttpHelper.parseJsonBody(exchange);
        String name = body.get("name");
        String category = body.get("category");
        String priceStr = body.get("price");
        String description = body.getOrDefault("description", "");
        String image = body.getOrDefault("image", "images/beef-ugali.jpg");

        if (name == null || name.isBlank() || priceStr == null || category == null) {
            HttpHelper.sendError(exchange, 400, "Name, category, and price are required");
            return;
        }

        double price = Double.parseDouble(priceStr);
        MenuItem newItem = new MenuItem(null, name.trim(), description.trim(), category.trim().toLowerCase(), price, image, true);
        MenuItem created = menuService.addMenuItem(newItem);

        Map<String, Object> resp = new HashMap<>();
        resp.put("message", "Menu item added successfully");
        resp.put("item", created);
        HttpHelper.sendJson(exchange, 201, resp);
    }

    private void handleToggleAvailability(HttpExchange exchange) throws Exception {
        Map<String, String> body = HttpHelper.parseJsonBody(exchange);
        String foodId = body.get("id");
        String availableStr = body.get("available");

        if (foodId == null || availableStr == null) {
            HttpHelper.sendError(exchange, 400, "Food id and available (true/false) are required");
            return;
        }

        boolean available = Boolean.parseBoolean(availableStr);
        boolean updated = menuService.toggleAvailability(foodId, available);

        if (updated) {
            System.out.printf("🍲 [ADMIN MENU UPDATE] Dish %s stock toggled -> %s%n", foodId, available ? "AVAILABLE" : "OUT OF STOCK");
            HttpHelper.sendJson(exchange, 200, Map.of("message", "Availability updated for " + foodId, "available", available));
        } else {
            HttpHelper.sendError(exchange, 404, "Menu item not found");
        }
    }

    private void handleEditMenuItem(HttpExchange exchange) throws Exception {
        Map<String, String> body = HttpHelper.parseJsonBody(exchange);
        String id = body.get("id");
        String name = body.get("name");
        String description = body.get("description");
        String category = body.get("category");
        String priceStr = body.get("price");
        String image = body.get("image");
        String availableStr = body.get("available");

        if (id == null) {
            HttpHelper.sendError(exchange, 400, "Item id is required");
            return;
        }

        MenuItem existing = menuService.getMenuItemById(id);
        if (existing == null) {
            HttpHelper.sendError(exchange, 404, "Menu item not found");
            return;
        }

        if (name != null) existing.setName(name);
        if (description != null) existing.setDescription(description);
        if (category != null) existing.setCategory(category);
        if (priceStr != null) existing.setPrice(Double.parseDouble(priceStr));
        if (image != null) existing.setImage(image);
        if (availableStr != null) existing.setAvailable(Boolean.parseBoolean(availableStr));

        menuService.updateMenuItem(existing);
        HttpHelper.sendJson(exchange, 200, Map.of("message", "Menu item updated successfully"));
    }
}
