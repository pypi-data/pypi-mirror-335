from pydantic import BaseModel
from typing import List
from phi_utils._utils.settings import DIFFICULTY_LEVEL_TYPE

class GameKeyItem(BaseModel):
    id: str
    type: List[bool]
    flag: List[bool]

class BaseSingleScore(BaseModel):
    '''
    基本单曲成绩
    
    score 为 单曲分数
    acc 为 单曲准度
    fc 为 单曲是否全连
    '''
    score: int
    acc: float
    fc: bool
    
class SingleScore(BaseSingleScore, BaseModel):
    '''
    完全单曲成绩
    
    name 为 单曲名称
    id 为 单曲id
    score 为 单曲分数
    acc 为 单曲准度
    fc 为 单曲是否全连
    difficulty 为 单曲难度定数
    level 为 单曲难度等级
    rks 为 单曲rks（通过 acc 和 difficulty 计算得出）
    '''
    id: str
    name: str
    difficulty: float
    level: DIFFICULTY_LEVEL_TYPE

    @property
    def rks(self):
        # 如果 acc 小于 70，rks 为 0
        if self.acc < 70:
            return 0.00
        # 否则计算 rks
        return ((self.acc - 55) / 45) ** 2 * self.difficulty
    
    class Config:
        # 允许将 property 转换为 JSON 字段
        json_encoders = {
            property: lambda v: v() if callable(v) else v
        }

class GameKey(BaseModel):
    key_list: List[GameKeyItem]

class GameSaves(BaseModel):
    game_key: GameKey
    song_list: List[SingleScore]
