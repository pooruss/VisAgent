from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    score: int
    is_pass: bool
    reason: str

    def to_json(self) -> dict:
        return {
            "score": self.score,
            "is_pass": self.is_pass,
            "reason": self.reason
        }

    def __str__(self):
        return str(self.is_pass)