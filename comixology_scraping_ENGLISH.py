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

# Remove attributes from links in a list and return "clean" list
def remove_attributes_from_link(comic_link_list):
    clean_comic_link_list = []   
    for comic_link in comic_link_list:
        # Substituir tudo após a "?" por nada
        new_comic_link = re.sub("(\?.+)","",comic_link)
        clean_comic_link_list.append(new_comic_link)
    return(clean_comic_link_list)

# Return list with links of publishers
def get_publishers_links():
    publisher_links = []
    
    # Iterate through each page of the link Browse > by Publisher
    for i in range(1,5):
        # Definition of the link to be scraped
        link = 'https://www.comixology.com/browse-publisher?publisherList_pg='
        page = requests.get(link+str(i))
        tree = html.fromstring(page.content)
        
        # Xpath expression for extraction of Publishers' links        
        quantity_pub_xpath = '//div[@class="list publisherList"]/ul'
        quantity_pub_xpath += '/li[@class="content-item"]/figure/div/a/@href'
        
        # Extraction of links through Xpath function
        extracted_publishers_links = tree.xpath(quantity_pub_xpath)
        clean_publisher_links = remove_attributes_from_link(
            extracted_publishers_links)
        # Insert links into the already created list
        publisher_links.extend(clean_publisher_links)
            
    return(publisher_links)

# Receive list of links for each Publisher and return list of links for the 
# Comics Series
def get_series_links_from_publisher(publisher_links):
    series_links = []
    
    for link in publisher_links:
        page = requests.get(link)
        tree = html.fromstring(page.content)
        
        # Xpath string for extraction of total quantity of Series
        xpath_series = '//div[@class="list seriesList"]/div[@class="pager"]'
        xpath_series += '/div[@class="pager-text"]/text()'
        
        total_series = tree.xpath(xpath_series)
        
        # If the extraction returned the total quantity
        if total_series:
            # The only item in the list is a string with the quantity, which
            # we will split to create a list with each word of it
            total_series = total_series[0].split()
            # Quantity of series will be the last item of that series
            total_series = int(total_series[len(total_series)-1])
            # Divide the quantity of Series by 36, in order to discover the
            # number of pages of Series in this Publisher
            if total_series % 36 == 0:
                number_of_pages = (total_series // 36)
            else:
                number_of_pages = (total_series // 36) + 1
        # If the extraction returns an empty list, there is only one page of Series
        else:
            number_of_pages = 1
        for page_number in range(1,number_of_pages+1):
            page = requests.get(link+'?seriesList_pg='+str(page_number))
            tree = html.fromstring(page.content)
            
            # Xpath for extraction of the Series links in this page
            xpath_series_links = '//div[@class="list seriesList"]/ul/'
            xpath_series_links += 'li[@class="content-item"]/figure/'
            xpath_series_links += 'div[@class="content-cover"]/a/@href'
            extracted_series_links = tree.xpath(xpath_series_links)
            clean_series_links = remove_attributes_from_link(extracted_series_links)
            series_links.extend(clean_series_links)
    return(series_links)


def extract_comics_links(link, div_xpath, page_link_str, tree):
    type_comics_links = []
    # Check if the div for this type of comic exists
    type_div = tree.xpath(div_xpath)
    
    if type_div:
        # Get the total quantity of comics for this type of comic
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
            # Path for the links to this type of comic
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
        # Scraping code for the collected editions
# -------------------------------------------------------------- #        
        
        collected_div_xpath = '//div[@class="list CollectedEditions"]'
        collected_link_str = '?CollectedEditions_pg='        
                    
        collected_links = extract_comics_links(link, collected_div_xpath, 
                                               collected_link_str, tree)
                
# -------------------------------------------------------------- #
        # Scraping code for the Issues
# -------------------------------------------------------------- #
        issues_div_xpath = '//div[@class="list Issues"]'
        issues_link_str = '?Issues_pg='
                    
        issues_links = extract_comics_links(link, issues_div_xpath,
                                            issues_link_str, tree)
                
# -------------------------------------------------------------- #
        # Scraping code for the Omnibuses
# -------------------------------------------------------------- #
        omnibuses_div_xpath = '//div[@class="list Omnibuses"]'
        omnibuses_link_str = '?Omnibuses_pg='               
                    
        omnibuses_links = extract_comics_links(link, omnibuses_div_xpath, 
                                               omnibuses_link_str, tree)
        
# -------------------------------------------------------------- #
        # Scraping code for the One-Shots
# -------------------------------------------------------------- #
        oneshots_div_xpath = '//div[@class="list OneShots"]'
        oneshots_link_str = '?Oneshots_pg='
                    
        oneshots_links = extract_comics_links(link, oneshots_div_xpath,
                                              oneshots_link_str, tree)
                    
# -------------------------------------------------------------- #
        # Scraping code for the Bandees Dessinees
# -------------------------------------------------------------- #
        bandes_div_xpath = '//div[@class="list BandesDessines"]'
        bandes_link_str = '?BandeesDessinees_pg='
                    
        bandes_links = extract_comics_links(link, bandes_div_xpath,
                                              bandes_link_str, tree)

# -------------------------------------------------------------- #
        # Scraping code for the Graphic Novels
# -------------------------------------------------------------- #
        graphicnovels_div_xpath = '//div[@class="list GraphicNovels"]'
        graphicnovels_link_str = '?GraphicNovels_pg='
                    
        graphicnovels_links = extract_comics_links(link, graphicnovels_div_xpath,
                                              graphicnovels_link_str, tree)

# -------------------------------------------------------------- #
        # Scraping code for the Extras
# -------------------------------------------------------------- #
        extras_div_xpath = '//div[@class="list Extras"]'
        extras_link_str = '?Extras_pg='
                    
        extras_links = extract_comics_links(link, extras_div_xpath,
                                              extras_link_str, tree)
                    
# -------------------------------------------------------------- #
        # Scraping code for Artbooks
# -------------------------------------------------------------- #
        artbooks_div_xpath = '//div[@class="list Artbooks"]'
        artbooks_link_str = '?Artbooks_pg='
                    
        artbooks_links = extract_comics_links(link, artbooks_div_xpath,
                                              artbooks_link_str, tree)
                                              
        # Add links to all kinds of comics in the list previously created
        comics_links.extend(collected_links + issues_links + omnibuses_links + 
                            oneshots_links + bandes_links + graphicnovels_links + 
                            extras_links + artbooks_links)        
        
        # Export links each time 100 links are visited, avoiding loss of information 
		# due to possible errors
        if (counter % 100 == 0 and counter != 0) or (
            counter == len(series_links) - 1):
            comics_links = comics_links_dump(comics_links, counter,
                                             comics_links_counter)
    return(comics_links)

def get_comic_info_from_page(link):
    comic_info = {}    
    
    page = requests.get(link)    
    tree = html.fromstring(page.content)    
    
    # Define the base path that contains the content of the page
    base_path = '//div[@class="comic_view detail-container"]'
    
     # Extract the title of the page, to check if this address returns a 404 error
    page_title = tree.xpath('//title/text()')[0]    
    if page_title != 'Site Error - Comics by comiXology':
        # Extract the name of the comic
        name = tree.xpath('//h2[@itemprop="name"]/text()')
        comic_info['Name'] = name[0]
        
        # Extract list of tasks from credits and names that execute each task
        credits_tasks_str = base_path + '/div[@id="column3"]/'
        credits_tasks_str += 'div[@class="credits"]/div/dl/dt/text()'
        credits_tasks = tree.xpath(credits_tasks_str)
        
        credits_names_str = base_path + '/div[@id="column3"]/'
        credits_names_str += 'div[@class="credits"]/div/dl/dd/a/text()'        
        credits_names = tree.xpath(credits_names_str)
        
        # ---------------------------------------------------------------------
        # Fix names, remove scape sequences and create new list of names
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
        # End of name fixing
        # ---------------------------------------------------------------------
        
        # Insert each credits information in the comic_info dictionary
        for counter, item in enumerate(credits_tasks):        
            comic_info[item] = new_names_credits[counter]
        
        # Extract Publisher of comic
        publisher = tree.xpath('//*[@id="column3"]/div/div[1]/a[2]/span/text()')
        publisher = re.sub("^\\n\\t\\t\\t","",publisher[0])
        publisher = re.sub("\\t\\t$","",publisher)
        comic_info['Publisher'] = publisher
        
        # Extract list of informations of the comic, such as page count, 
		# age classification, etc
        comics_infos_names_xpath = base_path + '/div[@id="column3"]/'
        comics_infos_names_xpath += 'div[@class="credits"]/'
        comics_infos_names_xpath += 'h4[@class="subtitle"]/text()'
        comics_infos_names = tree.xpath(comics_infos_names_xpath)
        
        comics_infos_values_xpath = base_path + '/div[@id="column3"]/'
        comics_infos_values_xpath += 'div[@class="credits"]/'
        comics_infos_values_xpath += 'div[@class="aboutText"]/text()'        
        comics_infos_values = tree.xpath(comics_infos_values_xpath)
        
        # Add the information of the comic into the dictionary
        for counter, item in enumerate(comics_infos_names):
            if item == 'Page Count':            
                comic_info[item] = int(comics_infos_values[counter].split()[0])
            else:
                comic_info[item] = comics_infos_values[counter]
                
        # Extract prices from the comic
        full_price_xpath = '//h6[@class="item-full-price"]/text()'
        # Extract full price
        full_price = tree.xpath(full_price_xpath)
        discounted_price_xpath = '//div[@class="pricing-info"]/'
        discounted_price_xpath += 'h5[@class="item-price"]/text()'
        # Extract discounted price, if it exists
        discounted_price = tree.xpath(discounted_price_xpath)
        if discounted_price:
            # If discounted price is equal to the string FREE, this is a free comic
            if discounted_price[0] == 'FREE':
                final_price = 0.0
            # If it is not, extract the final price
            else:
                final_price = float(discounted_price[0][1:])
            # If there is a full price, the comic has a discounted price too
            if full_price:
                original_price = float(full_price[0][1:])
                discounted = True
            # If there is not, the prices are equal and there is no discount
            else:
                original_price = final_price
                discounted = False            
        # Comics exclusive to bundles
        else:
            final_price = None
            original_price = None
            discounted = False
        comic_info['Original_price'] = original_price
        comic_info['Final_price'] = final_price
        comic_info['Discounted'] = discounted
    
        # Extract comic rating from the hidden element
        ratings_value_xpath = '//*[@id="column2"]/div[2]/div[2]/div[2]/text()'
        ratings_value = tree.xpath(ratings_value_xpath)
        if ratings_value:
            ratings_value = ratings_value[0]
            ratings_value = re.sub("^\\n\\t\\t\\t\\t\\t\\t\\t","",ratings_value)
            ratings_value = int(re.sub("\\t\\t\\t\\t\\t\\t$","",ratings_value))
            comic_info['Rating'] = ratings_value
        else:
            comic_info['Rating'] = None
        
        # Extract comic's rating quantity
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
    # For each file one the "comics_links_folder" folder
    for file in os.listdir("comics_links_folder"):
        temp_comics_links = pickle.load(open("comics_links_folder/" + file,"rb"))                
        comics_links.append(temp_comics_links)
    return(comics_links)
    
def join_comics_info():
    comics_info = []
    # For each file in the "comics_info_files" folder
    for file in os.listdir("comics_info_files"):
        if file != "counter_comics_info.p" and file != "Comics_info_backup.7z":
            print(file)
            comic_info = pickle.load(open("comics_info_files/" + file,"rb"))
            for comic in comic_info:    
                comics_info.append(comic)
    pickle.dump(comics_info, open("all_comics_info.p", "wb"))

# Check if the file publisher_links.p exists; if it does not, do the scraping   
if os.path.isfile('publisher_links.p') == True:
    print("Arquivo de Links de Publishers já existe... carregando arquivo")
    publisher_links = pickle.load(open("publisher_links.p","rb"))
# If it does not, do the scraping
else:
    print("Arquivo de Links de Publishers não existe.")
    print("Iniciando o Scraping do site para links de Publishers.")
    print("Links serão exportados para o arquivo publisher_links.p")
    publisher_links = get_publishers_links()
    pickle.dump(publisher_links, open("publisher_links.p","wb"))

# Check if the series_links.p file exists    
if os.path.isfile('series_links.p') == True:
    print("Arquivo de Links de Series já existe... carregando arquivo")
    series_links = pickle.load(open("series_links.p","rb"))
# If it does not, do the scraping  
else:
    print("Arquivo de Links de Series não existe.")
    print("Iniciando o Scraping do site para links de Series.")
    print("Links serão exportados para o arquivo series_links.p")
    series_links = get_series_links_from_publisher(publisher_links)
    pickle.dump(series_links, open("series_links.p","wb"))
 
# Check if the file publisher_links.p exists; if it does not, do the scraping
if os.path.isfile('publisher_links.p') == True:
    print("Publisher links file already exists... loading file")
    publisher_links = pickle.load(open("publisher_links.p","rb"))
else:
    print("Publisher links file does not exists.")
    print("Scraping website for the publisher links")
    print("Links will be exported to publisher_links.p")
    publisher_links = get_publishers_links()
    pickle.dump(publisher_links, open("publisher_links.p","wb"))
    
# Check if the series_links.p file exists; if it does not, do the scraping
if os.path.isfile('series_links.p') == True:
    print("Series links file already exists... loading file")
    series_links = pickle.load(open("series_links.p","rb"))
else:
    print("Series links file does not exists.")
    print("Scraping website for the series links")
    print("Links will be exported to series_links.p")
    series_links = get_series_links_from_publisher(publisher_links)
    pickle.dump(series_links, open("series_links.p","wb"))
 
# Check if the comics_links_files folder exists
if os.path.isdir('comics_links_files'):
    print("Folder comics_links_files already exists. Checking for files")
    # Check if the counter for the scraping code exists
    if os.path.isfile('comics_links_files/comics_links_counter.p'):
        # Load the counter and check if the scraping process is complete
        comics_links_counter = pickle.load(open("comics_links_files/comics_links_counter.p","rb"))       
        print("Current count: " + str(comics_links_counter+1) + " of " +
              str(len(series_links)))
        # If the scraping is complete, load the files
        if comics_links_counter + 1 == len(series_links):
            print("Scraping already completed. Loading files")
            comics_links = join_comics_links()
        # If the scraping is not complete, continue it
        else:
            print("Scraping initiated but not completed. Continuing...")
            get_issues_links_from_series(series_links[comics_links_counter+1:], 
                                         comics_links_counter)
            comics_links = join_comics_links()            
    # If the file does not exists, start the scraping
    else:
        print("Comics links extracting not started.")
        print("Starting comics links scraping")
        comics_links_counter = 0
        get_issues_links_from_series(series_links, comics_links_counter)
        comics_links = join_comics_links()
# If the folder does not exist, create the folder and start the scraping
else:
    print("Folder does not exists.")
    print("Creating folder comics_links_files")
    os.makedirs("comics_links_files")
    print("Starting comics links scraping")
    comics_links_counter = 0
    get_issues_links_from_series(series_links, comics_links_counter)
    comics_links = join_comics_links()

# Check if the comics_info_files folder exists    
if os.path.isdir('comics_info_files'):
    print("Folder comics_info_files already exists. Checking for files")
    # Check if the counter file exists
    if os.path.isfile('comics_info_files/comics_info_counter.p'):
        # If it exists, load the counter
        comics_info_counter = pickle.load(open("comics_info_counter.p"))        
        print("Current count: " + str(comics_info_counter+1) + " of " +
              str(len(comics_links)))
        # If the counter is equal to the quantity of items in the comics_links list
        if comics_info_counter + 1 == len(comics_links):
            print("Scraping already completed. Loading files")            
        # If the counter is not equal to the quantity of items, continue 
		# the scraping
        else:
            print("Scraping initiated but not completed. Continuing...")
            get_all_comics_info(comics_links[comics_info_counter+1:], 
                                comics_info_counter)
    # If the counter does not exists, start the scraping
    else:
        print("Comics info extracting not started.")
        print("Starting comics info scraping")
        comics_info_counter = 0
        get_all_comics_info(comics_links, comics_info_counter)
# If the folder does not exists, create it and start the scraping
else:
    print("Folder does not exists.")
    print("Creating folder comics_info_files")
    os.makedirs("comics_info_files")
    print("Starting comics info scraping")
    comics_info_counter = 0
    get_all_comics_info(comics_links, comics_info_counter)

# Load information from comics and create a DataFrame with it
join_comics_info()
# Load information of all comics
comics_info = pickle.load(open("comics_info_files/all_comics_info.p","rb"))
# Create DataFrame with list of dictionaries
comics_df = pd.DataFrame(comics_info)
# We can create a CSV with it
comics_df.to_csv("comixology_comics_dataset.csv")