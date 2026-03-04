import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import folium
from folium.plugins import MarkerCluster
import matplotlib.pyplot as plt
import seaborn as sns

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

class ShelterAQIRiskAnalyzer:
    def __init__(self):
        """初始化避難所AQI風險分析器"""
        pass
    
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """
        使用Haversine公式計算兩點之間的距離(公里)
        """
        # 將經緯度轉換為弧度
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine公式
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        # 地球半徑(公里)
        R = 6371.0
        distance = R * c
        
        return distance
    
    def find_nearest_aqi_station(self, shelter_lat, shelter_lon, aqi_df):
        """
        找到離避難所最近的AQI測站
        """
        min_distance = float('inf')
        nearest_station = None
        
        for _, station in aqi_df.iterrows():
            distance = self.haversine_distance(
                shelter_lat, shelter_lon,
                station['latitude'], station['longitude']
            )
            
            if distance < min_distance:
                min_distance = distance
                nearest_station = station.copy()
                nearest_station['distance_to_shelter'] = distance
        
        return nearest_station
    
    def classify_risk(self, aqi_value, is_indoor):
        """
        根據AQI值和設施類型分類風險等級
        """
        if aqi_value > 100:
            return "High Risk", "高風險"
        elif aqi_value > 50 and not is_indoor:
            return "Warning", "警告"
        else:
            return "Low Risk", "低風險"
    
    def analyze_shelter_aqi_risk(self):
        """
        執行避難所AQI風險分析
        """
        print("=" * 60)
        print("避難所AQI風險分析")
        print("=" * 60)
        
        # 載入資料
        shelter_df = pd.read_csv('../outputs_HW2/避難收容處所_室內外分類.csv')
        aqi_df = pd.read_csv('../outputs/all_aqi_data_20260225_111850.csv')
        
        print(f"載入避難收容所: {len(shelter_df)} 筆")
        print(f"載入AQI測站: {len(aqi_df)} 筆")
        
        # 為每個避難所找到最近的AQI測站
        analysis_results = []
        
        print("\n📍 正在計算每個避難所到最近AQI測站的距離...")
        
        for idx, shelter in shelter_df.iterrows():
            nearest_station = self.find_nearest_aqi_station(
                shelter['緯度'], shelter['經度'], aqi_df
            )
            
            if nearest_station is not None:
                # 分類風險
                risk_en, risk_zh = self.classify_risk(
                    nearest_station['aqi'], shelter['is_indoor']
                )
                
                result = {
                    '序號': shelter['序號'],
                    '避難收容處所名稱': shelter['避難收容處所名稱'],
                    '縣市及鄉鎮市區': shelter['縣市及鄉鎮市區'],
                    '地址': shelter['避難收容處所地址'],
                    '緯度': shelter['緯度'],
                    '經度': shelter['經度'],
                    '預計收容人數': shelter['預計收容人數'],
                    'is_indoor': shelter['is_indoor'],
                    '最近AQI測站名稱': nearest_station['site_name'],
                    '測站縣市': nearest_station['county'],
                    '測站AQI值': nearest_station['aqi'],
                    '測站距離(km)': round(nearest_station['distance_to_shelter'], 2),
                    '風險等級(英文)': risk_en,
                    '風險等級(中文)': risk_zh
                }
                
                analysis_results.append(result)
        
        results_df = pd.DataFrame(analysis_results)
        
        print(f"✅ 完成 {len(results_df)} 個避難所的風險分析")
        
        return results_df
    
    def analyze_risk_statistics(self, results_df):
        """
        分析風險統計
        """
        print("\n" + "=" * 60)
        print("風險分析統計")
        print("=" * 60)
        
        # 整體風險分布
        risk_counts = results_df['風險等級(中文)'].value_counts()
        print(f"📊 風險等級分布:")
        for risk, count in risk_counts.items():
            percentage = count / len(results_df) * 100
            print(f"  {risk}: {count} 筆 ({percentage:.1f}%)")
        
        # 室內外設施風險分布
        print(f"\n🏠 室內設施風險分布:")
        indoor_df = results_df[results_df['is_indoor'] == True]
        indoor_risk = indoor_df['風險等級(中文)'].value_counts()
        for risk, count in indoor_risk.items():
            percentage = count / len(indoor_df) * 100
            print(f"  {risk}: {count} 筆 ({percentage:.1f}%)")
        
        print(f"\n🌳 室外設施風險分布:")
        outdoor_df = results_df[results_df['is_indoor'] == False]
        outdoor_risk = outdoor_df['風險等級(中文)'].value_counts()
        for risk, count in outdoor_risk.items():
            percentage = count / len(outdoor_df) * 100
            print(f"  {risk}: {count} 筆 ({percentage:.1f}%)")
        
        # 高風險設施統計
        high_risk_df = results_df[results_df['風險等級(中文)'] == '高風險']
        print(f"\n🚨 高風險設施統計:")
        print(f"  總數: {len(high_risk_df)} 筆")
        print(f"  室內高風險: {len(high_risk_df[high_risk_df['is_indoor']])} 筆")
        print(f"  室外高風險: {len(high_risk_df[~high_risk_df['is_indoor']])} 筆")
        
        # 警告級設施統計
        warning_df = results_df[results_df['風險等級(中文)'] == '警告']
        print(f"\n⚠️ 警告級設施統計:")
        print(f"  總數: {len(warning_df)} 筆")
        print(f"  室內警告: {len(warning_df[warning_df['is_indoor']])} 筆")
        print(f"  室外警告: {len(warning_df[~warning_df['is_indoor']])} 筆")
        
        return risk_counts, indoor_risk, outdoor_risk
    
    def show_risk_samples(self, results_df, num_samples=10):
        """
        顯示各風險等級的樣本
        """
        print(f"\n🚨 高風險設施樣本 (前{num_samples}筆):")
        print("名稱\t\t\t\tAQI\t距離\t風險")
        print("-" * 80)
        
        high_risk = results_df[results_df['風險等級(中文)'] == '高風險'].head(num_samples)
        for _, row in high_risk.iterrows():
            name = row['避難收容處所名稱'][:15] + "..." if len(row['避難收容處所名稱']) > 15 else row['避難收容處所名稱']
            print(f"{name:<20}\t{row['測站AQI值']}\t{row['測站距離(km)']}km\t{row['風險等級(中文)']}")
        
        print(f"\n⚠️ 警告級設施樣本 (前{num_samples}筆):")
        warning_risk = results_df[results_df['風險等級(中文)'] == '警告'].head(num_samples)
        for _, row in warning_risk.iterrows():
            name = row['避難收容處所名稱'][:15] + "..." if len(row['避難收容處所名稱']) > 15 else row['避難收容處所名稱']
            print(f"{name:<20}\t{row['測站AQI值']}\t{row['測站距離(km)']}km\t{row['風險等級(中文)']}")
    
    def create_risk_analysis_map(self, results_df):
        """
        建立風險分析地圖
        """
        print("\n📍 建立風險分析地圖...")
        
        # 計算地圖中心點
        center_lat = results_df['緯度'].mean()
        center_lon = results_df['經度'].mean()
        
        # 建立地圖
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=8,
            tiles='OpenStreetMap'
        )
        
        # 建立不同風險等級的圖層
        high_risk_cluster = MarkerCluster(name='高風險設施').add_to(m)
        warning_cluster = MarkerCluster(name='警告級設施').add_to(m)
        low_risk_cluster = MarkerCluster(name='低風險設施').add_to(m)
        
        # 高風險設施 (紅色)
        high_risk_df = results_df[results_df['風險等級(中文)'] == '高風險']
        for _, row in high_risk_df.iterrows():
            facility_type = "室內" if row['is_indoor'] else "室外"
            
            popup_content = f"""
            <b>{row['避難收容處所名稱']}</b><br>
            📍 {row['縣市及鄉鎮市區']}<br>
            🏢 設施類型: {facility_type}<br>
            👥 收容人數: {row['預計收容人數']} 人<br>
            🌫️ 最近測站: {row['最近AQI測站名稱']}<br>
            📊 AQI值: <span style="color:red;font-weight:bold">{row['測站AQI值']}</span><br>
            📏 距離: {row['測站距離(km)']} km<br>
            ⚠️ 風險等級: <span style="color:red;font-weight:bold">{row['風險等級(中文)']}</span>
            """
            
            folium.Marker(
                location=[row['緯度'], row['經度']],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=f"{row['避難收容處所名稱']} (高風險)",
                icon=folium.Icon(color='red', icon='exclamation-triangle', prefix='fa')
            ).add_to(high_risk_cluster)
        
        # 警告級設施 (橙色)
        warning_df = results_df[results_df['風險等級(中文)'] == '警告']
        for _, row in warning_df.iterrows():
            facility_type = "室內" if row['is_indoor'] else "室外"
            
            popup_content = f"""
            <b>{row['避難收容處所名稱']}</b><br>
            📍 {row['縣市及鄉鎮市區']}<br>
            🏢 設施類型: {facility_type}<br>
            👥 收容人數: {row['預計收容人數']} 人<br>
            🌫️ 最近測站: {row['最近AQI測站名稱']}<br>
            📊 AQI值: <span style="color:orange;font-weight:bold">{row['測站AQI值']}</span><br>
            📏 距離: {row['測站距離(km)']} km<br>
            ⚠️ 風險等級: <span style="color:orange;font-weight:bold">{row['風險等級(中文)']}</span>
            """
            
            folium.Marker(
                location=[row['緯度'], row['經度']],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=f"{row['避難收容處所名稱']} (警告)",
                icon=folium.Icon(color='orange', icon='warning', prefix='fa')
            ).add_to(warning_cluster)
        
        # 低風險設施 (綠色)
        low_risk_df = results_df[results_df['風險等級(中文)'] == '低風險']
        for _, row in low_risk_df.iterrows():
            facility_type = "室內" if row['is_indoor'] else "室外"
            
            popup_content = f"""
            <b>{row['避難收容處所名稱']}</b><br>
            📍 {row['縣市及鄉鎮市區']}<br>
            🏢 設施類型: {facility_type}<br>
            👥 收容人數: {row['預計收容人數']} 人<br>
            🌫️ 最近測站: {row['最近AQI測站名稱']}<br>
            📊 AQI值: <span style="color:green;font-weight:bold">{row['測站AQI值']}</span><br>
            📏 距離: {row['測站距離(km)']} km<br>
            ✅ 風險等級: <span style="color:green;font-weight:bold">{row['風險等級(中文)']}</span>
            """
            
            folium.Marker(
                location=[row['緯度'], row['經度']],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=f"{row['避難收容處所名稱']} (低風險)",
                icon=folium.Icon(color='green', icon='check', prefix='fa')
            ).add_to(low_risk_cluster)
        
        # 添加圖層控制
        folium.LayerControl().add_to(m)
        
        # 添加地圖標題
        title_html = '''
        <div style="position: fixed; 
                    top: 10px; left: 50%; 
                    transform: translateX(-50%); 
                    z-index: 1000; 
                    background-color: white; 
                    padding: 10px; 
                    border: 2px solid grey; 
                    border-radius: 5px;
                    font-size: 16px;
                    font-weight: bold;">
            避難所AQI風險分析地圖
        </div>
        '''
        
        # 添加圖例
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 10px; 
                    z-index: 1000; 
                    background-color: white; 
                    padding: 10px; 
                    border: 2px solid grey; 
                    border-radius: 5px;
                    font-size: 12px;">
            <h4>風險等級圖例</h4>
            <div><i class="fa fa-exclamation-triangle" style="color:red"></i> 高風險 (AQI > 100)</div>
            <div><i class="fa fa-warning" style="color:orange"></i> 警告 (AQI > 50 且室外)</div>
            <div><i class="fa fa-check" style="color:green"></i> 低風險</div>
        </div>
        '''
        
        m.get_root().html.add_child(folium.Element(title_html))
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # 儲存地圖
        map_file = '../outputs_HW2/避難所AQI風險分析地圖.html'
        m.save(map_file)
        print(f"✅ 風險分析地圖已儲存: {map_file}")
        
        return m
    
    def create_risk_charts(self, results_df, risk_counts, indoor_risk, outdoor_risk):
        """
        建立風險分析圖表
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('避難所AQI風險分析', fontsize=16, fontweight='bold')
        
        # 1. 整體風險分布
        axes[0, 0].pie(risk_counts.values, labels=risk_counts.index, autopct='%1.1f%%', 
                     colors=['red', 'orange', 'green'])
        axes[0, 0].set_title('整體風險分布')
        
        # 2. 室內設施風險分布
        if len(indoor_risk) > 0:
            axes[0, 1].pie(indoor_risk.values, labels=indoor_risk.index, autopct='%1.1f%%',
                         colors=['green', 'orange', 'red'])
        axes[0, 1].set_title('室內設施風險分布')
        
        # 3. 室外設施風險分布
        if len(outdoor_risk) > 0:
            axes[1, 0].pie(outdoor_risk.values, labels=outdoor_risk.index, autopct='%1.1f%%',
                         colors=['green', 'orange', 'red'])
        axes[1, 0].set_title('室外設施風險分布')
        
        # 4. AQI值分布
        axes[1, 1].hist(results_df['測站AQI值'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        axes[1, 1].axvline(x=50, color='orange', linestyle='--', label='警告閾值 (50)')
        axes[1, 1].axvline(x=100, color='red', linestyle='--', label='高風險閾值 (100)')
        axes[1, 1].set_xlabel('AQI值')
        axes[1, 1].set_ylabel('設施數量')
        axes[1, 1].set_title('AQI值分布')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('../outputs_HW2/避難所AQI風險分析圖.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"📊 風險分析圖表已儲存: ../outputs_HW2/避難所AQI風險分析圖.png")
    
    def generate_risk_report(self, results_df):
        """
        生成風險分析報告
        """
        report_content = f"""
避難所AQI風險分析報告
=====================================

分析時間: {pd.Timestamp.now().strftime('%Y年%m月%d日 %H:%M:%S')}

📊 分析概要
總避難所數量: {len(results_df)}
分析基準: 使用Haversine公式計算最近AQI測站距離

🎯 風險分類標準
- 高風險: 最近AQI測站值 > 100
- 警告: 最近AQI測站值 > 50 且設施為室外
- 低風險: 其他情況

📈 風險統計結果
{chr(10).join([f"  {risk}: {count} 筆 ({count/len(results_df)*100:.1f}%)" for risk, count in results_df['風險等級(中文)'].value_counts().items()])}

🏠 室內設施風險分布
{chr(10).join([f"  {risk}: {count} 筆" for risk, count in results_df[results_df['is_indoor']]['風險等級(中文)'].value_counts().items()])}

🌳 室外設施風險分布
{chr(10).join([f"  {risk}: {count} 筆" for risk, count in results_df[~results_df['is_indoor']]['風險等級(中文)'].value_counts().items()])}

📏 距離統計
平均距離: {results_df['測站距離(km)'].mean():.2f} km
最遠距離: {results_df['測站距離(km)'].max():.2f} km
最近距離: {results_df['測站距離(km)'].min():.2f} km

🎯 建議措施
1. 高風險設施應考慮空氣淨化設備
2. 室外設施在空氣品質不佳時應轉移至室內
3. 建立AQI監控預警系統
4. 定期更新避難所空氣品質評估

📁 輸出檔案
- shelter_aqi_analysis_hight.csv: 詳細分析結果
- 避難所AQI風險分析地圖.html: 互動式地圖
- 避難所AQI風險分析圖.png: 統計圖表
- 避難所AQI風險分析報告.txt: 本報告
"""
        
        with open('../outputs_HW2/避難所AQI風險分析報告.txt', 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📄 風險分析報告已儲存: ../outputs_HW2/避難所AQI風險分析報告.txt")
    
    def run_complete_analysis(self):
        """
        執行完整的風險分析
        """
        try:
            # 執行風險分析
            results_df = self.analyze_shelter_aqi_risk()
            
            # 分析統計
            risk_counts, indoor_risk, outdoor_risk = self.analyze_risk_statistics(results_df)
            
            # 顯示樣本
            self.show_risk_samples(results_df)
            
            # 建立地圖
            self.create_risk_analysis_map(results_df)
            
            # 建立圖表
            self.create_risk_charts(results_df, risk_counts, indoor_risk, outdoor_risk)
            
            # 儲存結果
            results_df.to_csv('../outputs_HW2/shelter_aqi_analysis_hight.csv', 
                            index=False, encoding='utf-8-sig')
            print(f"\n💾 分析結果已儲存: ../outputs_HW2/shelter_aqi_analysis_hight.csv")
            
            # 生成報告
            self.generate_risk_report(results_df)
            
            print("\n" + "=" * 60)
            print("✅ 避難所AQI風險分析完成！")
            print("📁 產出檔案:")
            print("   - shelter_aqi_analysis_hight.csv")
            print("   - 避難所AQI風險分析地圖.html")
            print("   - 避難所AQI風險分析圖.png")
            print("   - 避難所AQI風險分析報告.txt")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ 分析過程中發生錯誤: {e}")

def main():
    """主函數"""
    analyzer = ShelterAQIRiskAnalyzer()
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()
