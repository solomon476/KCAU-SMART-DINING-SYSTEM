/**
 * Root Launcher for KCAU Smart Dining System
 * Seamlessly boots the modular com.kcau.dining.Server backend.
 */
public class Server {
    public static void main(String[] args) throws Exception {
        try {
            Class<?> cls = Class.forName("com.kcau.dining.Server");
            cls.getMethod("main", String[].class).invoke(null, (Object) args);
        } catch (Throwable t) {
            // Forward to the modular entry point with bundled library dependencies
            java.util.List<String> cmd = new java.util.ArrayList<>();
            cmd.add("java");
            cmd.add("-cp");
            cmd.add("lib/*");
            cmd.add("src/main/java/com/kcau/dining/Server.java");
            if (args != null) {
                java.util.Collections.addAll(cmd, args);
            }
            ProcessBuilder pb = new ProcessBuilder(cmd);
            pb.inheritIO();
            Process p = pb.start();
            System.exit(p.waitFor());
        }
    }
}
