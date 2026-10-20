
import csv
from collections import defaultdict
from pathlib import Path


# Project and O*NET data paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ONET_DIR = PROJECT_ROOT / "db_31_0_csv" / "db_31_0_csv"

OCCUPATIONS_FILE = ONET_DIR / "occupation_data.csv"
SKILLS_FILE = ONET_DIR / "essential_skills.csv"
SOFTWARE_FILE = ONET_DIR / "software_skills.csv"


def read_csv(file_path):
    """Read an O*NET CSV file using its original column names."""
    if not file_path.exists():
        raise FileNotFoundError(
            f"Required O*NET file not found: {file_path}"
        )

    with file_path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def classify_domain(title, description=""):
    """Group occupations into broad career domains."""
    text = f"{title} {description}".lower()

    rules = [
        (
            "Computer Science & IT",
            [
                "software", "computer", "programmer", "developer",
                "data scientist", "database", "cybersecurity",
                "web developer", "information technology",
                "machine learning", "artificial intelligence",
                "systems analyst", "network administrator"
            ]
        ),
        (
            "Engineering & Manufacturing",
            [
                "engineer", "engineering", "manufacturing",
                "mechanical", "electrical", "industrial",
                "aerospace", "civil", "technician", "robotics"
            ]
        ),
        (
            "Finance & Business",
            [
                "accountant", "auditor", "financial", "finance",
                "business", "management analyst", "economist",
                "investment", "banking", "actuary"
            ]
        ),
        (
            "Healthcare & Life Sciences",
            [
                "medical", "nurse", "physician", "health",
                "clinical", "pharmacist", "biologist",
                "laboratory", "therapist", "veterinarian"
            ]
        ),
        (
            "Education & Research",
            [
                "teacher", "professor", "instructor", "education",
                "researcher", "scientist", "lecturer"
            ]
        ),
        (
            "Marketing, Design & Media",
            [
                "marketing", "designer", "graphic", "artist",
                "public relations", "journalist", "writer",
                "photographer", "media", "advertising"
            ]
        ),
        (
            "Law, Public Service & Safety",
            [
                "lawyer", "attorney", "legal", "police",
                "firefighter", "security", "government",
                "social worker", "compliance"
            ]
        ),
    ]

    for domain, keywords in rules:
        if any(keyword in text for keyword in keywords):
            return domain

    return "Other Occupations"


def load_onet_database(min_importance=3.0, max_skills=20):
    """
    Return:
        domain_database: domain -> role -> required skills
        occupation_metadata: role -> occupation code and description

    Uses O*NET importance ratings and supplementary software names.
    Generic workplace skills are excluded when enough other skills exist.
    """
    occupations = read_csv(OCCUPATIONS_FILE)
    skill_rows = read_csv(SKILLS_FILE)
    software_rows = read_csv(SOFTWARE_FILE)

    occupation_info = {}

    for row in occupations:
        code = row["O*NET-SOC Code"]
        occupation_info[code] = {
            "title": row["Title"].strip(),
            "description": row.get("Description", "").strip()
        }

    # Generic skills to avoid prioritizing as skill-gap targets.
    generic_skills = {
        "reading comprehension",
        "active listening",
        "critical thinking",
        "speaking",
        "writing",
        "active learning",
        "monitoring",
        "learning strategies",
        "social perceptiveness",
        "coordination",
        "service orientation",
        "time management",
    }

    skills_by_code = defaultdict(dict)

    for row in skill_rows:
        code = row.get("O*NET-SOC Code", "")

        if code not in occupation_info:
            continue

        if row.get("Scale Name", "").strip().lower() != "importance":
            continue

        try:
            importance = float(row["Data Value"])
        except (ValueError, TypeError, KeyError):
            continue

        skill_name = row.get("Element Name", "").strip()

        if skill_name and importance >= min_importance:
            previous = skills_by_code[code].get(skill_name, 0)
            skills_by_code[code][skill_name] = max(previous, importance)

    # Collect supplementary software skills by occupation.
    software_by_code = defaultdict(set)

    for row in software_rows:
        code = row.get("O*NET-SOC Code", "")
        software_name = row.get("Example", "").strip()

        if code in occupation_info and software_name:
            software_by_code[code].add(software_name)

    domain_database = defaultdict(dict)
    occupation_metadata = {}

    for code, info in occupation_info.items():
        title = info["title"]
        description = info["description"]

        ranked_skills = sorted(
            skills_by_code[code].items(),
            key=lambda item: item[1],
            reverse=True
        )

        # Prefer skills other than generic workplace competencies.
        specific_skills = [
            skill
            for skill, _ in ranked_skills
            if skill.strip().lower() not in generic_skills
        ]

        required_skills = specific_skills[:max_skills]

        # Keep a fallback for occupations with too few specific skills.
        if len(required_skills) < 3:
            required_skills = [
                skill for skill, _ in ranked_skills[:max_skills]
            ]

        existing_lower = {skill.lower() for skill in required_skills}

        # Add software names where available, without exact duplicates.
        for software in sorted(software_by_code[code]):
            if len(required_skills) >= max_skills:
                break

            if software.lower() not in existing_lower:
                required_skills.append(software)
                existing_lower.add(software.lower())

        if not required_skills:
            continue

        domain = classify_domain(title, description)

        # Avoid overwriting occupations with duplicate titles.
        role_name = title

        if role_name in domain_database[domain]:
            role_name = f"{title} ({code})"

        domain_database[domain][role_name] = required_skills

        occupation_metadata[role_name] = {
            "occupation_code": code,
            "description": description
        }

    return dict(domain_database), occupation_metadata


if __name__ == "__main__":
    domains, metadata = load_onet_database()

    print(f"Occupations imported: {len(metadata)}")
    print(f"Career domains: {len(domains)}")

    for domain, roles in sorted(domains.items()):
        print(f"{domain}: {len(roles)} occupations")

    print("\nSample occupations and skills:")

    for domain, roles in sorted(domains.items()):
        for role, skills in list(roles.items())[:2]:
            print(f"\n{domain} — {role}")
            print(f"Skills: {skills[:8]}")

