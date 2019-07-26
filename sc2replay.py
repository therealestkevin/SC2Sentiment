from s2protocol import versions
import mpyq

archive = mpyq.MPQArchive('/home/realestkevin/ggtracker_265764.SC2Replay')

print(archive.files)

contents = archive.header['user_data_header']['content']
header = versions.latest().decode_replay_header(contents)
baseBuild = header['m_version']['m_baseBuild']
protocol = versions.build(baseBuild)

contents = archive.read_file('replay.details')

gameDetails = protocol.decode_replay_details(contents)

sentimentTotals = [0 for i in range(len(gameDetails['m_playerList']))]

for stuff in gameDetails:
    print(stuff)
contents = archive.read_file('replay.message.events')

messageEvents = protocol.decode_replay_message_events(contents)
listmessages = []

for event in messageEvents:
    if event['_event'] == 'NNet.Game.SChatMessage':
        listmessages.append(event['m_string'])

print(listmessages)



