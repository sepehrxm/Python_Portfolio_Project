import subprocess
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from scripts.email_sender import send_email
import schedule
import time

# Generate PDF report and schedule automatic email delivery every Wednesday at 15:00

IMG_DIR = "analysis_charts"
DATA_DIR = "./data"
REPORT_PATH = os.path.join(DATA_DIR, "Crypto_Weekly_Report.pdf")

def run_pipeline():
    print("Running pipeline")
    
    subprocess.run(["python", "scripts/crypto_data.py"], check=True)
    subprocess.run(["python", "scripts/google_trends_data.py"], check=True)
    
    subprocess.run(["python", "scripts/analysis.py"], check=True)
    
    print("Ready to report")


def create_pdf_report():
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(REPORT_PATH, pagesize=A4)
    story = []

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontSize=22,
        leading=26,
        alignment=1, 
        spaceAfter=38
    )

    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Normal"],
        fontSize=11,
        textColor="#555555",
        leftIndent=0,
        spaceAfter=14
    )

    author_style = ParagraphStyle(
        "AuthorStyle",
        parent=styles["Normal"],
        fontSize=10,
        textColor="#333333",
        leftIndent=0,
        spaceAfter=56
    )

    overview_style = ParagraphStyle(
        "OverviewStyle",
        parent=styles["Normal"],
        fontSize=11,
        leading=16,
        spaceAfter=72
    )

    chart_title_style = ParagraphStyle(
        "ChartTitle",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        alignment=1,
        spaceAfter=12
    )

    # Header
    title = Paragraph("<b>Crypto Weekly Report</b><br/><b>(Portfolio Project)</b>", title_style)
    date_text = Paragraph(datetime.now().strftime("%B %d, %Y"), subtitle_style)
    author = Paragraph("Author: Sepehr Mobayen<br/>Contact: Sepehrxm@gmail.com", author_style)

    overview_text = Paragraph(
        "Developed a fully automated weekly reporting pipeline using top five crypto coins. "
        "Using CoinGecko api for coins data and PyTrends for Google trends information related to them. "
        "This project streamlines weekly KPI reports, generates visual insights, "
        "and delivers a structured PDF report directly via email.",
        overview_style
    )

    # Pdf structure
    story.append(title)
    story.append(date_text)
    story.append(author)
    story.append(overview_text)
    story.append(Spacer(1, 10))

    #visuals
    story.append(Paragraph("<b>KPI Summary Table</b>", chart_title_style))
    story.append(Image("./analysis_charts/kpi_table.png", width=500, height=180,))
    story.append(Image("./analysis_charts/crypto_prices_subplots.png", width=450, height=600))
    story.append(Spacer(1, 10))

    charts = [
        "google_trends.png",
        "weekly_return.png",
        "volatility_strip.png",
        "correlation_price_trend.png"
    ]

    for chart in charts:
        path = os.path.join(IMG_DIR, chart)
        if os.path.exists(path):
            story.append(Image(path, width=480, height=300))
            story.append(Spacer(1, 12))

    doc.build(story)
    print("Pdf report generated")



PDF_PATH = "./data/crypto_weekly_report.pdf"
sender_email = "kpi.report.test@gmail.com"
sender_password = "axqn dzhy xgcd vzrn"
receiver_email = "sepehrxm@gmail.com"



def job():
    run_pipeline()
    create_pdf_report()
    send_email(pdf_path=REPORT_PATH, sender_email=sender_email, sender_password=sender_password, receiver_email=receiver_email)

job()


if __name__ == "__main__":
    schedule.every().wednesday.at("15:00").do(job)
    while True:
        schedule.run_pending()
        time.sleep(60)