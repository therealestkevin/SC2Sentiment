# SC2Sentiment
### **<a href = "https://www.sc2sentiment.live/">sc2sentiment.live</a>**

## Overview


SC2Sentiment is a Django webapp conducting mass sentiment analysis of Starcarft 2 replay in-game messages to determine overall attitudes of the three main factions players can choose to play as (Terran, Zerg, Protoss). 

The Terran, Zerg, and Protoss factions vary drastically in their play styles. As a result, the type of players that are attracted to each faction have marked differences. This project strives to determine if there are any quantitative differences between these players and their factions through natural language processing

## Details

- Sentiment analysis in the context of the informal in-game chat is done through VADER Sentiment analysis, which is tuned for social media sentiments. 

- Tens of thousands of replays have been sourced from the Starcraft replay repository https://gggreplays.com/landing_tour using a Selenium Webcrawler to build up a proper representation of the Starcraft playerbase. 

- The website itself also acts as a crowdsourcing point for visitors to upload their own replays to be analyzed and incorporated into the database of sentiment analyzed replays. 

- The Starcraft replays are parsed with the official Blizzard S2Protocol decoding library and asynchronously processed to prevent overly lengthy loading times on webpages.

