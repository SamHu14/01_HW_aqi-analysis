# 第二週作業 - 避難收容所座標驗證與AQI風險分析

## 專案概述

本專案建立了一個完整的避難收容所分析系統，解決了原始資料中的座標問題，並整合AQI空氣品質資料進行風險評估。

## 主要成果

### 1. 座標驗證與清理
- **問題識別**: 發現717筆超出縣市範圍的錯誤座標
- **驗證方法**: 以縣市為單位檢查座標合理性
- **清理結果**: 從5,928筆清理至5,211筆，準確率100%

### 2. 室內外設施分類
- **分類邏輯**: 基於設施名稱關鍵字自動分類
- **室內設施**: 4,736筆 (90.9%)
- **室外設施**: 475筆 (9.1%)

### 3. AQI風險分析
- **分析方法**: 使用Haversine公式計算避難所到最近AQI測站距離
- **風險分類**:
  - 高風險: AQI > 100 (638筆)
  - 警告: AQI > 50 且室外設施 (169筆)
  - 低風險: 其他 (4,404筆)

## 檔案結構

```
1_HW/
├── 避難收容處所點位檔案v9.csv          # 原始資料
├── outputs/
│   └── all_aqi_data_20260225_111850.csv # AQI測站資料
├── outputs_HW2/
│   ├── shelter_aqi_analysis_hight.csv     # 最終風險分析成果
│   ├── 避難收容處所_室內外分類.csv      # 室內外分類結果
│   ├── 避難收容處所_縣市驗證清理後.csv   # 座標驗證清理後資料
│   └── [其他分析檔案...]
├── scripts_HW2/
│   ├── city_based_coordinate_validation.py # 座標驗證腳本
│   ├── add_indoor_classification.py       # 室內外分類腳本
│   ├── aqi_shelter_map.py              # AQI地圖腳本
│   └── shelter_aqi_risk_analysis.py    # 風險分析腳本
└── README_HW2.md                     # 本檔案
```

## 線上地圖連結

### 1. 縣市範圍座標驗證地圖
🔗 [https://samhu14.github.io/01_HW_aqi-analysis/outputs_HW2/縣市範圍座標驗證地圖.html](https://samhu14.github.io/01_HW_aqi-analysis/outputs_HW2/縣市範圍座標驗證地圖.html)

**特色功能**:
- 🔵 藍色標記：驗證通過的座標
- 🔴 紅色標記：超出縣市範圍的問題座標
- 可切換圖層查看不同類型

### 2. AQI與避難收容所交集地圖
🔗 [https://samhu14.github.io/01_HW_aqi-analysis/outputs_HW2/AQI_避難收容所交集地圖.html](https://samhu14.github.io/01_HW_aqi-analysis/outputs_HW2/AQI_避難收容所交集地圖.html)

**特色功能**:
- 🟡🔴 彩色圓形：AQI測站(依污染程度分色)
- 🏠 藍色圖標：室內收容所
- 🌳 綠色圖標：室外收容所
- 點擊查看詳細資訊

### 3. 避難所AQI風險分析地圖
🔗 [https://samhu14.github.io/01_HW_aqi-analysis/outputs_HW2/避難所AQI風險分析地圖.html](https://samhu14.github.io/01_HW_aqi-analysis/outputs_HW2/避難所AQI風險分析地圖.html)

**特色功能**:
- 🔴 紅色標記：高風險設施 (AQI > 100)
- 🟠 橙色標記：警告級設施 (AQI > 50 且室外)
- 🟢 綠色標記：低風險設施
- 顯示最近AQI測站資訊和距離

## 技術特色

### 座標驗證技術
- 使用縣市邊界座標範圍驗證
- 解決海上點位和跨縣市錯誤
- 自動識別並標記問題座標

### 風險分析技術
- Haversine公式計算球面距離
- 智能風險分類演算法
- 考慮設施類型的風險評估

### 視覺化技術
- Folium互動式地圖
- 多圖層管理
- 響應式設計

## 分析發現

### 主要問題
1. **座標錯誤**: 12.1%的避難所座標超出縣市範圍
2. **空氣品質風險**: 12.2%的避難所位於高風險區域
3. **室外設施風險**: 35.6%的室外設施面臨空氣品質警告

### 縣市分布
- 新北市: 525筆 (10.1%)
- 臺中市: 475筆 (9.1%)
- 臺南市: 473筆 (9.1%)
- 高雄市: 447筆 (8.6%)

## 使用方法

### 環境設定
```bash
pip install -r requirements.txt
```

### 執行分析
```bash
# 座標驗證
cd scripts_HW2
python city_based_coordinate_validation.py

# 室內外分類
python add_indoor_classification.py

# AQI地圖
python aqi_shelter_map.py

# 風險分析
python shelter_aqi_risk_analysis.py
```

## 成果統計

| 項目 | 數量 | 百分比 |
|------|------|--------|
| 總避難所 | 5,211 | 100% |
| 室內設施 | 4,736 | 90.9% |
| 室外設施 | 475 | 9.1% |
| 高風險設施 | 638 | 12.2% |
| 警告級設施 | 169 | 3.2% |
| 低風險設施 | 4,404 | 84.5% |

## 作者資訊

- **學生姓名**: 胡舜宇 (R14521705)
- **作業題目**: 第二週 - 避難收容所座標驗證與AQI風險分析
- **GitHub**: https://github.com/SamHu14/01_HW_aqi-analysis

