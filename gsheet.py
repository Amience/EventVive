import streamlit as st
from google.oauth2.service_account import Credentials
import gspread
import time
from datetime import datetime

def create_gsheet_connection():
    """This function establishes a connection with GOOGLE SHEETS"""

    # Load credentials from Streamlit secrets
    creds_dict = {
        "type": st.secrets["connections"]["gsheets"]["type"],
        "project_id": st.secrets["connections"]["gsheets"]["project_id"],
        "private_key_id": st.secrets["connections"]["gsheets"]["private_key_id"],
        "private_key": st.secrets["connections"]["gsheets"]["private_key"],
        "client_email": st.secrets["connections"]["gsheets"]["client_email"],
        "client_id": st.secrets["connections"]["gsheets"]["client_id"],
        "auth_uri": st.secrets["connections"]["gsheets"]["auth_uri"],
        "token_uri": st.secrets["connections"]["gsheets"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["connections"]["gsheets"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["connections"]["gsheets"]["client_x509_cert_url"],
        "universe_domain": st.secrets["connections"]["gsheets"]["universe_domain"]
    }
    # Define the scope for Google Sheets access
    scope = ['https://www.googleapis.com/auth/spreadsheets']

    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    # Authorize the client
    client = gspread.authorize(creds)
    # Get the spreadsheet URL from Streamlit secrets
    spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    # Open the spreadsheet by URL
    return client.open_by_url(spreadsheet_url)


def save_data_to_sheet(sheet, username, user_message, selected_option):
    """Function to save data to Google Sheets"""
    # Generate the current timestamp
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Attempt to append the row
    try:
        sheet.append_row([current_timestamp, username, selected_option, user_message])
        #st.success("Data saved to Google Sheets!")
    except Exception as e:
        st.error("Error 1054 - retrying")
        time.sleep(1)  # Retry delay


def save_login_to_sheet(sheet, username):
    """Function to save data to Google Sheets"""
    # Generate the current timestamp
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Attempt to append the row
    try:
        sheet.append_row([current_timestamp, username])
        #st.success("Data saved to Google Sheets!")
    except Exception as e:
        st.error("Error 1054 - retrying")
        time.sleep(1)  # Retry delay

def save_feedback_to_sheet(sheet, username, feedback, selected_option):
    """Function to save feedback to Google Sheets"""
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Prepare the row data with an empty string for the second column
    row_data = [current_timestamp, username, selected_option, "", feedback]
    sheet.append_row(row_data)