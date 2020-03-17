#!/usr/bin/python3
from pathlib import Path
import sys
import requests
import json



# EPIC api docs
# https://epic.gsfc.nasa.gov/about/api

# Maintain a json file with metadata for each image
SAVE_META = True

# "jpg" for faster download
# "png" for higher quality
image_format = "jpg"

# Data storage location is received as a cmdline argument

if len(sys.argv) == 2:
    dataset_folder_location = Path(sys.argv[1])
else:
    dataset_folder_location = Path.cwd()

image_folder = dataset_folder_location / "EPIC/natural"

# To check for additional images uploaded to
# previously checked dates, delete acquired_file
acquired_file = dataset_folder_location / "dates_acquired.json"

if SAVE_META:
    metadata_file = dataset_folder_location / "EPIC_data.json"

baseurl = "https://epic.gsfc.nasa.gov/"

if not Path.exists( image_folder ):
    image_folder .mkdir(parents=True)

# load dates with downloaded images
if Path.is_file( acquired_file ):
    with open( acquired_file, 'r' ) as file:
        dates = json.loads( file.read() )
else:
    dates = []

if SAVE_META:
    # load metadata of downloaded images to append to
    if Path.is_file( dataset_folder_location / metadata_file ):
        with open( dataset_folder_location / metadata_file, 'r') as file:
            metadata = json.loads( file.read() )
    else:
        metadata = []

# get a list of images that have already been downloaded
downloaded_images = []
for file in image_folder.iterdir():
    downloaded_images.append(file)

# determine if there are any new dates with available imagery
available_dates = requests.get( baseurl + "api/natural/available" ).json()
new_dates = list(set( available_dates ) - set( dates ))
new_dates.sort()

for date in new_dates:
    # download unacquired image metadata for date
    date_data = requests.get( baseurl + "api/natural/date/" + date ).json()
    if SAVE_META:
        # store metadata and date of acquired images
        metadata.extend( date_data )
        dates.append( date )

    # download unacquired images
    for image_data in date_data:
        file_name = image_data[ "image" ] + "." + image_format
        if file_name not in downloaded_images:
            image_url = baseurl + "archive/natural/" + date.replace('-','/') + '/' + image_format + '/' + file_name
            if not Path.exists( image_folder / file_name ):
                print( "Downloading:", file_name )
                image = requests.get( image_url )
                with open( image_folder + file_name, 'wb') as file:
                    file.write( image.content )
            else:
                print("Image file found:  " + file_name)

if SAVE_META:
    # Save data
    with open( metadata_file, 'w') as file:
        json.dump( metadata, file)

# Save dates with acquired data
with open( acquired_file, 'w') as file:
    json.dump( dates, file)