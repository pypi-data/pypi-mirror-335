from pydantic import BaseModel
from typing import List
from phi_utils.models.saves import SingleScore

class BN(BaseModel):
    '''
    pN 为 AP 单曲成绩列表
    bN 为 进b 单曲成绩列表(不含pN)
    oN 为 其他 单曲成绩列表
    '''
    pN: List[SingleScore]
    bN: List[SingleScore]
    oN: List[SingleScore]