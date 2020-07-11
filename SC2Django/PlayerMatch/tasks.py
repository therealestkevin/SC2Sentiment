from celery import shared_task
from celery.utils.log import get_task_logger
from .models import PlayerMatchSingular
from s2protocol import versions
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import mpyq
from lxml import html

logger = get_task_logger(__name__)

emojiTranslations = {"(happy)": "😁", ":D": "😂", "(rofl)": "😂", ":(": "😢",
                     "(sad)": "😢", ":@": "😠", "(angry)": "😠", ":O": "😲",
                     "(surprised)": "😲", ";P": "😜", "(silly)": "😜",
                     ":|": "😐", "(speechless)": "😐", ":]": "😍", "(inlove)": "😍",
                     "B-}": "😎", "(cool)": "😎", ":S": "😨", "(scared)": "😨",
                     "|-]": "😴", "(sleepy)": "😴", "(kiss)": "😘", "(devil)": "😈"
                     }


def strip_html(s):
    return str(html.fromstring(s).text_content())


@shared_task()
def process_uploaded_replay(replayFile):
    print("Task Running...")

    archive = mpyq.MPQArchive(replayFile)

    contents = archive.header['user_data_header']['content']
    header = versions.latest().decode_replay_header(contents)
    baseBuild = header['m_version']['m_baseBuild']

    try:
        protocol = versions.build(baseBuild)

        contents = archive.read_file('replay.details')

        gameDetails = protocol.decode_replay_details(contents)
        # in the future, add functionality to check for duplicate replays
        # compare up to the database, only save the gamedetails in the database
        # gamedetails contain specific time and game equivalencies that are
        # completely unique, just a call simple contains on the DB
        sentimentTotals = [0 for i_ in range(len(gameDetails['m_playerList']) * 2)]

        contents = archive.read_file('replay.message.events')

        messageEvents = protocol.decode_replay_message_events(contents)
        listmessages = []
        listMessageSentiments = []
        for i in range(len(gameDetails['m_playerList'])):
            listmessages.append([])
            listMessageSentiments.append([])

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

        for i in range(len(gameDetails['m_playerList'])):
            curPlayer = playerList[i]
            curPlayerName = strip_html(curPlayer['m_name'].decode("utf-8"))
            PlayerMatchSingular.objects.create(username=curPlayerName,
                                compoundSentiment=compoundUserSentiments[i], messages=listmessages[i],
                                messageSentiments=listMessageSentiments[i])
    except ImportError as err:
        print(err.args)
