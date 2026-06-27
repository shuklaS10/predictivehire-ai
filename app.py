from flask import Flask, jsonify, redirect, render_template, request, url_for
import re

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import docx
except ImportError:
    docx = None


app = Flask(__name__, static_folder="Static", template_folder="templates")

PASS_THRESHOLD = 75


JOB_ROLES = {
    "Python Developer": [
        "Python",
        "Django",
        "Flask",
        "REST API",
        "SQL",
        "Git",
        "Data Structures",
        "Algorithms",
        "HTML",
        "CSS",
    ],
    "AI Engineer": [
        "Python",
        "Machine Learning",
        "Deep Learning",
        "TensorFlow",
        "PyTorch",
        "NLP",
        "Computer Vision",
        "Data Structures",
        "Algorithms",
    ],
    "Data Scientist": [
        "Python",
        "Statistics",
        "Pandas",
        "NumPy",
        "Machine Learning",
        "SQL",
        "Data Visualization",
        "Tableau",
        "Power BI",
    ],
    "UI/UX Designer": [
        "UI Design",
        "UX Design",
        "Figma",
        "Wireframing",
        "Prototyping",
        "User Research",
        "Usability Testing",
        "Design Systems",
        "Accessibility",
        "HTML",
        "CSS",
    ],
}


LEARNING_LINKS = {
    "Python": "https://www.w3schools.com/python/",
    "Django": "https://docs.djangoproject.com/",
    "Flask": "https://flask.palletsprojects.com/",
    "REST API": "https://www.redhat.com/en/topics/api/what-is-a-rest-api",
    "SQL": "https://www.sqltutorial.org/",
    "Git": "https://git-scm.com/doc",
    "Machine Learning": "https://www.coursera.org/learn/machine-learning",
    "TensorFlow": "https://www.tensorflow.org/tutorials",
    "PyTorch": "https://pytorch.org/tutorials/",
    "Figma": "https://www.figma.com/learn/",
    "UX Design": "https://www.interaction-design.org",
    "HTML": "https://www.w3schools.com/html/",
    "CSS": "https://www.w3schools.com/css/",
}


def normalize_text(text):
    return re.sub(r"\s+", " ", text or "").strip()


def extract_pdf_text(file):
    if PyPDF2 is None:
        return ""

    reader = PyPDF2.PdfReader(file)
    pages = []

    for page in reader.pages:
        pages.append(page.extract_text() or "")

    return " ".join(pages)


def extract_docx_text(file):
    if docx is None:
        return ""

    document = docx.Document(file)
    return " ".join(paragraph.text for paragraph in document.paragraphs)


def extract_text(file):
    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        return extract_pdf_text(file)

    if filename.endswith(".docx"):
        return extract_docx_text(file)

    if filename.endswith(".txt"):
        return file.read().decode("utf-8", errors="ignore")

    return ""


def find_skills(text, required_skills):
    text = normalize_text(text)
    found_skills = []

    for skill in required_skills:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text, re.IGNORECASE):
            found_skills.append(skill)

    return found_skills


def calculate_score(found_skills, required_skills):
    if not required_skills:
        return 0

    return int((len(found_skills) / len(required_skills)) * 100)


def roadmap_for_role(role):
    if role == "Python Developer":
        return "https://roadmap.sh/python"

    if role in ("AI Engineer", "Data Scientist"):
        return "https://roadmap.sh/ai-data-scientist"

    return "https://roadmap.sh"


@app.route("/")
def home():
    return render_template("index.html", roles=JOB_ROLES.keys())


@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    if request.method == "GET":
        return redirect(url_for("home"))

    resume = request.files.get("resume")
    role = request.form.get("job_role")
    job_description = request.form.get("job_description", "")

    if resume is None or resume.filename == "":
        return render_template(
            "index.html",
            roles=JOB_ROLES.keys(),
            error="Please upload a resume file.",
        )

    if role not in JOB_ROLES:
        return render_template(
            "index.html",
            roles=JOB_ROLES.keys(),
            error="Please select a valid job role.",
        )

    resume_text = extract_text(resume)

    if not resume_text:
        return render_template(
            "index.html",
            roles=JOB_ROLES.keys(),
            error="Please upload a readable PDF, DOCX, or TXT resume. Install PyPDF2 and python-docx if needed.",
        )

    required_skills = JOB_ROLES[role]
    candidate_skills = find_skills(resume_text, required_skills)
    job_description_skills = find_skills(job_description, required_skills)
    missing_skills = [
        skill for skill in required_skills
        if skill not in candidate_skills
    ]

    score = calculate_score(candidate_skills, required_skills)
    jd_focus = job_description_skills if job_description_skills else required_skills
    job_match_score = calculate_score(
        list(set(candidate_skills) & set(jd_focus)),
        jd_focus,
    )

    return render_template(
        "results.html",
        role=role,
        score=score,
        job_match_score=job_match_score,
        candidate_skills=candidate_skills,
        missing_skills=missing_skills,
        links=LEARNING_LINKS,
        roadmap=roadmap_for_role(role),
    )


@app.route("/finalize", methods=["POST"])
def finalize():
    data = request.get_json(silent=True) or {}
    role = data.get("role", "Python Developer")
    mcq_score_raw = data.get("score", 0)
    resume_score = data.get("resume_score", 82)

    try:
        mcq_score_raw = float(mcq_score_raw)
        resume_score = float(resume_score)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid score data."}), 400

    mcq_percentage = (mcq_score_raw / 5) * 100
    final_score = (resume_score * 0.8) + (mcq_percentage * 0.2)
    is_selected = final_score >= PASS_THRESHOLD

    if is_selected:
        feedback = "Congratulations! Your technical profile and quick-thinking skills align with our requirements."
    elif mcq_percentage < 60:
        feedback = "Your resume is strong, but you struggled with the rapid-fire technical assessment."
    else:
        feedback = "The technical assessment was good, but we suggest adding more project-specific keywords to your resume."

    return jsonify({
        "status": "Selected" if is_selected else "Not Selected",
        "final_score": round(final_score, 2),
        "feedback": feedback,
        "roadmap": roadmap_for_role(role),
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
