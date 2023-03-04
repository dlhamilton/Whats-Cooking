# What's Cooking Testing

[<< Back to ReadMe](README.md)

## Automated Tests

I have 197 tests with 100% coverage of my code.
![Coverage Report](readme-media/coverage.png)

***

## Manual Tests
Manual testing occurred regularly throughout local development. Tests are documented below.

### index
|Test #|Test|Results|Evidence|
| --- | --- | --- |--- |
|1|Logo heading shortens when screen size is smaller|Pass||
|2|Login/ Sign up button disappears when user is logged in|Pass||
|3| profile section appears on user presses profile and is showing the correct user|Pass||
|4| links go to the correct pages|Pass||
|5| clicking on the recipes go to the correct recipes|Pass||
|6| complete your account notification appears on the user has not complete the account details|Pass||
|7| complete account details on profile section disappears when user has completed account|Pass||
|8| Account status shows the correct position on the progress bar|Pass||
|9| Account status shows the correct colour of award|Pass||
|10| contact link navigates to the contact form on the about page|Pass||
### about_us
|Test #|Test|Results|Evidence|
| --- | --- | --- |--- |
|1| contact form has the correct validation|Pass||
|2| contact form send email to the admin|Pass||
### logged_in_user_card
|Test #|Test|Results|Evidence|
| --- | --- | --- |--- |
|1| shows the right information for the user page that you were looking at|Pass||
|2| shows the correct colour status for the user|Pass||
|3| follow button appears if you are logged in and not following a user|Pass||
|4| button goes to a mini version showing a icon instead of Word when the screen is on a smaller view|Pass||
### recipe_detail
|Test #|Test|Results|Evidence|
| --- | --- | --- |--- |
|1| if user is logged in it shows the edit button on their recipes|Pass||
|2| if user is logged in but not on the recipe the edit button does not appear|Pass||
|3| only if the user is logged in can they make a rating|Pass||
|4| the print button shows the print dialogue so the user can print the recipe|Pass||
|5| only if user is logged in can they favourite a recipe|Pass||
|6| only if a user is logged in can they upload a image|Pass||
|7| a user that has uploaded a image can delete their own image|Pass||
|8| images show on the recipe|Pass||
|9| user can turn on and off comments|Pass||
|10| only a log in user can leave a comment|Pass||
|11| if the user has written a comment they can only delete their own comment|Pass||
|12| header image disappears when the user is on a smaller screen|Pass||
|13| splide images change how many are on screen depending on the view size|Pass||
### recipes
|Test #|Test|Results|Evidence|
| --- | --- | --- |--- |
|1| links go to the correct pages|Pass||
|2| recipes link to the correct recipes|Pass||
|3| the page pagination works|Pass||
|4| sort and filter show results in the correct order|Pass||
|5| search shows the correct recipes|Pass||
### user_favourites
|Test #|Test|Results|Evidence|
| --- | --- | --- |--- |
|1| recipes link to the correct recipe pages|Pass||
|2| Page pagination works correctly|Pass||
### user_followers
|Test #|Test|Results|Evidence|
| --- | --- | --- |--- |
|1| correct users are shown in the following pages|Pass||
|2| correct user rating is shown on the page|Pass||
### user_profile_page
|Test #|Test|Results|Evidence|
| --- | --- | --- |--- |
|1| user can edit account if they are on their own account|Pass||
|2| edit account shows a following or follow button if you are logged in|Pass||
|3| supplied changes side depending on how big the view is|Pass||
|4| all links go to the correct pages|Pass||
### user_recipe_add
|Test #|Test|Results|Evidence|
| --- | --- | --- |--- |
|1| the form has the correct validation|Pass||
|2| sign postage is shown at the top of the form|Pass||
### user_recipes_edit
|Test #|Test|Results|Evidence|
| --- | --- | --- |--- |
|1| knows if the recipe is published or not|Pass||
|2| shows what ingredients are verified|Pass||
|3| shows the methods in the recipe clearly|Pass||
|4| is the ingredients in the recipe clearly|Pass||
|5| ingredient pagination works correctly|Pass||
|6| add an ingredient button only appears when less than 10 items show up in the search|Pass||
### user_recipes
|Test #|Test|Results|Evidence|
| --- | --- | --- |--- |
|1| recipes link to the correct recipe pages|Pass||
|2| Page pagination works correctly|Pass||
|3| shows a colour around the recipe if it has been published or not only if you are logged in to your recipes|Pass||

***

## User Story Testing

***

## Code Validation

### HTML
#### index
#### about_us
https://validator.w3.org/nu/?showsource=yes&showoutline=yes&showimagereport=yes&doc=https%3A%2F%2Fwhats-cooking.herokuapp.com%2Faboutus%2F
#### recipe_detail
#### recipes
#### user_favourites
#### user_followers
#### user_profile_page
#### user_recipe_add
#### user_recipes_edit
#### user_recipes

### CSS
https://jigsaw.w3.org/css-validator/validator?uri=https%3A%2F%2Fwhats-cooking.herokuapp.com%2F&profile=css3svg&usermedium=all&warning=1&vextwarning=&lang=en

### JavaScript
#### recipe_detail.js
No errors were found when passing through the official Jshint validator
- There are 23 functions in this file.
- Function with the largest signature take 1 arguments, while the median is 1.
- Largest function has 9 statements in it, while the median is 2.
- The most complex function has a cyclomatic complexity value of 4 while the median is 1.
#### recipes.js
No errors were found when passing through the official Jshint validator
- There are 3 functions in this file.
- Function with the largest signature take 1 arguments, while the median is 0.
- Largest function has 9 statements in it, while the median is 7.
- The most complex function has a cyclomatic complexity value of 2 while the median is 1.
#### sendEmail.js
No errors were found when passing through the official Jshint validator
- There are 7 functions in this file.
- Function with the largest signature take 1 arguments, while the median is 1.
- Largest function has 3 statements in it, while the median is 1.
- The most complex function has a cyclomatic complexity value of 1 while the median is 1.
#### user_profile_page.js
No errors were found when passing through the official Jshint validator
- There are 2 functions in this file.
- Function with the largest signature take 0 arguments, while the median is 0.
- Largest function has 1 statements in it, while the median is 1.
- The most complex function has a cyclomatic complexity value of 1 while the median is 1.
#### user_recipes_edit.js
No errors were found when passing through the official Jshint validator
- There are 12 functions in this file.
- Function with the largest signature take 2 arguments, while the median is 1.
- Largest function has 11 statements in it, while the median is 3.
- The most complex function has a cyclomatic complexity value of 3 while the median is 1.

### Python

***

## Lighthouse/ Accessibility Testing
### index
### about_us
### logged_in_user_card
### recipe_detail
### recipes
### user_favourites
### user_followers
### user_profile_page
### user_recipe_add
### user_recipes_edit
### user_recipes

***

## Devices used for manual testing
What's Cooking was tested using the following desktop and mobile browsers:

### Desktop
- Safari 15.6.1
- Firefox 109.0
- Chrome 109.0.5414.119
### Mobile and Tablet
- Safari iOS 16.3
- Chrome 112 for Android

[<< Back to ReadMe](README.md)