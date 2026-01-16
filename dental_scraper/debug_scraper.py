import os
import datetime

def run():
    print("Files in directory:")
    files = os.listdir(".")
    for f in files:
        print(f)
        
    if os.path.exists("debug_google_maps.png"):
        ts = os.path.getmtime("debug_google_maps.png")
        dt = datetime.datetime.fromtimestamp(ts)
        print(f"Debug Screenshot Timestamp: {dt}")
        print(f"Size: {os.path.getsize('debug_google_maps.png')} bytes")
    else:
        print("Debug Screenshot NOT found")

if __name__ == "__main__":
    run()
