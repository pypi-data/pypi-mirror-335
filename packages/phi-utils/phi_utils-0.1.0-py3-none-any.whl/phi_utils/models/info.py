from pydantic import BaseModel
from typing import List, Dict
from phi_utils._utils.settings import DIFFICULTY_LEVEL_TYPE

class SingleSongINFO(BaseModel):
    id: str
    name: str
    composer: str
    illustrator: str
    chart: List[Dict[DIFFICULTY_LEVEL_TYPE,str]]

class SongINFO(BaseModel):
    list: List[SingleSongINFO]