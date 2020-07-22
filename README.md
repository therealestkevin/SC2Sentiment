# SC2Sentiment
**www.sc2sentiment.me**


Django webapp conducting mass sentiment analysis of Starcarft 2 replay in-game messages to determine overall attitudes of the three main factions players can choose (Terran, Zerg, Protoss). Sentiment analysis in the context of the informal in-game chat is done through VADER Sentiment analysis, which is tuned for social media sentiments. 

Tens of thousands of replays have been sourced from the Starcraft replay repository www.gggreplays.com using a Selenium Webcrawler to build up a proper representation of the Starcraft playerbase. The website itself also acts as a crowdsourcing point for visitors to upload their own replays to be analyzed and incorporated into the database of sentiment analyzed replays. The Starcraft replays are parsed with the official Blizzard S2Protocol decoding library and asynchronously processed to prevent overly lengthy loading times on webpages.

Frameworks/Tools: Django, Selenium, Celery, jQuery Ajax, Bootstrap
