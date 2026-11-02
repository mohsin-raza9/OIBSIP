import json
import socket
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

HOST = "127.0.0.1"
PORT = 5050

EMOJI_MAP = {
    ":smile:": "😄",
    ":heart:": "❤️",
    ":thumbsup:": "👍",
    ":laugh:": "😂",
    ":fire:": "🔥",
    ":rocket:": "🚀",
    ":sad:": "😢",
    ":wave:": "👋",
    ":check:": "✅",
}


def render_shortcodes(text):
    for shortcode, emoji in EMOJI_MAP.items():
        text = text.replace(shortcode, emoji)
    return text


class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("OIBSIP Chat Application")
        self.root.geometry("900x620")
        self.root.minsize(760, 520)

        self.sock = None
        self.reader = None
        self.connected = False
        self.username = None
        self.room = None
        self.rooms = []

        self.show_login()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def connect(self):
        if self.sock:
            return True

        try:
            self.sock = socket.create_connection((HOST, PORT), timeout=5)
            self.sock.settimeout(None)
            self.reader = self.sock.makefile("r", encoding="utf-8")
            self.connected = True
            threading.Thread(target=self.receive_loop, daemon=True).start()
            return True
        except OSError as exc:
            self.sock = None
            messagebox.showerror("Connection Error", f"Could not connect to the server.\n\n{exc}")
            return False

    def send(self, payload):
        if not self.sock or not self.connected:
            return
        try:
            data = (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8")
            self.sock.sendall(data)
        except OSError:
            self.handle_disconnect()

    def show_login(self):
        self.clear_window()

        frame = ttk.Frame(self.root, padding=30)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(frame, text="OIBSIP Chat Application", font=("Segoe UI", 22, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 8)
        )
        ttk.Label(frame, text="Python Programming • Task 5", font=("Segoe UI", 11)).grid(
            row=1, column=0, columnspan=2, pady=(0, 24)
        )

        ttk.Label(frame, text="Username").grid(row=2, column=0, sticky="w", pady=6)
        self.username_entry = ttk.Entry(frame, width=32)
        self.username_entry.grid(row=2, column=1, pady=6)

        ttk.Label(frame, text="Password").grid(row=3, column=0, sticky="w", pady=6)
        self.password_entry = ttk.Entry(frame, width=32, show="•")
        self.password_entry.grid(row=3, column=1, pady=6)

        ttk.Button(frame, text="Login", command=self.login).grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(18, 6)
        )
        ttk.Button(frame, text="Register", command=self.register).grid(
            row=5, column=0, columnspan=2, sticky="ew"
        )

        ttk.Label(frame, text="Local demo server: 127.0.0.1:5050", foreground="#666666").grid(
            row=6, column=0, columnspan=2, pady=(18, 0)
        )

    def credentials(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showwarning("Missing Details", "Enter both username and password.")
            return None
        return username, password

    def register(self):
        credentials = self.credentials()
        if credentials and self.connect():
            self.send({"action": "register", "username": credentials[0], "password": credentials[1]})

    def login(self):
        credentials = self.credentials()
        if credentials and self.connect():
            self.send({"action": "login", "username": credentials[0], "password": credentials[1]})

    def build_chat_ui(self):
        self.clear_window()

        top = ttk.Frame(self.root, padding=(12, 10))
        top.pack(fill="x")

        ttk.Label(top, text=f"Logged in as: {self.username}", font=("Segoe UI", 11, "bold")).pack(side="left")
        self.room_label = ttk.Label(top, text=f"Room: {self.room}")
        self.room_label.pack(side="left", padx=20)

        ttk.Button(top, text="Refresh Rooms", command=self.refresh_rooms).pack(side="right")
        ttk.Button(top, text="Create Room", command=self.create_room).pack(side="right", padx=6)
        ttk.Button(top, text="Logout", command=self.logout).pack(side="right")

        main = ttk.Frame(self.root, padding=(12, 0, 12, 12))
        main.pack(fill="both", expand=True)

        room_frame = ttk.LabelFrame(main, text="Chat Rooms", padding=8)
        room_frame.pack(side="left", fill="y", padx=(0, 10))

        self.room_list = tk.Listbox(room_frame, width=20, exportselection=False)
        self.room_list.pack(fill="y", expand=True)
        self.room_list.bind("<<ListboxSelect>>", self.join_selected_room)

        chat_frame = ttk.Frame(main)
        chat_frame.pack(side="left", fill="both", expand=True)

        self.chat_text = tk.Text(chat_frame, wrap="word", state="disabled", font=("Segoe UI", 11))
        self.chat_text.pack(fill="both", expand=True)

        bottom = ttk.Frame(chat_frame, padding=(0, 10, 0, 0))
        bottom.pack(fill="x")

        self.message_entry = ttk.Entry(bottom)
        self.message_entry.pack(side="left", fill="x", expand=True)
        self.message_entry.bind("<Return>", lambda _event: self.send_message())
        ttk.Button(bottom, text="Send", command=self.send_message).pack(side="left", padx=(8, 0))

        ttk.Label(
            self.root,
            text="Emoji: :smile:  :heart:  :thumbsup:  :fire:  :rocket:",
            foreground="#666666",
            padding=(12, 0, 12, 8),
        ).pack(fill="x")

        self.populate_rooms()
        self.render_history([])
        self.root.focus_force()

    def populate_rooms(self):
        if not hasattr(self, "room_list"):
            return
        self.room_list.delete(0, tk.END)
        for room in self.rooms:
            self.room_list.insert(tk.END, room)
        if self.room in self.rooms:
            index = self.rooms.index(self.room)
            self.room_list.selection_set(index)
            self.room_list.see(index)

    def render_history(self, history):
        def update():
            if not hasattr(self, "chat_text"):
                return
            self.chat_text.config(state="normal")
            self.chat_text.delete("1.0", tk.END)
            for item in history:
                self.chat_text.insert(
                    tk.END,
                    f'[{item["time"]}] {item["username"]}: {render_shortcodes(item["message"])}\n',
                )
            self.chat_text.see(tk.END)
            self.chat_text.config(state="disabled")
        self.root.after(0, update)

    def append_message(self, line, notify=False):
        def update():
            if not hasattr(self, "chat_text"):
                return
            self.chat_text.config(state="normal")
            self.chat_text.insert(tk.END, line + "\n")
            self.chat_text.see(tk.END)
            self.chat_text.config(state="disabled")
            if notify:
                self.notify_new_message()
        self.root.after(0, update)

    def notify_new_message(self):
        try:
            unfocused = self.root.focus_displayof() is None or self.root.state() != "normal"
            if unfocused:
                self.root.title("🔔 New Message • OIBSIP Chat")
                self.root.bell()
        except tk.TclError:
            pass

    def clear_notification(self, _event=None):
        if self.room:
            self.root.title(f"OIBSIP Chat Application • {self.room}")

    def send_message(self):
        message = self.message_entry.get().strip()
        if not message:
            return
        self.send({"action": "message", "message": message})
        self.message_entry.delete(0, tk.END)

    def join_selected_room(self, _event=None):
        selection = self.room_list.curselection()
        if selection:
            self.send({"action": "join", "room": self.room_list.get(selection[0])})

    def create_room(self):
        room = simpledialog.askstring("Create Room", "Enter a room name:", parent=self.root)
        if room:
            self.send({"action": "create_room", "room": room.strip()})

    def refresh_rooms(self):
        self.send({"action": "rooms"})

    def logout(self):
        self.connected = False
        try:
            if self.sock:
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
        except OSError:
            pass
        self.sock = None
        self.reader = None
        self.username = None
        self.room = None
        self.rooms = []
        self.show_login()

    def handle_disconnect(self):
        if not self.connected:
            return
        self.connected = False
        self.sock = None
        self.root.after(
            0,
            lambda: messagebox.showwarning("Disconnected", "The chat server connection was closed."),
        )

    def receive_loop(self):
        try:
            for line in self.reader:
                if not line:
                    break
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue

                message_type = data.get("type")

                if message_type == "response":
                    if data.get("ok"):
                        self.root.after(0, lambda m=data.get("message", ""): messagebox.showinfo("Chat", m))
                    else:
                        self.root.after(0, lambda m=data.get("message", "Request failed."): messagebox.showwarning("Chat", m))

                elif message_type == "login_ok":
                    self.root.after(0, self.finish_login, data)

                elif message_type == "joined":
                    self.root.after(0, self.finish_join_room, data)

                elif message_type == "room_created":
                    self.root.after(0, self.handle_room_created, data)

                elif message_type == "rooms":
                    self.root.after(0, self.update_rooms, data.get("rooms", []))

                elif message_type == "message":
                    # Only display a live message if it belongs to the room currently open.
                    if data.get("room") != self.room:
                        continue
                    message = render_shortcodes(data.get("message", ""))
                    self.append_message(
                        f'[{data.get("time", "--:--")}] {data.get("username", "Unknown")}: {message}',
                        notify=data.get("username") != self.username,
                    )

                elif message_type == "system":
                    # System events are also limited to their own room.
                    if data.get("room") != self.room:
                        continue
                    self.append_message(
                        f'[{data.get("time", "--:--")}] • {data.get("message", "")}'
                    )
        except (OSError, ValueError):
            pass
        finally:
            self.handle_disconnect()

    def finish_login(self, data):
        self.username = data["username"]
        self.room = data["room"]
        self.rooms = data.get("rooms", [])
        self.build_chat_ui()
        self.render_history(data.get("history", []))

    def finish_join_room(self, data):
        self.room = data["room"]
        self.room_label.config(text=f"Room: {self.room}")
        self.populate_rooms()
        self.render_history(data.get("history", []))
        self.clear_notification()

    def handle_room_created(self, data):
        if data.get("ok"):
            self.rooms = data.get("rooms", self.rooms)
            self.populate_rooms()
            messagebox.showinfo("Room Created", data.get("message", "Room created."))
        else:
            messagebox.showwarning("Room", data.get("message", "Could not create room."))

    def update_rooms(self, rooms):
        self.rooms = rooms
        self.populate_rooms()

    def start(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.bind("<FocusIn>", self.clear_notification)
        self.root.mainloop()

    def on_close(self):
        self.connected = False
        try:
            if self.sock:
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
        except OSError:
            pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    app.start()
