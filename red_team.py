
import re
import json

def test_missing_details():
    data = {
        "name": None,
        "phone": None,
        "email": None,
        "year": None,
        "branch": None
    }

    return all(value is None for value in data.values())


def test_invalid_phone():
    phone = "12345"
    return not re.fullmatch(r"[6-9]\d{9}", phone)


def test_invalid_email():
    email = "student@"
    return not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)


def test_invalid_year():
    year = 7
    return year not in [1, 2, 3, 4]


def test_invalid_branch():
    branch = "UNKNOWN"
    branches = ["CSE", "IT", "AIDS", "ECE", "EEE", "MECH", "CIVIL"]

    return branch not in branches


def test_invalid_json():
    response = "{name: Karthik, phone: 12345}"

    try:
        json.loads(response)
        return False
    except json.JSONDecodeError:
        return True


def run_tests():

    tests = [
        ("Missing details", test_missing_details),
        ("Invalid phone", test_invalid_phone),
        ("Invalid email", test_invalid_email),
        ("Invalid year", test_invalid_year),
        ("Invalid branch", test_invalid_branch),
        ("Invalid JSON", test_invalid_json)
    ]

    print("\nWORKHUB - RED TEAM TESTING")
    print("---------------------------")

    passed = 0

    for name, test in tests:
        result = test()

        print(name, ":", "PASS" if result else "FAIL")

        if result:
            passed += 1

    print("\nTotal tests:", len(tests))
    print("Passed:", passed)
    print("Failed:", len(tests) - passed)

    print("\nRed Team testing completed!")


if __name__ == "__main__":
    run_tests()
