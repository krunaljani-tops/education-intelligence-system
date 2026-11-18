from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List, Optional

from backend.app.database import get_db
from backend.app.models import FeePayment
from backend.app.schemas import FeePaymentOut

def is_valid_filter(val: Optional[str]) -> bool:
    if val is None:
        return False
    s = str(val).strip()
    return s != "" and s.lower() not in ("undefined", "null", "none", "all")

router = APIRouter(prefix="/fees", tags=["Finance"])

@router.get("", response_model=List[FeePaymentOut])
def get_fee_payments(
    payment_status: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    installment_no: Optional[int] = Query(None),
    student_id: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    q = db.query(FeePayment)
    if is_valid_filter(payment_status):
        q = q.filter(FeePayment.payment_status == payment_status.strip())
    if is_valid_filter(payment_method):
        q = q.filter(FeePayment.payment_method == payment_method.strip())
    if installment_no is not None and str(installment_no).isdigit():
        q = q.filter(FeePayment.installment_no == int(installment_no))
    if is_valid_filter(student_id):
        q = q.filter(FeePayment.student_id == student_id.strip())
    return q.offset(skip).limit(limit).all()

@router.get("/summary")
def get_fees_summary(db: Session = Depends(get_db)):
    # Paid = Revenue
    paid_res = db.query(
        func.count(FeePayment.payment_id),
        func.sum(FeePayment.amount)
    ).filter(FeePayment.payment_status == "Paid").first()

    pending_res = db.query(
        func.count(FeePayment.payment_id),
        func.sum(FeePayment.amount)
    ).filter(FeePayment.payment_status == "Pending").first()

    failed_res = db.query(
        func.count(FeePayment.payment_id),
        func.sum(FeePayment.amount)
    ).filter(FeePayment.payment_status == "Failed").first()

    paid_amount = round(float(paid_res[1] or 0.0), 2)
    pending_amount = round(float(pending_res[1] or 0.0), 2)
    failed_amount = round(float(failed_res[1] or 0.0), 2)

    # Method analysis
    methods = (
        db.query(
            FeePayment.payment_method,
            func.count(FeePayment.payment_id),
            func.sum(case((FeePayment.payment_status == 'Paid', FeePayment.amount), else_=0))
        )
        .group_by(FeePayment.payment_method)
        .all()
    )
    methods_data = [
        {"method": m[0], "total_transactions": m[1], "paid_amount": round(float(m[2] or 0), 2)}
        for m in methods
    ]

    return {
        "collected_revenue": paid_amount,
        "paid_transactions": paid_res[0] or 0,
        "pending_amount": pending_amount,
        "pending_transactions": pending_res[0] or 0,
        "failed_amount": failed_amount,
        "failed_transactions": failed_res[0] or 0,
        "methods_summary": methods_data,
        "rule_note": "Strict compliance rule: Only 'Paid' transactions are recognized as revenue. Pending and Failed are tracked separately."
    }
