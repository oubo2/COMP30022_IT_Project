# ePortfolio

The ePortfolio is a part of our COMP30022 Project. As its name implies, it allows users to create an account, upload items to their portfolio as well as sharing their profile and portfolios for others to see.



## Installation

Simply clone this repo and run it from your Python editor of choice. 



## Usage and Deployment

Follow these instructions near the top of app.py when testing locally.

```python
# Config for wkhtmltopdf which converts a html page to pdf
# COMMENT THIS WHEN TESTING LOCAL!!
# UNCOMMENT THIS WHEN PUSHING TO PRODUCTION!!
app.config["WKHTMLTOPDF_CMD"] = subprocess.Popen(
    ['which', os.environ.get('WKHTMLTOPDF_BINARY', 'wkhtmltopdf')],
    stdout=subprocess.PIPE).communicate()[0].strip()

```

To run the project locally, use port 9999 as 5000 is taken for PostgreSQL. Type the following in to the terminal (make sure that the terminal is in the project's root directory) and ensure that the environment is venv (virtual environment). Then navigate to http://localhost:9999/.

```Bash
Python app.py
```

To deploy to Heroku, ensure that Heroku CLI is installed, and in the terminal, log in to Heroku and do the following line to prepare for a commit and push:

```Bash
git add .
git commit -m "message"
git push heroku master
```



## File Structure

In the root folder, we have four Python files:

app.py is the main file handling the routes and is the entry point to our project.

filters.py contains several important filtering functions used for checking file types, calculating age, concatenating strings together to form a link to access an S3 object and other auxiliary functions.

config.py contains the secret keys used to access S3 as well as the Flask secret key for handling sessions, imported from the .env file.

test_flask.py handles testing for the project, including navigating to different pages as well as checking whether logging in will give the correct response.

All html files are stored in the Templates folder.

Inside the Static folder, we have:

The wkhtmltopdf folder contains the configuration for our export to pdf function.

The landing folder contains picture assets for the landing page.

The Icons folder contains the icons used to show word docs, pdfs, videos and misc files in the portfolio.

The css folder, as its name implies, contains all the css files.




## Interaction with S3
Uploading portfolio items: files can be uploaded to our S3 bucket through the s3_upload function, visualised in the portfolio.html page. A user can browse through their local files and select something to be uploaded.

Downloading portfolio items: files can be downloaded in the portfolio page. For some image formats, clicking the download button will display the image on the browser. For others, the browser will prompt the user to download the file. This is handled in the s3_download function.

Deleting portfolio items: files can be deleted from the portfolio page by clicking the delete button next to items. The app queries the file's key and deletes it from the bucket accordingly. This is handled in the s3_delete function.

Displaying portfolio items: this is done in the art_portfolio.html page with the help of auxiliary functions from filter.py and art_portfolio() in app.py. It filters out items that don't belong to the user and only shows them their own items associated with their unique ID.

## UserInfo class
The UserInfo class contains user information such as their unique ID, email, password, name, bio, interests, age, occupation and education. All of which are displayed in their profile page bar their ID, email and password for obvious reasons. These information are stored in the Heroku PostgreSQL database.

## Login and Signup forms
They are handled in the LoginForm and SignupForm classes respectively, and uses the wtforms module to handle validations such as correct email format and correct length passwords.
