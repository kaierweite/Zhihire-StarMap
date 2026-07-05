import bcrypt
hash = bcrypt.hashpw(b'admin123', bcrypt.gensalt(rounds=10))
print(hash.decode())