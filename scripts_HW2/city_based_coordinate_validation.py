import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster
import matplotlib.pyplot as plt

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

class CityBasedValidator:
    def __init__(self):
        """初始化縣市座標驗證器"""
        # 定義各縣市的合理經緯度範圍
        self.city_bounds = {
            '新北市': {'lat_min': 24.8, 'lat_max': 25.3, 'lon_min': 121.3, 'lon_max': 121.9},
            '臺北市': {'lat_min': 24.9, 'lat_max': 25.3, 'lon_min': 121.4, 'lon_max': 121.7},
            '桃園市': {'lat_min': 24.6, 'lat_max': 25.1, 'lon_min': 120.9, 'lon_max': 121.4},
            '臺中市': {'lat_min': 24.0, 'lat_max': 24.4, 'lon_min': 120.4, 'lon_max': 120.9},
            '臺南市': {'lat_min': 22.8, 'lat_max': 23.5, 'lon_min': 120.0, 'lon_max': 120.4},
            '高雄市': {'lat_min': 22.4, 'lat_max': 23.1, 'lon_min': 120.2, 'lon_max': 120.6},
            '基隆市': {'lat_min': 25.0, 'lat_max': 25.3, 'lon_min': 121.6, 'lon_max': 121.8},
            '新竹市': {'lat_min': 24.7, 'lat_max': 24.9, 'lon_min': 120.9, 'lon_max': 121.1},
            '嘉義市': {'lat_min': 23.4, 'lat_max': 23.6, 'lon_min': 120.4, 'lon_max': 120.6},
            '新竹縣': {'lat_min': 24.4, 'lat_max': 24.9, 'lon_min': 120.9, 'lon_max': 121.2},
            '苗栗縣': {'lat_min': 24.2, 'lat_max': 24.7, 'lon_min': 120.7, 'lon_max': 121.0},
            '彰化縣': {'lat_min': 23.7, 'lat_max': 24.3, 'lon_min': 120.3, 'lon_max': 120.7},
            '南投縣': {'lat_min': 23.6, 'lat_max': 24.2, 'lon_min': 120.7, 'lon_max': 121.2},
            '雲林縣': {'lat_min': 23.5, 'lat_max': 23.9, 'lon_min': 120.2, 'lon_max': 120.6},
            '嘉義縣': {'lat_min': 23.3, 'lat_max': 23.7, 'lon_min': 120.2, 'lon_max': 120.6},
            '屏東縣': {'lat_min': 22.2, 'lat_max': 22.9, 'lon_min': 120.4, 'lon_max': 121.0},
            '宜蘭縣': {'lat_min': 24.4, 'lat_max': 24.8, 'lon_min': 121.6, 'lon_max': 121.9},
            '花蓮縣': {'lat_min': 22.9, 'lat_max': 24.0, 'lon_min': 121.2, 'lon_max': 121.7},
            '臺東縣': {'lat_min': 22.3, 'lat_max': 23.3, 'lon_min': 120.8, 'lon_max': 121.4},
            '澎湖縣': {'lat_min': 23.3, 'lat_max': 23.7, 'lon_min': 119.4, 'lon_max': 119.7},
            '金門縣': {'lat_min': 24.2, 'lat_max': 24.6, 'lon_min': 118.2, 'lon_max': 118.5},
            '連江縣': {'lat_min': 25.9, 'lat_max': 26.4, 'lon_min': 119.8, 'lon_max': 120.3}
        }
        
        # 外島地區
        self.outer_islands = ['澎湖縣', '金門縣', '連江縣']
        
    def extract_city_name(self, location_str):
        """從地點字串中提取縣市名稱"""
        if pd.isna(location_str):
            return None
            
        # 嘗試匹配縣市名稱
        for city in self.city_bounds.keys():
            if city in location_str:
                return city
        
        return None
    
    def validate_coordinates_by_city(self, df):
        """根據縣市驗證座標"""
        print("=" * 60)
        print("縣市範圍座標驗證")
        print("=" * 60)
        
        validation_results = []
        
        for idx, row in df.iterrows():
            location = row['縣市及鄉鎮市區']
            lat = row['緯度']
            lon = row['經度']
            
            # 提取縣市名稱
            city = self.extract_city_name(location)
            
            if city is None:
                validation_results.append({
                    'index': idx,
                    'city': '未知',
                    'location': location,
                    'lat': lat,
                    'lon': lon,
                    'status': '無法識別縣市',
                    'is_valid': False
                })
                continue
            
            # 檢查座標是否在該縣市範圍內
            if city in self.city_bounds:
                bounds = self.city_bounds[city]
                
                if (bounds['lat_min'] <= lat <= bounds['lat_max'] and 
                    bounds['lon_min'] <= lon <= bounds['lon_max']):
                    status = '正常'
                    is_valid = True
                else:
                    status = '超出縣市範圍'
                    is_valid = False
            else:
                status = '無定義範圍'
                is_valid = False
            
            validation_results.append({
                'index': idx,
                'city': city,
                'location': location,
                'lat': lat,
                'lon': lon,
                'status': status,
                'is_valid': is_valid
            })
        
        return validation_results
    
    def analyze_validation_results(self, validation_results):
        """分析驗證結果"""
        results_df = pd.DataFrame(validation_results)
        
        print(f"📊 驗證結果統計:")
        print(f"總筆數: {len(results_df)}")
        
        # 狀態統計
        status_counts = results_df['status'].value_counts()
        print(f"\n狀態分布:")
        for status, count in status_counts.items():
            percentage = count / len(results_df) * 100
            print(f"  {status}: {count} 筆 ({percentage:.1f}%)")
        
        # 按縣市統計問題
        problem_shelters = results_df[~results_df['is_valid']]
        if len(problem_shelters) > 0:
            print(f"\n🚨 問題點位按縣市分布:")
            city_problems = problem_shelters['city'].value_counts()
            for city, count in city_problems.head(10).items():
                print(f"  {city}: {count} 筆")
        
        return results_df, problem_shelters
    
    def create_problem_samples(self, problem_shelters, num_samples=20):
        """建立問題樣本"""
        if len(problem_shelters) == 0:
            print("✅ 沒有發現問題點位")
            return
        
        print(f"\n🚨 問題點位樣本 (前{min(num_samples, len(problem_shelters))}筆):")
        print("序號\t縣市\t\t緯度\t\t經度\t\t狀態")
        print("-" * 80)
        
        for i, (_, row) in enumerate(problem_shelters.head(num_samples).iterrows()):
            print(f"{row['index']+1}\t{row['city']}\t{row['lat']:.6f}\t{row['lon']:.6f}\t{row['status']}")
    
    def create_validation_map(self, df, validation_results):
        """建立驗證結果地圖"""
        print("\n📍 建立驗證結果地圖...")
        
        results_df = pd.DataFrame(validation_results)
        
        # 計算地圖中心點
        valid_points = results_df[results_df['is_valid']]
        if len(valid_points) > 0:
            center_lat = valid_points['lat'].mean()
            center_lon = valid_points['lon'].mean()
        else:
            center_lat = df['緯度'].mean()
            center_lon = df['經度'].mean()
        
        # 建立地圖
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=8,
            tiles='OpenStreetMap'
        )
        
        # 正常點位 (藍色)
        valid_cluster = MarkerCluster(name='正常座標').add_to(m)
        valid_shelters = results_df[results_df['is_valid']]
        
        for _, row in valid_shelters.iterrows():
            shelter_data = df.iloc[row['index']]
            
            popup_content = f"""
            <b>{shelter_data['避難收容處所名稱']}</b><br>
            📍 {row['location']}<br>
            🏢 縣市: {row['city']}<br>
            🌍 座標: ({row['lat']:.6f}, {row['lon']:.6f})<br>
            ✅ 狀態: {row['status']}<br>
            👥 收容人數: {shelter_data['預計收容人數']} 人
            """
            
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=shelter_data['避難收容處所名稱'],
                icon=folium.Icon(color='blue', icon='home', prefix='fa')
            ).add_to(valid_cluster)
        
        # 問題點位 (紅色)
        invalid_cluster = MarkerCluster(name='問題座標').add_to(m)
        invalid_shelters = results_df[~results_df['is_valid']]
        
        for _, row in invalid_shelters.iterrows():
            shelter_data = df.iloc[row['index']]
            
            popup_content = f"""
            <b>{shelter_data['避難收容處所名稱']}</b><br>
            📍 {row['location']}<br>
            🏢 縣市: {row['city']}<br>
            🌍 座標: ({row['lat']:.6f}, {row['lon']:.6f})<br>
            ❌ 狀態: {row['status']}<br>
            👥 收容人數: {shelter_data['預計收容人數']} 人<br>
            <br>
            <span style="color:red; font-weight:bold">
            ⚠️ 座標可能超出{row['city']}範圍
            </span>
            """
            
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=f"{shelter_data['避難收容處所名稱']} (問題)",
                icon=folium.Icon(color='red', icon='exclamation-triangle', prefix='fa')
            ).add_to(invalid_cluster)
        
        # 添加圖層控制
        folium.LayerControl().add_to(m)
        
        # 儲存地圖
        map_file = '../outputs_HW2/縣市範圍座標驗證地圖.html'
        m.save(map_file)
        print(f"✅ 驗證地圖已儲存: {map_file}")
        
        return m
    
    def create_city_analysis_charts(self, validation_results):
        """創建縣市分析圖表"""
        results_df = pd.DataFrame(validation_results)
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('縣市範圍座標驗證分析', fontsize=16, fontweight='bold')
        
        # 1. 整體驗證結果
        status_counts = results_df['status'].value_counts()
        axes[0, 0].pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%')
        axes[0, 0].set_title('整體驗證結果分布')
        
        # 2. 各縣市問題點數量
        problem_shelters = results_df[~results_df['is_valid']]
        if len(problem_shelters) > 0:
            city_problems = problem_shelters['city'].value_counts().head(15)
            axes[0, 1].barh(range(len(city_problems)), city_problems.values)
            axes[0, 1].set_yticks(range(len(city_problems)))
            axes[0, 1].set_yticklabels(city_problems.index)
            axes[0, 1].set_title('各縣市問題點數量 (前15名)')
            axes[0, 1].set_xlabel('問題點數量')
        else:
            axes[0, 1].text(0.5, 0.5, '無問題點位', ha='center', va='center', 
                           transform=axes[0, 1].transAxes, fontsize=14)
            axes[0, 1].set_title('各縣市問題點數量')
        
        # 3. 各縣市驗證通過率
        city_stats = []
        for city in results_df['city'].unique():
            if pd.notna(city):
                city_data = results_df[results_df['city'] == city]
                total = len(city_data)
                valid = len(city_data[city_data['is_valid']])
                pass_rate = valid / total * 100
                city_stats.append({'city': city, 'pass_rate': pass_rate, 'total': total})
        
        city_stats_df = pd.DataFrame(city_stats).sort_values('pass_rate')
        
        # 只顯示有問題的縣市
        problematic_cities = city_stats_df[city_stats_df['pass_rate'] < 100]
        if len(problematic_cities) > 0:
            axes[1, 0].barh(range(len(problematic_cities)), problematic_cities['pass_rate'])
            axes[1, 0].set_yticks(range(len(problematic_cities)))
            axes[1, 0].set_yticklabels(problematic_cities['city'])
            axes[1, 0].set_title('各縣市驗證通過率 (<100%)')
            axes[1, 0].set_xlabel('通過率 (%)')
            axes[1, 0].set_xlim(0, 100)
        else:
            axes[1, 0].text(0.5, 0.5, '所有縣市100%通過', ha='center', va='center', 
                           transform=axes[1, 0].transAxes, fontsize=14)
            axes[1, 0].set_title('各縣市驗證通過率')
        
        # 4. 座標分布散布圖
        valid_points = results_df[results_df['is_valid']]
        invalid_points = results_df[~results_df['is_valid']]
        
        if len(valid_points) > 0:
            axes[1, 1].scatter(valid_points['lon'], valid_points['lat'], 
                             alpha=0.6, s=8, c='blue', label='正常座標')
        if len(invalid_points) > 0:
            axes[1, 1].scatter(invalid_points['lon'], invalid_points['lat'], 
                             alpha=0.8, s=20, c='red', marker='x', label='問題座標')
        
        axes[1, 1].set_title('座標分布圖')
        axes[1, 1].set_xlabel('經度')
        axes[1, 1].set_ylabel('緯度')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('../outputs_HW2/縣市範圍座標驗證分析.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"📊 分析圖表已儲存: ../outputs_HW2/縣市範圍座標驗證分析.png")
    
    def generate_cleaned_data(self, df, validation_results):
        """生成清理後的資料"""
        results_df = pd.DataFrame(validation_results)
        
        # 只保留驗證通過的記錄
        valid_indices = results_df[results_df['is_valid']]['index']
        cleaned_df = df.iloc[valid_indices].copy()
        
        # 添加驗證狀態欄位
        cleaned_df['座標驗證狀態'] = '通過'
        
        # 保存清理後的資料
        cleaned_df.to_csv('../outputs_HW2/避難收容處所_縣市驗證清理後.csv', 
                         index=False, encoding='utf-8-sig')
        
        print(f"\n✅ 清理後資料已儲存: ../outputs_HW2/避難收容處所_縣市驗證清理後.csv")
        print(f"原始資料: {len(df)} 筆")
        print(f"清理後資料: {len(cleaned_df)} 筆")
        print(f"保留率: {len(cleaned_df)/len(df)*100:.2f}%")
        
        return cleaned_df
    
    def run_complete_validation(self):
        """執行完整的縣市範圍座標驗證"""
        try:
            # 載入資料
            df = pd.read_csv('../outputs_HW2/避難收容處所_清理後.csv')
            print(f"載入避難收容所資料: {len(df)} 筆")
            
            # 執行驗證
            validation_results = self.validate_coordinates_by_city(df)
            
            # 分析結果
            results_df, problem_shelters = self.analyze_validation_results(validation_results)
            
            # 顯示問題樣本
            self.create_problem_samples(problem_shelters)
            
            # 建立地圖
            self.create_validation_map(df, validation_results)
            
            # 建立分析圖表
            self.create_city_analysis_charts(validation_results)
            
            # 生成清理後資料
            cleaned_df = self.generate_cleaned_data(df, validation_results)
            
            # 生成詳細報告
            self.generate_detailed_report(results_df, problem_shelters)
            
            print("\n" + "=" * 60)
            print("✅ 縣市範圍座標驗證完成！")
            print("📁 產出檔案:")
            print("   - 縣市範圍座標驗證地圖.html")
            print("   - 縣市範圍座標驗證分析.png")
            print("   - 避難收容處所_縣市驗證清理後.csv")
            print("   - 縣市範圍座標驗證報告.txt")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ 驗證過程中發生錯誤: {e}")
    
    def generate_detailed_report(self, results_df, problem_shelters):
        """生成詳細報告"""
        report_content = f"""
縣市範圍座標驗證報告
=====================================

分析時間: {pd.Timestamp.now().strftime('%Y年%m月%d日 %H:%M:%S')}

📊 驗證結果統計
總筆數: {len(results_df)}
正常座標: {len(results_df[results_df['is_valid']])} 筆 ({len(results_df[results_df['is_valid']])/len(results_df)*100:.1f}%)
問題座標: {len(problem_shelters)} 筆 ({len(problem_shelters)/len(results_df)*100:.1f}%)

🔍 問題類型分析
{chr(10).join([f"  {status}: {count} 筆" for status, count in results_df['status'].value_counts().items()])}

🏢 問題點位縣市分布
{chr(10).join([f"  {city}: {count} 筆" for city, count in problem_shelters['city'].value_counts().head(10).items()]) if len(problem_shelters) > 0 else "  無問題點位"}

🎯 建議改善措施
1. 針對問題點位進行重新測量或座標校正
2. 建立縣市範圍的自動驗證機制
3. 定期更新座標資料以確保準確性
4. 建立座標資料品質監控系統

📁 輸出檔案
- 縣市範圍座標驗證地圖.html: 互動式驗證地圖
- 縣市範圍座標驗證分析.png: 統計分析圖表
- 避難收容處所_縣市驗證清理後.csv: 清理後資料
- 縣市範圍座標驗證報告.txt: 本統計報告
"""
        
        with open('../outputs_HW2/縣市範圍座標驗證報告.txt', 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📄 詳細報告已儲存: ../outputs_HW2/縣市範圍座標驗證報告.txt")

def main():
    """主函數"""
    validator = CityBasedValidator()
    validator.run_complete_validation()

if __name__ == "__main__":
    main()
