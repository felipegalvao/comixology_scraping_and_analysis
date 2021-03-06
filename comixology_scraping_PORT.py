# -*- coding: utf-8 -*-
"""
Created on Sat Mar 26 11:48:26 2016

@author: Felipe Galvão
"""

from lxml import html
import requests
import re
import pandas as pd
import pickle
import time
import os.path

# Remover atributos dos links de uma lista de links e retornar lista "limpa"
def remove_attributes_from_link(comic_link_list):
    clean_comic_link_list = []   
    for comic_link in comic_link_list:
        # Substituir tudo após a "?" por nada
        new_comic_link = re.sub("(\?.+)","",comic_link)
        clean_comic_link_list.append(new_comic_link)
    return(clean_comic_link_list)

# Retornar lista de Links dos Publishers
def get_publishers_links():
    publisher_links = []
    
    # Iterar por cada página do link Browse > by Publisher
    for i in range(1,5):
        # Definição do link a ser explorado
        link = 'https://www.comixology.com/browse-publisher?publisherList_pg='
        page = requests.get(link+str(i))
        tree = html.fromstring(page.content)
        
        # Expressão Xpath para extração dos links dos Publishers        
        quantity_pub_xpath = '//div[@class="list publisherList"]/ul'
        quantity_pub_xpath += '/li[@class="content-item"]/figure/div/a/@href'
        
        # Extração dos links através da função Xpath    
        extracted_publishers_links = tree.xpath(quantity_pub_xpath)
        clean_publisher_links = remove_attributes_from_link(
            extracted_publishers_links)
        # Inserir os links na lista já criada
        publisher_links.extend(clean_publisher_links)
            
    return(publisher_links)

# Recebe lista de links de cada Publisher e retorna lista de links para as
# Series de comics existentes no site Comixology
def get_series_links_from_publisher(publisher_links):
    series_links = []
    
    for link in publisher_links:
        page = requests.get(link)
        tree = html.fromstring(page.content)
        
        # String xpath para extração da quantidade total de Series
        xpath_series = '//div[@class="list seriesList"]/div[@class="pager"]'
        xpath_series += '/div[@class="pager-text"]/text()'
        
        total_series = tree.xpath(xpath_series)
        
        # Se a extração retornou a quantidade total:
        if total_series:
            # O único item da lista é a string, cujo último elemento é a 
            # quantidade de Series
            total_series = total_series[0].split()
            total_series = int(total_series[len(total_series)-1])
            # Divide-se o total de Series por 36, afim de descobrir o número
            # de páginas de Series neste Publisher
            if total_series % 36 == 0:
                number_of_pages = (total_series // 36)
            else:
                number_of_pages = (total_series // 36) + 1
        # Se a extração retornou uma lista vazia, só existe uma página de Series
        else:
            number_of_pages = 1     
        for page_number in range(1,number_of_pages+1):
            page = requests.get(link+'?seriesList_pg='+str(page_number))                
            tree = html.fromstring(page.content)            
            
            # String Xpath para extração dos links das Series nesta página
            xpath_series_links = '//div[@class="list seriesList"]/ul/'
            xpath_series_links += 'li[@class="content-item"]/figure/'
            xpath_series_links += 'div[@class="content-cover"]/a/@href'
            extracted_series_links = tree.xpath(xpath_series_links) 
            clean_series_links = remove_attributes_from_link(extracted_series_links)                
            series_links.extend(clean_series_links)
    return(series_links)


def extract_comics_links(link, div_xpath, page_link_str, tree):
    type_comics_links = []
    # Checa se o div para o tipo de comic em questão existe
    type_div = tree.xpath(div_xpath)
    
    if type_div:
        # Busca a quantidade total de comics para este tipo de comic
        total_quantity_xpath = div_xpath + '/div[@class="pager"]/'
        total_quantity_xpath += 'div[@class="pager-text"]/text()'
        total_type = tree.xpath(total_quantity_xpath)
        if total_type:
            total_type = total_type[0].split()
            total_type = int(total_type[len(total_type)-1])
            if total_type % 18 == 0:
                number_of_pages = (total_type // 18)
            else:
                number_of_pages = (total_type // 18) + 1
        else:
            number_of_pages = 1            
        for page_number in range(1,number_of_pages+1):            
            page = requests.get(link+page_link_str+str(page_number))                
            tree = html.fromstring(page.content)
            # Path para os links deste tipo de comic
            type_links_xpath = div_xpath + '/ul/li/figure/div/a/@href'
            type_links = tree.xpath(type_links_xpath)
            clean_type_links = remove_attributes_from_link(type_links)            
            type_comics_links.extend(clean_type_links)
    return(type_comics_links)  

def comics_links_dump(comics_links, counter, comics_links_counter):
    pickle.dump(comics_links, open("comics_links_files/comics_links" + 
                "_" + str((counter + comics_links_counter) // 100 + 1) 
                + ".p","wb"))
    pickle.dump(counter + comics_links_counter, 
                open("comics_links_files/comics_links_counter.p","wb"))
    comics_links = []
    return(comics_links)

def get_issues_links_from_series(series_links, comics_links_counter):
    comics_links = []
    
    for counter, link in enumerate(series_links):
        page = requests.get(link)    
        tree = html.fromstring(page.content)
        
# -------------------------------------------------------------- #
        # Código de scraping para collected editions
# -------------------------------------------------------------- #        
        
        collected_div_xpath = '//div[@class="list CollectedEditions"]'
        collected_link_str = '?CollectedEditions_pg='        
                    
        collected_links = extract_comics_links(link, collected_div_xpath, 
                                               collected_link_str, tree)
                
# -------------------------------------------------------------- #
        # Código de scraping para Issues
# -------------------------------------------------------------- #
        issues_div_xpath = '//div[@class="list Issues"]'
        issues_link_str = '?Issues_pg='
                    
        issues_links = extract_comics_links(link, issues_div_xpath,
                                            issues_link_str, tree)
                
# -------------------------------------------------------------- #
        # Código de scraping para Omnibuses
# -------------------------------------------------------------- #
        omnibuses_div_xpath = '//div[@class="list Omnibuses"]'
        omnibuses_link_str = '?Omnibuses_pg='               
                    
        omnibuses_links = extract_comics_links(link, omnibuses_div_xpath, 
                                               omnibuses_link_str, tree)
        
# -------------------------------------------------------------- #
        # Código de scraping para One-Shots
# -------------------------------------------------------------- #
        oneshots_div_xpath = '//div[@class="list OneShots"]'
        oneshots_link_str = '?Oneshots_pg='
                    
        oneshots_links = extract_comics_links(link, oneshots_div_xpath,
                                              oneshots_link_str, tree)
                    
# -------------------------------------------------------------- #
        # Código de scraping para Bandees Dessinees
# -------------------------------------------------------------- #
        bandes_div_xpath = '//div[@class="list BandesDessines"]'
        bandes_link_str = '?BandeesDessinees_pg='
                    
        bandes_links = extract_comics_links(link, bandes_div_xpath,
                                              bandes_link_str, tree)

# -------------------------------------------------------------- #
        # Código de scraping para Graphic Novels
# -------------------------------------------------------------- #
        graphicnovels_div_xpath = '//div[@class="list GraphicNovels"]'
        graphicnovels_link_str = '?GraphicNovels_pg='
                    
        graphicnovels_links = extract_comics_links(link, graphicnovels_div_xpath,
                                              graphicnovels_link_str, tree)

# -------------------------------------------------------------- #
        # Código de scraping para Extras
# -------------------------------------------------------------- #
        extras_div_xpath = '//div[@class="list Extras"]'
        extras_link_str = '?Extras_pg='
                    
        extras_links = extract_comics_links(link, extras_div_xpath,
                                              extras_link_str, tree)
                    
# -------------------------------------------------------------- #
        # Código de scraping para Artbooks
# -------------------------------------------------------------- #
        artbooks_div_xpath = '//div[@class="list Artbooks"]'
        artbooks_link_str = '?Artbooks_pg='
                    
        artbooks_links = extract_comics_links(link, artbooks_div_xpath,
                                              artbooks_link_str, tree)
        
        # Juntar os links de cada tipo de comic com a lista previamente criada                                      
        comics_links.extend(collected_links + issues_links + omnibuses_links + 
                            oneshots_links + bandes_links + graphicnovels_links + 
                            extras_links + artbooks_links)        
        
        # Exportar os links de comics de 100 em 100 ou quando o contador chega
        # ao último link para evitar perda de informações em possíveis erros / 
        # problemas
        if (counter % 100 == 0 and counter != 0) or (
            counter == len(series_links) - 1):
            comics_links = comics_links_dump(comics_links, counter, 
                                             comics_links_counter)            
    return(comics_links)

def get_comic_info_from_page(link):
    comic_info = {}    
    
    page = requests.get(link)    
    tree = html.fromstring(page.content)    
    
    # Definir o caminho base que contém o conteúdo da página
    base_path = '//div[@class="comic_view detail-container"]'
    
    # Extração do título da página, para verificar se este endereço retorna
    # um erro 404 ou não. Se não for um erro, continua o código
    page_title = tree.xpath('//title/text()')[0]    
    if page_title != 'Site Error - Comics by comiXology':
        # Extrair o nome do comic
        name = tree.xpath('//h2[@itemprop="name"]/text()')
        comic_info['Name'] = name[0]
        
        # Extrair lista das tarefas dos créditos e nomes que fazem cada uma
        credits_tasks_str = base_path + '/div[@id="column3"]/'
        credits_tasks_str += 'div[@class="credits"]/div/dl/dt/text()'
        credits_tasks = tree.xpath(credits_tasks_str)
        
        credits_names_str = base_path + '/div[@id="column3"]/'
        credits_names_str += 'div[@class="credits"]/div/dl/dd/a/text()'        
        credits_names = tree.xpath(credits_names_str)
        
        # ---------------------------------------------------------------------
        # Consertar os nomes, remover sequências escapadas e criar nova lista 
        # de nomes
        # ---------------------------------------------------------------------
        credits_names_lists = []
        
        first_item = 0
        for counter, name in enumerate(credits_names):
            if name == 'HIDE...':
                credits_names_lists.append(credits_names[first_item:counter])
                first_item = counter+1
        
        new_names = []
        new_names_credits = []
                
        for names_list in credits_names_lists:
            for name in names_list:
                new_name = re.sub("^\\n\\t\\t\\t\\t\\t\\t\\t","", name)
                new_name = re.sub("\\t\\t\\t\\t\\t\\t$", "", new_name)
                if new_name != "More...":
                    new_names.append(new_name)
            new_names_credits.append(new_names)
            new_names = []
        # ---------------------------------------------------------------------
        # Fim do ajuste dos nomes
        # ---------------------------------------------------------------------
        
        # Inserir cada informação de crédito no dict comic_info
        for counter, item in enumerate(credits_tasks):        
            comic_info[item] = new_names_credits[counter]
        
        # Extrair o Publisher do comic
        publisher = tree.xpath('//*[@id="column3"]/div/div[1]/a[2]/span/text()')
        publisher = re.sub("^\\n\\t\\t\\t","",publisher[0])
        publisher = re.sub("\\t\\t$","",publisher)
        comic_info['Publisher'] = publisher
        
        # Extrair lista de informações sobre o comic, como contagem de página, 
        # faixa etária, etc
        comics_infos_names_xpath = base_path + '/div[@id="column3"]/'
        comics_infos_names_xpath += 'div[@class="credits"]/'
        comics_infos_names_xpath += 'h4[@class="subtitle"]/text()'
        comics_infos_names = tree.xpath(comics_infos_names_xpath)
        
        comics_infos_values_xpath = base_path + '/div[@id="column3"]/'
        comics_infos_values_xpath += 'div[@class="credits"]/'
        comics_infos_values_xpath += 'div[@class="aboutText"]/text()'        
        comics_infos_values = tree.xpath(comics_infos_values_xpath)
        
        # Inserir a informação do comic no dictionary
        for counter, item in enumerate(comics_infos_names):
            if item == 'Page Count':            
                comic_info[item] = int(comics_infos_values[counter].split()[0])
            else:
                comic_info[item] = comics_infos_values[counter]
                
        # Extrair os preços do comic
        full_price_xpath = '//h6[@class="item-full-price"]/text()'
        # Extrair preço cheio
        full_price = tree.xpath(full_price_xpath)
        discounted_price_xpath = '//div[@class="pricing-info"]/'
        discounted_price_xpath += 'h5[@class="item-price"]/text()'
        # Extrair preço descontado, se houver
        discounted_price = tree.xpath(discounted_price_xpath)
        if discounted_price:
            # Se preço descontado é igual a string FREE, esse é um comic gratuito
            if discounted_price[0] == 'FREE':
                final_price = 0.0
            # Se não, extrair o preço final
            else:
                final_price = float(discounted_price[0][1:])
            # Se existe um preço cheio, o comic tem um preço descontado
            if full_price:
                original_price = float(full_price[0][1:])
                discounted = True
            # Se não, os preços são iguais e não há desconto para este comic
            else:
                original_price = final_price
                discounted = False            
        # Estes casos se aplicam a comics exclusivos de Bundles
        else:
            final_price = None
            original_price = None
            discounted = False
        comic_info['Original_price'] = original_price
        comic_info['Final_price'] = final_price
        comic_info['Discounted'] = discounted
    
        # Extrair a avaliação do comic do elemento escondido
        ratings_value_xpath = '//*[@id="column2"]/div[2]/div[2]/div[2]/text()'
        ratings_value = tree.xpath(ratings_value_xpath)
        if ratings_value:
            ratings_value = ratings_value[0]
            ratings_value = re.sub("^\\n\\t\\t\\t\\t\\t\\t\\t","",ratings_value)
            ratings_value = int(re.sub("\\t\\t\\t\\t\\t\\t$","",ratings_value))
            comic_info['Rating'] = ratings_value
        else:
            comic_info['Rating'] = None
        
        # Extrair quantidade de avaliações no comic
        ratings_quantity_xpath = '//*[@id="column2"]/div[2]/div[2]/div[1]/text()'
        ratings_quantity = tree.xpath(ratings_quantity_xpath)    
        if ratings_quantity:
            ratings_quantity = ratings_quantity[0].split()[2]
            ratings_quantity = ratings_quantity[1:][:-2]        
            comic_info['Ratings_Quantity'] = int(ratings_quantity)
        else:
            comic_info['Ratings_Quantity'] = 0

    return(comic_info)
    
def get_all_comics_info(comics_links, start_counter):
    all_comics_info = []
    for counter, link in enumerate(comics_links):    
        comic_info = get_comic_info_from_page(link)
        if comic_info:
            all_comics_info.append(comic_info)
        if (counter % 100 == 0 and counter != 0) or (counter + 
            start_counter == len(comics_links)-1):
            print(comic_info)
            pickle.dump(all_comics_info, open("Comics_info/comics_infos_" + "_" +
                        str((counter + start_counter) // 100) + ".p","wb"))
            pickle.dump(counter + start_counter, 
                        open("Comics_info/counter_comics_info.p","wb"))
            all_comics_info = []
            
def join_comics_links():
    comics_links = []
    # Para cada arquivo na pasta "comics_links_folder"
    for file in os.listdir("comics_links_folder"):
        temp_comics_links = pickle.load(open("comics_links_folder/" + file,"rb"))                
        comics_links.append(temp_comics_links)
    return(comics_links)
    
def join_comics_info():
    comics_info = []
    # Para cada arquivo na pasta "comics_info_files"
    for file in os.listdir("comics_info_files"):
        if file != "counter_comics_info.p" and file != "Comics_info_backup.7z":
            print(file)
            comic_info = pickle.load(open("comics_info_files/" + file,"rb"))
            for comic in comic_info:    
                comics_info.append(comic)
    pickle.dump(comics_info, open("all_comics_info.p", "wb"))

# Checar se o arquivo publisher_links.p existe   
if os.path.isfile('publisher_links.p') == True:
    print("Arquivo de Links de Publishers já existe... carregando arquivo")
    publisher_links = pickle.load(open("publisher_links.p","rb"))
# Se não existir, iniciar o scraping
else:
    print("Arquivo de Links de Publishers não existe.")
    print("Iniciando o Scraping do site para links de Publishers.")
    print("Links serão exportados para o arquivo publisher_links.p")
    publisher_links = get_publishers_links()
    pickle.dump(publisher_links, open("publisher_links.p","wb"))

# Checar se o arquivo series_links.p existe    
if os.path.isfile('series_links.p') == True:
    print("Arquivo de Links de Series já existe... carregando arquivo")
    series_links = pickle.load(open("series_links.p","rb"))
# Se não existir, iniciar o scraping  
else:
    print("Arquivo de Links de Series não existe.")
    print("Iniciando o Scraping do site para links de Series.")
    print("Links serão exportados para o arquivo series_links.p")
    series_links = get_series_links_from_publisher(publisher_links)
    pickle.dump(series_links, open("series_links.p","wb"))
 
# Checar se a pasta "comics_links_files" existe   
if os.path.isdir('comics_links_files'):
    print("Pasta comics_links_files já existe. Checando arquivos.")
    # Checar se o arquivo comics_links_counter.p (contador) existe
    if os.path.isfile('comics_links_files/comics_links_counter.p'):
        # Carregar o contador
        comics_links_counter = pickle.load(open("comics_links_files/comics_links_counter.p","rb"))        
        print("Contagem atual: " + str(comics_links_counter+1) + " de " +
              str(len(series_links)))
        # Checar, através da comparação do contador com a quantidade de itens, 
        # se o scraping está completo
        if comics_links_counter + 1 == len(series_links):
            print("Scraping completo. Carregando arquivos.")
            comics_links = join_comics_links()
        # Se não estiver, continuar o scraping de onde parou
        else:
            print("Scraping iniciado mas não completo. Continuando...")
            get_issues_links_from_series(series_links[comics_links_counter+1:], 
                                         comics_links_counter)
            comics_links = join_comics_links()
    # Se o contador não existir, iniciar o scraping        
    else:
        print("Scraping de links de comics não iniciado.")
        print("Iniciando scraping de links de comics.")
        comics_links_counter = 0
        get_issues_links_from_series(series_links, comics_links_counter)
        comics_links = join_comics_links()
# Se a pasta não existir, cria-la e iniciar o scraping
else:
    print("Pasta comics_links_files não existe.")
    print("Criando pasta comics_links_files")
    os.makedirs("comics_links_files")
    print("Iniciando scraping de links de comics.")
    comics_links_counter = 0
    get_issues_links_from_series(series_links, comics_links_counter)
    comics_links = join_comics_links()

# Checar se a pasta 'comics_info_files' existe    
if os.path.isdir('comics_info_files'):
    print("Pasta comics_info_files já existe. Checando arquivos.")
    # Checar se o arquivo 'comics_info_counter.p' (contador) existe
    if os.path.isfile('comics_info_files/comics_info_counter.p'):
        # Carregar o contador
        comics_info_counter = pickle.load(open("comics_info_counter.p"))        
        print("Contagem atual: " + str(comics_info_counter+1) + " de " +
              str(len(comics_links)))
        # Checar, através da comparação do contador com a quantidade de itens, 
        # se o scraping está completo
        if comics_info_counter + 1 == len(comics_links):
            print("Scraping já completo. Carregando arquivos.")
        # Se não estiver completo, continuar o scraping de onde parou            
        else:
            print("Scraping iniciado mas não completo. Continuando...")
            get_all_comics_info(comics_links[comics_info_counter+1:], 
                                comics_info_counter)
    # Se o contador não existir, iniciar o scraping
    else:
        print("Scraping de informações de comics não iniciado.")
        print("Iniciando scraping de informações de comics.")
        comics_info_counter = 0
        get_all_comics_info(comics_links, comics_info_counter)
# Se a pasta não existir, cria-la e iniciar o scraping
else:
    print("Pasta comics_info_files não existe.")
    print("Criando pasta comics_info_files")
    os.makedirs("comics_info_files")
    print("Iniciando scraping de informações de comics.")
    comics_info_counter = 0
    get_all_comics_info(comics_links, comics_info_counter)
    
# Juntar as informações dos comics
join_comics_info()
# Carregar as informações de todos os comics
comics_info = pickle.load(open("comics_info_files/all_comics_info.p","rb"))
# Criar um DataFrame com a lista de dictionaries
comics_df = pd.DataFrame(comics_info)
#Criar CSV com o DataFrame
comics_df.to_csv("comixology_comics_dataset.csv")