import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime

# Kết nối SQLite
conn = sqlite3.connect("gold_shop.db")
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        item TEXT,
        type TEXT,
        quantity REAL,
        unit_price REAL
    )
''')
conn.commit()

# Hàm thêm giao dịch
def add_transaction():
    date = date_entry.get()
    item = item_entry.get().upper()
    ttype = type_var.get()
    try:
        quantity = float(quantity_entry.get())
        unit_price = float(price_entry.get())
    except ValueError:
        messagebox.showerror("Lỗi", "Số lượng và đơn giá phải là số.")
        return

    cursor.execute('''
        INSERT INTO transactions (date, item, type, quantity, unit_price)
        VALUES (?, ?, ?, ?, ?)
    ''', (date, item, ttype, quantity, unit_price))
    conn.commit()
    refresh_summary()

# Làm mới bảng và tính lời lỗ
def refresh_summary():
    for row in tree.get_children():
        tree.delete(row)

    selected_date = date_entry.get()
    cursor.execute('''
        SELECT item,
            SUM(CASE WHEN type = 'buy' THEN quantity * unit_price ELSE 0 END) as total_buy,
            SUM(CASE WHEN type = 'sell' THEN quantity * unit_price ELSE 0 END) as total_sell
        FROM transactions
        WHERE date = ?
        GROUP BY item
    ''', (selected_date,))
    data = cursor.fetchall()

    total_buy = 0
    total_sell = 0

    for item, buy, sell in data:
        profit = sell - buy
        tree.insert("", "end", values=(item, f"{buy:,.0f}", f"{sell:,.0f}", f"{profit:,.0f}"))
        total_buy += buy
        total_sell += sell

    total_profit = total_sell - total_buy
    profit_label.config(text=f"Lãi/Lỗ ngày {selected_date}: {total_profit:,.0f} đ")

# Giao diện chính
root = tk.Tk()
root.title("Quản lý tiệm vàng")
root.geometry("1080x500")
style = ttk.Style()
style.theme_use("default")
style.configure("TLabel", font=("Segoe UI", 11))
style.configure("TButton", font=("Segoe UI", 11))
style.configure("Treeview", font=("Segoe UI", 10), rowheight=28)
style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))

# Frame nhập liệu
entry_frame = ttk.Frame(root, padding=10)
entry_frame.pack(fill="x")

ttk.Label(entry_frame, text="Ngày:").grid(row=0, column=0, padx=5)
date_entry = DateEntry(entry_frame, width=12, date_pattern="yyyy-mm-dd")
date_entry.grid(row=0, column=1, padx=5)

ttk.Label(entry_frame, text="Mặt hàng:").grid(row=0, column=2, padx=5)
item_entry = ttk.Entry(entry_frame, width=12)
item_entry.grid(row=0, column=3, padx=5)

ttk.Label(entry_frame, text="Loại:").grid(row=0, column=4, padx=5)
type_var = tk.StringVar(value="buy")
type_combo = ttk.Combobox(entry_frame, textvariable=type_var, values=["buy", "sell"], width=6, state="readonly")
type_combo.grid(row=0, column=5, padx=5)

ttk.Label(entry_frame, text="Số lượng:").grid(row=0, column=6, padx=5)
quantity_entry = ttk.Entry(entry_frame, width=10)
quantity_entry.grid(row=0, column=7, padx=5)

ttk.Label(entry_frame, text="Đơn giá:").grid(row=0, column=8, padx=5)
price_entry = ttk.Entry(entry_frame, width=12)
price_entry.grid(row=0, column=9, padx=5)

ttk.Button(entry_frame, text="Thêm giao dịch", command=add_transaction).grid(row=0, column=10, padx=10)

# Frame bảng
tree_frame = ttk.Frame(root)
tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

columns = ("Mặt hàng", "Tổng mua", "Tổng bán", "Lãi/Lỗ")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=130)
tree.pack(fill="both", expand=True)

# Label lãi lỗ
profit_label = ttk.Label(root, text="Lãi/Lỗ: 0 đ", foreground="green", font=("Segoe UI", 12, "bold"))
profit_label.pack(pady=5)

# Khởi chạy ban đầu
refresh_summary()
date_entry.bind("<<DateEntrySelected>>", lambda e: refresh_summary())

root.mainloop()
