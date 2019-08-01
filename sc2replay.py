from s2protocol import versions
import mpyq
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

races = {"Terran": [0, 0], "Zerg": [0, 0], "Protoss": [0, 0]}
emojiTranslations = {"(happy)": "😁", ":D": "😂", "(rofl)": "😂", ":(": "😢",
                     "(sad)": "😢", ":@": "😠", "(angry)": "😠", ":O": "😲",
                     "(surprised)": "😲", ";P": "😜", "(silly)": "😜",
                     ":|": "😐", "(speechless)": "😐", ":]": "😍", "(inlove)": "😍",
                     "B-}": "😎", "(cool)": "😎", ":S": "😨", "(scared)": "😨",
                     "|-]": "😴", "(sleepy)": "😴", "(kiss)": "😘", "(devil)": "😈"
                     }
archive = mpyq.MPQArchive('/home/realestkevin/Replays/ggtracker_272965.SC2Replay')

print(archive.files)

contents = archive.header['user_data_header']['content']
header = versions.latest().decode_replay_header(contents)
baseBuild = header['m_version']['m_baseBuild']
protocol = versions.build(baseBuild)
contents = archive.read_file('replay.initData')

lobbyDetails = protocol.decode_replay_initdata(contents)
contents = archive.read_file('replay.details')

gameDetails = protocol.decode_replay_details(contents)

sentimentTotals = [0 for i in range(len(gameDetails['m_playerList']) * 2)]

for stuff in gameDetails:
    print(stuff)
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
    if sentimentTotals[i-1] > 0:
        compoundUserSentiments.append(sentimentTotals[i]/sentimentTotals[i-1])
print(listmessages)
print(sentimentTotals)
print(compoundUserSentiments)

# print(analyzer.polarity_scores("😈"))
players = gameDetails['m_playerList']
for i in range(len(compoundUserSentiments)):
    curRace = str(players[i]['m_race'])

    curRace = curRace[2: len(curRace) - 1]
    races[curRace][0] += 1
    races[curRace][1] += compoundUserSentiments[i]

print(races)