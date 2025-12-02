import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# --- CẤU HÌNH ---
filename = 'pls-sem-finale ban dep.xlsx'

print("Đang quét toàn bộ file Excel...")
try:
    xls = pd.ExcelFile(filename, engine='openpyxl')
except FileNotFoundError:
    print(f"Lỗi: Không tìm thấy file '{filename}'.")
    exit()

# 1. Tìm xem bảng dữ liệu nằm ở Sheet nào
target_sheet = None
start_row = -1
df = None

for sheet_name in xls.sheet_names:
    print(f"Đang kiểm tra Sheet: {sheet_name}...")
    temp_df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
    
    # Quét tất cả các ô để tìm từ khóa
    # (Cách này chắc chắn tìm ra dù nó nằm ở cột A, B hay C)
    for i in range(len(temp_df)):
        # Lấy 5 cột đầu tiên để kiểm tra cho nhanh
        row_str = " ".join([str(x) for x in temp_df.iloc[i, :5].values])
        if "Fornell-Larcker criterion" in row_str:
            target_sheet = sheet_name
            start_row = i
            df = temp_df
            print(f"--> ĐÃ TÌM THẤY bảng tại dòng {start_row} của Sheet '{sheet_name}'")
            break
    
    if target_sheet:
        break

if target_sheet:
    # 2. Trích xuất dữ liệu
    header_row_idx = start_row + 2
    
    # Lấy danh sách tên biến
    headers = []
    # Quét hàng tiêu đề, bỏ qua các ô trống hoặc 'nan'
    for val in df.iloc[header_row_idx, :]:
        if pd.notna(val) and isinstance(val, str) and len(val) > 1:
            headers.append(val)
            
    num_vars = len(headers)
    print(f"Phát hiện {num_vars} biến tiềm ẩn: {headers}")
    
    # Xác định cột bắt đầu chứa dữ liệu (thường là cột thứ 3 - index 2)
    # Nhưng để chắc ăn, ta tìm cột chứa tên biến đầu tiên trong headers
    first_var = headers[0]
    start_col_idx = -1
    for j in range(len(df.columns)):
        if df.iloc[header_row_idx, j] == first_var:
            start_col_idx = j
            break
            
    if start_col_idx == -1:
        # Fallback nếu không tìm thấy header khớp
        start_col_idx = 2 

    # Lấy dữ liệu
    data_rows = []
    for i in range(num_vars):
        row_idx = header_row_idx + 1 + i
        # Lấy đúng số lượng cột tương ứng số biến
        vals = df.iloc[row_idx, start_col_idx : start_col_idx + num_vars].values
        data_rows.append(vals)
    
    fl_df = pd.DataFrame(data_rows, columns=headers, index=headers)
    fl_df = fl_df.apply(pd.to_numeric, errors='coerce')
    
    # 3. Điền đầy đủ ma trận
    for i in range(num_vars):
        for j in range(i+1, num_vars):
            fl_df.iloc[i, j] = fl_df.iloc[j, i]

    # 4. Vẽ Heatmap
    plt.figure(figsize=(10, 8), dpi=300)
    mask = np.triu(np.ones_like(fl_df, dtype=bool), k=1)
    
    sns.heatmap(fl_df, 
                mask=mask,
                annot=True, 
                fmt=".2f", 
                cmap='RdBu_r', 
                vmin=-1, vmax=1, 
                center=0,
                square=True, 
                linewidths=1, 
                cbar_kws={"shrink": .8})

    plt.title('Latent Variable Correlations (Fornell-Larcker)', fontsize=16, fontweight='bold', pad=20)
    plt.xticks(rotation=45, ha='right', fontsize=11)
    plt.yticks(rotation=0, fontsize=11)
    plt.tight_layout()
    
    plt.savefig('poster_heatmap.png')
    print("Xong! Ảnh biểu đồ đã được lưu tên là 'poster_heatmap.png'")
    plt.show()

else:
    print("Vẫn không tìm thấy. Bạn vui lòng mở file Excel lên và kiểm tra xem bảng 'Fornell-Larcker criterion' có tồn tại không nhé.")