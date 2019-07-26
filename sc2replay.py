from s2protocol import versions
import mpyq
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


emojiTranslations = {"(ha🤔ppy)": "😁", ":D": "😂", "(rofl)": "😂", ":(": "😢",
                     "(sad)": "😢", ":@": "😠", "(angry)": "😠", ":O": "😲",
                     "(surprised)": "😲", ";P": "😜", "(silly)": "😜",
                     ":|": "😐", "(speechless)": "😐", ":]": "😍", "(inlove)": "😍",
                     "B-}": "😎", "(cool)": "😎", ":S": "😨", "(scared)": "😨",
                     "|-]": "😴", "(sleepy)": "😴", "(kiss)": "😘", "(devil)": "😈"
                     }
archive = mpyq.MPQArchive('/home/realestkevin/ggtracker_265764.SC2Replay')

print(archive.files)

contents = archive.header['user_data_header']['content']
header = versions.latest().decode_replay_header(contents)
baseBuild = header['m_version']['m_baseBuild']
protocol = versions.build(baseBuild)

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
    compoundUserSentiments.append(sentimentTotals[i]/sentimentTotals[i-1])
print(listmessages)
print(sentimentTotals)
print(compoundUserSentiments)

print(analyzer.polarity_scores(""))
