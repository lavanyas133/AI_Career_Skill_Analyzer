
import re


def find_skill_evidence(text, skill):
    """
    Find resume lines containing a skill as a whole term.

    Returns:
        list[str]: Lines that contain the skill.
    """
    if not isinstance(text, str) or not isinstance(skill, str):
        return []

    skill = skill.strip()

    if not text.strip() or not skill:
        return []

    evidence = []

    # Escape special characters so skills like C++ and .NET
    # are searched as literal text.
    pattern = re.compile(
        r"(?<!\w)" + re.escape(skill) + r"(?!\w)",
        re.IGNORECASE
    )

    for line in text.splitlines():
        line_clean = line.strip()

        if line_clean and pattern.search(line_clean):
            evidence.append(line_clean)

    return evidence


def analyze_skill_evidence(text, skills):
    """
    Find text supporting each skill detected in a resume.

    'demonstrated' here means textual evidence was found;
    it does not verify a candidate's actual proficiency.
    """
    if not isinstance(text, str):
        text = ""

    results = {}

    for skill in skills:
        evidence = find_skill_evidence(text, skill)

        results[skill] = {
            "claimed": True,
            "demonstrated": bool(evidence),
            "evidence": evidence
        }

    return results


if __name__ == "__main__":
    sample_resume = """
    Skills: Python, JavaScript and SQL.
    Project: Built a Python data analysis application.
    Experience: Used JavaScript to create an interactive webpage.
    """

    test_cases = [
        ("Python is useful", "Python", True),
        ("Experience with JavaScript", "Java", False),
        ("Used C++ for a project", "C++", True),
        ("Worked with SQL databases", "SQL", True),
        ("", "Python", False),
    ]

    print("=== EVIDENCE ANALYZER TESTS ===")

    for number, (sample, skill, expected) in enumerate(
        test_cases, start=1
    ):
        actual = bool(find_skill_evidence(sample, skill))
        status = "PASS" if actual == expected else "FAIL"

        print(f"Test {number}: {status}")

        if actual != expected:
            print("Expected:", expected, "| Actual:", actual)

    print("\n=== SAMPLE RESUME EVIDENCE ===")
    results = analyze_skill_evidence(
        sample_resume,
        ["Python", "Java", "JavaScript", "SQL"]
    )

    for skill, result in results.items():
        print(f"\n{skill}:")
        print("Evidence found:", result["demonstrated"])
        print("Lines:", result["evidence"])
