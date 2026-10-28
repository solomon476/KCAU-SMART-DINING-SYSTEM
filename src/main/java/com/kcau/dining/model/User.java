package com.kcau.dining.model;

import java.time.Instant;

/**
 * Represents a student or staff user in the Smart Dining System.
 */
public class User {
    private String id;
    private String name;
    private String studentId;
    private String passwordHash;
    private Instant createdAt;

    public User() {
        this.createdAt = Instant.now();
    }

    public User(String id, String name, String studentId, String passwordHash) {
        this.id = id;
        this.name = name;
        this.studentId = studentId;
        this.passwordHash = passwordHash;
        this.createdAt = Instant.now();
    }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getStudentId() { return studentId; }
    public void setStudentId(String studentId) { this.studentId = studentId; }

    public String getPasswordHash() { return passwordHash; }
    public void setPasswordHash(String passwordHash) { this.passwordHash = passwordHash; }

    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }

    @Override
    public String toString() {
        return "User{" +
                "id='" + id + '\'' +
                ", name='" + name + '\'' +
                ", studentId='" + studentId + '\'' +
                ", createdAt=" + createdAt +
                '}';
    }
}
