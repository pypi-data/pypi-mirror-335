import logging
import random
from uuid import uuid4
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Optional, Set, TypeVar, Generic, Union
from uuid import UUID
import json
from multipledispatch import dispatch
from functools import reduce
from pyrsistent import PClass, field
from pyrsistent import v, pvector, PVector


class NoAction(PClass):
    pass

class RouteDiscardAction(PClass):
    pass

class DrawUnitDeckAction(PClass):
    pass

class DrawUnitFaceupAction(PClass):
    pass

class ClaimPointAction(PClass):
    pass


class TrueType(PClass):
    pass

class FalseType(PClass):
    pass


def getbooltype(bool):
    if bool:
        return TrueType()
    return FalseType()


@dataclass(frozen=True)
class FrozenLenScore:
    length: int
    score: int


@dataclass(frozen=True)
class FrozenDeckUnit2:
    num: int
    quantity: int
    is_wild: bool
    unit_uuid: UUID


@dataclass(frozen=True)
class FrozenLink2:
    num: int
    uuid: UUID
    c1: UUID
    c2: UUID
    length: int
    width: int


class FrozenPoint2(PClass):
    num = field(type=int)
    uuid = field(type=str)


class FrozenCluster(PClass):
    uuid = field(type=str)
    points = field(type=list)  # List[UUID]
    score = field(type=int)
    # uuid: UUID
    # points: List[UUID]
    # score: int


@dataclass(frozen=True)
class FrozenSegment:
    uuid: UUID
    link_uuid: UUID
    unit_uuid: Optional[UUID]
    path_idx: int
    idx: int


@dataclass(frozen=True)
class FrozenLinkPath:
    is_mixed: bool
    segments: List[FrozenSegment]


@dataclass(frozen=True)
class FrozenPath:
    num: int
    link_num: int
    start_point_num: int
    end_point_num: int
    path: FrozenLinkPath


@dataclass(frozen=True)
class FrozenRoute:
    num: int
    uuid: UUID
    point_a_uuid: UUID
    point_b_uuid: UUID
    score: int
    start_num: int
    end_num: int


@dataclass(frozen=True)
class FrozenSetting:
    name: str
    value_json: str


@dataclass(frozen=True)
class FrozenBoardConfig:
    deck_units: List[FrozenDeckUnit2]
    len_scores: List[FrozenLenScore]
    links: List[FrozenLink2]
    clusters: List[FrozenCluster]
    points: List[FrozenPoint2]
    board_paths: List[FrozenPath]
    routes: List[FrozenRoute]
    settings: List[FrozenSetting]


@dataclass(frozen=True)
class BoardNode:
    num: int
    point_num: Optional[int]  # Can be None
    point_uuid: UUID
    path_num: Optional[int]
    path_segment_num_a: Optional[int]
    path_segment_num_b: Optional[int]


@dataclass(frozen=True)
class BoardEdge:
    num: int
    src: int
    dst: int
    path_num: int
    path_segment_num: int
    segment_num: int


@dataclass(frozen=True)
class BoardGraph:
    nodes: List[BoardNode]
    edges: List[BoardEdge]
    adj: Any  # You can refine this type (e.g., List[List[float]]) depending on your matrix representation


@dataclass(frozen=True)
class Action:
    player_idx: int
    action_name: str
    return_route_cards: Set[int]
    point_uuid: Optional[UUID]
    path_idx: Optional[int]
    unit_combo: Optional[str]
    draw_faceup_unit_card_num: Optional[int]
    draw_faceup_spot_num: Optional[int]
    def __str__(self):
        return f"Action({self.action_name})"
    def __repr__(self):
        return self.__str__()


class FrozenRoute(PClass):
    num = field(type=int)
    uuid = field(type=str)
    point_a_uuid = field(type=str)
    point_b_uuid = field(type=str)
    score = field(type=int)
    start_num = field(type=int)
    end_num = field(type=int)


class FrozenBoardConfig(PClass):
    routes = field(type=list)  # List[FrozenRoute]
    deck_units = field(type=list)  # List[FrozenDeckUnit2]
    settings = field(type=list)  # List[FrozenSetting]
    points = field(type=list)  # List[FrozenPoint2]
    clusters = field(type=list)  # List[FrozenCluster]
    # len_scores::Vector{FrozenLenScore}
    # links::Vector{FrozenLink2}
    # board_paths::Vector{FrozenPath}
    # routes::Vector{FrozenRoute}


@dispatch(dict)
def initfrozenroutes(d):
    pointuuids2nums = {p['uuid']: n for n, p in enumerate(d['points'])}
    return [
        FrozenRoute(
            num=i+1,
            uuid=r['uuid'],
            point_a_uuid=r['point_a_uuid'],
            point_b_uuid=r['point_b_uuid'],
            score=r['score'],
            start_num=pointuuids2nums[r['point_a_uuid']],
            end_num=pointuuids2nums[r['point_b_uuid']],
        )
        for i, r in enumerate(d['routes'])
    ]


@dispatch(dict)
def initboardconfig(d):
    print("*****************************************1")
    print(d.keys())
    print("*****************************************2")
    return FrozenBoardConfig(
        routes = initfrozenroutes(d),
        deck_units = getdeckunits(d['deck_units']),
        settings = getsettings(d['settings']),
        points = getpoints(d["points"]),
        clusters = getclusters(d["clusters"]),
    )


def getclusters(d):
    return [
        FrozenCluster(
            uuid=x['uuid'],
            points=[p for p in x['points']],
            score=x['score'],
        )
        for n, x in enumerate(d)
    ]


def getpoints(d):
    return [
        FrozenPoint2(
            num=n,
            uuid=x['uuid'],
        )
        for n, x in enumerate(d)
    ]

def getsettings(d):
    return [
        BoardSetting(
            name=x['name'],
            value_json=x['value_json'],
        )
        for n, x in enumerate(d)
    ]


def getdeckunits(d):
    return [
        FrozenDeckUnit2(
            num=x['num'],
            quantity=x['quantity'],
            is_wild=x['is_wild'],
            unit_uuid=x['unit_uuid']
        )
        for n, x in enumerate(d)
    ]


class BoardSetting(PClass):
    name = field(type=str)
    value_json = field(type=str)


class FrozenDeckUnit2(PClass):
    num = field(type=int)
    quantity = field(type=int)
    is_wild = field(type=bool)
    unit_uuid = field(type=str)


class Fig(PClass):
    # static_board_config_uuid = field(type=int)
    board_config = field(type=FrozenBoardConfig)
    # graph = field(type=int)
    # path_scores = field(type=int)
    # static_board_config_uuid: UUID
    # board_config: FrozenBoardConfig
    # graph: BoardGraph
    # path_scores: List[int]
 

class Game(PClass):
    uuid = field(type=str)
    num_players = field(type=int)
    fig = field(type=Fig)
    seed = field(type=int)
    actions = field(type=list)  # List[Action]


class ActionDrawUnit:
   def __init__(self):
       pass


# struct PublicState
#     fig::Fig
#     logged_game_uuid::UUID
#     action_history::Vector{Action}
#     to_play::Vector{Int}
#     num_route_cards::Int
#     num_route_discards::Int
#     num_unit_cards::Int
#     num_unit_discards::Int
#     faceup_spots::Vector{Union{Nothing,Int}}
#     player_hands::Vector{PublicPlayerInfo}
#     captured_segments::Vector{CapturedSegment}
#     captured_points::Vector{CapturedPoint}
#     last_to_play::Union{Nothing,Int}
#     terminal::Bool
#     longest_road_player_idxs::Vector{Int}
#     most_clusters_player_idxs::Vector{Int}
#     winners::Vector{Int}
#     market_refills::Vector{MarketRefill}


class AltAction(PClass):
    player_idx = field(type=int)
    action_name = field(type=str)
    return_route_cards = field(type=list)  # List[int]
    draw_faceup_unit_card_num = field(type=(int, type(None)), initial=None)
    draw_faceup_spot_num = field(type=(int, type(None)), initial=None)
    point_uuid = field(type=(str, type(None)), initial=None)
    unit_combo = field(type=(str, type(None)), initial=None)  # TODO: should be list of int


class ActionSpec(PClass):
    # # TODO: should remove "player_idx" as it's always the same as "to_play"
    player_idx = field(type=int)
    action_name = field(type=str)
    return_route_option_sets = field(type=list)  # List[OptionSet]
    draw_faceup_spots = field(type=dict)  # Dict{Int, int}
    points = field(type=list)  # List[PointCombos]
    paths = field(type=list)  # List[PathCombos]


class PointCombos(PClass):
    point_uuid = field(type=str)
    default_combo = field(type=str)
    sample_fulfillment = field(type=list)  # List[int]


class PlayerInfo(PClass):
    fig = field(type=Fig)
    player_idx = field(type=int)
    new_route_cards = field(type=PVector)  # List[int]
    route_cards = field(type=PVector)  # List[int]
    unit_cards = field(type=PVector)  # List[int]
    completed_routes = field(type=list)  # List[int]
    clusters = field(type=list)  # List[UUID]
    completed_clusters = field(type=list)  # List[UUID]
    paths = field(type=list)  # List[int]
    points = field(type=list)  # List[UUID]
    num_pieces = field(type=int)
    num_point_pieces = field(type=int)
    longest_road = field(type=list)  # List[int]
    longest_road_len = field(type=int)
    final_score = field()  # Union{Nothing, PlayerScore}


class State(PClass):
    game = field(type=Game) 
    terminal = field(type=bool)
    action_history = field(type=list)  # List[Action]
    route_cards = field(type=PVector)  # List[int]
    route_discards = field(type=PVector)  # List[int]
    player_hands = field(type=PVector)  # List[PlayerInfo]
    unit_cards = field(type=PVector)  # List[int]
    faceup_spots = field(type=PVector)  # List[Union{Nothing, int}]
    unit_discards = field(type=PVector)  # List[int]
    most_clusters_player_idxs = field(type=list)  # List[int]
    # game::Game
    # fig::Fig
    # player_hands::Vector{PlayerInfo}
    # last_to_play::Union{Nothing,Int}
    # terminal::Bool
    # longest_road_player_idxs::Vector{Int}
    # winners::Vector{Int}
    # market_refills::Vector{MarketRefill}


# Implementing the following Julia function:
# getnumroutecards(f::Fig) = length(f.board_config.routes)
@dispatch(Fig)
def getnumroutecards(f):
    return len(f.board_config.routes) if f and f.board_config else 0


# Implementing the following Julia function:
# [x.quantity for x in f.board_config.deck_units] |> sum
@dispatch(Fig)
def gettotaldeckcards(f):
    return sum(x.quantity for x in f.board_config.deck_units) if f and f.board_config else 0
    

# Implementing the following Julia function:
# function shuffledeck(deck_size::Int, seed::Int)
#     shuffledeck(collect(1:deck_size), seed)
# end
@dispatch(int, int)
def shuffledeck(deck_size, seed):
    deck = list(range(1, deck_size + 1))
    return shuffledeck(deck, seed)


# Implementing the following Julia function:
# function shuffledeck(deck::Vector{Int}, seed::Int)
#     shuffle(MersenneTwister(seed), deck)
# end
@dispatch(list, int)
def shuffledeck(deck, seed):
    shuffled_deck = deck.copy()
    getrng(seed).shuffle(shuffled_deck)
    return shuffled_deck


class RandoPolicy:
   def __init__(self):
       pass

 # Functions  


class PublicState(PClass):
    game_idx = field(type=int)
    action_history = field(type=list)
    to_play = field(type=list)
    num_route_cards = field(type=int)
    num_unit_cards = field(type=int)
    faceup_spots = field(type=PVector)  # List[Union{Nothing, int}]
    most_clusters_player_idxs = field(type=list)
    num_route_discards = field(type=int)
    num_unit_discards = field(type=int)
    # fig::Fig
    # logged_game_uuid::UUID
    # num_unit_cards::Int
    # player_hands::Vector{PublicPlayerInfo}
    # captured_segments::Vector{CapturedSegment}
    # captured_points::Vector{CapturedPoint}
    # last_to_play::Union{Nothing,Int}
    # terminal::Bool
    # longest_road_player_idxs::Vector{Int}
    # winners::Vector{Int}
    # market_refills::Vector{MarketRefill}

def autoplay(fig, policy):
    g = Game(uuid=uuid4(), fig=fig, num_players=2, seed=random.randint(0, 2**32-1), actions=[])
    s = getstate(g)
    try:
        while not s.terminal:
            a = getnextaction(s, policy)
            s = getnextstate(s, a)
            g.actions.append(a)
    except Exception as e:
        logging.error(f"Something went wrong: {str(e)}", exc_info=True)
    finally:
        return g


@dispatch(Game)
def getstate(game):
    return getstate(game, game.actions)


@dispatch(Game)
def getinitialstate(game):
    return getinitialstate(game, game.fig)


@dispatch(Game, Fig)
def getinitialstate(g, f):
    route_deck = shuffledeck(getnumroutecards(f), g.seed)
    unit_deck = shuffledeck(gettotaldeckcards(f), g.seed)
    route_deck_idx, unit_deck_idx = 0, 0
    player_hands = []
    initial_num_route_choices = getsettingvalue(f, "initial_num_route_choices")
    num_initial_unit_cards = getsettingvalue(f, "num_initial_unit_cards")
    num_segment_pieces_per_player = 20 # getsettingvalue(f, :num_segment_pieces_per_player)
    num_point_pieces_per_player = 9 #getsettingvalue(f, :num_point_pieces_per_player)


    for player_idx in range(g.num_players):
        player_hand = PlayerInfo(
            fig=f,
            player_idx=player_idx,
            new_route_cards=pvector(route_deck[route_deck_idx:(route_deck_idx+(initial_num_route_choices))]),
            route_cards=pvector([]),
            unit_cards=pvector(unit_deck[unit_deck_idx:(unit_deck_idx + num_initial_unit_cards)]),
            completed_routes=[],
            clusters=[],
            completed_clusters=[],
            paths=[],
            points=[],
            num_pieces=num_segment_pieces_per_player,
            num_point_pieces=num_point_pieces_per_player,
            longest_road=[],
            longest_road_len=0
        )
        player_hands.append(player_hand)
        route_deck_idx += initial_num_route_choices
        unit_deck_idx += num_initial_unit_cards

    faceup_spots = getfaceupspots(f, unit_deck, unit_deck_idx)
    unit_deck_idx += 5
    # Implementing the following Julia function:
    # unit_cards = unit_deck[unit_deck_idx:end]
    unit_cards = unit_deck[unit_deck_idx:] if unit_deck_idx < len(unit_deck) else []
    route_cards = route_deck[route_deck_idx:]

    return State(
        game=g, 
        terminal=False, 
        action_history=[],
        route_cards=pvector(route_cards),
        route_discards=pvector([]),
        player_hands=pvector(player_hands),
        unit_cards=pvector(unit_cards),
        unit_discards=pvector([]),
        faceup_spots=pvector(faceup_spots),
        most_clusters_player_idxs=[],
    )


# Implementing the following Julia function:
# function getfaceupspots(f, unit_deck, unit_deck_idx)
#     num_faceup_spots = getsettingvalue(f, :num_faceup_spots)
#     unit_deck[unit_deck_idx:(unit_deck_idx+(num_faceup_spots - 1))]
# end
def getfaceupspots(f, unit_deck, unit_deck_idx):
    num_faceup_spots = getsettingvalue(f, 'num_faceup_spots')
    if num_faceup_spots is None:
        raise ValueError("Setting 'num_faceup_spots' not found in board config.")
    return unit_deck[unit_deck_idx:(unit_deck_idx + (num_faceup_spots - 1))] if unit_deck_idx < len(unit_deck) else []


@dispatch(Game, list)
def getstate(game, actions):
    return reduce(getnextstate, actions, getinitialstate(game))


@dispatch(State, AltAction)
def getnextstate(s, action):
    action_type = getactiontype(action.action_name)
    next = getnextstate(s, action, action_type)
    next = next.set(action_history=(next.game.actions + [action]))
    return next


@dispatch(State, AltAction, NoAction)
def getnextstate(s, action, action_type):
    return s


# Implementing the following Julia function:
# function getnextstate(s::State, a::Action, ::Val{:CLAIM_POINT})
#     player_hand_idx = findfirst(p -> p.player_idx == a.player_idx, s.player_hands)
#     player_hand = s.player_hands[player_hand_idx]
#     @reset player_hand.num_point_pieces = player_hand.num_point_pieces - 1
#     new_unit_cards, new_discards = removecombo(player_hand, a.unit_combo)
#     @reset s.unit_discards = [s.unit_discards..., new_discards...]
#     @reset player_hand.unit_cards = new_unit_cards
#     @reset player_hand.points = [player_hand.points..., a.point_uuid]
#     @reset player_hand.completed_clusters = getcompletedclusters(s.fig, player_hand)
#     @reset s.player_hands = [p.player_idx == a.player_idx ? player_hand : p for p in s.player_hands]
#     @reset s.most_clusters_player_idxs = getmostclustersplayeridxs(s.player_hands)
#     s
# end
@dispatch(State, AltAction, ClaimPointAction)
def getnextstate(s, action, action_type):
    player_hand_idx = next((i for i, p in enumerate(s.player_hands) if p.player_idx == action.player_idx), None)
    if player_hand_idx is None:
        raise ValueError(f"Player index {action.player_idx} not found in player hands.")
    
    player_hand = s.player_hands[player_hand_idx]
    # @reset player_hand.num_point_pieces = player_hand.num_point_pieces - 1
    player_hand = player_hand.set(num_point_pieces=player_hand.num_point_pieces - 1)

    # new_unit_cards, new_discards = removecombo(player_hand, a.unit_combo)
    new_unit_cards, new_discards = pvector([]), pvector([])
    if action.unit_combo:
        new_unit_cards, new_discards = removecombo(player_hand, action.unit_combo)
    # @reset s.unit_discards = [s.unit_discards..., new_discards...]
    s = s.set(unit_discards=s.unit_discards.extend(new_discards))
    # @reset player_hand.unit_cards = new_unit_cards
    player_hand = player_hand.set(unit_cards=new_unit_cards)
    # @reset player_hand.points = [player_hand.points..., a.point_uuid]
    player_hand = player_hand.set(points=player_hand.points + [action.point_uuid])
    # @reset player_hand.completed_clusters = getcompletedclusters(s.fig, player_hand)
    player_hand = player_hand.set(completed_clusters=getcompletedclusters(s.game.fig, player_hand))
    # @reset s.player_hands = [p.player_idx == a.player_idx ? player_hand : p for p in s.player_hands]
    s = s.transform(
        ('player_hands', player_hand_idx),
        player_hand.set(player_idx=player_hand.player_idx),
    )
    # @reset s.most_clusters_player_idxs = getmostclustersplayeridxs(s.player_hands)
    s = s.set(most_clusters_player_idxs=getmostclustersplayeridxs(s.player_hands))
    
    return s


# Implementing the following Julia function:
# function getmostclustersplayeridxs(player_hands::Vector{PlayerInfo})
#     most_clusters = maximum([length(p.completed_clusters) for p in player_hands])
#     if iszero(most_clusters)
#         return Int[]
#     end
#     [p.player_idx for p in player_hands if length(p.completed_clusters) == most_clusters]
# end
def getmostclustersplayeridxs(player_hands):
    most_clusters = max(len(p.completed_clusters) for p in player_hands)
    if most_clusters == 0:
        return []
    return [p.player_idx for p in player_hands if len(p.completed_clusters) == most_clusters]


# Implementing the following Julia function:
# function getcompletedclusters(fig::Fig, player_hand::PlayerInfo; log=false)
#     (; clusters) = fig.board_config
#     completed = filter(clusters) do cluster
#         for point in cluster.points
#             if !in(point, player_hand.points)
#                 return false
#             end
#         end
#         true
#     end
#     if isempty(completed)
#         return UUID[]
#     end
#     [x.uuid for x in completed]
# end
def getcompletedclusters(fig, player_hand, log=False):
    clusters = fig.board_config.clusters
    completed = [
        cluster
        for cluster in clusters
        if all(point in player_hand.points for point in cluster.points)
    ]
    if not completed:
        return []
    return [x.uuid for x in completed]

# Implementing the following Julia function:
# function removecombo(player_hand::PlayerInfo, combo::String)
#     (; unit_cards) = player_hand
#     unit_cards_to_remove = parse.(Int, split(combo, "-"))
#     new_unit_cards = filter(x->!in(x, unit_cards_to_remove), unit_cards)
#     new_discards = unit_cards_to_remove
#     new_unit_cards, new_discards
# end
def removecombo(player_hand, combo):
    if not combo:
        return player_hand.unit_cards, []
    unit_cards_to_remove = list(map(int, combo.split("-")))
    new_unit_cards = pvector([x for x in player_hand.unit_cards if x not in unit_cards_to_remove])
    new_discards = pvector([x for x in unit_cards_to_remove if x in player_hand.unit_cards])
    if len(new_discards) != len(unit_cards_to_remove):
        raise ValueError(f"Discarded cards {new_discards} do not match combo {combo}")
    return new_unit_cards, new_discards


@dispatch(State, AltAction, DrawUnitFaceupAction)
def getnextstate(s, action, action_type):
    pass
# Implementing the following Julia function:
# function getnextstate(s::State, a::Action, ::Val{:DRAW_UNIT_FACEUP})
#     player_hand_idx = findfirst(p -> p.player_idx == a.player_idx, s.player_hands)
#     player_hand = s.player_hands[player_hand_idx]
#     player_new_unit_idx = s.faceup_spots[a.draw_faceup_spot_num]

#     if isempty(s.unit_cards)
#         # TODO: do we need to reshuffle the unit discards?
#         @reset s.faceup_spots[a.draw_faceup_spot_num] = nothing
#     else
#         @reset s.faceup_spots[a.draw_faceup_spot_num] = s.unit_cards[end]
#         @reset s.unit_cards = s.unit_cards[1:end-1]
#     end

#     s = recycleunitdiscardsifneeded(s)
#     @reset s.player_hands[player_hand_idx].unit_cards = [player_hand.unit_cards..., player_new_unit_idx]
#     num_market_refills = 0

#     num_faceup_spots = getsettingvalue(s.fig, :num_faceup_spots)

#     s
# end
    player_hand_idx = next((i for i, p in enumerate(s.player_hands) if p.player_idx == action.player_idx), None)
    if player_hand_idx is None:
        raise ValueError(f"Player index {action.player_idx} not found in player hands.")
    player_hand = s.player_hands[player_hand_idx]
    player_new_unit_idx = s.faceup_spots[action.draw_faceup_spot_num-1]

    if not s.unit_cards:
        # TODO: do we need to reshuffle the unit discards?
        # @reset s.faceup_spots[a.draw_faceup_spot_num] = nothing
        s = s.set(
            faceup_spots = s.faceup_spots.set(action.draw_faceup_spot_num-1, None)
        )
    else:
        # Implementing the following Julia code:
        # @reset s.faceup_spots[a.draw_faceup_spot_num] = s.unit_cards[end]
        # @reset s.unit_cards = s.unit_cards[1:end-1]
        s = s.set(
            faceup_spots = s.faceup_spots.set(action.draw_faceup_spot_num-1, s.unit_cards[-1])
        )
        s = s.set(unit_cards = s.unit_cards[:-1])
    
    # s = recycleunitdiscardsifneeded(s)
    unit_cards = player_hand.unit_cards
    s = s.transform(
        ('player_hands', player_hand_idx),
        player_hand.set(unit_cards=unit_cards.append(player_new_unit_idx)),
    )
    num_market_refills = 0
    num_faceup_spots = getsettingvalue(s.game.fig, 'num_faceup_spots')
    return s


# Implementing the following Julia function:
# function getsettingvalue(f::Fig, setting_name::Symbol)
#     for setting in f.board_config.settings
#         if Symbol(setting.name) === setting_name
#             return JSON3.read(setting.value_json)
#         end
#     end
#     nothing
# end
@dispatch(Fig, str)
def getsettingvalue(f, setting_name):
    for setting in f.board_config.settings:
        if setting.name == setting_name:
            return json.loads(setting.value_json)
    return None

@dispatch(State, str)
def getsettingvalue(s, setting_name):
    return getsettingvalue(s.game.fig, setting_name)


@dispatch(State, AltAction, DrawUnitDeckAction)
def getnextstate(s, action, action_type):
# Implementing the following Julia function:
# function getnextstate(s::State, a::Action, ::Val{:DRAW_UNIT_DECK})
#     player_hand_idx = findfirst(p -> p.player_idx == a.player_idx, s.player_hands)
#     player_hand = s.player_hands[player_hand_idx]
#     @assert anyunitcardsleft(s) "Unit and discard decks are empty. Action illegal!"
#     s = recycleunitdiscardsifneeded(s)
#     drawn_card = s.unit_cards[end]
#     @reset s.unit_cards = s.unit_cards[1:end-1]
#     @reset s.player_hands[player_hand_idx].unit_cards = [player_hand.unit_cards..., drawn_card]
#     s = recycleunitdiscardsifneeded(s)
#     s
# end
    player_hand_idx = next((i for i, p in enumerate(s.player_hands) if p.player_idx == action.player_idx), None)
    if player_hand_idx is None:
        raise ValueError(f"Player index {action.player_idx} not found in player hands.")
    
    ## if not anyunitcardsleft(s):
    ##     raise ValueError("Unit and discard decks are empty. Action illegal!")
    ## s = recycleunitdiscardsifneeded(s)
    drawn_card = s.unit_cards[-1]
    s = s.set(unit_cards = s.unit_cards[:-1])
    
    # @reset s.player_hands[player_hand_idx].unit_cards = [player_hand.unit_cards..., drawn_card]
    player_hand = s.player_hands[player_hand_idx]
    unit_cards = player_hand.unit_cards
    s = s.transform(
        ('player_hands', player_hand_idx), 
        player_hand.set(unit_cards=unit_cards.append(drawn_card)),
    )

    ## s = recycleunitdiscardsifneeded(s)
    return s


@dispatch(State, AltAction, RouteDiscardAction)
def getnextstate(s, action, action_type):
# Implementing the following Julia function:
# function getnextstate(s::State, a::Action, ::Val{:ROUTE_DISCARD})
#     player_hand = s.player_hands[a.player_idx]
#     route_card_hand_nums = collect(a.return_route_cards)
#     return_route_card_nums = player_hand.new_route_cards[route_card_hand_nums]
#     chosen = setdiff(Set(player_hand.new_route_cards), Set(return_route_card_nums))
#     existing_route_cards = player_hand.route_cards
#     @reset s.player_hands[a.player_idx].route_cards = [existing_route_cards..., chosen...]
#     @reset s.route_discards = [s.route_discards..., return_route_card_nums...]
#     @reset s.player_hands[a.player_idx].new_route_cards = []
#     s
# end
    player_hand_idx = next((i for i, p in enumerate(s.player_hands) if p.player_idx == action.player_idx), None)
    if player_hand_idx is None:
        raise ValueError(f"Player index {action.player_idx} not found in player hands.")
    
    player_hand = s.player_hands[player_hand_idx]
    route_card_hand_nums = list(action.return_route_cards)
    return_route_card_nums = [player_hand.new_route_cards[i] for i in route_card_hand_nums]
    chosen = set(list(player_hand.new_route_cards)) - set(return_route_card_nums)
    
    print(f"new_route_cards: {list(player_hand.new_route_cards)}")
    print(f"return_route_card_nums: {return_route_card_nums}")
    print(f"Chosen route cards: {chosen}")
    
    # @reset s.player_hands[a.player_idx].route_cards = [existing_route_cards..., chosen...]
    print(f"Existing route cards: {list(player_hand.route_cards)}")
    player_hand = player_hand.set(route_cards=player_hand.route_cards + pvector(list(chosen)))
    print(f"New route cards: {list(player_hand.route_cards)}")
    # @reset s.route_discards = [s.route_discards..., return_route_card_nums...]
    s = s.set(route_discards=s.route_discards + return_route_card_nums)
    # @reset s.player_hands[a.player_idx].new_route_cards = []
    player_hand = player_hand.set(new_route_cards=pvector([]))
    print(f"New route cards: {list(player_hand.route_cards)}")

    s = s.transform(('player_hands', player_hand_idx), player_hand)

    return s


@dispatch(State, RandoPolicy)
def getnextaction(s, policy):
    player_idx = gettoplay(s)[0]
    legal_actions = getlegalactionsforplayer(s, player_idx, None, None)
    action_spec = legal_actions[getrng(s.game.seed).randint(0, len(legal_actions) - 1)]

    if action_spec.action_name == "ROUTE_DISCARD":
        return AltAction(
            action_name="ROUTE_DISCARD", 
            player_idx=player_idx,
            return_route_cards=[0],
        )
    
    if action_spec.action_name == "DRAW_UNIT_FACEUP":
        draw_faceup_spot_num = 1
        return AltAction(
            action_name="DRAW_UNIT_FACEUP", 
            player_idx=player_idx,
            draw_faceup_unit_card_num=s.faceup_spots[draw_faceup_spot_num-1],
            draw_faceup_spot_num=draw_faceup_spot_num,
        )

    if action_spec.action_name == "DRAW_UNIT_DECK":
        return AltAction(
            action_name="DRAW_UNIT_DECK", 
            player_idx=player_idx,
        )
    
    if action_spec.action_name == "CLAIM_POINT":
        point = action_spec.points[getrng(s.game.seed).randint(0, len(action_spec.points) - 1)]
        return AltAction(
            action_name="CLAIM_POINT",
            player_idx=player_idx,
            point_uuid=str(point.point_uuid),
            unit_combo=point.default_combo,
        )
    
    return None



@dispatch(State)
def getpublicstate(s):
    return PublicState(
        game_idx=len(s.game.actions),
        action_history=s.game.actions,
        to_play=gettoplay(s),
        num_route_cards=len(s.route_cards),
        num_route_discards=len(s.route_discards),
        num_unit_cards=len(s.unit_cards),
        num_unit_discards=len(s.unit_discards),
        faceup_spots=s.faceup_spots,
        most_clusters_player_idxs=s.most_clusters_player_idxs,
    )


# Implementing the following Julia function:
# getlastaction(s::State) = isempty(s.actions) ? nothing : s.actions[end]
def getlastaction(s):
    if not s.game.actions:
        return None
    return s.game.actions[-1]


# Function implements the following Julia function:
# function getlastactionkey(s)
#     last_action = getlastaction(s)
#     if isnothing(last_action)
#         return nothing
#     end
#     Val(Symbol(last_action.action_name))
# end
@dispatch(State)
def getlastactiontype(s):
    last_action = getlastaction(s)
    if last_action is None:
        return NoAction()
    return getactiontype(last_action.action_name)


def getactiontype(action_name):
    match action_name:
        case "ROUTE_DISCARD":
            return RouteDiscardAction()
        case "DRAW_UNIT_DECK":
            return DrawUnitDeckAction()
        case "DRAW_UNIT_FACEUP":
            return DrawUnitFaceupAction()
        case "CLAIM_POINT":
            return ClaimPointAction()
    
    return NoAction()


# Function implements the following Julia function:
# getlastplayeridxplus1(s) = mod1(getlastaction(s).player_idx + 1, s.game.num_players)
def getlastplayeridxplus1(s):
    last_action = getlastaction(s)
    if last_action is None:
        return 0
    return (last_action.player_idx + 1) % s.game.num_players


@dispatch(State)
def gettoplay(s):
    return gettoplay(s, getlastactiontype(s))


@dispatch(State, object)
def gettoplay(s, last_action_type):
    return [getlastplayeridxplus1(s)]


# Implementing the following Julia function:
@dispatch(State, NoAction)
# function gettoplay(s::State, last_action_key::Nothing)
#     if getsettingvalue(s, :action_route_discard)
#         return collect(1:s.game.num_players)
#     end
#     [getfirstplayeridx(s.game)]
# end
def gettoplay(s, last_action_type):
    if getsettingvalue(s, 'action_route_discard'):
        return list(range(1, s.game.num_players + 1))
    return [getfirstplayeridx(s.game)]


def getrng(seed):
    rng = random.Random()
    rng.seed(seed)
    return rng


# Implementing the following Julia function:
# getfirstplayeridx(g::Game) = rand(getrng(g), 1:g.num_players)
def getfirstplayeridx(g):
    return getrng(g.seed).randint(0, g.num_players-1)

# @dispatch(AltState, RouteDiscardAction)
# def gettoplay(s, action_type):
#     return [1]


# @dispatch(AltState, DrawUnitDeckAction)
# def gettoplay(s, action_type):
#     return [2]

# Implementing the following Julia function:
# function getlegalactions(s::State, player_idx::Int)
#     # Causal function chain: gettoplay => getlegalactions =>  isterminal
#     if s.terminal
#         return []
#     end
#     if !in(player_idx, gettoplay(s))
#         return []
#     end
#     getlegalactionsforplayer(s::State, player_idx, getrepeatplayerkey(s, player_idx), getlastactionkey(s))
# end
def getlegalactions(s, player_idx):
    # Causal function chain: gettoplay => getlegalactions =>  isterminal
    if s.terminal:
        return []
    if player_idx not in gettoplay(s):
        return []
    return getlegalactionsforplayer(s, player_idx, getrepeatplayerbooltype(s, player_idx), getlastactiontype(s))

# Implementing the following Julia function:
# function getrepeatplayerkey(s::State, player_idx)
#     last_action = getlastaction(s)
#     if isnothing(last_action)
#         return Val(false)
#     end
#     Val(player_idx == last_action.player_idx)
# end
def getrepeatplayerbooltype(s, player_idx):
    last_action = getlastaction(s)
    if last_action is None:
        return getbooltype(False)
    return getbooltype(player_idx == last_action.player_idx)


# Implementing the following Julia function:
# function getlegalactionsforplayer(s::State, player_idx, repeat_player, last_action)
#     min_initial_routes = getsettingvalue(s.fig, :min_initial_routes)
#     min_chosen_routes = getsettingvalue(s.fig, :min_chosen_routes)

#     # Initial Route Card Discard
#     if getsettingvalue(s, :action_route_discard) && length(s.action_history) < s.game.num_players
#         return [
#             ActionSpec(
#                 player_idx=player_idx, 
#                 action_name=ROUTE_DISCARD,
#                 return_route_option_sets=getrouteoptionsets(s, player_idx, min_initial_routes),
#             )
#         ]
#     end

#     action_specs = ActionSpec[]
#     if getsettingvalue(s, :action_draw_unit_faceup) && !isempty(getvalidspotnums(s))
#         push!(
#             action_specs, 
#             ActionSpec(
#                 player_idx=player_idx, 
#                 action_name=DRAW_UNIT_FACEUP,
#                 draw_faceup_spots=Dict((spot_num, s.faceup_spots[spot_num]) for spot_num in getvalidspotnums(s)),
#             )
#         )
#     end

#     if getsettingvalue(s, :action_draw_route) && (length(s.route_cards) + length(s.route_discards)) >= min_chosen_routes
#         push!(action_specs, ActionSpec(s.fig, player_idx, :DRAW_ROUTE))
#     end

#     if getsettingvalue(s, :action_draw_unit_deck) && (!isempty(s.unit_cards) || !isempty(s.unit_discards))
#         push!(action_specs, ActionSpec(s.fig, player_idx, :DRAW_UNIT_DECK))
#     end

#     if getsettingvalue(s, :action_claim_path)
#         append!(action_specs, getclaimpathactionspecs(s, player_idx))
#     end

#     if getsettingvalue(s.fig, :action_claim_point)
#         append!(action_specs, getclaimpointactionspecs(s, player_idx))
#     end

#     action_specs
# end
@dispatch(State, int, object, object)
def getlegalactionsforplayer(s, player_idx, repeat_player, last_action):
    min_initial_routes = getsettingvalue(s, 'min_initial_routes')
    min_chosen_routes = getsettingvalue(s, 'min_chosen_routes')

    # Initial Route Card Discard
    if getsettingvalue(s, 'action_route_discard') and len(s.action_history) < s.game.num_players:
        return [
            AltAction(
                player_idx=player_idx,
                action_name="ROUTE_DISCARD",
                return_route_cards=getrouteoptionsets(s, player_idx, min_initial_routes),
            )
        ]

    action_specs = []
    if getsettingvalue(s, 'action_draw_unit_faceup') and s.faceup_spots:
        action_specs.append(
            AltAction(
                player_idx=player_idx,
                action_name="DRAW_UNIT_FACEUP",
                draw_faceup_spot_num=getvalidspotnums(s),
            )
        )

    if getsettingvalue(s, 'action_draw_route') and (len(s.route_cards) + len(s.route_discards)) >= min_chosen_routes:
        action_specs.append(AltAction(player_idx=player_idx, action_name="DRAW_ROUTE"))

    if getsettingvalue(s, 'action_draw_unit_deck') and (s.unit_cards or s.unit_discards):
        action_specs.append(AltAction(player_idx=player_idx, action_name="DRAW_UNIT_DECK"))

    if getsettingvalue(s, 'action_claim_path'):
        # action_specs.extend(getclaimpathactionspecs(s, player_idx))
        pass

    if getsettingvalue(s, 'action_claim_point'):
        action_specs.extend(getclaimpointactionspecs(s, player_idx))

    return action_specs


# Implementing the following Julia function:
# function getclaimpointactionspecs(s::State, player_idx::Int; log=false)
#     action_specs = ActionSpec[]
#     available_point_statuses = getavailablepoints(s, player_idx)
#     points = map(available_point_statuses) do available_point_status
#         (; uuid, sample_fulfillment) = available_point_status
#         fulfillment_sorted = sample_fulfillment
#         sample_fulfillment = [x.unit_card_num for x in fulfillment_sorted]
#         fulfillment_str = join(sample_fulfillment, "-")
#         PointCombos(uuid, fulfillment_str, sample_fulfillment)
#     end
#     if !isempty(points)
#         push!(
#             action_specs,
#             ActionSpec(
#                 action_name=CLAIM_POINT,
#                 player_idx=player_idx,
#                 points=points,
#             )
#         )
#     end
#     action_specs
# end
def getclaimpointactionspecs(s, player_idx, log=False):
    action_specs = []
    available_point_statuses = getavailablepoints(s, player_idx)
    
    #     points = map(available_point_statuses) do available_point_status
    #         (; uuid, sample_fulfillment) = available_point_status
    #         fulfillment_sorted = sample_fulfillment
    #         sample_fulfillment = [x.unit_card_num for x in fulfillment_sorted]
    #         fulfillment_str = join(sample_fulfillment, "-")
    #         PointCombos(uuid, fulfillment_str, sample_fulfillment)
    #     end

    def process_point_status(available_point_status):
        uuid = available_point_status['uuid']
        sample_fulfillment = available_point_status['sample_fulfillment']
        fulfillment_sorted = sample_fulfillment
        sample_fulfillment = [x['unit_card_num'] for x in fulfillment_sorted]
        fulfillment_str = '-'.join(map(str, sample_fulfillment))
        return PointCombos(
            point_uuid=uuid,
            default_combo=fulfillment_str,
            sample_fulfillment=sample_fulfillment
        )

    point_combos = list(map(process_point_status, available_point_statuses))
    
    if point_combos:
        action_specs.append(
            ActionSpec(
                action_name="CLAIM_POINT",
                player_idx=player_idx,
                points=point_combos,
            )
        )
    
    return action_specs


# Implementing the following Julia function:
# function getavailablepoints(s::State, player_num::Int)
#     point_statuses = map(getpotentialpointuuids(s, player_num)) do point_uuid
#         getpointstatus(s, player_num, point_uuid)
#     end
#     sort(filter(x -> x.fulfillable, point_statuses); by=x -> x.uuid)
# end
def getavailablepoints(s, player_num):
    point_statuses = [
        getpointstatus(s, player_num, point_uuid)
        for point_uuid in getpotentialpointuuids(s, player_num)
    ]
    return sorted(
        filter(lambda x: x['fulfillable'], point_statuses),
        key=lambda x: x['uuid']
    )

# Implementing the following Julia function:
# function getpointstatus(s::State, player_idx::Int, point_uuid::UUID)
#     balance = s.player_hands[player_idx].unit_cards
#     fulfillment = OrderedPointFullfillment[]
#     if !isempty(balance)
#         push!(fulfillment, OrderedPointFullfillment(balance[1]))
#     end
#     PointStatus(point_uuid, true, fulfillment)
# end
def getpointstatus(s, player_idx, point_uuid):
    balance = s.player_hands[player_idx].unit_cards
    fulfillment = []
    if balance:
        fulfillment.append({'unit_card_num': balance[0]})
    return {
        'uuid': point_uuid,
        'fulfillable': True,
        'sample_fulfillment': fulfillment
    }

# Implementing the following Julia function:
# function getpotentialpointuuids(s::State, player_num::Int)
#     (; num_point_pieces) = s.player_hands[player_num]
#     setdiff(
#         Set(getnodeuuids(s.fig, num_point_pieces)),
#         Set(getunavailablepoints(s)),
#     ) |> collect
# end
def getpotentialpointuuids(s, player_num):
    num_point_pieces = s.player_hands[player_num].num_point_pieces
    return list(
        set(getnodeuuids(s.game.fig, num_point_pieces)) -
        set(getunavailablepoints(s))
    )

# Implementing the following Julia function:
# function getnodeuuids(f::Fig, remaining_pieces::Int)
#     point_capture_unit_count = getsettingvalue(f, :point_capture_unit_count)
#     if point_capture_unit_count <= remaining_pieces
#         return [p.uuid for p in f.board_config.points]
#     end
#     []
# end
def getnodeuuids(f, remaining_pieces):
    point_capture_unit_count = getsettingvalue(f, 'point_capture_unit_count')
    # print(f"f.board_config: ", f.board_config)
    # print(f"f.board_config: ", f.board_config.points)
    if point_capture_unit_count <= remaining_pieces:
        return [p.uuid for p in f.board_config.points]
    return []


# Implementing the following Julia function:
# function getunavailablepoints(s::State)
#     unavailable_points = []
#     for hand in s.player_hands
#         for point_uuid in hand.points
#             push!(unavailable_points, point_uuid)
#         end
#     end
#     unavailable_points
# end
def getunavailablepoints(s):
    unavailable_points = []
    for hand in s.player_hands:
        for point_uuid in hand.points:
            unavailable_points.append(point_uuid)
    return unavailable_points


def getstateidx(s):
    return len(s.action_history)


def printplayer(s, player_idx):
    hand = s.player_hands[player_idx]
    legal_actions = getlegalactions(s, player_idx)
    print(f"~~~~~~~~~~~~ P{player_idx} ~~~~~~~~~~~~")
    print(f"units:           {list(hand.unit_cards)}")
    if getsettingvalue(s, "route_scoring"):
        print(f"routes:          {list(hand.route_cards)} choices:{list(hand.new_route_cards)}")
    print(f"captured points: {list(str(p) for p in hand.points)}")
    print(f"legal actions:   {list(a.action_name for a in legal_actions)}")


def printstate(s):
    hand1 = s.player_hands[1]
    state_idx = getstateidx(s)
    print(f"*************** State {state_idx} ***************")
    print(f"Route Deck:      {list(s.route_cards)}")
    print(f"Route Disc:      {list(s.route_discards)}")
    print(f"Unit Deck:       ...{list(s.unit_cards[60:])}")
    print(f"Unit Disc:       {list(s.unit_discards)}")
    print(f"FaceUp:          {list(s.faceup_spots)}")
    print(f"ToPlay:          {gettoplay(s)}")
    for i in range(s.game.num_players):
        printplayer(s, i)
    print(f"****************************************\n")


def printaction(a, i):
    print(f"\n\n*************** Action {i} ***************")
    print(f"{a}")
    print(f"****************************************\n\n\n")