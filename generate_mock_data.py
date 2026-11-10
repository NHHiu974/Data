import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def create_shopee_dataset(num_records=1000, filename="Shopee_Simulated_Transactions.xlsx"):
    np.random.seed(42)
    categories = ['ThoiTrang', 'DienTu', 'MyPham', 'GiaDung', 'MeVaBe']
    cities = ['Ho Chi Minh', 'Ha Noi', 'Da Nang', 'Can Tho', 'Hai Phong']
    
    start_date = datetime(2026, 1, 1)
    
    data = []
    for i in range(1, num_records + 1):
        order_id = f"SP_{100000 + i}"
        customer_id = f"CUST_{np.random.randint(100, 350)}"
        order_time = start_date + timedelta(
            days=int(np.random.randint(0, 90)),
            hours=int(np.random.randint(0, 24)),
            minutes=int(np.random.randint(0, 60))
        )
        category = np.random.choice(categories, p=[0.35, 0.20, 0.20, 0.15, 0.10])
        city = np.random.choice(cities, p=[0.45, 0.30, 0.10, 0.08, 0.07])
        
        # Giá trị cơ sở theo ngành hàng
        base_price = {
            'ThoiTrang': np.random.uniform(80, 500),
            'DienTu': np.random.uniform(300, 3000),
            'MyPham': np.random.uniform(120, 800),
            'GiaDung': np.random.uniform(150, 1200),
            'MeVaBe': np.random.uniform(100, 700)
        }[category]
        
        voucher_discount = np.random.choice([0, 15, 30, 50, 100], p=[0.3, 0.3, 0.2, 0.15, 0.05])
        freeship_flag = np.random.choice([0, 1], p=[0.35, 0.65])
        
        # Đưa vào 1 số dòng outlier hoặc missing để DataCleaner xử lý
        status = np.random.choice(['Completed', 'Cancelled', 'Returned'], p=[0.88, 0.08, 0.04])
        
        data.append({
            'Order_ID': order_id,
            'Customer_ID': customer_id,
            'Order_Date': order_time,
            'Category': category,
            'City': city,
            'Item_Price_k': round(base_price, 2),
            'Voucher_Discount_k': voucher_discount,
            'Is_Freeship': freeship_flag,
            'Order_Status': status
        })
    
    df = pd.DataFrame(data)
    # Thêm giá trị rỗng ngẫu nhiên để demo tính năng DataCleaner
    df.loc[np.random.choice(df.index, 10), 'Category'] = np.nan
    df.to_excel(filename, index=False)
    print(f"[+] Da tao file du lieu mo phong thanh cong: {filename}")

if __name__ == "__main__":
    create_shopee_dataset()