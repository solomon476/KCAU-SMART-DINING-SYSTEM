package com.kcau.dining.model;

/**
 * Represents a cafeteria food/drink menu item.
 */
public class MenuItem {
    private String id;
    private String name;
    private String description;
    private double price;    // in KES
    private String category; // "breakfast", "lunch", "drinks", "fruits", "snacks"
    private String image;
    private boolean available;

    public MenuItem() {
        this.available = true;
    }

    public MenuItem(String id, String name, String category, double price, String image) {
        this(id, name, "", category, price, image, true);
    }

    public MenuItem(String id, String name, String description, String category, double price, String image, boolean available) {
        this.id = id;
        this.name = name;
        this.description = description != null ? description : "";
        this.category = category;
        this.price = price;
        this.image = image;
        this.available = available;
    }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }

    public double getPrice() { return price; }
    public void setPrice(double price) { this.price = price; }

    public String getImage() { return image; }
    public void setImage(String image) { this.image = image; }

    public boolean isAvailable() { return available; }
    public void setAvailable(boolean available) { this.available = available; }

    @Override
    public String toString() {
        return "MenuItem{" +
                "id='" + id + '\'' +
                ", name='" + name + '\'' +
                ", category='" + category + '\'' +
                ", price=" + price +
                ", available=" + available +
                '}';
    }
}
