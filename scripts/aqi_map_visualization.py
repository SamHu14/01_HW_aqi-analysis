#!/usr/bin/env python3
"""
AQI Map Visualization using Folium
Creates an interactive map showing all AQI monitoring stations with color-coded AQI values
"""

import os
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import json
from datetime import datetime

class AQIMapVisualizer:
    def __init__(self):
        self.aqi_colors = {
            'good': '#00E400',        # 綠色 0-50
            'moderate': '#FFFF00',    # 黃色 51-100
            'unhealthy_sensitive': '#FF7E00',  # 橙色 101-150
            'unhealthy': '#FF0000',   # 紅色 151-200
            'very_unhealthy': '#8F3F97',  # 紫色 201-300
            'hazardous': '#7E0023'    # 褐紅色 301-500
        }
        
        self.aqi_ranges = {
            'good': (0, 50),
            'moderate': (51, 100),
            'unhealthy_sensitive': (101, 150),
            'unhealthy': (151, 200),
            'very_unhealthy': (201, 300),
            'hazardous': (301, 500)
        }
        
        self.aqi_labels = {
            'good': '良好 (0-50)',
            'moderate': '普通 (51-100)',
            'unhealthy_sensitive': '對敏感族群不健康 (101-150)',
            'unhealthy': '對所有族群不健康 (151-200)',
            'very_unhealthy': '非常不健康 (201-300)',
            'hazardous': '危害 (301-500)'
        }
    
    def get_aqi_color(self, aqi_value):
        """Get color based on AQI value"""
        if aqi_value is None:
            return '#808080'  # 灰色 for missing data
        
        for category, (min_val, max_val) in self.aqi_ranges.items():
            if min_val <= aqi_value <= max_val:
                return self.aqi_colors[category]
        
        return '#808080'  # 灰色 for out of range
    
    def get_aqi_category(self, aqi_value):
        """Get category label based on AQI value"""
        if aqi_value is None:
            return '無資料'
        
        for category, (min_val, max_val) in self.aqi_ranges.items():
            if min_val <= aqi_value <= max_val:
                return self.aqi_labels[category]
        
        return '超出範圍'
    
    def load_aqi_data(self, csv_file):
        """Load AQI data from CSV file"""
        try:
            df = pd.read_csv(csv_file, encoding='utf-8-sig')
            print(f"Loaded {len(df)} stations from {csv_file}")
            return df
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            return None
    
    def create_popup_content(self, station):
        """Create HTML content for popup window"""
        aqi_value = station['aqi']
        category = self.get_aqi_category(aqi_value)
        color = self.get_aqi_color(aqi_value)
        
        popup_html = f"""
        <div style="font-family: 'Microsoft JhengHei', Arial, sans-serif; font-size: 12px;">
            <h4 style="margin: 5px 0; color: #333;">{station['site_name']}</h4>
            <p style="margin: 3px 0;"><strong>縣市:</strong> {station['county']}</p>
            <p style="margin: 3px 0;"><strong>AQI:</strong> 
                <span style="font-size: 16px; font-weight: bold; color: {color};">{aqi_value}</span>
            </p>
            <p style="margin: 3px 0;"><strong>狀態:</strong> {category}</p>
            <p style="margin: 3px 0;"><strong>主要污染物:</strong> {station.get('pollutant', 'N/A')}</p>
            {f"<p style='margin: 3px 0;'><strong>PM2.5:</strong> {station['pm25']}</p>" if pd.notna(station.get('pm25')) else ""}
            {f"<p style='margin: 3px 0;'><strong>PM10:</strong> {station['pm10']}</p>" if pd.notna(station.get('pm10')) else ""}
            {f"<p style='margin: 3px 0;'><strong>更新時間:</strong> {station.get('data_time', 'N/A')}</p>" if pd.notna(station.get('data_time')) else ""}
        </div>
        """
        return popup_html
    
    def create_aqi_map(self, df):
        """Create interactive AQI map"""
        if df is None:
            return None
        
        # Filter stations with valid coordinates
        valid_stations = df.dropna(subset=['latitude', 'longitude']).copy()
        print(f"Creating map with {len(valid_stations)} stations with valid coordinates")
        
        # Calculate center point of Taiwan
        center_lat = valid_stations['latitude'].mean()
        center_lon = valid_stations['longitude'].mean()
        
        # Create base map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=7,
            tiles='OpenStreetMap'
        )
        
        # Create marker cluster for better performance
        marker_cluster = MarkerCluster().add_to(m)
        
        # Add markers for each station
        for idx, station in valid_stations.iterrows():
            aqi_value = station['aqi']
            color = self.get_aqi_color(aqi_value)
            
            # Create popup content
            popup_content = self.create_popup_content(station)
            
            # Create tooltip
            tooltip = f"{station['site_name']} - AQI: {aqi_value}"
            
            # Add marker
            folium.CircleMarker(
                location=[station['latitude'], station['longitude']],
                radius=8,
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=tooltip,
                color='black',
                weight=1,
                fillColor=color,
                fillOpacity=0.8
            ).add_to(marker_cluster)
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: auto; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px; font-family: 'Microsoft JhengHei', Arial;">
        <h4 style="margin: 0 0 10px 0;">AQI 空氣品質指標</h4>
        '''
        
        for category, label in self.aqi_labels.items():
            color = self.aqi_colors[category]
            legend_html += f'''
            <p style="margin: 5px 0;">
                <i class="fa fa-circle" style="color: {color};"></i> {label}
            </p>
            '''
        
        legend_html += '</div>'
        
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Add title
        title_html = '''
        <div style="position: fixed; 
                    top: 10px; left: 50%; transform: translateX(-50%); 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:16px; font-weight: bold; padding: 10px; 
                    font-family: 'Microsoft JhengHei', Arial;">
        台灣空氣品質監測地圖
        </div>
        '''
        
        m.get_root().html.add_child(folium.Element(title_html))
        
        return m
    
    def create_statistics_summary(self, df):
        """Create statistics summary"""
        if df is None:
            return None
        
        # Count stations in each AQI category
        category_counts = {}
        for category, (min_val, max_val) in self.aqi_ranges.items():
            count = len(df[(df['aqi'] >= min_val) & (df['aqi'] <= max_val)])
            category_counts[category] = count
        
        # Add missing data count
        missing_count = len(df[df['aqi'].isna()])
        if missing_count > 0:
            category_counts['missing'] = missing_count
        
        # Calculate statistics
        valid_aqi = df[df['aqi'].notna()]['aqi']
        
        summary = {
            'total_stations': len(df),
            'stations_with_data': len(valid_aqi),
            'stations_missing_data': missing_count,
            'category_distribution': category_counts,
            'statistics': {
                'max_aqi': int(valid_aqi.max()) if len(valid_aqi) > 0 else None,
                'min_aqi': int(valid_aqi.min()) if len(valid_aqi) > 0 else None,
                'avg_aqi': round(valid_aqi.mean(), 1) if len(valid_aqi) > 0 else None,
                'median_aqi': int(valid_aqi.median()) if len(valid_aqi) > 0 else None
            },
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return summary
    
    def save_results(self, map_obj, summary):
        """Save map and summary to files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        outputs_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs')
        os.makedirs(outputs_dir, exist_ok=True)
        
        # Save map as HTML file
        map_file = os.path.join(outputs_dir, f'aqi_map_{timestamp}.html')
        map_obj.save(map_file)
        
        # Save summary as JSON
        summary_file = os.path.join(outputs_dir, f'aqi_map_summary_{timestamp}.json')
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"Map saved: {map_file}")
        print(f"Summary saved: {summary_file}")
        
        return map_file, summary_file
    
    def run_visualization(self, csv_file):
        """Main visualization function"""
        print("=== AQI Map Visualization ===")
        print()
        
        # Load data
        print("Loading AQI data...")
        df = self.load_aqi_data(csv_file)
        
        if df is None:
            print("Failed to load data. Exiting.")
            return
        
        # Create statistics summary
        print("Analyzing data...")
        summary = self.create_statistics_summary(df)
        
        # Display summary
        print(f"\n=== Data Summary ===")
        print(f"Total stations: {summary['total_stations']}")
        print(f"Stations with AQI data: {summary['stations_with_data']}")
        print(f"Stations missing data: {summary['stations_missing_data']}")
        
        if summary['statistics']['max_aqi'] is not None:
            print(f"AQI range: {summary['statistics']['min_aqi']} - {summary['statistics']['max_aqi']}")
            print(f"Average AQI: {summary['statistics']['avg_aqi']}")
            print(f"Median AQI: {summary['statistics']['median_aqi']}")
        
        print(f"\n=== AQI Category Distribution ===")
        for category, count in summary['category_distribution'].items():
            if category == 'missing':
                print(f"無資料: {count} 測站")
            else:
                label = self.aqi_labels.get(category, category)
                print(f"{label}: {count} 測站")
        
        # Create map
        print(f"\nCreating interactive map...")
        map_obj = self.create_aqi_map(df)
        
        if map_obj is None:
            print("Failed to create map. Exiting.")
            return
        
        # Save results
        print("Saving results...")
        map_file, summary_file = self.save_results(map_obj, summary)
        
        print(f"\n=== Map Features ===")
        print("- 互動式地圖可縮放和平移")
        print("- 點擓測站查看詳細資訊")
        print("- 顏色代表空氣品質等級")
        print("- 包含圖例說明")
        print("- 支援測站群集顯示")
        
        print(f"\nMap visualization completed!")
        print(f"Open {map_file} in your browser to view the interactive map.")
        
        return map_file, summary_file

if __name__ == "__main__":
    # Find the most recent all AQI data CSV file
    outputs_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs')
    csv_files = [f for f in os.listdir(outputs_dir) if f.startswith('all_aqi_data_') and f.endswith('.csv')]
    
    if not csv_files:
        print("No all AQI data CSV files found in outputs directory.")
        print("Please run aqi_monitor.py first to generate the data.")
    else:
        # Get the most recent file
        latest_file = sorted(csv_files)[-1]
        csv_path = os.path.join(outputs_dir, latest_file)
        
        print(f"Using latest file: {latest_file}")
        
        visualizer = AQIMapVisualizer()
        visualizer.run_visualization(csv_path)
