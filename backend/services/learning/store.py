import sqlite3, os, json
DB = os.getenv("LEARNING_DB", "learning.db")

def init_db():
    with sqlite3.connect(DB) as c:
        c.execute("""CREATE TABLE IF NOT EXISTS suggestions(
            id INTEGER PRIMARY KEY,
            repo TEXT, pr INTEGER, path TEXT, line INTEGER,
            body TEXT, severity TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            resolved INTEGER DEFAULT 0, resolution_note TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS metrics(
            id INTEGER PRIMARY KEY,
            repo TEXT, metric TEXT, value REAL, ts DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")

def save_suggestions(repo, pr, inline_comments):
    with sqlite3.connect(DB) as c:
        for ic in inline_comments:
            c.execute("""INSERT INTO suggestions(repo,pr,path,line,body,severity) VALUES(?,?,?,?,?,?)""",
                      (repo, pr, ic["path"], ic["line"], ic["body"], ic.get("severity","MEDIUM")))

def save_metric(repo: str, metric: str, value: float):
    with sqlite3.connect(DB) as c:
        c.execute(
            """INSERT INTO metrics(repo, metric, value) VALUES(?,?,?)""",
            (repo, metric, float(value))
        )