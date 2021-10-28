import requests
import bs4
import pandas as pd
import os
import time
import datetime

from requests.api import request

PAGES=8
if __name__ == "__main__":
    names=[]
    appID=[]

    gameNames=[]
    timeStamp=[]
    avgPlayers=[]
    gain =[]
    gainper=[]
    peakpl=[]
    #scraping data from steamcharts
    for page in range(1,PAGES + 1):
        response = requests.get("https://steamcharts.com/top/p." + str(page))
        soup = bs4.BeautifulSoup(response.text, features="html.parser")
        games = soup.find_all('tr')
        games.pop(0)
        for game in games:
            gameName=game.find('td','game-name')
            names.append(gameName.a.string.strip())
            appID.append(gameName.a['href'].split('/')[2])
    for game in range(len(appID)):
        response = requests.get(f'https://steamcharts.com/app/{appID[game]}')
        soup = bs4.BeautifulSoup(response.text, features="html.parser").tbody
        months = soup.find_all('tr')
        if len(months) > 1:
            data = months[0].find_all('td')
            gameNames.append(names[game])
            timeStamp.append(int(time.mktime(datetime.datetime.strptime(f'{format(datetime.datetime.now().month,"02d")} {datetime.datetime.now().year}',"%m %Y").timetuple())))
            avgPlayers.append(float(data[1].text.strip()))
            gain.append(float(data[2].text.strip()))
            gainper.append(float(data[3].text.strip().translate(bytes.maketrans(b"%",b" "))))
            peakpl.append(int(data[4].text.strip()))
            if len(months) > 2:
                for month in months[1:-1]:
                    data = month.find_all('td')
                    gameNames.append(names[game])
                    timeStamp.append(int(time.mktime(datetime.datetime.strptime(data[0].text.strip(),"%B %Y").timetuple())))
                    avgPlayers.append(float(data[1].text.strip()))
                    gain.append(float(data[2].text.strip()))
                    gainper.append(float(data[3].text.strip().translate(bytes.maketrans(b"%",b" "))))
                    peakpl.append(int(data[4].text.strip()))
        data = months[-1].find_all('td')
        gameNames.append(names[game])
        if len(months) >1:
            timeStamp.append(int(time.mktime(datetime.datetime.strptime(data[0].text.strip(),"%B %Y").timetuple())))
        else:
            timeStamp.append(int(time.mktime(datetime.datetime.strptime(f'{format(datetime.datetime.now().month,"02d")} {datetime.datetime.now().year}',"%m %Y").timetuple())))
        avgPlayers.append(float(data[1].text.strip()))
        peakpl.append(int(data[4].text.strip()))
        gain.append(0)
        gainper.append(0)

        #creating dataframes
    df = pd.DataFrame({'timeStamp':timeStamp,'gameName':gameNames,'averagePlayers':avgPlayers,'gain':gain ,'gainPercentage':gainper,'peakPlayers':peakpl})
    try:
        os.mkdir("ScrapedData")
    except Exception:
        pass
    df.to_csv("ScrapedData/topGames.csv")
    print(f'\U00002714 top {PAGES * 25} games scraped from steamcharts.com')