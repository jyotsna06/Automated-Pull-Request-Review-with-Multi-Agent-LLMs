"""
Test file with intentional security vulnerabilities for testing PR review system.
DO NOT USE IN PRODUCTION - This file is for testing purposes only.
"""

import os
import subprocess
import sqlite3
import hashlib

# Vulnerability 1: Hardcoded password/secret
API_KEY = "sk_live_1234567890abcdef"
DATABASE_PASSWORD = "admin123"

# Vulnerability 2: SQL Injection vulnerability
def get_user_data(username):
    """Vulnerable to SQL injection"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # BAD: Direct string concatenation in SQL query
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    return cursor.fetchall()

# Vulnerability 3: Use of insecure hash function
def hash_password(password):
    """Uses insecure MD5 hash"""
    return hashlib.md5(password.encode()).hexdigest()

# Vulnerability 4: Command injection vulnerability
def run_command(user_input):
    """Vulnerable to command injection"""
    # BAD: Direct execution of user input
    os.system(f"echo {user_input}")

# Vulnerability 5: Hardcoded credentials in code
def connect_to_database():
    """Hardcoded database credentials"""
    db_user = "admin"
    db_pass = "password123"
    return sqlite3.connect(f"sqlite:///{db_user}:{db_pass}@localhost/db")

# Vulnerability 6: Use of eval() with user input
def calculate_expression(expression):
    """Dangerous use of eval()"""
    # BAD: eval() can execute arbitrary code
    result = eval(expression)
    return result

# Vulnerability 7: Insecure random number generation
import random
def generate_token():
    """Uses insecure random for security token"""
    # BAD: random is not cryptographically secure
    return random.randint(1000, 9999)

# Vulnerability 8: Missing input validation
def process_file(filename):
    """No input validation on file path"""
    # BAD: No validation, could lead to path traversal
    with open(filename, 'r') as f:
        return f.read()

# Vulnerability 9: Use of pickle with untrusted data
import pickle
def load_data(data):
    """Unsafe deserialization"""
    # BAD: pickle can execute arbitrary code
    return pickle.loads(data)

# Vulnerability 10: Weak cryptographic function
def encrypt_data(data):
    """Uses weak encryption"""
    # BAD: XOR is not secure encryption
    key = b"secret"
    return bytes(a ^ b for a, b in zip(data.encode(), key))

if __name__ == "__main__":
    # Test the vulnerable functions
    print("This file contains intentional vulnerabilities for testing!")
    print("DO NOT USE IN PRODUCTION!")

