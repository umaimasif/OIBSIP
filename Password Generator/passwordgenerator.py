import tkinter as tk
from tkinter import ttk, messagebox
import secrets
import string

class AdvancedPasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Password Generator")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        
        self.length_var = tk.IntVar(value=16)
        self.use_upper = tk.BooleanVar(value=True)
        self.use_lower = tk.BooleanVar(value=True)
        self.use_numbers = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        self.exclude_var = tk.StringVar(value="")
        self.generated_password = tk.StringVar(value="")
        
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        display_frame = ttk.Frame(main_frame)
        display_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Entry(display_frame, textvariable=self.generated_password, font=("Courier", 14), state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(display_frame, text="Copy", command=self.copy_to_clipboard).pack(side=tk.RIGHT)

        length_frame = ttk.Frame(main_frame)
        length_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(length_frame, text="Password Length:").pack(side=tk.LEFT)
        ttk.Label(length_frame, textvariable=self.length_var).pack(side=tk.RIGHT)
        ttk.Scale(main_frame, from_=8, to_=64, variable=self.length_var, orient=tk.HORIZONTAL, command=self.update_length_label).pack(fill=tk.X, pady=(0, 20))

        options_frame = ttk.LabelFrame(main_frame, text="Character Types", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Checkbutton(options_frame, text="Uppercase (A-Z)", variable=self.use_upper).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Lowercase (a-z)", variable=self.use_lower).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Numbers (0-9)", variable=self.use_numbers).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Symbols (!@#$)", variable=self.use_symbols).pack(anchor=tk.W, pady=2)

        exclude_frame = ttk.Frame(main_frame)
        exclude_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(exclude_frame, text="Exclude Characters (e.g., l1O0):").pack(side=tk.LEFT)
        ttk.Entry(exclude_frame, textvariable=self.exclude_var, width=15).pack(side=tk.RIGHT)

        ttk.Button(main_frame, text="Generate Secure Password", command=self.generate_password).pack(fill=tk.X, pady=10)

    def update_length_label(self, event):
        self.length_var.set(int(float(self.length_var.get())))

    def generate_password(self):
        length = self.length_var.get()
        exclude_chars = set(self.exclude_var.get())

        upper_pool = [c for c in string.ascii_uppercase if c not in exclude_chars]
        lower_pool = [c for c in string.ascii_lowercase if c not in exclude_chars]
        number_pool = [c for c in string.digits if c not in exclude_chars]
        symbol_pool = [c for c in string.punctuation if c not in exclude_chars]

        pools = []
        required_chars = []

        if self.use_upper.get() and upper_pool:
            pools.extend(upper_pool)
            required_chars.append(secrets.choice(upper_pool))
        if self.use_lower.get() and lower_pool:
            pools.extend(lower_pool)
            required_chars.append(secrets.choice(lower_pool))
        if self.use_numbers.get() and number_pool:
            pools.extend(number_pool)
            required_chars.append(secrets.choice(number_pool))
        if self.use_symbols.get() and symbol_pool:
            pools.extend(symbol_pool)
            required_chars.append(secrets.choice(symbol_pool))

        if not pools:
            messagebox.showerror("Error", "Please select at least one character type that isn't completely excluded.")
            return

        if length < len(required_chars):
            messagebox.showerror("Error", "Password length is too short to include all selected character types.")
            return

        remaining_length = length - len(required_chars)
        random_chars = [secrets.choice(pools) for _ in range(remaining_length)]

        full_password_list = required_chars + random_chars
        
        secrets.SystemRandom().shuffle(full_password_list)
        
        final_password = "".join(full_password_list)
        self.generated_password.set(final_password)

    def copy_to_clipboard(self):
        password = self.generated_password.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            self.root.update()
            messagebox.showinfo("Success", "Password copied to clipboard!")
        else:
            messagebox.showwarning("Warning", "No password generated yet to copy.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedPasswordGenerator(root)
    root.mainloop()
