import os

file_path = r'c:\Users\SUBHASH\Desktop\AYUREZE PROJECT\ayureze-doctor-app-main\lib\screens\profile\profile.dart'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Line numbers are 1-indexed in my view_file output.
# 574 is index 573.
lines[573] = lines[573].replace('],', '),')
# 577 is index 576. We need to remove it if it's an extra ).
# Let's see what 575, 576, 577 are.
# 575: ),
# 576: ),
# 577: ),
# We need to close: Column, Container, SingleChildScrollView, Form, GestureDetector. (5 widgets)
# children list ended at 571.
# 572: Column
# 573: Container
# 574: SingleChildScrollView
# 575: Form
# 576: GestureDetector
# So 577 should be REMOVED.

# Wait, let's verify.
# 380: Step(
# 387: content: GestureDetector(
# 392: Form(
# 394: SingleChildScrollView(
# 395: Container(
# 396: Column(
# 397: children: [

# 571: ], (closes children)
# 572: ), (closes Column)
# 573: ), (closes Container)
# 574: ), (closes SingleChildScrollView)
# 575: ), (closes Form)
# 576: ), (closes GestureDetector)
# Total 5 closings after ].

lines[573] = lines[573].replace('],', '),')
# If 577 is index 576:
if index_to_remove := 576:
    lines.pop(index_to_remove)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Fixed profile.dart structural error.")
