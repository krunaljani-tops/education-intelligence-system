import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak, HRFlowable
)
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.agents.tools import EducationDatabaseTools
from backend.app.models import (
    AnalysisHistory, AgentExecutionLog, AIRecommendation, ApprovalHistory, GeneratedReport
)

def build_pdf_report(db: Session, analysis_id: str = None, generated_by: str = "Admin") -> str:
    """Generates an executive, professional multi-page PDF Education Business Intelligence Report."""
    tools = EducationDatabaseTools(db)
    stu_metrics = tools.get_student_metrics()
    enr_metrics = tools.get_enrollment_metrics()
    fin_metrics = tools.get_financial_metrics()
    acad_metrics = tools.get_academic_and_operations_metrics()

    # Fetch analysis run if available
    analysis_run = None
    agent_logs = []
    recs = []
    if analysis_id:
        analysis_run = db.query(AnalysisHistory).filter(AnalysisHistory.id == analysis_id).first()
        agent_logs = db.query(AgentExecutionLog).filter(AgentExecutionLog.analysis_id == analysis_id).all()
        recs = db.query(AIRecommendation).filter(AIRecommendation.analysis_id == analysis_id).all()
    else:
        # Latest analysis
        analysis_run = db.query(AnalysisHistory).order_by(AnalysisHistory.started_at.desc()).first()
        if analysis_run:
            analysis_id = analysis_run.id
            agent_logs = db.query(AgentExecutionLog).filter(AgentExecutionLog.analysis_id == analysis_id).all()
            recs = db.query(AIRecommendation).filter(AIRecommendation.analysis_id == analysis_id).all()

    approvals = db.query(ApprovalHistory).order_by(ApprovalHistory.reviewed_at.desc()).limit(10).all()

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"Education_Intelligence_Report_{timestamp}.pdf"
    file_path = os.path.join(settings.REPORTS_DIR, filename)

    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#4B5563"),
        spaceAfter=12
    )
    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1E40AF"),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1F2937")
    )
    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#111827")
    )
    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#111827")
    )

    elements = []

    # 1. Header Banner
    elements.append(Paragraph("AI-POWERED EDUCATION BUSINESS INTELLIGENCE SYSTEM", title_style))
    elements.append(Paragraph(
        f"<b>Dataset:</b> 02_Education.xlsx &nbsp;|&nbsp; <b>Coverage:</b> May 1, 2026 – Oct 31, 2026 (6 Months) &nbsp;|&nbsp; "
        f"<b>Currency:</b> INR (₹) &nbsp;|&nbsp; <b>Classification:</b> <font color='#DC2626'><b>DEMO DATA</b></font>",
        subtitle_style
    ))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3B82F6"), spaceAfter=10))

    # 2. Executive KPI Summary Table
    elements.append(Paragraph("1. Executive KPI Summary", h1_style))
    kpi_data = [
        [
            Paragraph("<b>Total Registered Students</b>", table_cell),
            Paragraph(f"{stu_metrics['total_students']:,}", table_cell_bold),
            Paragraph("<b>Total Course Enrollments</b>", table_cell),
            Paragraph(f"{enr_metrics['total_enrollments']:,}", table_cell_bold)
        ],
        [
            Paragraph("<b>Active Enrollments</b>", table_cell),
            Paragraph(f"{enr_metrics['status_distribution'].get('Active', 0):,}", table_cell),
            Paragraph("<b>Completed Enrollments</b>", table_cell),
            Paragraph(f"{enr_metrics['status_distribution'].get('Completed', 0):,}", table_cell)
        ],
        [
            Paragraph("<b>Dropped Enrollments</b>", table_cell),
            Paragraph(f"{enr_metrics['status_distribution'].get('Dropped', 0):,} ({round(enr_metrics['status_distribution'].get('Dropped', 0)/enr_metrics['total_enrollments']*100, 1)}%)", table_cell),
            Paragraph("<b>On Hold Enrollments</b>", table_cell),
            Paragraph(f"{enr_metrics['status_distribution'].get('On Hold', 0):,}", table_cell)
        ],
        [
            Paragraph("<b>Average Classroom Attendance</b>", table_cell),
            Paragraph(f"{acad_metrics['attendance']['attendance_percentage']}%", table_cell_bold),
            Paragraph("<b>Average Assessment Score</b>", table_cell),
            Paragraph(f"{acad_metrics['assessments']['average_score']}%", table_cell_bold)
        ],
        [
            Paragraph("<b>Total Paid Collections</b>", table_cell),
            Paragraph(f"₹{fin_metrics['total_paid_revenue']:,.2f}", table_cell_bold),
            Paragraph("<b>Pending Payments Volume</b>", table_cell),
            Paragraph(f"₹{fin_metrics['total_pending_amount']:,.2f}", table_cell)
        ],
        [
            Paragraph("<b>Failed Payments Volume</b>", table_cell),
            Paragraph(f"₹{fin_metrics['total_failed_amount']:,.2f}", table_cell),
            Paragraph("<b>Verification Gate Status</b>", table_cell),
            Paragraph(f"<font color='green'><b>{analysis_run.verification_status if analysis_run else 'APPROVED'}</b></font>", table_cell_bold)
        ]
    ]

    kpi_table = Table(kpi_data, colWidths=[140, 130, 140, 130])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 10))

    # 3. Course Enrollment & Popularity Table
    elements.append(Paragraph("2. Course Popularity and Performance Ranking", h1_style))
    course_headers = [
        Paragraph("<b>Course Program</b>", table_cell_bold),
        Paragraph("<b>Enrollments</b>", table_cell_bold),
        Paragraph("<b>Average Fee</b>", table_cell_bold),
        Paragraph("<b>Assessments</b>", table_cell_bold),
        Paragraph("<b>Avg Score</b>", table_cell_bold)
    ]
    course_rows = [course_headers]

    score_map = {c["course"]: c["avg_score"] for c in acad_metrics["assessments"]["course_performance"]}
    for c in enr_metrics["course_enrollment_ranking"]:
        course_rows.append([
            Paragraph(c["course"], table_cell),
            Paragraph(f"{c['enrollments']:,}", table_cell),
            Paragraph(f"₹{c['avg_fee']:,.2f}", table_cell),
            Paragraph(str(acad_metrics['assessments']['total_records'] // 8), table_cell),
            Paragraph(f"{score_map.get(c['course'], 'N/A')}%", table_cell)
        ])

    course_table = Table(course_rows, colWidths=[160, 85, 105, 95, 95])
    course_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EFF6FF")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(course_table)
    elements.append(Spacer(1, 10))

    # 4. Attendance & Academic Distribution
    elements.append(Paragraph("3. Attendance Operations and Examination Compliance", h1_style))
    att_summary = (
        f"<b>Attendance Sessions:</b> Total {acad_metrics['attendance']['total_records']:,} sessions logged. "
        f"Present: <b>{acad_metrics['attendance']['present_records']:,} ({acad_metrics['attendance']['attendance_percentage']}%)</b>, "
        f"Late: <b>{acad_metrics['attendance']['late_records']:,}</b>, Absent: <b>{acad_metrics['attendance']['absent_records']:,}</b>.<br/>"
        f"<b>Examinations:</b> Total {acad_metrics['assessments']['total_records']:,} exams. "
        f"Grade A: <b>{acad_metrics['assessments']['grade_distribution'].get('A', 0)}</b>, "
        f"Grade B: <b>{acad_metrics['assessments']['grade_distribution'].get('B', 0)}</b>, "
        f"Grade C: <b>{acad_metrics['assessments']['grade_distribution'].get('C', 0)}</b>, "
        f"Grade D: <b>{acad_metrics['assessments']['grade_distribution'].get('D', 0)}</b>.<br/>"
        f"<b>Submissions:</b> Submitted: {acad_metrics['assessments']['submission_status_distribution'].get('Submitted', 0)}, "
        f"Late: {acad_metrics['assessments']['submission_status_distribution'].get('Late', 0)}, "
        f"Missing: <b>{acad_metrics['assessments']['submission_status_distribution'].get('Missing', 0)}</b>."
    )
    elements.append(Paragraph(att_summary, body_style))
    elements.append(Spacer(1, 10))

    # 5. Financial Audit
    elements.append(Paragraph("4. Financial Audit & Revenue Recognition", h1_style))
    fin_summary = (
        f"<b>Accounting Policy Compliance:</b> Only 'Paid' transactions are recognized as collected institutional revenue.<br/>"
        f"• <b>Successful Collections:</b> ₹{fin_metrics['total_paid_revenue']:,.2f} ({fin_metrics['paid_transactions_count']} transactions)<br/>"
        f"• <b>Pending Settlements:</b> ₹{fin_metrics['total_pending_amount']:,.2f} ({fin_metrics['pending_transactions_count']} transactions)<br/>"
        f"• <b>Failed Settlements:</b> ₹{fin_metrics['total_failed_amount']:,.2f} ({fin_metrics['failed_transactions_count']} transactions)<br/>"
        f"• <b>Payment Methods Breakdown:</b> " + ", ".join([f"{m['method']}: ₹{m['paid_amount']:,.2f} ({m['transaction_count']} tx)" for m in fin_metrics['payment_methods']])
    )
    elements.append(Paragraph(fin_summary, body_style))
    elements.append(Spacer(1, 10))

    # 6. Multi-Agent Findings
    elements.append(PageBreak())
    elements.append(Paragraph("5. Collaborative Findings from All Six AI Agents", h1_style))

    for log in agent_logs:
        agent_block = [
            Paragraph(f"<b>{log.agent_name}</b> <i>({log.agent_role})</i>", table_cell_bold),
            Paragraph(f"<b>Verification:</b> <font color='green'>{log.verification_status}</font> &nbsp;|&nbsp; <b>Execution:</b> {log.status}", table_cell),
            Paragraph(log.output_summary or "No summary recorded.", body_style)
        ]
        agent_table = Table([[Paragraph(f"<b>{log.agent_name}</b>", table_cell_bold)], [Paragraph(log.output_summary or '', body_style)]], colWidths=[540])
        agent_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(agent_table)
        elements.append(Spacer(1, 6))

    # 7. Strategic Recommendations & Management Action Plan
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("6. Strategic Recommendations & Action Plan", h1_style))

    rec_headers = [
        Paragraph("<b>Category & Problem</b>", table_cell_bold),
        Paragraph("<b>Recommended Action & Evidence</b>", table_cell_bold),
        Paragraph("<b>Expected Benefit</b>", table_cell_bold),
        Paragraph("<b>Priority & Status</b>", table_cell_bold)
    ]
    rec_rows = [rec_headers]

    for r in recs:
        rec_rows.append([
            Paragraph(f"<b>[{r.category}]</b><br/>{r.problem_identified}", table_cell),
            Paragraph(f"{r.recommended_action}<br/><font color='#6B7280'><i>Evidence: {r.dataset_evidence}</i></font>", table_cell),
            Paragraph(r.expected_benefit, table_cell),
            Paragraph(f"<b>{r.priority}</b><br/>Status: {r.status}", table_cell)
        ])

    rec_table = Table(rec_rows, colWidths=[150, 180, 130, 80])
    rec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#FEF3C7")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(rec_table)
    elements.append(Spacer(1, 10))

    # 8. Approval History Log
    elements.append(Paragraph("7. Management Decision and Human-in-the-Loop Approval History", h1_style))
    if approvals:
        app_rows = [[
            Paragraph("<b>Audit ID</b>", table_cell_bold),
            Paragraph("<b>Reviewer</b>", table_cell_bold),
            Paragraph("<b>Decision</b>", table_cell_bold),
            Paragraph("<b>Review Date</b>", table_cell_bold),
            Paragraph("<b>Manager Comments</b>", table_cell_bold)
        ]]
        for a in approvals:
            color = "green" if a.action == "APPROVED" else "red"
            app_rows.append([
                Paragraph(f"APP-{a.id}", table_cell),
                Paragraph(a.reviewer_name, table_cell),
                Paragraph(f"<font color='{color}'><b>{a.action}</b></font>", table_cell),
                Paragraph(a.reviewed_at.strftime("%Y-%m-%d %H:%M") if a.reviewed_at else "N/A", table_cell),
                Paragraph(a.manager_comments or "None", table_cell)
            ])
        app_table = Table(app_rows, colWidths=[60, 100, 70, 90, 220])
        app_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F3F4F6")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(app_table)
    else:
        elements.append(Paragraph("<i>No approval decisions logged yet. Recommendations are pending manager sign-off.</i>", body_style))

    doc.build(elements)
    file_size = os.path.getsize(file_path)

    # Log in database
    report_record = GeneratedReport(
        analysis_id=analysis_id,
        report_title=f"Executive Education Intelligence Report ({timestamp})",
        filename=filename,
        file_path=file_path,
        file_size=file_size,
        generated_by=generated_by
    )
    db.add(report_record)
    db.commit()
    db.refresh(report_record)

    return file_path, filename, report_record.id
