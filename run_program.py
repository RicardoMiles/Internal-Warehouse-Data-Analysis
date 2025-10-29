import os
import sys

# Support CML Parameters, for example:
# python run_all.py --yesterday
# python run_all.py 2025-10-29
# python run_all.py --date 2025-10-29

args = " ".join(sys.argv[1:])  # Concatenate command-line arguments into a single string and then pass that string to second program.

scripts = [
    f"combine_excel_sheets.py {args}",  # Add the arguments here
    f"process_merged_files.py {args}",  # Add the arguments here
    "generate_weekly_report.py",
]

for script in scripts:
    print(f"Running {script} ...")
    os.system(f"python {script}")

print("All done!")
