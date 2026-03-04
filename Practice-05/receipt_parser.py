import re

# Read the receipt file
with open("raw.txt", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Extract all prices (numbers with format like 154,00 or 1 200,00)
prices = re.findall(r"Стоимость\s+([\d\s]+,\d{2})", text)
print("Prices:")
for p in prices:
    print(" ", p)

# 2. Find all product names (lines after item numbers like "1.", "2.", etc.)
products = re.findall(r"\d+\.\n(.+)", text)
print("\nProducts:")
for p in products:
    print(" ", p.strip())

# 3. Extract total amount
total = re.search(r"ИТОГО:\s*([\d\s]+,\d{2})", text)
print("\nTotal:", total.group(1) if total else "Not found")

# 4. Extract date and time
datetime_match = re.search(r"Время:\s*(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2})", text)
print("Date and Time:", datetime_match.group(1) if datetime_match else "Not found")

# 5. Find payment method
payment = re.search(r"(Банковская карта|Наличные)", text)
print("Payment method:", payment.group(0) if payment else "Not found")

# 6. Structured output
print("\n" + "=" * 50)
print("STRUCTURED RECEIPT")
print("=" * 50)

# Store info
store = re.search(r"Филиал (.+)", text)
print("Store:", store.group(1) if store else "N/A")

# Receipt number
receipt_num = re.search(r"Чек №(\d+)", text)
print("Receipt #:", receipt_num.group(1) if receipt_num else "N/A")

# Items with quantity, unit price, and total
print("\nItems:")
items = re.findall(r"(\d+)\.\n(.+)\n([\d,]+)\s*x\s*([\d\s]+,\d{2})\n([\d\s]+,\d{2})", text)
for item in items:
    num, name, qty, unit_price, item_total = item
    print(f"  {num}. {name.strip()} | Qty: {qty} | Price: {unit_price} | Total: {item_total}")

print(f"\nTotal: {total.group(1) if total else 'N/A'}")
print(f"Payment: {payment.group(0) if payment else 'N/A'}")
print(f"Date: {datetime_match.group(1) if datetime_match else 'N/A'}")
