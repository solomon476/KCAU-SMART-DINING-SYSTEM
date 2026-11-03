package com.kcau.dining.service;

import com.kcau.dining.database.DatabaseConnection;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Service calculating cafeteria sales summaries, order statistics, and item performance.
 */
public class ReportService {

    public Map<String, Object> getSalesSummary() throws Exception {
        Map<String, Object> summary = new HashMap<>();

        String sql = """
            SELECT
                COUNT(*) AS total_orders,
                COALESCE(SUM(total), 0.0) AS total_revenue,
                COALESCE(AVG(total), 0.0) AS avg_order_value,
                SUM(CASE WHEN order_status = 'PENDING' THEN 1 ELSE 0 END) AS pending_count,
                SUM(CASE WHEN order_status = 'PREPARING' THEN 1 ELSE 0 END) AS preparing_count,
                SUM(CASE WHEN order_status = 'READY' THEN 1 ELSE 0 END) AS ready_count,
                SUM(CASE WHEN order_status = 'COLLECTED' THEN 1 ELSE 0 END) AS collected_count
            FROM orders;
        """;

        try (Connection conn = DatabaseConnection.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            if (rs.next()) {
                summary.put("totalOrders", rs.getInt("total_orders"));
                summary.put("totalRevenue", Math.round(rs.getDouble("total_revenue") * 100.0) / 100.0);
                summary.put("averageOrderValue", Math.round(rs.getDouble("avg_order_value") * 100.0) / 100.0);
                summary.put("pendingOrders", rs.getInt("pending_count"));
                summary.put("preparingOrders", rs.getInt("preparing_count"));
                summary.put("readyOrders", rs.getInt("ready_count"));
                summary.put("collectedOrders", rs.getInt("collected_count"));
            }
        }

        // Get user counts
        try (Connection conn = DatabaseConnection.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SELECT COUNT(*) AS user_count FROM users")) {
            if (rs.next()) {
                summary.put("registeredUsers", rs.getInt("user_count"));
            }
        }

        return summary;
    }

    public List<Map<String, Object>> getItemPopularity() throws Exception {
        List<Map<String, Object>> list = new ArrayList<>();
        String sql = """
            SELECT food_name, SUM(quantity) AS total_qty, SUM(quantity * unit_price) AS total_sales
            FROM order_items
            GROUP BY food_name
            ORDER BY total_qty DESC
            LIMIT 10;
        """;

        try (Connection conn = DatabaseConnection.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            while (rs.next()) {
                Map<String, Object> item = new HashMap<>();
                item.put("name", rs.getString("food_name"));
                item.put("quantitySold", rs.getInt("total_qty"));
                item.put("revenue", Math.round(rs.getDouble("total_sales") * 100.0) / 100.0);
                list.add(item);
            }
        }
        return list;
    }
}
