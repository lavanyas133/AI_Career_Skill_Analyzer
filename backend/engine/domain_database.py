# =========================================================
# MULTI-DOMAIN CAREER DATABASE
# =========================================================

DOMAIN_DATABASE = {

    "Computer Science & AI": {

        "Machine Learning Engineer": [
            "Python",
            "SQL",
            "NumPy",
            "Pandas",
            "Machine Learning",
            "Statistics",
            "Scikit-learn",
            "TensorFlow",
            "PyTorch",
            "Deep Learning"
        ],

        "AI Engineer": [
            "Python",
            "Machine Learning",
            "Artificial Intelligence",
            "Natural Language Processing",
            "Deep Learning",
            "TensorFlow",
            "PyTorch",
            "SQL",
            "Git"
        ],

        "Software Developer": [
            "Python",
            "Java",
            "C++",
            "SQL",
            "Git",
            "GitHub",
            "HTML",
            "CSS",
            "JavaScript"
        ],

        "Data Scientist": [
            "Python",
            "SQL",
            "NumPy",
            "Pandas",
            "Statistics",
            "Machine Learning",
            "Data Visualization",
            "Scikit-learn"
        ]
    },


    "Finance & Business": {

        "Financial Analyst": [
            "Excel",
            "Financial Modeling",
            "Accounting",
            "Financial Analysis",
            "Statistics",
            "SQL",
            "Power BI",
            "Data Visualization"
        ],

        "Business Analyst": [
            "Excel",
            "SQL",
            "Power BI",
            "Data Analysis",
            "Statistics",
            "Business Analysis",
            "Requirements Analysis",
            "Data Visualization"
        ]
    },


    "Mechanical & Manufacturing": {

        "Mechanical Engineer": [
            "CAD",
            "SolidWorks",
            "Mechanical Design",
            "Thermodynamics",
            "Materials Science",
            "Manufacturing",
            "Engineering Drawing"
        ],

        "Manufacturing Engineer": [
            "CAD",
            "SolidWorks",
            "Manufacturing",
            "CNC",
            "Production Planning",
            "Quality Control",
            "Materials Science",
            "Lean Manufacturing"
        ]
    },


    "Civil & Infrastructure": {

        "Civil Engineer": [
            "AutoCAD",
            "Structural Analysis",
            "Construction",
            "Surveying",
            "Concrete Technology",
            "Geotechnical Engineering",
            "Engineering Drawing"
        ],

        "Structural Engineer": [
            "AutoCAD",
            "Structural Analysis",
            "STAAD.Pro",
            "Revit",
            "Concrete Technology",
            "Structural Design",
            "Engineering Drawing"
        ]
    },


    "Marketing & UX": {

        "Digital Marketing Specialist": [
            "SEO",
            "Content Marketing",
            "Social Media Marketing",
            "Google Analytics",
            "Digital Advertising",
            "Email Marketing",
            "Marketing Analytics"
        ],

        "UX Designer": [
            "Figma",
            "UI Design",
            "UX Design",
            "User Research",
            "Wireframing",
            "Prototyping",
            "Usability Testing"
        ]
    }
}


def get_domains():
    return list(DOMAIN_DATABASE.keys())


def get_roles(domain):
    if domain not in DOMAIN_DATABASE:
        raise ValueError(f"Unknown domain: {domain}")

    return list(DOMAIN_DATABASE[domain].keys())


def get_domain_role_requirements(domain, role):
    if domain not in DOMAIN_DATABASE:
        raise ValueError(f"Unknown domain: {domain}")

    if role not in DOMAIN_DATABASE[domain]:
        raise ValueError(
            f"Unknown role '{role}' in domain '{domain}'"
        )

    return DOMAIN_DATABASE[domain][role]

# =========================================================
# O*NET REAL OCCUPATION DATABASE
# =========================================================

from backend.data.onet_importer import load_onet_database

ONET_DATABASE, ONET_METADATA = load_onet_database()


def get_all_domains():
    """Return existing domains plus domains from O*NET."""
    return sorted(set(DOMAIN_DATABASE) | set(ONET_DATABASE))


def get_all_roles(domain):
    """Return existing and O*NET roles for a domain."""
    existing_roles = DOMAIN_DATABASE.get(domain, {})
    onet_roles = ONET_DATABASE.get(domain, {})

    return sorted(set(existing_roles) | set(onet_roles))



def get_all_role_requirements(domain, role):
    """Return role requirements from the selected domain."""
    existing_roles = DOMAIN_DATABASE.get(domain, {})
    onet_roles = ONET_DATABASE.get(domain, {})

    if role in existing_roles:
        return existing_roles[role]

    if role in onet_roles:
        return onet_roles[role]

    # Fallback: find the role in another domain if the exact
    # domain selection differs between the static and O*NET databases.
    for roles in DOMAIN_DATABASE.values():
        if role in roles:
            return roles[role]

    for roles in ONET_DATABASE.values():
        if role in roles:
            return roles[role]

    raise ValueError(f"Unknown role '{role}' in domain '{domain}'")
