from datetime import datetime, timedelta

# 1. Subtract five days from current date
today = datetime.today()
five_days_ago = today - timedelta(days=5)
print("Current date:", today)
print("Five days ago:", five_days_ago)


# 2. Print yesterday, today, tomorrow
today = datetime.today()
yesterday = today - timedelta(days=1)
tomorrow = today + timedelta(days=1)
print("Yesterday:", yesterday)
print("Today:", today)
print("Tomorrow:", tomorrow)


# 3. Drop microseconds from datetime
dt = datetime.today()
print("Before:", dt)
dt_without_micro = dt.replace(microsecond=0)
print("After:", dt_without_micro)


# 4. Calculate two date difference in seconds
date1 = datetime(2024, 1, 1)
date2 = datetime(2024, 1, 10)
diff = date2 - date1
print("Difference in seconds:", diff.total_seconds())
