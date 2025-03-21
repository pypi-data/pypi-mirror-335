from typing import Optional

from pydantic import BaseModel

from opgg.models.base_model import BaseResponse


class EvolveItem(BaseModel):
    key: str
    name: str
    image_url: str


class Info(BaseModel):
    attack: float
    defense: float
    magic: float
    difficulty: float


class Stats(BaseModel):
    hp: float
    hpperlevel: float
    mp: float
    mpperlevel: float
    movespeed: float
    armor: float
    armorperlevel: float
    spellblock: float
    spellblockperlevel: float
    attackrange: float
    hpregen: float
    hpregenperlevel: float
    mpregen: float
    mpregenperlevel: float
    crit: float
    critperlevel: float
    attackdamage: float
    attackdamageperlevel: float
    attackspeed: float
    attackspeedperlevel: float


class Price(BaseModel):
    currency: str
    cost: float


class Sale(BaseModel):
    currency: str
    cost: float
    discount_rate: float
    started_at: str
    ended_at: str


class Skin(BaseModel):
    id: float
    champion_id: float
    name: str
    has_chromas: bool
    splash_image: str
    loading_image: str
    tiles_image: str
    centered_image: str
    skin_video_url: Optional[str] = None
    prices: Optional[list[Price]] = None
    sales: Optional[list[Sale]] = None
    release_date: Optional[str] = None


class Passive(BaseModel):
    name: str
    description: str
    image_url: str
    video_url: Optional[str] = None


class Spell(BaseModel):
    key: str
    name: str
    description: str
    max_rank: float
    range_burn: list[float]
    cooldown_burn: list[float]
    cooldown_burn_float: list[float]
    cost_burn: list[float]
    tooltip: str
    image_url: str
    video_url: Optional[str] = None


class Champion(BaseModel):
    id: int
    key: str
    name: str
    image_url: str
    evolve: list[EvolveItem]
    blurb: str
    title: str
    tags: list[str]
    lore: str
    partype: str
    info: Info
    stats: Stats
    enemy_tips: list[str]
    ally_tips: list[str]
    skins: list[Skin]
    passive: Passive
    spells: list[Spell]


class ChampionAPIResponce(BaseResponse):
    data: list[Champion]
