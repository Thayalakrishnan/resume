from rest_framework import serializers
from rest_framework.serializers import ListSerializer
from nba_api.stats.static import teams
from nba_api.stats.endpoints import commonplayerinfo
from nba_api.stats.static import players
from .models import Team, Player, Position, Entity, Conference, Division
from datetime import date

nba_players = players.get_active_players()
nba_teams = teams.get_teams()

#########################################################################
# Serializer helper functions
#########################################################################

def good_value(value):
    return False if value in ['', ' ', 'Undrafted'] else True

def team_query(id):
    return Team.objects.get(team_id=id)

def convert_height(imperial):
    if good_value(imperial):
        feet, inches = imperial.split('-')
        return int(int(feet)*30.48 + int(inches)*2.54)
    return 0

def convert_weight(imperial):
    if good_value(imperial):
        return int(int(imperial)*0.453592)
    return 0

def convert_birthday(birthdatetime):
    birthdate, birthtime = birthdatetime.split('T')
    byear, bmonth, bday = map(int, birthdate.split('-'))
    return date(byear, bmonth, bday)

def year_filter(year):
    if good_value(year):
        return year
    return 0

def isactive(stat):
    return True if stat=='Active' else False

def convert_position(pos):
    positions = list(pos.split('-'))
    for pos in positions:
        obj, created = Position.objects.get_or_create(full_name=pos)
    return positions

def convert_draft_number(num):
    return 0 if num=='Undrafted' else num

def get_player_info(id):
    player_info = commonplayerinfo.CommonPlayerInfo(player_id=id)
    player_dict = player_info.common_player_info.get_dict()
    headers,data = player_dict["headers"], player_dict["data"][0]
    return dict(zip(headers,data))

#########################################################################
# Entity Serializer
#########################################################################
class EntityListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        result = [self.child.create(attrs) for attrs in validated_data]
        try:
             self.child.Meta.model.objects.bulk_create(result)
        except IntegrityError as e:
            raise ValidationError(e)
        return result
     
    def to_internal_value(self, data):
        for d in data:
            d['pkid'] = d.pop('id')
            d['full_name'] = d.pop('full_name')
            d['entity_type'] = d.pop('type')
        return super().to_internal_value(data)


class EntitySerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):
        instance = Entity(**validated_data)
        if isinstance(self._kwargs["data"], dict):
            instance.save()
        return instance

    def update(self, instance, validated_data):
        instance.pkid = validated_data.get('pkid', instance.pkid)
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.entity_type = validated_data.get('entity_type', instance.entity_type)
        if isinstance(self._kwargs["data"], dict):
            instance.save()
        return instance

    class Meta:
        model = Entity
        fields = ['pkid','full_name','entity_type']
        list_serializer_class = EntityListSerializer

#########################################################################
# Player Serializer
#########################################################################

class PlayerListSerializer(serializers.ListSerializer):
    
    def create(self, validated_data):
        result = [self.child.create(attrs) for attrs in validated_data]
        try:
             self.child.Meta.model.objects.bulk_create(result)
        except IntegrityError as e:
            raise ValidationError(e)

        return result


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        exclude = ['position']
        list_serializer_class = PlayerListSerializer

    
    def create(self, validated_data):
        instance = Player(**validated_data)
        if isinstance(self._kwargs["data"], dict):
            instance.save()
        return instance

    def update(self, instance, validated_data):
        instance.player_id = validated_data.get('player_id', instance.player_id)
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.birthdate = validated_data.get('birthdate', instance.birthdate)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.team_id = validated_data.get('team_id', instance.team_id)
        instance.jersey = validated_data.get('jersey', instance.jersey)
        instance.from_year = validated_data.get('from_year', instance.from_year)
        instance.to_year = validated_data.get('to_year', instance.to_year)
        instance.season_exp = validated_data.get('season_exp', instance.season_exp)
        instance.draft_year = validated_data.get('draft_year', instance.draft_year)
        instance.draft_round = validated_data.get('draft_round', instance.draft_round)
        instance.draft_number = validated_data.get('draft_number', instance.draft_number)
        instance.height = validated_data.get('height', instance.height)
        instance.weight = validated_data.get('weight', instance.weight)
        instance.position = validated_data.get('position', instance.position)
        
        instance.save()
        return instance
    
    def to_internal_value(self, data):
        data['birthdate'] = convert_birthday(data['birthdate'])
        data['height'] = convert_height(data['height'])
        data['weight'] = convert_weight(data['weight'])
        data['draft_year'] = convert_draft_number(data['draft_year'])
        data['draft_round'] = convert_draft_number(data['draft_round'])
        data['draft_number'] = convert_draft_number(data['draft_number'])
        data['is_active'] = isactive(data['is_active'])
        data['team_id'] = int(data['team_id'])
        #data['position'] = data['position'].split('-')
        return super().to_internal_value(data)


#########################################################################
# Team Serializer
#########################################################################

def convert_arenacapacity(cap):
    if cap==None:
        return str(0)
    else:
        return str(cap)

def convert_headcoach(coach):
    if coach==None or coach== ' ':
        return str('yeet')
    else:
        return str(coach)

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'

    def create(self, validated_data):
        instance = Team(**validated_data)
        if isinstance(self._kwargs["data"], dict):
            instance.save()
        return instance
    
    def to_internal_value(self, data):
        #print(data)
        data['headcoach'] = convert_headcoach(data['headcoach'])
        data['arenacapacity'] = convert_arenacapacity(data['arenacapacity'])
        data['team_division'] = Division.objects.get(full_name=data['team_division'])
        data['team_conference'] = Conference.objects.get(full_name=data['team_conference'])
        return super().to_internal_value(data)