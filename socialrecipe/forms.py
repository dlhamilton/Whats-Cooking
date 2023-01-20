from django import forms
from cloudinary.forms import CloudinaryInput
from cloudinary.models import CloudinaryField
from .models import Comments, Ingredients, Recipes, RecipeItems, Units


class CommentsForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('body',)


class RecipesForm(forms.ModelForm):
    publish = forms.BooleanField(initial=False, required=False, widget=forms.CheckboxInput(attrs={'label': 'Publish'}))
    
    recipe_image = CloudinaryField('image')
    
    class Meta:
        model = Recipes
        fields = ('title',
                  'recipe_image',
                  'excerpt',
                  'prep_time',
                  'cook_time',
                  'serves',)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.status == 1:
            self.fields['publish'].initial = True


class SearchRecipeForm(forms.Form):
    search_query = forms.CharField(max_length=100, required=False,
    widget = forms.TextInput(attrs={'id':'search_query',
    'placeholder': 'Search...' , 'class': 'form-control'}))


class FilterRecipeForm(forms.Form):
    filter_query = forms.ModelMultipleChoiceField(
        queryset=Ingredients.objects.filter(approved=True).order_by('name'),
        widget=forms.CheckboxSelectMultiple

    )


class AddToRecipeForm(forms.Form):
    search_term = forms.CharField(required=False)
    # filter_query = forms.ModelMultipleChoiceField(
    #     queryset=Ingredients.objects.filter(approved=True).order_by('name'),
    #     widget=forms.CheckboxSelectMultiple
    # )


class RecipeItemsForm(forms.ModelForm):
    class Meta:
        model = RecipeItems
        fields = ['ingredients', 'amount', 'unit']
        widgets = {
        'ingredients': forms.TextInput(attrs={'id': 'recipient-name'}),
        }

    unit = forms.ModelChoiceField(queryset=Units.objects.all())
   
    def __init__(self, *args, **kwargs):
        super(RecipeItemsForm, self).__init__(*args, **kwargs)
        self.fields['unit'].empty_label = "Select Unit"
        self.fields['ingredients'].widget.attrs.update({'id': 'ingredient-name'})