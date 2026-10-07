import secrets
import string
import tkinter as tk
from tkinter import ttk, messagebox


AMBIGUOUS = "0Ol1I|"


class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Password Generator")
        self.root.geometry("720x650")
        self.root.minsize(650, 580)

        self.history = []

        self.length_var = tk.IntVar(value=16)
        self.upper_var = tk.BooleanVar(value=True)
        self.lower_var = tk.BooleanVar(value=True)
        self.number_var = tk.BooleanVar(value=True)
        self.symbol_var = tk.BooleanVar(value=True)
        self.ambiguous_var = tk.BooleanVar(value=False)
        self.password_var = tk.StringVar(value="Your password will appear here")
        self.strength_var = tk.StringVar(value="Strength: -")

        self.build_ui()

    def build_ui(self):
        main = ttk.Frame(self.root, padding=24)
        main.pack(fill="both", expand=True)

        ttk.Label(
            main,
            text="Secure Password Generator",
            font=("Segoe UI", 22, "bold")
        ).pack(anchor="w")

        ttk.Label(
            main,
            text="Generate strong passwords using Python's cryptographically secure secrets module.",
            wraplength=650
        ).pack(anchor="w", pady=(4, 20))

        length_frame = ttk.LabelFrame(main, text="Password Length", padding=12)
        length_frame.pack(fill="x", pady=6)

        ttk.Label(length_frame, textvariable=self.length_var).pack(side="right")
        ttk.Scale(
            length_frame,
            from_=8,
            to=64,
            variable=self.length_var,
            command=self.update_length
        ).pack(fill="x")

        types_frame = ttk.LabelFrame(main, text="Character Types", padding=12)
        types_frame.pack(fill="x", pady=6)

        ttk.Checkbutton(types_frame, text="Uppercase (A-Z)", variable=self.upper_var).pack(anchor="w")
        ttk.Checkbutton(types_frame, text="Lowercase (a-z)", variable=self.lower_var).pack(anchor="w")
        ttk.Checkbutton(types_frame, text="Numbers (0-9)", variable=self.number_var).pack(anchor="w")
        ttk.Checkbutton(types_frame, text="Symbols (!@#$...)", variable=self.symbol_var).pack(anchor="w")

        ttk.Checkbutton(
            types_frame,
            text="Exclude ambiguous characters (0, O, l, 1, I, |)",
            variable=self.ambiguous_var
        ).pack(anchor="w", pady=(8, 0))

        result_frame = ttk.LabelFrame(main, text="Generated Password", padding=12)
        result_frame.pack(fill="x", pady=12)

        password_entry = ttk.Entry(
            result_frame,
            textvariable=self.password_var,
            font=("Consolas", 15),
            justify="center"
        )
        password_entry.pack(fill="x", ipady=8)

        self.strength_label = ttk.Label(
            result_frame,
            textvariable=self.strength_var,
            font=("Segoe UI", 11, "bold")
        )
        self.strength_label.pack(pady=8)

        buttons = ttk.Frame(main)
        buttons.pack(fill="x", pady=4)

        ttk.Button(
            buttons,
            text="Generate Password",
            command=self.generate_password
        ).pack(side="left", expand=True, fill="x", padx=(0, 5))

        ttk.Button(
            buttons,
            text="Copy to Clipboard",
            command=self.copy_password
        ).pack(side="left", expand=True, fill="x", padx=5)

        ttk.Button(
            buttons,
            text="Generate Again",
            command=self.generate_password
        ).pack(side="left", expand=True, fill="x", padx=(5, 0))

        history_frame = ttk.LabelFrame(main, text="Session History (Last 5)", padding=12)
        history_frame.pack(fill="both", expand=True, pady=12)

        self.history_list = tk.Listbox(history_frame, height=6, font=("Consolas", 11))
        self.history_list.pack(fill="both", expand=True)

        ttk.Label(
            main,
            text="Passwords are kept only in this session and are never saved to a file.",
            foreground="gray"
        ).pack(anchor="w")

    def update_length(self, value):
        self.length_var.set(int(float(value)))

    def selected_types(self):
        selected = []
        if self.upper_var.get():
            selected.append(string.ascii_uppercase)
        if self.lower_var.get():
            selected.append(string.ascii_lowercase)
        if self.number_var.get():
            selected.append(string.digits)
        if self.symbol_var.get():
            selected.append(string.punctuation)
        return selected

    def clean_ambiguous(self, characters):
        if not self.ambiguous_var.get():
            return characters
        return "".join(char for char in characters if char not in AMBIGUOUS)

    def generate_password(self):
        length = self.length_var.get()
        selected = self.selected_types()

        if length < 8:
            messagebox.showerror(
                "Invalid Length",
                "Password length must be at least 8 characters."
            )
            return

        if len(selected) < 2:
            messagebox.showerror(
                "Invalid Character Selection",
                "Please select at least two character types."
            )
            return

        pools = [self.clean_ambiguous(pool) for pool in selected]
        pools = [pool for pool in pools if pool]

        if len(pools) < 2:
            messagebox.showerror(
                "Invalid Selection",
                "The selected character types do not contain enough usable characters."
            )
            return

        all_characters = "".join(pools)

        
        password_chars = [secrets.choice(pool) for pool in pools]

        while len(password_chars) < length:
            password_chars.append(secrets.choice(all_characters))

        
        for i in range(len(password_chars) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            password_chars[i], password_chars[j] = password_chars[j], password_chars[i]

        password = "".join(password_chars)

        self.password_var.set(password)
        self.update_strength(password, len(pools))
        self.add_to_history(password)

        
        self.copy_password(silent=True)

    def update_strength(self, password, diversity):
        length = len(password)

        if length >= 16 and diversity >= 4:
            strength = "Strong"
        elif length >= 12 and diversity >= 3:
            strength = "Medium"
        else:
            strength = "Weak"

        self.strength_var.set(f"Strength: {strength}")

    def copy_password(self, silent=False):
        password = self.password_var.get()

        if not password or password == "Your password will appear here":
            if not silent:
                messagebox.showwarning("Nothing to Copy", "Generate a password first.")
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(password)
        self.root.update()

        if not silent:
            messagebox.showinfo("Copied", "Password copied to clipboard.")

    def add_to_history(self, password):
        self.history.insert(0, password)
        self.history = self.history[:5]

        self.history_list.delete(0, tk.END)
        for item in self.history:
            self.history_list.insert(tk.END, item)


def main():
    root = tk.Tk()
    PasswordGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
