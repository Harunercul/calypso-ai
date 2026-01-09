"""
Environments Module
Mock ve Unreal Engine bridge environments

CALYPSO oyununa özel genişletilmiş environment'lar.
"""

from .mock_env import MockCombatEnv
from .observation import ObservationBuilder

# CALYPSO-specific
from .calypso_mock_env import CalypsoMockEnv, CalypsoAction, make_calypso_env
from .calypso_observation import (
    CalypsoObservationBuilder,
    CalypsoBotState,
    CalypsoEnemyState,
    CalypsoEnvironmentState,
    CalypsoTeamState,
    EnemyTier,
    WeaponType,
    AreaType,
    AlarmLevel,
    CALYPSO_WEAPONS,
    CALYPSO_TIERS
)

__all__ = [
    # Generic
    "MockCombatEnv",
    "ObservationBuilder",
    # CALYPSO Environment
    "CalypsoMockEnv",
    "CalypsoAction",
    "make_calypso_env",
    # CALYPSO Observations
    "CalypsoObservationBuilder",
    "CalypsoBotState",
    "CalypsoEnemyState",
    "CalypsoEnvironmentState",
    "CalypsoTeamState",
    # CALYPSO Enums
    "EnemyTier",
    "WeaponType",
    "AreaType",
    "AlarmLevel",
    # CALYPSO Data
    "CALYPSO_WEAPONS",
    "CALYPSO_TIERS"
]
