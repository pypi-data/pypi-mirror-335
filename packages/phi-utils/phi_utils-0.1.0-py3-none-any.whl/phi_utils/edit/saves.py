from phi_utils.models.saves import SingleScore, GameSaves
from phi_utils.models.difficulty import Difficulty
from phi_utils.models.info import SongINFO
from copy import deepcopy

def update_song_list_difficulty(
    game_saves: GameSaves,
    difficultys: Difficulty,
) -> GameSaves:
    """
    更新存档打歌定数
    
    参数:
        game_saves (GameSaves): 存档数据，包含已有的打歌记录
        difficultys (Difficulty): 难度定数，包含歌曲ID和各难度级别的定数
    
    返回:
        GameSaves: 更新后的存档数据，包含补全后的歌曲难度   
    """
    # 获取当前存档的单曲数据
    song_list = game_saves.song_list
    
    # 遍历所有的难度定数，检查是否需要更新存档中的歌曲难度
    for difficulty in difficultys.list:
        for level_dict in difficulty.list:
            for level, diff_value in level_dict.items():
                # 遍历存档中的每首歌，检查是否有相同的 id 和 level
                for song in song_list:
                    if song.id == difficulty.id and song.level == level:
                        # 如果难度不同，更新该歌曲的难度
                        song.difficulty = diff_value
    
    # 返回更新后的存档数据
    return GameSaves(game_key=game_saves.game_key, song_list=song_list)

def complete_song_list(
    game_saves: GameSaves,
    difficultys: Difficulty,
    song_info: SongINFO
) -> GameSaves:
    """
    补全存档打歌数据

    参数:
        game_saves (GameSaves): 存档数据，包含已有的打歌记录
        difficultys (Difficulty): 难度定数，包含歌曲ID和各难度级别的定数
        song_info (SongINFO): 曲目信息，包含歌曲的ID和名称等

    返回:
        GameSaves: 新的存档对象，包含补全后的打歌数据
    """
    # 深拷贝 song_list，避免修改原始数据
    song_list = deepcopy(game_saves.song_list)

    # 补全存档
    for song_difficulty in difficultys.list:
        # 查找对应的歌曲信息
        song_info_item = next(
            (song for song in song_info.list if song.id == song_difficulty.id),
            None
        )
        # 如果找到歌曲信息，使用其名称；否则使用默认值
        song_name = song_info_item.name if song_info_item else "Unknown"

        for level_dict in song_difficulty.list:
            for level, diff_value in level_dict.items():
                # 检查是否已存在该歌曲和难度的记录
                if not any(song.id == song_difficulty.id and song.level == level for song in song_list):
                    new_score = SingleScore(
                        score=0,
                        acc=0.0,
                        fc=False,
                        level=level,
                        id=song_difficulty.id,
                        name=song_name,  # 使用从 song_info 提取的名称
                        difficulty=diff_value
                    )
                    song_list.append(new_score)

    # 返回新的 GameSaves 对象
    return GameSaves(game_key=game_saves.game_key, song_list=song_list)
