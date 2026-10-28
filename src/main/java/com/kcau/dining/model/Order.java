package com.kcau.dining.model;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

/**
 * Represents a cafeteria order placed by a student.
 */
public class Order {
    private String orderId;
    private String studentId;
    private List<OrderItem> items = new ArrayList<>();
    private double totalAmount;
    private String status; // "PENDING", "PREPARING", "READY", "COMPLETED"
    private Instant createdAt;

    public Order() {
        this.createdAt = Instant.now();
        this.status = "PENDING";
    }

    public Order(String orderId, String studentId) {
        this.orderId = orderId;
        this.studentId = studentId;
        this.createdAt = Instant.now();
        this.status = "PENDING";
    }

    public String getOrderId() { return orderId; }
    public void setOrderId(String orderId) { this.orderId = orderId; }

    public String getStudentId() { return studentId; }
    public void setStudentId(String studentId) { this.studentId = studentId; }

    public List<OrderItem> getItems() { return items; }
    public void setItems(List<OrderItem> items) { this.items = items; }

    public double getTotalAmount() { return totalAmount; }
    public void setTotalAmount(double totalAmount) { this.totalAmount = totalAmount; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }

    public static class OrderItem {
        private String itemName;
        private int quantity;
        private double unitPrice;

        public OrderItem() {}

        public OrderItem(String itemName, int quantity, double unitPrice) {
            this.itemName = itemName;
            this.quantity = quantity;
            this.unitPrice = unitPrice;
        }

        public String getItemName() { return itemName; }
        public void setItemName(String itemName) { this.itemName = itemName; }

        public int getQuantity() { return quantity; }
        public void setQuantity(int quantity) { this.quantity = quantity; }

        public double getUnitPrice() { return unitPrice; }
        public void setUnitPrice(double unitPrice) { this.unitPrice = unitPrice; }

        public double getSubtotal() { return quantity * unitPrice; }
    }
}
