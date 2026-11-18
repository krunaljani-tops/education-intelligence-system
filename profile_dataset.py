import os
import json
import pandas as pd
import numpy as np

excel_file = "02_Education.xlsx"

xl = pd.ExcelFile(excel_file)
sheet_names = xl.sheet_names
print(f"Worksheet Names: {sheet_names}")

profile = {}

for sheet in sheet_names:
    df = pd.read_excel(excel_file, sheet_name=sheet)
    num_records = len(df)
    columns = list(df.columns)
    dtypes = {col: str(df[col].dtype) for col in columns}
    missing = {col: int(df[col].isna().sum()) for col in columns}
    duplicates = int(df.duplicated().sum())
    unique_counts = {col: int(df[col].nunique()) for col in columns}
    
    # Check sample values
    sample = df.head(3).to_dict(orient="records")
    
    profile[sheet] = {
        "num_records": num_records,
        "columns": columns,
        "dtypes": dtypes,
        "missing_values": missing,
        "duplicate_rows": duplicates,
        "unique_values": unique_counts,
        "sample": sample
    }
    
    print(f"\n--- Sheet: {sheet} ---")
    print(f"Records: {num_records}")
    print(f"Columns: {columns}")
    print(f"Duplicates: {duplicates}")
    print("Missing values:", missing)
    print("Unique counts:", unique_counts)

# Let's inspect foreign keys & relationships
print("\n=== Relationship Validation ===")
students_df = pd.read_excel(excel_file, sheet_name="Students")
enrollments_df = pd.read_excel(excel_file, sheet_name="Enrollments")
attendance_df = pd.read_excel(excel_file, sheet_name="Attendance")
assessments_df = pd.read_excel(excel_file, sheet_name="Assessments")
fee_payments_df = pd.read_excel(excel_file, sheet_name="Fee_Payments")

stu_ids = set(students_df['student_id'].dropna())
enr_ids = set(enrollments_df['enrollment_id'].dropna())
att_ids = set(attendance_df['attendance_id'].dropna())
asm_ids = set(assessments_df['assessment_id'].dropna())
pay_ids = set(fee_payments_df['payment_id'].dropna())

print(f"Unique student_ids in Students: {len(stu_ids)}")
print(f"Duplicate student_id in Students: {students_df['student_id'].duplicated().sum()}")
print(f"Duplicate enrollment_id in Enrollments: {enrollments_df['enrollment_id'].duplicated().sum()}")
print(f"Duplicate attendance_id in Attendance: {attendance_df['attendance_id'].duplicated().sum()}")
print(f"Duplicate assessment_id in Assessments: {assessments_df['assessment_id'].duplicated().sum()}")
print(f"Duplicate payment_id in Fee_Payments: {fee_payments_df['payment_id'].duplicated().sum()}")

# Foreign key checks
enr_stu_diff = set(enrollments_df['student_id']) - stu_ids
att_stu_diff = set(attendance_df['student_id']) - stu_ids
asm_stu_diff = set(assessments_df['student_id']) - stu_ids
pay_stu_diff = set(fee_payments_df['student_id']) - stu_ids

print(f"Enrollment student_ids not in Students: {len(enr_stu_diff)}")
print(f"Attendance student_ids not in Students: {len(att_stu_diff)}")
print(f"Assessments student_ids not in Students: {len(asm_stu_diff)}")
print(f"Fee_Payments student_ids not in Students: {len(pay_stu_diff)}")

# Batches and Courses
courses_in_enr = sorted(enrollments_df['course'].unique().tolist())
courses_in_asm = sorted(assessments_df['course'].unique().tolist())
print(f"Courses in Enrollments ({len(courses_in_enr)}): {courses_in_enr}")
print(f"Courses in Assessments ({len(courses_in_asm)}): {courses_in_asm}")

batches_in_enr = sorted(enrollments_df['batch_id'].unique().tolist())
batches_in_att = sorted(attendance_df['batch_id'].unique().tolist())
print(f"Unique batches in Enrollments: {len(batches_in_enr)}")
print(f"Unique batches in Attendance: {len(batches_in_att)}")

# Save detailed profiling result
with open("dataset_profile.json", "w") as f:
    json.dump(profile, f, indent=2, default=str)
print("\nProfile saved to dataset_profile.json")
