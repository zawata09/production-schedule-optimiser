import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import logging
import sys
from datetime import datetime

# --- Configuration ---
SPREADSHEET_NAME = "Production Orders"  # Name of your Google Sheet
SHEET_NAME = "Optimized Schedule"       # Name of the new sheet to create
CSV_FILE = "production_orders.csv"      # Your input CSV file
SERVICE_ACCOUNT_FILE = "credentials.json" # Your downloaded Google API credentials

# --- Set Up Logging ---
# This configures logging to both the console and a file named 'app.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),   # Log to a file for record-keeping
        logging.StreamHandler(sys.stdout) # Also print to the console
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to orchestrate the ETL process."""
    logger.info("="*30)
    logger.info("Starting Production Schedule Optimizer")
    logger.info("="*30)

    # --- Step 1: Extract (Read CSV) ---
    logger.info(f"Attempting to read CSV file: {CSV_FILE}")
    
    try:
        df = pd.read_csv(CSV_FILE)
        logger.info(f"Successfully read {len(df)} rows from CSV.")
        logger.info(f"Actual column names: {list(df.columns)}")
        logger.debug(f"CSV Columns: {list(df.columns)}")
    except FileNotFoundError:
        logger.error(f"FATAL: CSV file '{CSV_FILE}' not found. Exiting.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"FATAL: Unexpected error reading CSV: {e}. Exiting.")
        sys.exit(1)

    # --- Step 2: Transform (Process Data) ---
    logger.info("Starting data transformation...")
    
    # Convert 'DueDate' column to datetime for proper sorting
    try:
        df['DueDate'] = pd.to_datetime(df['DueDate'])
        logger.info("Successfully converted 'DueDate' to datetime format.")
    except Exception as e:
        logger.error(f"Error converting dates: {e}. Check CSV for correct date format (YYYY-MM-DD).")
        sys.exit(1)

    # Add a new column 'SuggestedWeek' based on the due date's week number
    # This simulates a simple scheduling logic
    df['SuggestedWeek'] = df['DueDate'].dt.isocalendar().week
    logger.info(f"Calculated 'SuggestedWeek' for all orders.")

    # Sort the DataFrame by 'DueDate' (earliest to latest)
    df_sorted = df.sort_values(by='DueDate')
    logger.info(f"Sorted data by 'DueDate'.")

    # Rename columns for clarity in the output Google Sheet
    df_output = df_sorted.rename(columns={
        'DueDate': 'Due Date',
        'Qty': 'Quantity',
        'Material': 'Material Type'
    })

    # Convert the 'Due Date' column back to a string format for better display
    df_output['Due Date'] = df_output['Due Date'].dt.strftime('%Y-%m-%d')
    logger.info(f"Data transformation complete. DataFrame shape: {df_output.shape}")

    # --- Step 3: Load (Write to Google Sheets) ---
    logger.info("Attempting to write data to Google Sheets...")
    
    # Define the required OAuth2 scope for Google Sheets and Drive
    scope = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    try:
        # Authenticate using the service account JSON file
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scope)
        client = gspread.authorize(creds)
        logger.info("Successfully authenticated with Google Sheets API.")
    except FileNotFoundError:
        logger.error(f"FATAL: Credentials file '{SERVICE_ACCOUNT_FILE}' not found. Ensure it is in the script's directory.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"FATAL: Authentication error: {e}. Check your credentials file and API enablement.")
        sys.exit(1)

    try:
        # Open the Google Sheet by its name
        spreadsheet = client.open(SPREADSHEET_NAME)
        
        # Try to get the target worksheet. If it doesn't exist, create it.
        try:
            worksheet = spreadsheet.worksheet(SHEET_NAME)
            logger.info(f"Worksheet '{SHEET_NAME}' found. It will be overwritten.")
            worksheet.clear()  # Clear existing data before writing new data
        except gspread.exceptions.WorksheetNotFound:
            logger.info(f"Worksheet '{SHEET_NAME}' not found. Creating a new one.")
            # Create a new worksheet with a generous default size
            worksheet = spreadsheet.add_worksheet(title=SHEET_NAME, rows=100, cols=20)
        
        # Convert the final DataFrame to a list of lists format required by gspread
        # This includes the header row
        data_to_upload = [df_output.columns.values.tolist()] + df_output.values.tolist()
        
        # Update the worksheet starting from cell A1
        worksheet.update('A1', data_to_upload)
        logger.info(f"SUCCESS! Data successfully written to Google Sheet: '{SPREADSHEET_NAME}' -> '{SHEET_NAME}'.")
        
    except gspread.exceptions.SpreadsheetNotFound:
        logger.error(f"FATAL: Spreadsheet '{SPREADSHEET_NAME}' not found. Ensure it exists and is shared with the service account email.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"FATAL: An error occurred while writing to Google Sheets: {e}")
        sys.exit(1)

    logger.info("="*30)
    logger.info("Production Schedule Optimizer finished successfully!")
    logger.info("="*30)

if __name__ == "__main__":
    main()