import pandas as pd
import xml.etree.ElementTree as ET
import requests
import datetime
import csv

def get_article_ids(query, filename, retmax, sort, have_ids=False, api_key=""):

    now = datetime.datetime.now()

    ### If `have_ids` == TRUE, user has a list of IDs saved at `filename` already
    if (have_ids == True):

        epost_base = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/epost.fcgi?id='

        ### Read in the file IDs
        with open(filename, 'r') as f:
            uid_list = list(csv.reader(f))

        ### Create the URL to query
        url_post = epost_base
        for id in uid_list:
            url_post = url_post + id[0] + ','

        ### Get webpage with QK and WebEnv values for fetching articles
        docsearch_resp = requests.get(url_post)

        ### Set to blank because they don't apply with ID list
        ret_max, query_str = '', ''

        ### Build filename for the _fetch .XML file
        file_name_fetch = filename[:-4] + '_idlist_' + now.strftime("%y%m%d_%H%M") + '_fetch.xml'

    ### If have_ids != TRUE, then user wants to query using a search term/phrase
    else:
        query_str = query

        # file_name_search = query + now.strftime("%y%m%d_%H%M") + '_search.xml'
        file_name_fetch = query + '_' + now.strftime("%y-%m-%d-%H%M") + '_fetch.xml'
        esearch_base = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'

        ### More DB options here : https://www.ncbi.nlm.nih.gov/books/NBK3837/
        db = '?db=' + 'pubmed'
        query = '&term=' + query
        hist_api = "&usehistory=y"
        ret_max = '&retmax=' + str(retmax)
        sort = '&sort=' + sort

        ### Get the webpage with the IDs for the articles you'll want to fetch
        url_search = esearch_base + db + query + hist_api + ret_max + sort
        docsearch_resp = requests.get(url_search)



    ### Search the results
    root_search = ET.fromstring(docsearch_resp.content)
    #root_search = tree_search.getroot()
    QK = "&query_key=" + root_search.findall('./QueryKey')[0].text
    WE = "&WebEnv=" + root_search.findall('./WebEnv')[0].text


    ### Get Abstracts with efetch
    efetch_base = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
    rettype_mode = "&rettype=abstract&retmode=xml"

    url_ab = efetch_base + '?db=pubmed' + QK + WE + rettype_mode + ret_max

    docsab_resp = requests.get(url_ab)
    with open(file_name_fetch, 'wb') as f:
        f.write(docsab_resp.content)
    ret_list = [file_name_fetch, query_str]
    return ret_list
