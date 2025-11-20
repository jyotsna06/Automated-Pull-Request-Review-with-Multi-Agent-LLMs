"""
Another test file with intentional security vulnerabilities for testing PR review system.
DO NOT USE IN PRODUCTION - This file is for testing purposes only.
"""

import os
import subprocess
import sqlite3
import hashlib
import pickle
import base64
import urllib.parse

# Vulnerability 1: Hardcoded API credentials
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
DATABASE_URL = "postgresql://admin:SuperSecret123@localhost:5432/mydb"

# Vulnerability 2: SQL Injection with user input
def search_users(search_term):
    """Vulnerable SQL injection - direct string interpolation"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # BAD: User input directly in SQL query
    query = f"SELECT * FROM users WHERE name LIKE '%{search_term}%'"
    cursor.execute(query)
    return cursor.fetchall()

# Vulnerability 3: Command injection via subprocess
def execute_user_command(user_input):
    """Dangerous command execution"""
    # BAD: User input executed as shell command
    result = subprocess.run(f"ping {user_input}", shell=True, capture_output=True)
    return result.stdout.decode()

# Vulnerability 4: Weak cryptographic hash (SHA1)
def hash_user_password(password):
    """Uses weak SHA1 hash instead of bcrypt/argon2"""
    # BAD: SHA1 is cryptographically broken
    return hashlib.sha1(password.encode()).hexdigest()

# Vulnerability 5: Unsafe deserialization with pickle
def load_user_preferences(data_string):
    """Unsafe deserialization - can execute arbitrary code"""
    # BAD: pickle.loads can execute malicious code
    data = base64.b64decode(data_string)
    return pickle.loads(data)

# Vulnerability 6: Path traversal vulnerability
def read_config_file(filename):
    """No validation on file path - path traversal risk"""
    # BAD: No validation, could read ../../../etc/passwd
    file_path = os.path.join("/app/config", filename)
    with open(file_path, 'r') as f:
        return f.read()

# Vulnerability 7: Use of eval() with user input
def calculate_user_expression(expression):
    """Dangerous eval() usage"""
    # BAD: eval() can execute arbitrary Python code
    return eval(expression)

# Vulnerability 8: Insecure random for security tokens
import random
def generate_session_token():
    """Uses insecure random for security-critical token"""
    # BAD: random is not cryptographically secure
    token = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=32))
    return token

# Vulnerability 9: Hardcoded encryption key
ENCRYPTION_KEY = b"my-secret-key-12345"  # BAD: Hardcoded key

def encrypt_sensitive_data(data):
    """Weak encryption with hardcoded key"""
    # BAD: Simple XOR encryption with hardcoded key
    encrypted = bytes(a ^ b for a, b in zip(data.encode(), ENCRYPTION_KEY))
    return base64.b64encode(encrypted).decode()

# Vulnerability 10: SSRF (Server-Side Request Forgery) risk
def fetch_url(url):
    """No validation on URL - SSRF risk"""
    # BAD: Could request internal services
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme in ['http', 'https']:
        import urllib.request
        return urllib.request.urlopen(url).read()
    return None

# Example usage (for testing)
if __name__ == "__main__":
    print("This file contains intentional vulnerabilities for testing!")
    print("DO NOT USE IN PRODUCTION!")
    
    # Test the vulnerable functions
    # search_users("'; DROP TABLE users; --")
    # execute_user_command("8.8.8.8; rm -rf /")
    # hash_user_password("password123")
    # calculate_user_expression("__import__('os').system('ls')")

