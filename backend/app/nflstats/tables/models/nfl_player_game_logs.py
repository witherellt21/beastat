from datetime import datetime
from typing import Optional

from peewee import (
    BooleanField,
    CharField,
    DateTimeField,
    FloatField,
    ForeignKeyField,
    IntegerField,
)
from pydantic import BaseModel as BaseSerializer
from scrapp.db.models import BaseModel
from scrapp.tables.base_table import BaseTable

from .nfl_player import NFLPlayer, NFLPlayerReadSerializer
from .nfl_team import NFLTeam, NFLTeamReadSerializer


class NFLPlayerGameLog(BaseModel):
    player = ForeignKeyField(NFLPlayer, backref="gamelogs")
    date = DateTimeField()
    week = IntegerField()
    age_years = IntegerField()
    age_days = IntegerField()
    team = ForeignKeyField(NFLTeam, backref="gamelogs")
    home = BooleanField()
    opp = ForeignKeyField(NFLTeam, backref="gamelogs")
    result = CharField()
    team_pts = IntegerField()
    opp_pts = IntegerField()
    start = BooleanField(null=True)

    # Should all be null if the player did not play any offensive snaps
    pass_cmp = IntegerField(null=True)
    pass_att = IntegerField(null=True)
    pass_cmp_pct = FloatField(null=True)
    pass_yds = IntegerField(null=True)
    pass_tds = IntegerField(null=True)
    pass_ints = IntegerField(null=True)
    pass_rtng = FloatField(null=True)
    pass_scks = IntegerField(null=True)
    pass_scks_yds = IntegerField(null=True)
    pass_yds_per_att = FloatField(null=True)
    pass_yds_per_att_adj = FloatField(null=True)

    rec_tgts = IntegerField(null=True)
    rec_recs = IntegerField(null=True)
    rec_yds = IntegerField(null=True)
    rec_yds_per_rec = FloatField(null=True)
    rec_tds = IntegerField(null=True)
    rec_catch_pct = FloatField(null=True)
    rec_yds_per_tgt = FloatField(null=True)

    rush_att = IntegerField(null=True)
    rush_yds = IntegerField(null=True)
    rush_yds_per_att = FloatField(null=True)
    rush_tds = IntegerField(null=True)

    kickret_rts = IntegerField(null=True)
    kickret_yds = IntegerField(null=True)
    kickret_yds_per_rt = FloatField(null=True)
    kickret_tds = IntegerField(null=True)

    puntret_rts = IntegerField(null=True)
    puntret_yds = IntegerField(null=True)
    puntret_yds_per_rt = FloatField(null=True)
    puntret_tds = IntegerField(null=True)

    two_pts = IntegerField(null=True)
    td_tot = IntegerField(null=True)
    pts_tot = IntegerField(null=True)

    # Should be nan if the player did not play any defensive snaps
    def_scks = FloatField(null=True)
    def_tcks_tfls = IntegerField(null=True)
    def_tcks_qbhits = IntegerField(null=True)

    # Interceptions group
    def_ints = IntegerField(null=True)
    def_ints_yds = IntegerField(null=True)
    def_ints_tds = IntegerField(null=True)
    def_pass_def = IntegerField(null=True)

    # These could theoretically happen if a ball is turned over and still live so they are not tied to the def. snaps
    tcks_solo = IntegerField(null=True)
    tcks_ast = IntegerField(null=True)
    tcks = IntegerField(null=True)

    fmbs = IntegerField(null=True)
    fmbs_lost = IntegerField(null=True)
    fmbs_forced = IntegerField(null=True)
    fmbs_rcovd = IntegerField(null=True)
    fmbs_yds = IntegerField(null=True)
    fmbs_TD = IntegerField(null=True)

    offsnaps_num = IntegerField(null=True)
    offsnaps_pct = IntegerField(null=True)

    defsnaps_num = IntegerField(null=True)
    defsnaps_pct = IntegerField(null=True)

    # Defensive special teams snaps
    stsnaps_num = IntegerField(null=True)
    stsnaps_pct = IntegerField(null=True)

    status = CharField(null=True)

    dnp = BooleanField()
    out = BooleanField()
    sspd = BooleanField()

    class Meta:
        indexes = ((("player_id", "date"), True),)


class NFLPlayerGameLogSerializer(BaseSerializer):
    player_id: str
    date: datetime
    week: int
    age_years: int
    age_days: int
    team_id: str
    home: bool
    opp_id: str
    result: str
    team_pts: int
    opp_pts: int
    start: Optional[bool]

    # Should all be null if the player did not play any offensive snaps
    pass_cmp: Optional[int]
    pass_att: Optional[int]
    pass_cmp_pct: Optional[float]
    pass_yds: Optional[int]
    pass_tds: Optional[int]
    pass_ints: Optional[int]
    pass_rtng: Optional[float]
    pass_scks: Optional[int]
    pass_scks_yds: Optional[int]
    pass_yds_per_att: Optional[float]
    pass_yds_per_att_adj: Optional[float]

    rec_tgts: Optional[int]
    rec_recs: Optional[int]
    rec_yds: Optional[int]
    rec_yds_per_rec: Optional[float]
    rec_tds: Optional[int]
    rec_catch_pct: Optional[float]
    rec_yds_per_tgt: Optional[float]

    rush_att: Optional[int]
    rush_yds: Optional[int]
    rush_yds_per_att: Optional[float]
    rush_tds: Optional[int]

    kickret_rts: Optional[int]
    kickret_yds: Optional[int]
    kickret_yds_per_rt: Optional[float]
    kickret_tds: Optional[int]

    puntret_rts: Optional[int]
    puntret_yds: Optional[int]
    puntret_yds_per_rt: Optional[float]
    puntret_tds: Optional[int]

    two_pts: Optional[int]
    td_tot: Optional[int]
    pts_tot: Optional[int]

    # Should be nan if the player did not play any defensive snaps
    def_scks: Optional[float]
    def_tcks_tfls: Optional[int]
    def_tcks_qbhits: Optional[int]

    # Interceptions group
    def_ints: Optional[int]
    def_ints_yds: Optional[int]
    def_ints_tds: Optional[int]
    def_pass_def: Optional[int]

    # These could theoretically happen if a ball is turned over and still live so they are not tied to the def. snaps
    tcks_solo: Optional[int]
    tcks_ast: Optional[int]
    tcks: Optional[int]

    fmbs: Optional[int]
    fmbs_lost: Optional[int]
    fmbs_forced: Optional[int]
    fmbs_rcovd: Optional[int]
    fmbs_yds: Optional[int]
    fmbs_TD: Optional[int]

    offsnaps_num: Optional[int]
    offsnaps_pct: Optional[int]

    defsnaps_num: Optional[int]
    defsnaps_pct: Optional[int]

    # Defensive special teams snaps
    stsnaps_num: Optional[int]
    stsnaps_pct: Optional[int]

    status: Optional[str]

    dnp: bool
    out: bool
    sspd: bool


class NFLPlayerGameLogReadSerializer(NFLPlayerGameLogSerializer):
    _player_id: str
    player: NFLPlayerReadSerializer

    _team_id: str
    team: NFLTeamReadSerializer

    _opp_id: str
    opp: NFLTeamReadSerializer


class NFLPlayerGameLogs(BaseTable):
    MODEL_CLASS = NFLPlayerGameLog
    SERIALIZER_CLASS = NFLPlayerGameLogSerializer
    READ_SERIALIZER_CLASS = NFLPlayerGameLogReadSerializer
    PKS = ["player_id", "date"]
