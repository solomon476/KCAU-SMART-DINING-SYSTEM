package com.kcau.dining.service;

import com.kcau.dining.database.DatabaseConnection;
import com.kcau.dining.model.Order;
import com.kcau.dining.model.OrderItem;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * Service managing customer orders, cart validations, and status workflows.
 */
public class OrderService {

    public Order createOrder(String userId, String customerName, List<OrderItem> items) throws Exception {
        if (items == null || items.isEmpty()) {
            throw new IllegalArgumentException("Cannot place an order with an empty cart");
        }

        // Validate quantities and calculate total
        double total = 0.0;
        for (OrderItem item : items) {
            if (item.getQuantity() <= 0) {
                throw new IllegalArgumentException("Invalid quantity for item: " + item.getFoodName());
            }
            if (item.getUnitPrice() < 0) {
                throw new IllegalArgumentException("Invalid price for item: " + item.getFoodName());
            }
            total += item.getQuantity() * item.getUnitPrice();
        }

        String orderId = "ORD-" + System.currentTimeMillis() % 1000000;
        Instant now = Instant.now();
        String status = "PENDING";

        String insertOrderSql = "INSERT INTO orders (id, user_id, customer_name, date, total, order_status) VALUES (?, ?, ?, ?, ?, ?)";
        String insertItemSql = "INSERT INTO order_items (order_id, food_id, food_name, quantity, unit_price) VALUES (?, ?, ?, ?, ?)";

        try (Connection conn = DatabaseConnection.getConnection()) {
            conn.setAutoCommit(false);
            try {
                // 1. Insert Order
                try (PreparedStatement pstmt = conn.prepareStatement(insertOrderSql)) {
                    pstmt.setString(1, orderId);
                    pstmt.setString(2, userId != null ? userId : "GUEST");
                    pstmt.setString(3, customerName != null ? customerName : "Student");
                    pstmt.setString(4, now.toString());
                    pstmt.setDouble(5, total);
                    pstmt.setString(6, status);
                    pstmt.executeUpdate();
                }

                // 2. Insert Line Items
                try (PreparedStatement pstmt = conn.prepareStatement(insertItemSql)) {
                    for (OrderItem item : items) {
                        pstmt.setString(1, orderId);
                        pstmt.setString(2, item.getFoodId() != null ? item.getFoodId() : "dish");
                        pstmt.setString(3, item.getFoodName());
                        pstmt.setInt(4, item.getQuantity());
                        pstmt.setDouble(5, item.getUnitPrice());
                        pstmt.addBatch();
                    }
                    pstmt.executeBatch();
                }

                conn.commit();
            } catch (Exception e) {
                conn.rollback();
                throw e;
            } finally {
                conn.setAutoCommit(true);
            }
        }

        Order order = new Order(orderId, userId, customerName, total, status, now);
        order.setItems(items);
        return order;
    }

    public List<Order> getAllOrders() throws Exception {
        List<Order> orders = new ArrayList<>();
        String sql = "SELECT id, user_id, customer_name, date, total, order_status FROM orders ORDER BY date DESC";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql);
             ResultSet rs = pstmt.executeQuery()) {
            while (rs.next()) {
                String orderId = rs.getString("id");
                Instant date = Instant.parse(rs.getString("date"));
                Order order = new Order(
                    orderId,
                    rs.getString("user_id"),
                    rs.getString("customer_name"),
                    rs.getDouble("total"),
                    rs.getString("order_status"),
                    date
                );
                order.setItems(getOrderItems(conn, orderId));
                orders.add(order);
            }
        }
        return orders;
    }

    public List<Order> getOrdersByUser(String userId) throws Exception {
        List<Order> orders = new ArrayList<>();
        String sql = "SELECT id, user_id, customer_name, date, total, order_status FROM orders WHERE UPPER(user_id) = ? ORDER BY date DESC";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, userId.toUpperCase().trim());
            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    String orderId = rs.getString("id");
                    Instant date = Instant.parse(rs.getString("date"));
                    Order order = new Order(
                        orderId,
                        rs.getString("user_id"),
                        rs.getString("customer_name"),
                        rs.getDouble("total"),
                        rs.getString("order_status"),
                        date
                    );
                    order.setItems(getOrderItems(conn, orderId));
                    orders.add(order);
                }
            }
        }
        return orders;
    }

    public Order getOrderById(String orderId) throws Exception {
        String sql = "SELECT id, user_id, customer_name, date, total, order_status FROM orders WHERE id = ?";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, orderId);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    Instant date = Instant.parse(rs.getString("date"));
                    Order order = new Order(
                        rs.getString("id"),
                        rs.getString("user_id"),
                        rs.getString("customer_name"),
                        rs.getDouble("total"),
                        rs.getString("order_status"),
                        date
                    );
                    order.setItems(getOrderItems(conn, orderId));
                    return order;
                }
            }
        }
        return null;
    }

    public boolean updateOrderStatus(String orderId, String newStatus) throws Exception {
        String sql = "UPDATE orders SET order_status = ? WHERE id = ?";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, newStatus.toUpperCase().trim());
            pstmt.setString(2, orderId.trim());
            return pstmt.executeUpdate() > 0;
        }
    }

    private List<OrderItem> getOrderItems(Connection conn, String orderId) throws Exception {
        List<OrderItem> items = new ArrayList<>();
        String sql = "SELECT id, order_id, food_id, food_name, quantity, unit_price FROM order_items WHERE order_id = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, orderId);
            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    items.add(new OrderItem(
                        rs.getInt("id"),
                        rs.getString("order_id"),
                        rs.getString("food_id"),
                        rs.getString("food_name"),
                        rs.getInt("quantity"),
                        rs.getDouble("unit_price")
                    ));
                }
            }
        }
        return items;
    }
}
