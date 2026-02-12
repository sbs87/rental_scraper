#!/usr/bin/env python3
"""
Rental Analysis Script
Analyzes historical tracking data to generate insights
"""

import csv
import os
from collections import defaultdict, Counter
from datetime import datetime
import statistics

class RentalAnalyzer:
    def __init__(self, data_dir='rental_data'):
        self.data_dir = data_dir
        self.historical_file = os.path.join(data_dir, 'historical_data.csv')
        
    def load_data(self):
        """Load all historical data"""
        if not os.path.isfile(self.historical_file):
            print(f"❌ Historical data file not found: {self.historical_file}")
            return []
        
        with open(self.historical_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    
    def analyze_sold_properties(self, data):
        """Analyze properties that were sold/rented"""
        print("\n" + "=" * 60)
        print("🏠 SOLD/RENTED PROPERTIES ANALYSIS")
        print("=" * 60)
        
        # Group by property ID
        property_history = defaultdict(list)
        for row in data:
            property_history[row['property_id']].append(row)
        
        # Find properties that appeared then disappeared
        sold_properties = []
        
        all_dates = sorted(set(row['scraped_date'] for row in data))
        
        for prop_id, history in property_history.items():
            dates_seen = set(h['scraped_date'] for h in history)
            
            # If property was seen but not on the last scrape date, it was likely sold
            if all_dates and all_dates[-1] not in dates_seen and len(dates_seen) > 0:
                last_seen = max(dates_seen)
                last_data = next(h for h in history if h['scraped_date'] == last_seen)
                
                sold_properties.append({
                    'property_id': prop_id,
                    'address': last_data['address'],
                    'price': int(last_data['price']),
                    'bedrooms': int(last_data['bedrooms']),
                    'bathrooms': int(last_data['bathrooms']),
                    'property_type': last_data['property_type'],
                    'first_seen': min(dates_seen),
                    'last_seen': last_seen,
                    'days_on_market': len(dates_seen)
                })
        
        if not sold_properties:
            print("\nℹ️  No sold properties found yet (need more tracking data)")
            return
        
        print(f"\n📊 Total Sold/Rented: {len(sold_properties)}")
        
        # Average stats
        if sold_properties:
            avg_price = statistics.mean(p['price'] for p in sold_properties)
            avg_bedrooms = statistics.mean(p['bedrooms'] for p in sold_properties)
            avg_bathrooms = statistics.mean(p['bathrooms'] for p in sold_properties)
            
            print(f"\n💰 SOLD PROPERTY STATISTICS:")
            print(f"   Average Price: ${avg_price:,.0f}")
            print(f"   Average Bedrooms: {avg_bedrooms:.1f}")
            print(f"   Average Bathrooms: {avg_bathrooms:.1f}")
            
            # Price distribution
            price_ranges = {
                'Under $4,000': sum(1 for p in sold_properties if p['price'] < 4000),
                '$4,000-$5,000': sum(1 for p in sold_properties if 4000 <= p['price'] < 5000),
                '$5,000-$6,000': sum(1 for p in sold_properties if 5000 <= p['price'] < 6000),
                '$6,000+': sum(1 for p in sold_properties if p['price'] >= 6000),
            }
            
            print(f"\n💵 PRICE DISTRIBUTION:")
            for range_name, count in price_ranges.items():
                if count > 0:
                    print(f"   {range_name}: {count} properties")
            
            # Property types
            types = Counter(p['property_type'] for p in sold_properties)
            print(f"\n🏘️  PROPERTY TYPES:")
            for ptype, count in types.most_common():
                print(f"   {ptype}: {count}")
        
        # List individual properties
        print(f"\n📋 INDIVIDUAL SOLD PROPERTIES:")
        sorted_props = sorted(sold_properties, key=lambda x: x['price'])
        for prop in sorted_props:
            print(f"\n   {prop['address']}")
            print(f"   Price: ${prop['price']:,} | {prop['bedrooms']}bd/{prop['bathrooms']}ba | {prop['property_type']}")
            print(f"   First seen: {prop['first_seen']} | Last seen: {prop['last_seen']}")
            print(f"   Days tracked: {prop['days_on_market']}")
    
    def analyze_price_trends(self, data):
        """Analyze price changes over time"""
        print("\n" + "=" * 60)
        print("💰 PRICE TREND ANALYSIS")
        print("=" * 60)
        
        # Group by property
        property_history = defaultdict(list)
        for row in data:
            property_history[row['property_id']].append(row)
        
        price_changes = []
        
        for prop_id, history in property_history.items():
            if len(history) < 2:
                continue
            
            # Sort by date
            history = sorted(history, key=lambda x: x['scraped_date'])
            
            # Check for price changes
            for i in range(1, len(history)):
                prev = history[i-1]
                curr = history[i]
                
                if prev['price'] != curr['price']:
                    change = int(curr['price']) - int(prev['price'])
                    pct_change = (change / int(prev['price'])) * 100
                    
                    price_changes.append({
                        'address': curr['address'],
                        'old_price': int(prev['price']),
                        'new_price': int(curr['price']),
                        'change': change,
                        'pct_change': pct_change,
                        'date': curr['scraped_date']
                    })
        
        if not price_changes:
            print("\nℹ️  No price changes detected yet")
            return
        
        print(f"\n📈 Total Price Changes: {len(price_changes)}")
        
        increases = [p for p in price_changes if p['change'] > 0]
        decreases = [p for p in price_changes if p['change'] < 0]
        
        print(f"   Price Increases: {len(increases)}")
        print(f"   Price Decreases: {len(decreases)}")
        
        if increases:
            avg_increase = statistics.mean(p['change'] for p in increases)
            print(f"   Average Increase: ${avg_increase:,.0f}")
        
        if decreases:
            avg_decrease = statistics.mean(abs(p['change']) for p in decreases)
            print(f"   Average Decrease: ${avg_decrease:,.0f}")
        
        # List changes
        print(f"\n📋 PRICE CHANGES:")
        for change in sorted(price_changes, key=lambda x: abs(x['change']), reverse=True):
            direction = "↑" if change['change'] > 0 else "↓"
            print(f"\n   {change['address']}")
            print(f"   {direction} ${change['old_price']:,} → ${change['new_price']:,} "
                  f"({change['pct_change']:+.1f}%)")
            print(f"   Date: {change['date']}")
    
    def analyze_availability_trends(self, data):
        """Analyze availability patterns over time"""
        print("\n" + "=" * 60)
        print("📊 AVAILABILITY TRENDS")
        print("=" * 60)
        
        # Group by date
        by_date = defaultdict(list)
        for row in data:
            by_date[row['scraped_date']].append(row)
        
        dates = sorted(by_date.keys())
        
        if len(dates) < 2:
            print("\nℹ️  Need more tracking data to show trends")
            return
        
        print(f"\n📅 TRACKING PERIOD: {dates[0]} to {dates[-1]}")
        print(f"\n📈 AVAILABILITY BY DATE:")
        
        for date in dates:
            count = len(by_date[date])
            avg_price = statistics.mean(int(row['price']) for row in by_date[date])
            print(f"   {date}: {count} properties (avg price: ${avg_price:,.0f})")
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        data = self.load_data()
        
        if not data:
            print("❌ No data to analyze")
            return
        
        print("\n" + "=" * 60)
        print("📊 RENTAL TRACKING ANALYSIS REPORT")
        print("=" * 60)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Records: {len(data)}")
        
        # Get unique dates and properties
        unique_dates = len(set(row['scraped_date'] for row in data))
        unique_properties = len(set(row['property_id'] for row in data))
        
        print(f"Scraping Sessions: {unique_dates}")
        print(f"Unique Properties Tracked: {unique_properties}")
        
        # Run analyses
        self.analyze_availability_trends(data)
        self.analyze_price_trends(data)
        self.analyze_sold_properties(data)
        
        print("\n" + "=" * 60)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 60 + "\n")


def main():
    analyzer = RentalAnalyzer()
    analyzer.generate_report()


if __name__ == "__main__":
    main()
