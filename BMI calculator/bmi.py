import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class BMIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BMI Calculator & Tracker")
        self.root.geometry("800x600")
        
        self.conn = sqlite3.connect('bmi_data.db')
        self.cursor = self.conn.cursor()
        self.setup_db()
        
        self.setup_gui()
        self.load_users()

    def setup_db(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY, user_id INTEGER, date TEXT, weight REAL, height REAL, bmi REAL, category TEXT, FOREIGN KEY(user_id) REFERENCES users(id))")
        self.conn.commit()

    def setup_gui(self):
        left_frame = tk.Frame(self.root, padx=20, pady=20)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        tk.Label(left_frame, text="User Management", font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        self.user_var = tk.StringVar()
        self.user_combo = ttk.Combobox(left_frame, textvariable=self.user_var, state="readonly")
        self.user_combo.pack(fill=tk.X, pady=5)
        self.user_combo.bind("<<ComboboxSelected>>", self.on_user_select)
        
        self.new_user_entry = tk.Entry(left_frame)
        self.new_user_entry.pack(fill=tk.X, pady=5)
        tk.Button(left_frame, text="Add New User", command=self.add_user).pack(fill=tk.X, pady=5)
        
        tk.Label(left_frame, text="Calculate BMI", font=("Arial", 14, "bold")).pack(pady=(30, 10))
        
        tk.Label(left_frame, text="Weight (kg):").pack(anchor=tk.W)
        self.weight_entry = tk.Entry(left_frame)
        self.weight_entry.pack(fill=tk.X, pady=5)
        
        tk.Label(left_frame, text="Height (cm):").pack(anchor=tk.W)
        self.height_entry = tk.Entry(left_frame)
        self.height_entry.pack(fill=tk.X, pady=5)
        
        tk.Button(left_frame, text="Calculate & Save", command=self.calculate_bmi, bg="lightblue").pack(fill=tk.X, pady=15)
        
        self.result_label = tk.Label(left_frame, text="", font=("Arial", 12))
        self.result_label.pack(pady=10)
        
        self.right_frame = tk.Frame(self.root, padx=20, pady=20)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(self.right_frame, text="BMI Trend Analysis", font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def load_users(self):
        self.cursor.execute("SELECT name FROM users")
        users = [row[0] for row in self.cursor.fetchall()]
        self.user_combo['values'] = users
        if users:
            self.user_combo.set(users[0])
            self.update_graph()

    def add_user(self):
        name = self.new_user_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "User name cannot be empty.")
            return
        try:
            self.cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
            self.conn.commit()
            self.new_user_entry.delete(0, tk.END)
            self.load_users()
            self.user_combo.set(name)
            self.update_graph()
            messagebox.showinfo("Success", "User added successfully.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "User already exists.")

    def on_user_select(self, event):
        self.update_graph()

    def get_category(self, bmi):
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 24.9:
            return "Normal weight"
        elif 25 <= bmi < 29.9:
            return "Overweight"
        else:
            return "Obese"

    def calculate_bmi(self):
        user_name = self.user_var.get()
        if not user_name:
            messagebox.showerror("Error", "Please select or create a user first.")
            return
            
        try:
            weight = float(self.weight_entry.get())
            height_cm = float(self.height_entry.get())
            
            if weight <= 0 or height_cm <= 0:
                raise ValueError
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid positive numbers for weight and height.")
            return

        height_m = height_cm / 100
        bmi = weight / (height_m ** 2)
        category = self.get_category(bmi)
        
        self.result_label.config(text=f"BMI: {bmi:.2f}\nCategory: {category}")
        
        self.cursor.execute("SELECT id FROM users WHERE name=?", (user_name,))
        user_id = self.cursor.fetchone()[0]
        
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO records (user_id, date, weight, height, bmi, category) VALUES (?, ?, ?, ?, ?, ?)",
                            (user_id, date_str, weight, height_cm, bmi, category))
        self.conn.commit()
        
        self.update_graph()

    def update_graph(self):
        user_name = self.user_var.get()
        if not user_name:
            return
            
        self.cursor.execute("SELECT id FROM users WHERE name=?", (user_name,))
        user_row = self.cursor.fetchone()
        if not user_row:
            return
            
        user_id = user_row[0]
        self.cursor.execute("SELECT date, bmi FROM records WHERE user_id=? ORDER BY date", (user_id,))
        records = self.cursor.fetchall()
        
        self.ax.clear()
        
        if records:
            dates = [datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S").strftime("%m-%d") for r in records]
            bmis = [r[1] for r in records]
            
            self.ax.plot(dates, bmis, marker='o', linestyle='-', color='b')
            self.ax.set_title(f"BMI History for {user_name}")
            self.ax.set_xlabel("Date")
            self.ax.set_ylabel("BMI")
            self.ax.axhline(y=18.5, color='r', linestyle='--', alpha=0.5)
            self.ax.axhline(y=24.9, color='g', linestyle='--', alpha=0.5)
            self.ax.axhline(y=29.9, color='orange', linestyle='--', alpha=0.5)
            self.ax.tick_params(axis='x', rotation=45)
            self.fig.tight_layout()
        else:
            self.ax.text(0.5, 0.5, "No data available", ha='center', va='center')
            self.ax.set_title(f"BMI History for {user_name}")
            
        self.canvas.draw()

    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = BMIApp(root)
    root.mainloop()
