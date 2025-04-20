import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
import os

# Kết nối SQLite và khởi tạo database
def init_db():
    db_path = "gold_shop.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            sp TEXT,
            au TEXT,
            vang_tay_tl REAL,
            vang_tay_tt REAL,
            ngoai_te_tl REAL,
            ngoai_te_tt REAL,
            ngoai_te_loai TEXT,
            gia_sl REAL,
            gia_tt REAL,
            bac_tl REAL,
            bac_tt REAL,
            type TEXT
        )
    ''')
    conn.commit()
    return conn

# Khởi tạo database
conn = init_db()
cursor = conn.cursor()

def add_transaction():
    date = date_entry.get()
    transaction_type = "buy"  # Mua
    
    try:
        sp = sp_entry.get() or ""
        au = au_entry.get() or ""
        
        vang_tay_tl = float(vang_tay_tl_entry.get()) if vang_tay_tl_entry.get() else 0
        vang_tay_tt = float(vang_tay_tt_entry.get()) if vang_tay_tt_entry.get() else 0
        
        ngoai_te_tl = float(ngoai_te_tl_entry.get()) if ngoai_te_tl_entry.get() else 0
        ngoai_te_tt = float(ngoai_te_tt_entry.get()) if ngoai_te_tt_entry.get() else 0
        ngoai_te_loai = ngoai_te_loai_entry.get() or ""
        
        gia_sl = float(gia_sl_entry.get()) if gia_sl_entry.get() else 0
        gia_tt = float(gia_tt_entry.get()) if gia_tt_entry.get() else 0
        
        bac_tl = float(bac_tl_entry.get()) if bac_tl_entry.get() else 0
        bac_tt = float(bac_tt_entry.get()) if bac_tt_entry.get() else 0
        
    except ValueError:
        messagebox.showerror("Lỗi", "Vui lòng nhập số vào các ô số lượng và giá")
        return
    
    # Kiểm tra có nhập ít nhất một mặt hàng
    if not any([vang_tay_tl, ngoai_te_tl, gia_sl, bac_tl]):
        messagebox.showerror("Lỗi", "Vui lòng nhập ít nhất một mặt hàng")
        return
    
    try:
        cursor.execute('''
            INSERT INTO transactions (
                date, sp, au, 
                vang_tay_tl, vang_tay_tt,
                ngoai_te_tl, ngoai_te_tt, ngoai_te_loai,
                gia_sl, gia_tt,
                bac_tl, bac_tt,
                type
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            date, sp, au,
            vang_tay_tl, vang_tay_tt,
            ngoai_te_tl, ngoai_te_tt, ngoai_te_loai,
            gia_sl, gia_tt,
            bac_tl, bac_tt,
            transaction_type
        ))
        conn.commit()
        clear_entries()
        refresh_summary()
    except sqlite3.Error as e:
        messagebox.showerror("Lỗi database", f"Lỗi khi thêm giao dịch: {str(e)}")

def clear_entries():
    sp_entry.delete(0, tk.END)
    au_entry.delete(0, tk.END)
    vang_tay_tl_entry.delete(0, tk.END)
    vang_tay_tt_entry.delete(0, tk.END)
    ngoai_te_tl_entry.delete(0, tk.END)
    ngoai_te_tt_entry.delete(0, tk.END)
    ngoai_te_loai_entry.set("")
    gia_sl_entry.delete(0, tk.END)
    gia_tt_entry.delete(0, tk.END)
    bac_tl_entry.delete(0, tk.END)
    bac_tt_entry.delete(0, tk.END)

def refresh_summary():
    for row in tree.get_children():
        tree.delete(row)
    
    selected_date = date_entry.get()
    try:
        cursor.execute('''
            SELECT date, sp, au, 
                   vang_tay_tl, vang_tay_tt,
                   ngoai_te_tl, ngoai_te_tt, ngoai_te_loai,
                   gia_sl, gia_tt,
                   bac_tl, bac_tt
            FROM transactions
            WHERE date = ? AND type = 'buy'
            ORDER BY id DESC
        ''', (selected_date,))
        
        for row in cursor.fetchall():
            # Định dạng lại dữ liệu để hiển thị
            formatted_row = list(row)
            # Thay giá trị 0 bằng chuỗi rỗng
            formatted_row = ["" if x == 0 or x == "0" else x for x in formatted_row]
            tree.insert("", "end", values=formatted_row)
    except sqlite3.Error as e:
        messagebox.showerror("Lỗi database", f"Lỗi khi tải dữ liệu: {str(e)}")

# Tạo giao diện chính
root = tk.Tk()
root.title("QUẢN LÝ TIỆM VÀNG - PHIÊN BẢN NHẬP LIỆU")
root.geometry("1400x650")

# Tạo style để làm nổi bật các phần
style = ttk.Style()
style.configure("Header.TLabel", font=('Arial', 14, 'bold'), foreground='blue')
style.configure("Section.TLabel", font=('Arial', 12, 'bold'), foreground='dark green')
style.configure("Input.TLabel", font=('Arial', 10))

# Frame chứa phần nhập liệu
input_frame = ttk.LabelFrame(root, text="NHẬP THÔNG TIN GIAO DỊCH MUA", padding=15)
input_frame.pack(fill='x', padx=10, pady=5)

# Dòng 1: Tiêu đề và ngày
header_frame = ttk.Frame(input_frame)
header_frame.pack(fill='x', pady=5)

ttk.Label(header_frame, text="MUA VÀNG/BẠC/NGOẠI TỆ", style="Header.TLabel").pack(side='left', padx=5)
ttk.Label(header_frame, text="Ngày giao dịch:", style="Input.TLabel").pack(side='left', padx=5)
date_entry = DateEntry(header_frame, width=12, date_pattern="dd/mm/yyyy")
date_entry.pack(side='left', padx=5)

# Tạo bảng nhập liệu với các nhãn rõ ràng
table_frame = ttk.Frame(input_frame)
table_frame.pack(fill='x', pady=10)

# Tạo các section với tiêu đề rõ ràng
sections = [
    {"title": "THÔNG TIN CHUNG", "fields": [
        {"label": "SP (Sản phẩm):", "entry": "sp_entry", "width": 8},
        {"label": "AU (Độ tuổi):", "entry": "au_entry", "width": 8}
    ]},
    {"title": "VÀNG TÂY", "fields": [
        {"label": "Trọng lượng (TL):", "entry": "vang_tay_tl_entry", "width": 8},
        {"label": "Thành tiền (TT):", "entry": "vang_tay_tt_entry", "width": 12}
    ]},
    {"title": "NGOẠI TỆ", "fields": [
        {"label": "Trọng lượng (TL):", "entry": "ngoai_te_tl_entry", "width": 8},
        {"label": "Thành tiền (TT):", "entry": "ngoai_te_tt_entry", "width": 12},
        {"label": "Loại ngoại tệ:", "entry": "ngoai_te_loai_entry", "width": 10, "type": "combobox"}
    ]},
    {"title": "GIÁ", "fields": [
        {"label": "Số lượng (SL):", "entry": "gia_sl_entry", "width": 8},
        {"label": "Thành tiền (TT):", "entry": "gia_tt_entry", "width": 12}
    ]},
    {"title": "BẠC VÀ KHÁC", "fields": [
        {"label": "Trọng lượng (TL):", "entry": "bac_tl_entry", "width": 8},
        {"label": "Thành tiền (TT):", "entry": "bac_tt_entry", "width": 12}
    ]}
]

# Tạo các ô nhập liệu với nhãn mô tả rõ ràng
for section in sections:
    section_frame = ttk.LabelFrame(table_frame, text=section["title"], style="Section.TLabel")
    section_frame.pack(side='left', padx=5, fill='both', expand=True)
    
    for field in section["fields"]:
        field_frame = ttk.Frame(section_frame)
        field_frame.pack(fill='x', pady=2)
        
        ttk.Label(field_frame, text=field["label"], style="Input.TLabel", width=20).pack(side='left')
        
        if field.get("type") == "combobox":
            entry = ttk.Combobox(field_frame, values=["USD", "EUR", "GBP"], width=field["width"], state="readonly")
            entry.set("USD")
        else:
            entry = ttk.Entry(field_frame, width=field["width"])
        
        entry.pack(side='left')
        globals()[field["entry"]] = entry  # Lưu biến vào global

# Nút thêm giao dịch
button_frame = ttk.Frame(input_frame)
button_frame.pack(fill='x', pady=10)
ttk.Button(button_frame, text="THÊM GIAO DỊCH", style="TButton", command=add_transaction).pack(side='right')

# Bảng tổng hợp
summary_frame = ttk.LabelFrame(root, text="LỊCH SỬ GIAO DỊCH HÔM NAY", style="Section.TLabel", padding=10)
summary_frame.pack(fill='both', expand=True, padx=10, pady=10)

# Treeview với các cột rõ ràng
columns = [
    {"text": "Ngày", "width": 100},
    {"text": "SP", "width": 80, "tooltip": "Sản phẩm"},
    {"text": "AU", "width": 80, "tooltip": "Độ tuổi"},
    {"text": "Vàng Tây TL", "width": 100, "tooltip": "Trọng lượng vàng tây"},
    {"text": "Vàng Tây TT", "width": 120, "tooltip": "Thành tiền vàng tây"},
    {"text": "Ngoại tệ TL", "width": 100, "tooltip": "Trọng lượng ngoại tệ"},
    {"text": "Ngoại tệ TT", "width": 120, "tooltip": "Thành tiền ngoại tệ"},
    {"text": "Loại", "width": 80, "tooltip": "Loại ngoại tệ"},
    {"text": "Giá SL", "width": 80, "tooltip": "Số lượng giá"},
    {"text": "Giá TT", "width": 120, "tooltip": "Thành tiền giá"},
    {"text": "Bạc TL", "width": 80, "tooltip": "Trọng lượng bạc"},
    {"text": "Bạc TT", "width": 120, "tooltip": "Thành tiền bạc"}
]

tree = ttk.Treeview(summary_frame, columns=[col["text"] for col in columns], show="headings", height=15)

for col in columns:
    tree.heading(col["text"], text=col["text"])
    tree.column(col["text"], width=col["width"], anchor='center')

tree.pack(fill='both', expand=True)

# Thanh cuộn
scrollbar = ttk.Scrollbar(summary_frame, orient="vertical", command=tree.yview)
scrollbar.pack(side='right', fill='y')
tree.configure(yscrollcommand=scrollbar.set)

# Bind sự kiện ngày thay đổi
date_entry.bind("<<DateEntrySelected>>", lambda e: refresh_summary())

# Khởi chạy
refresh_summary()
root.mainloop()