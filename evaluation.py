
import csv
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


# Read CSV files
def read_csv(filename, folder):

    with open(BASE_DIR / folder / filename, "r", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


# Evaluation
def evaluate():

    registrations = read_csv("registrations.csv", "data")
    clean = read_csv("clean_list.csv", "reports")
    problems = read_csv("problems.csv", "reports")

    print("\nWORKHUB - EVALUATION REPORT")
    print("----------------------------")

    total = len(registrations)
    valid = len(clean)
    flagged = len(problems)

    check1 = total == valid + flagged

    input_ids = [r["id"] for r in registrations]
    output_ids = [r["id"] for r in clean + problems]

    check2 = len(input_ids) == len(set(input_ids))
    check3 = len(output_ids) == len(set(output_ids))
    check4 = set(input_ids) == set(output_ids)

    branches = ["CSE", "IT", "AIDS", "ECE", "EEE", "MECH", "CIVIL"]

    check5 = all(
        r["name"]
        and re.fullmatch(r"[6-9]\d{9}", r["phone"] or "")
        and re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", r["email"] or "")
        and r["year"] in ["1", "2", "3", "4"]
        and r["branch"] in branches
        for r in clean
    )

    check6 = all(
        r["status"] in ["needs_fix", "duplicate"]
        for r in problems
    )

    duplicates = sum(
        1 for r in problems if r["status"] == "duplicate"
    )

    needs_fix = sum(
        1 for r in problems if r["status"] == "needs_fix"
    )

    # Read summary
    with open(BASE_DIR / "reports" / "summary.txt", "r", encoding="utf-8") as file:
        summary = file.read()

    def summary_count(label):

        match = re.search(
            rf"{label}:\s*(\d+)", summary, re.IGNORECASE
        )

        return int(match.group(1)) if match else None

    check7 = summary_count("Total registrations") == total
    check8 = summary_count("Valid entries") == valid
    check9 = summary_count("Needs fixing") == needs_fix
    check10 = summary_count("Duplicates") == duplicates

    checks = [
        ("Total records check", check1),
        ("Input ID uniqueness", check2),
        ("Output ID uniqueness", check3),
        ("All registrations accounted for", check4),
        ("Valid data check", check5),
        ("Problem status check", check6),
        ("Summary total check", check7),
        ("Summary valid count check", check8),
        ("Summary needs-fixing check", check9),
        ("Summary duplicate count check", check10)
    ]

    passed = 0

    for name, result in checks:

        print(name, ":", "PASS" if result else "FAIL")

        if result:
            passed += 1

    print("\nTotal checks:", len(checks))
    print("Passed:", passed)
    print("Failed:", len(checks) - passed)

    print("\nEvaluation completed!")


if __name__ == "__main__":
    evaluate()
