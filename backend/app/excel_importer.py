import os
import hashlib
from datetime import datetime, date
from typing import Dict, Any, Tuple, List
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.app.models import (
    Student, Enrollment, Attendance, Assessment, FeePayment, UploadedDataset
)

MANDATORY_SHEETS = {
    "Students": [
        "student_id", "student_name", "age", "gender", "city", 
        "email", "admission_date", "education_level"
    ],
    "Enrollments": [
        "enrollment_id", "student_id", "course", "enrollment_date", 
        "batch_id", "course_fee", "enrollment_status", "delivery_mode"
    ],
    "Attendance": [
        "attendance_id", "student_id", "batch_id", "attendance_date", 
        "session_topic", "attendance_status", "session_duration_minutes"
    ],
    "Assessments": [
        "assessment_id", "student_id", "course", "assessment_date", 
        "assessment_type", "score", "max_score", "grade", "submission_status"
    ],
    "Fee_Payments": [
        "payment_id", "student_id", "payment_date", "amount", 
        "payment_method", "payment_status", "installment_no", "receipt_no"
    ]
}

def compute_checksum(file_path: str) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def validate_and_preview_excel(file_path: str) -> Dict[str, Any]:
    """Inspects workbook, verifies all mandatory sheets and columns, data types, duplicate IDs, missing values, FK references."""
    errors = []
    warnings = []
    previews = []
    record_counts = {}
    column_checks = {}
    foreign_key_errors = []

    try:
        xl = pd.ExcelFile(file_path)
    except Exception as e:
        return {
            "is_valid": False,
            "filename": os.path.basename(file_path),
            "sheets_found": [],
            "missing_sheets": list(MANDATORY_SHEETS.keys()),
            "record_counts": {},
            "column_checks": {},
            "foreign_key_errors": [],
            "warnings": [],
            "errors": [f"Invalid Excel file or corrupted format: {str(e)}"],
            "previews": []
        }

    sheets_found = xl.sheet_names
    missing_sheets = [s for s in MANDATORY_SHEETS.keys() if s not in sheets_found]

    if missing_sheets:
        errors.append(f"Missing mandatory worksheet(s): {', '.join(missing_sheets)}")

    dfs = {}
    for sheet_name in MANDATORY_SHEETS.keys():
        if sheet_name in sheets_found:
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                dfs[sheet_name] = df
                record_counts[sheet_name] = len(df)
                
                # Check mandatory columns
                expected_cols = MANDATORY_SHEETS[sheet_name]
                actual_cols = list(df.columns)
                missing_cols = [c for c in expected_cols if c not in actual_cols]
                
                if missing_cols:
                    column_checks[sheet_name] = False
                    errors.append(f"Sheet '{sheet_name}' is missing columns: {', '.join(missing_cols)}")
                else:
                    column_checks[sheet_name] = True

                # Check duplicates on primary ID
                pk_col = expected_cols[0]
                if pk_col in df.columns:
                    dups = df[pk_col].duplicated().sum()
                    if dups > 0:
                        errors.append(f"Sheet '{sheet_name}' has {dups} duplicate primary key values in '{pk_col}'.")

                # Check missing values
                missing_total = df.isna().sum().sum()
                if missing_total > 0:
                    warnings.append(f"Sheet '{sheet_name}' has {missing_total} missing cells across columns.")

                # Prepare sample preview
                sample_data = df.head(5).to_dict(orient="records")
                # Format dates and numbers for JSON
                for row in sample_data:
                    for k, v in row.items():
                        if isinstance(v, (datetime, date, pd.Timestamp)):
                            row[k] = v.strftime("%Y-%m-%d")
                        elif pd.isna(v):
                            row[k] = None

                previews.append({
                    "sheet_name": sheet_name,
                    "row_count": len(df),
                    "columns": actual_cols,
                    "dtypes": {c: str(df[c].dtype) for c in actual_cols},
                    "sample_data": sample_data
                })

            except Exception as e:
                errors.append(f"Error reading worksheet '{sheet_name}': {str(e)}")
        else:
            column_checks[sheet_name] = False

    # Foreign Key validation
    if "Students" in dfs and "student_id" in dfs["Students"].columns:
        valid_student_ids = set(dfs["Students"]["student_id"].dropna())

        for rel_sheet in ["Enrollments", "Attendance", "Assessments", "Fee_Payments"]:
            if rel_sheet in dfs and "student_id" in dfs[rel_sheet].columns:
                rel_student_ids = set(dfs[rel_sheet]["student_id"].dropna())
                orphans = rel_student_ids - valid_student_ids
                if orphans:
                    fk_msg = f"{len(orphans)} student_id(s) in sheet '{rel_sheet}' do not exist in 'Students' sheet."
                    foreign_key_errors.append(fk_msg)
                    errors.append(fk_msg)

    # Check for invalid amounts
    if "Fee_Payments" in dfs and "amount" in dfs["Fee_Payments"].columns:
        invalid_amounts = dfs["Fee_Payments"][dfs["Fee_Payments"]["amount"] < 0]
        if not invalid_amounts.empty:
            errors.append(f"Fee_Payments contains {len(invalid_amounts)} negative payment amounts.")

    if "Enrollments" in dfs and "course_fee" in dfs["Enrollments"].columns:
        invalid_fees = dfs["Enrollments"][dfs["Enrollments"]["course_fee"] < 0]
        if not invalid_fees.empty:
            errors.append(f"Enrollments contains {len(invalid_fees)} negative course fees.")

    is_valid = len(errors) == 0

    return {
        "is_valid": is_valid,
        "filename": os.path.basename(file_path),
        "sheets_found": sheets_found,
        "missing_sheets": missing_sheets,
        "record_counts": record_counts,
        "column_checks": column_checks,
        "foreign_key_errors": foreign_key_errors,
        "warnings": warnings,
        "errors": errors,
        "previews": previews
    }

def import_excel_to_db(file_path: str, db: Session, uploaded_by: str = "Admin") -> Tuple[bool, str, Dict[str, int]]:
    """Imports validated Excel dataset into database tables, avoiding duplicate imports."""
    validation = validate_and_preview_excel(file_path)
    if not validation["is_valid"]:
        return False, f"Validation failed: {'; '.join(validation['errors'])}", {}

    checksum = compute_checksum(file_path)
    
    # Check if this exact checksum has already been imported
    existing_upload = db.query(UploadedDataset).filter(UploadedDataset.checksum == checksum).first()
    if existing_upload and existing_upload.status == "Imported":
        # Check if tables already have records
        stu_count = db.query(Student).count()
        if stu_count > 0:
            return True, f"Dataset '{os.path.basename(file_path)}' was previously imported. Existing records are active.", {
                "students": existing_upload.student_count,
                "enrollments": existing_upload.enrollment_count,
                "attendance": existing_upload.attendance_count,
                "assessments": existing_upload.assessment_count,
                "fee_payments": existing_upload.payment_count
            }

    file_size = os.path.getsize(file_path)
    
    # Read all sheets
    students_df = pd.read_excel(file_path, sheet_name="Students")
    enrollments_df = pd.read_excel(file_path, sheet_name="Enrollments")
    attendance_df = pd.read_excel(file_path, sheet_name="Attendance")
    assessments_df = pd.read_excel(file_path, sheet_name="Assessments")
    fee_payments_df = pd.read_excel(file_path, sheet_name="Fee_Payments")

    # Clear existing operational tables to maintain pure consistency with dataset
    db.execute(text("DELETE FROM fee_payments"))
    db.execute(text("DELETE FROM assessments"))
    db.execute(text("DELETE FROM attendance"))
    db.execute(text("DELETE FROM enrollments"))
    db.execute(text("DELETE FROM students"))
    db.commit()

    # 1. Insert Students
    student_records = []
    for _, row in students_df.iterrows():
        adm_date = row["admission_date"]
        if isinstance(adm_date, pd.Timestamp):
            adm_date = adm_date.date()
        elif isinstance(adm_date, str):
            adm_date = datetime.strptime(adm_date[:10], "%Y-%m-%d").date()

        student_records.append(Student(
            student_id=str(row["student_id"]).strip(),
            student_name=str(row["student_name"]).strip(),
            age=int(row["age"]),
            gender=str(row["gender"]).strip(),
            city=str(row["city"]).strip(),
            email=str(row["email"]).strip(),
            admission_date=adm_date,
            education_level=str(row["education_level"]).strip()
        ))
    db.bulk_save_objects(student_records)
    db.commit()

    # 2. Insert Enrollments
    enrollment_records = []
    for _, row in enrollments_df.iterrows():
        enr_date = row["enrollment_date"]
        if isinstance(enr_date, pd.Timestamp):
            enr_date = enr_date.date()
        elif isinstance(enr_date, str):
            enr_date = datetime.strptime(enr_date[:10], "%Y-%m-%d").date()

        enrollment_records.append(Enrollment(
            enrollment_id=str(row["enrollment_id"]).strip(),
            student_id=str(row["student_id"]).strip(),
            course=str(row["course"]).strip(),
            enrollment_date=enr_date,
            batch_id=str(row["batch_id"]).strip(),
            course_fee=float(row["course_fee"]),
            enrollment_status=str(row["enrollment_status"]).strip(),
            delivery_mode=str(row["delivery_mode"]).strip()
        ))
    db.bulk_save_objects(enrollment_records)
    db.commit()

    # 3. Insert Attendance
    attendance_records = []
    for _, row in attendance_df.iterrows():
        att_date = row["attendance_date"]
        if isinstance(att_date, pd.Timestamp):
            att_date = att_date.date()
        elif isinstance(att_date, str):
            att_date = datetime.strptime(att_date[:10], "%Y-%m-%d").date()

        attendance_records.append(Attendance(
            attendance_id=str(row["attendance_id"]).strip(),
            student_id=str(row["student_id"]).strip(),
            batch_id=str(row["batch_id"]).strip(),
            attendance_date=att_date,
            session_topic=str(row["session_topic"]).strip(),
            attendance_status=str(row["attendance_status"]).strip(),
            session_duration_minutes=int(row["session_duration_minutes"])
        ))
    db.bulk_save_objects(attendance_records)
    db.commit()

    # 4. Insert Assessments
    assessment_records = []
    for _, row in assessments_df.iterrows():
        asm_date = row["assessment_date"]
        if isinstance(asm_date, pd.Timestamp):
            asm_date = asm_date.date()
        elif isinstance(asm_date, str):
            asm_date = datetime.strptime(asm_date[:10], "%Y-%m-%d").date()

        assessment_records.append(Assessment(
            assessment_id=str(row["assessment_id"]).strip(),
            student_id=str(row["student_id"]).strip(),
            course=str(row["course"]).strip(),
            assessment_date=asm_date,
            assessment_type=str(row["assessment_type"]).strip(),
            score=float(row["score"]),
            max_score=float(row["max_score"]),
            grade=str(row["grade"]).strip(),
            submission_status=str(row["submission_status"]).strip()
        ))
    db.bulk_save_objects(assessment_records)
    db.commit()

    # 5. Insert Fee Payments
    fee_records = []
    for _, row in fee_payments_df.iterrows():
        pay_date = row["payment_date"]
        if isinstance(pay_date, pd.Timestamp):
            pay_date = pay_date.date()
        elif isinstance(pay_date, str):
            pay_date = datetime.strptime(pay_date[:10], "%Y-%m-%d").date()

        fee_records.append(FeePayment(
            payment_id=str(row["payment_id"]).strip(),
            student_id=str(row["student_id"]).strip(),
            payment_date=pay_date,
            amount=float(row["amount"]),
            payment_method=str(row["payment_method"]).strip(),
            payment_status=str(row["payment_status"]).strip(),
            installment_no=int(row["installment_no"]),
            receipt_no=str(row["receipt_no"]).strip()
        ))
    db.bulk_save_objects(fee_records)
    db.commit()

    # 6. Record upload in UploadedDataset
    dataset_log = UploadedDataset(
        filename=os.path.basename(file_path),
        file_size=file_size,
        checksum=checksum,
        student_count=len(student_records),
        enrollment_count=len(enrollment_records),
        attendance_count=len(attendance_records),
        assessment_count=len(assessment_records),
        payment_count=len(fee_records),
        status="Imported",
        uploaded_by=uploaded_by
    )
    db.add(dataset_log)
    db.commit()

    counts = {
        "students": len(student_records),
        "enrollments": len(enrollment_records),
        "attendance": len(attendance_records),
        "assessments": len(assessment_records),
        "fee_payments": len(fee_records)
    }

    return True, f"Successfully imported {counts['students']} students, {counts['enrollments']} enrollments, {counts['attendance']} attendance records, {counts['assessments']} assessments, and {counts['fee_payments']} fee payments.", counts
