import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# --- CẤU HÌNH ---
filename = 'pls-sem-finale ban dep.xlsx'

print("Đang quét tìm bảng R-Square...")

try:
    # Đọc toàn bộ file (tất cả các sheet)
    xls = pd.ExcelFile(filename, engine='openpyxl')
except FileNotFoundError:
    print(f"Lỗi: Không tìm thấy file '{filename}'.")
    exit()

# 1. Tìm vị trí bảng R-square trong tất cả các Sheet
target_sheet = None
header_row_idx = -1
df = None

# Duyệt qua từng sheet
for sheet_name in xls.sheet_names:
    temp_df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
    
    # Quét từng dòng để tìm chữ "R-square adjusted"
    for i in range(len(temp_df)):
        # Kiểm tra 10 cột đầu tiên của mỗi dòng
        row_values = [str(x) for x in temp_df.iloc[i, :10].values]
        
        # Nếu dòng nào chứa chữ "R-square adjusted" thì đó chính là dòng tiêu đề
        if "R-square adjusted" in row_values:
            target_sheet = sheet_name
            header_row_idx = i
            df = temp_df
            print(f"--> ĐÃ TÌM THẤY bảng tại dòng {header_row_idx} của Sheet '{sheet_name}'")
            break
    
    if target_sheet:
        break

if target_sheet:
    # 2. Xác định cột chứa dữ liệu
    # Tìm xem "R-square adjusted" nằm ở cột số mấy
    r2_adj_col_idx = -1
    construct_col_idx = -1 # Cột tên biến
    
    # Quét dòng tiêu đề vừa tìm được
    for j in range(len(df.columns)):
        val = str(df.iloc[header_row_idx, j])
        if "R-square adjusted" in val:
            r2_adj_col_idx = j
            # Thường cột tên biến sẽ nằm trước đó 1 hoặc 2 cột, và là cột rỗng hoặc có tên
            # Ta giả định cột tên biến là cột đầu tiên có dữ liệu dạng chuỗi ở các dòng dưới
            # Nhưng an toàn nhất là lấy cột B (index 1) như chuẩn SmartPLS
            construct_col_idx = 1 
            break
            
    if r2_adj_col_idx != -1:
        # 3. Lấy dữ liệu
        data_list = []
        curr_row = header_row_idx + 1
        
        while curr_row < len(df):
            # Lấy tên biến (Construct)
            construct = df.iloc[curr_row, construct_col_idx]
            val = df.iloc[curr_row, r2_adj_col_idx]
            
            # Nếu tên biến bị trống -> Hết bảng -> Dừng
            if pd.isna(construct):
                break
                
            # Lưu dữ liệu nếu có giá trị R2
            if pd.notna(val):
                data_list.append({'Construct': construct, 'R2 Adjusted': val})
            
            curr_row += 1
            
        plot_df = pd.DataFrame(data_list)
        
        # 4. Vẽ biểu đồ
        if not plot_df.empty:
            plt.figure(figsize=(8, 6), dpi=300)
            plot_df = plot_df.sort_values('R2 Adjusted', ascending=False)
            
            ax = sns.barplot(data=plot_df, x='Construct', y='R2 Adjusted', palette='Blues_r')
            
            # Thêm đường mốc (Benchmark lines)
            plt.axhline(0.5, color='orange', linestyle='--', alpha=0.7, label='Moderate (0.5)')
            plt.axhline(0.75, color='green', linestyle='--', alpha=0.7, label='Substantial (0.75)')
            
            # Hiển thị số liệu
            for i in ax.containers:
                ax.bar_label(i, fmt='%.3f', padding=3, fontsize=11, fontweight='bold')

            plt.title('Model Explanatory Power (R-Square Adjusted)', fontsize=14, fontweight='bold', pad=20)
            plt.ylabel('R-Square Adjusted')
            plt.xlabel('')
            plt.ylim(0, 1)
            plt.legend(loc='upper right')
            plt.tight_layout()
            
            plt.savefig('poster_rsquare.png')
            print("Xong! Đã tạo file 'poster_rsquare.png'")
            plt.show()
        else:
            print("Tìm thấy bảng nhưng không có dữ liệu bên dưới.")
    else:
        print("Tìm thấy dòng tiêu đề nhưng không xác định được cột R-square adjusted.")
else:
    print("Vẫn không tìm thấy bảng R-Square. Bạn hãy chắc chắn file Excel có chứa bảng này.")