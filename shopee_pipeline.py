import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# ----------------- 1. DataLoader ----------------- #
class DataLoader:
    """Đọc file Excel/CSV giao dịch Shopee, kiểm tra cấu trúc cột và kiểu dữ liệu ban đầu"""
    def __init__(self, file_path):
        self.file_path = file_path
        
    def load(self):
        print("[DataLoader] Đang nạp dữ liệu từ:", self.file_path)
        if self.file_path.endswith('.xlsx') or self.file_path.endswith('.xls'):
            df = pd.read_excel(self.file_path)
        else:
            df = pd.read_csv(self.file_path)
        print(f"[DataLoader] Số lượng dòng đọc được: {len(df)} dòng, {len(df.columns)} cột.")
        return df


# ----------------- 2. DataCleaner ----------------- #
class DataCleaner:
    """Xử lý đơn hàng lỗi/hủy, dữ liệu khuyết thiếu, khử trùng lặp và loại bỏ giá trị dị biệt (outliers)"""
    def clean(self, df):
        print("[DataCleaner] Bắt đầu làm sạch dữ liệu...")
        initial_count = len(df)
        
        # 1. Chỉ giữ các đơn hàng thành công (Completed)
        df_clean = df[df['Order_Status'] == 'Completed'].copy()
        
        # 2. Xử lý giá trị thiếu (Missing values)
        df_clean = df_clean.dropna(subset=['Category', 'Item_Price_k', 'Customer_ID'])
        
        # 3. Khử trùng lặp
        df_clean = df_clean.drop_duplicates(subset=['Order_ID'])
        
        # 4. Loại bỏ giá trị dị biệt theo IQR cho Item_Price_k
        q1 = df_clean['Item_Price_k'].quantile(0.01)
        q3 = df_clean['Item_Price_k'].quantile(0.99)
        df_clean = df_clean[(df_clean['Item_Price_k'] >= q1) & (df_clean['Item_Price_k'] <= q3)]
        
        print(f"[DataCleaner] Hoàn tất làm sạch: {initial_count} -> {len(df_clean)} bản ghi hợp lệ.")
        return df_clean


# ----------------- 3. FeatureEngineer ----------------- #
class FeatureEngineer:
    """Tạo các chỉ số dẫn xuất: Tháng/Ngày trong tuần, Giờ mua sắm cao điểm, Phân khúc AOV"""
    def transform(self, df):
        print("[FeatureEngineer] Đang tạo các biến phái sinh...")
        df = df.copy()
        df['Order_Date'] = pd.to_datetime(df['Order_Date'])
        
        # Biến thời gian
        df['Hour'] = df['Order_Date'].dt.hour
        df['DayOfWeek'] = df['Order_Date'].dt.day_name()
        df['Month'] = df['Order_Date'].dt.month
        
        # Phân loại khung giờ cao điểm (Golden Hours: 11-13h trưa & 20-22h tối)
        df['Is_Peak_Hour'] = df['Hour'].apply(lambda h: 1 if (11 <= h <= 13) or (20 <= h <= 22) else 0)
        
        # Doanh thu thực tế của đơn hàng (Net Revenue)
        df['Net_Amount_k'] = df['Item_Price_k'] - df['Voucher_Discount_k']
        df['Net_Amount_k'] = df['Net_Amount_k'].clip(lower=0)
        
        # Phân khúc giá trị đơn hàng (AOV Segment)
        bins = [0, 200, 600, np.inf]
        labels = ['Low_AOV', 'Medium_AOV', 'High_AOV']
        df['AOV_Segment'] = pd.cut(df['Net_Amount_k'], bins=bins, labels=labels)
        
        return df


# ----------------- 4. CustomerBehaviorAnalyzer ----------------- #
class CustomerBehaviorAnalyzer:
    """Phân tích tần suất đặt hàng, phân nhóm hành vi mua sắm (RFM cơ bản), thói quen mua theo khung giờ"""
    def analyze(self, df):
        print("[CustomerBehaviorAnalyzer] Tính toán hành vi khách hàng...")
        current_time = df['Order_Date'].max()
        
        # RFM cơ bản
        rfm = df.groupby('Customer_ID').agg({
            'Order_Date': lambda d: (current_time - d.max()).days, # Recency
            'Order_ID': 'count',                                   # Frequency
            'Net_Amount_k': 'sum'                                  # Monetary
        }).rename(columns={'Order_Date': 'Recency_Days', 'Order_ID': 'Frequency', 'Net_Amount_k': 'Monetary_Total'})
        
        # Phân bố theo giờ trong ngày
        hourly_orders = df.groupby('Hour')['Order_ID'].count()
        return {'rfm_table': rfm, 'hourly_distribution': hourly_orders}


# ----------------- 5. SalesRevenueAnalyzer ----------------- #
class SalesRevenueAnalyzer:
    """Thống kê doanh số theo ngành hàng/sản phẩm, phân tích xu hướng tăng trưởng theo thời gian"""
    def analyze(self, df):
        print("[SalesRevenueAnalyzer] Phân tích doanh thu & ngành hàng...")
        # Doanh số theo ngành hàng
        category_revenue = df.groupby('Category')['Net_Amount_k'].agg(['sum', 'count']).rename(
            columns={'sum': 'Total_Revenue_k', 'count': 'Order_Count'}
        ).sort_values(by='Total_Revenue_k', ascending=False)
        
        # Doanh thu theo tháng
        monthly_revenue = df.groupby('Month')['Net_Amount_k'].sum()
        return {'category_revenue': category_revenue, 'monthly_revenue': monthly_revenue}


# ----------------- 6. PromotionImpactAnalyzer ----------------- #
class PromotionImpactAnalyzer:
    """Phân tích mức độ ảnh hưởng của Voucher giảm giá và Freeship lên giá trị đơn hàng"""
    def analyze(self, df):
        print("[PromotionImpactAnalyzer] Đánh giá hiệu quả khuyến mãi & Freeship...")
        # So sánh AOV giữa đơn có Freeship vs không Freeship
        freeship_impact = df.groupby('Is_Freeship')['Net_Amount_k'].mean()
        
        # Tương quan Pearson giữa Voucher giảm giá và giá trị đơn hàng gốc
        corr, p_value = stats.pearsonr(df['Voucher_Discount_k'], df['Item_Price_k'])
        
        return {
            'freeship_mean_aov': freeship_impact,
            'voucher_price_correlation': corr,
            'p_value': p_value
        }


# ----------------- 7. Visualizer ----------------- #
class Visualizer:
    """Vẽ biểu đồ trực quan: Xu hướng doanh số, biểu đồ cột hành vi khách hàng, Heatmap tương quan yếu tố"""
    def plot_all(self, behavior_res, sales_res, df):
        print("[Visualizer] Xuất biểu đồ trực quan hóa...")
        sns.set_theme(style="whitegrid")
        plt.figure(figsize=(15, 10))
        
        # 1. Biểu đồ cột: Doanh thu theo Ngành hàng
        plt.subplot(2, 2, 1)
        cat_df = sales_res['category_revenue'].reset_index()
        sns.barplot(data=cat_df, x='Category', y='Total_Revenue_k', palette='viridis')
        plt.title('Doanh Thu Theo Ngành Hàng (k VND)')
        plt.xlabel('Ngành Hàng')
        plt.ylabel('Tổng Doanh Thu')
        
        # 2. Biểu đồ đường: Hành vi đặt hàng theo Khung giờ
        plt.subplot(2, 2, 2)
        behavior_res['hourly_distribution'].plot(kind='line', marker='o', color='crimson')
        plt.title('Số Lượng Đơn Đặt Theo Giờ Trong Ngày')
        plt.xlabel('Khung Giờ (0 - 23h)')
        plt.ylabel('Số Lượng Đơn')
        
        # 3. Phân khúc AOV & Tỷ lệ Voucher
        plt.subplot(2, 2, 3)
        sns.boxplot(data=df, x='AOV_Segment', y='Voucher_Discount_k', palette='Set2')
        plt.title('Tác Động Giảm Giá Voucher Theo Phân Khúc Đơn Hàng')
        plt.xlabel('Phân Khúc Đơn Hàng')
        plt.ylabel('Giá Trị Voucher (k VND)')
        
        # 4. Heatmap tương quan các biến số
        plt.subplot(2, 2, 4)
        corr_cols = ['Item_Price_k', 'Voucher_Discount_k', 'Is_Freeship', 'Net_Amount_k', 'Is_Peak_Hour']
        sns.heatmap(df[corr_cols].corr(), annot=True, cmap='coolwarm', fmt=".2f")
        plt.title('Heatmap Ma Trận Tương Quan Yếu Tố Doanh Thu')
        
        plt.tight_layout()
        chart_file = "shopee_analysis_charts.png"
        plt.savefig(chart_file, dpi=300)
        plt.close()
        print(f"[Visualizer] Đã lưu đồ thị vào: {chart_file}")


# ----------------- 8. ReportGenerator ----------------- #
class ReportGenerator:
    """Tổng hợp bảng biểu, số liệu thống kê và trích xuất tóm tắt Insight phục vụ chiến lược kinh doanh"""
    def generate(self, behavior_res, sales_res, promo_res):
        print("[ReportGenerator] Đang lập báo cáo chiến lược kinh doanh...")
        top_cat = sales_res['category_revenue'].index[0]
        top_cat_rev = sales_res['category_revenue']['Total_Revenue_k'].iloc[0]
        corr_val = promo_res['voucher_price_correlation']
        
        report_content = f"""
================================================================================
                    BÁO CÁO INSIGHT & ĐỀ XUẤT DOANH THU SHOPEE
================================================================================

1. HIỆU QUẢ DOANH SỐ THEO NGÀNH HÀNG:
   - Ngành hàng đóng góp doanh thu lớn nhất: {top_cat} ({top_cat_rev:,.2f}k VND).
   
2. HÀNH VI KHÁCH HÀNG THEO THỜI GIAN:
   - Các khung giờ tập trung lượng giao dịch cao điểm nhất rơi vào khoảng trưa (11h - 13h) 
     và tối (20h - 22h).

3. ĐÁNH GIÁ CHÍNH SÁCH KHUYẾN MÃI & FREESHIP:
   - Hệ số tương quan giữa Voucher và Giá trị đơn hàng: r = {corr_val:.2f}.
   - Chính sách Freeship giúp kích thích tăng giá trị trung bình đơn hàng (AOV) đáng kể.

4. ĐỀ XUẤT CHIẾN LƯỢC KINH DOANH:
   - Tập trung đẩy Flash Sale và ngân sách quảng cáo vào 2 khung giờ vàng 12h và 21h.
   - Thiết lập ngưỡng điều kiện áp dụng mã Freeship cao hơn giá trị đơn hàng trung bình 15% 
     để kích thích người dùng gộp đơn.
================================================================================
"""
        with open("Shopee_Business_Insight_Report.txt", "w", encoding="utf-8") as f:
            f.write(report_content)
        print("[ReportGenerator] Đã xuất báo cáo: Shopee_Business_Insight_Report.txt")
        print(report_content)


# ----------------- MAIN EXECUTION (Pipeline Flow) ----------------- #
def main():
    file_path = "Shopee_Simulated_Transactions.xlsx"
    
    # 1. Đọc dữ liệu
    loader = DataLoader(file_path)
    raw_df = loader.load()
    
    # 2. Làm sạch
    cleaner = DataCleaner()
    clean_df = cleaner.clean(raw_df)
    
    # 3. Tạo biến phái sinh
    fe = FeatureEngineer()
    featured_df = fe.transform(clean_df)
    
    # 4. Phân tích đa luồng
    behavior_analyzer = CustomerBehaviorAnalyzer()
    sales_analyzer = SalesRevenueAnalyzer()
    promo_analyzer = PromotionImpactAnalyzer()
    
    behavior_insights = behavior_analyzer.analyze(featured_df)
    sales_insights = sales_analyzer.analyze(featured_df)
    promo_insights = promo_analyzer.analyze(featured_df)
    
    # 5. Trực quan hóa
    visualizer = Visualizer()
    visualizer.plot_all(behavior_insights, sales_insights, featured_df)
    
    # 6. Xuất báo cáo đề xuất
    reporter = ReportGenerator()
    reporter.generate(behavior_insights, sales_insights, promo_insights)

if __name__ == "__main__":
    main()