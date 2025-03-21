from enum import Enum


class Result(Enum):
    """
    Enum for game results.

    ### Options:
        `WIN` - Represents a win.\n
        `LOSE` - Represents a loss.\n
        `UNKNOWN` - Represents an unknown result.
    """

    WIN = "WIN"
    LOSE = "LOSE"
    UNKNOWN = "UNKNOWN"


class Map(Enum):
    """
    Enum for map types.

    ### Options:
        `SUMMONERS_RIFT` - Summoner's Rift.\n
        `TWISTED_TREELINE` - Twisted Treeline.\n
        `HOWLING_ABYSS` - Howling Abyss.\n
        `CRYSTAL_SCAR` - Crystal Scar.\n
        `BUTCHERS_BRIDGE` - Butcher's Bridge.
    """

    SUMMONERS_RIFT = "SUMMONER'S RIFT"
    TWISTED_TREELINE = "TWISTED TREELINE"
    HOWLING_ABYSS = "HOWLING ABYSS"
    CRYSTAL_SCAR = "CRYSTAL SCAR"
    BUTCHERS_BRIDGE = "BUTCHER'S BRIDGE"


class Key(Enum):
    """
    Enum for team keys.

    ### Options:
        `BLUE` - Represents the blue team.\n
        `RED` - Represents the red team.
    """

    BLUE = "BLUE"
    RED = "RED"


class Tier(Enum):
    """
    Enum for ranked tiers.

    ### Options:
        `IRON` - Iron tier.\n
        `BRONZE` - Bronze tier.\n
        `SILVER` - Silver tier.\n
        `GOLD` - Gold tier.\n
        `PLATINUM` - Platinum tier.\n
        `EMERALD` - Emerald tier.\n
        `DIAMOND` - Diamond tier.\n
        `MASTER` - Master tier.\n
        `GRANDMASTER` - Grandmaster tier.\n
        `CHALLENGER` - Challenger tier.
    """

    IRON = "IRON"
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"
    EMERALD = "EMERALD"
    DIAMOND = "DIAMOND"
    MASTER = "MASTER"
    GRANDMASTER = "GRANDMASTER"
    CHALLENGER = "CHALLENGER"


class Position(Enum):
    """
    Enum for player positions.

    ### Options:
        `MID` - Mid lane.\n
        `JUNGLE` - Jungle.\n
        `ADC` - Attack Damage Carry (Bot lane).\n
        `TOP` - Top lane.\n
        `SUPPORT` - Support role.
    """

    MID = "MID"
    JUNGLE = "JUNGLE"
    ADC = "ADC"
    TOP = "TOP"
    SUPPORT = "SUPPORT"


class Role(Enum):
    """
    Enum for champion roles.

    ### Options:
        `FIGHTER` - Fighter role.\n
        `MARKSMAN` - Marksman role.\n
        `MAGE` - Mage role.\n
        `TANK` - Tank role.\n
        `CONTROLLER` - Controller role.\n
        `SLAYER` - Slayer role.\n
        `SPECIALIST` - Specialist role.\n
        `NONE` - No specific role.
    """

    FIGHTER = "FIGHTER"
    MARKSMAN = "MARKSMAN"
    MAGE = "MAGE"
    TANK = "TANK"
    CONTROLLER = "CONTROLLER"
    SLAYER = "SLAYER"
    SPECIALIST = "SPECIALIST"
    NONE = "NONE"


class Season(Enum):
    """
    Enum for game seasons.

    ### Options:
        `S1` - Season 1.\n
        `S2` - Season 2.\n
        `S3` - Season 3.\n
        `S4` - Season 4.\n
        `S5` - Season 5.\n
        `S6` - Season 6.\n
        `S7` - Season 7.\n
        `S8_PRESEASON` - Preseason 8.\n
        `S8` - Season 8.\n
        `S9_PRESEASON` - Preseason 9.\n
        `S9` - Season 9.\n
        `S10_PRESEASON` - Preseason 10.\n
        `S10` - Season 10.\n
        `S11_PRESEASON` - Preseason 11.\n
        `S11` - Season 11.\n
        `S12_PRESEASON` - Preseason 12.\n
        `S12` - Season 12.\n
        `S13_SPLIT_1_PRESEASON` - Preseason 13 Split 1.\n
        `S13_SPLIT_1` - Season 13 Split 1.\n
        `S13_SPLIT_2_PRESEASON` - Preseason 13 Split 2.\n
        `S13_SPLIT_2` - Season 13 Split 2.\n
        `S14_SPLIT_1_PRESEASON` - Preseason 14 Split 1.\n
        `S14_SPLIT_1` - Season 14 Split 1.\n
        `S14_SPLIT_2_PRESEASON` - Preseason 14 Split 2.\n
        `S14_SPLIT_2` - Season 14 Split 2.\n
        `S14_SPLIT_3_PRESEASON` - Preseason 14 Split 3.\n
        `S14_SPLIT_3` - Season 14 Split 3.\n
        `S15_PRESEASON` - Preseason 15.\n
        `S15_SEASON_1` - Season 15.
    """

    S1 = 1
    S2 = 2
    S3 = 3
    S4 = 4
    S5 = 5
    S6 = 6
    S7 = 7
    S8_PRESEASON = 10
    S8 = 11
    S9_PRESEASON = 12
    S9 = 13
    S10_PRESEASON = 14
    S10 = 15
    S11_PRESEASON = 16
    S11 = 17
    S12_PRESEASON = 18
    S12 = 19
    S13_SPLIT_1_PRESEASON = 20
    S13_SPLIT_1 = 21
    S13_SPLIT_2_PRESEASON = 22
    S13_SPLIT_2 = 23
    S14_SPLIT_1_PRESEASON = 24
    S14_SPLIT_1 = 25
    S14_SPLIT_2_PRESEASON = 26
    S14_SPLIT_2 = 27
    S14_SPLIT_3_PRESEASON = 28
    S14_SPLIT_3 = 29
    S15_PRESEASON = 30
    S15_SEASON_1 = 31


class GameType(Enum):
    """
    Enum for game types.

    ### Options:
        `TOTAL` - All game types.\n
        `RANKED` - Ranked games.\n
        `SOLORANKED` - Solo ranked games.\n
        `FLEXRANKED` - Flex ranked games.\n
        `NORMAL` - Normal games.\n
        `ARAM` - ARAM games.\n
        `BOT` - Bot games.\n
        `URF` - Ultra Rapid Fire games.\n
        `CLASH` - Clash games.\n
        `ARENA` - Arena games.\n
        `NEXUS_BLITZ` - Nexus Blitz games.\n
        `CUSTOM` - Custom games.\n
        `TUTORIAL` - Tutorial games.\n
        `EVENT` - Event games.
    """

    TOTAL = "TOTAL"
    RANKED = "RANKED"
    SOLORANKED = "SOLORANKED"
    FLEXRANKED = "FLEXRANKED"
    NORMAL = "NORMAL"
    ARAM = "ARAM"
    BOT = "BOT"
    URF = "URF"
    CLASH = "CLASH"
    ARENA = "ARENA"
    NEXUS_BLITZ = "NEXUS_BLITZ"
    CUSTOM = "CUSTOM"
    TUTORIAL = "TUTORIAL"
    EVENT = "EVENT"


class Region(Enum):
    """
    Enum for regions.

    ### Options:
        `NA` - North America\n
        `EUW` - Europe West\n
        `EUNE` - Europe Nordic & East\n
        `KR` - Korea\n
        `JP` - Japan\n
        `BR` - Brazil\n
        `LAN` - Latin America North\n
        `LAS` - Latin America South\n
        `OCE` - Oceania\n
        `RU` - Russia\n
        `TR` - Turkey\n
        `ANY` - Any
    """

    NA = "NA"
    EUW = "EUW"
    EUNE = "EUNE"
    KR = "KR"
    JP = "JP"
    BR = "BR"
    LAN = "LAN"
    LAS = "LAS"
    OCE = "OCE"
    RU = "RU"
    TR = "TR"
    ANY = "ANY"

    def __str__(self):
        return self.value


class By(Enum):
    """
    Enum for search-by or match-by types.

    ### Options:
        `ID` - Generic ID\n
        `KEY` - Generic Key\n
        `NAME` - Generic Name\n
        `COST` - Generic Cost\n
        `BLUE_ESSENCE` - Specific Cost (Blue Essence)\n
        `RIOT_POINTS` - Specific Cost (Riot Points)
    """

    ID = "id"
    NAME = "name"
    COST = "cost"
    BLUE_ESSENCE = "BE"
    RIOT_POINTS = "RP"

    def __str__(self):
        return self.value


class Queue(Enum):
    """
    Enum for queue types.

    ### Options:
        `SOLO` - SoloQueue\n
        `FLEX` - FlexQueue\n
        `ARENA` - Arena
    """

    SOLO = "SOLORANKED"
    FLEX = "FLEXRANKED"
    ARENA = "ARENA"

    def __str__(self):
        return self.value


class LangCode(Enum):
    """
    Enum for language codes.

    Please note, some languages may not be supported by OPGG.

    ---

    ### Options:
        `ENGLISH` - en_US (United States)\n
        `SPANISH` - es_ES (Spain)\n
        `PORTUGUESE` - pt_BR (Brazil)\n
        `FRENCH` - fr_FR (France)\n
        `GERMAN` - de_DE (Germany)\n
        `ITALIAN` - it_IT (Italy)\n
        `RUSSIAN` - ru_RU (Russia)\n
        `TURKISH` - tr_TR (Turkey)\n
        `KOREAN` - ko_KR (Korea)\n
        `JAPANESE` - ja_JP (Japan)\n
        `CHINESE` - zh_CN (Simplified)\n
        `CHINESE_TRAD` - zh_TW (Traditional)
    """

    ENGLISH = "en_US"  # English (United States)
    SPANISH = "es_ES"  # Spanish (Spain)
    PORTUGUESE = "pt_BR"  # Portuguese (Brazil)
    FRENCH = "fr_FR"  # French (France)
    GERMAN = "de_DE"  # German (Germany)
    ITALIAN = "it_IT"  # Italian (Italy)
    RUSSIAN = "ru_RU"  # Russian (Russia)
    TURKISH = "tr_TR"  # Turkish (Turkey)
    KOREAN = "ko_KR"  # Korean (Korea)
    JAPANESE = "ja_JP"  # Japanese (Japan)
    CHINESE = "zh_CN"  # Chinese (Simplified)
    CHINESE_TRAD = "zh_TW"  # Chinese (Traditional)

    def __str__(self):
        return self.value
