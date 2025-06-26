import pandas as pd
import streamlit as st
from thefuzz import fuzz, process
import re
import io
from datetime import datetime
from all_trans_mvr import all_trans_mvr_app
from mvr_gpt import mvr_gpt_app
from qc_radar import qc_radar_app


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
    all_trans_mvr_app(get_valid_column, names_match)
# Welcome screen for "App" menu
elif menu == "App":
    from insight_dashboard import render_dashboard
    render_dashboard()
# HDVI MVR tool
elif menu == "QC Radar" and st.session_state["role"] in ["admin", "user"]:
    qc_radar_app()
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
    mvr_gpt_app()
    
