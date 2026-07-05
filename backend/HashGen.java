import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
public class HashGen {
    public static void main(String[] args) {
        BCryptPasswordEncoder enc = new BCryptPasswordEncoder();
        System.out.println(enc.encode("admin123"));
        System.out.println("MATCH: " + enc.matches("admin123", "$2a$10$EqKpf1OFJiGQEhFBJp5XOeJibkKJdfKPUqMCPd./4A7/XYz3k3XHm"));
    }
}
