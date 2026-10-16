
import re


# Each skill has one canonical name and a list of accepted variations.
# The extractor returns canonical names so duplicates are avoided.

SKILL_DATABASE = {
    # Programming and software
    "Python": ["python"],
    "C": ["c programming", "c language", "c"],
    "C++": ["c++"],
    "Java": ["java"],
    "JavaScript": ["javascript", "js"],
    "SQL": ["sql", "mysql"],
    "NumPy": ["numpy"],
    "Pandas": ["pandas"],
    "Git": ["git"],
    "GitHub": ["github"],
    "VS Code": ["vs code", "visual studio code"],
    "HTML": ["html"],
    "CSS": ["css"],
    "React": ["react"],
    "FastAPI": ["fastapi"],
    "Flask": ["flask"],

    # AI and data science
    "Machine Learning": ["machine learning", "ml"],
    "Artificial Intelligence": ["artificial intelligence", "ai"],
    "Natural Language Processing": [
        "natural language processing", "nlp"
    ],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "Computer Vision": ["computer vision"],
    "Data Analysis": ["data analysis"],
    "Data Visualization": [
        "data visualization", "data visualisation"
    ],

    # Robotics
    "ROS": ["ros", "robot operating system"],
    "SLAM": ["slam", "simultaneous localization and mapping"],
    "LiDAR": ["lidar", "light detection and ranging"],
    "Motion Planning": ["motion planning"],
    "Path Planning": ["path planning"],
    "Robotic Autonomy": [
        "robotic autonomy", "autonomous robot", "autonomous robotics"
    ],
    "Control Systems": [
        "control systems", "control system", "controllers"
    ],
    "Mechatronics": ["mechatronics"],
    "Perception": ["perception"],

    # Finance and business
    "Excel": ["excel", "microsoft excel"],
    "Financial Modeling": [
        "financial modeling", "financial modelling"
    ],
    "Accounting": ["accounting"],
    "Financial Analysis": ["financial analysis"],
    "Power BI": ["power bi"],
    "Business Analysis": ["business analysis"],
    "Requirements Analysis": ["requirements analysis"],

    # Mechanical and manufacturing
    "CAD": ["cad", "computer aided design"],
    "SolidWorks": ["solidworks", "solid works"],
    "Mechanical Design": ["mechanical design"],
    "Thermodynamics": ["thermodynamics"],
    "Materials Science": ["materials science"],
    "Manufacturing": ["manufacturing"],
    "Engineering Drawing": ["engineering drawing"],
    "CNC": ["cnc", "computer numerical control"],
    "Production Planning": ["production planning"],
    "Quality Control": ["quality control"],
    "Lean Manufacturing": ["lean manufacturing"],

    # Civil engineering
    "AutoCAD": ["autocad", "auto cad"],
    "Structural Analysis": ["structural analysis"],
    "Construction": ["construction"],
    "Surveying": ["surveying"],
    "Concrete Technology": ["concrete technology"],
    "Geotechnical Engineering": ["geotechnical engineering"],
    "STAAD.Pro": ["staad.pro", "staad pro"],
    "Revit": ["revit"],
    "Structural Design": ["structural design"],

    # Marketing and UX
    "SEO": ["seo", "search engine optimization"],
    "Content Marketing": ["content marketing"],
    "Social Media Marketing": ["social media marketing"],
    "Google Analytics": ["google analytics"],
    "Digital Advertising": ["digital advertising"],
    "Email Marketing": ["email marketing"],
    "Marketing Analytics": ["marketing analytics"],
    "Figma": ["figma"],
    "UI Design": ["ui design", "user interface design"],
    "UX Design": ["ux design", "user experience design"],
    "User Research": ["user research"],
    "Wireframing": ["wireframing", "wireframes"],
    "Prototyping": ["prototyping", "prototype"],
    "Usability Testing": ["usability testing"],
}


def extract_skills(text):
    """
    Extract recognized skills from resume text.

    Args:
        text (str): Text extracted from a resume.

    Returns:
        list[str]: Sorted, unique canonical skill names.

    Matching is case-insensitive and uses token boundaries
    to reduce accidental matches inside unrelated words.
    """

    if not isinstance(text, str) or not text.strip():
        return []

    text_lower = text.lower()
    found_skills = set()

    for skill, keywords in SKILL_DATABASE.items():
        for keyword in keywords:

            # Match a complete word or phrase rather than a
            # substring inside a different word.
            pattern = (
                r"(?<!\w)"
                + re.escape(keyword.lower())
                + r"(?!\w)"
            )

            if re.search(pattern, text_lower):
                found_skills.add(skill)
                break

    return sorted(found_skills)


if __name__ == "__main__":
    # Basic checks to demonstrate expected extractor behavior.
    test_cases = [
        (
            "I use Python, JavaScript, SQL and machine learning.",
            {"Python", "JavaScript", "SQL", "Machine Learning"},
        ),
        (
            "Experience with JavaScript and React.",
            {"JavaScript", "React"},
        ),
        (
            "Skills: NLP, ML, GitHub and Pandas.",
            {
                "Natural Language Processing",
                "Machine Learning",
                "GitHub",
                "Pandas",
            },
        ),
        (
            "Knowledge of financial modelling and data visualisation.",
            {"Financial Modeling", "Data Visualization"},
        ),
        (
            "",
            set(),
        ),
    ]

    for number, (sample, expected) in enumerate(test_cases, start=1):
        actual = set(extract_skills(sample))
        passed = actual == expected

        print(f"Test {number}: {'PASS' if passed else 'FAIL'}")

        if not passed:
            print("Expected:", sorted(expected))
            print("Actual:  ", sorted(actual))
