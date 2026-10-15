
def calculate_readiness_score(
    required_skills: list[str],
    known_skills: list[str]
) -> float:
    """
    Calculate career readiness based on required skills covered.

    Returns a score between 0 and 100.
    """
    if not required_skills:
        return 0.0

    known = {skill.strip().lower() for skill in known_skills}
    required = {skill.strip().lower() for skill in required_skills}

    matched_skills = required.intersection(known)

    score = (len(matched_skills) / len(required)) * 100

    return round(score, 2)


def simulate_learning_skill(
    required_skills: list[str],
    known_skills: list[str],
    skill_to_learn: str
) -> dict:
    """
    Simulate how learning one missing skill changes readiness.
    """
    current_score = calculate_readiness_score(
        required_skills, known_skills
    )

    required = {skill.strip().lower() for skill in required_skills}
    known = {skill.strip().lower() for skill in known_skills}
    selected = skill_to_learn.strip().lower()

    if selected not in required:
        raise ValueError("This skill is not required for the selected role.")

    if selected in known:
        raise ValueError("You already have this skill.")

    projected_skills = known_skills + [skill_to_learn]

    projected_score = calculate_readiness_score(
        required_skills, projected_skills
    )

    return {
        "current_score": current_score,
        "projected_score": projected_score,
        "improvement": round(projected_score - current_score, 2),
        "skill_to_learn": skill_to_learn
    }

def calculate_weighted_readiness_score(
    required_skill_weights: dict[str, float],
    known_skills: list[str]
) -> float:
    """
    Calculate readiness using role-specific skill weights.

    Each weight represents the importance assigned to a skill.
    Returns a score between 0 and 100.
    """
    if not required_skill_weights:
        return 0.0

    if any(weight < 0 for weight in required_skill_weights.values()):
        raise ValueError("Skill weights cannot be negative.")

    total_weight = sum(required_skill_weights.values())

    if total_weight <= 0:
        raise ValueError("Total skill weight must be positive.")

    known = {skill.strip().lower() for skill in known_skills}

    earned_weight = sum(
        weight
        for skill, weight in required_skill_weights.items()
        if skill.strip().lower() in known
    )

    return round((earned_weight / total_weight) * 100, 2)
