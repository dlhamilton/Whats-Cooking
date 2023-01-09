from .models import Comments, Ingredients
from django import forms


class CommentsForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('body',)


class SearchRecipeForm(forms.Form):
    search_query = forms.CharField(max_length=100, required=False, widget= forms.TextInput(attrs={'id':'search_query'}))


class FilterRecipeForm(forms.Form):
    filter_query = forms.ModelMultipleChoiceField(
        queryset=Ingredients.objects.filter(approved=True).order_by('name'),
        widget=forms.CheckboxSelectMultiple(
            attrs={'data-filter': 'false'}
            )

    )