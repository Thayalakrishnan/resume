from django.db import models
from django.shortcuts import reverse
from nba_api.stats.static import players
import os
from datetime import date, datetime
from colorfield.fields import ColorField


##############################################################################################
# Position
##############################################################################################
class Position(models.Model):
    full_name = models.CharField(max_length=50, primary_key=True)
    description = models.TextField(default='')
    
    class Meta:
        ordering = ['full_name']
    
    def __str__(self):
        return self.full_name
    
    def get_absolute_url(self):
        return reverse('position-detail', args=[str(self.full_name)])


##############################################################################################
# Conference
##############################################################################################

class Conference(models.Model):
    full_name = models.CharField(max_length=50, primary_key=True)
    description = models.TextField(default='')
    
    class Meta:
        ordering = ['full_name']
    
    def __str__(self):
        return self.full_name
    
    def get_absolute_url(self):
        return reverse('conference-detail', args=[str(self.full_name)])


##############################################################################################
# Division
##############################################################################################
class Division(models.Model):
    full_name = models.CharField(max_length=50, primary_key=True)
    description = models.TextField(default='')
    
    class Meta:
        ordering = ['full_name']
    
    def __str__(self):
        return self.full_name
    
    def get_absolute_url(self):
        return reverse('division-detail', args=[str(self.full_name)])

##############################################################################################
# Entity
##############################################################################################
class Entity(models.Model):
    pkid = models.PositiveIntegerField(primary_key=True)
    full_name = models.CharField(max_length=50)
    
    class Meta:
        abstract = True
        ordering = ['full_name']
    
    def __str__(self):
        return self.full_name
    
    def get_absolute_url(self):
        return reverse('detail', args=[str(self.pkid)])


##############################################################################################
# Team
##############################################################################################
class Team(models.Model):
    team_id = models.PositiveIntegerField(primary_key=True)
    full_name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=5)
    nickname = models.CharField(max_length=15)
    year_founded = models.IntegerField()
    owner = models.CharField(max_length=50, default='yeet')
    generalmanager = models.CharField(max_length=30, default='yeet')
    headcoach = models.CharField(max_length=30, default='yeet')
    city = models.CharField(max_length=15)
    state = models.CharField(max_length=25)
    arena = models.CharField(max_length=50)
    arenacapacity = models.PositiveSmallIntegerField(default=0)
    team_conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='teams', related_query_name='team')
    team_division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='teams', related_query_name='team')
    primary_color = ColorField(default='#000000')
    secondary_color = ColorField(default='#000000')
    tertiary_color = ColorField(default='#000000')

    class Meta:
        ordering = ['full_name']
        verbose_name = 'team'
        verbose_name_plural = 'teams'
    
    def __str__(self):
        return self.full_name
    
    def get_absolute_url(self):
        return reverse('nba:team-detail', kwargs={'pk':self.team_id})

    def get_players(self):
        return Player.objects.filter(team_id=self.team_id)

##############################################################################################
# Player
##############################################################################################
class Player(models.Model):
    player_id = models.PositiveIntegerField(primary_key=True)
    full_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    birthdate = models.DateField(default=date.today)
    is_active = models.BooleanField(default=False)
    team_id = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players', related_query_name='player')
    jersey = models.PositiveSmallIntegerField(default=0)
    from_year = models.PositiveSmallIntegerField(default=0)
    to_year = models.PositiveSmallIntegerField(default=0)
    season_exp = models.PositiveSmallIntegerField(default=0)
    draft_year = models.PositiveSmallIntegerField(default=0)
    draft_round = models.PositiveSmallIntegerField(default=0)
    draft_number = models.PositiveSmallIntegerField(default=0)
    height = models.PositiveSmallIntegerField(default=0)
    weight = models.PositiveSmallIntegerField(default=0)
    position = models.ManyToManyField(Position)
    
    
    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'player'
        verbose_name_plural = 'players'

    def __str__(self):
        return self.full_name
    
    def get_absolute_url(self):
        return reverse('nba:player-detail', kwargs={'pk':self.player_id})
    
    def get_team_mates(self):
        return Player.objects.filter(team_id=self.team_id)


##############################################################################################
# Coach
##############################################################################################
class Coach(models.Model):
    pkid = models.PositiveIntegerField(primary_key=True)
    full_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    rosterstatus = models.BooleanField(default=False)
    current_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='coaches', related_query_name='coach')
    start_year = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'coach'
        verbose_name_plural = 'coaches'
    
    def __str__(self):
        return self.full_name
    
    def get_absolute_url(self):
        return reverse('coach-detail', args=[str(self.pkid)])


##############################################################################################
# Staff
##############################################################################################
class Staff(models.Model):
    pkid = models.PositiveIntegerField(primary_key=True)
    full_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    current_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='staff', related_query_name='staff_member')
    rosterstatus = models.BooleanField(default=False)

    
    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'staff'
        verbose_name_plural = 'staff members'
        
    def __str__(self):
        return self.full_name
    
    def get_absolute_url(self):
        return reverse('staff-detail', args=[str(self.pkid)])

##############################################################################################
# Game
##############################################################################################
#
#class Game(models.Model):
#    game_id = models.PositiveIntegerField(primary_key=True)
#    home_team_id = models.ForeignKey(Team, on_delete=models.CASCADE)
#    away_team_id = models.ForeignKey(Team, on_delete=models.CASCADE)
#    game_date = models.DateField(default=date.today)
#    
#    winning_team = models.ForeignKey(Team, on_delete=models.CASCADE)
#    game_played = models.BooleanField(default=False)
#    
#    overtime = models.BooleanField(default=False)
#    
#    class Meta:
#        verbose_name = 'game'
#        verbose_name_plural = 'games'
#
#    def __str__(self):
#        return self.game_id
#    
#    def get_absolute_url(self):
#        return reverse('nba:games', kwargs={'pk':self.game_id})
#    
#    def get_game_description(self):
#        desc = f'Game between {self.away_team_id.full_name} @ {self.home_team_id.full_name}'
#        return desc