from celery import shared_task
from celery.utils.log import get_task_logger
from selenium.common.exceptions import TimeoutException

from .models import PlayerMatchSingular, OverallSentiment
from s2protocol import versions
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import mpyq
import os
from lxml import html
from shutil import rmtree
from uuid import uuid4
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from os import getcwd, listdir, mkdir, rename
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = get_task_logger(__name__)

emojiTranslations = {"(happy)": "😁", ":D": "😂", "(rofl)": "😂", ":(": "😢",
                     "(sad)": "😢", ":@": "😠", "(angry)": "😠", ":O": "😲",
                     "(surprised)": "😲", ";P": "😜", "(silly)": "😜",
                     ":|": "😐", "(speechless)": "😐", ":]": "😍", "(inlove)": "😍",
                     "B-}": "😎", "(cool)": "😎", ":S": "😨", "(scared)": "😨",
                     "|-]": "😴", "(sleepy)": "😴", "(kiss)": "😘", "(devil)": "😈",
                     "(hearts)": "💕"
                     }


def enable_download_in_headless_chrome(driver, download_dir):
    # add missing support for chrome "send_command"  to selenium webdriver
    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')

    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}

    command_result = driver.execute("send_command", params)


def analyze_sentiments(archive_, protocol_):
    contents = archive_.read_file('replay.initData')
    lobbyDetails = protocol_.decode_replay_initdata(contents)

    uniqueIdentifier = lobbyDetails['m_syncLobbyState']['m_gameDescription']['m_randomValue']

    if PlayerMatchSingular.objects.filter(uniqueID=uniqueIdentifier).exists():
        print("Already in Database")
        return

    contents = archive_.read_file('replay.details')

    gameDetails = protocol_.decode_replay_details(contents)
    # in the future, add functionality to check for duplicate replays
    # compare up to the database, only save the gamedetails in the database
    # gamedetails contain specific time and game equivalencies that are
    # completely unique, just a call simple contains on the DB
    sentimentTotals = [0 for i_ in range(len(gameDetails['m_playerList']) * 2)]

    contents = archive_.read_file('replay.message.events')

    messageEvents = protocol_.decode_replay_message_events(contents)
    listmessages = []
    listMessageSentiments = []
    compoundUserSentiments = []
    for i in range(len(gameDetails['m_playerList'])):
        listmessages.append([])
        listMessageSentiments.append([])
        compoundUserSentiments.append(0)

    analyzer = SentimentIntensityAnalyzer()

    for event in messageEvents:
        if event['_event'] == 'NNet.Game.SChatMessage':
            curMessage = str(event['m_string'])

            curMessage = curMessage[2: len(curMessage) - 1]

            for key in emojiTranslations:
                if key in curMessage:
                    curMessage = curMessage.replace(key, emojiTranslations[key])

            sentimentResult = analyzer.polarity_scores(curMessage)
            compoundSentiment = sentimentResult['compound']
            uid = event['_userid']
            sender = uid['m_userId']
            if sender >= len(gameDetails['m_playerList']):
                continue
            sentimentTotals[sender * 2] += 1
            sentimentTotals[(sender * 2) + 1] += compoundSentiment
            listmessages[sender].append(curMessage)
            listMessageSentiments[sender].append(compoundSentiment)
            print("CurrentUser: " + str(sender) + "   Sentiment: " + str(compoundSentiment))

            compoundUserSentiments = []
            for i_ in range(1, len(sentimentTotals), 2):
                # Counting Non-Message Players in Total Player Sentiment Count
                if sentimentTotals[i_ - 1] == 0:
                    compoundUserSentiments.append(0)
                else:
                    compoundUserSentiments.append(sentimentTotals[i_] / sentimentTotals[i_ - 1])

                # Not counting Non-Message Players in Total Player Sentiment Count
                # Results in an innacurate average as it disregards neutral players
                # if sentimentTotals[i - 1] > 0:
                #    compoundUserSentiments.append(sentimentTotals[i] / sentimentTotals[i - 1])

            print(sentimentTotals)
            print(compoundUserSentiments)

    playerList = gameDetails['m_playerList']
    overallSentiments = OverallSentiment.objects.get(pk=1)
    for i in range(len(gameDetails['m_playerList'])):
        curPlayerName = strip_html(playerList[i]['m_name'].decode("utf-8"))
        curRacePlayerMatch = ""
        greenLight = True
        curRace = str(playerList[i]['m_race'])
        if "Zerg" in curRace:
            overallSentiments.zergSentimentCount += 1

            overallSentiments.zergSentimentOverall += compoundUserSentiments[i]

            curRacePlayerMatch = "Zerg"
        elif "Terran" in curRace:
            overallSentiments.terranSentimentCount += 1

            overallSentiments.terranSentimentOverall += compoundUserSentiments[i]

            curRacePlayerMatch = "Terran"
        elif "Protoss" in curRace:
            overallSentiments.protossSentimentCount += 1

            overallSentiments.protossSentimentOverall += compoundUserSentiments[i]

            curRacePlayerMatch = "Protoss"
        else:
            greenLight = False

        if greenLight:
            PlayerMatchSingular.objects.create(username=curPlayerName, curRace=curRacePlayerMatch,
                                               uniqueID=uniqueIdentifier,
                                               compoundSentiment=compoundUserSentiments[i], messages=listmessages[i],
                                               messageSentiments=listMessageSentiments[i])
            firstPlayer = PlayerMatchSingular.objects.order_by('id')[0]
            firstPlayer.delete()

    overallSentiments.save()


def strip_html(s):
    return str(html.fromstring(s).text_content())


@shared_task()
def process_uploaded_replay(replayFiles):
    print("Task Running...")

    for file in replayFiles:
        archive = mpyq.MPQArchive(file)

        contents = archive.header['user_data_header']['content']
        header = versions.latest().decode_replay_header(contents)
        baseBuild = header['m_version']['m_baseBuild']
        try:
            protocol = versions.build(baseBuild)
            analyze_sentiments(archive, protocol)
        except ImportError as err:
            print(err.args)


@shared_task()
def selenium_process_replay():
    print("Processing One Map From Ladder Rotation")

    options = Options()

    options.add_argument("--headless")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')

    options.add_experimental_option("prefs", {
        "download.default_directory": getcwd() + '\\TempReplays',
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing_for_trusted_sources_enabled": False,
        "safebrowsing.enabled": False
    })

    curAllMaps = open(getcwd() + '/PlayerMatch/ValidMapRotationBackup.txt').readlines()
    remaining = len(curAllMaps)
    if remaining < 1:
        return

    curMap = curAllMaps[0]
    open(getcwd() + '/PlayerMatch/ValidMapRotationBackup.txt', 'w').writelines(curAllMaps[1:])

    curMapLink = ""
    # browser = webdriver.Chrome(getcwd() + '/PlayerMatch/chromedriver', options=options)
    browser = webdriver.Chrome(executable_path=str(os.environ.get('CHROMEDRIVER_PATH')), options=options)

    enable_download_in_headless_chrome(browser, getcwd() + '/PlayerMatch/TempReplays')

    curMapName = curMap
    curMapName = curMapName.replace(" ", "%20")

    curMapLink = "https://gggreplays.com/matches#?map_name=" + curMapName + "&page="
    isLast = False
    isLastPage = False
    curPage = 1
    browser.get(curMapLink + str(curPage))
    sleep(1)
    while not isLastPage:

        fileNameList = []
        TableBody = browser.find_element_by_xpath('//*[@id="matches"]/div[3]/div[3]/table/tbody')
        AllRows = TableBody.find_elements_by_tag_name("tr")
        TotalRowNum = len(AllRows)

        for i in range(2, TotalRowNum + 1):
            # Add this below if there is loading error on the table elements

            try:
                DateElement = WebDriverWait(browser, 5).until(EC.visibility_of_element_located((By.XPATH,
                                                                                                '//*[@id="matches"]/div[3]/div[3]/table/tbody/tr[{}]/td[20]'.format(
                                                                                                    i))))
            except TimeoutException as err:
                continue

            DateText = DateElement.text
            # browser.find_element_by_xpath(
            # '//*[@id="matches"]/div[3]/div[3]/table/tbody/tr[{}]/td[20]'.format(i)).text
            PlayerText = browser.find_element_by_xpath(
                '//*[@id="matches"]/div[3]/div[3]/table/tbody/tr[{}]/td[6]'.format(i)).text

            if "A.I." not in PlayerText and PlayerText:

                if "year" in DateText:
                    print(PlayerText)
                    matchLink = browser.find_element_by_xpath(
                        '//*[@id="matches"]/div[3]/div[3]/table/tbody/tr[{}]/td[2]/a'
                            .format(i)).get_attribute('href')
                    print(matchLink)

                    # browser.find_element_by_xpath('//*[@id="matches"]/div[3]/div[3]/table/tbody/tr[{}]'.format(i)).click()
                    before = listdir(getcwd() + '/PlayerMatch/TempReplays')

                    downURL = matchLink + "/replay"
                    browser.get(downURL)
                    # sleep(2)
                    after = listdir(getcwd() + '/PlayerMatch/TempReplays')
                    change = set(after) - set(before)
                    file_name = ""
                    loopCount = 0
                    while loopCount < 16 and len(change) == 0:
                        sleep(0.25)
                        after = listdir(getcwd() + '/PlayerMatch/TempReplays')
                        change = set(after) - set(before)
                        if len(change) > 0:
                            file_name = change.pop()
                            if 'crdownload' not in file_name:
                                break
                        loopCount += 1

                    if loopCount == 16:
                        browser.get(curMapLink + str(curPage))
                        continue
                        # and 'crdownload'

                    if file_name and 'crdownload' not in file_name:
                        fileNameList.append(file_name)

                    # browser.get(curMapLink+str(j))

        print(fileNameList)

        for fileName in fileNameList:
            archive = mpyq.MPQArchive(getcwd() + '/PlayerMatch/TempReplays/' + fileName)
            print(archive.files)
            contents = archive.header['user_data_header']['content']
            header = versions.latest().decode_replay_header(contents)
            baseBuild = header['m_version']['m_baseBuild']

            try:
                protocol = versions.build(baseBuild)
                analyze_sentiments(archive, protocol)
            except ImportError as err:
                print(err.args)

        if isLast:
            isLastPage = True

        curPage += 1

        browser.get(curMapLink + str(curPage))
        sleep(1)
        nextButton = browser.find_element_by_xpath(
            '//*[@id="matches"]/div[3]/div[3]/unpaginate/div/ul/li[3]').get_attribute("style")

        if 'none' in nextButton:
            isLast = True

        # curRace = curRace[2: len(curRace) - 1]
    archive = None
    browser.close()
    new_name = str(uuid4())
    rename(getcwd() + '/PlayerMatch/TempReplays/', getcwd() + '/PlayerMatch/' + new_name)
    rmtree(getcwd() + '/PlayerMatch/' + new_name)
    mkdir(getcwd() + '/PlayerMatch/TempReplays')


