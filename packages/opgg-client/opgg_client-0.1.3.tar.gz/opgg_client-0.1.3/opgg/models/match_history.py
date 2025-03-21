from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import AnyUrl, BaseModel

from opgg.models.base_model import BaseResponse
from opgg.models.shared import Key, Position, Result, Role, Tier


class Rune(BaseModel):
    primary_page_id: int
    primary_rune_id: int
    secondary_page_id: int


class ChampionTemp(BaseModel):
    id: int
    key: str


class OpScoreTimeline(BaseModel):
    second: int
    score: float


class Summoner(BaseModel):
    id: int
    summoner_id: str
    acct_id: str
    puuid: str
    game_name: str
    tagline: str
    name: str
    internal_name: str
    profile_image_url: AnyUrl
    level: int
    updated_at: datetime
    renewable_at: datetime
    revision_at: Optional[datetime]
    player: Optional[Any]


class QueueInfo(BaseModel):
    id: int
    queue_translate: str
    game_type: str


class GameStat(BaseModel):
    is_win: bool
    champion_kill: int
    champion_first: bool
    inhibitor_kill: int
    inhibitor_first: bool
    rift_herald_kill: int
    rift_herald_first: bool
    dragon_kill: int
    dragon_first: bool
    baron_kill: int
    baron_first: bool
    tower_kill: int
    tower_first: bool
    horde_kill: int
    horde_first: bool
    is_remake: bool
    death: int
    assist: int
    gold_earned: int
    kill: int


class Last(Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    FAIR = "FAIR"
    POOR = "POOR"


class Left(Enum):
    DOWN = "DOWN"
    UP = "UP"


class AverageTierInfo(BaseModel):
    tier: Tier
    division: int
    tier_image_url: AnyUrl
    border_image_url: AnyUrl


class OpScoreTimelineAnalysis(BaseModel):
    left: Left
    right: Left
    last: Last


class TierInfo(BaseModel):
    tier: Optional[Tier]
    division: Optional[int]
    lp: Optional[int]
    level: Optional[int]
    tier_image_url: AnyUrl
    border_image_url: Optional[AnyUrl]


class Team(BaseModel):
    key: Key
    game_stat: GameStat
    banned_champions: list[Optional[int]]


class Stats(BaseModel):
    champion_level: int
    damage_self_mitigated: int
    damage_dealt_to_objectives: int
    damage_dealt_to_turrets: int
    magic_damage_dealt_player: int
    physical_damage_taken: int
    physical_damage_dealt_to_champions: int
    total_damage_taken: int
    total_damage_dealt: int
    total_damage_dealt_to_champions: int
    largest_critical_strike: int
    time_ccing_others: int
    vision_score: int
    vision_wards_bought_in_game: int
    sight_wards_bought_in_game: int
    ward_kill: int
    ward_place: int
    turret_kill: int
    barrack_kill: int
    kill: int
    death: int
    assist: int
    largest_multi_kill: int
    largest_killing_spree: int
    minion_kill: int
    neutral_minion_kill_team_jungle: None
    neutral_minion_kill_enemy_jungle: None
    neutral_minion_kill: int
    gold_earned: int
    total_heal: int
    result: Result
    op_score: float
    op_score_rank: int
    is_opscore_max_in_team: bool
    lane_score: Optional[int]
    op_score_timeline: list[OpScoreTimeline]
    op_score_timeline_analysis: Optional[OpScoreTimelineAnalysis]
    keyword: Optional[str]
    keyword_label_temp: Optional[str] = None
    keyword_desc_temp: Optional[str] = None
    champion_temp: Optional[ChampionTemp] = None


class MyData(BaseModel):
    summoner: Summoner
    participant_id: int
    champion_id: int
    team_key: Key
    position: Position
    role: Optional[Role]
    items: list[int]
    trinket_item: int
    rune: Rune
    spells: list[int]
    stats: Stats
    tier_info: TierInfo


class Game(BaseModel):
    id: str
    created_at: datetime
    game_map: str
    queue_info: Optional[QueueInfo] = None
    game_type: str
    version: str
    meta_version: str
    game_length_second: int
    is_remake: bool
    is_opscore_active: bool
    is_recorded: Optional[bool]
    record_info: Any
    average_tier_info: AverageTierInfo
    participants: list[MyData]
    teams: list[Team]
    memo: Any
    myData: MyData


class Meta(BaseModel):
    first_game_created_at: Optional[datetime]
    last_game_created_at: Optional[datetime]


class MatchHistoryAPIResponce(BaseResponse):
    data: Optional[list[Game]] = []
    meta: Meta
