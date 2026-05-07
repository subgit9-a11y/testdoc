import sys
import re

file_path = r"c:\Users\SUBHASH\Desktop\AYUREZE PROJECT\ayureze-doctor-app-main\lib\screens\appointment\appointment_history.dart"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# The error was adding an extra }, and ) after the ListView.builder closing.
# The structure should be:
# itemBuilder: (context, i) {
#   return ...;
# },
# )
# But I added:
# itemBuilder: (context, i) {
#   return ...;
# },
# )
# },
# )

# I will find the specific blocks by looking for the ListView.builder structure followed by extra closers.
# Specifically around the ?: operators.

# Section 1: Upcoming search
# Section 2: Past search
# Section 3: Cancel search

# I'll use a regex that matches ); followed by }, ) followed by }, )
# and remove the last }, )

# Let's be very specific with the indentation if possible, but regex \s+ is safer.
new_content = re.sub(r'(\);\s+},\s+\))\s+},\s+\)', r'\1', content)

# Also check for any other structural issues.
# Wait, I should also check if I messed up the normal builders (not the search ones).

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Replacement done.")
