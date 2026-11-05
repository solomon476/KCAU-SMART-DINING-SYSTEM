package com.kcau.dining.service;

import com.kcau.dining.database.DatabaseConnection;
import com.kcau.dining.database.DatabaseInitializer;
import com.kcau.dining.model.User;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * Business service handling user accounts, roles, and authentication.
 */
public class UserService {

    public User registerUser(String name, String studentId, String password, String role) throws Exception {
        if (name == null || name.isBlank() || studentId == null || studentId.isBlank() || password == null || password.isBlank()) {
            throw new IllegalArgumentException("All fields (name, student ID, and password) are required");
        }

        String normId = studentId.trim().toUpperCase();
        if (getUserByStudentId(normId) != null) {
            throw new IllegalArgumentException("An account with Student ID '" + studentId.trim() + "' already exists");
        }

        String userRole = (role != null && !role.isBlank()) ? role.trim().toLowerCase() : "student";
        String hashedPassword = DatabaseInitializer.hashPassword(password);
        String userId = UUID.randomUUID().toString();
        Instant now = Instant.now();

        String sql = "INSERT INTO users (id, name, student_id, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?, ?)";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, userId);
            pstmt.setString(2, name.trim());
            pstmt.setString(3, normId);
            pstmt.setString(4, hashedPassword);
            pstmt.setString(5, userRole);
            pstmt.setString(6, now.toString());
            pstmt.executeUpdate();
        }

        return new User(userId, name.trim(), normId, hashedPassword, userRole, now);
    }

    public User authenticate(String studentId, String password) throws Exception {
        if (studentId == null || studentId.isBlank() || password == null || password.isBlank()) {
            throw new IllegalArgumentException("Student ID / Username and password are required");
        }

        String normId = studentId.trim();
        User user = getUserByStudentId(normId);
        if (user == null) {
            throw new IllegalArgumentException("No account found matching '" + studentId.trim() + "'. Please check your Student ID/Username or sign up first!");
        }

        if (!DatabaseInitializer.verifyPassword(password, user.getPasswordHash())) {
            throw new IllegalArgumentException("Incorrect password for " + user.getName() + " (" + user.getStudentId() + "). Please try again.");
        }

        return user;
    }

    public User getUserByStudentId(String studentId) throws Exception {
        if (studentId == null || studentId.isBlank()) return null;
        String raw = studentId.trim();
        String upper = raw.toUpperCase();

        String sql = """
            SELECT id, name, student_id, password_hash, role, created_at FROM users 
            WHERE UPPER(student_id) = ? 
               OR UPPER(id) = ? 
               OR UPPER(role) = ?
               OR UPPER(name) = ?
               OR UPPER(name) LIKE ?
            ORDER BY 
               CASE 
                 WHEN UPPER(student_id) = ? THEN 1
                 WHEN UPPER(id) = ? THEN 2
                 WHEN UPPER(role) = ? THEN 3
                 ELSE 4
               END
            LIMIT 1
        """;
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, upper);
            pstmt.setString(2, upper);
            pstmt.setString(3, upper);
            pstmt.setString(4, upper);
            pstmt.setString(5, "%" + upper + "%");
            pstmt.setString(6, upper);
            pstmt.setString(7, upper);
            pstmt.setString(8, upper);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    Instant createdAt = Instant.parse(rs.getString("created_at"));
                    return new User(
                        rs.getString("id"),
                        rs.getString("name"),
                        rs.getString("student_id"),
                        rs.getString("password_hash"),
                        rs.getString("role"),
                        createdAt
                    );
                }
            }
        }
        return null;
    }

    public List<User> getAllUsers() throws Exception {
        List<User> list = new ArrayList<>();
        String sql = "SELECT id, name, student_id, password_hash, role, created_at FROM users ORDER BY created_at DESC";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql);
             ResultSet rs = pstmt.executeQuery()) {
            while (rs.next()) {
                Instant createdAt = Instant.parse(rs.getString("created_at"));
                list.add(new User(
                    rs.getString("id"),
                    rs.getString("name"),
                    rs.getString("student_id"),
                    rs.getString("password_hash"),
                    rs.getString("role"),
                    createdAt
                ));
            }
        }
        return list;
    }

    public boolean updateUserRole(String userId, String newRole) throws Exception {
        String sql = "UPDATE users SET role = ? WHERE id = ? OR UPPER(student_id) = ?";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, newRole.toLowerCase().trim());
            pstmt.setString(2, userId);
            pstmt.setString(3, userId.toUpperCase().trim());
            return pstmt.executeUpdate() > 0;
        }
    }
}
