# Production Schedule Optimiser

A Python script that reads production orders from a CSV file, calculates a suggested schedule based on due dates, and writes the optimised plan to a Google Sheet. Built with **pandas**, **gspread**, and the **Google Sheets API**.

## Why This Project?

This tool solves a real-world business problem: manually creating production schedules is error‑prone and time‑consuming. By automating the process, the script:
- Removes manual data entry
- Ensures consistent scheduling logic
- Delivers the output to a collaborative Google Sheet
- Provides full logging for audit and debugging

## Features

- 📥 **Extract** – Reads order data from a CSV file  
- 🔄 **Transform** – Sorts by due date, calculates a suggested production week  
- 📤 **Load** – Writes the optimised schedule to a Google Sheet  
- 📝 **Logging** – Detailed console + file logs for tracking execution  
- 🛡️ **Error Handling** – Graceful failure with clear error messages  

## Technology Stack

- Python 3.8+
- pandas – data manipulation
- gspread – Google Sheets interaction
- google-auth – secure API authentication

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/production-schedule-optimiser.git
cd production-schedule-optimiser
