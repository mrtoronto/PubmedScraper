from search_ids import get_ids
from pubmed_scraper_notflat import pubmed_xml_parse
import sys
import os
#import getopt
#import argparse

#sort, retmax, query, filename = '', '', '', ''

api_key = ""

query = 'translational+AND+microbiome'
sort = 'relevance'
retmax = 20

search_ids_list = get_ids(have_ids=False, query=query, retmax=retmax, sort=sort, filename=None, api_key=api_key)


ids_fetch_file = search_ids_list[0]
query_str = search_ids_list[1]

output = pubmed_xml_parse(ids_fetch_file)

os.unlink(ids_fetch_file)

print('\n', output, '\n', '   Sort Order:', sort, '\n')

hold = input('press enter to continue')
