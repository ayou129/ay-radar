"""AI Radar 服务 — FastAPI 单文件后端。

启动: python server.py
访问: http://localhost:8002
"""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "data.db"


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS ai_discovery (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            platform TEXT DEFAULT 'x',
            author TEXT DEFAULT '',
            title TEXT DEFAULT '',
            summary TEXT DEFAULT '',
            category TEXT DEFAULT 'trend',
            importance TEXT DEFAULT 'medium',
            published_at TEXT,
            discovered_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            round_id TEXT DEFAULT '',
            raw_data TEXT,
            md TEXT
        );
        CREATE TABLE IF NOT EXISTS ai_follow_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT DEFAULT 'x',
            username TEXT UNIQUE NOT NULL,
            reason TEXT DEFAULT '',
            followed_at TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'success'
        );
    """)
    conn.commit()
    conn.close()


@asynccontextmanager
async def lifespan(app):
    init_db()
    logger.info("AI Radar 服务已启动 → http://localhost:8002")
    yield

app = FastAPI(title="AI Radar", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/")
async def index():
    return FileResponse(BASE_DIR / "index.html")


# ── Discovery API ──

class DiscoveryReq(BaseModel):
    url: str
    platform: str = "x"
    author: str = ""
    title: str = ""
    summary: str = ""
    category: str = "trend"
    importance: str = "medium"
    published_at: str | None = None
    round_id: str = ""
    raw_data: str | None = None
    md: str | None = None


@app.get("/api/discoveries")
async def list_discoveries(
    page: int = 1,
    page_size: int = 50,
    platform: str | None = None,
    category: str | None = None,
    importance: str | None = None,
    author: str | None = None,
    sort_by: str = "id",
    sort_order: str = "DESC",
):
    conn = get_db()
    allowed_sort = {"id", "discovered_at", "updated_at", "importance", "platform"}
    if sort_by not in allowed_sort:
        sort_by = "id"
    if sort_order.upper() not in ("ASC", "DESC"):
        sort_order = "DESC"

    where_parts: list[str] = []
    params: list = []
    if platform:
        where_parts.append("platform = ?")
        params.append(platform)
    if category:
        where_parts.append("category = ?")
        params.append(category)
    if importance:
        where_parts.append("importance = ?")
        params.append(importance)
    if author:
        where_parts.append("author = ?")
        params.append(author)

    where_sql = ("WHERE " + " AND ".join(where_parts)) if where_parts else ""
    offset = (page - 1) * page_size

    total = conn.execute(f"SELECT COUNT(*) FROM ai_discovery {where_sql}", params).fetchone()[0]
    rows = conn.execute(
        f"SELECT * FROM ai_discovery {where_sql} ORDER BY {sort_by} {sort_order} LIMIT ? OFFSET ?",
        params + [page_size, offset],
    ).fetchall()
    conn.close()
    return {"discoveries": [dict(r) for r in rows], "total": total, "page": page, "page_size": page_size}


@app.get("/api/discoveries/stats")
async def discovery_stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM ai_discovery").fetchone()[0]
    today = conn.execute(
        "SELECT COUNT(*) FROM ai_discovery WHERE date(discovered_at) = date('now')"
    ).fetchone()[0]
    by_importance = {}
    for row in conn.execute("SELECT importance, COUNT(*) as cnt FROM ai_discovery GROUP BY importance"):
        by_importance[row["importance"]] = row["cnt"]
    by_category = {}
    for row in conn.execute("SELECT category, COUNT(*) as cnt FROM ai_discovery GROUP BY category"):
        by_category[row["category"]] = row["cnt"]
    follows = conn.execute("SELECT COUNT(*) FROM ai_follow_log WHERE status = 'success'").fetchone()[0]
    conn.close()
    return {"total": total, "today": today, "by_importance": by_importance, "by_category": by_category, "follows": follows}


@app.get("/api/discoveries/authors")
async def list_discovery_authors():
    conn = get_db()
    rows = conn.execute("SELECT DISTINCT author FROM ai_discovery WHERE author != '' ORDER BY author").fetchall()
    conn.close()
    return {"authors": [r["author"] for r in rows]}


@app.post("/api/discoveries")
async def upsert_discovery(req: DiscoveryReq):
    conn = get_db()
    existing = conn.execute("SELECT id FROM ai_discovery WHERE url = ?", (req.url,)).fetchone()
    if existing:
        conn.execute(
            """UPDATE ai_discovery SET summary=?, importance=?, category=?, updated_at=?, round_id=?, raw_data=?,
               md=COALESCE(?, md)
               WHERE id=?""",
            (req.summary, req.importance, req.category, _now(), req.round_id, req.raw_data, req.md, existing["id"]),
        )
        conn.commit()
        conn.close()
        return {"status": "updated", "id": existing["id"]}
    else:
        cursor = conn.execute(
            """INSERT INTO ai_discovery (url, platform, author, title, summary, category, importance, published_at, discovered_at, updated_at, round_id, raw_data, md)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (req.url, req.platform, req.author, req.title, req.summary, req.category,
             req.importance, req.published_at, _now(), _now(), req.round_id, req.raw_data, req.md),
        )
        conn.commit()
        conn.close()
        return {"status": "created", "id": cursor.lastrowid}


@app.get("/api/discoveries/{discovery_id}")
async def get_discovery(discovery_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM ai_discovery WHERE id = ?", (discovery_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "记录不存在")
    return dict(row)


@app.delete("/api/discoveries/{discovery_id}")
async def delete_discovery(discovery_id: int):
    conn = get_db()
    conn.execute("DELETE FROM ai_discovery WHERE id = ?", (discovery_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}


@app.get("/api/discoveries/{discovery_id}/article")
async def get_discovery_article(discovery_id: int):
    """读取 discovery 的 md 字段，渲染为 HTML 返回。"""
    conn = get_db()
    row = conn.execute("SELECT md FROM ai_discovery WHERE id = ?", (discovery_id,)).fetchone()
    conn.close()
    if not row or not row["md"]:
        raise HTTPException(404, "该记录没有分析文章")
    import markdown as md_lib
    html = md_lib.markdown(row["md"], extensions=["extra", "codehilite", "toc"])
    return {"html": html}


# ── Follow Log API ──

class FollowReq(BaseModel):
    platform: str = "x"
    username: str
    reason: str = ""
    status: str = "success"


@app.get("/api/follow-log")
async def list_follow_log(page: int = 1, page_size: int = 50):
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM ai_follow_log").fetchone()[0]
    offset = (page - 1) * page_size
    rows = conn.execute(
        "SELECT * FROM ai_follow_log ORDER BY id DESC LIMIT ? OFFSET ?",
        [page_size, offset],
    ).fetchall()
    conn.close()
    return {"follows": [dict(r) for r in rows], "total": total}


@app.post("/api/follow-log")
async def add_follow_log(req: FollowReq):
    conn = get_db()
    existing = conn.execute("SELECT id FROM ai_follow_log WHERE username = ? AND platform = ?", (req.username, req.platform)).fetchone()
    if existing:
        conn.close()
        return {"status": "exists", "id": existing["id"]}
    cursor = conn.execute(
        "INSERT INTO ai_follow_log (platform, username, reason, followed_at, status) VALUES (?, ?, ?, ?, ?)",
        (req.platform, req.username, req.reason, _now(), req.status),
    )
    conn.commit()
    conn.close()
    return {"status": "created", "id": cursor.lastrowid}


# ── 启动 ──

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8002, reload=True)
