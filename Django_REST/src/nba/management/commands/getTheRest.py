from django.core.management.base import BaseCommand
from nba.models import Conference, Position, Division

conferences = ['East','West']

positions = ['Center', 'Forward', 'Guard', 'Small Forward', 'Wing', 'Power Forward', 'Point Guard', 'Shooting Guard',
             'Guard-Forward', 'Center-Forward', 'Forward-Guard', 'Forward-Center', 'NA']

divisions = ['Atlantic','Central','Southeast','Northwest','Pacific','Southwest']

class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        d = 'Write a description'
        
        # conference
        conference_list = [Conference(full_name = c,description = d) for c in conferences]
        Conference.objects.bulk_create(conference_list)
        print('creation done')
        for con in Conference.objects.all():
            con.save()
        self.stdout.write(self.style.SUCCESS('Bulk Conference Import Successful'))
        
        # position
        position_list = [Position(full_name = p,description = d) for p in positions]
        Position.objects.bulk_create(position_list)
        print('creation done')
        for pos in Position.objects.all():
            pos.save()
        self.stdout.write(self.style.SUCCESS('Bulk Position Import Successful'))
        
        # division
        division_list = [Division(full_name = c,description = d) for c in divisions]
        Division.objects.bulk_create(division_list)
        print('creation done')
        for div in Division.objects.all():
            div.save()
        self.stdout.write(self.style.SUCCESS('Bulk Division Import Successful'))