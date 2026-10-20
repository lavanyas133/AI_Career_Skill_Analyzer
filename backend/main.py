# =========================================================
# AI CAREER SKILL TWIN - FASTAPI BACKEND
# =========================================================

from fastapi import FastAPI, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException

import os
import shutil


# =========================================================
# NLP
# =========================================================

from backend.nlp.resume_parser import extract_resume_text
from backend.nlp.skill_extractor import extract_skills
from backend.nlp.evidence_analyzer import analyze_skill_evidence
from backend.nlp.semantic_matcher import SemanticSkillMatcher


# =========================================================
# SKILL ENGINE
# =========================================================

from backend.engine.domain_database import get_all_role_requirements

from backend.engine.skill_gap_analyzer import (
    analyze_skill_gap
)

from backend.engine.minimum_skill_path import (
    calculate_minimum_skill_path
)

from backend.engine.assessment_engine import (
    get_questions,
    calculate_score
)

from backend.engine.skill_dependency_graph import (
    get_graph_data
)


# =========================================================
# DATABASE
# =========================================================

from database.database import get_db

from database.models import (
    Student,
    SkillRecord,
    AssessmentResult
)

from database.progress_manager import (
    save_progress,
    get_student_progress
)


# =========================================================
# CREATE FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="AI Career Skill Twin API",
    description="AI-powered career skill gap analysis system",
    version="1.0.0"
)
semantic_matcher = SemanticSkillMatcher()


# =========================================================
# UPLOAD FOLDER
# =========================================================

UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "message": "AI Career Skill Twin API is running!"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


# =========================================================
# RESUME ANALYSIS
# =========================================================

@app.post("/analyze")
async def analyze_resume(

    file: UploadFile = File(...),
    role: str = Form(...),
    domain: str = Form(...),
    student_id: int | None = Form(None),
    db: Session = Depends(get_db)

):

    # -----------------------------------------------------
    # SAVE UPLOADED FILE
    # -----------------------------------------------------

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    # -----------------------------------------------------
    # EXTRACT RESUME TEXT
    # -----------------------------------------------------

    resume_text = extract_resume_text(
        file_path
    )


    # -----------------------------------------------------
    # EXTRACT SKILLS
    # -----------------------------------------------------

    student_skills = extract_skills(
        resume_text
    )


    # -----------------------------------------------------
    # GET TARGET ROLE REQUIREMENTS
    # -----------------------------------------------------

    required_skills = get_all_role_requirements(
    domain,
    role
)
    semantic_analysis = semantic_matcher.analyze_skills(
    student_skills,
    required_skills
)


    # -----------------------------------------------------
    # ANALYZE SKILL GAP
    # -----------------------------------------------------

    skill_gap = analyze_skill_gap(
        student_skills,
        required_skills
    )


    # -----------------------------------------------------
    # CALCULATE MINIMUM SKILL PATH
    # -----------------------------------------------------

    minimum_skill_path = (
        calculate_minimum_skill_path(
            student_skills,
            required_skills
        )
    )


    # -----------------------------------------------------
    # ANALYZE SKILL EVIDENCE
    # -----------------------------------------------------

    skill_evidence = analyze_skill_evidence(
        resume_text,
        student_skills
    )


    # =====================================================
    # CREATE STUDENT RECORD
    # =====================================================



    if student_id is not None:
        student = db.query(Student).filter(
            Student.id == student_id
        ).first()

        if student is None:
            raise HTTPException(
                status_code=404,
                detail="Student not found."
            )

        student.target_role = role
        db.commit()
        db.refresh(student)

    else:
        student = Student(
            target_role=role
        )

        db.add(student)
        db.commit()
        db.refresh(student)




    # =====================================================
    # SAVE SKILL RECORDS
    # =====================================================

    for skill in student_skills:

        evidence = skill_evidence.get(
            skill,
            {}
        )

        if evidence.get(
            "demonstrated"
        ):

            status = "demonstrated"

        else:

            status = "claimed"


        skill_record = SkillRecord(

            student_id=student.id,

            skill=skill,

            status=status,

            source="resume"

        )

        db.add(
            skill_record
        )


    db.commit()


    # =====================================================
    # CREATE INITIAL LEARNING PROGRESS
    # =====================================================

    # Skills already detected in the resume
    # are initially marked as completed.

    for skill in student_skills:

        save_progress(

            db=db,

            student_id=student.id,

            skill=skill,

            status="Completed",

            progress_percentage=100,

            notes="Skill detected from resume."

        )


    # =====================================================
    # CREATE PROGRESS RECORDS FOR MISSING SKILLS
    # =====================================================

    for skill in skill_gap["skills_missing"]:

        save_progress(

            db=db,

            student_id=student.id,

            skill=skill,

            status="Not Started",

            progress_percentage=0,

            notes="Skill identified as missing for target role."

        )


    # =====================================================
    # RETURN ANALYSIS
    # =====================================================

    return {

        "student_id": student.id,

        "career_role": role,

        "student_skills": student_skills,

        "required_skills": required_skills,

        "skills_you_have": (
    skill_gap["skills_you_have"]
),

"skills_semantically_related": (
    skill_gap["skills_semantically_related"]
),

"skills_missing": (
    skill_gap["skills_missing"]
),

        "minimum_skill_path": (
            minimum_skill_path
        ),

        "skill_evidence": skill_evidence,
    "semantic_analysis": semantic_analysis

    }


# =========================================================
# GET ASSESSMENT QUESTIONS
# =========================================================


@app.get("/assessment/{skill}")
def get_skill_assessment(skill: str):
    questions = get_questions(skill)

    if not questions:
        return {
            "skill": skill,
            "questions": [],
            "message": "No assessment is currently available for this skill."
        }

    safe_questions = [
        {
            "question": question["question"],
            "options": question["options"]
        }
        for question in questions
    ]

    return {
        "skill": skill,
        "questions": safe_questions
    }


# =========================================================
# SUBMIT ASSESSMENT
# =========================================================

@app.post(
    "/assessment/{skill}/submit"
)
def submit_skill_assessment(

    skill: str,

    answers: list[str],

    student_id: int,

    db: Session = Depends(get_db)

):

    # -----------------------------------------------------
    # CALCULATE SCORE
    # -----------------------------------------------------

    result = calculate_score(
        skill,
        answers
    )


    # -----------------------------------------------------
    # SAVE ASSESSMENT RESULT
    # -----------------------------------------------------

    assessment_record = AssessmentResult(

        student_id=student_id,

        skill=skill,

        score=result["score"],

        correct_answers=(
            result["correct_answers"]
        ),

        total_questions=(
            result["total_questions"]
        ),

        proficiency=result["level"]

    )


    db.add(
        assessment_record
    )

    db.commit()

    db.refresh(
        assessment_record
    )


    # =====================================================
    # UPDATE LEARNING PROGRESS
    # =====================================================

    score = result["score"]


    if score >= 80:

        status = "Completed"

    elif score >= 40:

        status = "In Progress"

    else:

        status = "Needs Improvement"


    save_progress(

        db=db,

        student_id=student_id,

        skill=skill,

        status=status,

        progress_percentage=score,

        notes=(
            f"Assessment completed with "
            f"{score:.0f}% score."
        )

    )


    # =====================================================
    # RETURN RESULT
    # =====================================================

    return {

        "assessment_id":
            assessment_record.id,

        "student_id":
            student_id,

        "skill":
            skill,

        "score":
            result["score"],

        "correct_answers":
            result["correct_answers"],

        "total_questions":
            result["total_questions"],

        "level":
            result["level"],

        "progress_status":
            status

    }


# =========================================================
# SKILL DEPENDENCY GRAPH
# =========================================================


@app.get("/skill-graph/{role}")
def get_skill_dependency_graph(
    role: str,
    domain: str = "Computer Science & AI"
):
    try:
        required_skills = get_all_role_requirements(
            domain,
            role
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    graph_data = get_graph_data(required_skills)

    return {
        "career_role": role,
        "domain": domain,
        "required_skills": required_skills,
        "graph": graph_data
    }


# =========================================================
# GET LEARNING PROGRESS
# =========================================================

@app.get(
    "/progress/{student_id}"
)
def get_learning_progress(

    student_id: int,

    db: Session = Depends(get_db)

):

    progress_records = (
        get_student_progress(
            db,
            student_id
        )
    )


    progress_data = []


    for record in progress_records:

        progress_data.append({

            "id":
                record.id,

            "student_id":
                record.student_id,

            "skill":
                record.skill,

            "status":
                record.status,

            "progress_percentage":
                record.progress_percentage,

            "notes":
                record.notes

        })


    return {

        "student_id":
            student_id,

        "progress":
            progress_data

    }


# =========================================================
# UPDATE LEARNING PROGRESS MANUALLY
# =========================================================

@app.put(
    "/progress/{student_id}/{skill}"
)
def update_learning_progress(

    student_id: int,

    skill: str,

    status: str,

    progress_percentage: float = 0,

    notes: str = None,

    db: Session = Depends(get_db)

):

    # -----------------------------------------------------
    # VALIDATE PROGRESS
    # -----------------------------------------------------

    if progress_percentage < 0:

        progress_percentage = 0


    if progress_percentage > 100:

        progress_percentage = 100


    # -----------------------------------------------------
    # SAVE PROGRESS
    # -----------------------------------------------------

    progress = save_progress(

        db=db,

        student_id=student_id,

        skill=skill,

        status=status,

        progress_percentage=(
            progress_percentage
        ),

        notes=notes

    )


    # -----------------------------------------------------
    # RETURN UPDATED DATA
    # -----------------------------------------------------

    return {

        "message":
            "Learning progress updated successfully.",

        "id":
            progress.id,

        "student_id":
            progress.student_id,

        "skill":
            progress.skill,

        "status":
            progress.status,

        "progress_percentage":
            progress.progress_percentage,

        "notes":
            progress.notes

    }

# =========================================================
# GET ASSESSMENT HISTORY
# =========================================================

@app.get("/assessment-history/{student_id}")
def get_assessment_history(
    student_id: int,
    db: Session = Depends(get_db)
):
    assessment_records = (
        db.query(AssessmentResult)
        .filter(AssessmentResult.student_id == student_id)
        .order_by(AssessmentResult.id.desc())
        .all()
    )

    return {
        "student_id": student_id,
        "assessment_history": [
            {
                "id": record.id,
                "skill": record.skill,
                "score": record.score,
                "correct_answers": record.correct_answers,
                "total_questions": record.total_questions,
                "proficiency": record.proficiency
            }
            for record in assessment_records
        ]
    }
