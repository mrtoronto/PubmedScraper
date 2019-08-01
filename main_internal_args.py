from search_ids import get_article_ids
from pubmed_scraper import pubmed_xml_parse
import sys
import os

id_list_filename = ''

api_key = ""

query_term = 'translational+AND+microbiome'
sort_order = 'relevance'
results = 2000

search_ids_list = get_article_ids(
                have_ids=False,
                query=query_term,
                retmax=results,
                sort=sort_order,
                filename=None,
                api_key=api_key
                )

ids_fetch_file = search_ids_list[0]
query_str = search_ids_list[1]

output = pubmed_xml_parse(ids_fetch_file)

os.unlink(ids_fetch_file)

print('\n', output, '\n', '   Sort Order:', sort_order, '\n')

hold = input('press enter to continue')
