"""OIBSIP Python Task 2: Advanced BMI Calculator."""
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import datetime

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except ImportError:
    Figure = FigureCanvasTkAgg = None

BASE = Path(__file__).resolve().parent
DB = BASE / 'bmi_records.db'

def connect():
    con = sqlite3.connect(DB, timeout=10)
    con.execute('PRAGMA busy_timeout=10000')
    return con

def init_db():
    with connect() as con:
        con.execute('''CREATE TABLE IF NOT EXISTS bmi_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL, weight REAL NOT NULL CHECK(weight>0),
            height REAL NOT NULL CHECK(height>0), bmi REAL NOT NULL,
            category TEXT NOT NULL, recorded_at TEXT NOT NULL)''')

def classify(bmi):
    if bmi < 18.5: return 'Underweight', '#d97706'
    if bmi < 25: return 'Normal', '#15803d'
    if bmi < 30: return 'Overweight', '#c2410c'
    return 'Obese', '#b91c1c'

def validate(weight_text, height_text):
    try:
        weight, height = float(weight_text.strip()), float(height_text.strip())
    except (ValueError, AttributeError):
        raise ValueError('Weight and height must be numeric values.')
    if weight <= 0: raise ValueError('Weight must be greater than zero kg.')
    if height <= 0: raise ValueError('Height must be greater than zero metres.')
    if weight > 500: raise ValueError('Please enter a realistic weight (500 kg or less).')
    if height > 3: raise ValueError('Enter height in metres, for example 1.75, not centimetres.')
    return weight, height

def save_record(user, weight, height, bmi, category):
    with connect() as con:
        con.execute('INSERT INTO bmi_records(username,weight,height,bmi,category,recorded_at) VALUES(?,?,?,?,?,?)',
                    (user, weight, height, bmi, category, datetime.now().isoformat(timespec='seconds')))

def records_for(user):
    with connect() as con:
        return con.execute('SELECT weight,height,bmi,category,recorded_at FROM bmi_records WHERE username=? ORDER BY recorded_at,id', (user,)).fetchall()

def usernames():
    with connect() as con:
        return [r[0] for r in con.execute('SELECT DISTINCT username FROM bmi_records ORDER BY username COLLATE NOCASE')]

class App:
    def __init__(self, root):
        self.root = root
        root.title('OIBSIP | BMI Calculator')
        root.geometry('880x680'); root.minsize(740, 600); root.configure(bg='#f3f6fb')
        self.user = tk.StringVar(); self.weight = tk.StringVar(); self.height = tk.StringVar()
        self.result = tk.StringVar(value='Enter your details and select Calculate.')
        self.category = tk.StringVar(); self.status = tk.StringVar(value='Ready')
        self.build(); self.refresh_users()

    def build(self):
        style = ttk.Style()
        try: style.theme_use('clam')
        except tk.TclError: pass
        header = tk.Frame(self.root, bg='#17324d', padx=22, pady=15); header.pack(fill='x')
        tk.Label(header, text='BMI CALCULATOR', font=('Segoe UI', 21, 'bold'), fg='white', bg='#17324d').pack(anchor='w')
        tk.Label(header, text='Calculate, save and track BMI over time', fg='#dce8f2', bg='#17324d').pack(anchor='w')
        body = tk.Frame(self.root, bg='#f3f6fb', padx=18, pady=14); body.pack(fill='both', expand=True)
        form = tk.LabelFrame(body, text='Your details', bg='white', padx=12, pady=10); form.pack(fill='x')
        tk.Label(form, text='User name:', bg='white').grid(row=0,column=0,sticky='w',padx=5,pady=5)
        self.userbox = ttk.Combobox(form, textvariable=self.user, width=24); self.userbox.grid(row=0,column=1,sticky='ew',pady=5)
        self.userbox.bind('<<ComboboxSelected>>', lambda e: self.refresh_history())
        tk.Label(form, text='Weight (kg):', bg='white').grid(row=1,column=0,sticky='w',padx=5,pady=5)
        ttk.Entry(form, textvariable=self.weight).grid(row=1,column=1,sticky='ew',pady=5)
        tk.Label(form, text='Height (m):', bg='white').grid(row=2,column=0,sticky='w',padx=5,pady=5)
        ttk.Entry(form, textvariable=self.height).grid(row=2,column=1,sticky='ew',pady=5)
        ttk.Button(form, text='Calculate & Save', command=self.calculate).grid(row=1,column=2,padx=12,sticky='ew')
        ttk.Button(form, text='Refresh History', command=self.refresh_history).grid(row=2,column=2,padx=12,sticky='ew')
        form.columnconfigure(1, weight=1)
        result = tk.Frame(body, bg='white', padx=14, pady=12, highlightbackground='#d9e2ec', highlightthickness=1); result.pack(fill='x',pady=12)
        tk.Label(result,text='YOUR RESULT',bg='white',fg='#526579',font=('Segoe UI',9,'bold')).pack(anchor='w')
        tk.Label(result,textvariable=self.result,bg='white',fg='#17324d',font=('Segoe UI',18,'bold')).pack(anchor='w',pady=3)
        self.catlabel = tk.Label(result,textvariable=self.category,bg='white',font=('Segoe UI',12,'bold')); self.catlabel.pack(anchor='w')
        tk.Label(result,text='BMI is a screening measure, not a diagnosis.',bg='white',fg='#64748b').pack(anchor='w',pady=(6,0))
        hist = tk.LabelFrame(body,text="Selected user's BMI history",bg='white',padx=8,pady=8); hist.pack(fill='both',expand=True)
        cols = ('date','weight','height','bmi','category')
        self.tree = ttk.Treeview(hist,columns=cols,show='headings',height=5)
        for c,title,width in [('date','Date / time',190),('weight','Weight (kg)',100),('height','Height (m)',100),('bmi','BMI',90),('category','Category',130)]:
            self.tree.heading(c,text=title); self.tree.column(c,width=width,anchor='center')
        self.tree.pack(fill='both',expand=True)
        buttons = tk.Frame(body,bg='#f3f6fb'); buttons.pack(fill='x',pady=(9,0))
        ttk.Button(buttons,text='Show BMI Trend Graph',command=self.graph).pack(side='left')
        ttk.Button(buttons,text='Clear Inputs',command=self.clear).pack(side='left',padx=8)
        tk.Label(self.root,textvariable=self.status,anchor='w',bg='#e5edf5',fg='#334155',padx=12,pady=5).pack(fill='x')

    def current_user(self):
        user = self.user.get().strip()
        if not user: raise ValueError('Please enter a user name first.')
        if len(user)>50: raise ValueError('User name must be 50 characters or fewer.')
        return user

    def calculate(self):
        try:
            user = self.current_user(); weight,height = validate(self.weight.get(),self.height.get())
            bmi = weight/(height**2); category,colour = classify(bmi)
            save_record(user,weight,height,bmi,category)
        except ValueError as e:
            messagebox.showerror('Check your input',str(e),parent=self.root); self.status.set('Please correct the input.'); return
        except (sqlite3.Error, OSError) as e:
            messagebox.showerror('Database error',f'Could not save BMI record: {e}',parent=self.root); self.status.set('Database save failed.'); return
        self.result.set(f'BMI: {bmi:.2f}'); self.category.set(category); self.catlabel.configure(fg=colour)
        self.status.set(f'Saved BMI record for {user}.'); self.refresh_users(); self.refresh_history()

    def refresh_users(self):
        try: self.userbox['values'] = usernames()
        except sqlite3.Error as e: messagebox.showerror('Database error',f'Could not read users: {e}',parent=self.root)

    def refresh_history(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        user = self.user.get().strip()
        if not user: return
        try: rows = records_for(user)
        except sqlite3.Error as e:
            messagebox.showerror('Database error',f'Could not read BMI history: {e}',parent=self.root); return
        for w,h,bmi,cat,stamp in rows:
            self.tree.insert('', 'end', values=(stamp.replace('T',' '),f'{w:.2f}',f'{h:.2f}',f'{bmi:.2f}',cat))
        self.status.set(f'Loaded {len(rows)} record(s) for {user}.')

    def graph(self):
        if Figure is None or FigureCanvasTkAgg is None:
            messagebox.showerror('Matplotlib missing','Run: python -m pip install matplotlib',parent=self.root); return
        try: user = self.current_user(); rows = records_for(user)
        except ValueError as e: messagebox.showerror('User name required',str(e),parent=self.root); return
        except sqlite3.Error as e: messagebox.showerror('Database error',f'Could not read BMI history: {e}',parent=self.root); return
        if not rows:
            messagebox.showinfo('No history','Save at least one BMI record for this user first.',parent=self.root); return
        win = tk.Toplevel(self.root); win.title(f'BMI Trend | {user}'); win.geometry('760x470')
        fig = Figure(figsize=(7.2,4.2),dpi=100); ax = fig.add_subplot(111)
        dates = [datetime.fromisoformat(r[4]) for r in rows]; values = [r[2] for r in rows]
        ax.plot(dates,values,marker='o',linewidth=2,label='BMI'); ax.set_title(f'BMI Trend for {user}')
        ax.set_xlabel('Date and time'); ax.set_ylabel('BMI'); ax.grid(True,alpha=.3); ax.legend(); fig.autofmt_xdate(); fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig,master=win); canvas.draw(); canvas.get_tk_widget().pack(fill='both',expand=True)

    def clear(self):
        self.weight.set(''); self.height.set(''); self.result.set('Enter your details and select Calculate.')
        self.category.set(''); self.status.set('Inputs cleared.')

def main():
    try: init_db()
    except (sqlite3.Error, OSError) as e:
        root=tk.Tk(); root.withdraw(); messagebox.showerror('Database error',f'Could not initialize database: {e}'); root.destroy(); return
    root=tk.Tk(); App(root); root.mainloop()

if __name__ == '__main__': main()
