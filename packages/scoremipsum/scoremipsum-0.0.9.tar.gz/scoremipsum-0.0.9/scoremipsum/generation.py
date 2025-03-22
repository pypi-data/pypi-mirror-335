#
#   SCOREM
#
"""
game
----------

game functions for the `scoremipsum` module.
"""

import random

from scoremipsum.data import TEAMS_DEFAULT
from scoremipsum.schedule import generate_schedule_single_pairs, generate_games_from_schedule
from scoremipsum.score import generate_score_anyball, generate_score_football, generate_score_hockey
from scoremipsum.util.conversion import convert_game_result_to_json
from scoremipsum.util.team import get_team_data, get_default_teamlist_from_gametype


def get_game(gametype=None):
    if not gametype:
        gametype = 'anyball'
    teamlist = get_default_teamlist_from_gametype(gametype)
    schedule = generate_schedule_single_pairs(teamlist)
    game_generation_results = generate_games_from_schedule(schedule, gametype=gametype)
    game_results_json = convert_game_result_to_json(game_generation_results, gametype=gametype)
    return game_results_json


class GameGeneration:
    """
    game generation class for the `scoremipsum` module.
    """

    def __init__(self, teams=None):
        if teams:
            self._teams = teams
        else:
            self._teams = TEAMS_DEFAULT

    def _team(self):
        return random.choice(self._teams)

    # BACKLOG US145:  Fix disconnect for these methods - remove, use as intended and add unit tests, or redesign.

    @staticmethod
    def get_result_anyball(active_team_data=None, opposing_team_data=None):
        """
        :param active_team_data:
        :param opposing_team_data:
        :return:
        """
        ruleset = {'anyball'}

        if not active_team_data:
            active_team_data = get_team_data()
        if not opposing_team_data:
            opposing_team_data = get_team_data()

        score = generate_score_anyball(ruleset, active_team_data, opposing_team_data)
        return score

    @staticmethod
    def get_result_football(active_team_data=None, opposing_team_data=None):
        """
        :param active_team_data:
        :param opposing_team_data:
        :return:
        """
        ruleset = {'football'}

        if not active_team_data:
            active_team_data = get_team_data()
        if not opposing_team_data:
            opposing_team_data = get_team_data()

        score = generate_score_football(ruleset, active_team_data, opposing_team_data)
        return score

    @staticmethod
    def get_result_hockey(active_team_data=None, opposing_team_data=None):
        """
        :param active_team_data:
        :param opposing_team_data:
        :return:
        """
        ruleset = {'hockey'}

        if not active_team_data:
            active_team_data = get_team_data()
        if not opposing_team_data:
            opposing_team_data = get_team_data()

        score = generate_score_hockey(ruleset, active_team_data, opposing_team_data)
        return score
