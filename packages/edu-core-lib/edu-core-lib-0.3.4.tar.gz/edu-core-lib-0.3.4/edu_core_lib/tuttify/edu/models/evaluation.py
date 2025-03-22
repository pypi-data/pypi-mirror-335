from typing import List, Optional

from pydantic import BaseModel


class EvaluationScheme(BaseModel):
    repr_name: str
    class_name: str

    class Config:
        schema_extra = {
            "example": {
                "repr_name": "base_scheme",
                "class_name": "BaseEvaluationScheme",
            }
        }


class WordsAnalyticsModel(BaseModel):
    length: int
    per_correct: Optional[float]
    mdn_t: Optional[float]
    result: str = "Not enough data"


class RecentWordModel(BaseModel):
    word: str
    mdn_t: Optional[float]
    Q1: Optional[float]
    Q2: Optional[float]
    Q3: Optional[float]


class SpellBeeAnalyticsModel(BaseModel):
    words_analytics: List[WordsAnalyticsModel]
    recent_words: List[RecentWordModel]
