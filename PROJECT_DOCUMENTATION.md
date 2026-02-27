# Technical Architecture Report: Intelligent CRM Platform

## 1. Executive Summary
This report details the technical implementation of the **Intelligent CRM Platform**, focusing specifically on its two core automated modules: the **Google Maps Scraper** and the **Email Verifier**. The system is built using a hybrid technology stack combining a **Streamlit (Python)** frontend for the user interface, a **Node.js (Express)** backend for data management, and specialized **Python (Scrapy/Playwright)** scripts for high-performance web scraping.

---

## 2. Google Maps Scraper Module
The scraper is a highly sophisticated, asynchronous web crawler designed to extract business leads (Name, Phone, Address, Website, Email) from Google Maps. It addresses complex challenges like infinite scrolling, dynamic content loading, and GDPR consent popups.

### 2.1 Technology Stack
- **Framework**: `Scrapy` (Python) - Provides the crawling framework, request scheduling, and signal handling.
- **Browser Automation**: `scrapy-playwright` - Integrates Microsoft Playwright to render JavaScript-heavy pages (Google Maps).
- **Driver**: Chromium (Headless mode).
- **Selector Engine**: CSS Selectors & XPath.

### 2.2 Core Logic & Workflow (`dental_spider.py`)

#### A. Initialization & Persistent Context
The spider initializes a **Persistent Browser Context**. This is critical because it allows the scraper to maintain session state (cookies, local storage) across requests.
- **Why it matters**: Once the scraper accepts cookies on the homepage, that consent persists for all subsequent search queries, preventing the scraper from being blocked by cookie popups on every page load.

#### B. Consent Handling System
The scraper implements a robust, multi-lingual consent handling mechanism.
- **Strategy**: It lands on `google.com` first before attempting any searches.
- **Detection**: It scans for buttons with keywords like "Accept", "Agree", "Zgadzam" (Polish), "Zustimmen" (German), etc.
- **Action**: It clicks the consent button and waits `networkidle` to ensure the cookie is set.

#### C. Search Query Generation
The scraper automates "Search Expansion" to maximize results.
- **Input**: "Dentist in London"
- **Expansion**: It automatically generates variations:
  - "Dentist services in London"
  - "Dentist clinic in London"
  - "Dentist office London"
- This ensures that businesses listing themselves under slightly different categories are captured.

#### D. Infinite Scroll & Feed Detection
Google Maps "lazy loads" results. The scraper implements a custom JavaScript injection loop:
1.  **Feed Detection**: It searches for the `div[role="feed"]` container.
2.  **Scroll Loop**: It programmatically scrolls this container to the bottom.
3.  **End Key Simulation**: It dispatches "End" key events to force the browser to request more data.
4.  **Stagnation Check**: It monitors the `scrollHeight`. If the height doesn't change after 5 attempts, it assumes the list is exhausted.

#### E. Data Extraction Strategy
1.  **Lead Extraction**: Extracts basic details (Name, Address) from the list view.
2.  **Detail Page Visits**: For every business found, it visits the specific Google Maps detail URL to extract the **Phone Number** and **Website URL**.
3.  **Website Crawling (Email Discovery)**:
    - If a website URL is found, the scraper schedules a *new* request to visit that website.
    - It downloads the HTML and uses a **Regex Pattern** (`[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`) to find email addresses on the homepage.
    - It filters out junk emails (e.g., `sentry@`, `example.com`, `.png`).

---

## 3. Email Verifier Module
The Email Verifier is a component designed to validate email addresses in real-time to reduce bounce rates.

### 3.1 Technology Stack
- **Frontend**: **Streamlit** (Python) with custom HTML/CSS injection.
- **Backend (Intended)**: **Node.js** (Express) with `axios` and DNS lookup libraries.

### 3.2 Frontend Implementation (`components/email_verifier.py`)
The frontend is built with a focus on **Premium UX**.
- **Visuals**: Uses "Glassmorphism" design, smooth gradients, and CSS animations (pulse effects).
- **Client-Side Validation**: Before sending data, it performs regex checks to ensure the email format is valid (has `@`, domain has `.`, etc.).
- **Rate Limiting**: Implements a session-based rate limiter (max 1 request per 2 seconds) to prevent abuse.
- **Graceful Error Handling**: 
  - It attempts to connect to the backend API (`/verify-email`).
  - **Fallback/Demo Mode**: If the backend is unreachable (e.g., deployed without the server), it seamlessly switches to a "Demo Mode" that returns simulated realistic data (Valid status, MX records) so the UI remains functional for demonstration.

### 3.3 Backend Status
*Note: Technical audit revealed a discrepancy.*
- The frontend expects endpoints: `/auth/dev-token` and `/verify-email`.
- The current `server.js` file handles Lead Generation and CRM logic but **does not currently contain the email verification logic**.
- **Recommendation**: To fully enable this feature, the backend requires an update to include:
  1.  **DNS MX Record Lookup**: To confirm the domain can receive emails.
  2.  **SMTP Handshake**: To verify the specific mailbox exists (without sending an actual email).
  3.  **Disposable Email Webhook**: Integration with a list of known temporary email providers.

---

## 4. Integration & Security
- **Process Management**: The Scraper runs as a "subprocess" invoked by Python's `subprocess.Popen`, allowing the Streamlit UI to remain responsive while the heavy scraping job runs in the background.
- **Real-time Feedback**: The scraper writes its status to `scraper_progress.txt`, which the Streamlit frontend polls every 2 seconds to update the progress bar.
- **Security**: The backend uses JWT-based authentication (referenced as `auth_token` in frontend code) to secure API endpoints.

## 5. Conclusion
The platform successfully integrates a high-complexity scraping engine with a modern CRM interface. The scraper's ability to handle dynamic content and GDPR consent makes it robust for international use. The Email Verifier provides a polished user interface, currently operating in a simulated mode pending backend service deployment.
