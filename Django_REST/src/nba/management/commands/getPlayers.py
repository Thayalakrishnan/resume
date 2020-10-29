from django.core.management.base import BaseCommand
from nba.serializers import PlayerSerializer
from nba_api.stats.static import players
from nba_api.stats.endpoints.commonplayerinfo import CommonPlayerInfo
from time import sleep
import sys
import json

json_path = '\\'.join(['C:','Python_Projects','DjangoREST','src','nba','management','commands','player_dicts.txt'])
dink = '#############################################################################'
spoof_data = [0, ' ', '2019-20', 0, 0, 0, 0]
spoof_header = ['PLAYER_ID', 'PLAYER_NAME', 'TimeFrame', 'PTS', 'AST', 'REB', 'PIE']

def get_pcommon(id):
    player = CommonPlayerInfo(player_id=id).common_player_info.get_dict()
    headers, data = player["headers"], player["data"][0]
    return dict(zip(headers, data))

def get_pheadline(id):
    player = CommonPlayerInfo(player_id=id).player_headline_stats.get_dict()
    try:
        headers, data = player["headers"], player["data"][0]
    except IndexError:
        headers, data = spoof_header, spoof_data
    player_dict = dict(zip(headers, data))
    player_dict['TIMEFRAME'] = player_dict.pop('TimeFrame')
    return player_dict


def lower_keys(player_dict):
    keys_lower = [k.lower() for k in player_dict.keys()]
    for key in keys_lower:
        player_dict[key] = player_dict.pop(key.upper())
    return player_dict

def func_start_stop(func):
    def func_wrapper():
        print(f'{func.__name__} started')
        func()
        print(f'{func.__name__} finished')
        return 
    return func_wrapper

#@func_start_stop
def grab_players():
    print(dink)
    print(f'Player Dictionary Started')
    lk , gc, gh = lower_keys, get_pcommon, get_pheadline
    all_p = players.get_active_players()
    for p in all_p:
        print(f'Dict: {p["full_name"]} | {p["id"]}')
        p.update(lk(gc(int(p['id']))))
        p.update(lk(gh(int(p['id']))))
        sleep(.5)
    print(dink)
    print(f'Player Dictionary Created')
    with open(json_path, 'w') as file:
        json.dump(all_p, file)
    print(f'Saved to JSON')
    return all_p


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        print(dink)
        self.stdout.write(self.style.SUCCESS(f'Importing'))
        #all_players = grab_players()
        with open(json_path, 'r') as file:
            all_players = json.load(file)
        valid_players =  [pl for pl in all_players if pl['team_id']!=0 if pl['player_id']!=0]
        nbaplayer = PlayerSerializer(data=valid_players, many=True, partial=True)
        nbaplayer.is_valid()
        print(nbaplayer.errors)
        #sleep(1)
        nbaplayer.save()
        self.stdout.write(self.style.SUCCESS(f'All Players Imported!'))