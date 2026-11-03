package com.kcau.dining.database;

import java.io.File;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

/**
 * Manages SQLite database connectivity for the KCAU Smart Dining System.
 */
public class DatabaseConnection {

    private static final String DB_PATH = "data/dining.db";
    private static final String JDBC_URL = "jdbc:sqlite:" + DB_PATH;

    static {
        try {
            Class.forName("org.sqlite.JDBC");
        } catch (ClassNotFoundException e) {
            System.err.println("⚠️  SQLite JDBC Driver not found in classpath. Ensure lib/sqlite-jdbc.jar is included.");
        }
    }

    /**
     * Gets a new connection to the SQLite database.
     * Ensures parent directories exist.
     */
    public static Connection getConnection() throws SQLException {
        File dbFile = new File(DB_PATH);
        File parentDir = dbFile.getParentFile();
        if (parentDir != null && !parentDir.exists()) {
            parentDir.mkdirs();
        }
        return DriverManager.getConnection(JDBC_URL);
    }

    public static String getDbPath() {
        return DB_PATH;
    }
}
