#!/usr/bin/env python3
"""
Multi-URL Rental Property Tracker for Freda Real Estate
Monitors multiple search criteria with automatic pagination
"""

from urllib.parse import parse_qs, urlparse
import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
import re
import time
import argparse

argparse = argparse.ArgumentParser(description="Multi-URL Rental Property Tracker for Freda Real Estate")
argparse.add_argument('--config', type=str, default='search_urls.csv', help='Path to search URLs config file (default: search_urls.csv)')
config_args = argparse.parse_args()
search_urls_file = config_args.config
global_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

class MultiRentalTracker:
    def __init__(self, config_file=search_urls_file, output_dir='rental_data'):
        self.config_file = config_file
        self.output_dir = output_dir
        self.timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.date_only = datetime.now().strftime('%Y-%m-%d')
        
        # Pagination settings
        self.results_per_page = 15  # Freda shows 15 results per page
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # File paths
        self.snapshot_file = os.path.join(output_dir, f'snapshot_{self.timestamp}.csv')
        self.historical_file = os.path.join(output_dir, 'historical_data.csv')
        self.summary_file = os.path.join(output_dir, 'tracking_summary.csv')
        
    def load_search_urls(self):
        """Load search URLs from config file"""
        if not os.path.isfile(self.config_file):
            print(f"❌ Config file not found: {self.config_file}")
            print("   Creating sample file...")
            self.create_sample_config()
            return []
        
        searches = []
        with open(self.config_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f,delimiter='\t')
            for row in reader:
                if row.get('url_id') and row.get('url'):
                    searches.append({
                        'url_id': row['url_id'].strip(),
                        'url': row['url'].strip(),
                        'description': row.get('description', '').strip()
                    })
        
        return searches
    
    def create_sample_config(self):
        """Create a sample configuration file"""
        sample_data = [
            {
                'url_id': 'URL_ID_1',
                'url': 'https://callfreda.com/rentalresults.php?vr=view&checkin=08/22/2026&checkout=08/29/2026&BD=5&MBD=7&BTH=3&MBTH=3&TW=Beach%20Block&MN=0&MX=999000&Amenities=Air%20Conditioning,Outside%20Shower,Washer,Dryer',
                'description': 'Beach Block, 5-7bd, 3ba, Aug 22-29'
            },
            {
                'url_id': 'URL_ID_2',
                'url': 'https://callfreda.com/rentalresults.php?vr=view&checkin=08/15/2026&checkout=08/22/2026&BD=5&MBD=7&BTH=3&MBTH=3&TW=Beach%20Block&MN=0&MX=999000&Amenities=Air%20Conditioning,Outside%20Shower,Washer,Dryer',
                'description': 'Beach Block, 5-7bd, 3ba, Aug 15-22'
            }
        ]
        
        with open(self.config_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['url_id', 'url', 'description'],delimiter='\t')
            writer.writeheader()
            writer.writerows(sample_data)
        
        print(f"✓ Created sample config: {self.config_file}")
        print("  Edit this file to add your search URLs")
    
    def build_paginated_url(self, base_url, start_index):
        """Build URL with pagination parameter"""
        # Remove any existing &start= parameter
        url = re.sub(r'&start=\d+', '', base_url)
        
        # Add the start parameter
        if start_index > 0:
            if '?' in url:
                url = f"{url}&start={start_index}"
            else:
                url = f"{url}?start={start_index}"
        
        return url
    
    def fetch_page(self, url):
        """Fetch the rental results page"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"   ❌ Error fetching page: {e}")
            return None
    
    def get_total_results(self, html):
        """Extract total number of results from the page"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for text like "You have X Rental Properties that Match Your Criteria"
        text = soup.get_text()
        match = re.search(r'You have\s+\*\*(\d+)\*\*\s+Rental Properties', text)
        if match:
            return int(match.group(1))
        
        # Alternative: look for "Displaying X - Y of Z"
        match = re.search(r'Displaying\s+\*\*\d+\*\*\s+-\s+\*\*\d+\*\*\s+of\s+\*\*(\d+)\*\*', text)
        if match:
            return int(match.group(1))
        
        return None
    
    def parse_rentals(self, html, url_id):
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

                # SLOPPY condense into a single parser Try to extract checkin/checkout from the link; fall back to the search URL if absent
                parsed = urlparse(href)
                query = parsed.query or urlparse(self.base_url).query
                params = parse_qs(query)
                checkin_date = params.get('checkin', [''])[0]
                checkout_date = params.get('checkout', [''])[0]
                
                
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
                    'url_id': url_id,
                    'property_id': property_id,
                    'timestamp': global_timestamp,
                    'checkin_date': checkin_date,
                    'checkout_date': checkout_date,
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
                print(f"   ⚠️  Error parsing rental: {e}")
                continue
        
        return rentals
    
    def fetch_all_pages(self, base_url, url_id):
        """Fetch all pages of results for a given search URL"""
        all_rentals = []
        page_num = 1
        start_index = 0
        
        print(f"   📄 Fetching page {page_num}...", end='', flush=True)
        
        # Fetch first page
        url = self.build_paginated_url(base_url, start_index)
        html = self.fetch_page(url)
        
        if not html:
            print(" failed!")
            return []
        
        # Get total results from first page
        total_results = self.get_total_results(html)
        if total_results:
            print(f" found {total_results} total results")
            expected_pages = (total_results + self.results_per_page - 1) // self.results_per_page
            print(f"   📊 Expecting approximately {expected_pages} pages")
        else:
            print(" (total unknown, will paginate until empty)")
        
        # Parse first page
        rentals = self.parse_rentals(html, url_id)
        if rentals:
            all_rentals.extend(rentals)
            print(f"   ✓ Page {page_num}: {len(rentals)} properties")
        else:
            print(f"   ⚠️  Page {page_num}: No properties found")
            return all_rentals
        
        # Continue fetching pages while we get results
        while True:
            # If we know the total and have reached it, stop
            if total_results and len(all_rentals) >= total_results:
                print(f"   ✓ Reached all {total_results} results")
                break
            
            # If the last page had fewer than expected results, we're done
            if len(rentals) < self.results_per_page:
                print(f"   ✓ Last page had {len(rentals)} results (less than {self.results_per_page}), pagination complete")
                break
            
            # Fetch next page
            page_num += 1
            start_index += self.results_per_page
            
            print(f"   📄 Fetching page {page_num}...", end='', flush=True)
            
            # Small delay to be respectful to the server
            time.sleep(0.5)
            
            url = self.build_paginated_url(base_url, start_index)
            html = self.fetch_page(url)
            
            if not html:
                print(" failed! Stopping pagination.")
                break
            
            rentals = self.parse_rentals(html, url_id)
            
            if not rentals:
                print(f" no more results found")
                break
            
            all_rentals.extend(rentals)
            print(f" {len(rentals)} properties")
        
        # Remove duplicates based on property_id (in case of overlap)
        seen_ids = set()
        unique_rentals = []
        for rental in all_rentals:
            if rental['property_id'] not in seen_ids:
                seen_ids.add(rental['property_id'])
                unique_rentals.append(rental)
        
        if len(unique_rentals) != len(all_rentals):
            duplicates_removed = len(all_rentals) - len(unique_rentals)
            print(f"   ℹ️  Removed {duplicates_removed} duplicate(s)")
        
        return unique_rentals
    
    def save_snapshot(self, all_rentals):
        """Save current snapshot to CSV"""
        if not all_rentals:
            print("   No rentals to save")
            return
        
        fieldnames = ['url_id', 'property_id', 'timestamp', 'checkin_date', 'checkout_date', 'address', 'unit', 'price', 'bedrooms', 
                     'bathrooms', 'half_baths', 'property_type', 'url', 
                     'scraped_date', 'scraped_timestamp']
        
        with open(self.snapshot_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames,delimiter='\t')
            writer.writeheader()
            writer.writerows(all_rentals)
        
        print(f"   ✓ Snapshot saved: {self.snapshot_file}")
    
    def update_historical(self, all_rentals):
        """Append to historical data file"""
        if not all_rentals:
            return
        
        fieldnames = ['url_id', 'property_id', 'timestamp', 'checkin_date', 'checkout_date', 'address', 'unit', 'price', 'bedrooms', 
                     'bathrooms', 'half_baths', 'property_type', 'url', 
                     'scraped_date', 'scraped_timestamp']
        
        file_exists = os.path.isfile(self.historical_file)
        
        with open(self.historical_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames,delimiter='\t')
            if not file_exists:
                writer.writeheader()
            writer.writerows(all_rentals)
        
        print(f"   ✓ Historical data updated: {self.historical_file}")
    
    def analyze_changes_by_url(self, rentals_by_url, searches):
        """Compare with previous data to identify changes for each URL"""
        if not os.path.isfile(self.historical_file):
            print("\nℹ️  First run - no previous data to compare")
            return
        
        # Read all historical data
        historical = []
        with open(self.historical_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f,delimiter='\t')
            historical = list(reader)
        
        if not historical:
            print("\nℹ️  No previous data to compare")
            return
        
        # Get the most recent previous scrape date (not today's)
        dates = sorted(set(row['scraped_date'] for row in historical if row['scraped_date'] != self.date_only))
        if not dates:
            print("\nℹ️  No previous scrape to compare with")
            return
        
        previous_date = dates[-1]
        
        print(f"\n{'='*70}")
        print(f"📊 COMPARISON WITH {previous_date}")
        print('='*70)
        
        # Analyze each URL separately
        for search in searches:
            url_id = search['url_id']
            description = search['description']
            
            print(f"\n🔍 {url_id}: {description}")
            print("-" * 70)
            
            # Get previous and current listings for this URL_ID
            previous_for_url = [row for row in historical 
                               if row['scraped_date'] == previous_date 
                               and row['url_id'] == url_id]
            current_for_url = rentals_by_url.get(url_id, [])
            
            if not previous_for_url and not current_for_url:
                print("   ℹ️  No data for this search")
                continue
            
            previous_ids = set(row['property_id'] for row in previous_for_url)
            current_ids = set(rental['property_id'] for rental in current_for_url)
            
            # Identify changes
            new_listings = current_ids - previous_ids
            removed_listings = previous_ids - current_ids
            still_available = current_ids & previous_ids
            
            print(f"   📈 Summary:")
            print(f"      • Current listings: {len(current_for_url)}")
            print(f"      • New: {len(new_listings)}")
            print(f"      • Removed (sold/rented): {len(removed_listings)}")
            print(f"      • Still available: {len(still_available)}")
            
            # Show details of removed listings
            if removed_listings:
                print(f"\n   🏠 REMOVED LISTINGS (Likely Sold/Rented):")
                for prop_id in removed_listings:
                    prop = next((p for p in previous_for_url if p['property_id'] == prop_id), None)
                    if prop:
                        print(f"      • {prop['address']} - ${prop['price']} "
                              f"({prop['bedrooms']}bd/{prop['bathrooms']}ba)")
            
            # Show new listings
            if new_listings:
                print(f"\n   ✨ NEW LISTINGS:")
                for prop_id in new_listings:
                    prop = next((p for p in current_for_url if p['property_id'] == prop_id), None)
                    if prop:
                        print(f"      • {prop['address']} - ${prop['price']} "
                              f"({prop['bedrooms']}bd/{prop['bathrooms']}ba)")
            
            # Check for price changes
            price_changes = []
            for current in current_for_url:
                if current['property_id'] in still_available:
                    prev = next((p for p in previous_for_url 
                               if p['property_id'] == current['property_id']), None)
                    if prev and prev['price'] != current['price']:
                        price_changes.append({
                            'address': current['address'],
                            'old_price': prev['price'],
                            'new_price': current['price']
                        })
            
            if price_changes:
                print(f"\n   💰 PRICE CHANGES:")
                for change in price_changes:
                    print(f"      • {change['address']}: ${change['old_price']} → ${change['new_price']}")
            elif still_available:
                print(f"\n   💰 No price changes detected")
        
        # Update summary file
        self.update_summary(rentals_by_url, searches)
    
    def update_summary(self, rentals_by_url, searches):
        """Update the tracking summary file with per-URL stats"""
        fieldnames = ['date', 'timestamp', 'url_id', 'total_listings']
        
        file_exists = os.path.isfile(self.summary_file)
        
        with open(self.summary_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames,delimiter='\t')
            if not file_exists:
                writer.writeheader()
            
            for search in searches:
                url_id = search['url_id']
                rentals = rentals_by_url.get(url_id, [])
                
                writer.writerow({
                    'date': self.date_only,
                    'timestamp': self.timestamp,
                    'url_id': url_id,
                    'total_listings': len(rentals)
                })
        
        print(f"\n   ✓ Summary updated: {self.summary_file}")
    
    def run(self):
        """Main execution method"""
        print("=" * 70)
        print("🏖️  MULTI-URL RENTAL TRACKER - Sea Isle City")
        print("=" * 70)
        print(f"Scraping at: {self.timestamp}\n")
        
        # Load search configurations
        searches = self.load_search_urls()
        
        if not searches:
            print("❌ No search URLs loaded. Please add URLs to search_urls.csv")
            return
        
        print(f"✓ Loaded {len(searches)} search configurations\n")
        
        # Track all rentals across all URLs
        all_rentals = []
        rentals_by_url = {}
        
        # Process each search URL
        for i, search in enumerate(searches, 1):
            url_id = search['url_id']
            url = search['url']
            description = search['description']
            
            print(f"\n{'='*70}")
            print(f"[{i}/{len(searches)}] Processing: {url_id}")
            print(f"Description: {description}")
            print(f"URL: {url[:80]}..." if len(url) > 80 else f"URL: {url}")
            print("-" * 70)
            
            # Fetch all pages for this search
            rentals = self.fetch_all_pages(url, url_id)
            rentals_by_url[url_id] = rentals
            all_rentals.extend(rentals)
            
            if not rentals:
                print(f"   ⚠️  No rentals found for {url_id}")
                continue
            
            print(f"\n   ✅ Total found: {len(rentals)} rental properties")
            print(f"\n   📋 SUMMARY FOR {url_id}:")
            
            # Show summary stats
            if rentals:
                prices = [int(r['price']) for r in rentals]
                print(f"      • Total listings: {len(rentals)}")
                print(f"      • Price range: ${min(prices):,} - ${max(prices):,}")
                print(f"      • Average price: ${sum(prices)//len(prices):,}")
        
        # Save data
        if all_rentals:
            print(f"\n{'='*70}")
            print("💾 SAVING DATA")
            print("=" * 70)
            self.save_snapshot(all_rentals)
            self.update_historical(all_rentals)
            
            # Analyze changes
            self.analyze_changes_by_url(rentals_by_url, searches)
        else:
            print("\n⚠️  No rentals found across all searches")
        
        print("\n" + "=" * 70)
        print("✅ TRACKING COMPLETE!")
        print("=" * 70)
        print(f"\nTotal properties tracked: {len(all_rentals)}")
        print(f"Across {len(searches)} searches\n")


def main():
    tracker = MultiRentalTracker()
    tracker.run()


if __name__ == "__main__":
    main()
