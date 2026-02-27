# 📜 Verification History - Quick Start Guide

## 🎯 How to Use Verification History

### Step 1: Verify Some Emails

**Option A: Single Verification**
1. Go to "Single Verify" tab
2. Enter an email (e.g., `test@gmail.com`)
3. Click "Verify Email"
4. ✅ Email is automatically logged to history

**Option B: Bulk Verification**
1. Go to "Bulk Verify" tab
2. Upload a CSV file with emails
3. Click "Start Bulk Process"
4. ✅ All emails are automatically logged to history

---

### Step 2: View Your History

1. Click on the **"Verification History"** tab
2. You'll see all your verified emails with:
   - ⏰ **Timestamp** - When it was verified
   - 📧 **Email** - The email address
   - ✅ **Status** - Valid / Invalid / Risky
   - 📊 **Score** - Trust score (0.00 - 0.99)
   - 📍 **Source** - Single or Bulk
   - 💬 **Reason** - Why it got that status
   - 🏷️ **Flags** - Is_Free, Is_Role, Is_Disposable

---

### Step 3: Filter Your Results

**Filter by Status:**
- Click "Filter by Status" dropdown
- Select: All / Valid / Invalid / Risky
- Table updates instantly

**Filter by Source:**
- Click "Filter by Source" dropdown
- Select: All / Single / Bulk
- See only verifications from that source

**Limit Entries:**
- Click "Show entries" dropdown
- Select: 50 / 100 / 250 / 500 / 1000
- Control how many rows to display

---

### Step 4: Export Your History

1. Click **"📥 Download Full History"** button
2. A CSV file will download: `verification_history.csv`
3. Open in Excel, Google Sheets, or any spreadsheet app
4. All columns included (even filtered-out entries)

---

### Step 5: Manage Your History

**Refresh:**
- Click **"🔄 Refresh"** button
- Reloads the page and updates the view

**Clear All:**
- Click **"🗑️ Clear"** button
- Removes all history entries
- ⚠️ This cannot be undone (download first if needed!)

---

## 📊 Understanding the History Table

### Column Descriptions:

| Column | What It Means | Example |
|--------|---------------|---------|
| **Timestamp** | When you verified this email | `2026-02-10 14:43:22` |
| **Email** | The email address checked | `john.doe@example.com` |
| **Status** | Verification result | `Valid` / `Invalid` / `Risky` |
| **Score** | Trust score (higher = better) | `0.95` (95% trustworthy) |
| **Source** | How it was verified | `Single` or `Bulk` |
| **Reason** | Why it got this status | `Verified (MX Records found)` |
| **Is_Free** | Free email provider? | `True` (Gmail, Yahoo, etc.) |
| **Is_Role** | Role-based email? | `True` (admin@, info@, etc.) |
| **Is_Disposable** | Temporary email? | `True` (tempmail, etc.) |

---

## 🎨 Visual Examples

### Example 1: Empty History (First Time)
```
┌─────────────────────────────────────────────┐
│  📜 Verification Log   [🔄 Refresh] [🗑️ Clear] │
├─────────────────────────────────────────────┤
│                                             │
│              📭                             │
│   No verification history found.            │
│   Start verifying emails to see history.    │
│                                             │
└─────────────────────────────────────────────┘
```

### Example 2: History with Entries
```
┌─────────────────────────────────────────────────────────────────┐
│  📜 Verification Log        [🔄 Refresh]  [🗑️ Clear]              │
├─────────────────────────────────────────────────────────────────┤
│  Total Verifications: 15                                        │
│                                                                 │
│  Filter by Status: [All ▼]  Source: [All ▼]  Show: [100 ▼]    │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  Timestamp           Email              Status  Score  Source   │
│  ──────────────────  ─────────────────  ──────  ─────  ──────  │
│  2026-02-10 14:43:22 test@gmail.com     Valid   0.85   Single  │
│  2026-02-10 14:42:15 admin@company.com  Risky   0.65   Bulk    │
│  2026-02-10 14:41:30 fake@tempmail.com  Invalid 0.00   Single  │
│  2026-02-10 14:40:12 john@business.org  Valid   0.92   Bulk    │
│  ...                                                            │
│                                                                 │
│  [📥 Download Full History]                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Common Use Cases

### Use Case 1: Quality Check After Bulk Upload
**Scenario:** You uploaded 500 emails and want to review the results

**Steps:**
1. Go to "Verification History" tab
2. Filter by Source: "Bulk"
3. Filter by Status: "Invalid"
4. Review all invalid emails
5. Download for further analysis

### Use Case 2: Find All Free Email Providers
**Scenario:** You want to see which emails are from Gmail, Yahoo, etc.

**Steps:**
1. Go to "Verification History" tab
2. Download full history
3. Open CSV in Excel
4. Filter column "Is_Free" = True
5. See all free provider emails

### Use Case 3: Audit Trail
**Scenario:** You need to prove when you verified certain emails

**Steps:**
1. Go to "Verification History" tab
2. Look at Timestamp column
3. Download as proof/record
4. Share CSV with team/client

### Use Case 4: Re-verify Old Emails
**Scenario:** You verified emails last week, want to check them again

**Steps:**
1. Go to "Verification History" tab
2. Download full history
3. Extract email column
4. Create new CSV with those emails
5. Upload to "Bulk Verify" tab

---

## 💡 Pro Tips

### Tip 1: Download Before Clearing
Always download your history before clicking "Clear" - you can't undo it!

### Tip 2: Use Filters for Analysis
Combine filters to find specific patterns:
- Status: "Invalid" + Source: "Bulk" = See all bulk failures
- Status: "Risky" = Review questionable emails

### Tip 3: Check Timestamps
Use timestamps to track verification batches and timing

### Tip 4: Monitor Flags
Watch the Is_Free, Is_Role, Is_Disposable columns to understand email quality

### Tip 5: Regular Exports
Download history daily/weekly for long-term records

---

## ⚠️ Important Notes

### Session-Based Storage
- History is stored in your browser session
- **Refreshing the page will clear history**
- **Closing the browser will clear history**
- **Each browser tab has separate history**

### Recommendation:
📥 **Download your history before closing the browser!**

### Memory Limit
- Maximum 1,000 entries stored
- Oldest entries automatically removed when limit reached
- Download regularly if you verify more than 1,000 emails

---

## 🐛 Troubleshooting

### Problem: "No verification history found"
**Solution:** 
- Verify at least one email first
- Switch to "Verification History" tab
- Click "🔄 Refresh" button

### Problem: History disappeared
**Solution:**
- Did you refresh the page? History is session-based
- Did you click "Clear"? Cannot be undone
- Download history regularly to prevent loss

### Problem: Can't see all entries
**Solution:**
- Change "Show entries" to higher number (500 or 1000)
- Or download full history as CSV

### Problem: Filters not working
**Solution:**
- Make sure you have entries matching the filter
- Try "All" to reset filters
- Click "🔄 Refresh" to reload

---

## 📈 What Gets Logged?

### ✅ Logged Automatically:
- Single email verifications
- Bulk email verifications (all emails)
- Valid emails
- Invalid emails
- Risky emails
- Cached results (when re-verified)

### ❌ NOT Logged:
- Emails with invalid format (caught before verification)
- Emails that fail to process due to errors

---

## 🎯 Quick Actions

| I Want To... | Do This... |
|--------------|------------|
| See all verifications | Go to "Verification History" tab |
| See only valid emails | Filter by Status: "Valid" |
| See only bulk results | Filter by Source: "Bulk" |
| Export everything | Click "📥 Download Full History" |
| Start fresh | Click "🗑️ Clear" |
| Update the view | Click "🔄 Refresh" |
| Show more rows | Change "Show entries" to 500 or 1000 |

---

## 📊 Sample History CSV Export

When you download, you'll get a CSV like this:

```csv
Timestamp,Email,Status,Score,Source,Reason,Is_Free,Is_Role,Is_Disposable
2026-02-10 14:43:22,test@gmail.com,Valid,0.85,Single,Verified (MX Records found),True,False,False
2026-02-10 14:42:15,admin@company.com,Risky,0.65,Bulk,Role-based account,False,True,False
2026-02-10 14:41:30,fake@tempmail.com,Invalid,0.00,Single,Disposable domain detected,False,False,True
2026-02-10 14:40:12,john@business.org,Valid,0.92,Bulk,Verified (MX Records found),False,False,False
```

Open this in Excel/Sheets for advanced analysis!

---

## ✅ Success Checklist

- [ ] Verified at least one email
- [ ] Opened "Verification History" tab
- [ ] See entries in the table
- [ ] Tried filtering by Status
- [ ] Tried filtering by Source
- [ ] Downloaded history as CSV
- [ ] Understand session-based storage
- [ ] Know to download before closing browser

---

**🎉 You're now a Verification History expert!**

For technical details, see: `VERIFICATION_HISTORY_FIX.md`
