# Pagination Guide

## 🔄 Automatic Multi-Page Support

The tracker now **automatically handles pagination** for searches with more than 15 results!

## How It Works

### The Problem
Freda Real Estate shows 15 results per page. If your search has 47 results, you'd see:
- Page 1: Results 1-15
- Page 2: Results 16-30 (URL ends with `&start=15`)
- Page 3: Results 31-45 (URL ends with `&start=30`)
- Page 4: Results 46-47 (URL ends with `&start=45`)

### The Solution
The tracker **automatically**:
1. Fetches page 1
2. Detects total results (e.g., "47 properties")
3. Calculates pages needed (47 ÷ 15 = 4 pages)
4. Fetches pages 2, 3, 4 automatically
5. Combines all results into one dataset

## What You See

### Terminal Output Example

```
======================================================================
[1/1] Processing: URL_ID_1
Description: Beach Block, 5-7bd, 3ba, Aug 22-29
----------------------------------------------------------------------
   📄 Fetching page 1... found 47 total results
   📊 Expecting approximately 4 pages
   ✓ Page 1: 15 properties
   📄 Fetching page 2... 15 properties
   📄 Fetching page 3... 15 properties
   📄 Fetching page 4... 2 properties
   ✓ Last page had 2 results (less than 15), pagination complete

   ✅ Total found: 47 rental properties
```

## Your Configuration File

**You DON'T need to do anything special!**

Just use the base URL without any `&start=` parameter:

```csv
url_id,url,description
URL_ID_1,https://callfreda.com/rentalresults.php?vr=view&checkin=08/22/2026&checkout=08/29/2026&BD=5&MBD=7&BTH=3&MBTH=3&TW=Beach%20Block&MN=0&MX=999000,All beach block properties
```

The tracker will:
- Try page 1
- If results found, try page 2 (`&start=15`)
- If results found, try page 3 (`&start=30`)
- Continue until no more results

## Edge Cases Handled

### 1. URL Already Has &start=
If you accidentally include `&start=15` in your config:
```csv
URL_ID_1,https://callfreda.com/...&start=15,My search
```

The tracker **removes it** and starts from page 1 automatically.

### 2. Unknown Total Results
If the page doesn't show total count:
- Tracker keeps fetching pages until it gets an empty page
- Ensures all results are captured

### 3. Duplicate Properties
If a property appears on multiple pages (edge case):
- Tracker automatically deduplicates by `property_id`
- You'll see: "Removed 1 duplicate(s)"

### 4. Server Errors
If a page fails to load:
- Tracker stops pagination gracefully
- Saves whatever was successfully fetched
- Shows error message

## Benefits

### ✅ Complete Data
No more missing properties because they were on page 2 or 3!

### ✅ No Manual Work
You don't need to:
- Count how many pages exist
- Create multiple URLs with different `&start=` values
- Manually combine results

### ✅ Respectful Scraping
- 0.5 second delay between pages
- Proper error handling
- Stops when no more results found

## Performance Notes

### Small Searches (< 15 results)
- One page fetch
- Very fast (2-3 seconds)

### Medium Searches (15-45 results)
- 2-3 page fetches
- Takes ~5-10 seconds
- Includes delays between requests

### Large Searches (100+ results)
- 7+ page fetches
- May take 30-60 seconds
- Worth it for complete data!

## Verification

### Check Total in CSV
After running, open `snapshot_[timestamp].csv` and filter by `url_id`:
- Count rows for that URL_ID
- Should match the total shown in terminal

### Example
Terminal says: "found 47 total results"
CSV filtered by URL_ID_1 should have: 47 rows

## Troubleshooting

### "No more results found" on page 2
**Cause**: Website might have changed or search truly has < 15 results
**Solution**: Check the URL in browser to verify

### Takes a long time
**Cause**: Large search with many pages
**Solution**: This is normal! Be patient, it's getting all data

### Removed duplicates message
**Cause**: Property appeared on multiple pages (rare)
**Solution**: No action needed, tracker handles it

### Page fetch failed
**Cause**: Network issue or website temporarily down
**Solution**: Re-run the tracker, it will try again

## Examples

### Example 1: Small Search (4 results)
```
   📄 Fetching page 1... found 4 total results
   📊 Expecting approximately 1 pages
   ✓ Page 1: 4 properties
   ✓ Last page had 4 results (less than 15), pagination complete
```

### Example 2: Medium Search (32 results)
```
   📄 Fetching page 1... found 32 total results
   📊 Expecting approximately 3 pages
   ✓ Page 1: 15 properties
   📄 Fetching page 2... 15 properties
   📄 Fetching page 3... 2 properties
   ✓ Last page had 2 results (less than 15), pagination complete
```

### Example 3: Large Search (127 results)
```
   📄 Fetching page 1... found 127 total results
   📊 Expecting approximately 9 pages
   ✓ Page 1: 15 properties
   📄 Fetching page 2... 15 properties
   📄 Fetching page 3... 15 properties
   📄 Fetching page 4... 15 properties
   📄 Fetching page 5... 15 properties
   📄 Fetching page 6... 15 properties
   📄 Fetching page 7... 15 properties
   📄 Fetching page 8... 15 properties
   📄 Fetching page 9... 7 properties
   ✓ Last page had 7 results (less than 15), pagination complete
```

## Best Practices

### 1. Broader Searches = More Pages
If you want to track ALL available properties:
```csv
url_id,url,description
ALL_PROPS,https://callfreda.com/...BD=1&MBD=10&MX=999000,Track everything
```

This might return 200+ results across 14 pages - that's fine!

### 2. Specific Searches = Faster
If you only care about specific criteria:
```csv
url_id,url,description
EXACT,https://callfreda.com/...BD=5&MBD=5&BTH=3&MBTH=3,Exactly 5bd/3ba
```

This might return 8 results on 1 page - very fast!

### 3. Multiple Targeted Searches
Better to have:
- 3 searches with 20 results each (1-2 pages)
  
Than:
- 1 search with 200 results (14 pages)

More targeted = faster + more relevant data

---

**The pagination is fully automatic - just sit back and let it work! 🚀**
