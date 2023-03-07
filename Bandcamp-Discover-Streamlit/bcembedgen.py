from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, ElementClickInterceptedException
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import random
import re


def verify_link(url):
    pattern = re.compile(r'bandcamp\.com/(album|track)')
    match = pattern.search(url)
    return bool(match)

def replace_special_chars_with_dash(s):
    return '-'.join(filter(None, re.split(r'[^a-zA-Z0-9\s]+', s.replace(' ', '-'))))

def clickNextCarousel(webelement):
    click = 1
    flag = False
    while click == 1:
        time.sleep(1)
        try:
            btn = webelement.find_element(By.CLASS_NAME, 'next-button')
            if btn is None:
                break
            btn.click()
            click-=1
            flag = True
        except ElementNotInteractableException:
                flag = False
                break
        except ElementClickInterceptedException:
                flag = False
                break
        except NoSuchElementException:
                flag = False
                break
    return flag

def digorempty(driver):
    flag = False
    while flag is False:
        time.sleep(1)
        try:
            element = driver.find_element(By.CLASS_NAME,"dig-deeper-items")
            flag = True
        except NoSuchElementException:
            break
    return flag

# tag = "house"
# tag = "deep-house"
def tracks(tag):

    tag_clean = replace_special_chars_with_dash(tag)
    url = f"https://bandcamp.com/tag/{tag_clean}/"
    # Open the web page
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(1)

    carousels = driver.find_elements(By.CLASS_NAME, 'carousel-wrapper')

    sections_tracks = pd.DataFrame(columns=['section','artist','title','link'])
    
    if carousels:
        for carousel in carousels:
            while True:
                carousel_soup = BeautifulSoup(carousel.get_attribute("outerHTML"), 'html.parser')
                section_title = carousel_soup.find("h3",{"class":"carousel-title"}).contents[0].strip()        

                section = carousel_soup.find_all("div",{"class":"col col-3-12 item"})
                if section == []:
                    section = carousel_soup.find_all("div",{"class":"col col-3-15 item"})
                if section == []:
                    section = carousel_soup.find_all("div",{"class":"col col-5-15 item"})
                if section != []:
                    for track in section:
                        temp = track.find("div",{"class":"info"})
                        link = temp.find('a', href=True).get('href')
                        if verify_link(link):
                            title = temp.find("div",{"class":"title"}).text
                            artist = temp.find("div",{"class":"artist"}).find('span').text
                            if ~sections_tracks[sections_tracks.duplicated(subset=sections_tracks.columns)].isin([section_title,artist,title,link]).any().any():
                                sections_tracks.loc[len(sections_tracks.index)] = [section_title,artist,title,link]
                        else:
                            break
                if (clickNextCarousel(carousel) == False):
                    break
    else:
        if digorempty(driver):
            alt_section = driver.find_element(By.CLASS_NAME,"dig-deeper-items")
            alt_tracks = BeautifulSoup(alt_section.get_attribute("outerHTML"), 'html.parser')
            alt_tracks = alt_tracks.find_all("div",{"class":"col col-3-15 dig-deeper-item item"})
            if alt_tracks:
                for track in alt_tracks:
                    temp = track.find("div",{"class":"info"})
                    link = temp.find('a', href=True).get('href')
                    if verify_link(link):
                        title = temp.find("div",{"class":"title"}).text
                        artist = temp.find("div",{"class":"artist"}).find('span').text
                    sections_tracks.loc[len(sections_tracks.index)] = ['None',artist,title,link]
        else:
            driver.close()
            return sections_tracks.drop_duplicates().reset_index(drop=True)

    driver.close()

    return sections_tracks.drop_duplicates().reset_index(drop=True)

# returns album id & track id
def track_embed_albumid_trackid(url):

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        x = soup.select('li[class^="recommended-album footer-"]')
        for li in x:
            match = re.search(r'a(\d+)', li.get('data-from'))
            if match:
                number = match.group(1)
                album_id = (number)
            break
        y = soup.find("meta",{"property":"og:video"})
        # track id
        if y is not None:
            track_id = (y.get("content").split("track=")[1].split("/")[0])
        else:
            return None
        return (album_id, track_id)
    else:
        return response.status_code
    
def track_embed_generator(album_id,track_id,url,title,artist,album_support_count,track_support_count):

    def compute_number(x, y):
        s = x + y
        if s == 0:
            return 0.524
        elif 0 < s <= 40:
            return 0.67
        elif 40 < s <= 50:
            return s * 0.018856
        elif 50 < s <= 60:
            return s * 0.014856
        elif 60 < s <= 80:
            return 0.95
        elif 80 < s < 100:
            return 0.98
        elif s >= 100:
            return 1.0

    size = (compute_number(album_support_count,track_support_count)*420)

    return f"""<iframe style="border: 0; width: {int(size)}px; height: {int(size)}px;" src="https://bandcamp.com/EmbeddedPlayer/album={album_id}/size=large/bgcol=ffffff/linkcol=0687f5/tracklist=false/track={track_id}/transparent=true/" seamless><a href="{url}">{title} by {artist}</a></iframe>"""

def verify_album(url):
    pattern = re.compile(r'bandcamp\.com/(album)')
    match = pattern.search(url)
    return bool(match)

def review_count(soup):
    reviews = soup.find("div",{"class":"collected-by tralbum collectors"})
    if reviews:
        fans = reviews.find("div",{"class":"no-writing"}).find_all("a",{"class":"fan pic"})
        if(len(fans)==60):
            if(reviews.find("a",{"class":"more-thumbs"})):
                if(reviews.find("a",{"class":"more-writing"})):
                    return(100) 
            else:
                return(80) 
        else:
            return(len(fans))
    else:
        return 0
    return 0


def embed_tracks_generator(tracks):
    
    if tracks.empty:
        return None
    pattern = re.compile(r'(https://.*\.bandcamp\.com)')

    embed_tracks = pd.DataFrame(columns=['artist','title','album_support_count','track_support_count','album_url','track_url','track_embed'])

    size = 10 if len(tracks) > 10 else len(tracks)-1

    for x in tracks.sample(size).link:
        url = x.replace('?from=hp','')
        if 'bandcamp.com/album' in url:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                album_support_count = review_count(soup)
                artist = soup.find("div",{"id":"name-section"}).find("span").find("a").text
                track_table = soup.find("table", {"id":"track_table"})
                if track_table:
                    table_rows = track_table.find_all("tr",{"class":"track_row_view linked"})
                    tr = random.choice(table_rows)
                    title = tr.find("td",{"class":"title-col"})
                    song_title = title.find("span").text
                    match = pattern.search(url)
                    if match:
                        track_url = (match.group(1)) + title.find("a").get('href')
                        if track_embed_albumid_trackid(track_url) is not None:
                            album_id, track_id = track_embed_albumid_trackid(track_url)
                            response = requests.get(track_url)
                            track_soup = BeautifulSoup(response.text, 'html.parser')
                            track_support_count = review_count(track_soup)
                            track_embed_code = track_embed_generator(album_id,track_id,url,song_title,artist,album_support_count,track_support_count)
                            embed_tracks.loc[len(embed_tracks.index)] = [artist,song_title,album_support_count,track_support_count,url,track_url,track_embed_code]
                        elif track_embed_albumid_trackid(track_url) is None:
                            print('None track url')
                        

    return embed_tracks