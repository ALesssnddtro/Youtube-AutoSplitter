from __future__ import unicode_literals
import datetime
import os
import sys
import youtube_dl
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import re


file_path = os.path.abspath(os.curdir)

# put your youtube link here
video_url = "https://www.youtube.com/watch?v=3FzJHsri8Zw"

titles = []
times = []

# bs4 fetch video data
session = HTMLSession()
response = session.get(video_url)
response.html.render(sleep=3)
soup = BeautifulSoup(response.html.html, "lxml")
data = soup.select('#contents > ytd-macro-markers-list-item-renderer > a', href=True)

for a in data:
    # print("Found the URL:", a['href'])
    time = a['href'].split("=")
    times.append(int(time[2][:-1]))

data = soup.select('#details > h4')

for a in data:
    # print("Found the URL:", a['href'])
    titles.append(a.text)

if len(titles) < 1:
    print("this video has no timecodes")
    sys.exit()

# youtube_dl download video
ydl_opts = {
    'format': ' bestvideo[ext=mp4]+bestaudio[ext=mp4]/mp4',
    'outtmpl': 'Original_Video.%(ext)s'
}

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download([video_url])

title_spaceless = ''.join(filter(str.isalpha, ydl.extract_info(video_url)['title']))
folder_rename_title = re.sub(r'[^A-Za-z]', ' ', ydl.extract_info(video_url)['title'])

# create folders
os.mkdir('Temp_files')
os.mkdir(title_spaceless)

# add final times / video duration
times.append(ydl.extract_info(video_url)['duration'])

# set os path
os.chdir(file_path)

# convert from mp4 to mp3
os.system("ffmpeg -i Original_Video.mp4 Temp_files/Original_Video-converted.mp3")

# create a mp3 for each title
index = 0
for i in titles:
    startSec = times[index]
    endSec = times[index + 1]

    # Seconds to hours, minutes, and seconds.
    startTime = "0" + str(datetime.timedelta(seconds=startSec))
    endTime = "0" + str(datetime.timedelta(seconds=endSec))

    print(i, startTime, endTime, type(endTime))

    # os commands break when inputting non alphabet chars
    file_title_dashes = re.sub(r'[^A-Za-z]', '_', i)

    # trim audio of mp3
    os.system(f'ffmpeg -i Temp_files/Original_Video-converted.mp3 -ss {startTime} -to {endTime} -acodec copy {title_spaceless}/{file_title_dashes}.mp3')
    index = index + 1
    os.rename(f'{title_spaceless}/{file_title_dashes}.mp3', f'{title_spaceless}/{i}.mp3')
os.rename(f'{title_spaceless}', f'{folder_rename_title}')

# delete clutter
os.remove('Temp_files/Original_Video-converted.mp3')
os.rmdir('Temp_files')
