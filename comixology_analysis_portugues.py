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

# Vamos criar uma coluna de preço por página para futuras análises
comixology_df['Price_per_page'] = pd.Series(comixology_df['Original_price'] / 
                                            comixology_df['Page Count'], 
                                            index=comixology_df.index)
                                            
# Como alguns comics estão com a contagem de páginas igual a zero, vamos 
# definir para estes o Price_per_page igual a NaN
comixology_df.Price_per_page[comixology_df['Price_per_page'] == np.inf] = np.nan

# Vamos extrair o ano da string de data de publicação da versão impressa
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

# Algumas informações médias do site
average_price = np.nanmean(comixology_df['Original_price'])
average_page_count = np.nanmean(comixology_df['Page Count'])
average_rating = np.nanmean(comixology_df['Rating'])
average_rating_quantity = np.nanmean(comixology_df['Ratings_Quantity'])
average_price_per_page = np.nanmean(comixology_df['Price_per_page'])

print("Preço médio: " + str(average_price))
print("Quantidade média de páginas: " + str(average_page_count))
print("Avaliação média: " + str(average_rating))
print("Quantidade média de avaliações por comic: " + 
      str(average_rating_quantity))
print("Preço por página médio por comic: " + str(average_price_per_page))
                                            
# Vamos listar as comics com rating 5 estrelas que possuam pelo menos 
# 20 ratings e ordena-las por preço por página
comics_with_5_stars = comixology_df[comixology_df.Rating == 5]
comics_with_5_stars = comics_with_5_stars[comics_with_5_stars.Ratings_Quantity 
                                          > 20]
print(comics_with_5_stars[['Name','Publisher','Price_per_page']].
      sort_values(by='Price_per_page'))      

# Para a próxima análise, usaremos somente comics com mais de 5 ratings
comics_more_than_5_ratings = comixology_df[comixology_df.Ratings_Quantity > 5]

# Criar pivot table com média das avaliações por Publisher
publishers_avg_rating = pd.pivot_table(comics_more_than_5_ratings, 
                                       values=['Rating'], 
                                       index=['Publisher'], 
                                       aggfunc=[np.mean, np.count_nonzero])

# Primeiramente vamos avaliar qualquer publisher que tenha mais de 20 comics 
# com avaliações
main_pub_avg_rating = publishers_avg_rating[publishers_avg_rating.
                                            count_nonzero.Rating > 20]
main_pub_avg_rating = main_pub_avg_rating.sort_values(by=('mean','Rating'), 
                                                      ascending=False)
print(main_pub_avg_rating)

# Agora, um gráfico com a avaliação média de cada editora
y_axis = main_pub_avg_rating['mean']['Rating']
x_axis = range(len(y_axis))

plt.bar(x_axis, y_axis)
plt.xticks(x_axis, tuple(main_pub_avg_rating.index),rotation=90)
plt.show()

# E agora vamos ver as bem grandes, com mais de 300 comics com avaliações
big_pub_avg_rating = publishers_avg_rating[publishers_avg_rating.
                                           count_nonzero.Rating > 300]
big_pub_avg_rating = big_pub_avg_rating.sort_values(by=('mean','Rating'), 
                                                    ascending=False)
print(big_pub_avg_rating)

# E agora, o mesmo gráfico com a avaliação média das grandes editoras
y_axis = big_pub_avg_rating['mean']['Rating']
x_axis = np.arange(len(y_axis))

plt.bar(x_axis, y_axis)
plt.xticks(x_axis+0.5, tuple(big_pub_avg_rating.index), rotation=90)
plt.show()

# Vamos ver agora se a classificação etária faz alguma diferença significativa 
# nas avaliações
rating_by_age = pd.pivot_table(comics_more_than_5_ratings, 
                               values=['Rating'], 
                               index=['Age Rating'], 
                               aggfunc=[np.mean, np.count_nonzero])
                               
print(rating_by_age)
                               
# Gráfico de barras com a avaliação média por faixa etária
y_axis = rating_by_age['mean']['Rating']
x_axis = np.arange(len(y_axis))

plt.bar(x_axis, y_axis)
plt.xticks(x_axis+0.25, tuple(rating_by_age.index), rotation=45)
plt.show()
                               
# Cria tabela com a quantidade de quadrinhos lançados por ano, baseado na data 
# de lançamento da versão impressa
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
    
# Criação do gráfico de lançamento de comics por ano    
y_axis = print_releases_per_year['count_nonzero']['Name']
x_axis = print_releases_per_year['count_nonzero']['Name'].index
plt.plot(x_axis, y_axis)
plt.show()

# Vejamos agora as 30 comics com mais avaliações; se for mantida a proporção, 
# pode-se dizer que estas são as comics mais baixadas (e não vendidas, pois 
# algumas destas são gratuitas)
comics_by_ratings_quantity = comixology_df[['Name','Publisher',
                                            'Ratings_Quantity']].sort_values(
                                            by='Ratings_Quantity', 
                                            ascending=False)
print(comics_by_ratings_quantity.head(30))

y_axis = comics_by_ratings_quantity.head(30)['Ratings_Quantity']
x_axis = np.arange(len(y_axis))

plt.bar(x_axis, y_axis)
plt.xticks(x_axis+0.5, tuple(comics_by_ratings_quantity.head(30)['Name']), 
           rotation=90)
plt.show()

# Vamos agora ver dados somente das duas maiores: Marvel e DC
marvel_dc_comics = comixology_df[(comixology_df.Publisher == 'Marvel') | 
                                 (comixology_df.Publisher == 'DC Comics')]
 
# Primeiro, alguns valores médios de cada uma                                
marvel_dc_pivot_averages = pd.pivot_table(marvel_dc_comics, 
                               values=['Rating','Original_price','Page Count',
                                       'Price_per_page'], 
                               index=['Publisher'], 
                               aggfunc=[np.mean])
print(marvel_dc_pivot_averages)

# Criação do gráfico com informações médias de DC Comics e Marvel
plt.figure(1)

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

# Vamos agora verificar a quantidade de comics de cada uma e fazer uma proporção
# com a quantidade de comics de cada uma com rating maior ou igual a 4. Desta 
# forma podemos ver qual delas, proporcionalmente, lança bons comics
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
print("Total de Comics Marvel: " + str(marvel_total))
print("Total de Comics Marvel com avaliação maior ou igual a 4: " + 
      str(marvel_4_or_5))
print("Proporção de Comics Marvel com avaliação maior ou igual a 4: " + 
      str("{0:.2f}%".format(marvel_proportion_4_or_5 * 100)))
print("Total de Comics Marvel com avaliação menor ou igual a 2: " + 
      str(marvel_1_or_2))
print("Proporção de Comics Marvel com avaliação menor ou igual a 2: " + 
      str("{0:.2f}%".format(marvel_proportion_1_or_2 * 100)))
print("\n")
print("Total de Comics DC Comics: " + str(dc_total))
print("Total de Comics DC Comics com avaliação maior ou igual a 4: " + 
      str(dc_4_or_5))
print("Proporção de Comics DC Comics com avaliação maior ou igual a 4: " + 
      str("{0:.2f}%".format(dc_proportion_4_or_5 * 100)))
print("Total de Comics DC Comics com avaliação menor ou igual a 2: " + 
      str(dc_1_or_2))
print("Proporção de Comics DC Comics com avaliação menor ou igual a 2: " + 
      str("{0:.2f}%".format(dc_proportion_1_or_2 * 100)))
print("\n")

# Criação dos gráficos relativos às proporções de DC Comics e Marvel
plt.figure(2)

plt.subplot(221) # Total de Comics de cada editora
y_axis = [dc_total, marvel_total]
x_axis = np.arange(len(y_axis))
plt.bar(x_axis, y_axis)
plt.xticks(x_axis+0.4, ('DC Comics','Marvel'))
plt.title('Comics Totais')
plt.tight_layout()

plt.subplot(222) # Proporção de Comics com avaliação 4 ou 5
y_axis = [dc_proportion_4_or_5 * 100, marvel_proportion_4_or_5 * 100]
x_axis = np.arange(len(y_axis))
plt.bar(x_axis, y_axis)
plt.xticks(x_axis+0.4, ('DC Comics','Marvel'))
plt.title('Proporção de Comics com avaliação 4 ou 5')
plt.tight_layout()

plt.subplot(223) # Proporção de Comics com avaliação 1 ou 2
y_axis = [dc_proportion_1_or_2 * 100, marvel_proportion_1_or_2 * 100]
x_axis = np.arange(len(y_axis))
plt.bar(x_axis, y_axis)
plt.xticks(x_axis+0.4, ('DC Comics','Marvel'))
plt.title('Proporção de Comics com avaliação 1 ou 2')
plt.tight_layout()

plt.show()

# Somar a quantidade de avaliações em comics de cada editora
marvel_dc_pivot_sums = pd.pivot_table(marvel_dc_comics, 
                               values=['Ratings_Quantity'], 
                               index=['Publisher'], 
                               aggfunc=[np.sum])
print(marvel_dc_pivot_sums)

# Definir lista de times e personagens da DC e Marvel
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


# Criação de lista e dict vazio para guardar as informações. O mesmo será feito
# para os times
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

characters_df = characters_df[characters_df['Quantity_of_comics'] > 20]
teams_df = teams_df[teams_df['Quantity_of_comics'] > 20]

# Limitando a 20 o número de personagens
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

# Criação dos gráficos dos personagens
plt.figure(3,figsize=(10, 6))

plt.subplot(121) # Personagem por quantidade de comics
y_axis = top_characters_by_quantity['Quantity_of_comics']
x_axis = np.arange(len(y_axis))
plt.bar(x_axis, y_axis)
plt.xticks(x_axis+0.4, tuple(top_characters_by_quantity['Character_Name']), 
                             rotation=90)
plt.title('Personagem por Qtd de Comics')
plt.tight_layout()

plt.subplot(122) # Personagem por avaliação média
y_axis = top_characters_by_rating['Average_Rating']
x_axis = np.arange(len(y_axis))
plt.bar(x_axis, y_axis)
plt.xticks(x_axis+0.4, tuple(top_characters_by_rating['Character_Name']), 
                             rotation=90)
plt.title('Personagem por Avaliação Média')
plt.tight_layout()

plt.show()

# Criação dos gráficos dos times
plt.figure(4,figsize=(10, 6))

plt.subplot(121) # Time por quantidade de comics
y_axis = top_teams_by_quantity['Quantity_of_comics']
x_axis = np.arange(len(y_axis))
plt.bar(x_axis, y_axis)
plt.xticks(x_axis+0.4, tuple(top_teams_by_quantity['Team_Name']), rotation=90)
plt.title('Time por quantidade de comics')
plt.tight_layout()

plt.subplot(122) # Time por avaliação média
y_axis = top_teams_by_rating['Average_Rating']
x_axis = np.arange(len(y_axis))
plt.bar(x_axis, y_axis)
plt.xticks(x_axis+0.4, tuple(top_teams_by_rating['Team_Name']), rotation=90)
plt.title('Time por avaliação média')
plt.tight_layout()

plt.show()