import os
import json
import pandas as pd

total_leads_in_crm = 0
total_calls = 0
total_meetings = 0
total_deals = 0

if os.path.exists("crm_data"):
    for root, dirs, files in os.walk("crm_data"):
        for f in files:
            if f.endswith(".json"):
                try:
                    df = pd.read_json(os.path.join(root, f))
                    total_leads_in_crm += len(df)
                    if 'status' in df.columns:
                        statuses = df['status'].dropna().astype(str).str.lower().str.strip()
                        
                        # Assuming every non-empty status except 'new' or '' implies a call was made, OR maybe any status implies a call? 
                        # Let's count any non-empty non-"new" status as a call.
                        # Wait, the user has "Called By" or "Call Notes"? In the json:
                        # "status" has values like "Interested", "Meeting Done ", "Not picking", "Call Later", "Closed - Won", "Meeting set "
                        
                        # Total calls: let's count anything where status is not empty/null and not "New"
                        total_calls += len(statuses[(statuses != '') & (statuses != 'new')])

                        # Total meetings: "meeting set" or "meeting done"
                        total_meetings += len(statuses[statuses.str.contains('meeting')])

                        # Total deals closed: "closed"
                        total_deals += len(statuses[statuses.str.contains('closed')])
                except Exception as e:
                    pass

print("Total CRM Leads:", total_leads_in_crm)
print("Total Calls:", total_calls)
print("Total Meetings:", total_meetings)
print("Total Deals:", total_deals)
