import json
from writeup.core.models import Feedback

def save_report_as_json(feedback: Feedback, position: str, seniority: str, output: str) -> None:
    report = {
        "score": feedback.score,
        "years_experience": feedback.years_experience,
        "summary": feedback.summary,
        "relevant_skills": feedback.relevant_skills,
        "other_skills": feedback.other_skills,
        "pros": feedback.pros,
        "cons": feedback.cons,
        "position": position,
        "seniority": seniority
    }
    with open(output, "w") as f:
        json.dump(report, f, indent=4)

def save_batch_report_as_json(reports: list, output: str) -> None:
    with open(output, "w") as f:
        json.dump(reports, f, indent=4)
