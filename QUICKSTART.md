# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies (30 seconds)

Open your terminal and run:

```bash
pip install requests beautifulsoup4
```

### Step 2: Run Your First Scrape (10 seconds)

```bash
python rental_tracker.py
```

You'll see output like:
```
============================================================
🏖️  RENTAL TRACKER - Sea Isle City Beach Block
============================================================
✓ Found 4 rental properties

📋 CURRENT LISTINGS:
   • 28 63rd Street West (West)
     $5,500 | 5bd/3ba | Condo
   ...

💾 SAVING DATA:
✓ Snapshot saved: rental_data/snapshot_2026-02-12_09-00-00.csv
✓ Historical data updated: rental_data/historical_data.csv
```

### Step 3: Run Daily & Analyze

**Set up daily automation** (choose your method):

**Mac/Linux (Cron):**
```bash
# Edit crontab
crontab -e

# Add this line (runs at 9 AM daily)
0 9 * * * cd /path/to/your/folder && python rental_tracker.py >> rental_data/scraper.log 2>&1
```

**Windows (Task Scheduler):**
1. Search for "Task Scheduler" in Start menu
2. Click "Create Basic Task"
3. Name: "Rental Tracker"
4. Trigger: Daily at 9:00 AM
5. Action: Start a program
   - Program: `python`
   - Arguments: `rental_tracker.py`
   - Start in: Your folder path

**After a few days, run analysis:**
```bash
python analyze_rentals.py
```

## 📂 Understanding Your Data

### What Gets Created

After your first run, you'll have a `rental_data/` folder with:

1. **snapshot_[timestamp].csv** - Current listings at that moment
2. **historical_data.csv** - All data from all runs
3. **tracking_summary.csv** - High-level metrics

### Example: What You'll Learn

After tracking for a week, the analysis will show:

```
🏠 REMOVED LISTINGS (Likely Sold/Rented):
   • 15 75th Street - $4,800 (5bd/3ba)
   
💰 PRICE CHANGES:
   • 22 78th Street: $5,000 → $4,750

📊 SOLD PROPERTY STATISTICS:
   Average Price: $4,800
   Properties Under $5,000 rent faster
```

## 🎯 What to Look For

### Week 1-2: Establish Baseline
- How many properties are available?
- What's the price range?
- Which properties stay listed?

### Week 3-4: Identify Patterns
- Did cheaper properties rent first?
- Are condos or townhomes more popular?
- Do price drops work?

### Week 5+: Make Decisions
- Sweet spot pricing (not too high, not too low)
- Best property characteristics
- Optimal booking timing

## 💡 Pro Tips

1. **Start Early**: Begin tracking 6+ months before your target dates
2. **Track Multiple Searches**: Run separate trackers for different date ranges
3. **Note External Events**: Add comments about holidays, events affecting prices
4. **Export to Excel**: Open CSVs in Excel for custom charts and analysis
5. **Share with Travel Group**: Help everyone find the best deal

## 🔧 Customizing Your Search

Want to track different criteria? Easy!

1. Go to: https://callfreda.com/vacationrentals.php
2. Enter your criteria (dates, bedrooms, price, etc.)
3. Click "View Rentals"
4. Copy the URL from your browser
5. Open `rental_tracker.py`
6. Replace the URL on line ~271 with yours
7. Save and run!

## 📊 Sample Data Included

Check the `example_data/` folder to see what your output will look like:
- Real property data structure
- Multiple days of tracking
- Example of a property getting rented

## ⚡ Troubleshooting

**"pip not found"**
- Install Python from python.org (includes pip)

**"No module named 'requests'"**
- Run: `pip install requests beautifulsoup4`

**"No rentals found"**
- Check your internet connection
- Make sure the URL is correct
- Website might be temporarily down

**Want to test without waiting?**
- Run the script 2-3 times manually (hours apart)
- Edit dates in historical_data.csv to simulate days passing
- Run analyze_rentals.py to see comparison features

## 📞 Need Help?

The README.md file has comprehensive documentation including:
- Detailed feature explanations
- Advanced scheduling options
- Data field descriptions
- Analysis interpretation

---

**You're ready! Run `python rental_tracker.py` now! 🏖️**
