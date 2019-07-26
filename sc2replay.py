from s2protocol import versions
import mpyq

archive = mpyq.MPQArchive('/home/realestkevin/ggtracker_271653.SC2Replay')

print(archive.files)

contents = archive.header['user_data_header']['content']
header = versions.latest().decode_replay_header(contents)
baseBuild = header['m_version']['m_baseBuild']
protocol = versions.build(baseBuild)

contents = archive.read_file('replay.message.events')

messageEvents = protocol.decode_replay_message_events(contents)
listmessages = []

for event in messageEvents:
    listmessages.append(event)
    print(str(event))
