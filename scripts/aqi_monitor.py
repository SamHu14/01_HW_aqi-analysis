#!/usr/bin/env python3
"""
Taiwan Air Quality Index (AQI) Monitor
Fetches real-time AQI data from MOENV API and identifies stations with AQI > 50
"""

import os
import requests
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import seaborn as sns
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set matplotlib font for Chinese characters
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# Load environment variables
load_dotenv()

class AQIMonitor:
    def __init__(self):
        self.api_key = os.getenv('MOENV_API_KEY')
        if not self.api_key or self.api_key == 'your_moenv_api_key_here':
            raise ValueError("Please set your MOENV_API_KEY in the .env file")
        
        self.base_url = "https://data.moenv.gov.tw/api/v2"
        self.aqi_endpoint = f"{self.base_url}/aqx_p_432"
        self.headers = {
            'accept': 'application/json'
        }
        
    def fetch_aqi_data(self):
        """Fetch real-time AQI data from MOENV API"""
        try:
            params = {
                'api_key': self.api_key,
                'limit': 100  # Get all stations
            }
            
            response = requests.get(self.aqi_endpoint, params=params, headers=self.headers, verify=False)
            response.raise_for_status()
            
            data = response.json()
            print(f"Successfully fetched {len(data)} records")
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return None
    
    def process_aqi_data(self, raw_data):
        """Process raw AQI data into structured format"""
        if not raw_data:
            return None
            
        processed_data = []
        for record in raw_data:
            try:
                processed_record = {
                    'site_id': record.get('siteid'),
                    'site_name': record.get('sitename'),
                    'county': record.get('county'),
                    'aqi': int(record.get('aqi', 0)) if record.get('aqi') else None,
                    'pollutant': record.get('pollutant'),
                    'status': record.get('status'),
                    'pm25': float(record.get('pm2.5', 0)) if record.get('pm2.5') else None,
                    'pm10': float(record.get('pm10', 0)) if record.get('pm10') else None,
                    'so2': float(record.get('so2', 0)) if record.get('so2') else None,
                    'no2': float(record.get('no2', 0)) if record.get('no2') else None,
                    'co': float(record.get('co', 0)) if record.get('co') else None,
                    'o3': float(record.get('o3', 0)) if record.get('o3') else None,
                    'wind_speed': float(record.get('windspeed', 0)) if record.get('windspeed') else None,
                    'wind_direction': float(record.get('winddirec', 0)) if record.get('winddirec') else None,
                    'data_time': record.get('datacreationdate'),
                    'latitude': float(record.get('latitude', 0)) if record.get('latitude') else None,
                    'longitude': float(record.get('longitude', 0)) if record.get('longitude') else None
                }
                processed_data.append(processed_record)
            except (ValueError, TypeError) as e:
                print(f"Error processing record {record.get('sitename', 'Unknown')}: {e}")
                continue
                
        return processed_data
    
    def identify_high_aqi_stations(self, processed_data, threshold=50):
        """Identify stations with AQI > threshold"""
        if not processed_data:
            return []
            
        high_aqi_stations = [
            station for station in processed_data 
            if station['aqi'] and station['aqi'] > threshold
        ]
        
        # Sort by AQI value (descending)
        high_aqi_stations.sort(key=lambda x: x['aqi'], reverse=True)
        
        return high_aqi_stations
    
    def generate_summary(self, processed_data, high_aqi_stations):
        """Generate summary statistics"""
        if not processed_data:
            return None
            
        total_stations = len(processed_data)
        high_aqi_count = len(high_aqi_stations)
        
        # Calculate statistics
        aqi_values = [s['aqi'] for s in processed_data if s['aqi'] is not None]
        
        summary = {
            'total_stations': total_stations,
            'stations_with_aqi_data': len(aqi_values),
            'high_aqi_stations': high_aqi_count,
            'percentage_high_aqi': (high_aqi_count / total_stations) * 100 if total_stations > 0 else 0,
            'max_aqi': max(aqi_values) if aqi_values else None,
            'min_aqi': min(aqi_values) if aqi_values else None,
            'avg_aqi': sum(aqi_values) / len(aqi_values) if aqi_values else None,
            'data_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return summary
    
    def save_results(self, processed_data, high_aqi_stations, summary):
        """Save results to files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create outputs directory if it doesn't exist
        outputs_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs')
        os.makedirs(outputs_dir, exist_ok=True)
        
        # Save all data
        all_df = pd.DataFrame(processed_data)
        all_df.to_csv(os.path.join(outputs_dir, f'all_aqi_data_{timestamp}.csv'), index=False, encoding='utf-8-sig')
        
        # Save high AQI stations
        high_aqi_df = pd.DataFrame(high_aqi_stations)
        high_aqi_df.to_csv(os.path.join(outputs_dir, f'high_aqi_stations_{timestamp}.csv'), index=False, encoding='utf-8-sig')
        
        # Save summary
        with open(os.path.join(outputs_dir, f'aqi_summary_{timestamp}.json'), 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"Results saved with timestamp: {timestamp}")
        
    def create_visualization(self, high_aqi_stations):
        """Create visualization of high AQI stations"""
        if not high_aqi_stations:
            print("No high AQI stations to visualize")
            return
            
        # Prepare data for visualization
        df = pd.DataFrame(high_aqi_stations)
        
        # Create bar chart
        plt.figure(figsize=(12, 8))
        sns.barplot(data=df.head(20), x='aqi', y='site_name', hue='county')
        plt.title('Top 20 Stations with AQI > 50', fontsize=16)
        plt.xlabel('AQI Value', fontsize=12)
        plt.ylabel('Station Name', fontsize=12)
        plt.tight_layout()
        
        # Save plot
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        outputs_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs')
        plt.savefig(os.path.join(outputs_dir, f'high_aqi_chart_{timestamp}.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Visualization saved: high_aqi_chart_{timestamp}.png")
    
    def run_monitoring(self):
        """Main monitoring function"""
        print("=== Taiwan AQI Monitor ===")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Fetch data
        print("Fetching AQI data...")
        raw_data = self.fetch_aqi_data()
        
        if not raw_data:
            print("Failed to fetch data. Exiting.")
            return
        
        # Process data
        print("Processing data...")
        processed_data = self.process_aqi_data(raw_data)
        
        if not processed_data:
            print("Failed to process data. Exiting.")
            return
        
        # Identify high AQI stations
        print("Identifying stations with AQI > 50...")
        high_aqi_stations = self.identify_high_aqi_stations(processed_data)
        
        # Generate summary
        summary = self.generate_summary(processed_data, high_aqi_stations)
        
        # Display results
        print(f"\n=== Summary ===")
        print(f"Total stations: {summary['total_stations']}")
        print(f"Stations with AQI > 50: {summary['high_aqi_stations']}")
        print(f"Percentage: {summary['percentage_high_aqi']:.1f}%")
        print(f"Max AQI: {summary['max_aqi']}")
        print(f"Min AQI: {summary['min_aqi']}")
        print(f"Average AQI: {summary['avg_aqi']:.1f}")
        
        print(f"\n=== Stations with AQI > 50 ({len(high_aqi_stations)} stations) ===")
        for station in high_aqi_stations:
            print(f"{station['site_name']} ({station['county']}): AQI = {station['aqi']} - {station['status']}")
        
        # Save results
        print("\nSaving results...")
        self.save_results(processed_data, high_aqi_stations, summary)
        
        # Create visualization
        print("Creating visualization...")
        self.create_visualization(high_aqi_stations)
        
        print("\nMonitoring completed successfully!")

if __name__ == "__main__":
    try:
        monitor = AQIMonitor()
        monitor.run_monitoring()
    except Exception as e:
        print(f"Error: {e}")
