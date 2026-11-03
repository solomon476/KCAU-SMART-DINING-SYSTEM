package com.kcau.dining.model;

import java.time.Instant;

/**
 * Represents a payment transaction (simulated or real) for a dining order.
 */
public class Payment {
    private String id;
    private String orderId;
    private String method;    // "MPESA", "AIRTEL", "CARD", "CASH"
    private double amount;
    private String status;    // "COMPLETED", "SIMULATED", "PENDING", "FAILED"
    private String reference; // Transaction reference code e.g. QA89X45Y7Z
    private Instant createdAt;

    public Payment() {
        this.status = "SIMULATED";
        this.createdAt = Instant.now();
    }

    public Payment(String id, String orderId, String method, double amount, String status, String reference, Instant createdAt) {
        this.id = id;
        this.orderId = orderId;
        this.method = method;
        this.amount = amount;
        this.status = (status != null && !status.isBlank()) ? status : "SIMULATED";
        this.reference = reference;
        this.createdAt = (createdAt != null) ? createdAt : Instant.now();
    }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getOrderId() { return orderId; }
    public void setOrderId(String orderId) { this.orderId = orderId; }

    public String getMethod() { return method; }
    public void setMethod(String method) { this.method = method; }

    public double getAmount() { return amount; }
    public void setAmount(double amount) { this.amount = amount; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getReference() { return reference; }
    public void setReference(String reference) { this.reference = reference; }

    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }

    @Override
    public String toString() {
        return "Payment{" +
                "id='" + id + '\'' +
                ", orderId='" + orderId + '\'' +
                ", method='" + method + '\'' +
                ", amount=" + amount +
                ", status='" + status + '\'' +
                ", reference='" + reference + '\'' +
                '}';
    }
}
