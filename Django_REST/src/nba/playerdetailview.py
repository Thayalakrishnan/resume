from .models import Player, Team
from time import sleep
from nba.toolbox import DataReturn, HeaderDataReturn, PrintInLines


#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
'''
accolade counter

playerid = 2544
lebron = getPlayerAccolades(playerid)
counted = CreateCounter(lebron, 4)
{
    'NBA Player of the Week': 63,
    'NBA All-Star Most Valuable Player': 3,
    'NBA Player of the Month': 39,
    'NBA Sporting News Most Valuable Player of the Year': 1,
    'NBA Most Valuable Player': 4,
    'NBA Rookie of the Month': 6,
    'All-NBA': 16,
    'NBA Rookie of the Year': 1,
    'All-Defensive Team': 6,
    'Olympic Gold Medal': 2,
    'Olympic Bronze Medal': 1,
    'NBA Finals Most Valuable Player': 3,
    'All-Rookie Team': 1,
    'NBA Sporting News Rookie of the Year': 1
}
'''

awards_counter = [
    'NBA Rookie of the Year',
    'All-NBA',
    'NBA All-Star Most Valuable Player',
    'Olympic Bronze Medal',
    'NBA Rookie of the Month',
    'NBA Sporting News Rookie of the Year',
    'NBA Most Valuable Player',
    'NBA Finals Most Valuable Player',
    'NBA Player of the Month',
    'Olympic Gold Medal',
    'NBA Player of the Week',
    'NBA Sporting News Most Valuable Player of the Year',
    'All-Rookie Team',
    'All-Defensive Team'
]

## adds one as a counter to be used in a list comprehension
def addOne(dict, value):
    dict[value]+=1
    return None

# returns a dictionary counter
# values are sourced from the given dataset at the given index position
# valus are set to zero
def CreateCounter(dataset, position):
    values = [_[position] for _ in dataset]
    dict_counter = dict.fromkeys(set(values), 0)
    [addOne(dict_counter, _) for _ in values]
    print(dict_counter)
    return dict_counter


def getPlayerPersonalDetails():
    ''' 
    player_id,full_name,first_name,last_name,birthdate,is_active,
    team_id,jersey,from_year,to_year,season_exp,draft_year,draft_round,
    draft_number,height,weight,position,
    '''
    return None


def getPlayerAccolades(player_id):
    from nba_api.stats.endpoints import playerawards as pa
    player = pa.PlayerAwards(player_id=player_id).player_awards
    return DataReturn(player)

def Counter(dic, dataset):
    [dic[_] + 1 for _ in dataset]
    return dic

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
'''
Championship counter 

to find the number of championships a player has, we must
- find the teams that won championships the last few years
    - the TeamDetails will return the year a team won a champhionship and against who
      however, its not a good return value as the year should be given as the season year, instead of a straight up year 
      [[2016, 'Golden State Warriors']]
      we would have to modify the is return value to correct input it when we want to find the roster
- find the rosters and check if the players were on that team
'''
# generate a list of the the nba champions

from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamdetails

teamlist = teams.get_teams()
team_ids = [team['id'] for team in teamlist]

teamid = 1610612737
champs = teamdetails.TeamDetails(team_id=teamid).team_awards_championships.get_dict()
# {'headers': ['YEARAWARDED', 'OPPOSITETEAM'], 'data': [[1958, 'Boston Celtics']]}

headers,data = champs["headers"],champs["data"]
#[[1958, 'Boston Celtics']]


def getChampionships(teamid, arr):
    results = teamdetails.TeamDetails(team_id=teamid).team_awards_championships.get_dict()
    sleep(1)
    headers, data = results["headers"], results["data"]
    if len(data)==0:
        return arr
    elif len(data)==1:
        arr.append(data[0].append(teamid))
        return arr
    else:
        [_.append(teamid) for _ in data]
        arr.extend(data)
        return arr

champlist = []
yeet = [getChampionships(t_id,champlist) for t_id in team_ids]
len(champlist)



#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
''' 
team lineups generator
''' 

from nba_api.stats.endpoints import teamplayerdashboard

lakers = 1610612747
heat = 1610612748

matchup = teamplayerdashboard.TeamPlayerDashboard(team_id=lakers, opponent_team_id=heat,season='2019-20',season_type_all_star="Playoffs")
totals = matchup.players_season_totals.get_dict()
headers,data = totals["headers"],totals["data"]