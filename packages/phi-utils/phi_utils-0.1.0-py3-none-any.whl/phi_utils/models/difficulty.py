from pydantic import BaseModel
from typing import List, Dict
from phi_utils._utils.settings import DIFFICULTY_LEVEL_TYPE

class SingleDifficulty(BaseModel):
    id: str
    list: List[Dict[DIFFICULTY_LEVEL_TYPE,float]]

class Difficulty(BaseModel):
    list: List[SingleDifficulty]
