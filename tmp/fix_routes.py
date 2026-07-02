
import os

target = r'c:\Users\SUBHASH\Music\vultr_astra_2\app\prescriptions\prescription_routes.py'
with open(target, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'name: str = Field(..., description="Medicine name")' in line:
        new_lines.append(line)
        new_lines.append('    shopify_variant_id: Optional[str] = Field(default=None)\n')
    elif 'frequency: str = Field(..., description="Frequency (once_daily, twice_daily, etc.)")' in line:
        new_lines.append(line)
        new_lines.append('    timing: Optional[str] = Field(default="After Food")\n')
    else:
        new_lines.append(line)

with open(target, 'w') as f:
    f.writelines(new_lines)
print("Updated successfully")
