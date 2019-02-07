from search_ids_iovita import get_ids
from pubmed_scraper_notflat import pubmed_xml_parse
import sys

sort, retmax, query, filename = '', '', '', ''

api_key = ""

id_or_query = input('Do you want to use a premade ID list or query? Enter I/Q : \n')

if (id_or_query.lower() == 'i'):
    filename = input('Enter the filename of the ID list.\n')
    search_ids_list = get_ids(have_ids=True, query=None, retmax=None, sort=None, filename=filename, api_key=api_key)
elif (id_or_query.lower() == 'q'):

    query = input('Query? (Use tags like [mesh] and [pdat]; cancer[mesh]+AND+2009[pdat] ) : \n')
    retmax = input('How many results? (Default is 20.) : \n')
    sort = input('Sort order? (Default is relevance) : \n')

    search_ids_list = get_ids(have_ids=False, query=query, retmax=retmax, sort=sort, filename=None, api_key=api_key)
else:
    print('Enter either I or Q!')
    sys.exit()

if sort == '':
    sort = 'relevance'
if retmax == '':
    retmax = 20

ids_list = search_ids_list[0]
query_str = search_ids_list[1]

output = pubmed_xml_parse(ids_list, 'pubtypes_data.csv')

print('\n', output, '\n', '   Sort Order:', sort, '\n')

hold = input('press enter to continue')
