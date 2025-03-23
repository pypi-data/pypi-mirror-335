from pydantic import BaseModel

class Feedback(BaseModel):
    score: float
    summary: str
    relevant_skills: list[str]
    other_skills: list[str]
    pros: list[str]
    cons: list[str]
    years_experience: int
