/**
 * Root-level Model for KCAU Smart Dining System
 * Extends the modular com.kcau.dining.model.Order
 */
public class Order extends com.kcau.dining.model.Order {
    public Order() {
        super();
    }

    public Order(String orderId, String userId, String customerName, double totalAmount, String status) {
        super(orderId, userId, customerName, totalAmount, status);
    }
}
