import requests
import bs4
import pandas as pd
import os
import sys
import time
import datetime
import argparse
from time import sleep

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pages", help="insert number of pages to scrap from steamcharts", type=int)
    parser.add_argument('-l','--log', help="log the problematic games into the specified file")
    args = parser.parse_args()

    if args.log:
        log =["name appID \n\n"]
    names=[]
    appID=[]


    #data from steamcharts
    gameNames=[]
    timeStamp=[]
    avgPlayers=[]
    appIDS = []
    gain =[]
    gainper=[]
    peakpl=[]

    #data from steam API
    developers= []
    publishers =[]
    windows =[]
    mac =[]
    linux =[]
    metacriticScore =[]

    #data from SteamSpy
    positiveRev = []
    negativeRev = []
    positiveRevPer = [] 
    languages= []
    genre = []
    tags = []
    #scraping data from steamcharts
    for page in range(1,args.pages + 1):
        response = requests.get("https://steamcharts.com/top/p." + str(page))
        if response.status_code != requests.codes.ok:
            response.raise_for_status()
        soup = bs4.BeautifulSoup(response.text, features="lxml")
        games = soup.find_all('tr')
        games.pop(0)
        for game in games:
            gameName=game.find('td','game-name')
            names.append(gameName.a.string.strip())
            appID.append(gameName.a['href'].split('/')[2])
    #scraping time data for scraped games
    for game in range(len(appID)):
        response = requests.get(f'https://steamcharts.com/app/{appID[game]}')
        if response.status_code != requests.codes.ok:
            response.raise_for_status()
        soup = bs4.BeautifulSoup(response.text, features="lxml").tbody
        months = soup.find_all('tr')
        if len(months) > 1:
            data = months[0].find_all('td')
            gameNames.append(names[game])
            appIDS.append(appID[game])
            timeStamp.append(int(time.mktime(datetime.datetime.strptime(f'{format(datetime.datetime.now().month,"02d")} {datetime.datetime.now().year}',"%m %Y").timetuple())))
            avgPlayers.append(float(data[1].text.strip()))
            gain.append(float(data[2].text.strip()))
            gainper.append(float(data[3].text.strip().translate(bytes.maketrans(b"%",b" "))))
            peakpl.append(int(data[4].text.strip()))
            if len(months) > 2:
                for month in months[1:-1]:
                    data = month.find_all('td')
                    gameNames.append(names[game])
                    appIDS.append(appID[game])
                    timeStamp.append(int(time.mktime(datetime.datetime.strptime(data[0].text.strip(),"%B %Y").timetuple())))
                    avgPlayers.append(float(data[1].text.strip()))
                    gain.append(float(data[2].text.strip()))
                    gainper.append(float(data[3].text.strip().translate(bytes.maketrans(b"%",b" "))))
                    peakpl.append(int(data[4].text.strip()))
        data = months[-1].find_all('td')
        gameNames.append(names[game])
        appIDS.append(appID[game])
        if len(months) >1:
            timeStamp.append(int(time.mktime(datetime.datetime.strptime(data[0].text.strip(),"%B %Y").timetuple())))
        else:
            timeStamp.append(int(time.mktime(datetime.datetime.strptime(f'{format(datetime.datetime.now().month,"02d")} {datetime.datetime.now().year}',"%m %Y").timetuple())))
        avgPlayers.append(float(data[1].text.strip()))
        peakpl.append(int(data[4].text.strip()))
        gain.append(0)
        gainper.append(0)
        sys.stdout.write(f'scraping from steamchart: {game} \ {len(appID)}\r')
        sys.stdout.flush()
    print(f'\U00002714 top {args.pages * 25} games scraped from steamcharts.com')
    #scraping from steam API
    for game in range(len(appID)):
        response=requests.get("https://store.steampowered.com/api/appdetails",params={"appids":appID[game]})
        if response.status_code != requests.codes.ok:
            response.raise_for_status()
        try:
            data =response.json()[str(appID[game])]
            data = data['data']
        except Exception:
            #invalid games append infos with null values
            developers.append(None)
            publishers.append(None)
            windows.append(None)
            mac.append(None)
            linux.append(None)
            metacriticScore.append(None)
            positiveRev.append(None)
            negativeRev.append(None)
            positiveRevPer.append(None)
            languages.append(None)
            genre.append(None)
            tags.append(None)
            if args.log:
               log.append(f'{names[game]} {appID[game]}\n')
            continue
        try:
            developers.append(data['developers'])
        except Exception:
            developers.append({})
        try:
            publishers.append(data['publishers'])
        except Exception:
            publishers.append({})
        try:
            windows.append(data['platforms']['windows'])
        except Exception:
            windows.append(False)
        try:
            mac.append(data['platforms']['mac'])
        except Exception:
            mac.append(False)
        try:
            linux.append(data['platforms']['linux'])
        except Exception:
            linux.append(False)
        try:
            metacriticScore.append(data['metacritic']['score'])
        except Exception:
            metacriticScore.append(-1)
        #scraping from steamSpy
        response=requests.get("https://steamspy.com/api.php",params={"request" : "appdetails", "appids":appID[game]})
        if response.status_code != requests.codes.ok:
            response.raise_for_status()
        data =response.json()
        positiveRev.append(data['positive'])
        negativeRev.append(data['negative'])
        positiveRevPer.append(data['positive']/(data['positive'] + data['negative']))
        languages.append(data['languages'].split(", "))
        genre.append(data['genre'].split(", "))
        tags.append(list(data['tags']))
        sys.stdout.write(f'scraping from steam: {game} \ {len(appID)}\r') #updating progress bar which is overwrited after done
        sys.stdout.flush()
        sleep(1.5)
    #creating dataframes
    steam= pd.DataFrame({'appID': appID, 'developers':developers, 'publishers': publishers,'mac' :mac, 'linux' : linux, 'metacriticScore' : metacriticScore})
    df = pd.DataFrame({'timeStamp':timeStamp,'gameName':gameNames, 'appID': appIDS,'averagePlayers':avgPlayers,'gain':gain ,'gainPercentage':gainper,'peakPlayers':peakpl})
    steamSpy = pd.DataFrame({'appID' : appID, 'positive reviews':positiveRev, 'negative reviews':negativeRev, 'share of positive reviews' : positiveRevPer, 'supported languages':languages, 'genres' : genre, 'tags' : tags})
    result = df.set_index('appID').join(steam.set_index('appID')).join(steamSpy.set_index('appID'))
    try:
        os.mkdir("ScrapedData")
    except Exception:
        pass
    result.to_json("ScrapedData/topGames.csv", orient="records")
    if args.log:
        with open(args.log,'w') as f:
            f.writelines(log) 