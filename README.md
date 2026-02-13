# Multi-URL Sea Isle City Rental Tracker

A Python-based web scraper that monitors multiple rental search criteria on Freda Real Estate (callfreda.com), tracking availability, prices, and property details over time across different date ranges and search parameters.

## 🎯 Purpose

This tracker helps you:
- Monitor **multiple searches simultaneously** (different weeks, criteria, etc.)
- Track rental availability and price changes for each search
- Identify which properties get rented/sold
- Compare availability across different date ranges
- Analyze patterns in successful rentals

## ✨ Key Features

- **Multi-URL Tracking**: Monitor unlimited search configurations in parallel
- **Automatic Pagination**: Automatically fetches all pages of results (15, 30, 45+ properties)
- **URL_ID Grouping**: Each search has a unique identifier for easy filtering
- **Separate Analysis**: Compare results across different date ranges or criteria
- **Historical Tracking**: Maintains complete history for each search
- **Change Detection**: Identifies new, removed, and price-changed listings per search
- **CSV Storage**: Easy to analyze in Excel, filter by URL_ID, or query programmatically

## 📋 How It Works

### 1. Configuration File (`search_urls.csv`)

Define multiple searches in a simple CSV file:

```csv
url_id,url,description
URL_ID_1,https://callfreda.com/rentalresults.php?...,Beach Block 5-7bd Aug 22-29
URL_ID_2,https://callfreda.com/rentalresults.php?...,Beach Block 5-7bd Aug 15-22
URL_ID_3,https://callfreda.com/rentalresults.php?...,Beach Block 5-7bd Aug 29-Sep 5
```

**Fields:**
- `url_id`: Unique identifier (e.g., URL_ID_1, WEEK1_SEARCH, etc.)
- `url`: Full search results URL from the website (base URL without `&start=` parameter)
- `description`: Human-readable description

**Note on Pagination:** Just provide the base URL! The tracker automatically handles pagination if your search has more than 15 results. See `PAGINATION.md` for details.

### 2. Output Format

All CSV files include `url_id` as the first column, allowing you to:
- Filter data in Excel by URL_ID
- Track specific searches independently
- Compare across different date ranges

**Example Output:**
```csv
url_id,property_id,address,price,bedrooms,bathrooms,...
URL_ID_1,144437,28 63rd Street West,5500,5,3,...
URL_ID_1,80842,25 68th St,4000,5,3,...
URL_ID_2,144437,28 63rd Street West,5500,5,3,...
URL_ID_3,98765,15 75th Street,4800,5,3,...
```

## 🔧 Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Your Searches**
   
   Edit `search_urls.csv` with your desired search URLs:
   
   a. Go to https://callfreda.com/vacationrentals.php
   b. Enter your search criteria (dates, bedrooms, price, etc.)
   c. Click "View Rentals"
   d. Copy the full URL from your browser
   e. Add a row to `search_urls.csv` with a unique URL_ID

3. **Run First Scrape**
   ```bash
   python rental_tracker.py
   ```

## 🚀 Usage

### Basic Tracking

Run the tracker manually:
```bash
python rental_tracker.py
```

**Output shows results for each URL_ID:**
```
======================================================================
[1/3] Processing: URL_ID_1
Description: Beach Block, 5-7bd, 3ba, Aug 22-29
----------------------------------------------------------------------
   ✓ Found 4 rental properties

   📋 CURRENT LISTINGS FOR URL_ID_1:
      • 28 63rd Street West (West)
        $5,500 | 5bd/3ba | Condo
      ...

======================================================================
[2/3] Processing: URL_ID_2
Description: Beach Block, 5-7bd, 3ba, Aug 15-22
----------------------------------------------------------------------
   ✓ Found 3 rental properties
   ...
```

### Running Analysis

Analyze historical data with URL_ID grouping:
```bash
python analyze_rentals.py
```

**Output includes:**
- Comparison across all URL_IDs
- Separate analysis for each search
- Sold properties by URL_ID
- Price trends by URL_ID

## 📁 Output Files

All files are stored in the `rental_data/` directory:

### 1. Snapshot Files
- **Format**: `snapshot_YYYY-MM-DD_HH-MM-SS.csv`
- **Contains**: All current listings across all URL_IDs
- **URL_ID Column**: First column for easy filtering

### 2. Historical Data
- **File**: `historical_data.csv`
- **Contains**: All scraped data with timestamps and URL_IDs
- **Usage**: Filter by URL_ID in Excel to see specific search history

### 3. Tracking Summary
- **File**: `tracking_summary.csv`
- **Contains**: Daily metrics for each URL_ID
- **Usage**: Quick overview of listing counts per search

## 📊 Data Fields

Each rental listing includes:

| Field | Description |
|-------|-------------|
| `url_id` | Search identifier (URL_ID_1, URL_ID_2, etc.) |
| `property_id` | Unique property identifier from website |
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

## 💡 Use Cases

### Track Multiple Weeks
Monitor availability for different vacation weeks:
```csv
url_id,url,description
WEEK1,https://callfreda.com/...checkin=07/01/2026...,July 1-8
WEEK2,https://callfreda.com/...checkin=07/08/2026...,July 8-15
WEEK3,https://callfreda.com/...checkin=07/15/2026...,July 15-22
```

### Compare Price Ranges
Track same dates with different price limits:
```csv
url_id,url,description
BUDGET,https://callfreda.com/...MX=5000...,Under $5k
MIDRANGE,https://callfreda.com/...MX=7000...,Under $7k
LUXURY,https://callfreda.com/...MX=999000...,All prices
```

### Monitor Different Locations
Track different areas in Sea Isle:
```csv
url_id,url,description
BEACH_BLOCK,https://callfreda.com/...TW=Beach%20Block...,Beach Block
BEACHFRONT,https://callfreda.com/...TW=Beachfront...,Beachfront
OCEANSIDE,https://callfreda.com/...TW=Oceanside...,Oceanside
```

## 🔍 Analyzing Your Data

### In Excel/Google Sheets

1. Open `historical_data.csv`
2. Filter by `url_id` column to see specific search
3. Create pivot tables by URL_ID
4. Chart trends over time per search

### Using the Analysis Script

```bash
python analyze_rentals.py
```

**Shows per URL_ID:**
- How many properties available over time
- Which properties were sold/rented
- Price changes within each search
- Average prices across searches

### Example Analysis Output

```
📊 COMPARISON ACROSS ALL SEARCHES
======================================================================
Latest Data: 2026-02-12

🔍 URL_ID_1:
   Listings: 4
   Price Range: $4,000 - $5,500
   Average Price: $4,850

🔍 URL_ID_2:
   Listings: 3
   Price Range: $3,800 - $5,200
   Average Price: $4,333

======================================================================
🏠 SOLD/RENTED PROPERTIES ANALYSIS - URL_ID_1
----------------------------------------------------------------------
Total Sold/Rented: 2
Average Price: $4,850
```

## 🔄 Automated Daily Scraping

### Linux/Mac (Cron)

```bash
crontab -e
```

Add line (runs at 9 AM daily):
```
0 9 * * * cd /path/to/rental-tracker && python rental_tracker.py >> rental_data/scraper.log 2>&1
```

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 9:00 AM
4. Action: Start a program
   - Program: `python`
   - Arguments: `rental_tracker.py`
   - Start in: Your folder path

## 🎨 Customizing URL_IDs

URL_IDs can be any unique string. Use descriptive names:

**Good Examples:**
- `JULY_WEEK1`, `JULY_WEEK2`, `JULY_WEEK3`
- `BUDGET_SEARCH`, `LUXURY_SEARCH`
- `5BD_SEARCH`, `6BD_SEARCH`, `7BD_SEARCH`
- `BEACHBLOCK_AUG`, `BEACHFRONT_AUG`

**Avoid:**
- Duplicate URL_IDs across different searches
- Very long IDs (keep under 20 characters for readability)
- Special characters (stick to letters, numbers, underscores)

## 📈 Sample Workflow

### Week 1: Setup Multiple Searches
```bash
# Edit search_urls.csv with 3 different weeks
python rental_tracker.py
# Output: Baseline established for all 3 searches
```

### Week 2-4: Daily Tracking
```bash
# Run daily (or use cron/Task Scheduler)
python rental_tracker.py
# Output: Shows changes per URL_ID
```

### Week 5: Analysis
```bash
python analyze_rentals.py
# Output: Comprehensive insights per search
```

## 🛠️ Troubleshooting

### "Config file not found"
The script will create a sample `search_urls.csv` automatically. Edit it with your URLs.

### "No rentals found for URL_ID_X"
- Check if the URL is correct
- Verify the website is accessible
- That search might genuinely have 0 results

### Excel: Filter by URL_ID
1. Open CSV in Excel
2. Click on column A header (url_id)
3. Use AutoFilter dropdown
4. Select specific URL_ID(s)

## 🎯 Pro Tips

1. **Descriptive URL_IDs**: Use meaningful names like `AUG_WEEK1` instead of `URL_ID_1`
2. **Track Early**: Start 6+ months before your target dates
3. **Multiple Searches**: More searches = better comparison data
4. **Regular Analysis**: Run `analyze_rentals.py` weekly to spot trends
5. **Export by URL_ID**: In Excel, filter and save separate sheets per search

## 📞 Example Configurations

### Scenario 1: Finding the Best Week
```csv
url_id,url,description
AUG_WK1,https://callfreda.com/...checkin=08/01/2026...,Aug 1-8
AUG_WK2,https://callfreda.com/...checkin=08/08/2026...,Aug 8-15
AUG_WK3,https://callfreda.com/...checkin=08/15/2026...,Aug 15-22
AUG_WK4,https://callfreda.com/...checkin=08/22/2026...,Aug 22-29
```

### Scenario 2: Finding the Right Price Point
```csv
url_id,url,description
UNDER_4K,https://callfreda.com/...MX=4000...,Budget under $4k
MID_4K_6K,https://callfreda.com/...MN=4000&MX=6000...,Mid-range $4-6k
OVER_6K,https://callfreda.com/...MN=6000...,Premium over $6k
```

---

**Track smarter, not harder! 🏖️**
