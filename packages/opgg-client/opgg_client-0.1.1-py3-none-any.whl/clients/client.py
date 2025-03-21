import datetime
import urllib
from typing import Generator

from clients.base_client import BaseAPIClient
from models.champion import ChampionAPIResponce
from models.match_history import MatchHistoryAPIResponce
from models.shared import Region
from models.summoner_champion_stats import (
    SummonerChampStatsAPIEmptyResponce,
    SummonerChampStatsAPIResponce,
)


class OPGGClient(BaseAPIClient):
    def __init__(self, region: Region = Region.EUW) -> None:
        super().__init__(base_url="https://lol-web-api.op.gg/api/v1.0/internal/bypass/")
        self.region: Region = region

    def get_match_history(
        self,
        summoner_id: str,
        ended_at: datetime = None,
    ) -> MatchHistoryAPIResponce:
        endpoint = f"games/{self.region.value}/summoners/{summoner_id}"
        params = {
            "limit": 20,
            "hl": "en_US",
            "game_type": "soloranked",
        }
        if ended_at:
            params["ended_at"] = str(ended_at)

        return MatchHistoryAPIResponce(**self._get(endpoint, params).json())

    def get_summoner_details(self):
        return

    def get_champ_stats(
        self,
        summoner_id: str,
        season_id: int = None,
    ) -> SummonerChampStatsAPIResponce | SummonerChampStatsAPIEmptyResponce:
        endpoint = f"summoners/{self.region.value}/{summoner_id}/most-champions/rank"
        params = {
            "game_type": "SOLORANKED",
        }
        if season_id:
            params["season_id"] = season_id
        data = self._get(endpoint, params).json()

        # the api returns data as a list insted of an object when no data is present (fuck opgg)
        if isinstance(data["data"], list):
            return SummonerChampStatsAPIEmptyResponce(**data)

        return SummonerChampStatsAPIResponce(**data)

    def get_all_match_history(
        self,
        summoner_id: str,
        start_date: datetime = None,
    ) -> Generator[MatchHistoryAPIResponce, None, None]:

        responce = self.get_match_history(
            summoner_id=summoner_id,
            ended_at=start_date,
        )
        while len(responce.data) > 0:
            self.logger.info(
                f"Yielding response of type: {type(responce)}"
            )  # Check the type here

            yield responce

            last_game_played = responce
            responce = self.get_match_history(
                summoner_id=summoner_id,
                ended_at=last_game_played.meta.last_game_created_at,
            )

    def get_champion_metadata(self) -> ChampionAPIResponce:
        endpoint = f"meta/champions"
        params = {"hl": "en_US"}

        return ChampionAPIResponce(**self._get(endpoint, params).json())
