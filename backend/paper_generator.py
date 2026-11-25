import os
import uuid
import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib import colors

UPLOAD_DIR = Path(__file__).resolve().parent / "uploads" / "question_papers"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def create_pdf(file_path: Path, title: str, subtitle: str, meta_info: dict, content_items: list, is_solution: bool = False):
    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=letter,
        rightMargin=40, leftMargin=40,
        topMargin=40, bottomMargin=40
    )
    styles = getSampleStyleSheet()

    header_style = ParagraphStyle(
        "HeaderStyle",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f172a" if not is_solution else "#047857"),
        alignment=1,
        fontName="Helvetica-Bold"
    )
    sub_style = ParagraphStyle(
        "SubStyle",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#475569"),
        alignment=1,
        fontName="Helvetica-Oblique"
    )
    q_title_style = ParagraphStyle(
        "QTitleStyle",
        parent=styles["Heading3"],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1e293b"),
        fontName="Helvetica-Bold",
        spaceBefore=10,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        fontName="Helvetica"
    )
    sol_style = ParagraphStyle(
        "SolStyle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#065f46"),
        fontName="Helvetica-Bold",
        spaceBefore=4
    )
    explanation_style = ParagraphStyle(
        "ExpStyle",
        parent=styles["Normal"],
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#1e293b"),
        fontName="Helvetica"
    )

    story = []
    story.append(Paragraph(title, header_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(subtitle, sub_style))
    story.append(Spacer(1, 12))

    meta_data = [
        [f"Subject: {meta_info.get('subject')}", f"Course: {meta_info.get('course')} - {meta_info.get('academic_year')}"],
        [f"Institution: {meta_info.get('curriculum')}", f"Exam Year: {meta_info.get('year')}"],
        [f"Max Marks: {meta_info.get('total_marks', 50)}", f"Duration: {meta_info.get('time_limit', '2 Hours')}"]
    ]
    t = Table(meta_data, colWidths=[260, 260])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#334155")),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
    ]))
    story.append(t)
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#94a3b8"), spaceBefore=2, spaceAfter=14))

    for item in content_items:
        q_num = item["question_number"]
        q_text = item["question_text"]
        q_topic = item.get("topic", "General Core")

        story.append(Paragraph(f"<b>Q{q_num}. [{q_topic}]</b> {q_text}", q_title_style))
        story.append(Spacer(1, 4))

        if "options" in item and item["options"]:
            for opt_idx, opt in enumerate(item["options"]):
                prefix = chr(65 + opt_idx)
                is_correct = (opt_idx == item.get("correct_option")) if is_solution else False
                opt_color = "#047857" if is_correct else "#334155"
                check_mark = "  ✓ (CORRECT ANSWER)" if is_correct else ""
                opt_text = f"<b>({prefix})</b> {opt}{check_mark}"
                opt_p = Paragraph(opt_text, ParagraphStyle(
                    f"Opt_{q_num}_{opt_idx}",
                    parent=body_style,
                    textColor=colors.HexColor(opt_color),
                    fontName="Helvetica-Bold" if is_correct else "Helvetica"
                ))
                story.append(opt_p)
                story.append(Spacer(1, 2))

        if is_solution and "step_by_step_solution" in item:
            story.append(Spacer(1, 4))
            correct_letter = chr(65 + item['correct_option'])
            story.append(Paragraph(f"<b>Key Answer:</b> Option {correct_letter} — {item['options'][item['correct_option']]}", sol_style))
            story.append(Spacer(1, 2))
            story.append(Paragraph(f"<b>Detailed Conceptual Solution:</b> {item['step_by_step_solution']}", explanation_style))

        story.append(Spacer(1, 12))

    doc.build(story)


def generate_paper_pdfs(file_code: str, title: str, exam_name: str, meta_info: dict, questions: list) -> Tuple[str, str]:
    qp_filename = f"{file_code}_qp.pdf"
    key_filename = f"{file_code}_key.pdf"

    qp_path = UPLOAD_DIR / qp_filename
    key_path = UPLOAD_DIR / key_filename

    create_pdf(
        file_path=qp_path,
        title=title,
        subtitle=f"{exam_name} • Question Paper",
        meta_info=meta_info,
        content_items=questions,
        is_solution=False
    )

    create_pdf(
        file_path=key_path,
        title=f"ANSWER KEY & DETAILED SOLUTIONS\n{title}",
        subtitle="Verified Step-by-Step Conceptual Solutions & Grading Key",
        meta_info=meta_info,
        content_items=questions,
        is_solution=True
    )

    rel_qp = f"question_papers/{qp_filename}"
    rel_key = f"question_papers/{key_filename}"
    return rel_qp, rel_key


SUBJECT_QUESTION_BANKS = {
    "marketing": [
        {
            "topic": "Market Segmentation, Targeting & Positioning (STP)",
            "question_text": "Which basis of market segmentation divides buyers into groups according to their knowledge, attitude, use, or response to a product?",
            "options": ["Behavioral Segmentation", "Psychographic Segmentation", "Demographic Segmentation", "Geographic Segmentation"],
            "correct_option": 0,
            "step_by_step_solution": "Behavioral segmentation divides buyers into groups based on their knowledge, attitudes, uses, or responses to a product, such as occasion-based buying, user status, or loyalty rate."
        },
        {
            "topic": "Marketing Mix (4Ps: Product Strategy)",
            "question_text": "In the BCG Growth-Share Matrix, a Strategic Business Unit (SBU) with low relative market share in a high-growth market is classified as a:",
            "options": ["Star", "Cash Cow", "Question Mark (Problem Child)", "Dog"],
            "correct_option": 2,
            "step_by_step_solution": "Question Marks have low market share in high-growth industries. They require significant cash injection to build share into Stars before market growth slows."
        },
        {
            "topic": "Consumer Buying Decision Process",
            "question_text": "What is the final stage of the five-stage consumer buying decision model?",
            "options": ["Information Search", "Purchase Decision", "Post-Purchase Behavior & Evaluation", "Alternative Evaluation"],
            "correct_option": 2,
            "step_by_step_solution": "The 5 stages are: Problem Recognition -> Information Search -> Evaluation of Alternatives -> Purchase Decision -> Post-Purchase Behavior (including satisfaction or cognitive dissonance)."
        },
        {
            "topic": "Pricing Strategies & Value Realization",
            "question_text": "Setting prices just below whole round numbers (e.g., $99.99 instead of $100.00) is a hallmark of:",
            "options": ["Psychological / Odd-Even Pricing", "Target Return Pricing", "Going-Rate Pricing", "Cost-Plus Markup Pricing"],
            "correct_option": 0,
            "step_by_step_solution": "Psychological pricing considers consumer perception; odd pricing creates an illusion of a lower price and a calculated bargain."
        }
    ],
    "finance": [
        {
            "topic": "Capital Budgeting & Project Evaluation",
            "question_text": "The discount rate that equates the present value of future expected cash inflows with the initial capital expenditure outlay is known as:",
            "options": ["Accounting Rate of Return (ARR)", "Internal Rate of Return (IRR)", "Weighted Average Cost of Capital (WACC)", "Modified Duration"],
            "correct_option": 1,
            "step_by_step_solution": "The Internal Rate of Return (IRR) is the exact discount rate at which Net Present Value (NPV) equals zero: PV(Inflows) - Outlay = 0."
        },
        {
            "topic": "Working Capital & Cash Management",
            "question_text": "Under the Miller-Orr cash management model, when the firm's cash balance touches the Upper Control Limit (UCL), the financial manager should:",
            "options": ["Sell marketable securities to raise cash", "Invest excess cash in marketable securities to return to the return point (Z)", "Borrow short-term commercial paper", "Declare an immediate stock dividend"],
            "correct_option": 1,
            "step_by_step_solution": "When cash reaches the Upper Limit, the excess cash (UCL - Return Point) is invested into interest-bearing marketable securities to restore liquidity back to optimal level Z."
        },
        {
            "topic": "Cost of Capital & Leverage",
            "question_text": "If a company has an Operating Leverage of 2.0 and a Financial Leverage of 1.5, its Combined (Total) Leverage is:",
            "options": ["0.5", "3.0", "3.5", "1.33"],
            "correct_option": 1,
            "step_by_step_solution": "Combined Leverage = Operating Leverage * Financial Leverage = 2.0 * 1.5 = 3.0. A 1% change in sales will produce a 3% change in Earnings Per Share."
        },
        {
            "topic": "Financial Ratio Analysis",
            "question_text": "The DuPont analysis decomposes Return on Equity (ROE) into which three fundamental components?",
            "options": ["Net Profit Margin, Asset Turnover, and Financial Leverage (Equity Multiplier)", "Gross Margin, Operating Margin, and Current Ratio", "Current Assets, Fixed Assets, and Working Capital", "EBIT, Tax Rate, and Dividend Payout Ratio"],
            "correct_option": 0,
            "step_by_step_solution": "DuPont ROE = (Net Income / Sales) * (Sales / Assets) * (Assets / Equity) = Net Profit Margin * Asset Turnover * Equity Multiplier."
        }
    ],
    "human resource": [
        {
            "topic": "Recruitment & Talent Selection",
            "question_text": "Which selection test is specifically designed to assess a candidate's innate ability to learn a new skill or acquire specialized knowledge?",
            "options": ["Aptitude Test", "Achievement Test", "Projective Personality Test", "Polygraph Examination"],
            "correct_option": 0,
            "step_by_step_solution": "Aptitude tests measure potential capacity to learn or perform new tasks. Achievement tests measure acquired proficiency or knowledge already mastered."
        },
        {
            "topic": "Performance Appraisal Systems",
            "question_text": "A performance appraisal error where a manager evaluates an employee based solely on their most recent month's performance rather than the whole appraisal year is called:",
            "options": ["Halo Effect", "Recency Error", "Leniency Bias", "Central Tendency Bias"],
            "correct_option": 1,
            "step_by_step_solution": "Recency bias occurs when evaluators overweight events in the recent memory of the appraisal cycle rather than assessing comprehensive year-round performance."
        },
        {
            "topic": "Motivation & Job Design",
            "question_text": "In the Hackman and Oldham Job Characteristics Model, which core job dimension directly fosters the critical psychological state of 'Experienced Responsibility for Outcomes'?",
            "options": ["Skill Variety", "Task Identity", "Autonomy", "Feedback from the Job"],
            "correct_option": 2,
            "step_by_step_solution": "Autonomy provides freedom and discretion in scheduling work and determining procedures, directly producing experienced responsibility for work outcomes."
        },
        {
            "topic": "Organizational Behavior & Conflict Handling",
            "question_text": "Which conflict handling style in the Thomas-Kilmann model represents low assertiveness and high cooperativeness, sacrificing one's own goals to appease others?",
            "options": ["Accommodating", "Competing", "Collaborating", "Avoiding"],
            "correct_option": 0,
            "step_by_step_solution": "Accommodating prioritizes relationship preservation and fulfilling the other party's concerns at the expense of one's own immediate interests."
        }
    ]
}


def get_ai_paper_questions(subject: str) -> list:
    sub_lower = subject.lower()
    for key, q_list in SUBJECT_QUESTION_BANKS.items():
        if key in sub_lower:
            return [
                {**q, "question_number": i + 1}
                for i, q in enumerate(q_list)
            ]
    # Default high-yield business questions
    return [
        {
            "question_number": 1,
            "topic": f"{subject} Core Principles",
            "question_text": f"In {subject}, which primary strategic management framework emphasizes continuous competitive advantage through internal resource alignment?",
            "options": ["Resource-Based View (RBV)", "Contingency Theory", "Scientific Management", "Classical Bureaucratic Model"],
            "correct_option": 0,
            "step_by_step_solution": "The Resource-Based View (RBV) posits that internal resources that are Valuable, Rare, Inimitable, and Non-substitutable (VRIN) serve as the foundation for sustainable competitive advantage."
        },
        {
            "question_number": 2,
            "topic": f"{subject} Decision Analysis",
            "question_text": "Which quantitative decision-making tool maps alternative options, uncertain event probabilities, and expected monetary payoffs?",
            "options": ["Decision Tree Analysis", "Pareto Chart", "Fishbone Diagram", "Gantt Milestone Schedule"],
            "correct_option": 0,
            "step_by_step_solution": "A Decision Tree graphically depicts decisions, chance events, and resulting payoffs to compute Expected Monetary Value (EMV)."
        },
        {
            "question_number": 3,
            "topic": f"{subject} Performance Evaluation",
            "question_text": "The Balanced Scorecard evaluates organizational performance across which four distinct perspectives?",
            "options": ["Financial, Customer, Internal Business Processes, and Learning & Growth", "Sales, Marketing, HR, and Accounting", "Short-term, Medium-term, Long-term, and Contingent", "Assets, Liabilities, Equity, and Retained Earnings"],
            "correct_option": 0,
            "step_by_step_solution": "Kaplan and Norton's Balanced Scorecard links strategic objectives across 4 perspectives: Financial, Customer, Internal Business Processes, and Organizational Learning/Growth."
        },
        {
            "question_number": 4,
            "topic": f"{subject} Governance & Ethics",
            "question_text": "What corporate governance principle demands truthful, accurate, and timely disclosure of material operational and financial matters?",
            "options": ["Transparency & Accountability", "Absolute Secrecy", "Arbitrary Discretion", "Selective Dissemination"],
            "correct_option": 0,
            "step_by_step_solution": "Transparency requires timely, accurate, and complete disclosure of financial results, governance structures, and risks to stakeholders."
        }
    ]
