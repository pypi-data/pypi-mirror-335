from buco_db_controller.models.team import Team


class Odds:
    def __init__(
            self,
            fixture_id: int,
            ht: Team,
            at: Team,
            result: dict,
            over_under: dict,
            btts: dict,
            dnb: dict,
            handicap: dict
    ):
        self.fixture_id: int = fixture_id
        self.ht: Team = ht
        self.at: Team = at
        self.result: dict = result
        self.over_under: dict = over_under
        self.btts: dict = btts
        self.dnb: dict = dnb
        self.handicap: dict = handicap

    @classmethod
    def from_dict(cls, response: dict) -> 'Odds':
        data = response['data']

        return cls(
            fixture_id=response['parameters']['fixture'],
            ht=Team(team_id=data['home']['team']['id'], name=data['home']['team']['name']),
            at=Team(team_id=data['away']['team']['id'], name=data['away']['team']['name']),
            result=data['odds']['1X2'],
            over_under=data['odds']['over_under'],
            btts=data['odds']['btts'],
            dnb=data['odds']['dnb'],
            handicap=data['odds']['handicap']
        )
