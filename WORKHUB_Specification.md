# WORKHUB – Project Specification

## 1. Project Overview
WORKHUB is an AI-powered workshop registration cleaner developed using Python and Google's Gemini API. It extracts participant details from registration messages and converts them into structured records.

## 2. Problem Statement
Workshop registrations received through forms and WhatsApp messages may contain incomplete details, incorrect information and duplicate entries. Manually checking these records is time-consuming.

## 3. Input
The system accepts registration records containing:
- Registration ID
- Workshop name
- Participant registration message

## 4. AI Extraction
Gemini AI extracts the following five fields:
- Name
- Phone number
- Email address
- Academic year
- Branch

The extracted information must be returned as a JSON object.

## 5. Cleaning and Validation Rules
- Remove unnecessary spaces from names.
- Validate phone numbers using the required format.
- Check email address format.
- Accept academic years from 1 to 4.
- Accept only approved branches: CSE, IT, AIDS, ECE, EEE, MECH and CIVIL.
- Missing or invalid details must be flagged.

## 6. Fact Checking
Extracted phone numbers and email addresses are checked against the original registration message. Information that does not match the source is rejected.

## 7. Duplicate Detection
Registrations are compared using phone numbers and email addresses within the same workshop. Repeated registrations are marked as duplicates.

## 8. Output
The system generates three files:
- clean_list.csv – Valid registration records.
- problems.csv – Duplicate and incorrect records with reasons.
- summary.txt – Registration statistics grouped by status, branch and year.

## 9. Error Handling
Missing information, invalid data, incorrect JSON responses and API errors are identified and recorded for review.

## 10. Human Responsibility
The system identifies problematic records. A workshop organiser reviews and corrects flagged entries before finalising registrations.

## 11. Technologies Used
Python, Google Gemini API, CSV, JSON, Regular Expressions and Python-dotenv.