import requests
import sys
import json
import math
import pandas as pd
import plotly.express as px

#get list of pokemon and their speed stats
f = open('pokedex.ts', 'r').read()


def speedFormula(Base, IV, EV, Nature, Level = 50):
	value = math.floor((math.floor(((2*Base+IV+math.floor(EV/4))*Level)/100)+5)*Nature)
	return value

speedDict = {}
for textbox in f.split('name: "')[1:]:
	monName = textbox.split('"')[0]
	monSpeed = int(textbox.split(', spe: ')[1].split('}')[0])
	speedDict[monName] = monSpeed

#natures:
speedBoostingNatures = ['Timid', 'Hasty', 'Jolly' ,'Naive']
speedDroppingNatures = ['Brave', 'Relaxed, "Quiet', "Sassy"]


url = '''https://www.smogon.com/stats/2023-09-DLC1/chaos/gen9vgc2023regulatione-'''
url1760 = url + "1760.json"
url1630 = url + "1630.json"
url1500 = url + "1500.json"
url0 = url + "0.json"



r = requests.get(url1500).json()['data']


#Dictionary of Speed Stats, key is number
#value is [overall pct, {pokemon, cumulative pct}]
SpeedStatDict = {}
mon_usage_dict = {}

for mon in r:
	pokemon = r[mon]
	baseSpeed = speedDict[mon]
	for spread in pokemon['Spreads']:
		usage = pokemon['Spreads'][spread]
		if mon not in mon_usage_dict:
			mon_usage_dict[mon] = 0
		mon_usage_dict[mon] += usage
		nature = spread.split(':')[0]
		natureMultiplier = 1
		if nature in speedDroppingNatures:
			natureMultiplier = .9
		if nature in speedBoostingNatures:
			natureMultiplier= 1.1
		speedEVs = int(spread.split('/')[-1])
		IV = 31
		if speedEVs == 0 and natureMultiplier == .9:
			IV = 0
		speedStat = speedFormula(baseSpeed, IV, speedEVs, natureMultiplier)
		if speedStat not in SpeedStatDict:
			SpeedStatDict[speedStat] = [usage, {mon:usage}]
		else:
			SpeedStatDict[speedStat][0] =SpeedStatDict[speedStat][0] + usage
			if mon in SpeedStatDict[speedStat][1]:
				SpeedStatDict[speedStat][1][mon] = SpeedStatDict[speedStat][1][mon] + usage
			else:
				SpeedStatDict[speedStat][1][mon] = usage


usage_total = 0
for k in SpeedStatDict:
    usage_total += SpeedStatDict[k][0]

df_list_of_lists = []
for k in SpeedStatDict:
	other_total = 0
	for mon in SpeedStatDict[k][1]:
		usage = SpeedStatDict[k][1][mon]
		usage2 = 600*usage/usage_total
		monOverallUsage = mon_usage_dict[mon]
		if monOverallUsage*600/usage_total < 1.5:
			other_total += usage2
		else:
			df_list_of_lists.append([k, usage2, mon])
	df_list_of_lists.append([k, other_total, "other"])

df = pd.DataFrame(df_list_of_lists, columns = ['Speed', 'Usage', "Pokemon"])

title_name = '1500 Speed Tiers Sep 2023'

fig = px.bar(df, x="Speed", y="Usage", color="Pokemon",
            hover_data=['Pokemon'], barmode = 'stack', title=title_name)
fig.update_layout(xaxis_range=[45,220])
#fig.show()

fig.write_html("/Users/adisubra/Documents/PokemonTools/Rscripts/Interactive_Speed_Tiers_" +title_name + "_Sep_2023.html")



