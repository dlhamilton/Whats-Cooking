import os

os.environ["DATABASE_URL"]="Starting with 'postgres://', only required for deployment"
os.environ["SECRET_KEY"]="YOUR KEY HERE"
os.environ["DEVELOPMENT"]="True"
os.environ["HEROKU_HOST_NAME"] = "YOUR HOST NAME"
os.environ["CLOUDINARY_URL"]= "Starting with 'cloudinary://'"
os.environ["EMAIL_HOST_USER"]="only required for deployment or if not 'DEV_ENVIRONMENT_EMAIL = True'"
os.environ["EMAIL_HOST_PASSWORD"]="only required for deployment or if not 'DEV_ENVIRONMENT_EMAIL = True'"
os.environ["GOOGLE_OAUTH_CLIENT_ID"] = "YOUR GOOGLE ID"
os.environ["GOOGLE_OAUTH_SECRET"] = "YOUR GOOGLE KEY"
