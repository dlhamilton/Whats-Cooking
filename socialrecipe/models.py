"""
Socialrecipe Models
"""
from decimal import Decimal
from django.db import models
from django.dispatch import receiver
from django.db.models import Avg
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from cloudinary.models import CloudinaryField
from allauth.account.signals import user_signed_up

RECIPE_STATUS = ((0, "Draft"), (1, "Published"), (2, "Hidden"), (3, "Removed"))
USER_STATUS = ((0, "Suspended"), (1, "Standard"), (2, "Bronze"), (3, "Silver"),
               (4, "Gold"), (5, "Platnium"))
INGREDIENTS = ((0, "Approved"), (1, "Disapproved"))


class UserDetails(models.Model):
    '''
    Extend the user model
    '''
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_details")
    location = models.CharField(
        max_length=150, blank=True)
    status = models.IntegerField(
        choices=USER_STATUS, default=1)
    user_image = CloudinaryField(
        'image', default='placeholder.webp')
    follows = models.ManyToManyField(
        User, related_name='user_follows', blank=True)

    def __str__(self):
        return str(self.user.username)

    def number_of_follows(self):
        '''
        gets the number of followers
        '''
        return self.follows.count()

    def get_followers(self):
        '''
        get a list of all followers
        '''
        follow_list = self.follows.all()
        return follow_list

    def get_amount_of_recipes(self):
        '''
        gets the number of recipes made
        '''
        total = self.user.user_recipes.count()
        return total % 10

    def get_amount_to_next(self):
        '''
        gets the amount of recipes until next status
        '''
        total = self.user.user_recipes.count()
        return 10 - total % 10

    def update_status(self):
        '''
        changes the users status to the next level
        '''
        status_ranges = [(40, 5), (30, 4), (20, 3), (10, 2), (0, 1)]
        num = self.user.user_recipes.filter(status=1).count()
        for threshold, value in status_ranges:
            if num >= threshold:
                self.status = value
                break


class Recipes(models.Model):
    '''
    stores the recipes
    '''
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_recipes")
    recipe_image = CloudinaryField(
        'image', default='placeholder-recipe')
    excerpt = models.TextField()
    status = models.IntegerField(choices=RECIPE_STATUS, default=0)
    favourites = models.ManyToManyField(
        User, related_name='user_favourites', blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    prep_time = models.PositiveIntegerField(default=0)
    cook_time = models.PositiveIntegerField(default=0)
    serves = models.PositiveIntegerField(default=1)

    class Meta:
        '''
        The meta data
        '''
        ordering = ['-upload_date']

    def __str__(self):
        return str(self.title)

    def number_of_favourites(self):
        '''
        gets the number of favourites
        '''
        return self.favourites.count()

    def total_time(self):
        '''
        the total amount of time the recipe takes
        '''
        return self.prep_time + self.cook_time


class RecipeImages(models.Model):
    '''
    store the images of the recipe
    '''
    recipe = models.ForeignKey(
        Recipes, on_delete=models.CASCADE, related_name="recipe_images")
    recipe_image = CloudinaryField('image')
    headline = models.TextField(blank=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipe_images")
    upload_date = models.DateTimeField(auto_now_add=True)


class Comments(models.Model):
    '''
    stores the comments made of the recipe
    '''
    recipe = models.ForeignKey(
        Recipes, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments")
    body = models.TextField()
    post_date = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=RECIPE_STATUS, default=1)

    class Meta:
        '''
        The meta data
        '''
        ordering = ['-post_date']

    def __str__(self):
        return f"Comment {self.body} by {self.user.username}"


class Methods(models.Model):
    '''
    The steps to create the recipe
    '''
    recipe = models.ForeignKey(
        Recipes, on_delete=models.CASCADE, related_name="methods")
    order = models.IntegerField()
    method = models.TextField()

    class Meta:
        '''
        The meta data
        '''
        ordering = ['order', 'recipe']

    def number_of_methods(self, recipe_id):
        '''
        numebr of methods linked to the recipe
        '''
        return Methods.objects.filter(recipe_id=recipe_id).count()


class StarRating(models.Model):
    '''
    the star rating of the recipe
    '''
    recipe = models.ForeignKey(
        Recipes, on_delete=models.CASCADE, related_name="star_rating")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="star_rating")
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    date_given = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_average(cls, recipe_id):
        '''
        get the average rating for the recipe by recipe_id
        '''
        return cls.objects.filter(
            recipe_id=recipe_id).aggregate(
                average=Avg('rating')).get('average')


class Ingredients(models.Model):
    '''
    All the ingridents on the app
    '''
    name = models.CharField(max_length=150)
    approved = models.BooleanField(default=False)
    ingredients_image = CloudinaryField('image', default='placeholder')

    class Meta:
        '''
        The meta data
        '''
        ordering = ['name']

    def __str__(self):
        return str(self.name)


class Units(models.Model):
    '''
    units of measure
    '''
    name = models.CharField(max_length=150)

    def __str__(self):
        return str(self.name)


class RecipeItems(models.Model):
    '''
    All the items that are in the recipe
    '''
    recipe = models.ForeignKey(
        Recipes, on_delete=models.CASCADE, related_name="recipe_items")
    ingredients = models.ForeignKey(
        Ingredients, on_delete=models.CASCADE, related_name="recipe_items")
    amount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))])
    unit = models.ForeignKey(
        Units, on_delete=models.CASCADE, related_name="recipe_items")

    def __str__(self):
        return str(self.ingredients.name)


@receiver(user_signed_up)
def after_user_signed_up(sender, request, user, **kwargs):
    '''
    create a userdetails profile after user signs up
    '''
    UserDetails.objects.create(user=user)
