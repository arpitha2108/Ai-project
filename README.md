# WORKHUB – AI-Powered Workshop Registration Cleaner

## 1. Project Overview

WORKHUB is an AI-powered workshop registration cleaning system developed using Python and Google's Gemini API.

The system extracts participant information from registration messages, cleans and validates the details, detects duplicate registrations and generates organised output reports.

## 2. Problem Statement

Workshop registrations are received through forms and WhatsApp messages. These registrations may contain missing information, incorrect phone numbers, invalid email addresses and duplicate entries.

Manually checking every registration takes time and may result in errors.

WORKHUB automates the extraction, cleaning and validation process to make registration management easier.

## 3. Objectives

- Extract participant details using Gemini AI.
- Clean names, phone numbers and email addresses.
- Validate academic year and branch.
- Detect duplicate registrations.
- Identify incomplete and incorrect entries.
- Generate organised CSV and TXT reports.

## 4. Technologies Used

- Python
- Google Gemini API
- Google GenAI SDK
- CSV
- JSON
- Regular Expressions
- Python-dotenv

## 5. Project Structure

```text
WORKHUB/
│
├── data/
│   └── registrations.csv
│
├── reports/
│   ├── clean_list.csv
│   ├── problems.csv
│   └── summary.txt
│
├── main.py
├── evaluation.py
├── red_team.py
├── test_gemini.py
├── system_prompt.txt
├── requirements.txt
├── README.md
├── Red_Team_Results.md
├── .gitignore
└── .env
```

## 6. System Workflow

1. Read registration messages from the input CSV file.
2. Send each registration message to Gemini AI.
3. Extract name, phone, email, year and branch.
4. Fact-check extracted information against the original message.
5. Clean and validate participant details.
6. Detect duplicate registrations.
7. Separate valid and problematic records.
8. Generate output reports.

## 7. Input File

The input file is `data/registrations.csv`.

It contains registration IDs and participant messages.

## 8. Data Cleaning and Validation

The system applies the following rules:

- Removes unnecessary spaces from names.
- Validates phone numbers.
- Checks email address format.
- Accepts academic years from 1 to 4.
- Checks branches against the approved branch list.
- Identifies missing or incorrect information.

## 9. Duplicate Detection

WORKHUB checks phone numbers and email addresses within the same workshop.

If an existing registration is found with the same phone number or email address, the new registration is marked as a duplicate.

## 10. Output Files

The system generates three reports.

**clean_list.csv**

Contains valid and cleaned registration records.

**problems.csv**

Contains duplicate registrations and entries that need correction, along with their reasons.

**summary.txt**

Displays total registrations, valid entries, entries needing correction, duplicates and valid registrations grouped by branch and year.

## 11. Evaluation

The `evaluation.py` program performs 10 automated checks on the generated reports.

The checks include:

- Total record verification.
- Input and output ID uniqueness.
- Record completeness.
- Valid data checking.
- Problem status checking.
- Summary count verification.

The current evaluation run completed with 10 checks passed and 0 failed.

## 12. Red Team Testing

The `red_team.py` program performs six initial tests:

1. Missing details.
2. Invalid phone number.
3. Invalid email.
4. Invalid year.
5. Invalid branch.
6. Invalid JSON response.

The initial test run completed with 6 passed and 0 failed.

Three documented red-team scenarios are also maintained in `Red_Team_Results.md`.

## 13. Installation

Install the required Python libraries:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project folder and add:

```text
GEMINI_API_KEY=your_api_key
```

Replace `your_api_key` with your own Gemini API key.

## 14. How to Run

Run the main program:

```bash
python main.py
```

Run evaluation:

```bash
python evaluation.py
```

Run red-team tests:

```bash
python red_team.py
```

## 15. Conclusion

WORKHUB provides an organised approach to workshop registration management.

By combining AI-based information extraction with Python-based data cleaning, validation and duplicate detection, the system helps workshop organisers process registrations and identify entries that require attention.