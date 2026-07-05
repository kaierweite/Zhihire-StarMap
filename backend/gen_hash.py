import bcrypt
hash = bcrypt.hashpw(b'admin123', bcrypt.gensalt(rounds=10))
# Convert $ to $ for Spring Security compatibility
print(hash.decode().replace('$2b$', '$2a$'))