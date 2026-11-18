import pandas as pd

excel_file = "02_Education.xlsx"

students_df = pd.read_excel(excel_file, sheet_name="Students")
enrollments_df = pd.read_excel(excel_file, sheet_name="Enrollments")
attendance_df = pd.read_excel(excel_file, sheet_name="Attendance")
assessments_df = pd.read_excel(excel_file, sheet_name="Assessments")
fee_payments_df = pd.read_excel(excel_file, sheet_name="Fee_Payments")

total_students = len(students_df)
total_enrollments = len(enrollments_df)
active_enrollments = len(enrollments_df[enrollments_df['enrollment_status'] == 'Active'])
completed_enrollments = len(enrollments_df[enrollments_df['enrollment_status'] == 'Completed'])
dropped_enrollments = len(enrollments_df[enrollments_df['enrollment_status'] == 'Dropped'])
on_hold_enrollments = len(enrollments_df[enrollments_df['enrollment_status'] == 'On Hold'])

# Attendance calculations
total_attendance_records = len(attendance_df)
present_records = len(attendance_df[attendance_df['attendance_status'] == 'Present'])
late_records = len(attendance_df[attendance_df['attendance_status'] == 'Late'])
absent_records = len(attendance_df[attendance_df['attendance_status'] == 'Absent'])
attendance_percentage = (present_records / total_attendance_records) * 100

# Assessment calculations
total_assessments = len(assessments_df)
avg_score = assessments_df['score'].mean()
avg_score_pct = (assessments_df['score'] / assessments_df['max_score']).mean() * 100

# Fee calculations
paid_df = fee_payments_df[fee_payments_df['payment_status'] == 'Paid']
pending_df = fee_payments_df[fee_payments_df['payment_status'] == 'Pending']
failed_df = fee_payments_df[fee_payments_df['payment_status'] == 'Failed']

total_paid_revenue = paid_df['amount'].sum()
total_pending_amount = pending_df['amount'].sum()
total_failed_amount = failed_df['amount'].sum()

print("=== GROUND TRUTH CALCULATIONS ===")
print(f"Total Students: {total_students}")
print(f"Total Enrollments: {total_enrollments}")
print(f"Active Enrollments: {active_enrollments}")
print(f"Completed Enrollments: {completed_enrollments}")
print(f"Dropped Enrollments: {dropped_enrollments}")
print(f"On Hold Enrollments: {on_hold_enrollments}")
print(f"Attendance Total: {total_attendance_records}")
print(f"Present Records: {present_records}")
print(f"Late Records: {late_records}")
print(f"Absent Records: {absent_records}")
print(f"Average Attendance Percentage: {attendance_percentage:.2f}%")
print(f"Average Assessment Score: {avg_score:.2f}")
print(f"Total Paid Fee Collection: ₹{total_paid_revenue:,.2f}")
print(f"Pending Payments: ₹{total_pending_amount:,.2f}")
print(f"Failed Payments: ₹{total_failed_amount:,.2f}")
