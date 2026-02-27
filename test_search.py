
from duckduckgo_search import DDGS

try:
    print("Testing DDGS...")
    results = list(DDGS().text('"support@google.com"', max_results=5))
    print(f"Results found: {len(results)}")
    for r in results:
        print(r)
except Exception as e:
    print(f"Error: {e}")
