import pytest

from logic_utils import DIFFICULTY_SETTINGS


@pytest.fixture(params=list(DIFFICULTY_SETTINGS.items()))
def game_settings(request):
    """Provide each supported game range and turn budget to bot tests."""
    difficulty, settings = request.param
    return difficulty, settings["range"], settings["attempts"]
