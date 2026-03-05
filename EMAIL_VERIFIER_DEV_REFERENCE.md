# Email Verifier - Developer Quick Reference

## 🔧 Key Functions Reference

### Client-Side Validation

```python
# Normalize email
normalized = normalize_email("  Admin@EXAMPLE.COM  ")
# Returns: "admin@example.com"

# Generate cache key
key = generate_cache_key("test@example.com")
# Returns: "098f6bcd4621d373cade4e832627b4f6"

# Analyze email locally
is_valid, flags, msg = analyze_email_local("admin@gmail.com")
# Returns: (True, {'is_free': True, 'is_role': True, ...}, "Valid syntax")
```

### Smart Scoring

```python
# Calculate trust score
score = calculate_smart_score(local_flags, backend_details)
# Returns: 0.0 to 0.99

# Scoring weights:
# - Not disposable: +0.15
# - Valid format: +0.10
# - SMTP Connected: +0.35
# - SMTP Verified: +0.45
# - MX Records: +0.20
# - Not role: +0.10
# - Business domain: +0.10
# - Social profile: +0.15
```

### Caching

```python
# Check cache
cached_result = check_cache("test@example.com")
# Returns: result dict or None

# Update cache
update_cache("test@example.com", result_object)
# Stores for 10 minutes with hashed key
```

### Verification

```python
# Verify single email
results = verify_emails("test@example.com", source="Single")
# Returns: [result_dict]

# Verify bulk emails
results = verify_emails(email_list, source="Bulk", use_cache=True)
# Returns: [result_dict, result_dict, ...]
```

---

## 📊 Data Structures

### Local Flags Object
```python
{
    'is_free': bool,           # Gmail, Yahoo, etc.
    'is_role': bool,           # admin@, info@, etc.
    'is_disposable': bool,     # Temp mail services
    'is_suspect_format': bool, # Invalid patterns
    'domain': str,             # example.com
    'username': str            # john.doe
}
```

### Result Object
```python
{
    'email': str,              # Normalized email
    'status': str,             # Valid / Invalid / Risky
    'score': float,            # 0.0 to 0.99
    'reason': str,             # Human-readable reason
    'details': {
        'smtpCheck': str,      # Connected / Verified / Failed
        'mxRecords': list,     # ['mx1.example.com', ...]
        'isDisposable': bool,
        'isRole': bool,
        'isFree': bool,
        'socialProfile': {
            'hasProfile': bool,
            'url': str
        },
        # Local flags merged here
        'is_free': bool,
        'is_role': bool,
        'domain': str,
        'username': str
    }
}
```

---

## 🎯 Configuration Constants

```python
# Backend URL
BACKEND_URL = "http://localhost:3000"

# Free email providers
FREE_PROVIDERS = {
    'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 
    'aol.com', 'icloud.com', 'protonmail.com', 'mail.com', 
    'yandex.com', 'zoho.com'
}

# Role-based prefixes
ROLE_PREFIXES = {
    'admin', 'info', 'support', 'sales', 'contact', 'help', 
    'billing', 'marketing', 'hr', 'recruit', 'office', 
    'enquiry', 'jobs', 'team', 'no-reply'
}

# Disposable domains
DISPOSABLE_DOMAINS = {
    'tempmail.com', 'throwawaymail.com', 'mailinator.com', 
    'guerrillamail.com', 'yopmail.com', '10minutemail.com', 
    'sharklasers.com', 'getnada.com', 'dispostable.com'
}

# Processing limits
MAX_BULK_EMAILS = 5000
BATCH_SIZE = 20
CACHE_DURATION_MINUTES = 10
RATE_LIMIT_SECONDS = 2
MAX_RETRIES = 2
API_TIMEOUT_SECONDS = 35
```

---

## 🔄 Processing Flow

### Single Email Flow
```
User Input
    ↓
normalize_email()
    ↓
analyze_email_local()
    ↓
Check Cache → HIT → Return cached result
    ↓ MISS
Backend API Call (with retry)
    ↓
calculate_smart_score()
    ↓
update_cache()
    ↓
Display Result
```

### Bulk Email Flow
```
CSV Upload
    ↓
Extract emails → Normalize → Deduplicate
    ↓
Check bulk limit (5000)
    ↓
For each email:
    - Check cache
    - analyze_email_local()
    - Queue for backend if needed
    ↓
Process in batches (20 emails)
    ↓
Backend API Call (with retry)
    ↓
calculate_smart_score() for each
    ↓
update_cache() for all
    ↓
Generate Analytics
    ↓
Domain Intelligence
    ↓
Export Results
```

---

## 🚨 Error Handling

### Try-Catch Blocks

```python
# Backend call with retry
attempts = 0
while attempts < 2 and not success:
    try:
        response = requests.post(...)
        if response.status_code == 200:
            success = True
        else:
            attempts += 1
            time.sleep(1)
    except requests.exceptions.RequestException:
        attempts += 1
        time.sleep(1)
```

### Error Messages

```python
# Connection Error
"Could not connect to verification server. Is the backend running?"

# Timeout Error
"Request timed out. The server might be busy."

# Bulk Limit Error
"Bulk limit exceeded. Please upload fewer than 5,000 unique emails."

# File Processing Error
"Error processing file: [details]"

# Validation Error
"Validation Error: Invalid regex format"
```

---

## 📈 Performance Optimization Tips

### 1. Batch Size Tuning
```python
# Current: 20 emails per batch
# Increase for faster backend: 50
# Decrease for slower backend: 10
BATCH_SIZE = 20
```

### 2. Cache Duration
```python
# Current: 10 minutes
# Increase for more hits: 30 minutes
# Decrease for fresher data: 5 minutes
CACHE_DURATION = timedelta(minutes=10)
```

### 3. Parallel Processing (Future)
```python
# Use ThreadPoolExecutor for concurrent batches
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(verify_batch, batch) for batch in batches]
```

---

## 🧪 Unit Test Examples

```python
import pytest
from components.email_verifier import *

def test_normalize_email():
    assert normalize_email("  TEST@EXAMPLE.COM  ") == "test@example.com"
    assert normalize_email("Admin@Gmail.com") == "admin@gmail.com"

def test_analyze_email_local():
    valid, flags, msg = analyze_email_local("admin@gmail.com")
    assert valid == True
    assert flags['is_free'] == True
    assert flags['is_role'] == True
    
def test_calculate_smart_score():
    flags = {'is_free': False, 'is_role': False, 'is_disposable': False}
    details = {'smtpCheck': 'Verified', 'mxRecords': ['mx1.example.com']}
    score = calculate_smart_score(flags, details)
    assert 0.8 <= score <= 0.99

def test_cache_key_generation():
    key1 = generate_cache_key("test@example.com")
    key2 = generate_cache_key("TEST@EXAMPLE.COM")
    assert key1 == key2  # Should be same after normalization
```

---

## 🔍 Debugging Tips

### Enable Verbose Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Cache State
```python
# In Streamlit app
st.write("Cache size:", len(st.session_state.email_cache))
st.write("Cache contents:", st.session_state.email_cache)
```

### Monitor API Calls
```python
# Add before requests.post()
print(f"Calling API with {len(emails)} emails")
print(f"Payload: {payload}")
```

### Track Performance
```python
import time
start = time.time()
# ... processing ...
duration = time.time() - start
print(f"Processed in {duration:.2f}s")
```

---

## 📝 Code Comments Convention

```python
# Single-line comment for simple explanations

"""
Multi-line docstring for functions
Explains: purpose, parameters, returns, side effects
"""

# TODO: Future enhancement
# FIXME: Known issue to address
# NOTE: Important information
# HACK: Temporary workaround
```

---

## 🔗 API Endpoints

### Backend Endpoints Used

```python
# Email Verification
POST /verify-email
Body: {"emails": [...], "source": "Single|Bulk"}
Response: {"results": [...]}

# Health Check
GET /
Response: "BackEnd CRM v2 is running 🚀"
```

---

## 🎨 UI Integration Points

### Session State Variables
```python
st.session_state.email_cache          # Cache storage
st.session_state.last_verification_time  # Rate limiting
```

### Streamlit Components
```python
st.text_input()      # Email input
st.button()          # Verify button
st.file_uploader()   # CSV upload
st.progress()        # Progress bar
st.metric()          # Analytics display
st.dataframe()       # Results table
st.download_button() # Export CSV
```

---

## 🚀 Deployment Checklist

- [ ] Backend running on port 3000
- [ ] Frontend running on port 8501
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Cache initialized in session state
- [ ] Error handling tested
- [ ] Performance benchmarks met
- [ ] Documentation updated
- [ ] Test cases passing

---

## 📞 Support & Maintenance

### Common Modifications

**Add new free provider:**
```python
FREE_PROVIDERS.add('newprovider.com')
```

**Add new role prefix:**
```python
ROLE_PREFIXES.add('newrole')
```

**Change batch size:**
```python
BATCH_SIZE = 30  # Line ~755
```

**Adjust scoring weights:**
```python
# In calculate_smart_score() function
score += 0.20  # Modify weight values
```

---

## 🎯 Quick Commands

```bash
# Start backend
node server.js

# Start frontend
python3 -m streamlit run app.py

# Check ports
lsof -i :3000
lsof -i :8501

# View logs
tail -f backend.log
tail -f streamlit.log

# Test API
curl http://localhost:3000
```

---

**Last Updated:** 2026-02-10
**Version:** 2.0 (Enhanced)
**Maintainer:** Development Team
