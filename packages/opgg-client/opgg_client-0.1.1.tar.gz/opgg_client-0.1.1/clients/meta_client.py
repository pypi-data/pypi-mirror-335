from clients.base_client import BaseAPIClient
from models.meta_responses import (
    GameTypeAPIResponse,
    SeasonAPIResponce,
    TierAPIResponse,
)


class OPGGMetaClient(BaseAPIClient):
    def __init__(self) -> None:
        super().__init__(base_url="https://lol-api-summoner.op.gg/api/meta/")

    def get_seasons(self) -> SeasonAPIResponce:
        endpoint = f"seasons"
        params = {"hl": "eu_US"}

        return SeasonAPIResponce(**self._get(endpoint, params).json())

    def get_tiers(self) -> TierAPIResponse:
        endpoint = f"tiers"
        params = {"hl": "eu_US"}

        return TierAPIResponse(**self._get(endpoint, params).json())

    def get_game_types(self) -> GameTypeAPIResponse:
        endpoint = f"game-type"
        params = {"hl": "eu_US"}

        return GameTypeAPIResponse(**self._get(endpoint, params).json())
