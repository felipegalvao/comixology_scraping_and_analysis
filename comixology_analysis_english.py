# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 17:25:27 2016

@author: Felipe
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

comixology_df = pd.read_csv("comixology_comics_dataset_19.04.2016.csv", 
                            encoding = "ISO-8859-1")

# Create price per page column
comixology_df['Price_per_page'] = pd.Series(comixology_df['Original_price'] / 
                                            comixology_df['Page Count'], 
                                            index=comixology_df.index)
                                            
# Define price_per_page as NaN for comics with no information about page count
comixology_df.Price_per_page[comixology_df['Price_per_page'] == np.inf] = np.nan

# Extract the year of release for print version
print_dates = []
for index, row in comixology_df.iterrows():
    if type(comixology_df.ix[index]['Print Release Date']) == float:
        row_year = np.nan
    else:        
        row_year = int(comixology_df.ix[index]['Print Release Date'].split()[2])
        if row_year > 2016:
            row_year = np.nan
    print_dates.append(row_year)

comixology_df['Print_Release_Year'] = pd.Series(print_dates, 
                                                index=comixology_df.index)
                                                
# Calculate some average values of the site
average_price = np.nanmean(comixology_df['Original_price'])
average_page_count = np.nanmean(comixology_df['Page Count'])
average_rating = np.nanmean(comixology_df['Rating'])
average_rating_quantity = np.nanmean(comixology_df['Ratings_Quantity'])
average_price_per_page = np.nanmean(comixology_df['Price_per_page'])

print("Average Price: " + str(average_price))
print("Average Page Count: " + str(average_page_count))
print("Average Rating: " + str(average_rating))
print("Average Ratings Quantity: " + 
      str(average_rating_quantity))
print("Average Price Per Page: " + str(average_price_per_page))

# List comics with 5 stars rating that have at least 20 ratings
comics_with_5_stars = comixology_df[comixology_df.Rating == 5]
comics_with_5_stars = comics_with_5_stars[comics_with_5_stars.Ratings_Quantity 
                                          > 20]
# Print comics sorted by price per page
print(comics_with_5_stars[['Name','Publisher','Price_per_page']].
      sort_values(by='Price_per_page')) 
      
# Filter the original DataFrame for comics with more than 5 ratings
comics_more_than_5_ratings = comixology_df[comixology_df.Ratings_Quantity > 5]

# Create pivot table with average rating by publisher
publishers_avg_rating = pd.pivot_table(comics_more_than_5_ratings, 
                                       values=['Rating'], 
                                       index=['Publisher'], 
                                       aggfunc=[np.mean, np.count_nonzero])

# Filter for any Publisher that has more than 20 comics rated
main_pub_avg_rating = publishers_avg_rating[publishers_avg_rating.
                                            count_nonzero.Rating > 20]
main_pub_avg_rating = main_pub_avg_rating.sort_values(by=('mean','Rating'), 
                                                      ascending=False)
print(main_pub_avg_rating)

# Create chart with average ratings for the Publishers
plt.figure(figsize=(10, 6))
y_axis = main_pub_avg_rating['mean']['Rating']
x_axis = range(len(y_axis))

plt.bar(x_axis, y_axis)
plt.xticks(x_axis, tuple(main_pub_avg_rating.index),rotation=90)
plt.show()

# Filter for Publishers that have more than 300 comics rated
big_pub_avg_rating = publishers_avg_rating[publishers_avg_rating.
                                           count_nonzero.Rating > 300]
big_pub_avg_rating = big_pub_avg_rating.sort_values(by=('mean','Rating'), 
                                                    ascending=False)
print(big_pub_avg_rating)

# Create chart with average ratings for Publishers with more than 300 comics 
# rated
plt.figure(figsize=(10, 6))
y_axis = big_pub_avg_rating['mean']['Rating']
x_axis = np.arange(len(y_axis))

plt.bar(x_axis, y_axis)
plt.xticks(x_axis+0.5, tuple(big_pub_avg_rating.index), rotation=90)
plt.show()

# Create pivot table with Rating by Age Rating
rating_by_age = pd.pivot_table(comics_more_than_5_ratings, 
                               values=['Rating'], 
                               index=['Age Rating'], 
                               aggfunc=[np.mean, np.count_nonzero])
                               
print(rating_by_age)

# Bar Chart with rating by age rating
plt.figure(figsize=(10, 6))
y_axis = rating_by_age['mean']['Rating']
x_axis = np.arange(len(y_axis))

plt.bar(x_axis, y_axis)
plt.xticks(x_axis+0.25, tuple(rating_by_age.index), rotation=45)
plt.show()

# Create pivot table with print releases per year
print_releases_per_year = pd.pivot_table(comixology_df, 
                                         values=['Name'], 
                                         index=['Print_Release_Year'], 
                                         aggfunc=[np.count_nonzero])
print_years = []
for index, row in print_releases_per_year.iterrows():    
    print_year = int(index)
    print_years.append(print_year)
print_releases_per_year.index = print_years
print(print_releases_per_year)

# Create chart with print releases per year
y_axis = print_releases_per_year['count_nonzero']['Name']
x_axis = print_releases_per_year['count_nonzero']['Name'].index
plt.figure(figsize=(10, 6))
plt.plot(x_axis, y_axis)
plt.show()

# Sort the DataFrame by ratings quantity and show Name, Publisher and quantity
comics_by_ratings_quantity = comixology_df[['Name','Publisher',
                                            'Ratings_Quantity']].sort_values(
                                            by='Ratings_Quantity', 
                                            ascending=False)
print(comics_by_ratings_quantity.head(30))

# Create chart with the previously sorted comics
plt.figure(figsize=(10, 6))
y_axis = comics_by_ratings_quantity.head(30)['Ratings_Quantity']
x_axis = np.arange(len(y_axis))

plt.bar(x_axis, y_axis)
plt.xticks(x_axis+0.5, tuple(comics_by_ratings_quantity.head(30)['Name']), 
           rotation=90)
plt.show()

# Filter the DataFrame for comics from Marvel or DC Comics
marvel_dc_comics = comixology_df[(comixology_df.Publisher == 'Marvel') | 
                                 (comixology_df.Publisher == 'DC Comics')]
 
# Create pivot table with Primeiro, alguns valores médios de cada uma                                
marvel_dc_pivot_averages = pd.pivot_table(marvel_dc_comics, 
                               values=['Rating','Original_price','Page Count',
                                       'Price_per_page'], 
                               index=['Publisher'], 
                               aggfunc=[np.mean])
print(marvel_dc_pivot_averages)

# Charts for average values for Marvel and DC
plt.figure(1,figsize=(10, 6))

plt.subplot(221) # Mean original price
y_axis = marvel_dc_pivot_averages['mean']['Original_price']
x_axis = np.arange(len(marvel_dc_pivot_averages['mean']['Original_price']))
plt.bar(x_axis, y_axis)
plt.xticks(x_axis+0.4, 
           tuple(marvel_dc_pivot_averages['mean']['Original_price'].index))
plt.title('Mean Original Price')
plt.tight_layout()

plt.subplot(222) # Mean page count
y_axis = marvel_dc_pivot_averages['mean']['Page Count']
x_axis = np.arange(len(marvel_dc_pivot_averages['mean']['Page Count']))
plt.bar(x_axis, y_axis)
plt.xticks(x_axis+0.4, 
           tuple(marvel_dc_pivot_averages['mean']['Page Count'].index))
plt.title('Mean Page Count')
plt.tight_layout()

plt.subplot(223) # Mean Price Per Page
y_axis = marvel_dc_pivot_averages['mean']['Price_per_page']
x_axis = np.arange(len(marvel_dc_pivot_averages['mean']['Price_per_page']))
plt.bar(x_axis, y_axis)
plt.xticks(x_axis+0.4, 
           tuple(marvel_dc_pivot_averages['mean']['Price_per_page'].index))
plt.title('Mean Price Per Page')
plt.tight_layout()

plt.subplot(224) # Mean Comic Rating
y_axis = marvel_dc_pivot_averages['mean']['Rating']
x_axis = np.arange(len(marvel_dc_pivot_averages['mean']['Rating']))
plt.bar(x_axis, y_axis)
plt.xticks(x_axis+0.4, 
           tuple(marvel_dc_pivot_averages['mean']['Rating'].index))
plt.title('Mean Comic Rating')
plt.tight_layout()

plt.show()

# Calculate total number of comics for each Publisher, proportion of comics 
# with rating 4 or bigger and proportion of comics with rating 2 or smaller
marvel_total = len(marvel_dc_comics[marvel_dc_comics['Publisher'] == 'Marvel'])
marvel_4_or_5 = len(marvel_dc_comics[(marvel_dc_comics['Publisher'] == 'Marvel')
                                     & (marvel_dc_comics['Rating'] >= 4)])
marvel_proportion_4_or_5 = marvel_4_or_5 / marvel_total
marvel_1_or_2 = len(marvel_dc_comics[(marvel_dc_comics['Publisher'] == 'Marvel') 
                                     & (marvel_dc_comics['Rating'] <= 2)])
marvel_proportion_1_or_2 = marvel_1_or_2 / marvel_total

dc_total = len(marvel_dc_comics[marvel_dc_comics['Publisher'] == 'DC Comics'])
dc_4_or_5 = len(marvel_dc_comics[(marvel_dc_comics['Publisher'] == 'DC Comics')
                                 & (marvel_dc_comics['Rating'] >= 4)])
dc_proportion_4_or_5 = dc_4_or_5 / dc_total
dc_1_or_2 = len(marvel_dc_comics[(marvel_dc_comics['Publisher'] == 'DC Comics') 
                                 & (marvel_dc_comics['Rating'] <= 2)])
dc_proportion_1_or_2 = dc_1_or_2 / dc_total

print("\n")
print("Marvel's Total Comics: " + str(marvel_total))
print("Marvel's comics with rating 4 or bigger: " + 
      str(marvel_4_or_5))
print("Proportion of Marvel's comics with rating 4 or bigger: " + 
      str("{0:.2f}%".format(marvel_proportion_4_or_5 * 100)))
print("Marvel's comics with rating 2 or smaller: " + 
      str(marvel_1_or_2))
print("Proportion of Marvel's comics with rating 2 or smaller: " + 
      str("{0:.2f}%".format(marvel_proportion_1_or_2 * 100)))
print("\n")
print("DC's Total Comics: " + str(dc_total))
print("DC's comics with rating 4 or bigger: " + 
      str(dc_4_or_5))
print("Proportion of DC's comics with rating 4 or bigger: " + 
      str("{0:.2f}%".format(dc_proportion_4_or_5 * 100)))
print("DC's comics with rating 2 or smaller: " + 
      str(dc_1_or_2))
print("Proportion of DC's comis with rating 2 or smaller: " + 
      str("{0:.2f}%".format(dc_proportion_1_or_2 * 100)))
print("\n")

# Create charts with total comics and previously calculated proportions for 
# Marvel and DC
plt.figure(2,figsize=(10, 6))

plt.subplot(221) # Total comics for Marvel and DC
y_axis = [dc_total, marvel_total]
x_axis = np.arange(len(y_axis))
plt.bar(x_axis, y_axis)
plt.xticks(x_axis+0.4, ('DC Comics','Marvel'))
plt.title('Total Comics')
plt.tight_layout()

plt.subplot(222) # Proportion of comics with rating 4 or 5
y_axis = [dc_proportion_4_or_5 * 100, marvel_proportion_4_or_5 * 100]
x_axis = np.arange(len(y_axis))
plt.bar(x_axis, y_axis)
plt.xticks(x_axis+0.4, ('DC Comics','Marvel'))
plt.title('Proportion of comics with rating 4 or 5')
plt.tight_layout()

plt.subplot(223) # Proportion of comics with rating 1 or 2
y_axis = [dc_proportion_1_or_2 * 100, marvel_proportion_1_or_2 * 100]
x_axis = np.arange(len(y_axis))
plt.bar(x_axis, y_axis)
plt.xticks(x_axis+0.4, ('DC Comics','Marvel'))
plt.title('Proportion of comics with rating 1 or 2')
plt.tight_layout()

plt.show()

# Create Pivot Table with quantity of ratings of each Publisher
marvel_dc_pivot_sums = pd.pivot_table(marvel_dc_comics, 
                               values=['Ratings_Quantity'], 
                               index=['Publisher'], 
                               aggfunc=[np.sum])
print(marvel_dc_pivot_sums)

# Define list of characters and teams of DC and Marvel
main_dc_characters = ['Superman','Batman','Aquaman','Wonder Woman', 'Flash', 
                      'Robin','Arrow', 'Batgirl', 'Bane', 'Harley Queen', 
                      'Poison Ivy', 'Joker','Firestorm','Vixen',
                      'Martian Manhunter','Zod','Penguin','Lex Luthor',
                      'Green Lantern','Supergirl','Atom','Cyborg','Hawkgirl',
                      'Starfire','Jonah Hex','Booster Gold','Black Canary',
                      'Shazam','Catwoman','Nightwing','Zatanna','Hawkman',
                      'Power Girl','Rorschach','Doctor Manhattan',
                      'Blue Beetle','Batwoman','Darkseid','Vandal Savage', 
                      "Ra's Al Ghul",'Riddler','Reverse Flash','Black Adam',
                      'Deathstroke','Brainiac','Sinestro','Two-Face']
                      
main_marvel_characters = ['Spider-Man','Captain Marvel','Hulk','Thor',
                          'Iron Man','Luke Cage','Black Widow','Daredevil',
                          'Captain America','Jessica Jones','Ghost Rider',
                          'Spider-Woman','Silver Surfer','Beast','Thing',
                          'Kitty Pride','Doctor Strange','Black Panther',
                          'Invisible Woman','Nick Fury','Storm','Professor X',
                          'Cyclops','Jean Grey','Wolverine','Scarlet Witch',
                          'Gambit','Rogue','X-23','Iceman','She-Hulk',
                          'Iron Fist','Hawkeye','Quicksilver','Vision',
                          'Ant-Man','Cable','Bishop','Colossus','Deadpool',
                          'Human Torch','Mr. Fantastic','Nightcrawler','Nova',
                          'Psylocke','Punisher','Rocket Raccoon','Groot',
                          'Star-Lord','War Machine','Gamora','Drax','Venom',
                          'Carnage','Octopus','Green Goblin','Abomination',
                          'Enchantress','Sentinel','Viper','Lady Deathstrike',
                          'Annihilus','Ultron','Galactus','Kang','Bullseye',
                          'Juggernaut','Sabretooth','Mystique','Kingpin',
                          'Apocalypse','Thanos','Dark Phoenix','Loki',
                          'Red Skull','Magneto','Doctor Doom','Ronan']
                          
dc_teams = ['Justice League','Teen Titans','Justice Society','Lantern Corps',
            'Legion of Super-Heroes','All-Star Squadron','Suicide Squad',
            'Birds of Prey','Gen13', 'The League of Extraordinary Gentlemen',
            'Watchmen']
            
marvel_teams = ['X-Men','Avengers','Fantastic Four','Asgardian Gods','Skrulls',
                'S.H.I.E.L.D.','Inhumans','A.I.M.','X-Factor','X-Force',
                'Defenders','New Mutants','Brotherhood of Evil Mutants',
                'Thunderbolts', 'Alpha Flight','Guardians of the Galaxy',
                'Nova Corps','Illuminati']
                
# Create empty list and dict to hold character info
character_row = {}
characters_dicts = []

for character in main_dc_characters:
    character_df = comixology_df[(comixology_df['Name'].str.contains(character)) & 
                                 (comixology_df['Publisher'] == 'DC Comics')]
    character_row['Character_Name'] = character
    character_row['Quantity_of_comics'] = len(character_df)
    character_row['Average_Rating'] = np.nanmean(character_df['Rating'])
    character_row['Average_Price'] = np.nanmean(character_df['Original_price'])
    character_row['Average_Pages'] = np.nanmean(character_df['Page Count'])
    character_row['Publisher'] = "DC Comics"
    characters_dicts.append(character_row)
    character_row = {}
    
for character in main_marvel_characters:
    character_df = comixology_df[(comixology_df['Name'].str.contains(character)) & 
                                 (comixology_df['Publisher'] == 'Marvel')]
    character_row['Character_Name'] = character
    character_row['Quantity_of_comics'] = len(character_df)
    character_row['Average_Rating'] = np.nanmean(character_df['Rating'])
    character_row['Average_Price'] = np.nanmean(character_df['Original_price'])
    character_row['Average_Pages'] = np.nanmean(character_df['Page Count'])
    character_row['Publisher'] = "Marvel"
    characters_dicts.append(character_row)
    character_row = {}
    
characters_df = pd.DataFrame(characters_dicts)

# Create empty list and dict to hold team info
team_row = {}
teams_dicts = []

for team in dc_teams:
    team_df = comixology_df[(comixology_df['Name'].str.contains(team)) & 
                                 (comixology_df['Publisher'] == 'DC Comics')]
    team_row['Team_Name'] = team
    team_row['Quantity_of_comics'] = len(team_df)
    team_row['Average_Rating'] = np.nanmean(team_df['Rating'])
    team_row['Average_Price'] = np.nanmean(team_df['Original_price'])
    team_row['Average_Pages'] = np.nanmean(team_df['Page Count'])
    team_row['Publisher'] = "DC Comics"
    teams_dicts.append(team_row)
    team_row = {}
    
for team in marvel_teams:
    team_df = comixology_df[(comixology_df['Name'].str.contains(team)) & 
                                 (comixology_df['Publisher'] == 'Marvel')]
    team_row['Team_Name'] = team
    team_row['Quantity_of_comics'] = len(team_df)
    team_row['Average_Rating'] = np.nanmean(team_df['Rating'])
    team_row['Average_Price'] = np.nanmean(team_df['Original_price'])
    team_row['Average_Pages'] = np.nanmean(team_df['Page Count'])
    team_row['Publisher'] = "Marvel"
    teams_dicts.append(team_row)
    team_row = {}
    
teams_df = pd.DataFrame(teams_dicts)

# Filter characters and teams DataFrame for rows where there are more than 20
# comics where the character / team name is present on the title of the comics
characters_df = characters_df[characters_df['Quantity_of_comics'] > 20]
teams_df = teams_df[teams_df['Quantity_of_comics'] > 20]

# Limit number of characters to 20
top_characters_by_quantity = characters_df.sort_values(by='Quantity_of_comics',
                                         ascending=False)[['Character_Name',
                                         'Average_Rating',
                                         'Quantity_of_comics']].head(20)
top_characters_by_rating = characters_df.sort_values(by='Average_Rating',
                                         ascending=False)[['Character_Name',
                                         'Average_Rating',
                                         'Quantity_of_comics']].head(20)

top_teams_by_quantity = teams_df.sort_values(by='Quantity_of_comics', 
                                             ascending=False)[['Team_Name',
                                             'Average_Rating',
                                             'Quantity_of_comics']]
top_teams_by_rating = teams_df.sort_values(by='Average_Rating', 
                                           ascending=False)[['Team_Name',
                                           'Average_Rating',
                                           'Quantity_of_comics']]

print(top_characters_by_quantity)
print(top_characters_by_rating)
print(top_teams_by_quantity)
print(top_teams_by_rating)

# Create charts related to the characters information
plt.figure(3,figsize=(10, 6))

plt.subplot(121) # Characters by quantity of comics
y_axis = top_characters_by_quantity['Quantity_of_comics']
x_axis = np.arange(len(y_axis))
plt.bar(x_axis, y_axis)
plt.xticks(x_axis+0.4, tuple(top_characters_by_quantity['Character_Name']), 
                             rotation=90)
plt.title('Characters by quantity of comics')
plt.tight_layout()

plt.subplot(122) # Characters by average rating
y_axis = top_characters_by_rating['Average_Rating']
x_axis = np.arange(len(y_axis))
plt.bar(x_axis, y_axis)
plt.xticks(x_axis+0.4, tuple(top_characters_by_rating['Character_Name']), 
                             rotation=90)
plt.title('Characters by average ratings')
plt.tight_layout()

plt.show()

# Creation of charts related to teams
plt.figure(4,figsize=(10, 6))

plt.subplot(121) # Teams by quantity of comics
y_axis = top_teams_by_quantity['Quantity_of_comics']
x_axis = np.arange(len(y_axis))
plt.bar(x_axis, y_axis)
plt.xticks(x_axis+0.4, tuple(top_teams_by_quantity['Team_Name']), rotation=90)
plt.title('Teams by quantity of comics')
plt.tight_layout()

plt.subplot(122) # Teams by average ratings
y_axis = top_teams_by_rating['Average_Rating']
x_axis = np.arange(len(y_axis))
plt.bar(x_axis, y_axis)
plt.xticks(x_axis+0.4, tuple(top_teams_by_rating['Team_Name']), rotation=90)
plt.title('Teams by average ratings')
plt.tight_layout()

plt.show()