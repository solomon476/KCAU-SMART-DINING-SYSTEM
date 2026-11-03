package com.kcau.dining.model;

/**
 * Represents a single line item within a cafeteria customer order.
 */
public class OrderItem {
    private int id;
    private String orderId;
    private String foodId;
    private String foodName;
    private int quantity;
    private double unitPrice;

    public OrderItem() {}

    public OrderItem(String foodId, String foodName, int quantity, double unitPrice) {
        this.foodId = foodId;
        this.foodName = foodName;
        this.quantity = quantity;
        this.unitPrice = unitPrice;
    }

    public OrderItem(int id, String orderId, String foodId, String foodName, int quantity, double unitPrice) {
        this.id = id;
        this.orderId = orderId;
        this.foodId = foodId;
        this.foodName = foodName;
        this.quantity = quantity;
        this.unitPrice = unitPrice;
    }

    public int getId() { return id; }
    public void setId(int id) { this.id = id; }

    public String getOrderId() { return orderId; }
    public void setOrderId(String orderId) { this.orderId = orderId; }

    public String getFoodId() { return foodId; }
    public void setFoodId(String foodId) { this.foodId = foodId; }

    public String getFoodName() { return foodName; }
    public void setFoodName(String foodName) { this.foodName = foodName; }

    public int getQuantity() { return quantity; }
    public void setQuantity(int quantity) { this.quantity = quantity; }

    public double getUnitPrice() { return unitPrice; }
    public void setUnitPrice(double unitPrice) { this.unitPrice = unitPrice; }

    public double getSubtotal() { return quantity * unitPrice; }

    @Override
    public String toString() {
        return "OrderItem{" +
                "foodName='" + foodName + '\'' +
                ", quantity=" + quantity +
                ", unitPrice=" + unitPrice +
                ", subtotal=" + getSubtotal() +
                '}';
    }
}
