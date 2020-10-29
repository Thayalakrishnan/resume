from django import forms
from .models import Picture
from tempus_dominus.widgets import DatePicker

class PictureForm(forms.ModelForm):
    date = forms.DateField(widget=DatePicker)
    
    class Meta:
        model = Picture
        fields =(
            'title',
            'picture',
            'date',
            'caption',
            'description',
            'album',
            'starred',
            'tags',
            'equipment_used',
            'editing',
            )
