import logging
from pathlib import Path
from writeup.core.models import Feedback
from google.genai import types
from datetime import date
from dateutil.relativedelta import relativedelta  # pip install python-dateutil if needed

logger = logging.getLogger(__name__)

def generate_system_instruction(position: str, seniority: str) -> str:
    """
    Generate a refined system instruction for evaluating candidate CVs that includes:
      - Detailed guidance for interpreting seniority and role-specific matching.
      - Use of a future reference date for experience calculation.
      - Strict penalties for any deviation in specialization.
      - Filtering of skills so that only those used in the target role are considered relevant.
      - A deterministic evaluation process that produces consistent outputs.
    """
    from datetime import date
    from dateutil.relativedelta import relativedelta
    # Set a reference date two months into the future.
    future_date = date.today() + relativedelta(months=2)
    future_date_str = future_date.strftime("%B %Y")
    
    instruction = (
        "Instruction:\n"
        "Role: You are an advanced, neutral, and objective CV evaluator. Your evaluation must be fully deterministic so that "
        "running the same CV with these instructions always yields the same output. Use your chain-of-thought reasoning internally "
        "to ensure consistency and accuracy.\n\n"
        f"Task: Evaluate the candidate for a {seniority} {position} role based solely on the qualifications and experience in the CV.\n\n"
        "Guidelines:\n"
        "1. Experience Calculation:\n"
        f"   - Calculate the candidate's years of relevant experience as of {future_date_str}.\n\n"
        "2. Role-Specific Evaluation & Picky Matching:\n"
        "   - Check if the candidate's primary specialization exactly matches the target role. If there is any deviation, "
        "apply a severe penalty by reducing the role-specific skill match score to at most 10-20% of its computed value. "
        "Such a mismatch should result in an overall score typically below 4 on a 0–10 scale, regardless of strengths in other areas.\n\n"
        "3. Relevant Skills Filtering:\n"
        "   - Identify and include only those skills in the 'relevant_skills' list that are explicitly and exclusively used in the target role. "
        "All other skills must be placed in the 'other_skills' list.\n\n"
        "4. Seniority Derivation:\n"
        "   - Derive the candidate's seniority from a combination of their years of relevant experience and how well their background "
        "matches the specific requirements of the target role. A strong position-specific evaluation should support the expected seniority level, "
        "while a poor match should lower it accordingly.\n\n"
        "5. Point Allocation and Weighting:\n"
        "   - Break down the evaluation into the following components, each scored from 0 to 100:\n"
        "       a. Role-Specific Skill Match and Relevance – Suggested weight: 60%\n"
        "       b. Seniority Alignment (based on experience and role-specific evaluation) – Suggested weight: 30%\n"
        "       c. Overall CV Quality and Presentation – Suggested weight: 10%\n"
        "   - Before computing the weighted average, if the candidate’s specialization does not exactly match the target role, apply the penalty "
        "to the role-specific component. Convert the final weighted percentage to a score on a 0–10 scale.\n\n"
        "6. Consistency and Determinism:\n"
        "   - Ensure that your evaluation process is fully deterministic. Running the same CV with these instructions must always yield the same output.\n\n"
        "7. Internal Chain-of-Thought (Do NOT include in final output):\n"
        "   a. Calculate the candidate's years of experience as of the reference date.\n"
        "   b. Evaluate if the candidate’s specialization is an exact match with the target role.\n"
        "   c. Filter and classify skills strictly into 'relevant_skills' (used in the target role) and 'other_skills'.\n"
        "   d. Derive seniority based on experience and the position-specific evaluation.\n"
        "   e. Apply a severe penalty to the role-specific score if any specialization mismatch is detected.\n"
        "   f. Compute the weighted score and convert it to a final score on a 0–10 scale.\n\n"
        "Final Output:\n"
        "Return only a JSON object that strictly follows this schema (exclude any internal reasoning):\n"
        "{\n"
        '  "score": float,          // Final score on a 0–10 scale\n'
        '  "summary": string,       // Concise summary of your evaluation\n'
        '  "relevant_skills": list, // Key skills directly matching the target role\n'
        '  "other_skills": list,    // Additional skills not directly relevant\n'
        '  "pros": list,            // Strengths of the candidate\n'
        '  "cons": list,            // Weaknesses of the candidate\n'
        '  "years_experience": int  // Total years of relevant experience as of the reference date\n'
        "}\n\n"
        "Note: The evaluation must be extremely picky about role matching, include only exactly relevant skills, "
        "and produce consistent outputs if re-run."
    )
    return instruction


def evaluate_cv(filepath: Path, position: str, seniority: str, client) -> Feedback:
    system_instruction = generate_system_instruction(position, seniority)
    try:
        response = client.models.generate_content(
            config={
                'response_mime_type': 'application/json',
                'response_schema': Feedback,
            },
            model="gemini-2.0-flash",
            contents=[
                system_instruction,
                types.Part.from_bytes(
                    data=filepath.read_bytes(),
                    mime_type='application/pdf',
                ),
            ]
        )
        return response.parsed
    except Exception as e:
        logger.error(f"Error during API call for {filepath.name}: {e}")
        raise

def evaluate_cv_batch(directory: Path, position: str, seniority: str, client) -> list:
    reports = []
    for pdf_file in directory.glob("*.pdf"):
        try:
            response = client.models.generate_content(
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': Feedback,
                },
                model="gemini-2.0-flash",
                contents=[
                    generate_system_instruction(position, seniority),
                    types.Part.from_bytes(
                        data=pdf_file.read_bytes(),
                        mime_type='application/pdf',
                    ),
                    "max 25 words summary"
                ]
            )
            feedback = response.parsed
            reports.append({
                "file": pdf_file.name,
                "score": feedback.score,
                "years_experience": feedback.years_experience,
                "summary": feedback.summary,
                "relevant_skills": feedback.relevant_skills,
            })
        except Exception as e:
            logger.error(f"Error evaluating {pdf_file.name}: {e}")
    if not reports:
        raise Exception("No CVs were successfully evaluated.")
    return sorted(reports, key=lambda r: r["score"], reverse=True)
