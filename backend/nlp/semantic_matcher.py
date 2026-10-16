
from sentence_transformers import SentenceTransformer, util


class SemanticSkillMatcher:
    """
    Compare candidate skills with job requirements using
    exact matching and semantic similarity.
    """

    def __init__(self, model_name="all-MiniLM-L6-v2"):
        # Load the pretrained model once and reuse it.
        self.model = SentenceTransformer(model_name)

    def similarity(self, skill1, skill2):
        """Return cosine similarity between two skills."""
        if not skill1 or not skill2:
            return 0.0

        embeddings = self.model.encode(
            [skill1, skill2],
            convert_to_tensor=True
        )

        score = util.cos_sim(embeddings[0], embeddings[1])
        return float(score.item())

    def analyze_skills(
        self,
        candidate_skills,
        required_skills,
        semantic_threshold=0.65
    ):
        """
        Classify requirements as exact matches, related skills,
        or unmatched requirements.

        Semantic relations indicate similarity, not proof of
        practical experience or qualification.
        """
        candidate_skills = list(candidate_skills or [])
        required_skills = list(required_skills or [])

        exact_matches = []
        semantic_relations = []
        unmatched_skills = []

        # Case-insensitive exact lookup.
        candidate_lookup = {
            str(skill).strip().casefold(): skill
            for skill in candidate_skills
            if str(skill).strip()
        }

        # Preserve the original candidate skill for reporting.
        valid_candidates = [
            str(skill).strip()
            for skill in candidate_skills
            if str(skill).strip()
        ]

        # Find requirements that need semantic comparison.
        pending_requirements = []

        for required in required_skills:
            required_text = str(required).strip()

            if not required_text:
                continue

            exact_key = required_text.casefold()

            if exact_key in candidate_lookup:
                exact_matches.append({
                    "required_skill": required,
                    "matched_skill": candidate_lookup[exact_key],
                    "similarity": 1.0
                })
            else:
                pending_requirements.append(required_text)

        # Encode each skill only once for this analysis.
        if valid_candidates and pending_requirements:
            candidate_embeddings = self.model.encode(
                valid_candidates,
                convert_to_tensor=True
            )

            required_embeddings = self.model.encode(
                pending_requirements,
                convert_to_tensor=True
            )

            # Compare all candidate skills against all requirements.
            similarity_matrix = util.cos_sim(
                required_embeddings,
                candidate_embeddings
            )

            for index, required in enumerate(pending_requirements):
                scores = similarity_matrix[index]
                best_index = int(scores.argmax().item())
                best_score = float(scores[best_index].item())
                best_candidate = valid_candidates[best_index]

                if best_score >= semantic_threshold:
                    semantic_relations.append({
                        "required_skill": required,
                        "related_skill": best_candidate,
                        "similarity": round(best_score, 3)
                    })
                else:
                    unmatched_skills.append({
                        "required_skill": required,
                        "best_candidate": best_candidate,
                        "similarity": round(best_score, 3)
                    })

        else:
            # No candidate skills available for comparison.
            for required in pending_requirements:
                unmatched_skills.append({
                    "required_skill": required,
                    "best_candidate": None,
                    "similarity": 0.0
                })

        return {
            "exact_matches": exact_matches,
            "semantic_relations": semantic_relations,
            "unmatched_skills": unmatched_skills
        }

    def match_skills(
        self,
        candidate_skills,
        required_skills,
        threshold=0.55
    ):
        """Backward-compatible function returning skill pairs."""
        candidate_skills = list(candidate_skills or [])
        required_skills = list(required_skills or [])

        candidates = [
            str(skill).strip()
            for skill in candidate_skills
            if str(skill).strip()
        ]
        requirements = [
            str(skill).strip()
            for skill in required_skills
            if str(skill).strip()
        ]

        if not candidates or not requirements:
            return []

        # Batch encode instead of calling the model for every pair.
        candidate_embeddings = self.model.encode(
            candidates,
            convert_to_tensor=True
        )
        required_embeddings = self.model.encode(
            requirements,
            convert_to_tensor=True
        )

        matrix = util.cos_sim(
            candidate_embeddings,
            required_embeddings
        )

        matches = []

        for i, candidate in enumerate(candidates):
            for j, required in enumerate(requirements):
                score = float(matrix[i][j].item())

                if score >= threshold:
                    matches.append({
                        "candidate_skill": candidate,
                        "required_skill": required,
                        "similarity": round(score, 3)
                    })

        return matches


if __name__ == "__main__":
    matcher = SemanticSkillMatcher()

    candidate_skills = ["Python", "PyTorch", "SQL"]
    required_skills = [
        "Python",
        "Machine Learning",
        "Deep Learning",
        "SQL"
    ]

    analysis = matcher.analyze_skills(
        candidate_skills,
        required_skills
    )

    print("\n=== HYBRID SEMANTIC SKILL ANALYSIS ===")

    print("\nEXACT MATCHES:")
    for item in analysis["exact_matches"]:
        print(
            f"{item['matched_skill']} -> "
            f"{item['required_skill']} "
            f"(score: {item['similarity']})"
        )

    print("\nSEMANTIC RELATIONS:")
    for item in analysis["semantic_relations"]:
        print(
            f"{item['related_skill']} -> "
            f"{item['required_skill']} "
            f"(score: {item['similarity']})"
        )

    print("\nUNMATCHED / LOW SIMILARITY:")
    for item in analysis["unmatched_skills"]:
        print(
            f"{item['required_skill']} "
            f"<- best candidate: {item['best_candidate']} "
            f"(score: {item['similarity']})"
        )
