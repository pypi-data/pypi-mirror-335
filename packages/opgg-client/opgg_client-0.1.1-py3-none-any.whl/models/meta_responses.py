from typing import Optional

from pydantic import BaseModel

from models.base_model import BaseResponse


class SeasonModel(BaseModel):
    id: int
    value: int
    display_value: int
    split: Optional[int] = None
    is_preseason: bool


class SeasonAPIResponce(BaseResponse):
    data: list[SeasonModel]


class GameTypeModel(BaseModel):
    game_type: str
    game_translate: str


class GameTypeAPIResponse(BaseResponse):
    data: list[GameTypeModel]


class TierModel(BaseModel):
    name: str
    tier_image_url: str
    border_image_url: str
    tier_mini_image_url: str


class TierAPIResponse(BaseResponse):
    data: list[TierModel]
