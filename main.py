import requests
import bs4
import pandas as pd
PAGES=8
if __name__ == "__main__":
    names=[]
    appID=[]
    currentPlayers=[]
    peakPlayers=[]
    hoursPlayed=[]
    for page in range(1,PAGES + 1):
        response = requests.get("https://steamcharts.com/top/p." + str(page))
        soup = bs4.BeautifulSoup(response.text, features="html.parser")
        games = soup.find_all('tr')
        games.pop(0)
        for game in games:
            gameName=game.find('td','game-name')
            names.append(gameName.a.string.strip())
            appID.append(gameName.a['href'].split('/')[2])
            currentPlayers.append(int(game.find('td','num').string))
            peakPlayers.append(int(game.find('td','peak-concurrent').string))
            hoursPlayed.append(int(game.find('td','player-hours').string))

    df = pd.DataFrame({'name':names,'appID':appID})
    df.to_csv("ScrapedData/topGames.csv")