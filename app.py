import streamlit as st
import cv2
import pandas as pd
import numpy as np
from PIL import Image
import json

# Custom CSS for mobile-friendly live scanning
st.markdown(
    """
    <style>
    .stApp {
        background-color: #212121;
        color: white;
    }
    .title {
        font-size: 18px;
        text-align: center;
        margin: 5px 0;
    }
    .instruction {
        font-size: 12px;
        text-align: center;
        font-family: 'cursive';
        color: #bbdefb;
    }
    .capture-box {
        text-align: center;
        margin: 5px 0;
    }
    .details-box {
        text-align: center;
        margin: 5px 0;
        padding: 6px;
        border-radius: 6px;
    }
    .login-box {
        text-align: center;
        margin: 5px 0;
    }
    .stButton>button {
        width: 100%;
        max-width: 180px;
        font-size: 14px;
        padding: 8px;
        margin: 5px auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Coordinator credentials
VALID_CREDENTIALS = {
    "DATTU": "FAIRWELL2K25",
    "BHANU": "PARTY2025",
    "RAHUL": "EVENT2025",
    "YUDENDAR": "WELCOME2025",
    "NARENDRA": "CELEBRATE2025",
    "SAITEJA": "WELCOME2025",
    "IMROSE": "PARTY2025",
    "SAIGANESH": "EVENT2025",
}

# Login function
def check_credentials():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        username = st.text_input("Username", key="username_input")
        password = st.text_input("Password", type="password", key="password_input")
        if st.button("Login"):
            if username in VALID_CREDENTIALS and VALID_CREDENTIALS[username] == password:
                st.session_state.authenticated = True
                st.success(f"Login successful! Welcome, {username}!")
            else:
                st.error("❌ Invalid username or password. Please try again.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()
    return st.session_state.authenticated

# Load student data
if check_credentials():
    try:
        student_df = pd.read_csv("students.csv")
        student_df["Roll Number"] = student_df["Roll Number"].astype(str)
        column_mapping = {
            "Roll Number": next((col for col in student_df.columns if "roll" in col.lower()), "Roll Number"),
            "Student Name": next((col for col in student_df.columns if "name" in col.lower()), "Student Name"),
            "Department": next((col for col in student_df.columns if "dept" in col.lower()), "Department")
        }
        if "Scanned" not in student_df.columns:
            student_df["Scanned"] = False
    except FileNotFoundError:
        st.error("❌ Error: 'students.csv' not found. Please upload the student data file.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error loading CSV: {str(e)}. Please check the file format.")
        st.stop()

    # UI Setup
    st.markdown('<div class="title">🎉 2k25 Farewell Party Event</div>', unsafe_allow_html=True)
    st.markdown('<div class="instruction">Tap to scan your QR code with camera</div>', unsafe_allow_html=True)

    # Placeholder for student details
    details_box = st.empty()

    # Function to decode QR code
    def decode_qr(image):
        img = np.array(image.convert('RGB'))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(img)
        return data if data else None

    # Function to extract roll number
    def extract_roll_number(qr_data):
        try:
            data_dict = json.loads(qr_data)
            return data_dict.get("roll_no")
        except json.JSONDecodeError:
            return None

    # Camera input
    image = st.camera_input("Tap to scan QR code", key="camera_input")

    if image is not None:
        qr_data = decode_qr(Image.open(image))
        if qr_data:
            roll_number = extract_roll_number(qr_data)
            if roll_number:
                print(f"Debug: Checking roll number: {roll_number}")  # Debug print
                student = student_df[student_df[column_mapping["Roll Number"]] == roll_number]
                if not student.empty:
                    if not student["Scanned"].iloc[0]:
                        roll = student[column_mapping["Roll Number"]].iloc[0]
                        name = student[column_mapping["Student Name"]].iloc[0]
                        dept = student[column_mapping["Department"]].iloc[0]
                        details_box.markdown(
                            '<div class="details-box" style="background-color: #424242; color: white;">'
                            f'✅ GIVE THE FOOD\n\n**Roll Number**: {roll}<br>**Name**: {name}<br>**Department**: {dept}'
                            '</div>',
                            unsafe_allow_html=True
                        )
                        student_df.loc[student_df[column_mapping["Roll Number"]] == roll_number, "Scanned"] = True
                        student_df.to_csv("students.csv", index=False)
                    else:
                        details_box.markdown(
                            '<div class="details-box" style="background-color: #d32f2f; color: white;">'
                            f'❌ Already Taken: {roll_number}'
                            '</div>',
                            unsafe_allow_html=True
                        )
                else:
                    details_box.markdown(
                        '<div class="details-box" style="background-color: #d32f2f; color: white;">'
                        f'❌ Invalid QR Code: {roll_number} not found in CSV'
                        '</div>',
                        unsafe_allow_html=True
                    )
            else:
                details_box.markdown(
                    '<div class="details-box" style="background-color: #d32f2f; color: white;">'
                    f'❌ Invalid QR format: {qr_data}'
                    '</div>',
                    unsafe_allow_html=True
                )
        else:
            details_box.markdown(
                '<div class="details-box" style="background-color: #d32f2f; color: white;">'
                '❌ No QR code detected. Try again or adjust camera angle!'
                '</div>',
                unsafe_allow_html=True
            )

    # Instructions
    st.markdown("---")
    st.write("🎊 **How to Enter**: Tap 'Tap to scan QR code', allow camera access, and point at your QR code. Adjust lighting or angle if needed. Check your details!")