from typing import Optional

from pydantic import BaseModel


class ChampionStat(BaseModel):
    id: int
    play: int
    win: int
    lose: int
    game_length_second: Optional[int] = None
    kill: int
    death: int
    assist: int
    gold_earned: int
    minion_kill: int
    neutral_minion_kill: int
    damage_taken: int
    damage_dealt_to_champions: Optional[int]
    double_kill: int
    triple_kill: int
    quadra_kill: int
    penta_kill: int
    vision_wards_bought_in_game: Optional[int]
    op_score: Optional[int]
    snowball_throws: Optional[int]
    snowball_hits: Optional[int]


class Data(BaseModel):
    game_type: str
    season_id: int
    year: Optional[int]
    play: int
    win: int
    lose: int
    champion_stats: list[ChampionStat]


class SummonerChampStatsAPIResponce(BaseModel):
    data: Data


class SummonerChampStatsAPIEmptyResponce(BaseModel):
    data: list[None]
