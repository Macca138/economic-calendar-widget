import investpy
from datetime import datetime, timedelta
import html
import sys

# --- Configuration ---
TODAY = datetime.today().date()
TOMORROW = TODAY + timedelta(days=1)
MAJOR_COUNTRIES = [
    "united states", "euro zone", "united kingdom", "japan",
    "australia", "new zealand", "canada", "switzerland"
]

# --- Debug Information ---
print(f"Looking for events from {TODAY} to {TOMORROW}")
print(f"Countries: {MAJOR_COUNTRIES}")

# --- Fetch Economic Events ---
try:
    # Important: 'high' should be lowercase for investpy
    events = investpy.economic_calendar(
        time_zone='GMT', 
        countries=MAJOR_COUNTRIES,
        importances=['high'],  # This ensures proper filtering
        from_date=TODAY.strftime("%d/%m/%Y"),  # Explicitly set dates
        to_date=TOMORROW.strftime("%d/%m/%Y")
    )
    print(f"Retrieved {len(events)} total events")
    
    # Print first few events for debugging
    if len(events) > 0:
        print("Sample events:")
        print(events.head())
        # Print column names to debug the structure
        print("Available columns:", events.columns.tolist())
    else:
        print("No events were retrieved!")
except Exception as e:
    print(f"Error retrieving events: {e}")
    sys.exit(1)  # Exit with error code

# --- Filter Events ---
filtered_events = []
for _, event in events.iterrows():
    event_date = datetime.strptime(event['date'], "%d/%m/%Y").date()
    
    # Log what we're processing
    print(f"Processing event: {event['date']} - {event['event']}")
    
    # Get the country from the 'zone' column instead of 'country'
    country = event['zone'].title() if 'zone' in event else "Unknown"
    
    # No need to filter by importance as we already did that in the API call
    filtered_events.append({
        "date": event_date.strftime("%a %b %d"),
        "time": event['time'],
        "country": country,
        "event": event['event']
    })

print(f"Filtered to {len(filtered_events)} events")

# --- Generate HTML ---
with open("index.html", "w", encoding="utf-8") as f:
    f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>High-Impact Economic Events</title>
  <style>
    body { background: #1e1e1e; color: #fff; font-family: Arial; margin: 0; padding: 1rem; width: 250px; height: 500px; overflow-y: auto; }
    h3 { color: #f0ad4e; }
    .event { margin-bottom: 12px; border-bottom: 1px solid #444; padding-bottom: 6px; }
    .event .time { color: #999; font-size: 14px; }
    .event .title { font-weight: bold; font-size: 16px; }
    .event .impact { font-size: 12px; color: #f44336; }
  </style>
</head>
<body>
  <h3>High-Impact Economic Events</h3>
""")
    if not filtered_events:
        f.write("<p>No high-impact events for today or tomorrow.</p>")
        print("No events to display")
    else:
        for e in filtered_events:
            f.write(f"""
  <div class="event">
    <div class="time">{html.escape(e['date'])} — {html.escape(e['time'])} GMT</div>
    <div class="title">{html.escape(e['country'])}: {html.escape(e['event'])}</div>
    <div class="impact">Impact: High</div>
  </div>
""")
        print(f"Generated HTML with {len(filtered_events)} events")
    f.write("</body></html>")

print("Script completed successfully")