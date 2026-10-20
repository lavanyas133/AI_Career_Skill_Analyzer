import streamlit as st
import requests
import networkx as nx
import plotly.graph_objects as go

from backend.engine.domain_database import (
    get_all_domains,
    get_all_roles,
    get_all_role_requirements
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Career Skill Twin",
    page_icon="🎯",
    layout="wide"
)


# =========================================================
# CUSTOM STYLING
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 45px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 18px;
        opacity: 0.8;
        margin-bottom: 30px;
    }

    .roadmap-step {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(128,128,128,0.3);
        margin-bottom: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# TITLE
# =========================================================

st.markdown(
    '<div class="main-title">🎯 AI Career Skill Twin</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Analyze your resume, discover your skill gaps, '
    'test your skills, and build a personalized career roadmap.'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# BACKEND
# =========================================================

BACKEND_URL = "http://127.0.0.1:8000"


# =========================================================
# SESSION STATE
# =========================================================

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "student_id" not in st.session_state:
    st.session_state.student_id = None

if "assessment_skill" not in st.session_state:
    st.session_state.assessment_skill = None

if "assessment_questions" not in st.session_state:
    st.session_state.assessment_questions = []

if "assessment_result" not in st.session_state:
    st.session_state.assessment_result = None


# =========================================================
# RESUME & CAREER TARGET
# =========================================================

st.header("📄 Resume & Career Target")

col1, col2 = st.columns(2)


with col1:

    uploaded_file = st.file_uploader(
        "Upload your resume",
        type=["pdf", "docx"]
    )


with col2:

    domain = st.selectbox(
    "🌐 Select your career domain",
    get_all_domains()
)

role = st.selectbox(
    "🎯 Select your target career role",
    get_all_roles(domain)
)


st.write("")


# =========================================================
# ANALYZE RESUME
# =========================================================

if st.button(
    "🚀 Analyze My Skills",
    use_container_width=True
):

    if uploaded_file is None:

        st.warning(
            "⚠️ Please upload your resume first."
        )

    else:

        with st.spinner(
            "🔍 Analyzing your resume..."
        ):

            try:

                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type
                    )
                }

                data = {
                    "role": role,
                    "domain": domain
            }

                if st.session_state.student_id is not None:
                    data["student_id"] = st.session_state.student_id

                response = requests.post(
                    f"{BACKEND_URL}/analyze",
                    files=files,
                    data=data
                )


                if response.status_code == 200:

                    result = response.json()

                    st.session_state.analysis_result = result

                    # Store database student ID
                    st.session_state.student_id = (
                        result.get("student_id")
                    )

                    # Reset assessment
                    st.session_state.assessment_skill = None
                    st.session_state.assessment_questions = []
                    st.session_state.assessment_result = None

                    st.success(
                        "🎉 Resume analysis completed successfully!"
                    )

                else:

                    st.error(
                        "❌ The backend returned an error."
                    )

                    st.code(
                        response.text
                    )


            except requests.exceptions.ConnectionError:

                st.error(
                    "❌ Cannot connect to the FastAPI backend."
                )

                st.info(
                    "Make sure the FastAPI server is running "
                    "on http://127.0.0.1:8000"
                )


            except Exception as e:

                st.error(
                    f"❌ An unexpected error occurred: {e}"
                )


# =========================================================
# DISPLAY ANALYSIS
# =========================================================

if st.session_state.analysis_result is not None:

    result = st.session_state.analysis_result


    # -----------------------------------------------------
    # GET DATA
    # -----------------------------------------------------

    career_role = result["career_role"]

    student_skills = result["student_skills"]

    required_skills = result["required_skills"]

    skills_you_have = result["skills_you_have"]

    skills_semantically_related = result.get(
        "skills_semantically_related",
        []
    )

    skills_missing = result["skills_missing"]

    minimum_skill_path = result.get(
        "minimum_skill_path",
        []
    )

    skill_evidence = result.get(
        "skill_evidence",
        {}
    )


    # =====================================================
    # MATCH PERCENTAGE
    # =====================================================

    total_skills = len(
        required_skills
    )

    matched_skills = len(
        skills_you_have
    )


    if total_skills > 0:

        match_percentage = (
            matched_skills / total_skills
        ) * 100

    else:

        match_percentage = 0


    # =====================================================
    # CAREER ANALYSIS
    # =====================================================

    st.header(
        "🎯 Career Analysis"
    )

    st.write(
        f"**Target Role:** {career_role}"
    )


    metric1, metric2, metric3 = st.columns(3)


    with metric1:

        st.metric(
            "Skills Matched",
            f"{matched_skills}/{total_skills}"
        )


    with metric2:

        st.metric(
            "Skills to Develop",
            len(skills_missing)
        )


    with metric3:

        st.metric(
            "Skill Match",
            f"{match_percentage:.0f}%"
        )


    st.write(
        "### 📊 Skill Match Progress"
    )

    st.progress(
        match_percentage / 100
    )


    st.write(
        f"You currently match "
        f"**{match_percentage:.0f}%** "
        f"of the skills listed for this career role."
    )


    st.divider()


    # =====================================================
    # SKILL GAP
    # =====================================================

    st.header(
        "🧠 Skill Gap Analysis"
    )

    col1, col2 = st.columns(2)


    with col1:

        st.subheader(
            "✅ Skills You Have"
        )

        if skills_you_have:

            for skill in skills_you_have:

                st.success(
                    f"✓ {skill}"
                )

        else:

            st.info(
                "No matching skills detected."
            )


    with col2:

        st.subheader(
            "⚠️ Skills to Develop"
        )

        if skills_missing:

            for skill in skills_missing:

                st.warning(
                    f"• {skill}"
                )

        else:

            st.success(
                "No skill gaps detected!"
            )


    # -----------------------------------------------------
    # SEMANTICALLY RELATED SKILLS
    # -----------------------------------------------------




    st.divider()


    # =====================================================
    # PRIORITY SKILLS
    # =====================================================

    st.header(
        "🔥 Priority Skills"
    )


    if skills_missing:

        st.write(
            "These skills are currently missing "
            "from the detected resume skills."
        )

        priority_skills = skills_missing[:3]


        for index, skill in enumerate(
            priority_skills,
            start=1
        ):

            st.info(
                f"Priority {index}: **{skill}**"
            )

    else:

        st.success(
            "🎉 No immediate skill gaps detected."
        )


    st.divider()


    # =====================================================
    # MINIMUM SKILL PATH
    # =====================================================

    st.header(
        "🗺️ Your Minimum Skill Path"
    )


    if minimum_skill_path:

        st.write(
            "Based on your current skills and the "
            "requirements of your target role, this "
            "is the suggested learning sequence."
        )


        for index, skill in enumerate(
            minimum_skill_path,
            start=1
        ):

            st.markdown(
                f"""
                <div class="roadmap-step">
                    <b>Step {index}</b>
                    → {skill}
                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        st.success(
            "🎉 No additional skills are currently required."
        )


    st.divider()


    # =====================================================
    # SKILL EVIDENCE
    # =====================================================

    st.header(
        "🔬 Skill Evidence"
    )


    st.write(
        "The system checks whether each detected skill "
        "has supporting evidence in the resume."
    )


    if skill_evidence:

        for skill, evidence_data in (
            skill_evidence.items()
        ):

            if evidence_data["demonstrated"]:

                st.success(
                    f"✅ {skill} — Demonstrated"
                )


                with st.expander(
                    f"View evidence for {skill}"
                ):

                    evidence_list = (
                        evidence_data.get(
                            "evidence",
                            []
                        )
                    )


                    for evidence in evidence_list:

                        st.write(
                            f"• {evidence}"
                        )

            else:

                st.warning(
                    f"⚠️ {skill} — "
                    f"Claimed but not demonstrated"
                )

    else:

        st.info(
            "No skill evidence available."
        )


    st.divider()


    # =====================================================
    # SKILL DEPENDENCY GRAPH
    # =====================================================

    st.header(
        "🕸️ Skill Dependency Graph"
    )


    st.write(
        "This graph shows how the skills required for "
        "your target career are connected through "
        "prerequisites."
    )


    try:

        graph_response = requests.get(
            f"{BACKEND_URL}/skill-graph/{career_role}"
        )


        if graph_response.status_code == 200:

            graph_result = graph_response.json()

            graph_data = graph_result["graph"]

            nodes = graph_data["nodes"]

            edges = graph_data["edges"]


            if nodes:

                graph = nx.DiGraph()

                graph.add_nodes_from(
                    nodes
                )


                for edge in edges:

                    graph.add_edge(
                        edge["source"],
                        edge["target"]
                    )


                positions = nx.spring_layout(
                    graph,
                    seed=42
                )


                edge_x = []
                edge_y = []


                for source, target in graph.edges():

                    x0, y0 = positions[source]

                    x1, y1 = positions[target]


                    edge_x.extend(
                        [x0, x1, None]
                    )

                    edge_y.extend(
                        [y0, y1, None]
                    )


                edge_trace = go.Scatter(
                    x=edge_x,
                    y=edge_y,
                    mode="lines",
                    hoverinfo="none"
                )


                node_x = []
                node_y = []
                node_text = []


                for node in graph.nodes():

                    x, y = positions[node]

                    node_x.append(x)

                    node_y.append(y)

                    node_text.append(node)


                node_trace = go.Scatter(
                    x=node_x,
                    y=node_y,
                    mode="markers+text",
                    text=node_text,
                    textposition="top center",
                    hoverinfo="text",
                    marker={
                        "size": 25
                    }
                )


                figure = go.Figure(
                    data=[
                        edge_trace,
                        node_trace
                    ]
                )


                figure.update_layout(
                    title="Career Skill Dependency Graph",
                    showlegend=False,
                    hovermode="closest",
                    margin=dict(
                        l=20,
                        r=20,
                        t=50,
                        b=20
                    ),
                    xaxis=dict(
                        showgrid=False,
                        zeroline=False,
                        showticklabels=False
                    ),
                    yaxis=dict(
                        showgrid=False,
                        zeroline=False,
                        showticklabels=False
                    )
                )


                st.plotly_chart(
                    figure,
                    use_container_width=True
                )


            else:

                st.info(
                    "No dependency graph is available."
                )


        else:

            st.warning(
                "Unable to load the skill dependency graph."
            )


    except requests.exceptions.ConnectionError:

        st.warning(
            "The dependency graph could not connect "
            "to the backend."
        )


    except Exception as e:

        st.warning(
            f"Unable to display dependency graph: {e}"
        )


    st.divider()


    # =====================================================
    # ADAPTIVE SKILL ASSESSMENT
    # =====================================================

    st.header(
        "🧪 Adaptive Skill Assessment"
    )


    st.write(
        "Test your knowledge of a skill detected as "
        "missing or needing development."
    )


    # -----------------------------------------------------
    # FIND AVAILABLE ASSESSMENTS
    # -----------------------------------------------------

    assessment_options = []


    for skill in skills_missing:

        try:

            check_response = requests.get(
                f"{BACKEND_URL}/assessment/{skill}"
            )


            if check_response.status_code == 200:

                check_data = check_response.json()


                if check_data.get("questions"):

                    assessment_options.append(
                        skill
                    )


        except Exception:

            pass


    # -----------------------------------------------------
    # ALSO CHECK STUDENT SKILLS
    # -----------------------------------------------------

    for skill in student_skills:

        if skill not in assessment_options:

            try:

                check_response = requests.get(
                    f"{BACKEND_URL}/assessment/{skill}"
                )


                if check_response.status_code == 200:

                    check_data = check_response.json()


                    if check_data.get("questions"):

                        assessment_options.append(
                            skill
                        )


            except Exception:

                pass


    # -----------------------------------------------------
    # SELECT SKILL
    # -----------------------------------------------------

    if assessment_options:

        selected_skill = st.selectbox(
            "🎯 Select a skill to assess",
            assessment_options
        )


        if st.button(
            "📝 Start Assessment",
            use_container_width=True
        ):

            try:

                assessment_response = requests.get(
                    f"{BACKEND_URL}/assessment/"
                    f"{selected_skill}"
                )


                if assessment_response.status_code == 200:

                    assessment_data = (
                        assessment_response.json()
                    )


                    questions = assessment_data.get(
                        "questions",
                        []
                    )


                    if questions:

                        st.session_state.assessment_skill = (
                            selected_skill
                        )

                        st.session_state.assessment_questions = (
                            questions
                        )

                        st.session_state.assessment_result = (
                            None
                        )

                        st.rerun()

                    else:

                        st.warning(
                            "No assessment is available "
                            "for this skill yet."
                        )


                else:

                    st.error(
                        "Unable to load the assessment."
                    )


            except requests.exceptions.ConnectionError:

                st.error(
                    "❌ Cannot connect to the backend."
                )


            except Exception as e:

                st.error(
                    f"❌ Error loading assessment: {e}"
                )


    else:

        st.info(
            "No assessment is currently available "
            "for the detected skills."
        )


    # =====================================================
    # ACTIVE ASSESSMENT
    # =====================================================

    if st.session_state.assessment_questions:

        assessment_skill = (
            st.session_state.assessment_skill
        )

        questions = (
            st.session_state.assessment_questions
        )


        st.divider()


        st.subheader(
            f"📝 {assessment_skill} Assessment"
        )


        st.write(
            f"Answer all {len(questions)} questions."
        )


        user_answers = []


        for index, question in enumerate(
            questions
        ):

            st.markdown(
                f"### Question {index + 1}"
            )

            st.write(
                question["question"]
            )

            selected_answer = st.radio(
                "Select your answer:",
                question["options"],
                index=None,
                key=(
                    f"{assessment_skill}_"
                    f"question_{index}"
                )
            )

            user_answers.append(
                selected_answer
            )

        # -------------------------------------------------
        # SUBMIT ASSESSMENT
        # -------------------------------------------------

        if st.button(
            "✅ Submit Assessment",
            use_container_width=True
        ):

            try:

                student_id = (
                    st.session_state.student_id
                )


                if student_id is None:

                    st.error(
                        "❌ Student profile not found. "
                        "Please analyze your resume again."
                    )

                else:

                    submit_response = requests.post(
                        f"{BACKEND_URL}/assessment/"
                        f"{assessment_skill}/submit",
                        params={
                            "student_id": student_id
                        },
                        json=user_answers
                    )


                    if submit_response.status_code == 200:

                        assessment_result = (
                            submit_response.json()
                        )


                        st.session_state.assessment_result = (
                            assessment_result
                        )


                        st.rerun()


                    else:

                        st.error(
                            "❌ Unable to submit assessment."
                        )


                        st.code(
                            submit_response.text
                        )


            except requests.exceptions.ConnectionError:

                st.error(
                    "❌ Cannot connect to the backend."
                )


            except Exception as e:

                st.error(
                    f"❌ Error submitting assessment: {e}"
                )


    # =====================================================
    # ASSESSMENT RESULT
    # =====================================================

    if st.session_state.assessment_result:

        assessment_result = (
            st.session_state.assessment_result
        )


        st.divider()


        st.subheader(
            "📊 Assessment Result"
        )


        result_col1, result_col2, result_col3 = (
            st.columns(3)
        )


        with result_col1:

            st.metric(
                "Score",
                f"{assessment_result['score']:.0f}%"
            )


        with result_col2:

            st.metric(
                "Correct Answers",
                f"{assessment_result['correct_answers']}/"
                f"{assessment_result['total_questions']}"
            )


        with result_col3:

            st.metric(
                "Proficiency",
                assessment_result["level"]
            )


        level = assessment_result["level"]


        if level == "Advanced":

            st.success(
                "🏆 Excellent! You demonstrated "
                "strong knowledge of this skill."
            )


        elif level == "Intermediate":

            st.info(
                "👍 Good progress! You have a "
                "reasonable understanding of this skill."
            )


        elif level == "Beginner":

            st.warning(
                "📚 You have some understanding, "
                "but more practice is recommended."
            )


        else:

            st.error(
                "📖 This skill needs more preparation. "
                "Consider learning the fundamentals first."
            )


    st.divider()


    # =====================================================
    # ALL DETECTED RESUME SKILLS
    # =====================================================

    st.header(
        "🔎 All Detected Resume Skills"
    )


    if student_skills:

        with st.expander(
            "View all detected skills"
        ):

            for skill in student_skills:

                st.write(
                    f"• {skill}"
                )

    else:

        st.info(
            "No skills were detected."
        )


    # =====================================================
    # REQUIRED SKILLS
    # =====================================================

    with st.expander(
        "📋 View All Skills Required for This Role"
    ):

        for skill in required_skills:

            if skill in skills_you_have:

                st.write(
                    f"✅ {skill}"
                )

            else:

                st.write(
                    f"⚠️ {skill}"
                )


# =========================================================
# STUDENT PROGRESS DASHBOARD
# =========================================================

if st.session_state.student_id is not None:

    st.divider()
    st.header("📈 Student Progress Dashboard")

    student_id = st.session_state.student_id


    try:
        progress_response = requests.get(
            f"{BACKEND_URL}/progress/{student_id}",
            timeout=10
        )

        history_response = requests.get(
            f"{BACKEND_URL}/assessment-history/{student_id}",
            timeout=10
        )

        if progress_response.status_code == 200:
            progress_records = progress_response.json().get(
                "progress", []
            )
        else:
            progress_records = []
            st.warning("Unable to load learning progress.")

        if history_response.status_code == 200:
            assessment_records = history_response.json().get(
                "assessment_history", []
            )
        else:
            assessment_records = []
            st.warning("Unable to load assessment history.")

        # Learning progress metrics
        st.subheader("📚 Learning Progress")

        total_skills = len(progress_records)
        completed_skills = sum(
            1 for item in progress_records
            if item.get("status", "").lower() == "completed"
        )

        average_progress = (
            sum(
                float(item.get("progress_percentage") or 0)
                for item in progress_records
            ) / total_skills
            if total_skills else 0
        )

        col1, col2, col3 = st.columns(3)

        col1.metric("Tracked Skills", total_skills)
        col2.metric("Completed Skills", completed_skills)
        col3.metric("Average Progress", f"{average_progress:.0f}%")

        if progress_records:
            progress_df = __import__("pandas").DataFrame(
                progress_records
            )

            st.dataframe(
                progress_df[
                    [
                        "skill",
                        "status",
                        "progress_percentage",
                        "notes"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

            st.subheader("Progress by Skill")

            progress_chart = go.Figure(
                data=[
                    go.Bar(
                        x=progress_df["skill"],
                        y=progress_df["progress_percentage"],
                        text=progress_df["progress_percentage"],
                        textposition="auto"
                    )
                ]
            )

            progress_chart.update_layout(
                xaxis_title="Skill",
                yaxis_title="Progress (%)",
                yaxis_range=[0, 100]
            )

            st.plotly_chart(
                progress_chart,
                use_container_width=True
            )
        else:
            st.info(
                "No learning progress saved yet. "
                "Analyze a resume or complete an assessment "
                "to start tracking your progress."
            )

        # Manually update learning progress
        if progress_records:
            st.subheader("✏️ Update Learning Progress")

            progress_by_skill = {
                item["skill"]: item
                for item in progress_records
            }

            selected_skill = st.selectbox(
                "Choose a skill",
                options=list(progress_by_skill.keys()),
                key="progress_edit_skill"
            )

            selected_record = progress_by_skill[selected_skill]

            status_options = [
                "Not Started",
                "In Progress",
                "Completed"
            ]

            current_status = selected_record.get(
                "status", "Not Started"
            )

            if current_status not in status_options:
                current_status = "In Progress"

            updated_status = st.selectbox(
                "Learning status",
                status_options,
                index=status_options.index(current_status),
                key=f"progress_status_{selected_skill}"
            )

            updated_percentage = st.slider(
                "Progress percentage",
                min_value=0,
                max_value=100,
                value=max(
                    0,
                    min(
                        100,
                        int(
                            selected_record.get(
                                "progress_percentage", 0
                            ) or 0
                        )
                    )
                ),
                key=f"progress_percent_{selected_skill}"
            )

            updated_notes = st.text_area(
                "Notes (optional)",
                value=selected_record.get("notes") or "",
                key=f"progress_notes_{selected_skill}"
            )

            if st.button("Save Progress"):
                try:
                    update_response = requests.put(
                        f"{BACKEND_URL}/progress/"
                        f"{student_id}/{selected_skill}",
                        params={
                            "status": updated_status,
                            "progress_percentage": updated_percentage,
                            "notes": updated_notes
                        },
                        timeout=10
                    )

                    if update_response.status_code == 200:
                        st.success("Learning progress saved!")
                        st.rerun()
                    else:
                        st.error(
                            "Could not save progress: "
                            f"{update_response.text}"
                        )

                except requests.exceptions.RequestException as error:
                    st.error(
                        f"Unable to save progress: {error}"
                    )

        # Assessment history
        # Assessment history
        st.subheader("🧪 Assessment History")

        if assessment_records:
            history_df = __import__("pandas").DataFrame(
                assessment_records
            )

            st.dataframe(
                history_df[
                    [
                        "skill",
                        "score",
                        "correct_answers",
                        "total_questions",
                        "proficiency"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

            st.subheader("Assessment Scores")

            score_chart = go.Figure(
                data=[
                    go.Bar(
                        x=history_df["skill"],
                        y=history_df["score"],
                        text=history_df["score"],
                        textposition="auto"
                    )
                ]
            )

            score_chart.update_layout(
                xaxis_title="Skill",
                yaxis_title="Score (%)",
                yaxis_range=[0, 100]
            )

            st.plotly_chart(
                score_chart,
                use_container_width=True
            )
        else:
            st.info(
                "No assessment history yet. Complete and submit "
                "a skill assessment to see your saved results here."
            )

    except requests.exceptions.ConnectionError:
        st.error(
            "Cannot connect to the backend. "
            "Make sure FastAPI is running."
        )

    except requests.exceptions.RequestException as error:
        st.error(f"Unable to load dashboard data: {error}")
