#!/usr/bin/env python3
import sys
from datetime import datetime
from nepali_datetime import date as nepali_date

def get_nepali_day_name(day_number):
    nepali_days = {
    0: "आइतबार",
    1: "सोमबार",
    2: "मंगलबार",
    3: "बुधबार",
    4: "बिहिबार",
    5: "शुक्रबार",
    6: "शनिबार"
    }
    return nepali_days.get(day_number, "")

def to_nepali_numerals(number):
    nepali_numerals = {
        '0': '०',
        '1': '१',
        '2': '२',
        '3': '३',
        '4': '४',
        '5': '५',
        '6': '६',
        '7': '७',
        '8': '८',
        '9': '९'
    }
    return ''.join(nepali_numerals.get(digit, digit) for digit in str(number))

def main():
    try:
        # Get current date
        current_date = datetime.now()
        
        # Convert to Nepali date
        nepali_current = nepali_date.from_datetime_date(current_date.date())
        
        # Get day names
        nepali_day = get_nepali_day_name(nepali_current.weekday())
        english_day = current_date.strftime("%A")
        
        # Format Nepali date with Nepali numerals
        nepali_year = to_nepali_numerals(nepali_current.year)
        nepali_month = to_nepali_numerals(nepali_current.month)
        nepali_day_num = to_nepali_numerals(nepali_current.day)
        nepali_date_str = f"{nepali_year}-{nepali_month}-{nepali_day_num}"
        
        # Format English date
        english_date_str = current_date.strftime("%Y-%m-%d")
        
        print(f"नेपाली मिति: {nepali_day} {nepali_date_str}")
        print(f"English Date: {english_day} {english_date_str}")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 