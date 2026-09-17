# ============================================================
# PDF_REPORT.PY
# ============================================================
#
# METRIUS EATS
#
# Generates a professional PDF report from ResultTracker data.
#
# The report contains:
#
#   - Simulation information
#   - Algorithms actually used
#   - Algorithm comparison table
#   - Individual algorithm results
#   - Performance comparison
#   - Best algorithm
#   - RL-specific information
#   - Allocation quality
#
# Requires:
#
#     reportlab
#
# Install once if needed:
#
#     pip install reportlab
#
# ============================================================

import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether
)


# ============================================================
# OUTPUT DIRECTORY
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

REPORTS_DIR = os.path.join(
    BASE_DIR,
    "reports"
)


# ============================================================
# HELPERS
# ============================================================

def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def format_number(value):
    value = safe_float(value)

    if value.is_integer():
        return str(int(value))

    return f"{value:.2f}"


def format_duration(seconds):
    seconds = max(
        0,
        int(safe_float(seconds))
    )

    minutes = seconds // 60
    seconds = seconds % 60

    return (
        f"{minutes:02d} min "
        f"{seconds:02d} sec"
    )


def format_datetime(timestamp):
    if not timestamp:
        return "--"

    try:
        return datetime.fromtimestamp(
            float(timestamp)
        ).strftime(
            "%d %b %Y, %I:%M:%S %p"
        )
    except (TypeError, ValueError, OSError):
        return "--"


def safe_text(value, default="--"):
    if value is None:
        return default

    text = str(value).strip()

    return text if text else default


# ============================================================
# PAGE HEADER / FOOTER
# ============================================================

def draw_page(canvas, document):
    canvas.saveState()

    width, height = A4

    # Header
    canvas.setFont(
        "Helvetica-Bold",
        8
    )

    canvas.setFillColor(
        colors.HexColor("#486581")
    )

    canvas.drawString(
        18 * mm,
        height - 12 * mm,
        "METRIUS EATS"
    )

    canvas.setFont(
        "Helvetica",
        8
    )

    canvas.setFillColor(
        colors.HexColor("#7B8794")
    )

    canvas.drawRightString(
        width - 18 * mm,
        height - 12 * mm,
        "RL Algorithm Evaluation"
    )

    # Header line
    canvas.setStrokeColor(
        colors.HexColor("#D9E2EC")
    )

    canvas.line(
        18 * mm,
        height - 16 * mm,
        width - 18 * mm,
        height - 16 * mm
    )

    # Footer
    canvas.line(
        18 * mm,
        14 * mm,
        width - 18 * mm,
        14 * mm
    )

    canvas.setFont(
        "Helvetica",
        7
    )

    canvas.setFillColor(
        colors.HexColor("#7B8794")
    )

    canvas.drawString(
        18 * mm,
        9 * mm,
        "Metrius Eats • Reinforcement Learning Simulation"
    )

    canvas.drawRightString(
        width - 18 * mm,
        9 * mm,
        f"Page {document.page}"
    )

    canvas.restoreState()


# ============================================================
# STYLES
# ============================================================

def build_styles():
    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=23,
            leading=27,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#102A43"),
            spaceAfter=5
        )
    )

    styles.add(
        ParagraphStyle(
            name="ReportSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#627D98"),
            spaceAfter=15
        )
    )

    styles.add(
        ParagraphStyle(
            name="Section",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#102A43"),
            spaceBefore=8,
            spaceAfter=7
        )
    )

    styles.add(
        ParagraphStyle(
            name="BodySmall",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334E68"),
            spaceAfter=5
        )
    )

    styles.add(
        ParagraphStyle(
            name="Winner",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#0F5132"),
            spaceBefore=6,
            spaceAfter=6
        )
    )

    styles.add(
        ParagraphStyle(
            name="SmallCenter",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#627D98")
        )
    )

    return styles


# ============================================================
# TABLE STYLE
# ============================================================

def apply_table_style(table, header=True):
    commands = [
        (
            "FONTNAME",
            (0, 0),
            (-1, -1),
            "Helvetica"
        ),
        (
            "FONTSIZE",
            (0, 0),
            (-1, -1),
            8
        ),
        (
            "TEXTCOLOR",
            (0, 0),
            (-1, -1),
            colors.HexColor("#334E68")
        ),
        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.4,
            colors.HexColor("#D9E2EC")
        ),
        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "MIDDLE"
        ),
        (
            "LEFTPADDING",
            (0, 0),
            (-1, -1),
            6
        ),
        (
            "RIGHTPADDING",
            (0, 0),
            (-1, -1),
            6
        ),
        (
            "TOPPADDING",
            (0, 0),
            (-1, -1),
            6
        ),
        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, -1),
            6
        ),
    ]

    if header:
        commands.extend([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#243B53")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
        ])

    table.setStyle(
        TableStyle(commands)
    )

    return table


# ============================================================
# BUILD COMPARISON TABLE
# ============================================================

def build_comparison_table(
    report_data,
    available_width
):
    algorithms = report_data.get(
        "algorithms_used",
        []
    )

    results = report_data.get(
        "results",
        {}
    )

    if not algorithms:
        return None

    rows = [
        [
            "Metric"
        ] + algorithms
    ]

    metrics = [
        ("Customers Served", "customers_served"),
        ("Average Wait Time", "average_wait_time"),
        ("Total Reward", "total_reward"),
        ("Penalties", "penalties"),
        ("Waste Penalties", "waste_penalties"),
        ("Q-Value Updates", "q_updates"),
        ("Successful Allocations", "successful_allocations"),
        ("Invalid Allocations", "invalid_allocations"),
    ]

    for label, key in metrics:
        row = [label]

        for algorithm in algorithms:
            value = results.get(
                algorithm,
                {}
            ).get(
                key,
                0
            )

            if key == "average_wait_time":
                display = (
                    f"{safe_float(value):.2f} sec"
                )
            elif key == "total_reward":
                display = (
                    f"{safe_float(value):+.2f}"
                )
            else:
                display = format_number(value)

            row.append(display)

        rows.append(row)

    # Dynamic column widths.
    first_width = 50 * mm
    remaining = max(
        70 * mm,
        available_width - first_width
    )

    algorithm_width = (
        remaining / max(
            1,
            len(algorithms)
        )
    )

    table = Table(
        rows,
        colWidths=[
            first_width
        ] + [
            algorithm_width
        ] * len(algorithms),
        repeatRows=1
    )

    apply_table_style(table)

    return table


# ============================================================
# BUILD INDIVIDUAL RESULT TABLE
# ============================================================

def build_algorithm_detail_table(
    algorithm,
    record,
    available_width
):
    rows = [
        ["Metric", "Value"],
        [
            "Customers Served",
            format_number(
                record.get(
                    "customers_served",
                    0
                )
            )
        ],
        [
            "Successful Allocations",
            format_number(
                record.get(
                    "successful_allocations",
                    0
                )
            )
        ],
        [
            "Failed Allocations",
            format_number(
                record.get(
                    "failed_allocations",
                    0
                )
            )
        ],
        [
            "Invalid Allocations",
            format_number(
                record.get(
                    "invalid_allocations",
                    0
                )
            )
        ],
        [
            "Average Wait Time",
            f"{safe_float(record.get('average_wait_time', 0)):.2f} sec"
        ],
        [
            "Total Reward",
            f"{safe_float(record.get('total_reward', 0)):+.2f}"
        ],
        [
            "Average Reward",
            f"{safe_float(record.get('average_reward', 0)):+.2f}"
        ],
        [
            "Penalties",
            format_number(
                record.get(
                    "penalties",
                    0
                )
            )
        ],
        [
            "Waste Penalties",
            format_number(
                record.get(
                    "waste_penalties",
                    0
                )
            )
        ],
        [
            "Q-Value Updates",
            format_number(
                record.get(
                    "q_updates",
                    0
                )
            )
        ],
        [
            "Decisions",
            format_number(
                record.get(
                    "decisions",
                    0
                )
            )
        ],
        [
            "Policy",
            safe_text(
                record.get(
                    "policy"
                )
            )
        ],
        [
            "Learning",
            safe_text(
                record.get(
                    "learning_method"
                )
            )
        ],
        [
            "Tracking Duration",
            format_duration(
                record.get(
                    "duration_seconds",
                    0
                )
            )
        ],
    ]

    table = Table(
        rows,
        colWidths=[
            65 * mm,
            available_width - 65 * mm
        ]
    )

    apply_table_style(table)

    # Highlight the algorithm name above the table using a
    # separate paragraph rather than making a special row.
    return table


# ============================================================
# PERFORMANCE SUMMARY
# ============================================================

def build_performance_summary(
    report_data,
    styles,
    available_width
):
    comparison = report_data.get(
        "comparison",
        {}
    )

    algorithms = report_data.get(
        "algorithms_used",
        []
    )

    if len(algorithms) < 2:
        return [
            Paragraph(
                "A comparison requires at least two algorithms to be used during the simulation.",
                styles["BodySmall"]
            )
        ]

    winner = comparison.get(
        "winner"
    )

    winner_reason = comparison.get(
        "winner_reason",
        ""
    )

    story = []

    if winner:
        story.append(
            Paragraph(
                f"🏆 Best Overall Algorithm: {safe_text(winner)}",
                styles["Winner"]
            )
        )

        story.append(
            Paragraph(
                safe_text(
                    winner_reason,
                    "Best overall performance based on the recorded metrics."
                ),
                styles["BodySmall"]
            )
        )

    # Pairwise metric summary when exactly two algorithms are
    # available. For more algorithms, show the metric winners.
    if len(algorithms) == 2:

        a = algorithms[0]
        b = algorithms[1]

        results = report_data.get(
            "results",
            {}
        )

        ra = results.get(a, {})
        rb = results.get(b, {})

        summary_rows = [
            ["Metric", a, b, "Better"]
        ]

        metric_info = [
            (
                "Customers Served",
                "customers_served",
                True
            ),
            (
                "Average Wait Time",
                "average_wait_time",
                False
            ),
            (
                "Total Reward",
                "total_reward",
                True
            ),
            (
                "Penalties",
                "penalties",
                False
            ),
            (
                "Waste Penalties",
                "waste_penalties",
                False
            ),
        ]

        for label, key, higher_is_better in metric_info:

            va = safe_float(
                ra.get(key, 0)
            )

            vb = safe_float(
                rb.get(key, 0)
            )

            if va == vb:
                better = "Equal"

            elif (
                higher_is_better
                and
                va > vb
            ):
                better = a

            elif (
                higher_is_better
                and
                vb > va
            ):
                better = b

            elif (
                not higher_is_better
                and
                va < vb
            ):
                better = a

            else:
                better = b

            summary_rows.append([
                label,
                format_number(va),
                format_number(vb),
                better
            ])

        table = Table(
            summary_rows,
            colWidths=[
                52 * mm,
                35 * mm,
                35 * mm,
                available_width - 122 * mm
            ],
            repeatRows=1
        )

        apply_table_style(table)

        story.append(
            Spacer(1, 4)
        )

        story.append(table)

    else:

        metric_comparison = comparison.get(
            "metrics",
            {}
        )

        rows = [
            ["Metric", "Best Algorithm"]
        ]

        for key, info in metric_comparison.items():

            rows.append([
                safe_text(
                    info.get(
                        "label"
                    ),
                    key
                ),
                safe_text(
                    info.get(
                        "best"
                    )
                )
            ])

        table = Table(
            rows,
            colWidths=[
                85 * mm,
                available_width - 85 * mm
            ],
            repeatRows=1
        )

        apply_table_style(table)

        story.append(table)

    return story


# ============================================================
# MAIN PDF GENERATOR
# ============================================================

def generate_pdf_report(
    report_data,
    output_path=None
):
    """
    Generate the Metrius Eats RL evaluation PDF.

    Parameters
    ----------
    report_data:
        Dictionary returned by ResultTracker.get_report_data().

    output_path:
        Optional full output path.

    Returns
    -------
    str
        Absolute path to the generated PDF.
    """

    if not isinstance(
        report_data,
        dict
    ):
        raise TypeError(
            "report_data must be a dictionary."
        )

    # --------------------------------------------------------
    # Output path
    # --------------------------------------------------------

    os.makedirs(
        REPORTS_DIR,
        exist_ok=True
    )

    if output_path is None:

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        output_path = os.path.join(
            REPORTS_DIR,
            f"Metrius_Eats_RL_Report_{timestamp}.pdf"
        )

    output_path = os.path.abspath(
        output_path
    )

    output_directory = os.path.dirname(
        output_path
    )

    if output_directory:
        os.makedirs(
            output_directory,
            exist_ok=True
        )

    # --------------------------------------------------------
    # Document
    # --------------------------------------------------------

    page_width, page_height = A4

    margin_left = 18 * mm
    margin_right = 18 * mm
    margin_top = 22 * mm
    margin_bottom = 20 * mm

    available_width = (
        page_width
        -
        margin_left
        -
        margin_right
    )

    document = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=margin_right,
        leftMargin=margin_left,
        topMargin=margin_top,
        bottomMargin=margin_bottom,
        title="Metrius Eats - RL Algorithm Evaluation",
        author="Metrius Eats"
    )

    styles = build_styles()

    story = []

    # ========================================================
    # COVER / TITLE
    # ========================================================

    story.append(
        Spacer(
            1,
            12 * mm
        )
    )

    story.append(
        Paragraph(
            "METRIUS EATS",
            styles["ReportTitle"]
        )
    )

    story.append(
        Paragraph(
            "Reinforcement Learning Algorithm Evaluation Report",
            styles["ReportSubtitle"]
        )
    )

    simulation = report_data.get(
        "simulation",
        {}
    )

    generated_at = datetime.now().strftime(
        "%d %B %Y, %I:%M:%S %p"
    )

    title_info = Table(
        [
            [
                "Simulation Day",
                safe_text(
                    report_data.get(
                        "day",
                        1
                    )
                )
            ],
            [
                "Generated",
                generated_at
            ],
            [
                "Simulation Duration",
                format_duration(
                    simulation.get(
                        "duration_seconds",
                        0
                    )
                )
            ],
            [
                "Algorithms Used",
                format_number(
                    report_data.get(
                        "algorithm_count",
                        0
                    )
                )
            ],
        ],
        colWidths=[
            55 * mm,
            available_width - 55 * mm
        ]
    )

    apply_table_style(
        title_info,
        header=False
    )

    # Make the first column visually stronger.
    title_info.setStyle(
        TableStyle([
            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.HexColor("#F0F4F8")
            ),
        ])
    )

    story.append(
        title_info
    )

    story.append(
        Spacer(
            1,
            9 * mm
        )
    )

    # ========================================================
    # ALGORITHMS USED
    # ========================================================

    story.append(
        Paragraph(
            "1. Algorithms Used",
            styles["Section"]
        )
    )

    algorithms = report_data.get(
        "algorithms_used",
        []
    )

    if algorithms:

        algorithm_rows = [
            [
                "Algorithm",
                "Status"
            ]
        ]

        for algorithm in algorithms:

            record = report_data.get(
                "results",
                {}
            ).get(
                algorithm,
                {}
            )

            algorithm_rows.append([
                safe_text(
                    algorithm
                ),
                "Evaluated"
                if record.get(
                    "used",
                    True
                )
                else "Not Used"
            ])

        algorithm_table = Table(
            algorithm_rows,
            colWidths=[
                80 * mm,
                available_width - 80 * mm
            ],
            repeatRows=1
        )

        apply_table_style(
            algorithm_table
        )

        story.append(
            algorithm_table
        )

    else:

        story.append(
            Paragraph(
                "No algorithm results were recorded.",
                styles["BodySmall"]
            )
        )

    # ========================================================
    # COMPARISON
    # ========================================================

    story.append(
        Paragraph(
            "2. Algorithm Comparison",
            styles["Section"]
        )
    )

    comparison_table = build_comparison_table(
        report_data,
        available_width
    )

    if comparison_table is not None:

        story.append(
            comparison_table
        )

    else:

        story.append(
            Paragraph(
                "No comparison data is available.",
                styles["BodySmall"]
            )
        )

    story.append(
        Spacer(
            1,
            5 * mm
        )
    )

    # ========================================================
    # PERFORMANCE SUMMARY
    # ========================================================

    story.append(
        Paragraph(
            "3. Performance Summary",
            styles["Section"]
        )
    )

    story.extend(
        build_performance_summary(
            report_data,
            styles,
            available_width
        )
    )

    # ========================================================
    # INDIVIDUAL ALGORITHM RESULTS
    # ========================================================

    story.append(
        PageBreak()
    )

    story.append(
        Paragraph(
            "4. Individual Algorithm Results",
            styles["Section"]
        )
    )

    results = report_data.get(
        "results",
        {}
    )

    for index, algorithm in enumerate(
        algorithms
    ):

        record = results.get(
            algorithm,
            {}
        )

        block = []

        block.append(
            Paragraph(
                safe_text(
                    algorithm
                ),
                styles["Section"]
            )
        )

        detail_table = build_algorithm_detail_table(
            algorithm,
            record,
            available_width
        )

        block.append(
            detail_table
        )

        block.append(
            Spacer(
                1,
                7 * mm
            )
        )

        # Allocation quality
        quality_rows = [
            [
                "Allocation Quality",
                "Count"
            ],
            [
                "Exact Fit",
                format_number(
                    record.get(
                        "exact_fits",
                        0
                    )
                )
            ],
            [
                "1 Unused Seat",
                format_number(
                    record.get(
                        "one_unused",
                        0
                    )
                )
            ],
            [
                "2 Unused Seats",
                format_number(
                    record.get(
                        "two_unused",
                        0
                    )
                )
            ],
            [
                "3+ Unused Seats",
                format_number(
                    record.get(
                        "large_waste",
                        0
                    )
                )
            ],
        ]

        quality_table = Table(
            quality_rows,
            colWidths=[
                75 * mm,
                available_width - 75 * mm
            ],
            repeatRows=1
        )

        apply_table_style(
            quality_table
        )

        block.append(
            quality_table
        )

        if index < len(algorithms) - 1:

            block.append(
                Spacer(
                    1,
                    8 * mm
                )
            )

        story.append(
            KeepTogether(block)
        )

    # ========================================================
    # CONCLUSION
    # ========================================================

    story.append(
        Paragraph(
            "5. Conclusion",
            styles["Section"]
        )
    )

    comparison = report_data.get(
        "comparison",
        {}
    )

    winner = comparison.get(
        "winner"
    )

    if len(algorithms) >= 2 and winner:

        conclusion = (
            f"Based on the recorded simulation metrics, "
            f"<b>{safe_text(winner)}</b> achieved the strongest "
            f"overall performance. The evaluation considers "
            f"customer service, waiting time, cumulative reward, "
            f"and penalty-related outcomes."
        )

    elif len(algorithms) == 1:

        conclusion = (
            f"The simulation evaluated "
            f"<b>{safe_text(algorithms[0])}</b>. "
            f"A direct algorithm comparison requires at least "
            f"two algorithms to be used."
        )

    else:

        conclusion = (
            "No algorithm results were recorded for this "
            "simulation."
        )

    story.append(
        Paragraph(
            conclusion,
            styles["BodySmall"]
        )
    )

    story.append(
        Spacer(
            1,
            4 * mm
        )
    )

    story.append(
        Paragraph(
            "This report was generated automatically by the "
            "Metrius Eats simulation.",
            styles["SmallCenter"]
        )
    )

    # ========================================================
    # BUILD
    # ========================================================

    document.build(
        story,
        onFirstPage=draw_page,
        onLaterPages=draw_page
    )

    return output_path


# ============================================================
# ALIAS
# ============================================================

create_pdf_report = generate_pdf_report


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_data = {
        "title": "METRIUS EATS",
        "subtitle": "Reinforcement Learning Algorithm Evaluation",
        "day": 1,

        "simulation": {
            "duration_seconds": 342,
            "algorithm_switches": 1,
            "total_decisions": 93
        },

        "algorithms_used": [
            "Default",
            "Expected SARSA"
        ],

        "algorithm_count": 2,

        "results": {
            "Default": {
                "algorithm": "Default",
                "used": True,
                "customers_served": 42,
                "successful_allocations": 42,
                "failed_allocations": 0,
                "invalid_allocations": 0,
                "average_wait_time": 1.8,
                "total_reward": 320,
                "average_reward": 7.62,
                "penalties": 8,
                "waste_penalties": 5,
                "q_updates": 0,
                "decisions": 42,
                "exact_fits": 20,
                "one_unused": 12,
                "two_unused": 5,
                "large_waste": 5,
                "policy": "Rule-Based",
                "learning_method": "None",
                "duration_seconds": 170
            },

            "Expected SARSA": {
                "algorithm": "Expected SARSA",
                "used": True,
                "customers_served": 51,
                "successful_allocations": 51,
                "failed_allocations": 0,
                "invalid_allocations": 0,
                "average_wait_time": 1.2,
                "total_reward": 487,
                "average_reward": 9.55,
                "penalties": 3,
                "waste_penalties": 1,
                "q_updates": 184,
                "decisions": 51,
                "exact_fits": 31,
                "one_unused": 14,
                "two_unused": 5,
                "large_waste": 1,
                "policy": "Epsilon Greedy",
                "learning_method": "Expected Q-value",
                "duration_seconds": 172
            }
        },

        "comparison": {
            "algorithms": [
                "Default",
                "Expected SARSA"
            ],
            "can_compare": True,
            "winner": "Expected SARSA",
            "winner_reason": (
                "Best overall performance across "
                "customers served, waiting time, reward, "
                "and penalty metrics."
            ),
            "metrics": {
                "customers_served": {
                    "label": "Customers Served",
                    "values": {
                        "Default": 42,
                        "Expected SARSA": 51
                    },
                    "best": "Expected SARSA",
                    "higher_is_better": True
                }
            }
        },

        "best_algorithm": "Expected SARSA"
    }

    path = generate_pdf_report(
        test_data,
        os.path.join(
            REPORTS_DIR,
            "Metrius_Eats_Test_Report.pdf"
        )
    )

    print()
    print(
        "========================================"
    )
    print(
        "PDF REPORT TEST SUCCESSFUL"
    )
    print(
        "========================================"
    )
    print(
        path
    )
    print()
