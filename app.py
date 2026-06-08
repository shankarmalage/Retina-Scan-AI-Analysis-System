from pprint import pp
from urllib import response

import tensorflow as tf
from flask import *
from flask_mail import Mail, Message
import os

from flask import Flask, render_template, request, send_file, url_for, redirect, session
import mysql.connector
import os
import cv2
import numpy as np
from datetime import datetime
from werkzeug.utils import secure_filename
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
 
app = Flask(__name__)
app.secret_key = "retina_secret_key"
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'shankarmalage07@gmail.com'
app.config['MAIL_PASSWORD'] = 'oipgcucfmflojbpr'

mail = Mail(app)

# SAVE INTO STATIC FOLDER SO BROWSER CAN LOAD IMAGES
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Create folder if not exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ================= MYSQL CONNECTION =================

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="retina_db"
)

cursor = db.cursor()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# ================= LOAD AI MODEL =================

model = tf.saved_model.load("64x3-CNN.model")

infer = model.signatures["serving_default"]

# ================= PREDICT CLASS =================

def predict_class(path):

    img = cv2.imread(path)

    RGBImg = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    RGBImg = cv2.resize(RGBImg, (224, 224))

    image = np.array(RGBImg) / 255.0

    predict = infer(
        tf.constant([image], dtype=tf.float32)
    )

    probabilities = predict['dense_1'].numpy()[0].tolist()

    diagnosis = (
        "No Diabetic Retinopathy Detected"
        if np.argmax(probabilities) == 1
        else "Diabetic Retinopathy Detected"
    )

    return diagnosis, probabilities





from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, 
                                TableStyle, PageBreak, Image, Frame, PageTemplate)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime

def generate_pdf_report(patient_id, image_path, diagnosis, probabilities):
    """
    Generates a professional medical report PDF with enhanced formatting.
    """
    file_name = "Medical_Analysis_Report.pdf"
    doc = SimpleDocTemplate(
        file_name,
        pagesize=A4,
        leftMargin=50,
        rightMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()
    story = []

    # ==================== CUSTOM STYLES ====================
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#0b5e3a'),
        alignment=TA_CENTER,
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )

    hospital_style = ParagraphStyle(
        'HospitalStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER,
        spaceAfter=20
    )

    report_title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#0b5e3a'),
        alignment=TA_CENTER,
        spaceAfter=30,
        fontName='Helvetica-Bold',
        backColor=colors.HexColor('#f0f8f5'),
        borderWidth=2,
        borderColor=colors.HexColor('#0b5e3a'),
        borderPadding=10
    )

    section_heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor('#0b5e3a'),
        fontName='Helvetica-Bold',
        spaceAfter=12,
        spaceBefore=16,
        backColor=colors.HexColor('#e8f5e9'),
        borderPadding=6
    )

    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['BodyText'],
        fontSize=10,
        leading=16,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor('#333333')
    )

    diagnosis_style = ParagraphStyle(
        'DiagnosisStyle',
        parent=styles['Normal'],
        fontSize=12,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#d32f2f'),
        spaceAfter=10,
        alignment=TA_CENTER,
        backColor=colors.HexColor('#ffebee'),
        borderWidth=1,
        borderColor=colors.HexColor('#d32f2f'),
        borderPadding=10
    )

    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#888888'),
        alignment=TA_CENTER
    )

    # ==================== PAGE 1 ====================

    story.append(Paragraph("<b>Retinex Retinopathy Detection</b>", title_style))
    story.append(Paragraph("Ai Based Retinopathy Detection<br/>", hospital_style))

    story.append(Spacer(1, 10))
    line_table = Table([['']], colWidths=[500])
    line_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (0, 0), 2, colors.HexColor('#0b5e3a')),
    ]))
    story.append(line_table)
    story.append(Spacer(1, 20))

    story.append(Paragraph("DIABETIC RETINOPATHY SCREENING REPORT", report_title_style))

    analysis_date = datetime.now().strftime("%B %d, %Y at %H:%M")
    report_id = f"DR-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    info_data = [
        ['Report ID :', report_id],
        ['Analysis Date :', analysis_date],
        ['Scan Type :', 'Fundus Photography (Digital Retinal Imaging)'],
        ['Image Resolution :', '32×32 pixels (Processed)'],
        ['AI Model :', 'Convolutional Neural Network v2.3'],
        ['Processing Time :', '< 2 seconds']
    ]

    info_table = Table(info_data, colWidths=[150, 340])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc'))
    ]))

    story.append(info_table)
    story.append(Spacer(1, 25))

    story.append(Paragraph("CLINICAL ASSESSMENT", section_heading_style))
    story.append(Paragraph(
        "This automated screening analysis evaluates digital fundus photography for clinical "
        "indicators of diabetic retinopathy...",
        body_style
    ))
    story.append(Spacer(1, 20))

    # Diagnosis
    story.append(Paragraph("SCREENING RESULT", section_heading_style))
    story.append(Paragraph(diagnosis, diagnosis_style))
    story.append(Spacer(1, 20))

    # Probabilities
    story.append(Paragraph("PREDICTION CONFIDENCE LEVELS", section_heading_style))

    p_pos = round(probabilities[0] * 100, 2)

    if len(probabilities) > 1:
        p_neg = round(probabilities[1] * 100, 2)
    else:
        p_neg = round((1 - probabilities[0]) * 100, 2)
        

    prob_table = Table([
        ['Classification', 'Confidence (%)', 'Interpretation'],
        ['Diabetic Retinopathy Detected', f'{p_pos}%', 'Positive finding' if p_pos > 50 else 'Low probability'],
        ['No Diabetic Retinopathy', f'{p_neg}%', 'Negative finding' if p_neg > 50 else 'Low probability']
    ], colWidths=[200, 140, 150])

    prob_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0b5e3a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#0b5e3a'))
    ]))

    story.append(prob_table)
    story.append(Spacer(1, 25))

    # ==================== PAGE 2 ====================
    story.append(PageBreak())

    # -----------------------------------------
    # IMPROVED CONDITION FOR SHOWING LIFESTYLE + DIET
    # Check if diabetic retinopathy is detected (positive case)
    # -----------------------------------------
    diagnosis_lower = diagnosis.lower().strip()
    # Show recommendations only if DR is detected (when it's NOT "no diabetic retinopathy")
    show_recommendations = "no diabetic retinopathy" not in diagnosis_lower

    # ==================== LIFESTYLE (ONLY IF POSITIVE) ====================
    if show_recommendations:
        story.append(Paragraph("LIFESTYLE RECOMMENDATIONS", section_heading_style))

        lifestyle_recommendations = [
            ['<b>Blood Glucose Control</b>', 'Maintain HbA1c below 7%.'],
            ['<b>Blood Pressure</b>', 'Target < 130/80 mmHg.'],
            ['<b>Exercise</b>', '150 minutes of activity weekly.'],
            ['<b>Smoking</b>', 'Quit immediately.'],
            ['<b>Weight</b>', 'Maintain healthy BMI.'],
            ['<b>Stress</b>', 'Practice relaxation and sleep well.']
        ]

        for item in lifestyle_recommendations:
            lifestyle_table = Table([[Paragraph(item[0], body_style), Paragraph(item[1], body_style)]],
                                    colWidths=[140, 350])
            lifestyle_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#e8f5e9')),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc'))
            ]))
            story.append(lifestyle_table)
            story.append(Spacer(1, 8))

        story.append(Spacer(1, 15))

    # ==================== DIET (ONLY IF POSITIVE) ====================
    if show_recommendations:
        story.append(Paragraph("DIETARY RECOMMENDATIONS", section_heading_style))

        diet_intro = Paragraph(
            "A retinal-protective diet rich in antioxidants and omega-3 helps prevent progression:",
            body_style
        )
        story.append(diet_intro)
        story.append(Spacer(1, 12))

        diet_table = Table([
            ['Food Category', 'Recommended Foods', 'Foods to Limit'],
            ['Vegetables', 'Spinach, broccoli', 'Fried vegetables'],
            ['Fruits', 'Berries, apples', 'Fruit juices'],
            ['Proteins', 'Fish, legumes', 'Processed meats'],
            ['Grains', 'Whole grains', 'White bread'],
            ['Fats', 'Olive oil, nuts', 'Trans fats'],
            ['Beverages', 'Water, green tea', 'Sugary drinks']
        ], colWidths=[90, 200, 200])

        diet_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0b5e3a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#0b5e3a'))
        ]))

        story.append(diet_table)
        story.append(Spacer(1, 20))

    # ==================== SCREENING (ALWAYS SHOW) ====================
    story.append(Paragraph("FOLLOW-UP SCREENING SCHEDULE", section_heading_style))

    screening_text = Paragraph(
        "• <b>No DR detected:</b> Annual eye exam<br/>"
        "• <b>Mild DR:</b> Every 6–12 months<br/>"
        "• <b>Moderate–Severe:</b> Every 3–6 months<br/>"
        "• <b>Any vision change:</b> Immediate consultation",
        body_style
    )
    story.append(screening_text)
    story.append(Spacer(1, 20))

    # ==================== IMAGE ====================
    story.append(Paragraph("ANALYZED FUNDUS IMAGE", section_heading_style))
    story.append(Spacer(1, 15))

    try:
        img = Image(image_path)
        img.drawWidth = 3.5 * inch
        img.drawHeight = 3.5 * inch
        img_table = Table([[img]], colWidths=[5 * inch])
        img_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('BOX', (0, 0), (0, 0), 2, colors.HexColor('#0b5e3a'))
        ]))
        story.append(img_table)
    except:
        story.append(Paragraph("<i>Image load failed.</i>", body_style))

    story.append(Spacer(1, 15))

    # ==================== FOOTER ====================
    footer_line = Table([['']], colWidths=[490])
    footer_line.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (0, 0), 1, colors.HexColor('#cccccc'))
    ]))
    story.append(footer_line)
    story.append(Paragraph(
        f"<b>Retinex Retinopathy Detection</b> | Report generated on {analysis_date}",
        footer_style
    ))

    # ==================== PAGE 3 DISCLAIMER ====================
    story.append(PageBreak())
    story.append(Paragraph("IMPORTANT MEDICAL DISCLAIMER", section_heading_style))

    disclaimer_table = Table([[Paragraph(
        "<b>THIS IS AN AI-ASSISTED SCREENING TOOL ONLY</b><br/><br/>"
        "Not a substitute for medical diagnosis. Seek professional evaluation.",
        body_style
    )]], colWidths=[490])

    disclaimer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#fff3cd')),
        ('BOX', (0, 0), (0, 0), 2, colors.HexColor('#d32f2f')),
        ('TOPPADDING', (0, 0), (0, 0), 15),
        ('BOTTOMPADDING', (0, 0), (0, 0), 15),
        ('LEFTPADDING', (0, 0), (0, 0), 15)
    ]))

    story.append(disclaimer_table)
    story.append(Spacer(1, 20))

    doc.build(story)

    cursor.execute("""
    INSERT INTO reports
    (patient_id, diagnosis, report_name)
    VALUES (%s, %s, %s)
    """,
    (
        patient_id,
        diagnosis,
        file_name
    ))

    db.commit()

    return file_name

# ================= SIGNUP =================

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Save user
        query = """
        INSERT INTO users(username, email, password)
        VALUES(%s, %s, %s)
        """

        cursor.execute(query, (username, email, password))
        db.commit()

        # Get newly created user ID
        patient_id = cursor.lastrowid

        # Create appointment automatically
        appointment_query = """
        INSERT INTO appointments
        (patient_id, doctor_name, appointment_date, status)
        VALUES(%s, %s, CURDATE(), %s)
        """

        cursor.execute(
            appointment_query,
            (patient_id, 'Not Assigned', 'Pending')
        )

        db.commit()

        return redirect('/login')

    return render_template('signup.html')
# ================= HOME =================

@app.route('/')
def home():
    return redirect('/login')


# ================= PATIENT DASHBOARD =================
@app.route('/patientDashboard')
def patient_dashboard():

    if 'user' not in session:
        return redirect('/login')

    patient_id = session['user_id']
    username = session['user']

    # Appointment Count
    cursor.execute(
        "SELECT COUNT(*) FROM appointments1 WHERE patient_id=%s",
        (patient_id,)
    )
    appointment_count = cursor.fetchone()[0]

    # Appointment List
    cursor.execute("""
    SELECT doctor_name,
           appointment_date,
           appointment_time,
           status
    FROM appointments1
    WHERE patient_id=%s
    """, (patient_id,))

    appointments = cursor.fetchall()

    # Get latest health score
    cursor.execute("""
    SELECT health_score
    FROM ai_history
    WHERE patient_id=%s
    ORDER BY id DESC
    LIMIT 1
    """, (patient_id,))

    result = cursor.fetchone()

    # ADD THIS PART HERE
    if result:
        health_score = result[0]
    else:
        health_score = 0
        ai_status = "No Scan"

    print("Dashboard Health Score:", health_score)

    return render_template(
    'patientDashboard.html',
    appointment_count=appointment_count,
    appointments=appointments,
    username=username,
    health_score=health_score,

)
# ================= TEST ROUTE =================

@app.route('/test')
def test():
    return "Route Working"


# ================= LOGIN =================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        query = "SELECT * FROM users WHERE email=%s"
        cursor.execute(query, (email,))

        user = cursor.fetchone()

        if user and user[3] == password:

             session['user'] = user[2]
              # username
             session['user_id'] = user[0]   # id from users table

             return redirect('/dashboard')

        else:

            return render_template(
                'login.html',
                message="Invalid Email or Password"
            )

    return render_template('login.html')

# ================= DASHBOARD =================
@app.route('/dashboard')
def dashboard():
    return render_template('index.html')
@app.route('/doctor_dashboard')
def doctor_dashboard():

    if 'doctor' not in session:
        return redirect('/doctor_login')

    # Total Scans
    cursor.execute("SELECT COUNT(*) FROM scan_history")
    total_scans = cursor.fetchone()[0]

    # DR Cases
    cursor.execute("""
    SELECT COUNT(*)
    FROM scan_history
    WHERE diagnosis = 'Diabetic Retinopathy Detected'
    """)
    dr_cases = cursor.fetchone()[0]

    # Normal Cases
    cursor.execute("""
    SELECT COUNT(*)
    FROM scan_history
    WHERE diagnosis = 'No Diabetic Retinopathy Detected'
    """)
    normal_cases = cursor.fetchone()[0]

    # Reports
    cursor.execute("SELECT COUNT(*) FROM reports")
    reports = cursor.fetchone()[0]

    # Recent Appointments
    cursor.execute("""
    SELECT patient_id, appointment_date, status
    FROM appointments1
    ORDER BY created_at DESC
    LIMIT 5
    """)
    appointments = cursor.fetchall()

    return render_template(
        'doctorDashboard.html',
        total_scans=total_scans,
        dr_cases=dr_cases,
        normal_cases=normal_cases,
        reports=reports,
        appointments=appointments
    )
# ================= PREDICT =================

@app.route('/predict', methods=['POST'])
def upload_file():

    if 'user' not in session:
        return redirect('/login')

    if 'file' not in request.files:
        return render_template(
            'index.html',
            message='Please upload retina image'
        )

    file = request.files['file']

    if file.filename == '':
        return render_template(
            'index.html',
            message='Please select retina image'
        )

    if file and allowed_file(file.filename):

        filename = secure_filename(file.filename)

        save_path = os.path.join(
            app.config['UPLOAD_FOLDER'],
            filename
        )

        file.save(save_path)

        if not is_retina_image(save_path):

            os.remove(save_path)

            return render_template(
                'index.html',
                message='Please upload a valid retina scan image only'
            )

        diagnosis, probabilities = predict_class(save_path)

        confidence = round(max(probabilities) * 100, 2)
    if diagnosis == "No_DR":
        ai_status = "Normal"
        health_score = 95
    elif diagnosis == "Mild":
        health_score = 80
    elif diagnosis == "Moderate":
        health_score = 65
    elif diagnosis == "Severe":
        health_score = 45
    else:
        ai_status = "Abnormal"
        health_score = 25
        print("Diagnosis:", diagnosis)
        print("Health Score:", health_score)
    

        print("Saving to database:", filename, diagnosis, confidence)

        patient_id = session['user_id']

        query = """
        INSERT INTO scan_history
        (image_name, diagnosis, confidence, patient_id)
        VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
    query,
    (filename, diagnosis, confidence, patient_id)
  )

        db.commit()


        # Save AI History
        cursor.execute("""
        INSERT INTO ai_history
        (patient_id, image_name, diagnosis, confidence, health_score)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
                patient_id,
                filename,
                diagnosis,
                confidence,
                health_score
            ))

        db.commit()

        timestamp = datetime.now().strftime(
            "%d-%m-%Y %H:%M"
        )

        pdf_file = generate_pdf_report(
                patient_id,
                save_path,
                diagnosis,
                probabilities
            )
        patient_email = session['user']

        msg = Message(
    'Retina Scan Report',
    sender=app.config['MAIL_USERNAME'],
    recipients=[patient_email]
    )

    msg.body = "Your retina scan report is attached."

    with app.open_resource(pdf_file) as fp:
     msg.attach(
        "Retina_Report.pdf",
        "application/pdf",
        fp.read()
    )
    print("Sending email to:", patient_email)
    mail.send(msg)
    
        
    return render_template(
            'predict.html',
            diagnosis=diagnosis,
            probabilities=probabilities,
            user_image=filename,
            timestamp=timestamp,
            pdf_report=pdf_file
        )

    return render_template(
        'index.html',
        message='Only JPG, PNG, JPEG images allowed'
    )
#=============================================
@app.route('/download_report/<int:scan_id>')
def download_report_record(scan_id):

    cursor.execute(
        "SELECT * FROM scan_history WHERE id=%s",
        (scan_id,)
    )

    record = cursor.fetchone()

    if not record:
        return "Record not found"

    image_name = record[1]
    diagnosis = record[2]

    image_path = os.path.join(
        "static",
        "uploads",
        image_name
    )

    probabilities = [0.95]
  
    pdf_file = generate_pdf_report(
        session['user_id'],
        image_path,
        diagnosis,
        probabilities
    )
    response = send_file(
    pdf_file,
    as_attachment=True
)

    response.headers["Cache-Control"] = "no-cache"
    return response

#==============================================
@app.route('/download_report', methods=['POST'])
def download_report():

    image_filename = request.form['image_path']
    diagnosis = request.form['diagnosis']
    probs = request.form.getlist('probabilities')

    probabilities = list(map(float, probs))

    image_path = os.path.join(
        "static",
        "uploads",
        image_filename
    )

    pdf_file = generate_pdf_report(
        session['user_id'],
        image_path,
        diagnosis,
        probabilities
    )

    return send_file(pdf_file, as_attachment=True)
#================================================
def is_retina_image(path):

    img = cv2.imread(path)

    if img is None:
        return False

    img = cv2.resize(img, (300, 300))

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_red = np.array([0, 20, 20])
    upper_red = np.array([30, 255, 255])

    mask = cv2.inRange(hsv, lower_red, upper_red)

    red_pixels = cv2.countNonZero(mask)

    total_pixels = img.shape[0] * img.shape[1]

    red_ratio = red_pixels / total_pixels

    print("Red Ratio =", red_ratio)

    if red_ratio < 0.08:
        return False

    return True
#==========================================

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/dashboard')
#===============View Records===============
@app.route('/viewRecords')
def view_records():

    if 'user_id' not in session:
        return redirect('/login')

    new_cursor = db.cursor()

    new_cursor.execute(
        "SELECT * FROM scan_history ORDER BY id DESC"
    )

    records = new_cursor.fetchall()

    return render_template(
        'viewRecords.html',
        records=records
    )
#=========================================
@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():

    if request.method == 'POST':

        doctor = request.form['doctor']
        date = request.form['date']
        time = request.form['time']

        patient_id = session['user_id']

        cursor.execute("""
            INSERT INTO appointments1
            (patient_id, doctor_name, appointment_date, appointment_time)
            VALUES (%s,%s,%s,%s)
        """, (patient_id, doctor, date, time))

        # Change this after checking your DB connection name
        db.commit()

        return redirect('/patientDashboard')

    return render_template('book_appointment.html')
#=========================================
@app.route('/appointments')
def appointments():

    patient_id = session['user_id']

    cursor.execute("""
        SELECT id,
            doctor_name,
            appointment_date,
            appointment_time,
            status
        FROM appointments1
        WHERE patient_id=%s
        AND status != 'Cancelled'
""", (patient_id,))

    data = cursor.fetchall()

    return render_template(
        'appointments.html',
        appointments=data
    )

#=========================================
@app.route('/cancel_appointment/<int:id>')
def cancel_appointment(id):

    cursor.execute("""
        UPDATE appointments1
        SET status='Cancelled'
        WHERE id=%s
    """, (id,))

    db.commit()

    return redirect('/appointments')
#=========================================
@app.route('/confirm_appointment/<int:id>')
def approve_appointment(id):

    cursor.execute("""
        UPDATE appointments1
        SET status='Confirmed'
        WHERE id=%s
    """, (id,))

    db.commit()

    return redirect('/appointments')
#=========================================
@app.route('/confirm_appointment/<int:id>')
def confirm_appointment(id):

    cursor.execute("""
        UPDATE appointments1
        SET status='Confirmed'
        WHERE id=%s
    """, (id,))

    db.commit()

    return redirect('/appointments')
#=========================================
@app.route('/contact_doctor')
def contact_doctor():
    return render_template('contact_doctor.html')


#=========================
@app.route('/contact_doctor', methods=['GET', 'POST'])
def contact_doctor_page():

    if request.method == 'POST':

        message = request.form['message']
        patient_id = session['user_id']

        # Save in database
        cursor.execute("""
        INSERT INTO doctor_messages(patient_id, message)
        VALUES(%s,%s)
        """, (patient_id, message))

        db.commit()

        # Send email to doctor
        msg = Message(
            'Patient Message',
            sender=app.config['MAIL_USERNAME'],
            recipients=['shankarmalage07@gmail.com']
        )

        msg.body = f"""
Patient ID: {patient_id}

Message:
{message}

Sent from Retina Detection System.
"""

        mail.send(msg)

        return render_template("message_sent.html")
    return render_template('contact_doctor.html')
#=========================================

@app.route('/prescriptions')
def prescriptions():

    patient_id = session['user_id']

    cursor.execute("""
    SELECT doctor_name,
           medicine,
           dosage,
           instructions
    FROM prescriptions
    WHERE patient_id=%s
    """,(patient_id,))

    data = cursor.fetchall()

    return render_template(
        'prescriptions.html',
        prescriptions=data
    )
#=========================================
@app.route('/send_emergency', methods=['POST'])
def send_emergency():

    patient_name = session['user']

    msg = Message(
        'Emergency Alert',
        sender=app.config['MAIL_USERNAME'],
        recipients=['doctor@gmail.com']
    )

    msg.body = f"""
Emergency Alert!

Patient Name: {patient_name}

The patient has requested immediate medical assistance.
Please contact the patient as soon as possible.
"""

    mail.send(msg)

    return """
    <script>
    alert('Emergency Alert Sent Successfully!');
    window.location='/patientDashboard';
    </script>
    """
#=========================================
@app.route('/doctor_register', methods=['GET', 'POST'])
def doctor_register():

    if request.method == 'POST':

        doctor_name = request.form['doctor_name']
        email = request.form['email']
        password = request.form['password']

        cursor.execute("""
        INSERT INTO doctors
        (doctor_name, email, password)
        VALUES (%s, %s, %s)
        """, (doctor_name, email, password))

        db.commit()

        return redirect('/doctor_login')

    return render_template('doctorRegister.html')

#=========================================
@app.route('/doctor_login', methods=['GET', 'POST'])
def doctor_login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        cursor.execute(
            """
            SELECT * FROM doctors
            WHERE email=%s AND password=%s
            """,
            (username, password)
        )

        doctor = cursor.fetchone()

        if doctor:

            session['doctor'] = doctor[1]

            return redirect('/doctor_dashboard')

        return render_template(
            'doctorLogin.html',
            message='Invalid Login'
        )

    return render_template('doctorLogin.html')

#===========================================    
@app.route('/doctor_logout')
def doctor_logout():

    session.pop('doctor', None)

    return redirect('/doctor_login')
#===========================================
@app.route('/upload_scan')
def upload_scan():
    return render_template('upload.html')

@app.route('/run_ai_detection')
def run_ai_detection():
    return render_template('run_ai_detection.html')

@app.route('/generate_report')
def generate_report():
    return render_template('generate_report.html')


@app.route('/analysis_history')
def analysis_history():

    cursor.execute("""
    SELECT *
    FROM scan_history
    ORDER BY id DESC
    """)

    history = cursor.fetchall()

    return render_template(
        'analysis_history.html',
        history=history
    )
#================Follow Up Reminder===================
from datetime import timedelta

@app.route('/followup_reminder')
def followup_reminder():

    patient_id = session.get('user_id')

    cursor.execute("""
        SELECT scan_date, diagnosis
        FROM scan_history
        WHERE patient_id=%s
        ORDER BY scan_date DESC
        LIMIT 1
    """, (patient_id,))

    scan = cursor.fetchone()

    if scan:

        scan_date = scan[0]
        diagnosis = scan[1]

        next_visit = scan_date + timedelta(days=90)

        return render_template(
            'followup_reminder.html',
            scan_date=scan_date,
            diagnosis=diagnosis,
            next_visit=next_visit
        )

    return render_template(
        'followup_reminder.html',
        scan_date=None
    )
#============Follo-up the remender=======
@app.route('/send_reminder_email')
def send_reminder_email():

    

    patient_id = session.get('user_id')

    cursor.execute("""
        SELECT username, email
        FROM users
        WHERE id=%s
    """, (patient_id,))

    patient = cursor.fetchone()

    if not patient:
        return "Patient not found"

    patient_name = patient[0]
    patient_email = patient[1]

    msg = Message(
        "Retina Follow-up Reminder",
        sender=app.config['MAIL_USERNAME'],
        recipients=[patient_email]
    )

    msg.body = f"""
        Hello {patient_name},

        This is a reminder for your retina follow-up eye examination.

        Please schedule your next retina checkup with your doctor.

Regular monitoring helps detect diabetic retinopathy early.

Thank You,
Diabetic Retinopathy Detection System
"""

    mail.send(msg)

    return render_template('email_sent.html')
#===========================================
@app.route('/prescriptions')
def prescriptions1():
    return render_template('prescriptions.html')

@app.route('/save_prescription', methods=['POST'])
def save_prescription():

    patient_id = request.form['patient_id']
    medicine = request.form['medicine']
    dosage = request.form['dosage']
    instructions = request.form['instructions']

    cursor.execute("""
        INSERT INTO prescriptions1
        (patient_id, medicine, dosage, instructions)
        VALUES (%s,%s,%s,%s)
    """, (
        patient_id,
        medicine,
        dosage,
        instructions
    ))

    db.commit()

    return render_template("prescription_saved.html")
#===============Diabetes Diet Recommendation============
@app.route('/diet_recommendation')
def diet_recommendation():
    return render_template('diet_recommendation.html')

if __name__ == '__main__':
    app.run(debug=True)
