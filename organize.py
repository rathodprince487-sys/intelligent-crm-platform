import os
import shutil
import glob

docs_dir = 'docs'
tests_dir = 'tests'
scripts_dir = 'scripts'
logs_dir = 'logs'
data_scraper_dir = 'data/scraper'
assets_base64_dir = 'assets/base64'

# Create dirs
for d in [docs_dir, tests_dir, scripts_dir, logs_dir, data_scraper_dir, assets_base64_dir]:
    os.makedirs(d, exist_ok=True)

docs_files = [
    'DEPLOYMENT_INSTRUCTIONS.md', 'DEPLOY_FREE.md', 'DIGITAL_PRESENCE_SUMMARY.md',
    'DIGITAL_PRESENCE_TESTING.md', 'DIGITAL_PRESENCE_UI_GUIDE.md', 'DISCOVERABILITY_GUIDE.md',
    'EMAIL_DIGITAL_PRESENCE.md', 'EMAIL_VERIFIER_DEV_REFERENCE.md', 'EMAIL_VERIFIER_ENHANCEMENTS.md',
    'EMAIL_VERIFIER_TESTING.md', 'FREE_DEPLOYMENT_GUIDE.md', 'GUIDE_GOOGLE_DRIVE_SETUP.md',
    'PROJECT_DOCUMENTATION.md', 'PROJECT_DOCUMENTATION.pdf', 'PROJECT_PROPOSAL.md',
    'STREAMLIT_DEPLOYMENT_GUIDE.md', 'VERIFICATION_HISTORY_FIX.md', 'VERIFICATION_HISTORY_GUIDE.md'
]

scripts_files = [
    'apply_glass_theme.py', 'check_import.py', 'dark_theme_email_verifier.py',
    'generate_pdf.py', 'make_transparent.py', 'print_css.py', 'replace_logo.py',
    'reset_sat_pass.py', 'update_theme.py'
]

def move_files(files, dest):
    for f in files:
        if os.path.exists(f) and os.path.isfile(f):
            try:
                shutil.move(f, os.path.join(dest, os.path.basename(f)))
            except Exception as e:
                print(f"Error moving {f}: {e}")

move_files(docs_files, docs_dir)
move_files(scripts_files, scripts_dir)

# Test files
for fmt in ['test_*.py', 'test_*.txt', 'test_*.log', 'test_*.csv', 'test_out*.txt', 'debug_*.png', 'debug_*.py']:
    move_files(glob.glob(fmt), tests_dir)

# Logs
move_files(glob.glob('*.log'), logs_dir)

# Scraper Data
move_files(glob.glob('scraped_results*.csv'), data_scraper_dir)
move_files(['scraper_progress.txt'], data_scraper_dir)

# Base64 assets
move_files(glob.glob('*_b64.txt'), assets_base64_dir)
move_files(glob.glob('*base64.txt'), assets_base64_dir)
move_files(['test_avatar.gif'], assets_base64_dir)

print("Project structured successfully.")
