# ddnet
from collections import Counter
from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field

rm_list = ["DD-Persian", "/vDQMHSss8W", '']


class DPoints(BaseModel):
    total: int
    points: Optional[int] = Field(default=None)
    rank: Optional[int] = Field(default=None)


class MaxFinishes(BaseModel):
    rank: int
    player: str
    num: int
    time: float
    min_timestamp: int
    max_timestamp: int


class DDRanks(BaseModel):
    rank: int
    player: str
    time: float
    timestamp: int
    country: str


class DDTeamRanks(BaseModel):
    rank: int
    players: list[str]
    time: float
    timestamp: int
    country: str


class DMap(BaseModel):
    name: str
    website: str
    thumbnail: str
    web_preview: str
    type: str
    points: int
    difficulty: int
    mapper: str
    release: Optional[int] = None
    median_time: float
    first_finish: int
    last_finish: int
    finishes: int
    finishers: int
    biggest_team: int
    width: int
    height: int
    tiles: list[str]
    team_ranks: list[DDTeamRanks]
    ranks: list[DDRanks]
    max_finishes: list[MaxFinishes]


class DRank(BaseModel):
    points: Optional[int] = None
    rank: Optional[int] = None


class FirstFinish(BaseModel):
    timestamp: float
    map: str
    time: float


class LastFinish(BaseModel):
    timestamp: float
    map: str
    time: float
    country: str
    type: Optional[str] = None


class FavoritePartner(BaseModel):
    name: str
    finishes: int


class DData(BaseModel):
    points: Optional[DPoints] = Field(default=None)
    team_rank: Optional[DRank] = Field(default=None)
    rank: Optional[DRank] = Field(default=None)
    maps: Optional[dict] = Field(default=None)


class DDType(BaseModel):
    Novice: Optional[DData] = None
    Moderate: Optional[DData] = None
    Brutal: Optional[DData] = None
    Insane: Optional[DData] = None
    Dummy: Optional[DData] = None
    DDmaX_Easy: Optional[DData] = Field(default=None, validation_alias='DDmaX.Easy')
    DDmaX_Next: Optional[DData] = Field(default=None, validation_alias='DDmaX.Next')
    DDmaX_Nut: Optional[DData] = Field(default=None, validation_alias='DDmaX.Nut')
    DDmaX_Pro: Optional[DData] = Field(default=None, validation_alias='DDmaX.Pro')
    Oldschool: Optional[DData] = Field(default=None)
    Race: Optional[DData] = None
    Solo: Optional[DData] = None
    total: Optional[DData] = None


class Activity(BaseModel):
    date: str
    hours_played: int


class FavoriteServer(BaseModel):
    server: str


class DDPlayer(BaseModel):
    player: str
    points: DPoints
    team_rank: Optional[DRank] = None
    rank: Optional[DRank] = None
    points_last_year: Optional[DRank] = None
    points_last_month: Optional[DRank] = None
    points_last_week: Optional[DRank] = None
    favorite_server: FavoriteServer
    first_finish: FirstFinish
    last_finishes: list[LastFinish]
    favorite_partners: Optional[list[FavoritePartner]] = None
    types: DDType
    activity: list[Activity]
    hours_played_past_365_days: int


class Skin(BaseModel):
    name: Optional[str] = None
    color_body: Optional[int] = None
    color_feet: Optional[int] = None


class Client(BaseModel):
    name: str
    clan: str
    country: int
    score: int
    is_player: Optional[bool] = None
    skin: Optional[Skin] = None
    afk: Optional[bool] = None
    team: Optional[int] = None


class Map(BaseModel):
    name: str
    sha256: Optional[str] = None
    size: Optional[int] = None


class Community(BaseModel):
    id: str
    icon: str
    admin: list[str]
    public_key: Optional[str] = None
    signature: Optional[str] = None


class Info(BaseModel):
    max_clients: int = None
    max_players: int = None
    passworded: bool = None
    game_type: str = None
    name: str = None
    map: Map = None
    version: str = None
    clients: Optional[list[Client]] = None
    requires_login: Optional[bool] = None
    community: Optional[Community] = None

    def __len__(self) -> int:
        return len(self.clients)


class Server(BaseModel):
    addresses: list | str
    location: str = Field(default=None)
    info: Info

    def __len__(self) -> int:
        return self.count_client

    @property
    def count_client(self) -> int:
        if self.info.clients is not None:
            return len(self.info.clients)
        return 0


class CountServers(BaseModel):
    name: str
    address: str
    game_type: str
    count_clients: int


class Master(BaseModel):
    servers: list[Server]

    def __len__(self) -> int:
        return len(self.servers)

    def get_clans(self, rm: list[str] = None) -> list[tuple[Any, int]]:
        remove_list = rm_list.copy() if rm is None else rm
        if not self.servers:
            return []

        dat: Counter[Any] = Counter(
            client.clan
            for server in self.servers
            for client in server.info.clients
            if client != ''
        )

        for i in remove_list:
            del dat[i]
        return sorted(dat.items(), key=lambda x: x[1], reverse=True)

    @property
    def count_servers(self) -> list[CountServers]:
        return sorted(
            (
                CountServers(
                    count_clients=i.count_client,
                    address=i.addresses[0],
                    game_type=i.info.game_type,
                    name=i.info.name
                )
                if isinstance(i.addresses, list)
                else CountServers(
                    count_clients=i.count_client,
                    address=i.addresses,
                    game_type=i.info.game_type,
                    name=i.info.name
                )
                for i in self.servers
            ), key=lambda x: x.count_clients, reverse=True)

    @property
    def count_clients(self) -> int:
        return sum(i.count_client for i in self.servers)


class ReleasesMapsData(BaseModel):
    name: str
    website: str
    thumbnail: str
    web_preview: str
    type: str
    points: int
    difficulty: int
    mapper: str
    release: datetime | str
    width: int
    height: int
    tiles: list[str]


class ReleasesMaps(BaseModel):
    maps: list[ReleasesMapsData]


class QueryData(BaseModel):
    points: int
    name: str


class Query(BaseModel):
    players: list[QueryData]


class QueryMapperData(BaseModel):
    mapper: str
    num_maps: int


class QueryMapper(BaseModel):
    players: list[QueryMapperData]


class QueryMapData(BaseModel):
    name: str
    type: str
    mapper: str


class QueryMap(BaseModel):
    maps: list[QueryMapData]
