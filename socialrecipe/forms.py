from .models import Comments, Ingredients, Recipes
from django import forms


class CommentsForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('body',)


class RecipesForm(forms.ModelForm):
    publish = forms.BooleanField(initial=False, required=False, 
                    widget=forms.CheckboxInput(attrs={'label': 'Publish'}))
    
    class Meta:
        model = Recipes
        fields = ('title',
                  'recipe_image',
                  'excerpt',
                  'prep_time',
                  'cook_time',
                  'serves',)


class SearchRecipeForm(forms.Form):
    search_query = forms.CharField(max_length=100, required=False,
    widget = forms.TextInput(attrs={'id':'search_query',
    'placeholder': 'Search...' , 'class': 'form-control'}))


class FilterRecipeForm(forms.Form):
    filter_query = forms.ModelMultipleChoiceField(
        queryset=Ingredients.objects.filter(approved=True).order_by('name'),
        widget=forms.CheckboxSelectMultiple

    )