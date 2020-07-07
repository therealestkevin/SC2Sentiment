from s2protocol import versions
import mpyq
from selenium import webdriver
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from os import getcwd, listdir
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def enable_download_in_headless_chrome(driver, download_dir):
    # add missing support for chrome "send_command"  to selenium webdriver
    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
    command_result = driver.execute("send_command", params)


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
  "download.default_directory": "H:\Code\SC2Sentiment\SC2Logic\TempReplays",
  "download.prompt_for_download": False,
  "download.directory_upgrade": True,
  "safebrowsing_for_trusted_sources_enabled": False,
  "safebrowsing.enabled": False
})


validMapsFile = open("ValidMapRotation.txt", "r")

validMapsList = validMapsFile.readlines()

curMapLink = ""
#ChromeDriverManager().install()
browser = webdriver.Chrome('H:/chromedriver_win32/chromedriver.exe', options=options)

enable_download_in_headless_chrome(browser, "H:\Code\SC2Sentiment\SC2Logic\TempReplays")

for k in range(2, 4):
    curMapName = validMapsList[k]
    curMapName = curMapName.replace(" ", "%20")

    curMapLink = "https://gggreplays.com/matches#?map_name=" + curMapName + "&page="



#testBaseAcidPlant = "https://gggreplays.com/matches#?map_name=Acid%20Plant%20LE&page="

    for j in range(1, 3):

        fileNameList = []
        browser.get(curMapLink+str(j))
        sleep(1)
        for i in range(2, 12):
            DateElement = WebDriverWait(browser, 5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="matches"]/div[3]/div[3]/table/tbody/tr[{}]/td[20]'.format(i))))
            DateText = browser.find_element_by_xpath('//*[@id="matches"]/div[3]/div[3]/table/tbody/tr[{}]/td[20]'.format(i)).text
            PlayerText = browser.find_element_by_xpath('//*[@id="matches"]/div[3]/div[3]/table/tbody/tr[{}]/td[6]'.format(i)).text

            if "A.I." not in PlayerText and PlayerText:

                if "year" in DateText or "11 months" in DateText or "10 months" in DateText:
                    print(PlayerText)
                    browser.find_element_by_xpath('//*[@id="matches"]/div[3]/div[3]/table/tbody/tr[{}]'.format(i)).click()
                    before = listdir('H:\Code\SC2Sentiment\SC2Logic\TempReplays')

                    #browser.find_element_by_xpath('//*[@id="heading"]/div[1]/div[3]/a/span').click()
                    downURL = browser.current_url+"/replay"
                    browser.get(downURL)
                    sleep(5)
                    after = listdir('H:\Code\SC2Sentiment\SC2Logic\TempReplays')

                    change = set(after) - set(before)

                    file_name = change.pop()
                    fileNameList.append(file_name)

                    browser.get(curMapLink+str(j))

        print(fileNameList)

        for fileName in fileNameList:
            archive = mpyq.MPQArchive("H:\Code\SC2Sentiment\SC2Logic\TempReplays\\" + fileName)
            print(archive.files)

            contents = archive.header['user_data_header']['content']
            header = versions.latest().decode_replay_header(contents)
            baseBuild = header['m_version']['m_baseBuild']
            protocol = versions.build(baseBuild)

            # contents = archive.read_file('replay.initData')

            # lobbyDetails = protocol.decode_replay_initdata(contents)
            contents = archive.read_file('replay.details')

            gameDetails = protocol.decode_replay_details(contents)

            sentimentTotals = [0 for i in range(len(gameDetails['m_playerList']) * 2)]

            contents = archive.read_file('replay.message.events')

            messageEvents = protocol.decode_replay_message_events(contents)
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
            for i in range(1, len(sentimentTotals), 2):
                if sentimentTotals[i - 1] > 0:
                    compoundUserSentiments.append(sentimentTotals[i] / sentimentTotals[i - 1])
            print(listmessages)
            print(sentimentTotals)
            print(compoundUserSentiments)

            # print(analyzer.polarity_scores("😈"))
            players = gameDetails['m_playerList']
            for i in range(len(compoundUserSentiments)):
                curRace = str(players[i]['m_race'])
                if "Zerg" in curRace:
                    curRace = "Zerg"
                    races[curRace][0] += 1
                    races[curRace][1] += compoundUserSentiments[i]
                elif "Terran" in curRace:
                    curRace = "Terran"
                    races[curRace][0] += 1
                    races[curRace][1] += compoundUserSentiments[i]
                elif "Protoss" in curRace:
                    curRace = "Protoss"
                    races[curRace][0] += 1
                    races[curRace][1] += compoundUserSentiments[i]

                #curRace = curRace[2: len(curRace) - 1]
print(races)

