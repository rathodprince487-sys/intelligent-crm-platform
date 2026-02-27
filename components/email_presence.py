"""
Email Digital Presence Checker Module

This module checks if an email address has an active digital presence on the internet.
Uses safe, lightweight HTTP checks without scraping or illegal methods.

Methods:
1. Gravatar Check - Primary indicator
2. Domain Website Check - Business email validation
3. Social Profile Indicators - Pattern-based checks

Returns presence score (0-1) and sources found.
"""

import hashlib
import requests
from datetime import datetime, timedelta
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# Configuration
GRAVATAR_BASE_URL = "https://www.gravatar.com/avatar/"
REQUEST_TIMEOUT = 2  # seconds
CACHE_DURATION = timedelta(minutes=10)

# Global cache for presence checks
_presence_cache = {}


def _generate_md5_hash(email):
    """Generate MD5 hash of email for Gravatar."""
    return hashlib.md5(email.strip().lower().encode()).hexdigest()


def _get_cache_key(email):
    """Generate cache key for presence check."""
    return f"presence_{email.strip().lower()}"


def _check_cache(email):
    """Check if presence result is cached."""
    key = _get_cache_key(email)
    if key in _presence_cache:
        result, timestamp = _presence_cache[key]
        if datetime.now() - timestamp < CACHE_DURATION:
            return result
    return None


def _update_cache(email, result):
    """Update cache with presence result."""
    key = _get_cache_key(email)
    _presence_cache[key] = (result, datetime.now())
    
    # Limit cache size to 1000 entries
    if len(_presence_cache) > 1000:
        # Remove oldest entries
        sorted_items = sorted(_presence_cache.items(), key=lambda x: x[1][1])
        for old_key, _ in sorted_items[:200]:
            del _presence_cache[old_key]


def check_gravatar(email):
    """
    Check if email has a Gravatar profile.
    
    Args:
        email (str): Email address to check
        
    Returns:
        dict: {'found': bool, 'url': str or None}
    """
    try:
        email_hash = _generate_md5_hash(email)
        gravatar_url = f"{GRAVATAR_BASE_URL}{email_hash}?d=404"
        
        response = requests.get(
            gravatar_url,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=False
        )
        
        # Status 200 means profile exists, 404 means no profile
        if response.status_code == 200:
            return {
                'found': True,
                'url': f"https://www.gravatar.com/{email_hash}"
            }
        else:
            return {'found': False, 'url': None}
            
    except requests.exceptions.Timeout:
        return {'found': False, 'url': None}
    except Exception as e:
        print(f"Gravatar check error: {e}")
        return {'found': False, 'url': None}


def check_domain_website(domain):
    """
    Check if the email domain has an active website.
    Tries multiple combinations (http/https, www/non-www) with browser headers.
    """
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        })
        
        # Variations to try: https://domain, https://www.domain, http://domain, http://www.domain
        variations = []
        for protocol in ['https', 'http']:
            variations.append(f"{protocol}://{domain}")
            # Only add www if not already present
            if not domain.startswith('www.'):
                variations.append(f"{protocol}://www.{domain}")
                
        for url in variations:
            try:
                # Use GET with stream=True or HEAD? GET is safer for some firewalls that block HEAD
                # stream=True avoids downloading body
                response = session.get(
                    url,
                    timeout=3.5,
                    allow_redirects=True,
                    stream=True
                )
                
                # Check status code
                if 200 <= response.status_code < 400:
                    response.close() # Close connection
                    return {
                        'active': True, 
                        'status_code': response.status_code, 
                        'protocol': url.split(':')[0],
                        'url': response.url # Return final URL (might be redirected)
                    }
                    
            except Exception:
                continue
                
        return {'active': False, 'status_code': None, 'protocol': None}
        
    except Exception as e:
        print(f"Domain website check error: {e}")
        return {'active': False, 'status_code': None, 'protocol': None}


def check_company_pages(domain, username, full_email=None):
    """
    Check specific company pages for presence of username/email.
    Safely checks Homepage, /team, /about, /contact
    """
    # Added '' to check the homepage (root) where footers usually are
    pages = ['', 'contact', 'contact-us', 'about', 'team', 'people']
    found_urls = []
    
    try:
        # Simple validation
        if not domain or not username:
            return []
            
        # Try HTTPS first
        base_url = f"https://{domain}"
        
        # Requests session with Browser Headers to avoid blocking
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        })
        
        for page in pages:
            url = f"{base_url}/{page}".strip('/')
            # Handle root url correctly
            if not page:
                url = base_url
                
            try:
                # Increased timeout slightly for slower corporate sites
                resp = session.get(url, timeout=3.5, allow_redirects=True)
                
                if resp.status_code == 200:
                    text_content = resp.text.lower()
                    
                    # Strongest Signal: Search for exact email
                    if full_email and full_email.lower() in text_content:
                        found_urls.append({
                            'platform': 'Company Website',
                            'url': url,
                            'type': 'Email Listed', 
                            'details': "Exact email match found on page"
                        })
                        return found_urls
                        
                    # Secondary Signal: Search for username (if long enough to be unique)
                    # Skip short usernames like 'info', 'paras' might be common but we check length
                    if len(username) > 4 and username.lower() in text_content:
                        found_urls.append({
                            'platform': 'Company Website',
                            'url': url,
                            'type': 'Mention',
                            'details': f"Username '{username}' mentions found"
                        })
                        return found_urls 
            except Exception as e:
                # specific page check failed, continue to next
                continue
                
    except Exception as e:
        print(f"Company page check error: {e}")
        pass
        
    return found_urls

def check_web_mentions(email):
    """
    Search for the email on the web using a lightweight scraping method.
    Using DuckDuckGo HTML as it is safer and less aggressive than Google scraping.
    """
    try:
        url = "https://html.duckduckgo.com/html/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        data = {'q': f'"{email}"'}
        
        # Timeout quickly to not stall the app
        res = requests.post(url, data=data, headers=headers, timeout=4)
        
        if res.status_code != 200:
            return []
            
        soup = BeautifulSoup(res.text, 'html.parser')
        mentions = []
        
        # Parse DDG HTML results
        for result in soup.select('.result'):
            try:
                title_el = result.select_one('.result__title a')
                snippet_el = result.select_one('.result__snippet')
                url_el = result.select_one('.result__url')
                
                # Check different DDG HTML structures
                actual_link = None
                display_url = None
                
                if title_el:
                    actual_link = title_el.get('href')
                
                # Sometimes URL is in the result__url span
                if not actual_link and url_el:
                     # This usually has the text only, link might be relative
                     pass
                     
                if actual_link:
                    # Parse domain
                    parsed = urlparse(actual_link)
                    domain = parsed.netloc
                    if not domain: continue
                    
                    # Clean snippet
                    snippet = snippet_el.get_text(strip=True) if snippet_el else "Found on web search"
                    
                    mentions.append({
                        'platform': f'Web: {domain}',
                        'url': actual_link,
                        'type': 'Web Listing', 
                        'details': snippet[:80] + "..."
                    })
                    
                    if len(mentions) >= 3:
                        break
            except:
                continue
                
        return mentions
    except Exception as e:
        print(f"Web mention check error: {e}")
        return []


def check_github_user(email):
    """
    Check if email appears to have GitHub presence (lightweight check).
    
    Args:
        email (str): Email address
        
    Returns:
        dict: {'likely_exists': bool, 'reason': str}
    """
    try:
        # Extract username from email for common patterns
        username = email.split('@')[0]
        
        # Skip if username is too generic or role-based
        generic_names = {'admin', 'info', 'support', 'contact', 'sales', 'hello', 'team'}
        if username.lower() in generic_names or len(username) < 3:
            return {'likely_exists': False, 'reason': 'Generic username'}
        
        # Check if GitHub profile exists for username (lightweight)
        # This is a HEAD request, very lightweight
        github_url = f"https://github.com/{username}"
        
        response = requests.head(
            github_url,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True
        )
        
        if response.status_code == 200:
            return {
                'likely_exists': True,
                'reason': f'GitHub profile found for username: {username}',
                'url': github_url
            }
        else:
            return {'likely_exists': False, 'reason': 'No GitHub profile'}
            
    except:
        return {'likely_exists': False, 'reason': 'Check unavailable'}


def is_corporate_domain(domain):
    """
    Check if domain appears to be corporate (not free provider).
    
    Args:
        domain (str): Email domain
        
    Returns:
        bool: True if corporate domain
    """
    free_providers = {
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com',
        'icloud.com', 'protonmail.com', 'mail.com', 'yandex.com', 'zoho.com',
        'gmx.com', 'live.com', 'msn.com', 'me.com', 'qq.com', '163.com'
    }
    
    return domain.lower() not in free_providers


def calculate_presence_score(checks):
    """
    Calculate overall presence score based on all checks.
    
    Scoring:
    - Gravatar found: +0.4
    - Domain website active: +0.2
    - Corporate domain: +0.1
    - GitHub profile: +0.3
    
    Args:
        checks (dict): Results from all presence checks
        
    Returns:
        float: Score between 0.0 and 1.0
    """
    score = 0.0
    
    # Gravatar (primary indicator)
    if checks.get('gravatar', {}).get('found'):
        score += 0.1  # Updated from 0.4
    
    # Domain website active
    if checks.get('domain_website', {}).get('active'):
        score += 0.2
    
    # Corporate domain (not free provider)
    if checks.get('is_corporate'):
        score += 0.1
    
    # GitHub profile
    if checks.get('github', {}).get('likely_exists'):
        score += 0.2  # Updated from 0.3
        
    # Company Pages Found
    if checks.get('company_pages', []):
        score += 0.2
        
    # Web Mentions Found
    if checks.get('web_mentions', []):
        count = len(checks.get('web_mentions', []))
        score += min(0.3, count * 0.1)  # Up to 0.3 for multiple mentions
        
    # Cap at 1.0
    return min(1.0, score)


def check_email_presence(email, skip_optional=False):
    """
    Main function to check email digital presence.
    
    Args:
        email (str): Email address to check
        skip_optional (bool): Skip optional checks for bulk processing
        
    Returns:
        dict: {
            'has_presence': bool,
            'presence_score': float (0-1),
            'sources_found': list,
            'reason': str,
            'details': dict
        }
    """
    # Check cache first
    cached = _check_cache(email)
    if cached:
        return cached
    
    # Initialize result
    result = {
        'has_presence': False,
        'presence_score': 0.0,
        'sources_found': [],
        'reason': '',
        'details': {}
    }
    
    try:
        # Extract domain
        if '@' not in email:
            result['reason'] = 'Invalid email format'
            return result
        
        username, domain = email.split('@')
        
        # Perform checks
        checks = {}
        
        # 1. Gravatar Check (Primary - always run)
        gravatar_result = check_gravatar(email)
        checks['gravatar'] = gravatar_result
        if gravatar_result['found']:
            result['sources_found'].append('Gravatar')
            result['details']['gravatar_url'] = gravatar_result['url']
        
        # 2. Domain Website Check
        domain_result = check_domain_website(domain)
        checks['domain_website'] = domain_result
        if domain_result['active']:
            result['sources_found'].append('Domain Website')
            result['details']['domain_active'] = True
        
        # 3. Corporate Domain Check
        is_corp = is_corporate_domain(domain)
        checks['is_corporate'] = is_corp
        if is_corp:
            result['sources_found'].append('Corporate Domain')
            result['details']['corporate_domain'] = True
        
        # 4. GitHub Check (Optional - skip for bulk)
        if not skip_optional:
            github_result = check_github_user(email)
            checks['github'] = github_result
            if github_result.get('likely_exists'):
                result['sources_found'].append('GitHub')
                result['details']['github_url'] = github_result.get('url')
                result.setdefault('found_locations', []).append({
                    'platform': 'GitHub',
                    'url': github_result.get('url'),
                    'type': 'Profile'
                })
                
            # 5. Company Pages Check (New)
            company_pages = check_company_pages(domain, username, full_email=email)
            checks['company_pages'] = company_pages
            if company_pages:
                result['sources_found'].append('Company Page')
                for page in company_pages:
                    result.setdefault('found_locations', []).append({
                        'platform': 'Company Website',
                        'url': page['url'],
                        'type': 'Mention'
                    })

            # 6. General Web Mentions (Last Resort / Bonus)
            # Only run if score is low OR we are doing a deep single check
            # We already passed skip_optionalcheck, so we run this for single emails
            web_mentions = check_web_mentions(email)
            checks['web_mentions'] = web_mentions
            if web_mentions:
                result['sources_found'].append('Web Listings')
                for mention in web_mentions:
                    result.setdefault('found_locations', []).append({
                        'platform': mention['platform'],
                        'url': mention['url'],
                        'type': mention['type']
                    })

        # Add Gravatar to found_locations if found
        if gravatar_result['found']:
             result.setdefault('found_locations', []).append({
                'platform': 'Gravatar',
                'url': gravatar_result['url'],
                'type': 'Profile'
            })
        
        # Calculate presence score
        presence_score = calculate_presence_score(checks)
        result['presence_score'] = presence_score
        
        # Determine has_presence
        result['has_presence'] = presence_score > 0.0
        
        # Generate reason
        if presence_score >= 0.5:
            result['reason'] = 'Strong digital presence detected'
        elif presence_score >= 0.2:
            result['reason'] = 'Moderate digital presence'
        elif presence_score > 0.0:
            result['reason'] = 'Low digital footprint'
        else:
            result['reason'] = 'No digital presence found'
        
        # Add sources to reason if found
        if result['sources_found']:
            sources_str = ', '.join(result['sources_found'])
            result['reason'] += f' ({sources_str})'
        
    except Exception as e:
        print(f"Presence check error for {email}: {e}")
        result['reason'] = 'Presence check unavailable'
        result['presence_score'] = 0.0
        result['has_presence'] = False
    
    # Cache the result
    _update_cache(email, result)
    
    return result


def classify_presence_risk(presence_score):
    """
    Classify email based on presence score.
    
    Args:
        presence_score (float): Presence score (0-1)
        
    Returns:
        str: Risk classification
    """
    if presence_score >= 0.5:
        return 'Likely Real Person'
    elif presence_score >= 0.2:
        return 'Moderate Confidence'
    elif presence_score > 0.0:
        return 'Low Digital Footprint'
    else:
        return 'No Presence Detected'


def get_presence_weight_for_trust_score(presence_score):
    """
    Get weighted contribution of presence score to overall trust score.
    
    Args:
        presence_score (float): Presence score (0-1)
        
    Returns:
        float: Weighted score contribution (max 0.15)
    """
    # Presence contributes up to 15% of overall trust score
    return presence_score * 0.15


# Utility function for bulk processing
def should_skip_presence_check(batch_size):
    """
    Determine if presence check should be skipped for bulk processing.
    
    Args:
        batch_size (int): Number of emails in batch
        
    Returns:
        bool: True if should skip optional checks
    """
    return batch_size > 500


# Clear cache function
def clear_presence_cache():
    """Clear the presence check cache."""
    global _presence_cache
    _presence_cache = {}


# Get cache stats
def get_cache_stats():
    """Get cache statistics."""
    return {
        'size': len(_presence_cache),
        'max_size': 1000
    }
