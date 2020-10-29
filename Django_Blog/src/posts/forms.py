from django import forms
from tinymce import TinyMCE
from .models import Post,Category,MembershipThrough, get_categories_list
from django.forms.models import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Div, HTML, ButtonHolder, Submit
from crispy_forms.bootstrap import InlineRadios
from .custom_layout_object import *

class TinyMCEWidget(TinyMCE):
    def use_required_attribute(self, *args):
        return False



class CategoryForm(forms.ModelForm):
    
    class Meta:
        model = Category
        fields = ['title',]


CategoryFormSet = inlineformset_factory(Category,Post.categories.through,form=CategoryForm,fields = ['category'], extra=2, can_delete=True)


class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=TinyMCEWidget(
            attrs={
                'required': False,
                'cols': 30,
                'rows': 10
                }
        )
    )
    
    categories_list = get_categories_list()
    class Meta:
            model = Post
            fields =['title', 'overview', 'content', 'thumbnail', 'categories', 'featured', 'previous_post', 'next_post']
    
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Field('title'),
                Field('overview'),
                Field('content'),
                Field('thumbnail'),
                InlineRadios('categories_list'),
                Fieldset('Add categories',
                    Formset('categories')),
                Field('featured'),
                Field('previous_post'),
                Field('next_post'),
                HTML("<br>"),
                ButtonHolder(Submit('submit', 'save')),
                )
            )