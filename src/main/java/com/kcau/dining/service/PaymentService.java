package com.kcau.dining.service;

import com.kcau.dining.database.DatabaseConnection;
import com.kcau.dining.model.Payment;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * Service managing payment recordings and simulated transaction logs.
 */
public class PaymentService {

    public Payment recordPayment(String orderId, String method, double amount, String status, String reference) throws Exception {
        if (orderId == null || orderId.isBlank()) {
            throw new IllegalArgumentException("Order ID is required for payment recording");
        }

        String paymentId = "PAY-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
        String payMethod = (method != null && !method.isBlank()) ? method.toUpperCase() : "MPESA";
        String payStatus = (status != null && !status.isBlank()) ? status.toUpperCase() : "COMPLETED";
        String ref = (reference != null && !reference.isBlank()) ? reference : "MP-" + (System.currentTimeMillis() % 10000000);
        Instant now = Instant.now();

        String sql = "INSERT INTO payments (id, order_id, method, amount, status, reference, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, paymentId);
            pstmt.setString(2, orderId.trim());
            pstmt.setString(3, payMethod);
            pstmt.setDouble(4, amount);
            pstmt.setString(5, payStatus);
            pstmt.setString(6, ref);
            pstmt.setString(7, now.toString());
            pstmt.executeUpdate();
        }

        return new Payment(paymentId, orderId, payMethod, amount, payStatus, ref, now);
    }

    public Payment getPaymentByOrderId(String orderId) throws Exception {
        String sql = "SELECT id, order_id, method, amount, status, reference, created_at FROM payments WHERE order_id = ?";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, orderId.trim());
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    return new Payment(
                        rs.getString("id"),
                        rs.getString("order_id"),
                        rs.getString("method"),
                        rs.getDouble("amount"),
                        rs.getString("status"),
                        rs.getString("reference"),
                        Instant.parse(rs.getString("created_at"))
                    );
                }
            }
        }
        return null;
    }

    public List<Payment> getAllPayments() throws Exception {
        List<Payment> list = new ArrayList<>();
        String sql = "SELECT id, order_id, method, amount, status, reference, created_at FROM payments ORDER BY created_at DESC";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql);
             ResultSet rs = pstmt.executeQuery()) {
            while (rs.next()) {
                list.add(new Payment(
                    rs.getString("id"),
                    rs.getString("order_id"),
                    rs.getString("method"),
                    rs.getDouble("amount"),
                    rs.getString("status"),
                    rs.getString("reference"),
                    Instant.parse(rs.getString("created_at"))
                ));
            }
        }
        return list;
    }
}
