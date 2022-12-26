# What's Cooking!

Click the link to view the live app [What's Cooking](https://whats-cooking.herokuapp.com/)

Making recipes by putting ingredients first and sharing recipes between the Whats Cooking community.

***

## Contents
* [About What's Cooking](#Introduction)
* [How To Use It](#how-to-use-it)
* [User Story](#User-Stories)
* [Design](#Design)
* [ERD](#ERD)
* [Wireframes](#Wireframes)
* [Navigation Plan](#Navigation-Plan)
* [Colour Scheme](#Colour-Scheme)
* [Fonts](#Fonts)
* [Features](#features)
    * [Existing Features](#Existing-Features)
    * [Future Features](#future-features)
* [Testing](#testing)
    * [Manual Testing](#manual-testing)
    * [User Story Testing](#user-story-testing)
    * [Validator](#validatiors)
* [Solved Bugs](#solved-bugs)
* [Deployment](#Deployment-Incomplete!!!)
    * [Cloning & Forking](#cloning--forking)
    * [Local Deployment](#local-deployment)
    * [Remote Deployment](#remote-deployment)
    * [Google Sheets](#google-sheet)
* [Credits / Acknowledgements](#credits--acknowledgement)

***

## Introduction

## How to use it

## User Stories

***

## Design
### ERD
![ERD](readme-media/ERD.png)

### Wireframes
#### Index
Mobile
![Index M Screen](readme-media/IndexMobile.png)
Desktop
![Index D Screen](readme-media/IndexDesktop.png)

#### Shopping List
Mobile
![Shopping M Screen](readme-media/ShoppingList.png)
Desktop
![Shopping D Screen](readme-media/ShoppingListDesktop.png)

#### Logged In Recipe List
Mobile
![Recipe List M Screen](readme-media/LoggedInHomePageMobile.png)
Desktop
![Recipe List D Screen](readme-media/LoggedInHomePageDesktop.png)

#### Login
Mobile
![Login M Screen](readme-media/LoginMobile.png)
Desktop
![Login D Screen](readme-media/LoginDesktop.png)

#### New Recipe
Mobile
![New Recipe M Screen](readme-media/NewRecipe.png)
Desktop
![New Recipe D Screen](readme-media/NewRecipeDesktop.png)

#### Search Ingridents
![Program Screen](readme-media/SearchIngridents.png)

#### Add New Instruction
![Program Screen](readme-media/AddNewInstruction.png)

### Navigation Plan
![Navigation Plan](readme-media/NavigationPlan.png)

### Colour Scheme
![colours](readme-media/TestColours.png)

### Fonts

***

## Features
### Existing Features
### Future Features

***

## Testing 
### Manual Testing
### User Story Testing
### Validators
### Solved Bugs

***

## Deployment Incomplete!!!
### Cloning & Forking
#### Fork
1. On GitHub.com, navigate to the [dlhamilton/Route Me](https://github.com/dlhamilton/route-me) repository.
2. In the top-right corner of the page, click Fork.
3. By default, forks are named the same as their parent repositories. You can change the name of the fork to distinguish it further.
4. Add a description to your fork.
5. Click Create fork.

#### Clone
1. Above the list of files click the button that says 'Code'.
2. Copy the URL for the repository.
3. Open Terminal. Change the directory to the location where you want the cloned directory.
4. Type git clone, and then paste the URL
5. Press Enter.

### Local Deployment
1. Sign up to [Gitpod](https://gitpod.io/)
2. Download the Gitpod browser extension.
3. On GitHub.com, navigate to the [dlhamilton/route_me](https://github.com/dlhamilton/route-me) repository.
4. Above the list of files click the button that says 'Gitpod'.
5. Once open you will need to install the libraries, you can do this by typing "pip3 install -r requirements.txt" into the terminal

### Remote Deployment 
 The prgoram was deployed to Heroku. If you have forked/cloned the repository the steps to deploy are:
 1. On Heroku, create a new app.
 2. input a name for your app
 3. Click on the settings tab
 4. Scroll to the Config Vars and click on the "Reveal Config Vars"
 5. Input CREDS into the key field and the content of the Google API creds file into the value area.
 6. Add another config, PORT into key and 8000 into value.
 7. Set the buildbacks to Python and NodeJs in that order .
 8. Link your Heroku app to you repository.
 9. Click on Deploy.
 10. The page will then provide the url to the python terminal.

 The live link can be found here - [Route Me](https://route-me-dh.herokuapp.com/)
### Google Sheet
The program uses a Google Sheets to store saved graphs and mazes. 

1. Sign up to a [Google Account](https://support.google.com/accounts/answer/27441?hl=en#)
2. Open Google Sheets and create a new spreadsheet. [Click here for Google Sheets](https://docs.google.com/spreadsheets/)
3. Change the name of the spreadsheet to 'route_me_data'
    ```python
    SHEET = GSPREAD_CLIENT.open('route_me_data')
    ```
4. You now need to change the name of the worksheet to 'saves'
5. The google sheet is now complete

Now you need to get the API credentials from the [Google Cloud Platform](https://console.cloud.google.com/)

1. Create a new project and give it a name.
2. Select APIs and services from the navigation pane. 
3. Now click Library
4. Search for the Google Sheets and click enable.
5. Search for the google Drive API and click enable.
6. Click create credentials and from the drop down select Google dRIVE api.
7. From the form select Application data
8. Then click No for "are you planning to use this API with compute Engine, Kubernetes engine, App engine or cloud Functions?"
9. Press Create and Continue.
10. Select a role of Editor from the options and click "Done"
11. Navigate to the service account on the credentials page. 
12. On the tab click KEYS then ADD KEY.
13. The Key type will need to be JSON
14. Copy the downloaded JSON file into your repository and name it "creds.json"
15. ADD THE "creds.json" FILE TO .gitignore FILE. DO NOT SHARE PUBLICLY.

***

## Credits / Acknowledgements

- For colour pallete 
[Coolors](https://coolors.co/dac03e-b1b1b1-34d1a2-e63946-f1faee-a8dadc-457b9d-1d3557)

***