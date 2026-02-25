#!/usr/bin/env python3
"""
Distance Analysis for High AQI Stations
Calculates distance from high AQI stations to Taipei Main Station
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from math import radians, cos, sin, asin, sqrt

# Set matplotlib font for Chinese characters
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

class DistanceAnalyzer:
    def __init__(self):
        self.taipei_station = {
            'name': '台北總站',
            'latitude': 25.0478,
            'longitude': 121.5170
        }
    
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        Returns distance in kilometers
        """
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        
        return c * r
    
    def load_high_aqi_data(self, csv_file):
        """Load high AQI stations data from CSV file"""
        try:
            df = pd.read_csv(csv_file, encoding='utf-8-sig')
            print(f"Loaded {len(df)} high AQI stations from {csv_file}")
            return df
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            return None
    
    def calculate_distances(self, df):
        """Calculate distances from each station to Taipei Main Station"""
        if df is None:
            return None
        
        # Filter out stations with missing coordinates
        valid_stations = df.dropna(subset=['latitude', 'longitude']).copy()
        print(f"Found {len(valid_stations)} stations with valid coordinates")
        
        # Calculate distance for each station
        distances = []
        for idx, station in valid_stations.iterrows():
            distance = self.haversine_distance(
                station['latitude'], station['longitude'],
                self.taipei_station['latitude'], self.taipei_station['longitude']
            )
            distances.append(distance)
        
        valid_stations['distance_to_taipei'] = distances
        valid_stations['distance_to_taipei'] = valid_stations['distance_to_taipei'].round(2)
        
        return valid_stations
    
    def analyze_distance_distribution(self, df_with_distance):
        """Analyze distance distribution"""
        if df_with_distance is None:
            return None
        
        analysis = {
            'total_stations': len(df_with_distance),
            'avg_distance': df_with_distance['distance_to_taipei'].mean(),
            'median_distance': df_with_distance['distance_to_taipei'].median(),
            'min_distance': df_with_distance['distance_to_taipei'].min(),
            'max_distance': df_with_distance['distance_to_taipei'].max(),
            'std_distance': df_with_distance['distance_to_taipei'].std(),
            'nearest_station': df_with_distance.loc[df_with_distance['distance_to_taipei'].idxmin()],
            'farthest_station': df_with_distance.loc[df_with_distance['distance_to_taipei'].idxmax()]
        }
        
        return analysis
    
    def create_distance_visualization(self, df_with_distance):
        """Create visualization of distance analysis"""
        if df_with_distance is None:
            return
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('高AQI測站到台北總站距離分析', fontsize=16, fontweight='bold')
        
        # 1. Distance distribution histogram
        axes[0, 0].hist(df_with_distance['distance_to_taipei'], bins=15, alpha=0.7, color='skyblue', edgecolor='black')
        axes[0, 0].set_title('距離分布直方圖')
        axes[0, 0].set_xlabel('距離 (公里)')
        axes[0, 0].set_ylabel('測站數量')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Distance vs AQI scatter plot
        scatter = axes[0, 1].scatter(df_with_distance['distance_to_taipei'], df_with_distance['aqi'], 
                                   c=df_with_distance['aqi'], cmap='Reds', alpha=0.6, s=60)
        axes[0, 1].set_title('距離 vs AQI 散布圖')
        axes[0, 1].set_xlabel('距離 (公里)')
        axes[0, 1].set_ylabel('AQI 值')
        plt.colorbar(scatter, ax=axes[0, 1], label='AQI')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Top 10 nearest stations
        nearest_10 = df_with_distance.nsmallest(10, 'distance_to_taipei')
        axes[1, 0].barh(range(len(nearest_10)), nearest_10['distance_to_taipei'], color='lightcoral')
        axes[1, 0].set_yticks(range(len(nearest_10)))
        axes[1, 0].set_yticklabels([f"{row['site_name']}" for _, row in nearest_10.iterrows()], fontsize=10)
        axes[1, 0].set_title('距離台北總站最近的10個高AQI測站')
        axes[1, 0].set_xlabel('距離 (公里)')
        axes[1, 0].invert_yaxis()
        
        # 4. County-wise distance boxplot
        county_distances = df_with_distance.groupby('county')['distance_to_taipei'].apply(list).reset_index()
        county_data = [distances for distances in county_distances['distance_to_taipei']]
        county_names = county_distances['county'].tolist()
        
        axes[1, 1].boxplot(county_data, labels=county_names, patch_artist=True)
        axes[1, 1].set_title('各縣市測站距離分布')
        axes[1, 1].set_xlabel('縣市')
        axes[1, 1].set_ylabel('距離 (公里)')
        axes[1, 1].tick_params(axis='x', rotation=45)
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save the plot
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        outputs_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs')
        os.makedirs(outputs_dir, exist_ok=True)
        plt.savefig(os.path.join(outputs_dir, f'distance_analysis_{timestamp}.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Distance analysis visualization saved: distance_analysis_{timestamp}.png")
    
    def save_results(self, df_with_distance, analysis):
        """Save analysis results to files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        outputs_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs')
        os.makedirs(outputs_dir, exist_ok=True)
        
        # Save stations with distance data
        df_with_distance.to_csv(os.path.join(outputs_dir, f'high_aqi_with_distances_{timestamp}.csv'), 
                              index=False, encoding='utf-8-sig')
        
        # Save analysis summary
        summary_data = {
            'analysis_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'taipei_main_station': {
                'name': self.taipei_station['name'],
                'coordinates': f"({self.taipei_station['latitude']}, {self.taipei_station['longitude']})"
            },
            'statistics': {
                'total_stations': analysis['total_stations'],
                'average_distance_km': round(analysis['avg_distance'], 2),
                'median_distance_km': round(analysis['median_distance'], 2),
                'min_distance_km': round(analysis['min_distance'], 2),
                'max_distance_km': round(analysis['max_distance'], 2),
                'std_distance_km': round(analysis['std_distance'], 2)
            },
            'nearest_station': {
                'name': analysis['nearest_station']['site_name'],
                'county': analysis['nearest_station']['county'],
                'aqi': int(analysis['nearest_station']['aqi']),
                'distance_km': round(analysis['nearest_station']['distance_to_taipei'], 2)
            },
            'farthest_station': {
                'name': analysis['farthest_station']['site_name'],
                'county': analysis['farthest_station']['county'],
                'aqi': int(analysis['farthest_station']['aqi']),
                'distance_km': round(analysis['farthest_station']['distance_to_taipei'], 2)
            }
        }
        
        import json
        with open(os.path.join(outputs_dir, f'distance_analysis_summary_{timestamp}.json'), 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
        
        print(f"Results saved with timestamp: {timestamp}")
    
    def run_analysis(self, csv_file):
        """Main analysis function"""
        print("=== High AQI Stations Distance Analysis ===")
        print(f"Target: {self.taipei_station['name']} ({self.taipei_station['latitude']}, {self.taipei_station['longitude']})")
        print()
        
        # Load data
        print("Loading high AQI stations data...")
        df = self.load_high_aqi_data(csv_file)
        
        if df is None:
            print("Failed to load data. Exiting.")
            return
        
        # Calculate distances
        print("Calculating distances to Taipei Main Station...")
        df_with_distance = self.calculate_distances(df)
        
        if df_with_distance is None:
            print("Failed to calculate distances. Exiting.")
            return
        
        # Analyze distribution
        print("Analyzing distance distribution...")
        analysis = self.analyze_distance_distribution(df_with_distance)
        
        # Display results
        print(f"\n=== Distance Analysis Results ===")
        print(f"Total stations analyzed: {analysis['total_stations']}")
        print(f"Average distance: {analysis['avg_distance']:.2f} km")
        print(f"Median distance: {analysis['median_distance']:.2f} km")
        print(f"Distance range: {analysis['min_distance']:.2f} - {analysis['max_distance']:.2f} km")
        print(f"Standard deviation: {analysis['std_distance']:.2f} km")
        
        print(f"\n=== Nearest Station ===")
        nearest = analysis['nearest_station']
        print(f"{nearest['site_name']} ({nearest['county']}): {nearest['distance_to_taipei']:.2f} km, AQI: {nearest['aqi']}")
        
        print(f"\n=== Farthest Station ===")
        farthest = analysis['farthest_station']
        print(f"{farthest['site_name']} ({farthest['county']}): {farthest['distance_to_taipei']:.2f} km, AQI: {farthest['aqi']}")
        
        # Show top 10 nearest stations
        print(f"\n=== Top 10 Nearest High AQI Stations ===")
        nearest_10 = df_with_distance.nsmallest(10, 'distance_to_taipei')
        for idx, (_, station) in enumerate(nearest_10.iterrows(), 1):
            print(f"{idx:2d}. {station['site_name']} ({station['county']}): {station['distance_to_taipei']:.2f} km, AQI: {station['aqi']}")
        
        # Save results
        print("\nSaving results...")
        self.save_results(df_with_distance, analysis)
        
        # Create visualization
        print("Creating visualization...")
        self.create_distance_visualization(df_with_distance)
        
        print("\nDistance analysis completed successfully!")

if __name__ == "__main__":
    # Find the most recent high AQI stations CSV file
    outputs_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs')
    csv_files = [f for f in os.listdir(outputs_dir) if f.startswith('high_aqi_stations_') and f.endswith('.csv')]
    
    if not csv_files:
        print("No high AQI stations CSV files found in outputs directory.")
        print("Please run aqi_monitor.py first to generate the data.")
    else:
        # Get the most recent file
        latest_file = sorted(csv_files)[-1]
        csv_path = os.path.join(outputs_dir, latest_file)
        
        print(f"Using latest file: {latest_file}")
        
        analyzer = DistanceAnalyzer()
        analyzer.run_analysis(csv_path)
