/**
 * Root-level Model for KCAU Smart Dining System
 * Extends the modular com.kcau.dining.model.User
 */
public class User extends com.kcau.dining.model.User {
    public User() {
        super();
    }

    public User(String id, String name, String studentId, String passwordHash, String role) {
        super(id, name, studentId, passwordHash, role);
    }
}
