from typing import List, Optional
from typeguard import typechecked

from rstt.stypes import SPlayer, Score
import rstt.config as cfg 

class Match():
    @typechecked
    def __init__(self, teams: List[List[SPlayer]], tracking: Optional[bool]=None) -> None:
        self.__teams = teams
        self.__scores = None
        self.__tracking = tracking if tracking is not None else cfg.MATCH_HISTORY
        
    # --- getter --- #
    def teams(self) -> List[List[SPlayer]]:
        return self.__teams
    
    def players(self) -> List[List[SPlayer]]:
        return [player for team in self.__teams for player in team]

    def opponents(self, player: SPlayer) -> List[SPlayer]:
        return [p for p in self.players() if p not in self.teammates(player)]
    
    def teammates(self, player: SPlayer) -> List[SPlayer]:
        for team in self.players():
            if player in team:
                return [p for p in team if p != player]
    
    def scores(self) -> Score:
        return self.__scores
    
    def score(self, player: SPlayer) -> float:
        for team, score in zip(self.__teams, self.__scores):
            if player in team:
                return score
            
    def ranks(self) -> List[int]:
        if not self.__scores:
            msg = ""
            raise RuntimeError(msg)
        return [len([other for other in self.__scores if other > value]) + 1 for value in self.__scores]
    
    # --- user interface --- #
    def live(self) -> bool:
        return True if self.__scores is None else False
    
    # --- internal mechanism --- #
    def __set_result(self, result: Score):
        # bunch of errors to raise
        if self.__scores is not None:
            msg = f'Attempt to assign a score to a game that has already one {self}'
            raise RuntimeError(msg)
        if not isinstance(result, list):
            msg  = f"result must be instance of List[float], received {type(result)}"
            raise TypeError(msg)
        if not isinstance(result[0], float):
            msg = f'result must be instance of List[float], received List[{type(result[0])}]'
            raise TypeError(msg)
        if len(result) != len(self._Match__teams):
            msg = f"""result lenght does not match number of teams,
                    len(result) == {len(result)}, excepted: {len(self._Match__teams)}"""
            raise ValueError(msg)
        
        # actual result assignement
        self.__scores = result
        
        # player may track match history
        if self.__tracking:
            self.__update_players_history()
   
    def __update_players_history(self):
        for player in self.players():
            try:
                player.add_game(self)
            except AttributeError:
                pass # ??? raise warning
            
    # --- magic methods --- #
    def __repr__(self) -> str:
        return str(self)
    
    def __str__(self) -> str:
        return f"{type(self)} - teams: {self.__teams}, scores: {self.__scores}"
         
    def __contains__(self, player: SPlayer) -> bool:
        return player in self.players()
    
    
class Duel(Match):
    def __init__(self, player1: SPlayer, player2: SPlayer, tracking: Optional[bool]=None) -> None:
        tracking = tracking if tracking is not None else cfg.DUEL_HISTORY
        super().__init__(teams=[[player1], [player2]], tracking=tracking)
        
    # --- getter --- #
    def player1(self) -> SPlayer:
        return self._Match__teams[0][0]
    
    def player2(self) -> SPlayer:
        return self._Match__teams[1][0]
    
    def opponent(self, player: SPlayer):
        players = set(self.players())
        players.remove(player) # this can raise a KeyError, which is what we want
        return list(players)[0]
    
    def winner(self) -> SPlayer:
        if not self._Match__scores:
            return None
        if self._Match__scores[0] > self._Match__scores[1]:
            return self._Match__teams[0][0]
        elif self._Match__scores[0] < self._Match__scores[1]:
            return self._Match__teams[1][0]
        else:
            return None
        #return self._Match__teams[0][0] if self._Match__scores[0] > self._Match__scores[1] else self._Match__teams[1][0]
    
    def loser(self) -> SPlayer:
        if not self._Match__scores:
            return None
        if self._Match__scores[0] > self._Match__scores[1]:
            return self._Match__teams[1][0]
        elif self._Match__scores[0] < self._Match__scores[1]:
            return self._Match__teams[0][0]
        else:
            return None
        #return self._Match__teams[0][0] if self._Match__scores[1] > self._Match__scores[0] else self._Match__teams[1][0]
    
    def isdraw(self) -> bool:
        if not self._Match__scores:
            return False
        return True if self._Match__scores[0] == self._Match__scores[1] else False    