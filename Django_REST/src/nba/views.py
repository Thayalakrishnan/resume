from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Team, Player
from .serializers import TeamSerializer, PlayerSerializer
# thirdparty imports
from django.http import JsonResponse
# thirdparty imports
from rest_framework import generics, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.renderers import TemplateHTMLRenderer
from nba_api.stats.endpoints import teamgamelog
from nba_api.stats.static import teams

import django_tables2 as tables
from django_tables2 import SingleTableView


#####################################################################################
# Player Detail View
#####################################################################################
class PlayerDetailView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'player_detail.html'
    
    def get(self, request, pk):
        player = get_object_or_404(Player, pk=pk)
        data ={
            'player':player,
        }
        return Response(data)


#####################################################################################
# Player List View
#####################################################################################
class PlayerListView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'player_list.html'
    
    def get(self, request):
        queryset = Player.objects.all()
        teams = Team.objects.all()
        data ={
            'queryset':queryset,
            'teams':teams,
        }
        return Response(data)


#####################################################################################
# Team Detail View
#####################################################################################
class TeamDetailView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'team_detail.html'
    
    def get(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        data ={
            'team':team,
        }
        return Response(data)

#####################################################################################
# Team table view
#####################################################################################
class TeamListTable(tables.Table):
    attrs = {
        'th':{'float': 'center', 'nowrap': 'nowrap'},
        'td':{'float': 'center', 'nowrap': 'nowrap', 'border-spacing': '0.1rem','border-collapse': 'collapse'}
        }
    
    abbreviation = tables.Column(verbose_name='Abbr.', attrs=attrs)
    full_name = tables.Column(verbose_name='Name', attrs=attrs)
    team_id = tables.Column(verbose_name='Team ID', attrs=attrs)
    year_founded = tables.Column(verbose_name='Founded', attrs=attrs)
    owner = tables.Column(verbose_name='Owner', attrs=attrs)
    generalmanager = tables.Column(verbose_name='General Manager', attrs=attrs)
    headcoach = tables.Column(verbose_name='Coach', attrs=attrs)
    city = tables.Column(verbose_name='City', attrs=attrs)
    state = tables.Column(verbose_name='State', attrs=attrs)
    arena = tables.Column(verbose_name='Arena', attrs=attrs)
    arenacapacity = tables.Column(verbose_name='Arena Capacity', attrs=attrs)
    team_conference = tables.Column(verbose_name='Conference', attrs=attrs)
    team_division = tables.Column(verbose_name='Division', attrs=attrs)
    class Meta:
        model = Team
        fields = ['abbreviation', 'full_name', 'team_id', 'year_founded',
                  'owner','generalmanager','headcoach','city','state','arena',
                  'arenacapacity','team_conference','team_division']
        template_name = "django_tables2/bootstrap-responsive.html"

SingleTableView.table_pagination = False

class TeamTableView(SingleTableView):
    SingleTableView.table_pagination = False
    table_class = TeamListTable
    queryset = Team.objects.all()
    template_name = "team_table.html"

#####################################################################################
# Team list view
#####################################################################################
class TeamListView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'team_list.html'
    
    def get(self, request):
        queryset = Team.objects.all()
        data ={
            'queryset':queryset,
        }
        return Response(data)


#####################################################################################
# NBA Home Page View
#####################################################################################
class NBAHomePageView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'nba_index.html'
    
    def get(self, request):
        players = Player.objects.all()
        teams = Team.objects.all()
        data ={
            'players':players,
            'teams':teams,
        }
        return Response(data)

#####################################################################################
# Team Schedule View
#####################################################################################

def teams_from_team_schedule(games_list, teams_q):
    team, courtadvantage, opponent = [[game['MATCHUP'].split()[i] for game in games_list] for i in range(3)]
    opponents = [teams_q.get(abbreviation=current_opp) for current_opp in opponent]
    courtadvantages = ['Home' if current != '@' else 'Away' for current in courtadvantage]
    addTodict = [game.update for game in games_list]
    new_games_list = [addict({'OPPONENT':opp, 'COURTADVANTAGE':court,}) for opp, court,addict  in zip(opponents,courtadvantages,addTodict)]
    return games_list


def get_team_schedules(team_id):
    gamelog = teamgamelog.TeamGameLog(team_id=team_id).team_game_log.get_dict()
    headers,data = gamelog["headers"], gamelog["data"]
    return [dict(zip(headers, _)) for _ in data]


class TeamScheduleView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'team_schedule.html'
    
    def get(self, request, pk):
        teams_q = Team.objects.all()
        team = teams_q.get(team_id=pk)
        gamelog = get_team_schedules(team.team_id)
        gamelog = teams_from_team_schedule(gamelog, teams_q)
        
        data ={
            'teams_q':teams_q,
            'gamelog':gamelog,
        }
        return Response(data)


#####################################################################################
# player list data tables
#####################################################################################
def index(request):
    return render(request, 'players.html')

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
