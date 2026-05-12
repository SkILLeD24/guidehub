from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from flask import Flask, jsonify, request, session, redirect
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DB_NAME = BASE_DIR / "guidehub.db"

app = Flask(__name__, static_folder=".", static_url_path="")
app.secret_key = "guidehub-secret-key-change-me"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def row_to_dict(row):
    return dict(row) if row else None


def parse_platforms(raw):
    if not raw:
        return []
    if isinstance(raw, list):
        return raw
    try:
        return json.loads(raw)
    except Exception:
        return [item.strip() for item in str(raw).split(",") if item.strip()]


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    conn = get_connection()
    row = conn.execute("SELECT id, username, email, role FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return row_to_dict(row)


def require_admin() -> bool:
    user = get_current_user()
    return bool(user and user["role"] == "admin")


def serialize_game(row):
    game = dict(row)
    game["platforms"] = parse_platforms(game.get("platforms"))
    return game


@app.route("/")
def root():
    return app.send_static_file("index.html")


@app.route("/index.html")
def home_page():
    return app.send_static_file("index.html")


@app.route("/game.html")
def game_page():
    return app.send_static_file("game.html")


@app.route("/register.html")
def register_page():
    return app.send_static_file("register.html")


@app.route("/submit.html")
def submit_page():
    user = get_current_user()
    if not user:
        return redirect("/index.html")
    return app.send_static_file("submit.html")


@app.route("/admin.html")
def admin_page():
    user = get_current_user()
    if not user:
        return redirect("/index.html")
    if user["role"] != "admin":
        return redirect("/submit.html")
    return app.send_static_file("admin.html")


@app.route("/api/auth/me", methods=["GET"])
def auth_me():
    user = get_current_user()
    if not user:
        return jsonify({"authenticated": False, "username": None, "email": None, "role": "guest"}), 200
    return jsonify({"authenticated": True, "username": user["username"], "email": user["email"], "role": user["role"]}), 200


@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    session.clear()
    session["user_id"] = user["id"]
    return jsonify({"message": "Login successful", "username": user["username"], "role": user["role"]}), 200


@app.route("/api/auth/logout", methods=["POST"])
def auth_logout():
    session.clear()
    return jsonify({"message": "Logout successful"}), 200


@app.route("/api/auth/register", methods=["POST"])
def auth_register():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    confirm_password = data.get("confirmPassword", "").strip()

    if not username or not email or not password or not confirm_password:
        return jsonify({"error": "All fields are required"}), 400
    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    conn = get_connection()
    existing = conn.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email)).fetchone()
    if existing:
        conn.close()
        return jsonify({"error": "Username or email already exists"}), 409

    conn.execute(
        "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
        (username, email, generate_password_hash(password), "user")
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Account created successfully"}), 201


@app.route("/api/games", methods=["GET"])
def get_games():
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT
            g.id, g.title, g.slug, g.description, g.image_url, g.genre, g.difficulty,
            g.studio, g.release_year, g.platforms, g.official_url,
            COALESCE((SELECT COUNT(1) FROM articles a WHERE a.game_id = g.id AND a.status = 'approved'), 0) AS approved_articles,
            COALESCE((SELECT COUNT(1) FROM game_sources s WHERE s.game_id = g.id), 0) AS source_count
        FROM games g
        ORDER BY g.title
        """
    ).fetchall()
    conn.close()
    return jsonify([serialize_game(row) for row in rows]), 200


@app.route("/api/admin/summary", methods=["GET"])
def admin_summary():
    if not require_admin():
        return jsonify({"error": "Admin access required"}), 403
    conn = get_connection()
    result = {
        "games": conn.execute("SELECT COUNT(1) FROM games").fetchone()[0],
        "users": conn.execute("SELECT COUNT(1) FROM users").fetchone()[0],
        "approved": conn.execute("SELECT COUNT(1) FROM articles WHERE status = 'approved'").fetchone()[0],
        "pending": conn.execute("SELECT COUNT(1) FROM articles WHERE status = 'pending'").fetchone()[0],
        "rejected": conn.execute("SELECT COUNT(1) FROM articles WHERE status = 'rejected'").fetchone()[0],
        "sources": conn.execute("SELECT COUNT(1) FROM game_sources").fetchone()[0],
    }
    conn.close()
    return jsonify(result), 200


@app.route("/api/articles/latest", methods=["GET"])
def latest_articles():
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT
            a.id, a.title, a.summary, a.created_at,
            c.name AS category,
            g.title AS game,
            g.slug AS game_slug,
            u.username AS author
        FROM articles a
        JOIN categories c ON c.id = a.category_id
        JOIN games g ON g.id = a.game_id
        JOIN users u ON u.id = a.user_id
        WHERE a.status = 'approved' AND c.name NOT IN ('Codes', 'Discount Coupons')
        ORDER BY a.created_at DESC, a.id DESC
        LIMIT 6
        """
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200


@app.route("/api/games/<slug>", methods=["GET"])
def game_details(slug):
    conn = get_connection()
    game = conn.execute(
        """
        SELECT id, title, slug, description, image_url, genre, difficulty, studio, release_year, platforms, official_url
        FROM games WHERE slug = ?
        """,
        (slug,)
    ).fetchone()
    if not game:
        conn.close()
        return jsonify({"error": "Game not found"}), 404

    articles = conn.execute(
        """
        SELECT a.id, a.title, a.summary, a.content, a.status, a.created_at,
               c.name AS category, u.username AS author
        FROM articles a
        JOIN categories c ON c.id = a.category_id
        JOIN users u ON u.id = a.user_id
        WHERE a.game_id = ? AND a.status = 'approved'
        ORDER BY a.created_at DESC, a.id DESC
        """,
        (game["id"],)
    ).fetchall()

    full_articles = []
    for article in articles:
        sources = conn.execute("SELECT id, title, url FROM sources WHERE article_id = ? ORDER BY id", (article["id"],)).fetchall()
        item = dict(article)
        item["sources"] = [dict(s) for s in sources]
        full_articles.append(item)

    sources = conn.execute("SELECT id, title, url FROM game_sources WHERE game_id = ? ORDER BY id", (game["id"],)).fetchall()
    conn.close()

    serialized_game = serialize_game(game)
    return jsonify({"game": serialized_game, "articles": full_articles, "sources": [dict(s) for s in sources]}), 200


@app.route("/api/games", methods=["POST"])
def create_game():
    if not require_admin():
        return jsonify({"error": "Admin access required"}), 403
    data = request.get_json() or {}
    title = data.get("title", "").strip()
    slug = data.get("slug", "").strip().lower()
    description = data.get("description", "").strip()
    image_url = data.get("image_url", "").strip() or "assets/images/guidehub-logo.png"
    genre = data.get("genre", "").strip()
    difficulty = data.get("difficulty", "").strip() or "Medium"
    studio = data.get("studio", "").strip() or "Independent Studio"
    release_year = int(data.get("release_year") or 2026)
    platforms = data.get("platforms") or []
    if isinstance(platforms, str):
        platforms = [p.strip() for p in platforms.split(",") if p.strip()]
    official_url = data.get("official_url", "").strip() or "#"

    if not title or not slug or not description or not genre:
        return jsonify({"error": "Title, slug, description and genre are required"}), 400

    conn = get_connection()
    exists = conn.execute("SELECT id FROM games WHERE slug = ?", (slug,)).fetchone()
    if exists:
        conn.close()
        return jsonify({"error": "Game slug already exists"}), 409

    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO games (title, slug, description, image_url, genre, difficulty, studio, release_year, platforms, official_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (title, slug, description, image_url, genre, difficulty, studio, release_year, json.dumps(platforms), official_url)
    )
    game_id = cur.lastrowid
    cur.execute("INSERT INTO game_sources (game_id, title, url) VALUES (?, ?, ?)", (game_id, f"{title} official source", official_url))
    conn.commit()
    conn.close()
    return jsonify({"message": "Game created successfully", "slug": slug}), 201


@app.route("/api/articles/submit", methods=["POST"])
def submit_article():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Login required"}), 401
    data = request.get_json() or {}
    game_slug = data.get("gameSlug", "").strip()
    category_name = data.get("category", "").strip()
    title = data.get("title", "").strip()
    summary = data.get("summary", "").strip()
    content = data.get("content", "").strip()
    source_title = data.get("sourceTitle", "").strip()
    source_url = data.get("sourceUrl", "").strip()

    if not game_slug or not category_name or not title or not content:
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_connection()
    game = conn.execute("SELECT id FROM games WHERE slug = ?", (game_slug,)).fetchone()
    category = conn.execute("SELECT id FROM categories WHERE name = ?", (category_name,)).fetchone()
    if not game or not category:
        conn.close()
        return jsonify({"error": "Invalid game or category"}), 404

    status = "approved" if user["role"] == "admin" else "pending"
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO articles (game_id, category_id, user_id, title, summary, content, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (game["id"], category["id"], user["id"], title, summary, content, status)
    )
    article_id = cur.lastrowid
    if source_title and source_url:
        cur.execute("INSERT INTO sources (article_id, title, url) VALUES (?, ?, ?)", (article_id, source_title, source_url))
    conn.commit()
    conn.close()
    return jsonify({"message": "Article submitted successfully", "status": status}), 201


@app.route("/api/articles/mine", methods=["GET"])
def my_articles():
    user = get_current_user()
    if not user:
        return jsonify([]), 200
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT a.id, a.title, a.summary, a.status, c.name AS category, g.title AS game
        FROM articles a
        JOIN categories c ON c.id = a.category_id
        JOIN games g ON g.id = a.game_id
        WHERE a.user_id = ?
        ORDER BY a.created_at DESC, a.id DESC
        """,
        (user["id"],)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200


@app.route("/api/articles/pending", methods=["GET"])
def pending_articles():
    if not require_admin():
        return jsonify({"error": "Admin access required"}), 403
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT a.id, a.title, a.summary, a.status, g.title AS game, g.slug AS game_slug, c.name AS category, u.username AS author
        FROM articles a
        JOIN games g ON g.id = a.game_id
        JOIN categories c ON c.id = a.category_id
        JOIN users u ON u.id = a.user_id
        WHERE a.status = 'pending'
        ORDER BY a.created_at DESC, a.id DESC
        """
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200


@app.route("/api/articles/admin", methods=["GET"])
def admin_articles():
    if not require_admin():
        return jsonify({"error": "Admin access required"}), 403
    status = request.args.get("status", "all").strip().lower()
    where = "" if status == "all" else "WHERE a.status = ?"
    params = () if status == "all" else (status,)
    conn = get_connection()
    rows = conn.execute(
        f"""
        SELECT a.id, a.title, a.summary, a.content, a.status, a.created_at,
               g.title AS game, g.slug AS game_slug, c.name AS category, u.username AS author
        FROM articles a
        JOIN games g ON g.id = a.game_id
        JOIN categories c ON c.id = a.category_id
        JOIN users u ON u.id = a.user_id
        {where}
        ORDER BY a.created_at DESC, a.id DESC
        """,
        params
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200


@app.route("/api/articles/<int:article_id>/approve", methods=["PUT"])
def approve_article(article_id):
    if not require_admin():
        return jsonify({"error": "Admin access required"}), 403
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE articles SET status = 'approved' WHERE id = ?", (article_id,))
    conn.commit()
    affected = cur.rowcount
    conn.close()
    if not affected:
        return jsonify({"error": "Article not found"}), 404
    return jsonify({"message": "Article approved"}), 200


@app.route("/api/articles/<int:article_id>/reject", methods=["PUT"])
def reject_article(article_id):
    if not require_admin():
        return jsonify({"error": "Admin access required"}), 403
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE articles SET status = 'rejected' WHERE id = ?", (article_id,))
    conn.commit()
    affected = cur.rowcount
    conn.close()
    if not affected:
        return jsonify({"error": "Article not found"}), 404
    return jsonify({"message": "Article rejected"}), 200


@app.route("/api/articles/<int:article_id>", methods=["DELETE"])
def delete_article(article_id):
    if not require_admin():
        return jsonify({"error": "Admin access required"}), 403
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM articles WHERE id = ?", (article_id,))
    conn.commit()
    affected = cur.rowcount
    conn.close()
    if not affected:
        return jsonify({"error": "Article not found"}), 404
    return jsonify({"message": "Article deleted"}), 200


@app.route("/api/articles/<int:article_id>", methods=["PUT"])
def update_article(article_id):
    if not require_admin():
        return jsonify({"error": "Admin access required"}), 403
    data = request.get_json() or {}
    title = data.get("title", "").strip()
    summary = data.get("summary", "").strip()
    content = data.get("content", "").strip()
    if not title or not content:
        return jsonify({"error": "Title and content are required"}), 400
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE articles SET title = ?, summary = ?, content = ? WHERE id = ?", (title, summary, content, article_id))
    conn.commit()
    affected = cur.rowcount
    conn.close()
    if not affected:
        return jsonify({"error": "Article not found"}), 404
    return jsonify({"message": "Article updated"}), 200


if __name__ == "__main__":
    app.run(debug=True)
