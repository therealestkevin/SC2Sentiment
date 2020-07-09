from s2protocol import versions
import mpyq
from selenium import webdriver
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from selenium.webdriver.chrome.options import Options
from time import sleep
from os import getcwd, listdir, mkdir, rename
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from shutil import rmtree
from uuid import uuid4


def enable_download_in_headless_chrome(driver, download_dir):
    # add missing support for chrome "send_command"  to selenium webdriver
    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
    command_result = driver.execute("send_command", params)


def analyze_sentiments(archive_, protocol_, races_):
    contents_ = archive_.read_file('replay.details')

    gameDetails_ = protocol_.decode_replay_details(contents_)
    #in the future, add functionality to check for duplicate replays
    #compare up to the database, only save the gamedetails in the database
    #gamedetails contain specific time and game equivalencies that are
    #completely unique, just a call simple contains on the DB

    sentimentTotals = [0 for i_ in range(len(gameDetails_['m_playerList']) * 2)]

    contents_ = archive_.read_file('replay.message.events')

    messageEvents = protocol_.decode_replay_message_events(contents_)
    listmessages = []
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
            sentimentTotals[sender * 2] += 1
            sentimentTotals[(sender * 2) + 1] += compoundSentiment
            listmessages.append(curMessage)
            print("CurrentUser: " + str(sender) + "Sentiment: " + str(compoundSentiment))

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

    print(listmessages)
    print(sentimentTotals)
    print(compoundUserSentiments)

    players = gameDetails_['m_playerList']
    for i_ in range(len(compoundUserSentiments)):
        curRace = str(players[i_]['m_race'])
        if "Zerg" in curRace:
            curRace = "Zerg"
            races_[curRace][0] += 1
            races_[curRace][1] += compoundUserSentiments[i_]
        elif "Terran" in curRace:
            curRace = "Terran"
            races_[curRace][0] += 1
            races_[curRace][1] += compoundUserSentiments[i_]
        elif "Protoss" in curRace:
            curRace = "Protoss"
            races_[curRace][0] += 1
            races_[curRace][1] += compoundUserSentiments[i_]


races = {"Terran": [0, 0], "Zerg": [0, 0], "Protoss": [0, 0]}
emojiTranslations = {"(happy)": "😁", ":D": "😂", "(rofl)": "😂", ":(": "😢",
                     "(sad)": "😢", ":@": "😠", "(angry)": "😠", ":O": "😲",
                     "(surprised)": "😲", ";P": "😜", "(silly)": "😜",
                     ":|": "😐", "(speechless)": "😐", ":]": "😍", "(inlove)": "😍",
                     "B-}": "😎", "(cool)": "😎", ":S": "😨", "(scared)": "😨",
                     "|-]": "😴", "(sleepy)": "😴", "(kiss)": "😘", "(devil)": "😈"
                     }
options = Options()

options.add_argument("--headless")

options.add_experimental_option("prefs", {
    "download.default_directory": getcwd() + '\\TempReplays',
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing_for_trusted_sources_enabled": False,
    "safebrowsing.enabled": False
})

validMapsFile = open("ValidMapRotation.txt", "r")

validMapsList = validMapsFile.readlines()

curMapLink = ""
browser = webdriver.Chrome('H:\\chromedriver_win32\\chromedriver.exe', options=options)

enable_download_in_headless_chrome(browser, getcwd() + '\\TempReplays')

for k in range(2, 4):
    curMapName = validMapsList[k]
    curMapName = curMapName.replace(" ", "%20")

    curMapLink = "https://gggreplays.com/matches#?map_name=" + curMapName + "&page="

    for j in range(1, 3):

        fileNameList = []
        browser.get(curMapLink + str(j))
        sleep(1)
        for i in range(2, 12):
            DateElement = WebDriverWait(browser, 5).until(EC.visibility_of_element_located((By.XPATH,
                '//*[@id="matches"]/div[3]/div[3]/table/tbody/tr[{}]/td[20]'.format(i))))
            DateText = browser.find_element_by_xpath(
                '//*[@id="matches"]/div[3]/div[3]/table/tbody/tr[{}]/td[20]'.format(i)).text
            PlayerText = browser.find_element_by_xpath(
                '//*[@id="matches"]/div[3]/div[3]/table/tbody/tr[{}]/td[6]'.format(i)).text

            if "A.I." not in PlayerText and PlayerText:

                if "year" in DateText or "11 months" in DateText or "10 months" in DateText:
                    print(PlayerText)
                    matchLink = browser.find_element_by_xpath(
                        '//*[@id="matches"]/div[3]/div[3]/table/tbody/tr[{}]/td[2]/a'
                        .format(i)).get_attribute('href')
                    print(matchLink)

                    # browser.find_element_by_xpath('//*[@id="matches"]/div[3]/div[3]/table/tbody/tr[{}]'.format(i)).click()
                    before = listdir(getcwd() + '\\TempReplays')

                    downURL = matchLink + "/replay"
                    browser.get(downURL)
                    #sleep(2)
                    after = listdir(getcwd() + '\\TempReplays')
                    change = set(after) - set(before)
                    file_name = ""
                    loopCount = 0
                    while loopCount < 16 or len(change) == 0:
                        sleep(0.25)
                        after = listdir(getcwd() + '\\TempReplays')
                        change = set(after) - set(before)
                        if len(change) > 0:
                            file_name = change.pop()
                            if 'crdownload' not in file_name:
                                break
                        loopCount += 1

                    if loopCount == 16:
                        continue

                    fileNameList.append(file_name)

                    # browser.get(curMapLink+str(j))

        print(fileNameList)

        for fileName in fileNameList:
            archive = mpyq.MPQArchive(getcwd() + '\\TempReplays\\' + fileName)
            print(archive.files)
            contents = archive.header['user_data_header']['content']
            header = versions.latest().decode_replay_header(contents)
            baseBuild = header['m_version']['m_baseBuild']

            try:
                protocol = versions.build(baseBuild)
                analyze_sentiments(archive, protocol, races)
            except ImportError as err:
                print(err.args)

            # contents = archive.read_file('replay.initData')
            # lobbyDetails = protocol.decode_replay_initdata(contents)


                # curRace = curRace[2: len(curRace) - 1]
archive = None
browser.close()
new_name = str(uuid4())
rename(getcwd() + '\\TempReplays', new_name)
rmtree(getcwd() + '\\' + new_name)
mkdir(getcwd() + '\\TempReplays')
print(races)
