#!/usr/bin/env python3
"""
Rental Property Tracker for Freda Real Estate
Monitors beach block rentals in Sea Isle City, NJ
"""

import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
from urllib.parse import urlencode, urlparse, parse_qs
import re
import time

class RentalTracker:
    def __init__(self, base_url, output_dir='rental_data'):
        self.base_url = base_url
        self.output_dir = output_dir
        self.timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.date_only = datetime.now().strftime('%Y-%m-%d')
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # File paths
        self.snapshot_file = os.path.join(output_dir, f'snapshot_{self.timestamp}.csv')
        self.historical_file = os.path.join(output_dir, 'historical_data.csv')
        self.summary_file = os.path.join(output_dir, 'tracking_summary.csv')
        
    def fetch_page(self):
        """Fetch the rental results page"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(self.base_url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            return None
    
    def parse_rentals(self, html):
        """Parse rental listings from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        rentals = []
        
        # Find all rental property links
        rental_links = soup.find_all('a', href=re.compile(r'rentalproperty\.php\?id='))
        
        for link in rental_links:
            try:
                # Extract property ID from URL
                href = link.get('href', '')
                id_match = re.search(r'id=(\d+)', href)
                property_id = id_match.group(1) if id_match else 'unknown'
                
                # Find the parent container with all property details
                parent = link.find_parent('td')
                if not parent:
                    continue
                
                # Extract property details from the link text and structure
                link_text = link.get_text(strip=True)
                
                # Parse address (first line in bold)
                address_match = re.search(r'^(.+?),\s*Sea Isle City', link_text)
                address = address_match.group(1) if address_match else link_text.split(',')[0]
                
                # Extract rate (price)
                rate_match = re.search(r'Rate:\s*\$?([\d,]+)', link_text)
                price = rate_match.group(1).replace(',', '') if rate_match else '0'
                
                # Extract unit type
                unit_match = re.search(r'Unit:\s*(\w+)', link_text)
                unit = unit_match.group(1) if unit_match else ''
                
                # Extract bedrooms
                bd_match = re.search(r'(\d+)\s+Bd', link_text)
                bedrooms = bd_match.group(1) if bd_match else '0'
                
                # Extract bathrooms
                ba_match = re.search(r'(\d+)\s+Ba', link_text)
                bathrooms = ba_match.group(1) if ba_match else '0'
                
                # Extract half bathrooms
                half_match = re.search(r'(\d+)\s+Half', link_text)
                half_baths = half_match.group(1) if half_match else '0'
                
                # Extract property type
                type_match = re.search(r'(Condo|Townhome|House|Apartment)', link_text)
                property_type = type_match.group(1) if type_match else 'Unknown'
                
                rental_data = {
                    'property_id': property_id,
                    'address': address.strip(),
                    'unit': unit,
                    'price': price,
                    'bedrooms': bedrooms,
                    'bathrooms': bathrooms,
                    'half_baths': half_baths,
                    'property_type': property_type,
                    'url': f"https://callfreda.com/{href}",
                    'scraped_date': self.date_only,
                    'scraped_timestamp': self.timestamp
                }
                
                rentals.append(rental_data)
                
            except Exception as e:
                print(f"Error parsing rental: {e}")
                continue
        
        return rentals
    
    def save_snapshot(self, rentals):
        """Save current snapshot to CSV"""
        if not rentals:
            print("No rentals to save")
            return
        
        fieldnames = ['property_id', 'address', 'unit', 'price', 'bedrooms', 
                     'bathrooms', 'half_baths', 'property_type', 'url', 
                     'scraped_date', 'scraped_timestamp']
        
        with open(self.snapshot_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rentals)
        
        print(f"✓ Snapshot saved: {self.snapshot_file}")
    
    def update_historical(self, rentals):
        """Append to historical data file"""
        if not rentals:
            return
        
        fieldnames = ['property_id', 'address', 'unit', 'price', 'bedrooms', 
                     'bathrooms', 'half_baths', 'property_type', 'url', 
                     'scraped_date', 'scraped_timestamp']
        
        file_exists = os.path.isfile(self.historical_file)
        
        with open(self.historical_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerows(rentals)
        
        print(f"✓ Historical data updated: {self.historical_file}")
    
    def analyze_changes(self, rentals):
        """Compare with previous data to identify changes"""
        if not os.path.isfile(self.historical_file):
            print("ℹ First run - no previous data to compare")
            return
        
        # Read all historical data
        historical = []
        with open(self.historical_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            historical = list(reader)
        
        if not historical:
            print("ℹ No previous data to compare")
            return
        
        # Get the most recent previous scrape date (not today's)
        dates = sorted(set(row['scraped_date'] for row in historical if row['scraped_date'] != self.date_only))
        if not dates:
            print("ℹ No previous scrape to compare with")
            return
        
        previous_date = dates[-1]
        
        # Get previous listings
        previous = [row for row in historical if row['scraped_date'] == previous_date]
        previous_ids = set(row['property_id'] for row in previous)
        
        # Get current listings
        current_ids = set(rental['property_id'] for rental in rentals)
        
        # Identify changes
        new_listings = current_ids - previous_ids
        removed_listings = previous_ids - current_ids
        still_available = current_ids & previous_ids
        
        print(f"\n📊 COMPARISON WITH {previous_date}:")
        print(f"   New listings: {len(new_listings)}")
        print(f"   Removed (sold/rented): {len(removed_listings)}")
        print(f"   Still available: {len(still_available)}")
        
        # Show details of removed listings
        if removed_listings:
            print(f"\n🏠 REMOVED LISTINGS (Likely Sold/Rented):")
            for prop_id in removed_listings:
                prop = next((p for p in previous if p['property_id'] == prop_id), None)
                if prop:
                    print(f"   • {prop['address']} - ${prop['price']} ({prop['bedrooms']}bd/{prop['bathrooms']}ba)")
        
        # Show new listings
        if new_listings:
            print(f"\n✨ NEW LISTINGS:")
            for prop_id in new_listings:
                prop = next((p for p in rentals if p['property_id'] == prop_id), None)
                if prop:
                    print(f"   • {prop['address']} - ${prop['price']} ({prop['bedrooms']}bd/{prop['bathrooms']}ba)")
        
        # Check for price changes
        print(f"\n💰 PRICE CHANGES:")
        price_changes = False
        for current in rentals:
            if current['property_id'] in still_available:
                prev = next((p for p in previous if p['property_id'] == current['property_id']), None)
                if prev and prev['price'] != current['price']:
                    price_changes = True
                    print(f"   • {current['address']}: ${prev['price']} → ${current['price']}")
        
        if not price_changes:
            print("   No price changes detected")
        
        # Update summary file
        self.update_summary(len(rentals), len(new_listings), len(removed_listings), len(still_available))
    
    def update_summary(self, total, new, removed, still_available):
        """Update the tracking summary file"""
        fieldnames = ['date', 'timestamp', 'total_listings', 'new_listings', 
                     'removed_listings', 'still_available']
        
        file_exists = os.path.isfile(self.summary_file)
        
        with open(self.summary_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            
            writer.writerow({
                'date': self.date_only,
                'timestamp': self.timestamp,
                'total_listings': total,
                'new_listings': new,
                'removed_listings': removed,
                'still_available': still_available
            })
        
        print(f"✓ Summary updated: {self.summary_file}")
    
    def run(self):
        """Main execution method"""
        print("=" * 60)
        print("🏖️  RENTAL TRACKER - Sea Isle City Beach Block")
        print("=" * 60)
        print(f"Scraping at: {self.timestamp}")
        print(f"URL: {self.base_url}\n")
        
        # Fetch and parse
        html = self.fetch_page()
        if not html:
            print("❌ Failed to fetch page")
            return
        
        rentals = self.parse_rentals(html)
        
        if not rentals:
            print("⚠️  No rentals found (page structure may have changed)")
            return
        
        print(f"✓ Found {len(rentals)} rental properties\n")
        
        # Display current listings
        print("📋 CURRENT LISTINGS:")
        for rental in rentals:
            print(f"   • {rental['address']} ({rental['unit']})")
            print(f"     ${rental['price']} | {rental['bedrooms']}bd/{rental['bathrooms']}ba | {rental['property_type']}")
        
        # Save data
        print("\n💾 SAVING DATA:")
        self.save_snapshot(rentals)
        self.update_historical(rentals)
        
        # Analyze changes
        self.analyze_changes(rentals)
        
        print("\n" + "=" * 60)
        print("✅ Tracking complete!")
        print("=" * 60)


def main():
    # Your search URL
    url = "https://callfreda.com/rentalresults.php?vr=view&checkin=08/22/2026&checkout=08/29/2026&BD=5&MBD=7&BTH=3&MBTH=3&TW=Beach%20Block&MN=0&MX=999000&Amenities=Air%20Conditioning,Outside%20Shower,Washer,Dryer"
    
    tracker = RentalTracker(url)
    tracker.run()


if __name__ == "__main__":
    main()
