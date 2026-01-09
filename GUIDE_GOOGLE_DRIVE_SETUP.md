# ☁️ How to Get Your Google Service Account Key

To enable Google Drive uploads, you need to create a "Service Account" (a robot account) that can manage files.

### Step 1: Create a Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project dropdown (top left) and select **"New Project"**.
3. Name it (e.g., "Spreadsheet Tool") and create it.

### Step 2: Enable Google Drive API
1. In the search bar at the top, type **"Google Drive API"**.
2. Click on it and press **"Enable"**.

### Step 3: Create Service Account & Key
1. Go to **APIs & Services > Credentials** (in the sidebar).
2. Click **+ CREATE CREDENTIALS** (top) → **Service Account**.
3. Give it a name (e.g., "uploader") and click **Done**.
4. You will see the new service account in the list. Click on the **Pencil Icon (Edit)** or the email address.
5. Go to the **KEYS** tab (top menu).
6. Click **ADD KEY** → **Create new key**.
7. Select **JSON** and click **CREATE**.

### Step 4: Use the Key
1. A file will automatically download to your computer.
2. Rename this file to exactly: `service-account.json`.
3. Go back to this App, open the **"Save to Google Drive"** section, and drop the file there!

---
**💡 Pro Tip:**
If you want the files to appear in YOUR personal Google Drive folder:
1. Copy the **email address** of the Service Account (it looks like `uploader@project-id.iam.gserviceaccount.com`).
2. Go to your Google Drive, create a folder, right-click it, and select **Share**.
3. Paste the Service Account email and give it "Editor" access.
