package com.kcau.dining.model;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

/**
 * Represents an order placed by a student or staff member.
 */
public class Order {
    private String orderId;
    private String userId;
    private String customerName;
    private double totalAmount;
    private String status; // "PENDING", "PREPARING", "READY", "COLLECTED", "CANCELLED"
    private Instant createdAt;
    private List<OrderItem> items = new ArrayList<>();

    public Order() {
        this.status = "PENDING";
        this.createdAt = Instant.now();
    }

    public Order(String orderId, String userId, String customerName, double totalAmount, String status, Instant createdAt) {
        this.orderId = orderId;
        this.userId = userId;
        this.customerName = customerName;
        this.totalAmount = totalAmount;
        this.status = (status != null && !status.isBlank()) ? status : "PENDING";
        this.createdAt = (createdAt != null) ? createdAt : Instant.now();
    }

    public String getOrderId() { return orderId; }
    public void setOrderId(String orderId) { this.orderId = orderId; }

    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }

    // Backward compatibility helper for studentId
    public String getStudentId() { return userId; }
    public void setStudentId(String studentId) { this.userId = studentId; }

    public String getCustomerName() { return customerName; }
    public void setCustomerName(String customerName) { this.customerName = customerName; }

    public double getTotalAmount() { return totalAmount; }
    public void setTotalAmount(double totalAmount) { this.totalAmount = totalAmount; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }

    public List<OrderItem> getItems() { return items; }
    public void setItems(List<OrderItem> items) { this.items = items; }

    public void addItem(OrderItem item) {
        this.items.add(item);
    }

    @Override
    public String toString() {
        return "Order{" +
                "orderId='" + orderId + '\'' +
                ", customerName='" + customerName + '\'' +
                ", totalAmount=" + totalAmount +
                ", status='" + status + '\'' +
                ", itemsCount=" + items.size() +
                '}';
    }
}
