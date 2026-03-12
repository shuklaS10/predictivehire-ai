from flask import Flask, render_template, request
import PyPDF2
import docx
import re

app = Flask(__name__)

# ---------------- JOB ROLES CONFIG ---------------- #

JOB_ROLES = {
    "UI/UX Designer": {
        "skills": [
            "UI Design", "UX Design", "Figma", "Wireframing",
            "Prototyping", "User Research", "Usability Testing",
            "Design Systems", "Accessibility", "HTML", "CSS"
        ]
    },
    "AI Engineer": {
        "skills": [
            "Python", "Machine Learning", "Deep Learning",
            "TensorFlow", "PyTorch", "NLP",
            "Computer Vision", "Data Structures", "Algorithms"
        ]
    },
    "Data Scientist": {
        "skills": [
            "Python", "Statistics", "Pandas", "NumPy",
            "Machine Learning", "SQL",
            "Data Visualization", "Tableau", "Power BI"
        ]
    },
    "iOS Developer": {
        "skills": [
            "Swift", "iOS", "Xcode", "UIKit",
            "SwiftUI", "REST API", "Git", "MVC"
        ]
    }
}

LEARNING_LINKS = {
    "Python": "https://www.w3schools.com/python/",
    "Machine Learning": "https://www.coursera.org/learn/machine-learning",
    "Figma": "https://www.figma.com/learn/",
    "UX Design": "https://www.interaction-design.org",
    "Swift": "https://developer.apple.com/swift/",
    "SQL": "https://www.sqltutorial.org/",
    "TensorFlow": "https://www.tensorflow.org/tutorials",
    "HTML": "https://www.w3schools.com/html/",
    "CSS": "https://www.w3schools.com/css/"
}

# ---------------- HELPERS ---------------- #

def extract_text(file):
    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        return " ".join([page.extract_text() or "" for page in reader.pages])

    elif filename.endswith(".docx"):
        doc = docx.Document(file)
        return " ".join([p.text for p in doc.paragraphs])

    else:
        return file.read().decode("utf-8", errors="ignore")


def find_skills(text, skills):
    found = []
    for skill in skills:
        if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE):
            found.append(skill)
    return found


# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return render_template("index.html", roles=JOB_ROLES.keys())


@app.route("/analyze", methods=["POST"])
def analyze():
    resume = request.files["resume"]
    role = request.form["job_role"]
    job_description = request.form["job_description"]

    resume_text = extract_text(resume)

    required_skills = JOB_ROLES[role]["skills"]
    candidate_skills = find_skills(resume_text, required_skills)
    missing_skills = list(set(required_skills) - set(candidate_skills))

    score = int((len(candidate_skills) / len(required_skills)) * 100)

    return render_template(
        "results.html",
        role=role,
        score=score,
        candidate_skills=candidate_skills,
        missing_skills=missing_skills,
        links=LEARNING_LINKS
    )


if __name__ == "__main__":
    app.run(debug=True)