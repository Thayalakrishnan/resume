from django.core.management.base import BaseCommand
from nba.serializers import TeamSerializer
from nba_api.stats.static import teams
from nba_api.stats.endpoints.teaminfocommon import TeamInfoCommon
from nba_api.stats.endpoints.teamdetails import TeamDetails
from time import sleep

def team_ids_list():
    return [t['id'] for t in teams.get_teams()]

def get_tcommon(id):
    nbateam = TeamInfoCommon(team_id=id).team_info_common.get_dict()
    headers, data = nbateam["headers"], nbateam["data"][0]
    return dict(zip(headers, data))

def get_tdetails(id):
    nbateam = TeamDetails(team_id=id).team_background.get_dict()
    headers, data = nbateam["headers"], nbateam["data"][0]
    return dict(zip(headers, data))

def valid_values(dictionary):
    crap = [' ', '']
    for key, value in dictionary.items():
        if value in crap:
            dictionary[key] = f'No {key}'
        elif value==None and key=='arenacapacity':
            dictionary[key] = f'0'
    return dictionary

def lower_keys(dictionary):
    keys_lower = [k.lower() for k in dictionary.keys()]
    for key in keys_lower:
        dictionary[key] = dictionary.pop(key.upper())
    return dictionary

class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        get_team_ids = team_ids_list()
        for teamid in get_team_ids:
            # build dictionary
            get_team = teams.find_team_name_by_id(teamid)
            self.stdout.write(self.style.NOTICE(f'Begin importing the {get_team["full_name"]}'))
            get_team.update(lower_keys(get_tcommon(teamid)))
            get_team.update(lower_keys(get_tdetails(teamid)))
            get_team = valid_values(get_team)
            #serialize
            nbateam = TeamSerializer(data=get_team, partial=True)
            nbateam.is_valid()
            print(nbateam.errors)
            nbateam.save()
            self.stdout.write(self.style.SUCCESS(f'Imported The {get_team["full_name"]}'))
            sleep(1)
        self.stdout.write(self.style.SUCCESS('Team import successfully'))
        