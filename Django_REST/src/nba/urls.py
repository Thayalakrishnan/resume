from django.urls import path, include
from .views import PlayerDetailView, PlayerListView, NBAHomePageView, TeamListView, TeamDetailView, TeamTableView, TeamScheduleView, PlayerViewSet, index

app_name = 'nba'

urlpatterns = [
    path('', NBAHomePageView.as_view(), name='homepage'),
    path('player-list/', PlayerListView.as_view(), name='player-list'),
    path('player-detail/<pk>', PlayerDetailView.as_view(), name='player-detail'),
    path('team-list/', TeamListView.as_view(), name='team-list'),
    path('team-table/', TeamTableView.as_view(), name='team-table'),
    path('team-detail/<pk>', TeamDetailView.as_view(), name='team-detail'),
    path('team-schedule/<pk>', TeamScheduleView.as_view(), name='team-schedule'),
    path('team-schedule/<pk>', TeamScheduleView.as_view(), name='team-schedule'),
]
