import pandas as pd
import streamlit as st
from thefuzz import fuzz, process
import re
import io
from datetime import datetime
import os

# Set page configuration
st.set_page_config(layout="wide")

# Apply custom styling
st.markdown("""
<style>
/* Main page background pure black */
.stApp {
    background-color: #000000;
}
/* Sidebar background medium black */
[data-testid="stSidebar"] {
    background-color: #111111 !important;
}
/* Sidebar text bright white but now in normal font */
[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
    font-weight: normal;
}
/* Left-aligned Heading with smaller font and no border */
.custom-heading {
    font-size: 2rem;
    color: white;
    text-align: left;
    font-weight: bold;
    margin-bottom: 1.5rem;
    margin-left: 2rem;
    background: none;
    border: none;
    padding: 0;
}
/* Remove extra empty box inside file uploader */
[data-testid="stFileUploader"] > div {
    background-color: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
    border: none !important;
    min-height: 0 !important;
    min-width: 0 !important;
}
/* Label and input text white */
label, .stFileUploader, .stNumberInput label, .stSelectbox label {
    color: white !important;
}
/* White text for all content */
body, .stMarkdown, .stText, .stDataFrame, .stMetric {
    color: white !important;
}
/* Custom button styling */
.stButton>button {
    background-color: #000000;
    color: white;
    border-radius: 5px;
    padding: 0.5rem 1rem;
    font-weight: bold;
}
/* Status indicator */
.status-indicator {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-right: 5px;
}
.status-operational {
    background-color: #4CAF50;
}
</style>
""", unsafe_allow_html=True)

# --- Authentication System ---
def authenticate(username, password):
    """Check user credentials and return role"""
    credentials = {
        "admin": {"username": "yogaraj", "password": "afrin", "role": "ADMIN"},
        "user": {"username": "user", "password": "ssapresu", "role": "QA"},
        "bpo": {"username": "user", "password": "ssapopb", "role": "MAKER"}
    }
    
    for role, creds in credentials.items():
        if username == creds["username"] and password == creds["password"]:
            return role
    return None

def show_login():
    """Show login form and handle authentication"""
    with st.sidebar:
        st.title("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            role = authenticate(username, password)
            if role:
                st.session_state["authenticated"] = True
                st.session_state["role"] = role
                st.session_state["username"] = username
                st.rerun()
            else:
                st.error("Invalid username or password")

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["role"] = None
    st.session_state["username"] = None

# Show login if not authenticated
if not st.session_state["authenticated"]:
    show_login()
    st.stop()

# --- Role-Based Access Control ---
def get_menu_options(role):
    """Return menu options based on user role"""
    full_menu = ["App", "QC Radar", "All Trans MVR", "Truckings IFTA", "Riscom MVR", "MVR GPT"]
    
    if role == "admin":
        return full_menu
    elif role == "user":
        return full_menu  # User gets 99% access (all options)
    elif role == "bpo":
        return ["MVR GPT"]  # BPO only gets MVR GPT
    return []

# Sidebar menu with role-based options
menu_options = get_menu_options(st.session_state["role"])

with st.sidebar:
    st.markdown(f"### Welcome, {st.session_state['username']} ({st.session_state['role']})")
    st.markdown("---")
    st.markdown("### Menu")
    
    if menu_options:
        menu = st.radio("", menu_options, index=0, label_visibility="collapsed")
    else:
        st.warning("No menu options available for your role")
        menu = None
    
    st.markdown("---")
    if st.button("Logout"):
        st.session_state["authenticated"] = False
        st.session_state["role"] = None
        st.session_state["username"] = None
        st.rerun()
    
    st.markdown("Built with Yogaraj")

# --- EXACT CORE LOGIC FROM YOUR PROVIDED CODE ---
def normalize_name(name):
    """Enhanced name normalization with title removal and initials handling"""
    if pd.isna(name) or not name:
        return []
    name = str(name).lower()
    # Remove common prefixes/suffixes
    name = re.sub(r'\b(mr|mrs|ms|dr|jr|sr|iii|ii|iv)\b', '', name)
    # Remove non-alpha chars except spaces
    name = re.sub(r'[^a-z\s]', '', name)
    # Normalize spaces
    name = re.sub(r'\s+', ' ', name).strip()
    parts = name.split()
    if not parts:
        return []

    formats = []
    # Full name normal
    formats.append(' '.join(parts))
    # First last and last first formats
    if len(parts) > 1:
        formats.append(f"{parts[0]} {parts[-1]}")
        formats.append(f"{parts[-1]} {parts[0]}")
        formats.append(f"{parts[0]}{parts[-1]}")
        formats.append(f"{parts[-1]}{parts[0]}")

    # Initial-based formats if middle names exist
    if len(parts) > 2:
        first = parts[0]
        last = parts[-1]
        initials = ''.join([p[0] for p in parts[1:-1]])
        formats.append(f"{first} {initials} {last}")
        formats.append(f"{first} {initials}{last}")
        formats.append(f"{first}{initials} {last}")
        formats.append(f"{first}{initials}{last}")

    # Remove duplicates
    return list(set(formats))

def names_match(name1, name2):
    """Stricter matching with multiple fuzzy strategies"""
    if pd.isna(name1) or pd.isna(name2) or not name1 or not name2:
        return False
    formats1 = normalize_name(name1)
    formats2 = normalize_name(name2)
    for f1 in formats1:
        for f2 in formats2:
            if f1 == f2:
                return True
            if fuzz.token_set_ratio(f1, f2) >= 95:
                return True
            if fuzz.partial_ratio(f1, f2) >= 96:
                return True
            if fuzz.token_sort_ratio(f1, f2) >= 98:
                return True
    return False

def get_valid_column(df, purpose, default_names, required=True):
    """Find column with fuzzy matching, using defaults if possible"""
    # First try exact matches to default names
    for col in default_names:
        if col in df.columns:
            return col
    
    # Then try fuzzy matching
    for col_name in default_names:
        match, score = process.extractOne(col_name, df.columns, scorer=fuzz.ratio)
        if score > 80:
            return match
    
    # If not found and required, return first column
    if required and len(df.columns) > 0:
        return df.columns[0]
    
    return None
# --- END OF EXACT CORE LOGIC ---

# --- Main Application Logic ---
if menu == "All Trans MVR" and st.session_state["role"] in ["admin", "user"]:
    # Left-aligned heading in main page
    st.markdown('<div class="custom-heading">Alltrans Excel Creation</div>', unsafe_allow_html=True)
    
    # --- Driver Matching Tool ---
    def driver_matching_app():
        # File upload section
        st.header("Upload Files")
        col1, col2 = st.columns(2)
        
        with col1:
            driver_file = st.file_uploader("DRIVER LIST", type=["xlsx"])
        
        with col2:
            output_file = st.file_uploader("OUTPUT FILE", type=["xlsx"])
        
        if not driver_file or not output_file:
            st.info("Please upload both files to proceed")
            return
        
        # Configuration section
        st.header("Configuration...")
        
        # Default row skipping
        driver_skip = st.number_input("Rows to skip in DRIVER file", min_value=0, value=0)
        output_skip = 3  # Fixed as requested
        
        # Load data
        try:
            # Load output file to get sheet names
            xls = pd.ExcelFile(output_file)
            sheet_names = xls.sheet_names
            
            # Sheet selection with "All Trans" as default
            sheet = st.selectbox("Select sheet to process", sheet_names, 
                                index=sheet_names.index("All Trans") if "All Trans" in sheet_names else 0)
            
            # Read data
            drivers = pd.read_excel(driver_file, skiprows=driver_skip)
            output = pd.read_excel(output_file, sheet_name=sheet, skiprows=output_skip)
            
            # Column mapping section
            st.header("Column Mapping Running...")
            st.info("Map columns between files. The tool will try to auto-detect columns.")
            
            # Driver file columns
            st.subheader("Driver File Columns")
            driver_name_col = get_valid_column(drivers, "driver names", 
                                            ['name', 'driver name', 'full name'])
            hire_date_col = get_valid_column(drivers, "hire dates", 
                                        ['hire date', 'date of hire', 'doh'], False)
            dob_col = get_valid_column(drivers, "date of birth", 
                                    ['dob', 'date of birth', 'birth date'], False)
            license_col = get_valid_column(drivers, "license state", 
                                        ['license state', 'lic state', 'state'], False)
            
            # Display detected driver columns
            st.write(f"Detected Driver Name Column: `{driver_name_col}`")
            if hire_date_col:
                st.write(f"Detected Hire Date Column: `{hire_date_col}`")
            if dob_col:
                st.write(f"Detected Date of Birth Column: `{dob_col}`")
            if license_col:
                st.write(f"Detected License State Column: `{license_col}`")
            
            # Output file columns (with defaults)
            st.subheader("Output File Columns")
            output_name_col = get_valid_column(output, "driver names", 
                                            ['Name of Driver', 'Driver Name', 'Name'])
            output_dob_col = get_valid_column(output, "date of birth", 
                                            ['DOB', 'Date of Birth'], False) or "DOB"
            output_license_col = get_valid_column(output, "license state", 
                                                ['Lic State', 'License State', 'State'], False) or "Lic State"
            output_notes_col = get_valid_column(output, "notes", 
                                            ['Notes', 'Remarks', 'Comments']) or "Notes"
            output_hire_col = get_valid_column(output, "hire date", 
                                            ['DOH', 'Hire Date', 'Date of Hire'], False) or "DOH"
            
            # Display detected output columns
            st.write(f"Detected Driver Name Column: `{output_name_col}`")
            st.write(f"Detected DOB Column: `{output_dob_col}`")
            st.write(f"Detected License State Column: `{output_license_col}`")
            st.write(f"Detected Notes Column: `{output_notes_col}`")
            st.write(f"Detected Hire Date Column: `{output_hire_col}`")
            
            # Initialize output columns if needed
            for col in [output_dob_col, output_license_col, output_notes_col, output_hire_col]:
                if col not in output.columns:
                    output[col] = ""
            
            # Process button
            if st.button("Process File", use_container_width=True):
                with st.spinner("Matching names..."):
                    # Perform matching
                    match_count = 0
                    total_original = len(output)
                    
                    # Track matched driver indices
                    matched_driver_indices = set()
                    
                    # Progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for idx, row in output.iterrows():
                        output_name = row[output_name_col]
                        matched = False
                        
                        for driver_idx, driver_row in drivers.iterrows():
                            if driver_idx in matched_driver_indices:
                                continue
                                
                            if names_match(output_name, driver_row[driver_name_col]):
                                # Mark as matched
                                matched_driver_indices.add(driver_idx)
                                output.at[idx, output_notes_col] = "MATCH FOUND"
                                
                                # Transfer all available data
                                if hire_date_col:
                                    output.at[idx, output_hire_col] = driver_row[hire_date_col]
                                if dob_col:
                                    output.at[idx, output_dob_col] = driver_row[dob_col]
                                if license_col:
                                    output.at[idx, output_license_col] = driver_row[license_col]
                                
                                match_count += 1
                                matched = True
                                break
                        
                        # Update progress
                        progress = (idx + 1) / total_original
                        progress_bar.progress(progress)
                        status_text.text(f"Processed {idx + 1}/{total_original} records")
                    
                    # Add non-matched driver records at the end
                    new_rows = []
                    for driver_idx, driver_row in drivers.iterrows():
                        if driver_idx not in matched_driver_indices:
                            # Create new row with driver data
                            new_row = {col: "" for col in output.columns}
                            new_row[output_name_col] = driver_row[driver_name_col]
                            
                            # Add all available driver information
                            if hire_date_col:
                                new_row[output_hire_col] = driver_row[hire_date_col]
                            if dob_col:
                                new_row[output_dob_col] = driver_row[dob_col]
                            if license_col:
                                new_row[output_license_col] = driver_row[license_col]
                            
                            new_row[output_notes_col] = "MISSING MVR"
                            new_rows.append(new_row)
                    
                    # Append new rows to output
                    if new_rows:
                        new_rows_df = pd.DataFrame(new_rows)
                        output = pd.concat([output, new_rows_df], ignore_index=True)
                        added_count = len(new_rows)
                    else:
                        added_count = 0
                    
                    # Generate timestamped filename
                    timestamp = datetime.now().strftime("%m%d%Y")
                    result_filename = f"Driver_Matching_Result_{timestamp}.xlsx"
                    
                    # Save to BytesIO for download
                    output_bytes = io.BytesIO()
                    with pd.ExcelWriter(output_bytes, engine='openpyxl') as writer:
                        output.to_excel(writer, sheet_name=sheet, index=False)
                        # Preserve other sheets
                        for other_sheet in sheet_names:
                            if other_sheet != sheet:
                                pd.read_excel(output_file, sheet_name=other_sheet).to_excel(writer, sheet_name=other_sheet, index=False)
                    
                    output_bytes.seek(0)
                    
                    # Results Summary
                    total_final = len(output)
                    st.success("Matching complete!")
                    
                    # Show summary
                    st.subheader("📊 Results Summary")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Original Records", total_original)
                    col2.metric("Matched Records", match_count)
                    col3.metric("Added Records", added_count)
                    
                    # Show data transfer summary
                    st.write("**Data Transferred:**")
                    if hire_date_col:
                        st.write(f"- Hire Dates: {match_count + added_count}")
                    if dob_col:
                        st.write(f"- Birth Dates: {match_count + added_count}")
                    if license_col:
                        st.write(f"- License States: {match_count + added_count}")
                    
                    # Download button
                    st.download_button(
                        label="Download Excel",
                        data=output_bytes,
                        file_name=result_filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                    # Show preview
                    st.subheader("Preview of Processed Data")
                    st.dataframe(output.head(10))
        
        except Exception as e:
            st.error(f"⚠️ Error occurred: {str(e)}")
            st.exception(e)

    # Run the driver matching app
    driver_matching_app()

# Welcome screen for "App" menu
elif menu == "App":
    st.markdown('<div class="custom-heading">NLR Hub</div>', unsafe_allow_html=True)
    
    # Welcome section with profile picture and greeting
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # kung fu panda (Dragon Warrior)
        st.image("https://w0.peakpx.com/wallpaper/899/489/HD-wallpaper-po-impressed-hall-of-warriors-kung-fu-panda.jpg", 
                 width=200, 
                 caption="insights are coming")
    
    with col2:
        st.markdown("""
        <div style='border-left: 4px solid #4CAF50; padding-left: 1rem;'>
        <h2 style='color: #4CAF50;'>Welcome to InsightOps Hub!</h2>
        <p style='font-size: 1.1rem;'>
        Your central engine for processing documents, extracting insights, and generating requirement-driven outputs — all automated. Streamline MVR processing, 
        IFTA reporting, and driver record management with our powerful automation tools.
        </p>
        <p style='font-size: 1.1rem;'>
        <b>Today's Focus:</b> We've processed 142 MVRs this week with 98% accuracy
        </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Quick stats dashboard
    st.subheader("Performance Dashboard")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Drivers", "1,428", "+24 this week")
    col2.metric("Compliance Rate", "96.7%", "+1.2% from last month")
    col3.metric("Processing Time", "3.2 mins", "-45s average")
    
    # Recent activity feed
    st.subheader("📋 Recent Activity")
    activity_data = [
        {"action": "MVR Processed", "driver": "James Wilson", "time": "2 mins ago", "status": "Completed"},
        {"action": "IFTA Report", "description": "Q2 2024 Submission", "time": "1 hour ago", "status": "Pending Review"},
        {"action": "New Driver Added", "driver": "Sarah Johnson", "time": "3 hours ago", "status": "Verified"},
        {"action": "Compliance Alert", "description": "5 Licenses Expiring", "time": "Yesterday", "status": "Attention Needed"}
    ]
    
    for activity in activity_data:
        status_color = "#4CAF50" if "Completed" in activity["status"] else "#FF9800" if "Pending" in activity["status"] else "#F44336"
        st.markdown(f"""
        <div style='background-color: #222222; padding: 12px; border-radius: 8px; margin: 8px 0;'>
            <div style='display: flex; justify-content: space-between;'>
                <b>{activity['action']}</b>
                <span style='color: {status_color};'>{activity['status']}</span>
            </div>
            <div>{activity.get('driver', activity.get('description', ''))}</div>
            <div style='font-size: 0.8rem; color: #aaa;'>{activity['time']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    qcol1, qcol2, qcol3 = st.columns(3)
    qcol1.button("Process New MVRs")
    qcol2.button("Generate IFTA Report")
    qcol3.button("Add New Driver")
    
    # System status
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #aaa;'>
        System Status: <span style='color: #4CAF50;'>● Operational</span> | 
        Last Updated: 2024-06-08 14:30 EST
    </div>
    """, unsafe_allow_html=True)

# Qc doing for HDVI BRO
elif menu == "QC Radar" and st.session_state["role"] in ["admin", "user"]:
    import pandas as pd
    from datetime import date
    from io import BytesIO
    import streamlit as st

    st.markdown('<div class="custom-heading">QC Radar by HDVI</div>', unsafe_allow_html=True)
    st.write("Upload an MVR Excel file to validate using HDVI’s QC Radar engine.")

    def run_qc(df: pd.DataFrame):
        today = date.today()
        df.columns = [str(col).strip() for col in df.columns]
        df.replace(regex={r"(?i)^\s*$": pd.NA, r"(?i)^N/A$": pd.NA}, inplace=True)

        required_fields = [
            "First Name", "Last Name", "Date of Birth", "Age",
            "Years of Experience", "Hire Date", "Years of Tenure",
            "License State", "CDL Number", "CDL Type", "Expiration Date"
        ]
        allowed_cdl_types = {"A", "B", "C"}

        results = []
        tag_counts = {"valid": 0, "partial": 0, "fail": 0}
        total_deductions = 0

        for idx, row in df.iterrows():
            issues = []
            score = 100

            def deduct(points, reason):
                nonlocal score
                score -= points
                issues.append(reason)

            for field in required_fields:
                if pd.isna(row.get(field)) or str(row.get(field)).strip() == "":
                    deduct(10, f"{field} missing")

            try:
                dob = pd.to_datetime(row["Date of Birth"], errors="coerce").date()
                if dob >= today:
                    deduct(15, "DOB is in the future")
            except:
                dob = None

            try:
                age = int(row["Age"])
                if dob:
                    expected_age = (today - dob).days // 365
                    if abs(expected_age - age) > 1:
                        deduct(15, f"Age mismatch (expected ~{expected_age}, got {age})")
            except:
                pass

            try:
                exp = float(row["Years of Experience"])
                if 'age' in locals() and exp > age - 18:
                    deduct(10, f"Experience too high for age {age}")
            except:
                pass

            try:
                hire = pd.to_datetime(row["Hire Date"], errors="coerce").date()
                if dob and hire < dob.replace(year=dob.year + 18):
                    deduct(20, "Hire before legal age (18)")
            except:
                hire = None

            try:
                tenure = float(row["Years of Tenure"])
                if hire:
                    expected_tenure = (today - hire).days / 365.25
                    if abs(expected_tenure - tenure) > 1:
                        deduct(5, f"Tenure mismatch (expected ~{expected_tenure:.2f}, got {tenure})")
            except:
                pass

            try:
                exp_date = pd.to_datetime(row["Expiration Date"], errors="coerce").date()
                if exp_date < today:
                    deduct(20, f"License expired on {exp_date}")
            except:
                pass

            cdl_type = str(row.get("CDL Type", "")).strip().upper()
            if cdl_type and cdl_type not in allowed_cdl_types:
                deduct(5, f"Unexpected CDL Type '{cdl_type}'")

            cdl_num = str(row.get("CDL Number", "")).strip()
            if cdl_num and not cdl_num.replace("-", "").isalnum():
                deduct(5, "CDL Number not alphanumeric")

            if score >= 90:
                tag = "✅ Valid"
                tag_counts["valid"] += 1
            elif score >= 75:
                tag = "⚠️ Partial"
                tag_counts["partial"] += 1
            else:
                tag = "❌ High Risk"
                tag_counts["fail"] += 1

            results.append({"QC Tag": tag, "QC Issues": "; ".join(issues) if issues else "OK"})
            total_deductions += (100 - score)

        total_possible = 100 * len(df)
        confidence = round((1 - (total_deductions / total_possible)) * 100, 2)

        qc_df = df.copy().reset_index(drop=True)
        qc_df = pd.concat([qc_df, pd.DataFrame(results)], axis=1)

        return qc_df, confidence, tag_counts

    uploaded = st.file_uploader("📂 Upload Excel File", type=["xlsx"])
    if uploaded:
        try:
            raw_df = pd.read_excel(uploaded, sheet_name="hdvi output", header=None)
            raw_df.columns = raw_df.iloc[1]
            df = raw_df[2:].reset_index(drop=True)
            df.columns = [str(c).strip() for c in df.columns]

            if "MVR Received" not in df.columns:
                st.error("🚫 'MVR Received' column is missing. Please include it to proceed.")
                st.stop()

            # Step 1: Get user-declared client and MVR TRUE counts
            client_driver_count = st.number_input("🧑‍💼 Enter total number of drivers from client list:", min_value=1)
            expected_true_count = st.number_input("✅ Enter number of drivers expected to have MVRs (TRUE):", min_value=0, max_value=client_driver_count)

            if client_driver_count and expected_true_count is not None:
                df["MVR Received"] = df["MVR Received"].astype(str).str.upper().str.strip()
                actual_true = (df["MVR Received"] == "TRUE").sum()
                actual_false = (df["MVR Received"] == "FALSE").sum()
                total_labeled = actual_true + actual_false

                st.markdown("### 🔍 MVR Received Breakdown")
                st.write(f"✅ Marked TRUE: {actual_true}")
                st.write(f"❌ Marked FALSE: {actual_false}")
                st.write(f"📄 Total Labeled: {total_labeled}")
                st.write(f"🧑‍💼 Declared Client Count: {int(client_driver_count)}")
                st.write(f"🎯 Expected TRUEs: {int(expected_true_count)}")

                if total_labeled != client_driver_count:
                    st.error("🚫 Mismatch: TRUE + FALSE must equal client driver count. Please check your file.")
                    st.stop()

                if actual_true != expected_true_count:
                    st.error("❗ TRUE count mismatch. File cannot be processed until corrected.")
                    st.stop()

                st.success("✅ MVR count validation passed. Proceeding to QC...")

                qc_df, confidence, counts = run_qc(df)

                st.success(f"✅ QC completed! Confidence Score: **{confidence}%**")
                st.dataframe(qc_df[["QC Tag", "QC Issues"]], use_container_width=True)

                buffer = BytesIO()
                qc_df.to_excel(buffer, index=False, engine="openpyxl")
                buffer.seek(0)

                st.download_button(
                    label="📥 Download QC Report",
                    data=buffer,
                    file_name="qc_results_output.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                st.markdown("### 📊 QC Summary")
                st.write(f"✅ Valid Rows: {counts['valid']}")
                st.write(f"⚠️ Partial Rows: {counts['partial']}")
                st.write(f"❌ High Risk Rows: {counts['fail']}")

        except Exception as e:
            st.error(f"An error occurred while processing your file: {e}")

# Truckings IFTA tool
elif menu == "Truckings IFTA" and st.session_state["role"] in ["admin", "user"]:
    st.markdown('<div class="custom-heading">Truckings IFTA Tool</div>', unsafe_allow_html=True)
    st.write("Truckings IFTA tool will be available soon.")

# Riscom MVR tool
elif menu == "Riscom MVR" and st.session_state["role"] in ["admin", "user"]:
    st.markdown('<div class="custom-heading">Riscom MVR Tool</div>', unsafe_allow_html=True)
    st.write("Riscom MVR tool will be available soon.")

# MVR GPT tool (accessible to all roles)
elif menu == "MVR GPT":
    import pandas as pd
    import streamlit as st
    from fuzzywuzzy import process, fuzz
    import re
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    import joblib
    from sklearn.preprocessing import LabelEncoder
    
    st.markdown('<div class="custom-heading">MVR GPT Tool</div>', unsafe_allow_html=True)
    st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTIGEqSiDgNs2c5VkcZ9eUba_LVjvy74f7w-w&s",
             width=100, caption="")
    
    @st.cache_data
    def load_data():
        try:
            df = pd.read_excel("Violation GPT MODEL.xlsx", engine="openpyxl")
            df.columns = df.columns.str.strip()  # Clean column names
            df = df.dropna(subset=["Violation Description", "Category"])
            df["Violation Description"] = df["Violation Description"].str.strip()
            return df
        except Exception as e:
            st.error(f"❌ Failed to load data: {e}")
            return pd.DataFrame()
    
    df = load_data()
    if df.empty:
        st.stop()
    
    X_text = df["Violation Description"].str.lower()
    y = df["Category"]
    
    # === Encode & Vectorize ===
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    tfidf = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
    X_vect = tfidf.fit_transform(X_text)
    
    # === Model Train and Save Function ===
    def train_and_save_model(X_vect, y_encoded, tfidf, label_encoder, model_path):
        model = Pipeline([("clf", LogisticRegression(max_iter=500))])
        model.fit(X_vect, y_encoded)
        joblib.dump((model, tfidf, label_encoder), model_path)  # Save all 3 objects in a tuple
        return model, tfidf, label_encoder
    
    # === Model Train or Robust Load ===
    model_path = "violation_model.pkl"
    if not os.path.exists(model_path):
        st.info("Training model for the first time...")
        model, tfidf, label_encoder = train_and_save_model(X_vect, y_encoded, tfidf, label_encoder, model_path)
    else:
        loaded_obj = joblib.load(model_path)
        if isinstance(loaded_obj, tuple) and len(loaded_obj) == 3:
            model, tfidf, label_encoder = loaded_obj
        else:
            st.warning("⚠️ Existing pickle file is invalid. Retraining model...")
            model, tfidf, label_encoder = train_and_save_model(X_vect, y_encoded, tfidf, label_encoder, model_path)
    
    # === Keyword Rules ===
    non_moving_keywords = [
        "improper equipment", "defective equipment", "traffic fines", "penalties",
        "lic", "fine", "court", "suspension", "misc", "sticker", "tags", "miscellaneous",
        "background check", "notice", "seat belt", "insurance", "certificate",
        "weighing", "loading", "length", "carrying", "loads", "susp", "seatbelt",
        "failure to signal", "illegal stop", "obstructing traffic","law"
    ]
    non_moving_keywords = [kw.lower() for kw in non_moving_keywords]
    
    rules = {
        "Accident Violation": ["collision", "crash", "hit and run"],
        "Major Violation": ["reckless", "dui", "excessive speeding", "dangerous"],
        "Prohibited Violation": ["prohibited", "unauthorized", "restricted"],
        "Minor Violation": ["speeding", "late payment", "parking violation"]
    }
    
    # === Rule-Based Priority Detection ===
    def detect_priority(desc):
        desc = desc.lower()
    
        if any(kw in desc for kw in non_moving_keywords):
            return "🚨 **Non-Moving Violation**"
    
        match = re.search(r"(\d{2,})/(\d{2,})", desc)
        if match:
            num, denom = map(int, match.groups())
            if num < denom:
                return "Minor Violation"
            elif num - denom >= 20:
                return "🚨 Major Violation"
            else:
                return "⚠️ Minor Violation"
    
        for lbl, kw_list in rules.items():
            if any(k in desc for k in kw_list):
                return f"🚨 Rule-Based: **{lbl}**"
    
        return "Unknown Violation"
    
    # === Classification Engine ===
    def classify_violation(description):
        desc = description.strip().lower()
    
        exact = df[df["Violation Description"].str.lower() == desc]
        if not exact.empty:
            return f"✅ Exact: **{exact['Category'].values[0]}**"
    
        rule = detect_priority(desc)
        if rule != "Unknown Violation,Better ask QA Team":
            return rule
    
        vec = tfidf.transform([desc])
        proba = model.predict_proba(vec)
        idx = np.argmax(proba)
        predicted_label = label_encoder.inverse_transform([idx])[0]
        confidence = proba[0][idx] * 100
        return f"🤖 Partial Prediction: **{predicted_label}** (Confidence: {confidence:.2f}%)"
    
    # === Streamlit UI ===
    user_input = st.text_input("🔍 Enter Violation Description:")
    if user_input:
        if user_input.strip().lower() in ["yogaraj", "yoga"]:
            st.success("🐉 **Dragon Warrior** 🐼")
        else:
            result = classify_violation(user_input)
            st.info(result)
