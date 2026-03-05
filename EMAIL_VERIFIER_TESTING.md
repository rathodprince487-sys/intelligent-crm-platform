# Email Verifier Testing Guide

## 🧪 How to Test the New Features

### Access the Application
```
URL: http://localhost:8501
Backend: http://localhost:3000
```

---

## 1. Test Client-Side Validation

### Test Cases:

**Invalid Formats (should be caught immediately):**
```
john..doe@example.com          → ❌ "Invalid regex format" (consecutive dots)
.john@example.com              → ❌ "Invalid regex format" (leading dot)
john.@example.com              → ❌ "Invalid regex format" (trailing dot)
john@example                   → ❌ "Invalid regex format" (no TLD)
john@@example.com              → ❌ "Invalid regex format" (double @)
```

**Role-Based Detection:**
```
admin@company.com              → ⚠️ Risky (role-based)
info@company.com               → ⚠️ Risky (role-based)
support@company.com            → ⚠️ Risky (role-based)
sales@company.com              → ⚠️ Risky (role-based)
```

**Free Provider Detection:**
```
user@gmail.com                 → Flag: is_free=True
user@yahoo.com                 → Flag: is_free=True
user@outlook.com               → Flag: is_free=True
```

**Disposable Detection:**
```
test@tempmail.com              → ❌ Invalid (disposable)
user@mailinator.com            → ❌ Invalid (disposable)
fake@guerrillamail.com         → ❌ Invalid (disposable)
```

---

## 2. Test Smart Scoring

### Expected Score Ranges:

**High Score (0.85-0.99):**
- Business email
- Valid MX records
- SMTP verified
- Not role-based
- Has social profile

**Medium Score (0.50-0.84):**
- Free provider (Gmail, Yahoo)
- Valid MX records
- SMTP connected
- No social profile

**Low Score (0.0-0.49):**
- Role-based email
- Disposable domain
- No MX records
- Invalid format

### Test Example:
```
john.doe@company.com
Expected:
- Score: ~0.90-0.95
- Status: Valid
- Flags: is_free=False, is_role=False

admin@gmail.com
Expected:
- Score: ~0.60-0.70
- Status: Risky
- Flags: is_free=True, is_role=True
```

---

## 3. Test Bulk Processing

### Create Test CSV:

**test_emails.csv:**
```csv
email
john.doe@example.com
jane.smith@example.com
john.doe@example.com
admin@company.com
test@gmail.com
invalid..email@test.com
user@tempmail.com
sales@business.org
contact@yahoo.com
support@outlook.com
```

### Expected Results:
- **Total rows:** 10
- **Unique emails:** 9 (1 duplicate removed)
- **Invalid:** 2 (consecutive dots, disposable)
- **Risky:** 3 (role-based)
- **Valid:** 4

### What to Observe:
1. ✅ Progress bar with batch updates
2. ✅ "Duplicates removed" message
3. ✅ Processing time and speed (emails/sec)
4. ✅ Analytics summary with 8 metrics
5. ✅ Domain Intelligence table
6. ✅ New columns in results

---

## 4. Test Caching

### Steps:
1. Verify email: `test@example.com`
2. Wait 2 seconds
3. Verify same email again
4. **Expected:** Instant result (from cache)
5. Wait 11 minutes
6. Verify again
7. **Expected:** New API call (cache expired)

### Bulk Cache Test:
1. Upload CSV with 100 emails
2. Process completely
3. Upload same CSV again
4. **Expected:** All 100 from cache, instant completion

---

## 5. Test Rate Limiting

### Test Max Limit:
1. Create CSV with 6,000 emails
2. Upload to bulk verifier
3. **Expected:** Error message:
   ```
   "Bulk limit exceeded. Please upload fewer than 5,000 unique emails. (You have 6,000)"
   ```

### Test Cooldown:
1. Verify single email
2. Immediately verify another
3. **Expected:** 2-second delay enforced

---

## 6. Test Error Handling

### Backend Down Test:
1. Stop backend: `Ctrl+C` on `node server.js`
2. Try to verify email
3. **Expected:** 
   ```
   "Could not connect to verification server. Is the backend running?"
   ```
4. Restart backend: `node server.js`

### Invalid CSV Test:
1. Upload text file renamed to .csv
2. **Expected:** 
   ```
   "Error processing file: [error details]"
   ```

### Empty Column Test:
1. Create CSV with column "contact" (not "email")
2. Upload
3. **Expected:** Auto-detects first column or shows selector

---

## 7. Test Domain Intelligence

### Create Domain-Heavy CSV:
```csv
email
user1@example.com
user2@example.com
user3@example.com
admin@example.com
user1@test.org
user2@test.org
invalid@test.org
```

### Expected Output:
```
Domain Intelligence Table:
Domain       | Total | Valid_Rate
-------------|-------|------------
example.com  | 4     | 75.0%
test.org     | 3     | 66.7%
```

---

## 8. Test Performance Monitoring

### Benchmark Test:
1. Upload CSV with 500 emails
2. Observe completion message
3. **Expected format:**
   ```
   ✅ Completed in 28.3s (17.7 emails/sec)
   ```

### What to Check:
- Processing time is reasonable
- Speed calculation is accurate
- No crashes or timeouts
- Progress updates smoothly

---

## 9. Test Analytics Dashboard

### After Bulk Processing, Verify:

**Row 1 Metrics:**
- ✅ Valid Emails (with % rate)
- ✅ Invalid Emails
- ✅ Risky/Catch-all
- ✅ Trust Score (Average)

**Row 2 Metrics:**
- ✅ Disposable count
- ✅ Role-Based count
- ✅ Free Providers count
- ✅ MX Records Found count

**Additional Sections:**
- ✅ Domain Intelligence table
- ✅ Detailed Results (first 100 rows)
- ✅ Download button with new filename

---

## 10. Test Export Functionality

### Steps:
1. Process bulk CSV
2. Click "Download Full Report"
3. Open downloaded file
4. **Verify new columns exist:**
   - Status
   - Score
   - Reason
   - Is_Disposable
   - Is_Free
   - Is_Role
   - MX_Found

---

## 🐛 Common Issues & Solutions

### Issue: "Backend verification failed after retries"
**Solution:** Check if backend is running on port 3000

### Issue: Cache not working
**Solution:** Check session state is initialized (should auto-initialize)

### Issue: Slow bulk processing
**Solution:** Normal for large batches; retry logic may be triggering

### Issue: Domain Intelligence not showing
**Solution:** Ensure email column is properly detected

---

## 📊 Expected Performance Benchmarks

| Emails | Expected Time | Speed |
|--------|---------------|-------|
| 10     | ~2s           | 5/s   |
| 100    | ~15s          | 6-7/s |
| 500    | ~60s          | 8-9/s |
| 1000   | ~120s         | 8-10/s|
| 5000   | ~600s         | 8-10/s|

*Note: Times vary based on backend response and network*

---

## ✅ Success Criteria

All features working if:
- ✅ Invalid formats caught before API call
- ✅ Smart scores between 0.0-0.99
- ✅ Duplicates removed automatically
- ✅ Cache hits return instantly
- ✅ Bulk limit enforced at 5,000
- ✅ Errors handled gracefully
- ✅ Domain intelligence displays
- ✅ Performance metrics shown
- ✅ Export includes all new columns
- ✅ No crashes or breaking errors

---

## 🎯 Quick Smoke Test

**5-Minute Test:**
1. Single verify: `test@gmail.com` → Should work
2. Single verify: `admin@test.com` → Should flag as risky
3. Upload 10-email CSV → Should complete with analytics
4. Re-upload same CSV → Should use cache (instant)
5. Check export → Should have all columns

**If all pass → System is working correctly! 🎉**
