import datetime, urllib, json
import matplotlib.pyplot as plt
from newsapi import NewsApiClient
import numpy as np

AnalysisStartDate = datetime.date(2018, 2, 2)
NUM_OF_DAYS = 4
NEWS_API_KEY = 'ad490ddac082441d8f6980842b815629'
ALPHA_API_KEY = "504P0GG4DGGV7D16"
FUNC = "TIME_SERIES_DAILY"
obvURL = "https://www.alphavantage.co/query?function=" + FUNC + "&interval=daily&apikey=" + ALPHA_API_KEY
newsapi = NewsApiClient(api_key=NEWS_API_KEY)

def previousWeekday(date):
    #Mon-Sun is represented by 0-6
    date -= datetime.timedelta(days=1)
    while date.weekday() > 4:
        date -= datetime.timedelta(days=1)
    return date


def getJsonResponse(url):
    response = urllib.urlopen(url)
    return json.loads(response.read())


def parseOBV(obvs, startDate):
    obvDict = {}
    for i in range(NUM_OF_DAYS):
        currentDate = str(startDate)
        if (obvs.has_key(currentDate)):
            obvDict[startDate] = obvs[currentDate]
        startDate = previousWeekday(startDate)
    return obvDict


def getOBVFor(stockSymbol, url, analysisStartDate):
    url += "&symbol=" + stockSymbol
    result = getJsonResponse(url)["Time Series (Daily)"]
    obvResults = {}
    for weekDay, obvValue in result.iteritems():
        obvResults[weekDay] = obvValue["5. volume"]
    return parseOBV(obvResults, analysisStartDate)

def getNumberOfNews(searchTerm, startDate):
    prevWeekDay = previousWeekday(startDate)
    numberOfNews = newsapi.get_everything(q=searchTerm,
                                      from_parameter=str(prevWeekDay),
                                      to=str(startDate),
                                      language='en')
    return numberOfNews["totalResults"]


def getMonthlyNewsCount(searchTerm, startDate):
    newsCount = {}
    for i in range(NUM_OF_DAYS):
        currentDate = str(startDate)
        newsCount[startDate] = getNumberOfNews(searchTerm, startDate)
        startDate = previousWeekday(startDate)
    return newsCount


def two_scales(ax1, dates, obvs, count):
    ax2 = ax1.twinx()
    ax1.plot(dates, obvs, '-bo')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Trading Volume')

    ax2.plot(dates, count, '-ro')
    ax2.set_ylabel('News Count')
    return ax1, ax2


def color_y_axis(ax, color):
    for t in ax.get_yticklabels():
        t.set_color(color)
    return None


if __name__ == '__main__':
    companyAndSymbols = { "Apple" : "AAPL"}
    for company, stockSymbol in companyAndSymbols.iteritems():
        obvresult = getOBVFor(stockSymbol, obvURL, AnalysisStartDate)
        monthlyNewsCount = getMonthlyNewsCount(company, AnalysisStartDate)
        dates = sorted(list(obvresult.keys()))
        obvs = []
        count = []
        for date in dates:
            obvs.append(obvresult[date])
            count.append(monthlyNewsCount[date])
            print "Current Week date: " + str(date)
            print "==========================================="
            print "OBV values: " + str(obvresult[date])
            print "News Count: " + str(monthlyNewsCount[date])
        correlation = np.corrcoef(obvs, count)[0, 1]
        print "Company Name: " + company
        print "Correlation: " + str(correlation)
        #Plot for individual company
        fig, ax = plt.subplots()
        ax1, ax2 = two_scales(ax, dates, obvs, count)
        color_y_axis(ax1, 'b')
        color_y_axis(ax2, 'r')
        plt.show()
