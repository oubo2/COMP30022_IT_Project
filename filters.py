import arrow
import mimetypes
import os
import boto3
import botocore
from datetime import date
import calendar


# Converts the datetime to "x hours/days ago" format
def convert_date(old_datetime):
    pretty_datetime = arrow.get(old_datetime)
    return pretty_datetime.humanize()


# Detect the file's type
def file_type(filename):
    f = os.path.splitext(filename)
    f_extention = f[1]
    return f_extention


# Return the url of an image
def get_image(key):
    s3 = boto3.resource('s3',
                        aws_access_key_id='AKIAIVUAFHRHT4F6FHEA',
                        aws_secret_access_key='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')
    s3.Bucket('sss-portfolio').Object(key).key
    url = f"https://sss-portfolio.s3.us-east-2.amazonaws.com/" + s3.Bucket('sss-portfolio').Object(key).key
    return url


# Get avatar source
# TODO: support other image formats than just PNG
def get_avatar(user_id):
    s3 = boto3.resource('s3',
                        aws_access_key_id='AKIAIVUAFHRHT4F6FHEA',
                        aws_secret_access_key='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')

    user_avatar = "/Avatar/" + str(user_id) + ".png"
    try:
        return "https://sss-portfolio.s3.us-east-2.amazonaws.com" + user_avatar
    except botocore.exceptions.ClientError:
        print("https://sss-portfolio.s3.us-east-2.amazonaws.com" + user_avatar)
        print("not found")
        return "https://sss-portfolio.s3.us-east-2.amazonaws.com/Avatar/profile.png"

    return "https://sss-portfolio.s3.us-east-2.amazonaws.com/Avatar/profile.png"


# Checks to see if an item belongs to the authenticated user
def show_own_items(id, filename):
    file_id = filename.split('/')[0]
    if file_id == str(id):
        return True
    return False


# Checks whether an item is an image
def filter_image(filename):
    if '.' not in filename:
        return False

    t = filename.rsplit('.', 1)[1]

    if t.upper() in ['PNG', 'JPG', 'JPEG', 'GIF']:
        return True
    else:
        return False


# Checks whether an item is an word doc
def filter_word(filename):
    if '.' not in filename:
        return False

    t = filename.rsplit('.', 1)[1]

    if t.upper() in ['DOC', 'DOT', 'WBK', 'DOCX', 'DOCM', 'DOTX', 'DOTM', 'DOCB']:
        return True
    else:
        return False


# Checks whether an item is an pdf
def filter_pdf(filename):
    if '.' not in filename:
        return False

    t = filename.rsplit('.', 1)[1]

    if t.upper() in ['PDF']:
        return True
    else:
        return False


# Checks whether an item is an pdf
def filter_video(filename):
    if '.' not in filename:
        return False

    t = filename.rsplit('.', 1)[1]

    if t.upper() in ['MP4', 'MOV', 'WMV', 'FLV', 'AVI', 'AVCHD', 'WEBM', 'MKV']:
        return True
    else:
        return False


# Checks whether an item is a misc item
def filter_misc(filename):
    if '.' not in filename:
        return False

    t = filename.rsplit('.', 1)[1]

    if t.upper() not in ['DOC', 'DOT', 'WBK', 'DOCX', 'DOCM', 'DOTX', 'DOTM', 'DOCB', 'PDF', 'PNG', 'JPG', 'JPEG',
                         'GIF']:
        return True
    else:
        return False


# Removes the subdirectory id in the file name given a key
def remove_file_id(key):
    return key.split('/')[1]


# Calculate age based on today's date and user birthday
def calc_age(year, month, day):
    months_list = [month for month in calendar.month_name][1:]
    month_name = months_list.index(month)

    today = date.today()
    age = today.year - year - ((today.month, today.day) < (month_name, day))
    return age
