from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3, os

DB = os.getenv("LEARNING_DB", "learning.db")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/metrics/top")
def top_metrics():
	try:
		with sqlite3.connect(DB) as c:
			rows = c.execute("SELECT repo, metric, AVG(value) FROM metrics GROUP BY repo, metric").fetchall()
			return [{"repo": r[0], "metric": r[1], "avg": r[2]} for r in rows]
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
	return {"ok": True}
