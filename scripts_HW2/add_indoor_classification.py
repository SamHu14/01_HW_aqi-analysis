import pandas as pd
import re

def classify_indoor_facilities():
    """根據設施名稱分類室內外收容所"""
    
    # 載入重新清理後的資料
    df = pd.read_csv('../outputs_HW2/避難收容處所_縣市驗證清理後.csv')
    
    print("=" * 60)
    print("室內外設施分類分析")
    print("=" * 60)
    print(f"原始資料筆數: {len(df)}")
    
    # 定義室外設施關鍵字 (更精確的定義，排除可能誤判的詞彙)
    outdoor_keywords = [
        '公園', '廣場', '操場', '運動場', '球場',
        '河濱公園', '森林公園', '兒童公園',
        '臨時停車場', '露天廣場', '戶外廣場',
        '營地', '露營區', '戶外',
        '海灘', '沙灘', '河濱',
        '登山口', '步道',
        '橋下', '高架下', '地下道'
    ]
    
    # 定義強制室內關鍵字 (優先級最高)
    strong_indoor_keywords = [
        '學校', '國小', '國中', '高中', '大學', '校',
        '教室', '禮堂', '圖書館', '體育館',
        '活動中心', '社區活動中心', '里民活動中心', '集會所',
        '辦公處', '公所', '鄉公所', '鎮公所', '市公所', '區公所',
        '村里辦公處', '村辦公處', '里辦公處',
        '醫院', '診所', '衛生所',
        '市場', '超市', '百貨',
        '旅館', '飯店', '招待所',
        '倉庫', '車庫', '室內停車場'
    ]
    
    # 初始化 is_indoor 欄位
    df['is_indoor'] = True  # 預設為室內
    
    # 根據設施名稱判斷 (修正邏輯)
    facility_classifications = []
    
    for idx, row in df.iterrows():
        facility_name = str(row['避難收容處所名稱']).strip()
        is_indoor = True  # 預設室內
        classification_reason = "預設室內"
        
        # 優先檢查強制室內關鍵字 (學校、活動中心等)
        for keyword in strong_indoor_keywords:
            if keyword in facility_name:
                is_indoor = True
                classification_reason = f"包含強制室內關鍵字: {keyword}"
                break
        
        # 如果不是強制室內，再檢查室外關鍵字
        if is_indoor:  # 只有在沒有被強制室內判定時才檢查室外
            for keyword in outdoor_keywords:
                if keyword in facility_name:
                    is_indoor = False
                    classification_reason = f"包含室外關鍵字: {keyword}"
                    break
        
        # 特殊規則處理
        if '停車場' in facility_name and '室內' not in facility_name:
            is_indoor = False
            classification_reason = "停車場預設為室外"
        elif '臨時' in facility_name and ('廣場' in facility_name or '公園' in facility_name):
            is_indoor = False
            classification_reason = "臨時廣場/公園為室外"
        elif '操場' in facility_name and '室內' not in facility_name:
            is_indoor = False
            classification_reason = "操場預設為室外"
        
        facility_classifications.append({
            '序號': row['序號'],
            '設施名稱': facility_name,
            'is_indoor': is_indoor,
            '分類原因': classification_reason
        })
        
        df.loc[idx, 'is_indoor'] = is_indoor
    
    # 統計結果
    indoor_count = df['is_indoor'].sum()
    outdoor_count = len(df) - indoor_count
    
    print(f"\n📊 分類結果統計:")
    print(f"室內設施: {indoor_count} 筆 ({indoor_count/len(df)*100:.1f}%)")
    print(f"室外設施: {outdoor_count} 筆 ({outdoor_count/len(df)*100:.1f}%)")
    
    # 顯示分類樣本
    print(f"\n🏠 室內設施樣本 (前10筆):")
    indoor_samples = df[df['is_indoor'] == True]['避難收容處所名稱'].head(10)
    for i, name in enumerate(indoor_samples, 1):
        print(f"  {i}. {name}")
    
    print(f"\n🌳 室外設施樣本 (前10筆):")
    outdoor_samples = df[df['is_indoor'] == False]['避難收容處所名稱'].head(10)
    for i, name in enumerate(outdoor_samples, 1):
        print(f"  {i}. {name}")
    
    # 按縣市統計室內外分布
    print(f"\n📍 各縣市室內外設施分布:")
    city_stats = []
    for city in df['縣市及鄉鎮市區'].str.extract(r'([^縣市]+縣|[^縣市]+市)')[0].unique():
        if pd.notna(city):
            city_data = df[df['縣市及鄉鎮市區'].str.contains(city, na=False)]
            city_indoor = city_data['is_indoor'].sum()
            city_total = len(city_data)
            city_outdoor = city_total - city_indoor
            city_stats.append({
                '縣市': city,
                '總數': city_total,
                '室內': city_indoor,
                '室外': city_outdoor,
                '室內比例': city_indoor/city_total*100
            })
    
    city_stats_df = pd.DataFrame(city_stats).sort_values('總數', ascending=False)
    print("縣市\t總數\t室內\t室外\t室內比例")
    print("-" * 50)
    for _, row in city_stats_df.head(10).iterrows():
        print(f"{row['縣市']}\t{row['總數']}\t{row['室內']}\t{row['室外']}\t{row['室內比例']:.1f}%")
    
    # 設施類型分析
    print(f"\n🏢 設施類型分析:")
    
    # 學校類
    school_keywords = ['學校', '國小', '國中', '高中', '大學']
    schools = df[df['避難收容處所名稱'].str.contains('|'.join(school_keywords), na=False)]
    print(f"學校類設施: {len(schools)} 筆 (室內: {schools['is_indoor'].sum()} 筆)")
    
    # 活動中心類
    activity_centers = df[df['避難收容處所名稱'].str.contains('活動中心', na=False)]
    print(f"活動中心類設施: {len(activity_centers)} 筆 (室內: {activity_centers['is_indoor'].sum()} 筆)")
    
    # 公園廣場類
    parks = df[df['避難收容處所名稱'].str.contains('公園|廣場', na=False)]
    print(f"公園廣場類設施: {len(parks)} 筆 (室內: {parks['is_indoor'].sum()} 筆)")
    
    # 政府機關類
    gov_offices = df[df['避難收容處所名稱'].str.contains('公所|辦公處', na=False)]
    print(f"政府機關類設施: {len(gov_offices)} 筆 (室內: {gov_offices['is_indoor'].sum()} 筆)")
    
    # 儲存更新後的資料
    df.to_csv('../outputs_HW2/避難收容處所_室內外分類.csv', index=False, encoding='utf-8-sig')
    
    # 儲存分類詳細報告
    classification_df = pd.DataFrame(facility_classifications)
    classification_df.to_csv('../outputs_HW2/室內外分類詳細報告.csv', index=False, encoding='utf-8-sig')
    
    print(f"\n✅ 分類完成！")
    print(f"📁 已儲存檔案:")
    print(f"   - outputs_HW2/避難收容處所_室內外分類.csv (新增 is_indoor 欄位)")
    print(f"   - outputs_HW2/室內外分類詳細報告.csv (分類原因詳細說明)")
    
    return df

def create_indoor_visualization(df):
    """創建室內外分布視覺化"""
    
    import matplotlib.pyplot as plt
    
    # 設定中文字體
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('避難收容所室內外設施分析', fontsize=16, fontweight='bold')
    
    # 1. 整體室內外分布圓餅圖
    indoor_count = df['is_indoor'].sum()
    outdoor_count = len(df) - indoor_count
    
    axes[0, 0].pie([indoor_count, outdoor_count], 
                   labels=['室內設施', '室外設施'],
                   colors=['lightblue', 'lightgreen'],
                   autopct='%1.1f%%',
                   startangle=90)
    axes[0, 0].set_title('整體室內外分布')
    
    # 2. 各縣市室內外比例
    city_stats = []
    for city in df['縣市及鄉鎮市區'].str.extract(r'([^縣市]+縣|[^縣市]+市)')[0].unique():
        if pd.notna(city):
            city_data = df[df['縣市及鄉鎮市區'].str.contains(city, na=False)]
            city_indoor = city_data['is_indoor'].sum()
            city_total = len(city_data)
            city_stats.append({
                '縣市': city,
                '室內比例': city_indoor/city_total*100,
                '總數': city_total
            })
    
    city_stats_df = pd.DataFrame(city_stats).sort_values('總數', ascending=False).head(10)
    
    axes[0, 1].barh(range(len(city_stats_df)), city_stats_df['室內比例'], 
                     color='skyblue')
    axes[0, 1].set_yticks(range(len(city_stats_df)))
    axes[0, 1].set_yticklabels(city_stats_df['縣市'])
    axes[0, 1].set_title('各縣市室內設施比例 (前10名)')
    axes[0, 1].set_xlabel('室內設施比例 (%)')
    axes[0, 1].set_xlim(0, 100)
    
    # 3. 設施類型分布
    facility_types = []
    
    # 學校
    schools = df[df['避難收容處所名稱'].str.contains('學校|國小|國中|高中', na=False)]
    facility_types.append(('學校', len(schools)))
    
    # 活動中心
    activity_centers = df[df['避難收容處所名稱'].str.contains('活動中心', na=False)]
    facility_types.append(('活動中心', len(activity_centers)))
    
    # 公園廣場
    parks = df[df['避難收容處所名稱'].str.contains('公園|廣場', na=False)]
    facility_types.append(('公園廣場', len(parks)))
    
    # 政府機關
    gov_offices = df[df['避難收容處所名稱'].str.contains('公所|辦公處', na=False)]
    facility_types.append(('政府機關', len(gov_offices)))
    
    # 其他
    others_count = len(df) - sum(count for _, count in facility_types)
    facility_types.append(('其他', others_count))
    
    labels, counts = zip(*facility_types)
    axes[1, 0].bar(labels, counts, color='lightcoral')
    axes[1, 0].set_title('設施類型分布')
    axes[1, 0].set_ylabel('數量')
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # 4. 室內外設施地理分布
    indoor_data = df[df['is_indoor'] == True]
    outdoor_data = df[df['is_indoor'] == False]
    
    axes[1, 1].scatter(indoor_data['經度'], indoor_data['緯度'], 
                       alpha=0.6, s=8, c='blue', label='室內設施')
    axes[1, 1].scatter(outdoor_data['經度'], outdoor_data['緯度'], 
                       alpha=0.8, s=15, c='red', marker='^', label='室外設施')
    axes[1, 1].set_title('室內外設施地理分布')
    axes[1, 1].set_xlabel('經度')
    axes[1, 1].set_ylabel('緯度')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('../outputs_HW2/室內外設施分析圖.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"📊 視覺化圖表已儲存: ../outputs_HW2/室內外設施分析圖.png")

def main():
    """主函數"""
    try:
        df = classify_indoor_facilities()
        create_indoor_visualization(df)
        
        print(f"\n" + "=" * 60)
        print("✅ 室內外分類分析完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 分析過程中發生錯誤: {e}")

if __name__ == "__main__":
    main()
