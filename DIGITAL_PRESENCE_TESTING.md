# Digital Presence Check - Quick Testing Guide

## 🧪 How to Test the New Feature

### Prerequisites
- ✅ Backend running on `http://localhost:3000`
- ✅ Frontend running on `http://localhost:8501`
- ✅ Internet connection (for external checks)

---

## Test 1: Single Email with Gravatar

### Steps:
1. Go to `http://localhost:8501`
2. Navigate to "Single Verify" tab
3. Enter email: `beau@dentedreality.com.au` (known Gravatar user)
4. Click "Verify Email"

### Expected Results:
- ✅ Status: Valid or Risky
- ✅ Digital Presence metric shows: **40-100%**
- ✅ Sources shown: "Gravatar" (and possibly others)
- ✅ Expandable section "🌐 Digital Presence Details" available
- ✅ Click to expand shows:
  - Presence Score metric
  - "Strong digital presence detected" or similar
  - ✅ Gravatar in sources list
  - Link to Gravatar profile

---

## Test 2: Corporate Email

### Steps:
1. Single Verify tab
2. Enter email: `contact@microsoft.com`
3. Click "Verify Email"

### Expected Results:
- ✅ Digital Presence: **20-40%**
- ✅ Sources: "Domain Website", "Corporate Domain"
- ✅ Reason: "Moderate digital presence"
- ✅ No Gravatar link (likely not found)

---

## Test 3: Free Provider (No Presence)

### Steps:
1. Single Verify tab
2. Enter email: `randomtest12345@gmail.com` (non-existent)
3. Click "Verify Email"

### Expected Results:
- ✅ Digital Presence: **0%**
- ✅ Sources: "None Found"
- ✅ No expandable section (no presence detected)
- ✅ Metric shows gray color

---

## Test 4: Disposable Email

### Steps:
1. Single Verify tab
2. Enter email: `test@tempmail.com`
3. Click "Verify Email"

### Expected Results:
- ✅ Status: Invalid (disposable)
- ✅ Digital Presence: **0%**
- ✅ Sources: "None Found"
- ✅ Overall trust score very low

---

## Test 5: Bulk Processing

### Create Test CSV:

**test_presence.csv:**
```csv
email
beau@dentedreality.com.au
contact@microsoft.com
random@gmail.com
test@tempmail.com
admin@google.com
```

### Steps:
1. Go to "Bulk Verify" tab
2. Upload `test_presence.csv`
3. Click "Start Bulk Process"
4. Wait for completion

### Expected Results:
- ✅ All 5 emails processed
- ✅ Progress bar shows batches
- ✅ Results table includes presence data
- ✅ Download CSV includes presence columns
- ✅ Processing time: ~20-30 seconds

### Check Downloaded CSV:
Should include columns:
- `Email`
- `Status`
- `Score`
- `Presence_Score` (or similar)
- `Presence_Sources`

---

## Test 6: Cache Performance

### Steps:
1. Verify email: `test@example.com`
2. Note the processing time (~4-6 seconds)
3. Immediately verify the SAME email again
4. Note the processing time

### Expected Results:
- ✅ First verification: 4-6 seconds
- ✅ Second verification: <1 second (instant)
- ✅ Same presence score both times
- ✅ "Cached" indicator (if implemented)

---

## Test 7: Large Bulk (Optional Check Skip)

### Create Large CSV:
Generate CSV with 600 emails (or use existing large list)

### Steps:
1. Upload 600+ email CSV
2. Start bulk process
3. Monitor processing

### Expected Results:
- ✅ Processing completes successfully
- ✅ GitHub checks are skipped (faster processing)
- ✅ Gravatar and domain checks still run
- ✅ Presence scores still calculated
- ✅ Processing time: ~10-15 minutes

---

## Test 8: Verification History

### Steps:
1. Verify several emails (mix of presence/no presence)
2. Go to "Verification History" tab
3. Check the entries

### Expected Results:
- ✅ All verifications logged
- ✅ History shows presence data (if columns added)
- ✅ Can filter and download

---

## 🔍 What to Look For

### UI Elements:

**Results Card:**
```
┌────────────────────────────────────┐
│ ✅ Valid                           │
│ Verified (MX Records found)        │
│                           95%      │
│                      TRUST SCORE   │
├────────────────────────────────────┤
│ SMTP Connection │ Disposable       │
│ Connected       │ No               │
│                                    │
│ Role Based      │ Digital Presence │
│ No              │ 85%              │
│                 │ Gravatar, Domain │
└────────────────────────────────────┘

🌐 Digital Presence Details [Expand ▼]
```

**Expanded Details:**
```
Presence Score: 85%
Strong digital presence detected (Gravatar, Domain Website)

────────────────────────────
Sources Found:
✅ Gravatar
✅ Domain Website
✅ Corporate Domain

────────────────────────────
Gravatar Profile:
[View Profile](https://...)
This email has an active Gravatar profile...
```

---

## 🐛 Troubleshooting

### Issue: "Module not found: email_presence"
**Solution:**
```bash
# Check file exists
ls components/email_presence.py

# Restart Streamlit
# Press Ctrl+C in terminal
python3 -m streamlit run app.py
```

### Issue: Presence always shows 0%
**Possible Causes:**
1. No internet connection
2. Gravatar/domain servers down
3. Timeout too short

**Debug:**
- Check terminal for error messages
- Try known Gravatar email: `beau@dentedreality.com.au`
- Check internet connection

### Issue: Processing very slow
**Possible Causes:**
1. Network latency
2. Timeout settings
3. No caching

**Solutions:**
- Check cache is working (verify same email twice)
- Reduce timeout in `email_presence.py` (line ~15)
- Skip optional checks for bulk

### Issue: Trust score seems wrong
**Check:**
- Presence score is calculated correctly
- Weight contribution is 15% max
- Other factors still apply
- Score caps at 99%

---

## ✅ Success Criteria

All tests pass if:

- [x] Gravatar emails show 40%+ presence
- [x] Corporate domains show 20%+ presence
- [x] Free providers (no Gravatar) show 0%
- [x] Disposable emails show 0%
- [x] Bulk processing completes successfully
- [x] Cache works (instant second verification)
- [x] Large batches skip optional checks
- [x] UI displays presence metric
- [x] Expandable details work
- [x] Trust score includes presence (15%)
- [x] No crashes or errors
- [x] Export includes presence data

---

## 📊 Sample Test Results

### Expected Scores:

| Email | Gravatar | Domain | Corporate | GitHub | Presence Score |
|-------|----------|--------|-----------|--------|----------------|
| beau@dentedreality.com.au | ✅ | ✅ | ✅ | ❓ | 70-100% |
| contact@microsoft.com | ❌ | ✅ | ✅ | ❌ | 30% |
| random@gmail.com | ❌ | N/A | ❌ | ❌ | 0% |
| test@tempmail.com | ❌ | ❌ | ❌ | ❌ | 0% |
| admin@google.com | ❌ | ✅ | ✅ | ❌ | 30% |

---

## 🎯 Quick Smoke Test (2 Minutes)

1. **Verify:** `beau@dentedreality.com.au`
   - Should show presence 40%+
   
2. **Verify:** `random@gmail.com`
   - Should show presence 0%

3. **Verify same email again:**
   - Should be instant (cached)

4. **Upload 5-email CSV:**
   - Should complete in ~30 seconds

**If all pass → Feature is working! 🎉**

---

## 📝 Notes

- Gravatar checks are most reliable
- Domain checks depend on website availability
- GitHub checks are optional (skip for bulk > 500)
- Caching improves performance significantly
- Timeouts prevent hanging (2 seconds per check)
- All checks are safe HTTP requests only

---

## 🔗 Related Documentation

- **Feature Overview:** `EMAIL_DIGITAL_PRESENCE.md`
- **Module Code:** `components/email_presence.py`
- **Integration:** `components/email_verifier.py` (lines 12, 111-156, 254-280)

---

**Happy Testing! 🚀**
