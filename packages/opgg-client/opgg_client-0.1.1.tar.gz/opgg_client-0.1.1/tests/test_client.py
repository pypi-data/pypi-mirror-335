import json
from enum import Enum
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from clients.client import OPGGClient
from models.base_model import BaseResponse
from models.champion import ChampionAPIResponce
from models.match_history import MatchHistoryAPIResponce
from models.shared import Region
from models.summoner_champion_stats import (
    SummonerChampStatsAPIEmptyResponce,
    SummonerChampStatsAPIResponce,
)


class DataPaths(Enum):
    DIR = Path("test_data")
    MATCH_HISTORY = Path("match_history")
    CHAMP_STATS = Path("champ_stats")
    CHAMP_STATS_EMPTY = Path("champ_stats_empty")
    CHAMPION_METADATA = Path("champion_metadata")


JSON_EXTENTION = ".json"
TEST_SUMMONER_ID = "r5WSLNaMXFIpGO-vdtQCHzPjGBTMQB-7JkMjHkpsgdT3qJg"  # challenger player at time of writing 19/03/2025, has no games played in season 1


@pytest.fixture
def client():
    return OPGGClient(region=Region.EUW)


def load_json_test_data(filename: DataPaths, model: BaseResponse) -> BaseResponse:
    """Helper function to load JSON test data."""
    test_data_path = Path(__file__).parent / DataPaths.DIR.value / filename
    with open(
        test_data_path.with_suffix(JSON_EXTENTION), "r", encoding="utf-8"
    ) as file:
        return model(**json.load(file))


def save_json_test_data(filename: DataPaths, data: BaseResponse) -> dict:
    """Helper function to load JSON test data."""
    test_data_path = (
        Path(__file__).parent / "tests" / DataPaths.DIR.value / filename.value
    )
    with open(
        test_data_path.with_suffix(JSON_EXTENTION), "w", encoding="utf-8"
    ) as file:
        file.write(data.model_dump_json())


def test_get_match_history(client: OPGGClient):
    result = client.get_match_history(TEST_SUMMONER_ID)
    assert isinstance(result, MatchHistoryAPIResponce)


def test_opgg_api_health(client: OPGGClient):
    """Test the health of the OPGG API using champion metadata as no params are needed."""
    result = client.get_champion_metadata()
    assert isinstance(result, ChampionAPIResponce)


def test_get_champ_stats(client: OPGGClient):
    result = client.get_champ_stats(TEST_SUMMONER_ID)
    assert isinstance(result, SummonerChampStatsAPIResponce)


def test_get_champ_stats_empty(client: OPGGClient):
    result = client.get_champ_stats(TEST_SUMMONER_ID, 1)
    print(type(result))
    assert isinstance(result, SummonerChampStatsAPIEmptyResponce)


def test_get_champion_metadata(client: OPGGClient):
    result = client.get_champion_metadata()
    assert isinstance(result, ChampionAPIResponce)


@patch("clients.client.OPGGClient.get_match_history")
def test_get_all_match_history(mock_get: MagicMock, client: OPGGClient):

    first_response = load_json_test_data(
        DataPaths.MATCH_HISTORY.value / "2025-03-18", MatchHistoryAPIResponce
    )
    second_response = load_json_test_data(
        DataPaths.MATCH_HISTORY.value / "2025-03-16", MatchHistoryAPIResponce
    )

    end_response = load_json_test_data(
        DataPaths.MATCH_HISTORY.value / "end", MatchHistoryAPIResponce
    )

    mock_get.side_effect = [
        first_response,
        second_response,
        end_response,
    ]

    all_history = list(client.get_all_match_history(TEST_SUMMONER_ID))

    assert len(all_history) == 2
    assert len(all_history[0].data) == len(first_response.data)
    assert len(all_history[1].data) == len(second_response.data)

    assert all_history[0].data[0] == first_response.data[0]
    assert all_history[0].data[1] == first_response.data[1]

    assert all_history[1].data[0] == second_response.data[0]
    assert all_history[1].data[1] == second_response.data[1]
