
import time
import csv
import json
import os
import re
from pathlib import Path
from collections import defaultdict

from google import genai
from dotenv import load_dotenv


# 1. PATH AND API SETUP

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"

REPORTS_DIR.mkdir(exist_ok=True)

load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing. Check your .env file.")

client = genai.Client(api_key=api_key)

MODEL = "gemini-3.5-flash-lite"

BRANCHES = ["CSE", "IT", "AIDS", "ECE", "EEE", "MECH", "CIVIL"]

FIELDS = ["name", "phone", "email", "year", "branch"]

TEST_ONE_ENTRY = False


# 2. READ SYSTEM PROMPT

def read_prompt():

    with open(BASE_DIR / "system_prompt.txt", "r", encoding="utf-8") as file:
        return file.read()


# 3. READ CSV FILE

def read_entry():

    entries = []

    with open(DATA_DIR / "registrations.csv", "r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None or not {"id", "entry"}.issubset(reader.fieldnames):
            raise ValueError("CSV must contain id and entry columns.")

        for row in reader:
            entries.append(row)

    return entries


# 4. GET WORKSHOP NAME

def get_workshop(entry):

    match = re.search(r"Workshop\s*:\s*([^\.\n]+)", entry, re.IGNORECASE)

    if match:
        return match.group(1).strip()

    return "Unknown"


# 5. EXTRACT DETAILS USING GEMINI

def extract_details(entry, prompt):

    response = client.models.generate_content(
        model=MODEL,
        contents=entry,
        config={
            "system_instruction": prompt,
            "response_mime_type": "application/json"
        }
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    data = json.loads(response.text)

    if not isinstance(data, dict):
        raise ValueError("Gemini response must be a JSON object.")

    if set(data.keys()) != set(FIELDS):
        raise ValueError("Gemini returned incorrect fields.")

    return data


# 6. FACT CHECK

def check_facts(data, original_entry):

    reasons = []

    source_digits = re.sub(r"\D", "", original_entry)

    phone = data.get("phone")

    if phone is not None:

        phone_digits = re.sub(r"\D", "", str(phone))

        if not phone_digits or phone_digits not in source_digits:
            data["phone"] = None
            reasons.append("Phone does not match original entry")

    email = data.get("email")

    if email is not None:

        email = str(email).strip()

        if email.lower() not in original_entry.lower():
            data["email"] = None
            reasons.append("Email does not match original entry")

    return data, reasons


# 7. CLEAN PHONE NUMBER

def clean_phone(phone):

    if phone is None:
        return None

    phone = str(phone)

    phone = phone.replace(" ", "")
    phone = phone.replace("-", "")
    phone = phone.replace("+", "")

    if phone.startswith("91") and len(phone) > 10:
        phone = phone[2:]

    elif phone.startswith("0") and len(phone) > 10:
        phone = phone[1:]

    if not phone.isdigit():
        return None

    if len(phone) != 10:
        return None

    if phone[0] not in "6789":
        return None

    return phone


# 8. CLEAN EMAIL

def clean_email(email):

    if email is None:
        return None

    email = str(email).strip().lower()

    if " " in email:
        return None

    if email.count("@") != 1:
        return None

    if "." not in email.split("@")[1]:
        return None

    if email.startswith("@") or email.endswith("."):
        return None

    return email


# 9. CLEAN ALL DETAILS

def clean(data):

    cleaned = {}
    reasons = []

    # Clean name
    name = data.get("name")

    if name is None or not str(name).strip():
        cleaned["name"] = None
        reasons.append("Missing name")
    else:
        cleaned["name"] = " ".join(str(name).split()).title()

    # Clean phone
    phone = clean_phone(data.get("phone"))
    cleaned["phone"] = phone

    if phone is None:
        reasons.append("Invalid or missing phone number")

    # Clean email
    email = clean_email(data.get("email"))
    cleaned["email"] = email

    if email is None:
        reasons.append("Invalid or missing email")

    # Check year
    year = data.get("year")

    try:

        if year is None or isinstance(year, bool):
            raise ValueError

        year = int(year)

        if year not in [1, 2, 3, 4]:
            raise ValueError

        cleaned["year"] = year

    except (ValueError, TypeError):
        cleaned["year"] = None
        reasons.append("Invalid or missing year")

    # Check branch
    branch = data.get("branch")

    if branch is None:
        cleaned["branch"] = None
        reasons.append("Missing branch")

    else:

        branch = str(branch).strip().upper()

        if branch not in BRANCHES:
            cleaned["branch"] = "other"
            reasons.append("Unrecognised branch")
        else:
            cleaned["branch"] = branch

    return cleaned, reasons


# 10. CHECK VALIDITY

def is_valid(reasons):

    return len(reasons) == 0


# 11. PROCESS REGISTRATIONS

def process(entries, prompt):

    results = []

    seen_phones = {}
    seen_emails = {}

    for row in entries:

        entry_id = row["id"]
        original_entry = row["entry"]

        workshop = get_workshop(original_entry)

        try:

            # Extract details
            data = extract_details(original_entry, prompt)

            # Fact check
            data, fact_reasons = check_facts(data, original_entry)

            # Clean details
            cleaned, clean_reasons = clean(data)

            reasons = fact_reasons + clean_reasons

            phone_key = (workshop.lower(), cleaned["phone"])
            email_key = (workshop.lower(), cleaned["email"])

            duplicate_of = None

            if cleaned["phone"] is not None and phone_key in seen_phones:
                duplicate_of = seen_phones[phone_key]

            if cleaned["email"] is not None and email_key in seen_emails:
                if duplicate_of is None:
                    duplicate_of = seen_emails[email_key]

            # Decide status
            if duplicate_of is not None:
                status = "duplicate"
                reasons.append("Duplicate of " + duplicate_of)

            elif is_valid(reasons):
                status = "valid"

            else:
                status = "needs_fix"

            # Remember first occurrence
            if cleaned["phone"] is not None and phone_key not in seen_phones:
                seen_phones[phone_key] = entry_id

            if cleaned["email"] is not None and email_key not in seen_emails:
                seen_emails[email_key] = entry_id

            result = {
                "id": entry_id,
                "workshop": workshop,
                "name": cleaned["name"],
                "phone": cleaned["phone"],
                "email": cleaned["email"],
                "year": cleaned["year"],
                "branch": cleaned["branch"],
                "status": status,
                "reason": "; ".join(reasons),
                "original_entry": original_entry
            }

        except Exception as error:

            result = {
                "id": entry_id,
                "workshop": workshop,
                "name": None,
                "phone": None,
                "email": None,
                "year": None,
                "branch": None,
                "status": "needs_fix",
                "reason": "Extraction error: " + str(error),
                "original_entry": original_entry
            }

        results.append(result)

        print(entry_id, ":", result["status"])

        # Wait before sending the next Gemini request
        time.sleep(5)

    return results


# 12. WRITE OUTPUT FILES

def write_reports(results):

    valid_entries = []
    problem_entries = []

    for row in results:

        if row["status"] == "valid":
            valid_entries.append(row)

        else:
            problem_entries.append(row)

    # Create clean_list.csv
    with open(REPORTS_DIR / "clean_list.csv", "w", newline="", encoding="utf-8") as file:
        fields = ["id", "workshop", "name", "phone", "email", "year", "branch"]

        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for row in valid_entries:
            writer.writerow({key: row[key] for key in fields})

    # Create problems.csv
    with open(REPORTS_DIR / "problems.csv", "w", newline="", encoding="utf-8") as file:

        fields = [
            "id", "workshop", "name", "phone", "email",
            "year", "branch", "status", "reason", "original_entry"
        ]

        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for row in problem_entries:
            writer.writerow({key: row[key] for key in fields})

    # Create summary.txt
    status_count = defaultdict(int)
    branch_count = defaultdict(int)
    year_count = defaultdict(int)

    for row in results:
        status_count[row["status"]] += 1

    for row in valid_entries:
        branch_count[row["branch"]] += 1
        year_count[row["year"]] += 1

    with open(REPORTS_DIR / "summary.txt", "w", encoding="utf-8") as file:

        file.write("WORKHUB REGISTRATION SUMMARY\n")
        file.write("----------------------------\n")

        file.write("Total registrations: " + str(len(results)) + "\n")
        file.write("Valid entries: " + str(status_count["valid"]) + "\n")
        file.write("Needs fixing: " + str(status_count["needs_fix"]) + "\n")
        file.write("Duplicates: " + str(status_count["duplicate"]) + "\n")

        file.write("\nVALID REGISTRATIONS BY BRANCH\n")

        for branch, count in branch_count.items():
            file.write(branch + ": " + str(count) + "\n")

        file.write("\nVALID REGISTRATIONS BY YEAR\n")

        for year, count in year_count.items():
            file.write(str(year) + " year: " + str(count) + "\n")

    print("\nReports created successfully!")


# 13. MAIN FUNCTION

def main():

    print("WORKHUB - Workshop Registration Cleaner")
    print("----------------------------------------")

    prompt = read_prompt()
    entries = read_entry()

    if TEST_ONE_ENTRY:
        entries = entries[:1]

    print("\nProcessing registrations...\n")

    results = process(entries, prompt)

    write_reports(results)

    print("\nProcessing completed!")


# 14. RUN PROGRAM

if __name__ == "__main__":
    main()
