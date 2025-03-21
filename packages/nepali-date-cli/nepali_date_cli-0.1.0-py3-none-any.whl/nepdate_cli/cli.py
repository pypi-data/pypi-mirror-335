#!/usr/bin/env python3
import sys
from datetime import datetime
from nepali_datetime import date as nepali_date

def main():
    try:
        # Get current date
        current_date = datetime.now()
        
        # Convert to Nepali date
        nepali_current = nepali_date.from_datetime_date(current_date.date())
        
        # Format the output
        nepali_date_str = nepali_current.strftime("%Y-%m-%d")
        english_date_str = current_date.strftime("%Y-%m-%d")
        
        print(f"Nepali Date: {nepali_date_str}")
        print(f"English Date: {english_date_str}")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 