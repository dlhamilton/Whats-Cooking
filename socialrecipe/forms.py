from .models import Comments
from django import forms


class CommentsForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('body',)


class SearchRecipeForm(forms.Form):
    search_query = forms.CharField(max_length=100, required=False, widget= forms.TextInput(attrs={'id':'search_query'}))