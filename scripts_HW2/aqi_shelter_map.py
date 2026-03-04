import pandas as pd
import folium
import numpy as np
from folium.plugins import MarkerCluster
import branca.colormap as cm

def load_aqi_data():
    """載入AQI資料"""
    try:
        # 載入正確的AQI資料檔案
        aqi_df = pd.read_csv('../outputs/all_aqi_data_20260225_111850.csv')
        print(f"✅ 成功載入AQI資料: {len(aqi_df)} 筆")
        
        # 檢查並標準化欄位名稱
        print(f"AQI資料欄位: {list(aqi_df.columns)}")
        
        # 確保必要的欄位存在
        required_cols = ['latitude', 'longitude', 'aqi']
        missing_cols = [col for col in required_cols if col not in aqi_df.columns]
        if missing_cols:
            print(f"❌ AQI資料缺少必要欄位: {missing_cols}")
            raise ValueError(f"缺少欄位: {missing_cols}")
        
        return aqi_df
        
    except FileNotFoundError:
        print("❌ 找不到AQI資料檔案，將使用模擬資料")
        # 建立模擬AQI資料
        np.random.seed(42)
        cities = ['台北市', '新北市', '桃園市', '台中市', '台南市', '高雄市', 
                 '基隆市', '新竹市', '嘉義市', '宜蘭縣', '新竹縣', '苗栗縣',
                 '彰化縣', '南投縣', '雲林縣', '嘉義縣', '屏東縣', '花蓮縣', '台東縣']
        
        # 台灣主要城市的大概經緯度
        city_coords = {
            '台北市': (25.0330, 121.5654),
            '新北市': (25.0173, 121.4663),
            '桃園市': (24.9936, 121.3009),
            '台中市': (24.1477, 120.6736),
            '台南市': (22.9999, 120.2269),
            '高雄市': (22.6273, 120.3014),
            '基隆市': (25.1276, 121.7392),
            '新竹市': (24.8138, 120.9675),
            '嘉義市': (23.4801, 120.4491),
            '宜蘭縣': (24.6917, 121.7709),
            '新竹縣': (24.6949, 121.0406),
            '苗栗縣': (24.3518, 120.8226),
            '彰化縣': (24.0766, 120.5435),
            '南投縣': (23.8381, 120.9847),
            '雲林縣': (23.6995, 120.4316),
            '嘉義縣': (23.4598, 120.2923),
            '屏東縣': (22.5495, 120.5403),
            '花蓮縣': (23.7571, 121.5682),
            '台東縣': (22.7560, 121.1466)
        }
        
        aqi_data = []
        for i, city in enumerate(cities):
            lat, lon = city_coords[city]
            # 在城市周圍添加一些隨機偏移
            lat += np.random.uniform(-0.1, 0.1)
            lon += np.random.uniform(-0.1, 0.1)
            
            # 生成AQI值 (0-300)
            aqi = np.random.randint(15, 180)
            
            aqi_data.append({
                'site_name': f'{city}測站{i%3+1}',
                'county': city,
                'latitude': lat,
                'longitude': lon,
                'aqi': aqi,
                'pm25': np.random.randint(10, 80),
                'pm10': np.random.randint(15, 120),
                'so2': np.random.uniform(1, 10),
                'co': np.random.uniform(0.1, 2.0),
                'o3': np.random.randint(20, 100),
                'no2': np.random.uniform(5, 40),
                'data_time': '2026-03-04 14:00:00'
            })
        
        aqi_df = pd.DataFrame(aqi_data)
        print(f"📊 建立模擬AQI資料: {len(aqi_df)} 筆")
        return aqi_df

def get_aqi_color(aqi_value):
    """根據AQI值回傳對應顏色"""
    if aqi_value <= 50:
        return '#00E400'  # 綠色 - 良好
    elif aqi_value <= 100:
        return '#FFFF00'  # 黃色 - 中等
    elif aqi_value <= 150:
        return '#FF7E00'  # 橙色 - 對敏感族群不健康
    elif aqi_value <= 200:
        return '#FF0000'  # 紅色 - 對所有族群不健康
    elif aqi_value <= 300:
        return '#8F3F97'  # 紫色 - 非常不健康
    else:
        return '#7E0023'  # 褐紅色 - 危害

def get_aqi_level(aqi_value):
    """根據AQI值回傳等級描述"""
    if aqi_value <= 50:
        return '良好'
    elif aqi_value <= 100:
        return '中等'
    elif aqi_value <= 150:
        return '對敏感族群不健康'
    elif aqi_value <= 200:
        return '對所有族群不健康'
    elif aqi_value <= 300:
        return '非常不健康'
    else:
        return '危害'

def create_aqi_shelter_map():
    """建立AQI與避難收容所的交集地圖"""
    
    print("=" * 60)
    print("建立AQI與避難收容所交集地圖")
    print("=" * 60)
    
    # 載入資料
    shelter_df = pd.read_csv('../outputs_HW2/避難收容處所_室內外分類.csv')
    aqi_df = load_aqi_data()
    
    print(f"避難收容所資料: {len(shelter_df)} 筆")
    print(f"AQI測站資料: {len(aqi_df)} 筆")
    
    # 計算地圖中心點
    all_lats = list(shelter_df['緯度']) + list(aqi_df['latitude'])
    all_lons = list(shelter_df['經度']) + list(aqi_df['longitude'])
    center_lat = sum(all_lats) / len(all_lats)
    center_lon = sum(all_lons) / len(all_lons)
    
    # 建立地圖
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=8,
        tiles='OpenStreetMap'
    )
    
    # 建立AQI顏色圖例
    aqi_colormap = cm.LinearColormap(
        colors=['#00E400', '#FFFF00', '#FF7E00', '#FF0000', '#8F3F97', '#7E0023'],
        index=[0, 50, 100, 150, 200, 300],
        vmin=0,
        vmax=300
    )
    aqi_colormap.caption = 'AQI 空氣品質指標'
    m.add_child(aqi_colormap)
    
    # 圖層 A: AQI測站
    print("\n📍 添加AQI測站圖層...")
    aqi_cluster = MarkerCluster(name='AQI測站').add_to(m)
    
    for idx, row in aqi_df.iterrows():
        color = get_aqi_color(row['aqi'])
        level = get_aqi_level(row['aqi'])
        
        popup_content = f"""
        <b>{row['site_name']}</b><br>
        縣市: {row['county']}<br>
        AQI: <span style="color:{color};font-weight:bold">{row['aqi']}</span> ({level})<br>
        PM2.5: {row['pm25']} μg/m³<br>
        PM10: {row['pm10']} μg/m³<br>
        SO₂: {row['so2']:.1f} ppb<br>
        CO: {row['co']:.1f} ppm<br>
        O₃: {row['o3']} ppb<br>
        NO₂: {row['no2']:.1f} ppb<br>
        更新時間: {row['data_time']}
        """
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=8,
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"{row['site_name']} (AQI: {row['aqi']})",
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        ).add_to(aqi_cluster)
    
    # 圖層 B: 避難收容所
    print("🏠 添加避難收容所圖層...")
    
    # 分離室內外收容所
    indoor_shelters = shelter_df[shelter_df['is_indoor'] == True]
    outdoor_shelters = shelter_df[shelter_df['is_indoor'] == False]
    
    print(f"室內收容所: {len(indoor_shelters)} 筆")
    print(f"室外收容所: {len(outdoor_shelters)} 筆")
    
    # 室內收容所圖層
    indoor_cluster = MarkerCluster(name='室內收容所').add_to(m)
    
    for idx, row in indoor_shelters.iterrows():
        capacity = row['預計收容人數'] if pd.notna(row['預計收容人數']) else '未知'
        
        popup_content = f"""
        <b>{row['避難收容處所名稱']}</b><br>
        📍 地址: {row['避難收容處所地址']}<br>
        🏢 縣市: {row['縣市及鄉鎮市區']}<br>
        👥 預計收容人數: {capacity} 人<br>
        🏠 類型: <span style="color:blue;font-weight:bold">室內設施</span><br>
        🎯 適用災害: {row['適用災害類別']}<br>
        📞 管理人: {row['管理人姓名']}<br>
        """
        
        folium.Marker(
            location=[row['緯度'], row['經度']],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=row['避難收容處所名稱'],
            icon=folium.Icon(
                color='blue',
                icon='home',
                prefix='fa'
            )
        ).add_to(indoor_cluster)
    
    # 室外收容所圖層
    outdoor_cluster = MarkerCluster(name='室外收容所').add_to(m)
    
    for idx, row in outdoor_shelters.iterrows():
        capacity = row['預計收容人數'] if pd.notna(row['預計收容人數']) else '未知'
        
        popup_content = f"""
        <b>{row['避難收容處所名稱']}</b><br>
        📍 地址: {row['避難收容處所地址']}<br>
        🏢 縣市: {row['縣市及鄉鎮市區']}<br>
        👥 預計收容人數: {capacity} 人<br>
        🌳 類型: <span style="color:green;font-weight:bold">室外設施</span><br>
        🎯 適用災害: {row['適用災害類別']}<br>
        📞 管理人: {row['管理人姓名']}<br>
        """
        
        folium.Marker(
            location=[row['緯度'], row['經度']],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=row['避難收容處所名稱'],
            icon=folium.Icon(
                color='green',
                icon='tree',
                prefix='fa'
            )
        ).add_to(outdoor_cluster)
    
    # 添加圖層控制
    folium.LayerControl().add_to(m)
    
    # 添加地圖標題和說明
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
        AQI空氣品質與避難收容所分布圖
    </div>
    '''
    
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 10px; 
                z-index: 1000; 
                background-color: white; 
                padding: 10px; 
                border: 2px solid grey; 
                border-radius: 5px;
                font-size: 12px;">
        <h4>圖例說明</h4>
        <div><i class="fa fa-home" style="color:blue"></i> 室內收容所</div>
        <div><i class="fa fa-tree" style="color:green"></i> 室外收容所</div>
        <div><span style="display:inline-block;width:12px;height:12px;background-color:#00E400;"></span> AQI 0-50 (良好)</div>
        <div><span style="display:inline-block;width:12px;height:12px;background-color:#FFFF00;"></span> AQI 51-100 (中等)</div>
        <div><span style="display:inline-block;width:12px;height:12px;background-color:#FF7E00;"></span> AQI 101-150 (敏感不健康)</div>
        <div><span style="display:inline-block;width:12px;height:12px;background-color:#FF0000;"></span> AQI 151-200 (不健康)</div>
        <div><span style="display:inline-block;width:12px;height:12px;background-color:#8F3F97;"></span> AQI 201-300 (非常不健康)</div>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(title_html))
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # 儲存地圖
    map_file = '../outputs_HW2/AQI_避難收容所交集地圖.html'
    m.save(map_file)
    
    print(f"\n✅ 地圖已儲存: {map_file}")
    
    # 生成統計報告
    generate_map_statistics(shelter_df, aqi_df)
    
    return m

def generate_map_statistics(shelter_df, aqi_df):
    """生成地圖統計報告"""
    
    print("\n" + "=" * 60)
    print("地圖統計報告")
    print("=" * 60)
    
    # AQI統計
    print(f"🌫️  AQI測站統計:")
    print(f"   總測站數: {len(aqi_df)}")
    aqi_stats = aqi_df['aqi'].describe()
    print(f"   平均AQI: {aqi_stats['mean']:.1f}")
    print(f"   最高AQI: {aqi_stats['max']}")
    print(f"   最低AQI: {aqi_stats['min']}")
    
    # AQI等級分布
    aqi_levels = aqi_df['aqi'].apply(get_aqi_level).value_counts()
    print(f"\n   AQI等級分布:")
    for level, count in aqi_levels.items():
        print(f"   {level}: {count} 筆")
    
    # 避難收容所統計
    print(f"\n🏠 避難收容所統計:")
    print(f"   總收容所數: {len(shelter_df)}")
    indoor_count = shelter_df['is_indoor'].sum()
    outdoor_count = len(shelter_df) - indoor_count
    print(f"   室內收容所: {indoor_count} ({indoor_count/len(shelter_df)*100:.1f}%)")
    print(f"   室外收容所: {outdoor_count} ({outdoor_count/len(shelter_df)*100:.1f}%)")
    
    # 收容能力統計
    capacity_data = pd.to_numeric(shelter_df['預計收容人數'], errors='coerce').dropna()
    if len(capacity_data) > 0:
        print(f"\n👥 收容能力統計:")
        print(f"   總收容容量: {capacity_data.sum():,} 人")
        print(f"   平均收容容量: {capacity_data.mean():.0f} 人")
        print(f"   最大收容容量: {capacity_data.max():,} 人")
        print(f"   有容量資料: {len(capacity_data)} 筆 ({len(capacity_data)/len(shelter_df)*100:.1f}%)")
    
    # 縣市分布
    print(f"\n📍 縣市分布 (前10名):")
    city_count = shelter_df['縣市及鄉鎮市區'].str.extract(r'([^縣市]+縣|[^縣市]+市)')[0].value_counts().head(10)
    for city, count in city_count.items():
        percentage = count / len(shelter_df) * 100
        print(f"   {city}: {count} 筆 ({percentage:.1f}%)")
    
    # 儲存統計報告
    report_content = f"""
AQI與避難收容所交集地圖統計報告
=====================================

分析時間: {pd.Timestamp.now().strftime('%Y年%m月%d日 %H:%M:%S')}

🌫️ AQI測站統計
總測站數: {len(aqi_df)}
平均AQI: {aqi_df['aqi'].mean():.1f}
最高AQI: {aqi_df['aqi'].max()}
最低AQI: {aqi_df['aqi'].min()}

AQI等級分布:
{chr(10).join([f'  {level}: {count} 筆' for level, count in aqi_levels.items()])}

🏠 避難收容所統計
總收容所數: {len(shelter_df)}
室內收容所: {indoor_count} ({indoor_count/len(shelter_df)*100:.1f}%)
室外收容所: {outdoor_count} ({outdoor_count/len(shelter_df)*100:.1f}%)

👥 收容能力統計
總收容容量: {capacity_data.sum():,} 人
平均收容容量: {capacity_data.mean():.0f} 人
最大收容容量: {capacity_data.max():,} 人
有容量資料: {len(capacity_data)} 筆 ({len(capacity_data)/len(shelter_df)*100:.1f}%)

📍 縣市分布 (前10名)
{chr(10).join([f'  {city}: {count} 筆 ({count/len(shelter_df)*100:.1f}%)' for city, count in city_count.items()])}

📁 輸出檔案
- AQI_避難收容所交集地圖.html: 互動式地圖
- AQI_避難收容所統計報告.txt: 本統計報告
"""
    
    with open('../outputs_HW2/AQI_避難收容所統計報告.txt', 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n📄 統計報告已儲存: ../outputs_HW2/AQI_避難收容所統計報告.txt")

def main():
    """主函數"""
    try:
        m = create_aqi_shelter_map()
        
        print("\n" + "=" * 60)
        print("✅ AQI與避難收容所交集地圖建立完成！")
        print("📁 產出檔案:")
        print("   - outputs_HW2/AQI_避難收容所交集地圖.html")
        print("   - outputs_HW2/AQI_避難收容所統計報告.txt")
        print("\n🌐 使用說明:")
        print("   1. 用瀏覽器開啟HTML檔案查看互動式地圖")
        print("   2. 可點擊圖層控制開關不同圖層")
        print("   3. 點擊標記查看詳細資訊")
        print("   4. AQI測站以圓形顯示，顏色代表污染程度")
        print("   5. 收容所以圖標顯示，藍色為室內，綠色為室外")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 建立地圖過程中發生錯誤: {e}")

if __name__ == "__main__":
    main()
