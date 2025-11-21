"""
Third test file with intentional security vulnerabilities for exercising the PR review pipeline.
DO NOT USE IN PRODUCTION.
"""

import os
import subprocess
import tempfile
import yaml
import secrets
import requests
from flask import Flask, request

app = Flask(__name__)

# Vulnerability 1: Hardcoded secret key & debug mode enabled
app.config["SECRET_KEY"] = "super-secret-flask-key"
app.config["DEBUG"] = True  # BAD: Debug mode in production exposes internals

# Vulnerability 2: OS command injection via shell=True
@app.route("/run")
def run_command():
    """Execute arbitrary shell commands from query parameter"""
    cmd = request.args.get("cmd", "")
    # BAD: shell=True with untrusted input
    output = subprocess.check_output(cmd, shell=True)
    return output.decode()

# Vulnerability 3: Path traversal when reading files
@app.route("/config")
def read_config():
    """Reads any file on the filesystem"""
    filename = request.args.get("file", "config.yaml")
    # BAD: No validation on path, allows ../../etc/passwd
    with open(filename, "r", encoding="utf-8") as fh:
        return fh.read()

# Vulnerability 4: Unsafe YAML deserialization
def load_yaml_config(config_str):
    """Uses yaml.load with default loader (unsafe)"""
    # BAD: yaml.load can execute arbitrary code
    return yaml.load(config_str, Loader=yaml.Loader)

# Vulnerability 5: Predictable temp file creation
def write_temp_file(data):
    """Creates temp file with predictable name"""
    # BAD: Predictable temp file path
    temp_path = os.path.join(tempfile.gettempdir(), "app_temp.txt")
    with open(temp_path, "w", encoding="utf-8") as tmp:
        tmp.write(data)
    return temp_path

# Vulnerability 6: SSRF via unvalidated URL fetch
def fetch_internal_url():
    """Allows fetching arbitrary URLs including internal services"""
    target = request.args.get("target", "http://localhost:5000/health")
    # BAD: No validation, could hit internal metadata services
    resp = requests.get(target, timeout=5)
    return resp.text

# Vulnerability 7: Insecure random token (predictable)
def issue_token(user_id):
    """Uses predictable hex token"""
    # BAD: secrets.token_hex is fine, but mixing predictable data compromises it
    deterministic = f"{user_id}-" + os.urandom(2).hex()
    return deterministic


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

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

