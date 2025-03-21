import pytest

from opgg.clients.meta_client import OPGGMetaClient
from opgg.models.meta_responses import (
    GameTypeAPIResponse,
    SeasonAPIResponce,
    TierAPIResponse,
)
from opgg.models.shared import GameType, Season, Tier


@pytest.fixture
def client():
    return OPGGMetaClient()


def test_get_season_enum_matches_api(client: OPGGMetaClient):
    result = client.get_seasons()
    assert isinstance(result, SeasonAPIResponce)

    enum_values = {s.value for s in Season}
    api_ids = {
        r.id for r in result.data}
    
    assert api_ids == enum_values, f"Mismatch! API: {api_ids}, Enum: {enum_values}"


def test_get_tier_enum_matches_api(client: OPGGMetaClient):
    result = client.get_tiers()
    assert isinstance(result, TierAPIResponse)

    enum_values = {t.value for t in Tier}
    api_names = {r.name for r in result.data}

    assert api_names == enum_values, f"Mismatch! API: {api_names}, Enum: {enum_values}"


def test_get_game_type_enum_matches_api(client: OPGGMetaClient):
    result = client.get_game_types()
    assert isinstance(result, GameTypeAPIResponse)

    enum_values = {g.value for g in GameType}
    api_game_types = {r.game_type for r in result.data}

    assert (
        api_game_types == enum_values
    ), f"Mismatch! API: {api_game_types}, Enum: {enum_values}"
