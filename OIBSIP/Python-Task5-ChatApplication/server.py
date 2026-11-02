import hashlib
import hmac
import json
import os
import socket
import sqlite3
import threading
from datetime import datetime

HOST = "127.0.0.1"
PORT = 5050
DB = "chat.db"

clients = {}
clients_lock = threading.Lock()
db_lock = threading.Lock()


def ts():
    return datetime.now().strftime("%H:%M")


def db():
    conn = sqlite3.connect(DB, timeout=10)
    conn.execute("PRAGMA busy_timeout=10000")
    return conn


def init_db():
    with db_lock:
        conn = db()
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    salt TEXT NOT NULL,
                    password_hash TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS rooms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room TEXT NOT NULL,
                    username TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            conn.execute(
                "INSERT OR IGNORE INTO rooms(name) VALUES(?)",
                ("General",),
            )
            conn.commit()
        finally:
            conn.close()


def hash_password(password):
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 120_000
    )
    return salt.hex(), digest.hex()


def verify_password(password, salt_hex, digest_hex):
    try:
        salt = bytes.fromhex(salt_hex)
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, 120_000
        ).hex()
        return hmac.compare_digest(digest, digest_hex)
    except (ValueError, TypeError):
        return False


def register(username, password):
    username = username.strip()

    if len(username) < 3 or len(username) > 30:
        return False, "Username must be 3-30 characters."
    if any(ch.isspace() for ch in username):
        return False, "Username cannot contain spaces."
    if len(password) < 8 or not any(ch.isdigit() for ch in password):
        return False, "Password must be 8+ characters and contain a number."

    salt, digest = hash_password(password)

    with db_lock:
        conn = db()
        try:
            conn.execute(
                "INSERT INTO users(username, salt, password_hash) VALUES(?,?,?)",
                (username, salt, digest),
            )
            conn.commit()
            return True, "Registration successful. You can now log in."
        except sqlite3.IntegrityError:
            return False, "Username already exists."
        finally:
            conn.close()


def authenticate(username, password):
    with db_lock:
        conn = db()
        try:
            row = conn.execute(
                "SELECT salt, password_hash FROM users WHERE username=?",
                (username,),
            ).fetchone()
        finally:
            conn.close()

    return bool(row and verify_password(password, row[0], row[1]))


def get_rooms():
    with db_lock:
        conn = db()
        try:
            rows = conn.execute(
                "SELECT name FROM rooms ORDER BY name COLLATE NOCASE"
            ).fetchall()
            return [row[0] for row in rows]
        finally:
            conn.close()


def get_history(room, limit=50):
    with db_lock:
        conn = db()
        try:
            rows = conn.execute(
                """
                SELECT username, message, created_at
                FROM messages
                WHERE room=?
                ORDER BY id DESC
                LIMIT ?
                """,
                (room, limit),
            ).fetchall()
        finally:
            conn.close()

    return [
        {"username": row[0], "message": row[1], "time": row[2][11:16]}
        for row in reversed(rows)
    ]


def save_message(room, username, message):
    with db_lock:
        conn = db()
        try:
            conn.execute(
                """
                INSERT INTO messages(room, username, message, created_at)
                VALUES(?,?,?,?)
                """,
                (room, username, message, datetime.now().isoformat(timespec="seconds")),
            )
            conn.commit()
        finally:
            conn.close()


def create_room(room):
    room = room.strip()
    if not room:
        return False, "Room name cannot be empty."
    if len(room) > 40:
        return False, "Room name must be 40 characters or fewer."

    with db_lock:
        conn = db()
        try:
            conn.execute("INSERT INTO rooms(name) VALUES(?)", (room,))
            conn.commit()
            return True, "Room created."
        except sqlite3.IntegrityError:
            return False, "Room already exists."
        finally:
            conn.close()


def send_json(conn, payload):
    data = (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8")
    with clients_lock:
        info = clients.get(conn)
        send_lock = info["send_lock"] if info else None

    if send_lock:
        with send_lock:
            conn.sendall(data)
    else:
        conn.sendall(data)


def broadcast(room, payload, exclude=None):
    with clients_lock:
        targets = [
            (conn, info["send_lock"])
            for conn, info in clients.items()
            if info["room"] == room and conn != exclude
        ]

    data = (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8")
    for conn, send_lock in targets:
        try:
            with send_lock:
                conn.sendall(data)
        except OSError:
            remove_client(conn)


def remove_client(conn):
    with clients_lock:
        clients.pop(conn, None)


def handle(conn, address):
    username = None
    room = "General"
    reader = None

    with clients_lock:
        clients[conn] = {
            "username": None,
            "room": room,
            "send_lock": threading.Lock(),
        }

    try:
        reader = conn.makefile("r", encoding="utf-8")

        for line in reader:
            if not line:
                break

            try:
                request = json.loads(line)
            except json.JSONDecodeError:
                send_json(conn, {"type": "response", "ok": False, "message": "Invalid request format."})
                continue

            action = request.get("action")

            if username is None:
                if action == "register":
                    ok, message = register(
                        request.get("username", ""),
                        request.get("password", ""),
                    )
                    send_json(conn, {"type": "response", "ok": ok, "message": message})

                elif action == "login":
                    candidate = request.get("username", "").strip()
                    password = request.get("password", "")

                    if authenticate(candidate, password):
                        username = candidate
                        with clients_lock:
                            clients[conn]["username"] = username

                        send_json(
                            conn,
                            {
                                "type": "login_ok",
                                "username": username,
                                "room": room,
                                "rooms": get_rooms(),
                                "history": get_history(room),
                            },
                        )
                    else:
                        send_json(
                            conn,
                            {"type": "response", "ok": False, "message": "Invalid username or password."},
                        )
                else:
                    send_json(
                        conn,
                        {"type": "response", "ok": False, "message": "Please register or log in first."},
                    )
                continue

            if action == "message":
                message = request.get("message", "").strip()
                if not message:
                    continue
                if len(message) > 1000:
                    send_json(
                        conn,
                        {"type": "response", "ok": False, "message": "Message must be 1000 characters or fewer."},
                    )
                    continue

                save_message(room, username, message)
                broadcast(
                    room,
                    {
                        "type": "message",
                        "room": room,
                        "username": username,
                        "message": message,
                        "time": ts(),
                    },
                )

            elif action == "join":
                new_room = request.get("room", "").strip()
                if new_room not in get_rooms():
                    send_json(
                        conn,
                        {"type": "response", "ok": False, "message": "Room does not exist."},
                    )
                    continue

                old_room = room
                room = new_room
                with clients_lock:
                    if conn in clients:
                        clients[conn]["room"] = room

                send_json(
                    conn,
                    {"type": "joined", "room": room, "history": get_history(room)},
                )

                if old_room != room:
                    broadcast(
                        old_room,
                        {"type": "system", "room": old_room, "message": f"{username} left {old_room}.", "time": ts()},
                        exclude=conn,
                    )
                    broadcast(
                        room,
                        {"type": "system", "room": room, "message": f"{username} joined {room}.", "time": ts()},
                        exclude=conn,
                    )

            elif action == "create_room":
                ok, message = create_room(request.get("room", ""))
                send_json(
                    conn,
                    {
                        "type": "room_created",
                        "ok": ok,
                        "message": message,
                        "rooms": get_rooms() if ok else None,
                    },
                )

            elif action == "rooms":
                send_json(conn, {"type": "rooms", "rooms": get_rooms()})

            else:
                send_json(conn, {"type": "response", "ok": False, "message": "Unknown action."})

    except (ConnectionResetError, BrokenPipeError, OSError):
        pass
    finally:
        remove_client(conn)

        if username:
            broadcast(
                room,
                {"type": "system", "room": room, "message": f"{username} disconnected.", "time": ts()},
                exclude=conn,
            )

        try:
            if reader:
                reader.close()
        except OSError:
            pass
        try:
            conn.close()
        except OSError:
            pass


def main():
    init_db()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()

    print(f"Chat server listening on {HOST}:{PORT}")
    print("Press Ctrl+C to stop the server.")

    try:
        while True:
            conn, address = server.accept()
            threading.Thread(target=handle, args=(conn, address), daemon=True).start()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.close()


if __name__ == "__main__":
    main()
