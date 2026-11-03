package com.kcau.dining.service;

import com.kcau.dining.database.DatabaseConnection;
import com.kcau.dining.model.MenuItem;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * Service managing cafeteria food catalog and dish availability.
 */
public class MenuService {

    public List<MenuItem> getAllMenuItems() throws Exception {
        List<MenuItem> items = new ArrayList<>();
        String sql = "SELECT id, name, description, price, category, image, available FROM menu_items ORDER BY category, name";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql);
             ResultSet rs = pstmt.executeQuery()) {
            while (rs.next()) {
                items.add(new MenuItem(
                    rs.getString("id"),
                    rs.getString("name"),
                    rs.getString("description"),
                    rs.getString("category"),
                    rs.getDouble("price"),
                    rs.getString("image"),
                    rs.getInt("available") == 1
                ));
            }
        }
        return items;
    }

    public List<MenuItem> getAvailableMenuItems() throws Exception {
        List<MenuItem> items = new ArrayList<>();
        String sql = "SELECT id, name, description, price, category, image, available FROM menu_items WHERE available = 1 ORDER BY category, name";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql);
             ResultSet rs = pstmt.executeQuery()) {
            while (rs.next()) {
                items.add(new MenuItem(
                    rs.getString("id"),
                    rs.getString("name"),
                    rs.getString("description"),
                    rs.getString("category"),
                    rs.getDouble("price"),
                    rs.getString("image"),
                    true
                ));
            }
        }
        return items;
    }

    public MenuItem getMenuItemById(String id) throws Exception {
        String sql = "SELECT id, name, description, price, category, image, available FROM menu_items WHERE id = ?";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, id);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    return new MenuItem(
                        rs.getString("id"),
                        rs.getString("name"),
                        rs.getString("description"),
                        rs.getString("category"),
                        rs.getDouble("price"),
                        rs.getString("image"),
                        rs.getInt("available") == 1
                    );
                }
            }
        }
        return null;
    }

    public MenuItem addMenuItem(MenuItem item) throws Exception {
        if (item.getId() == null || item.getId().isBlank()) {
            item.setId("food-" + UUID.randomUUID().toString().substring(0, 8));
        }
        String sql = "INSERT INTO menu_items (id, name, description, price, category, image, available) VALUES (?, ?, ?, ?, ?, ?, ?)";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, item.getId());
            pstmt.setString(2, item.getName());
            pstmt.setString(3, item.getDescription());
            pstmt.setDouble(4, item.getPrice());
            pstmt.setString(5, item.getCategory());
            pstmt.setString(6, item.getImage());
            pstmt.setInt(7, item.isAvailable() ? 1 : 0);
            pstmt.executeUpdate();
        }
        return item;
    }

    public boolean updateMenuItem(MenuItem item) throws Exception {
        String sql = "UPDATE menu_items SET name = ?, description = ?, price = ?, category = ?, image = ?, available = ? WHERE id = ?";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, item.getName());
            pstmt.setString(2, item.getDescription());
            pstmt.setDouble(3, item.getPrice());
            pstmt.setString(4, item.getCategory());
            pstmt.setString(5, item.getImage());
            pstmt.setInt(6, item.isAvailable() ? 1 : 0);
            pstmt.setString(7, item.getId());
            return pstmt.executeUpdate() > 0;
        }
    }

    public boolean toggleAvailability(String id, boolean available) throws Exception {
        String sql = "UPDATE menu_items SET available = ? WHERE id = ?";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, available ? 1 : 0);
            pstmt.setString(2, id);
            return pstmt.executeUpdate() > 0;
        }
    }
}
