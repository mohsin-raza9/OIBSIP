# OIBSIP Python Task 5 - Advanced Chat Application

A local real-time Python chat application built for the Oasis Infobyte Python Programming Task 5.

## Advanced requirements covered

- Tkinter GUI chat application
- Client/server communication using Python sockets
- Multiple chat rooms with create/join support
- Strict room-isolated message storage and history in SQLite
- Message history loaded when joining a room
- Registration and login with SQLite user storage
- Password hashing using PBKDF2-HMAC-SHA256 with per-user salt
- Timestamped messages
- Graceful disconnection handling
- Desktop/in-app notification when a new message arrives while the window is unfocused
- Emoji shortcode rendering such as `:smile:` and `:heart:`
- README documentation of SQLite storage and encryption limitations

## Important room-isolation behavior

Each message is saved with its room name. When a room is opened, the server returns only messages whose `room` matches that room. Live messages also include their room, and the client ignores live events belonging to another room. This prevents messages from one room from appearing in another room.

## Run

1. Open Command Prompt in this folder.
2. Start the server:

```bash
python server.py
```

3. Open two more Command Prompt windows in the same folder.
4. Run the client in both:

```bash
python client.py
```

## Clean test database

For a fresh demonstration, stop the server and delete `chat.db` once. Start the server again. The application will recreate the database and the `General` room automatically.

## Test room isolation

1. Create `python` and `fyp` rooms.
2. Join `python` and send `PYTHON_ONLY`.
3. Join `fyp` and send `FYP_ONLY`.
4. Return to `General` and send `GENERAL_ONLY`.
5. Open each room again.
6. Verify that each room displays only its own messages.

## Data storage and encryption

User accounts, room names, and chat messages are stored in SQLite (`chat.db`). Passwords are not stored as plain text; they are protected with PBKDF2-HMAC-SHA256 and a random salt. Chat messages are stored as application data in SQLite and are not end-to-end encrypted. This project is intended for local demonstration use on `127.0.0.1`.
