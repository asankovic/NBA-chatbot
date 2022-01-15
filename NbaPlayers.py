import pandas as pd
import os.path
from os import path
import NbaScraper

class Player:
	def __init__(self, **kwargs):
		self.name = kwargs.get('name') 
		self.team = kwargs.get('team') 
		self.age = int(kwargs.get('age')) 	
		self.wins = kwargs.get('w')	
		self.loses = kwargs.get('l')	
		self.minutes_played = kwargs.get('mins')	
		self.field_goal_made = kwargs.get('fgm')	
		self.field_goal_attempt = kwargs.get('fga')	
		self.field_goal_3_made = kwargs.get('fg3m')
		self.field_goal_3_attempt = kwargs.get('fg3a')	
		self.free_throws_made = kwargs.get('ftm')	
		self.free_throws_attempt = kwargs.get('fta')	
		self.off_rebound = kwargs.get('oreb')	
		self.def_rebound = kwargs.get('dreb')	
		self.assists = kwargs.get('ast')
		self.turnovers = kwargs.get('tov')	
		self.steals = kwargs.get('stl')	
		self.blocks = kwargs.get('blk')	
		self.points = kwargs.get('pts')
		
		self.games_played = self.wins + self.loses
		self.win_percentage = safe_div(self.wins, self.games_played)
		self.field_goal_percentage = safe_div(self.field_goal_made, self.field_goal_attempt)
		self.field_goal_3_percentage = safe_div(self.field_goal_3_made, self.field_goal_3_attempt)
		self.free_throws_percentage = safe_div(self.free_throws_made, self.free_throws_attempt)
		self.rebounds = self.off_rebound + self.def_rebound

def safe_div(x,y):
    if y == 0:
        return 0
    return x / y	


players = {}
file = 'player_stats.csv'

def format():    
        df = pd.read_csv(file, delimiter = ',')
        for index, row in df.iterrows():
                new_player = Player(
                    name = row['PLAYER_NAME'],
                    team = row['TEAM_ABBREVIATION'],
                    age = row['AGE'],
                    w = row['W'],
                    l = row['L'],
                    mins = row['MIN'],
                    fgm = row['FGM'],
                    fga = row['FGA'],
                    fg3m = row['FG3M'],
                    fg3a = row['FG3A'],
                    ftm = row['FTM'],
                    fta = row['FTA'],
                    oreb = row['OREB'],
                    dreb = row['DREB'],
                    ast = row['AST'],
                    tov = row['TOV'],
                    stl = row['STL'],
                    blk = row['BLK'],
                    pts = row['PTS'])
                players[new_player.name.lower()] = new_player

def setup():
    if path.exists(file):
        format()
    else:
        NbaScraper.scrape()
        format()
