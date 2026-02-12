# Sea Isle City Rental Tracker

A Python-based web scraper that monitors beach block rental properties on Freda Real Estate (callfreda.com), tracking availability, prices, and property details over time.

## 🎯 Purpose

This tracker helps you:
- Monitor rental availability for specific search criteria
- Track price changes over time
- Identify which properties get rented/sold
- Analyze patterns in successful rentals (price, bedrooms, etc.)

## 📋 Features

- **Daily Scraping**: Captures current listings with all details
- **Historical Tracking**: Maintains complete history in CSV format
- **Change Detection**: Identifies new, removed, and price-changed listings
- **Analysis Tools**: Generates insights about sold properties and trends
- **CSV Storage**: Easy to analyze in Excel, Google Sheets, or Python

## 🔧 Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify Setup**
   ```bash
   python rental_tracker.py
   ```

## 🚀 Usage

### Basic Tracking

Run the tracker manually:
```bash
python rental_tracker.py
```

This will:
- Scrape the current listings
- Save a timestamped snapshot
- Update historical data
- Compare with previous runs
- Display changes in the terminal

### Automated Daily Scraping

#### Option 1: Cron (Linux/Mac)

Add to your crontab to run daily at 9 AM:
```bash
crontab -e
```

Add this line (adjust path to your script location):
```
0 9 * * * cd /path/to/rental-tracker && python rental_tracker.py >> rental_data/scraper.log 2>&1
```

#### Option 2: Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 9:00 AM
4. Action: Start a program
   - Program: `python`
   - Arguments: `rental_tracker.py`
   - Start in: `C:\path\to\rental-tracker`

#### Option 3: Python Script (Cross-platform)

Create a scheduled runner script:
```python
import schedule
import time
from rental_tracker import RentalTracker

def run_tracker():
    url = "https://callfreda.com/rentalresults.php?..."  # Your URL
    tracker = RentalTracker(url)
    tracker.run()

# Run daily at 9 AM
schedule.every().day.at("09:00").do(run_tracker)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Running Analysis

Generate insights from collected data:
```bash
python analyze_rentals.py
```

This provides:
- Statistics on sold/rented properties
- Price change analysis
- Availability trends over time
- Average prices and property characteristics

## 📁 Output Files

All files are stored in the `rental_data/` directory:

### 1. Snapshot Files
- **Format**: `snapshot_YYYY-MM-DD_HH-MM-SS.csv`
- **Contains**: Current listings at that specific time
- **Use**: Point-in-time view of available rentals

### 2. Historical Data
- **File**: `historical_data.csv`
- **Contains**: All scraped data with timestamps
- **Use**: Complete tracking history for analysis

### 3. Tracking Summary
- **File**: `tracking_summary.csv`
- **Contains**: High-level metrics for each scrape
- **Use**: Quick overview of changes over time

## 📊 Data Fields

Each rental listing includes:

| Field | Description |
|-------|-------------|
| `property_id` | Unique identifier from website |
| `address` | Street address |
| `unit` | Unit designation (East, West, etc.) |
| `price` | Weekly rental price |
| `bedrooms` | Number of bedrooms |
| `bathrooms` | Number of full bathrooms |
| `half_baths` | Number of half bathrooms |
| `property_type` | Condo, Townhome, House, etc. |
| `url` | Direct link to property page |
| `scraped_date` | Date of scraping (YYYY-MM-DD) |
| `scraped_timestamp` | Full timestamp |

## 🔍 Understanding the Output

### Terminal Output Example

```
📊 COMPARISON WITH 2026-02-11:
   New listings: 1
   Removed (sold/rented): 2
   Still available: 2

🏠 REMOVED LISTINGS (Likely Sold/Rented):
   • 28 63rd Street West - $5,500 (5bd/3ba)
   • 42 78th Street East - $4,900 (5bd/3ba)

✨ NEW LISTINGS:
   • 15 75th Street - $4,800 (5bd/3ba)

💰 PRICE CHANGES:
   • 22 78th Street: $5,000 → $4,750
```

### Analysis Insights

The `analyze_rentals.py` script provides:

**Sold Properties Analysis**
- Average price of rented properties
- Most common property types
- Price ranges that rent fastest

**Price Trends**
- How often prices change
- Average increase/decrease amounts
- Properties with significant price drops

**Availability Trends**
- How inventory changes over time
- Seasonal patterns (with enough data)

## 🎯 Customizing Your Search

To monitor different criteria, update the URL in `rental_tracker.py`:

```python
# Current URL searches for:
# - Check-in: 08/22/2026
# - Check-out: 08/29/2026
# - Bedrooms: 5-7
# - Bathrooms: 3
# - Location: Beach Block
# - Price: $0-$999,000
# - Amenities: Air Conditioning, Outside Shower, Washer, Dryer

# To change criteria:
# 1. Go to https://callfreda.com/vacationrentals.php
# 2. Select your desired criteria
# 3. Click "View Rentals"
# 4. Copy the full URL from the results page
# 5. Replace the URL in the script
```

## 📈 Tips for Best Results

1. **Run Daily**: More frequent data = better insights
2. **Track Full Season**: Start tracking early (Jan-Feb for summer)
3. **Monitor Price Drops**: Properties with reduced prices may indicate flexibility
4. **Note Patterns**: Properties that rent quickly often share characteristics
5. **Compare Weeks**: Different weeks have different availability/pricing

## 🔐 Data Privacy

- All data scraped is publicly available on the website
- No personal information or authentication required
- Data stored locally on your machine
- Not shared or transmitted anywhere

## ⚠️ Important Notes

- **Respectful Scraping**: Script includes delays and proper headers
- **Website Changes**: If the site structure changes, parsing may break
- **Legal**: Review the website's Terms of Service for scraping policies
- **Rate Limiting**: Don't run more frequently than once per hour

## 🐛 Troubleshooting

### "No rentals found"
- Check if the URL is still valid
- Website structure may have changed
- Run manually and check terminal output

### "Error fetching page"
- Check your internet connection
- Website may be temporarily down
- Try again in a few minutes

### Empty CSV files
- First run creates structure but needs data
- Run at least twice to see comparisons

## 📞 Search Criteria Info

Your current search is for:
- **Dates**: Aug 22-29, 2026 (1 week)
- **Bedrooms**: 5-7
- **Bathrooms**: 3
- **Location**: Beach Block only
- **Max Price**: $999,000
- **Required Amenities**: Air Conditioning, Outside Shower, Washer, Dryer

## 🎓 Next Steps

After collecting a week of data:
1. Run `python analyze_rentals.py` to see patterns
2. Look for properties that rented quickly
3. Note the price range that moves fastest
4. Check if certain property types are more popular
5. Use insights to inform your rental decisions

## 📝 Example Analysis Workflow

```bash
# Day 1: First run
python rental_tracker.py
# Output: 4 properties found, baseline established

# Day 2: Second run
python rental_tracker.py
# Output: 3 properties (1 rented), identifies which one

# Day 7: After a week
python analyze_rentals.py
# Output: Insights on rented properties
```

---

**Happy Tracking! 🏖️**
