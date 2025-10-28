import os

scripts = ["combine_excel_sheets.py", "process_merged_files.py", "generate_weekly_report.py"]

for script in scripts:
    print(f"Running {script} ...")
    os.system(f"python {script}")

print("All done!")
