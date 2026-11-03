/**
 * Root-level Model for KCAU Smart Dining System
 * Extends the modular com.kcau.dining.model.MenuItem
 */
public class MenuItem extends com.kcau.dining.model.MenuItem {
    public MenuItem() {
        super();
    }

    public MenuItem(String id, String name, String category, double price, String description, String image, boolean available) {
        super(id, name, category, price, description, image, available);
    }
}
