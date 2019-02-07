# Documentation : https://dataguide.nlm.nih.gov/eutilities/utilities.html#efetch
# Link to other dbs : https://www.ncbi.nlm.nih.gov/books/NBK25497/table/chapter2.T._entrez_unique_identifiers_ui/?report=objectonly
# esearch query pieces
    # datetype: pdat
    # reldate : n
    # mindate, maxdate : YYYY, YYYY/MM, YYYY/MM/DD
    # sort : default = 'most+recent' ; others are 'journal' 'pub+date' 'most+recent' 'relevance' 'title' 'author'


import pandas as pd
import xml.etree.ElementTree as ET
import requests
import datetime

def pubmed_xml_parse(filename):
    now = datetime.datetime.now()

    ### Parse XML File
    tree_ab = ET.parse(filename)
    root_ab = tree_ab.getroot()

    sql_list = []
    df = pd.DataFrame(columns=['title', 'journal info', 'abstract info', 'mesh dict', 'keyword list', 'artID_list'])
    pub_type_df_list = []
    journal_list_df = []
    abstract_df_list = []
    artID_df_list = []
    keyword_df_list = []
    author_df_list = []
    mesh_df_list = []

    for article in root_ab.findall('./PubmedArticle'):

        uni_mesh_dict = {}
        keyword_list = []
        artID_list = []
        abstract_list = []
        journal_list = []
        pub_type_list = []
        author_list = []

        for PubMedPubDate in article.findall('./PubmedData/History/PubMedPubDate'):
            if PubMedPubDate.get('PubStatus') == 'pubmed':
                year = PubMedPubDate.findall('./Year')[0].text
                month = PubMedPubDate.findall('./Month')[0].text
        art_pubdate = month + '/' + year

        PMID = article.find('./MedlineCitation/PMID').text
        link_str = 'https://www.ncbi.nlm.nih.gov/pubmed/' + PMID

        for title in article.findall('./MedlineCitation/Article/ArticleTitle'):
            title_text = ''.join(title.itertext())

        for type in article.findall('./MedlineCitation/Article/PublicationTypeList/PublicationType'):
            pub_type_list.append(type.text)
            pub_type_df_list.append([PMID, title_text, type.text])

        for journal in article.findall('./MedlineCitation/Article/Journal'):
            try:
                journal_title = journal.find('Title').text
                journal_abbr = journal.find('ISOAbbreviation').text
                journal_issn = journal.find('ISSN').text
                journal_issn_type = journal.find('ISSN').get('IssnType')
                journal_list = [journal_title, journal_issn, journal_issn_type, journal_abbr]
                journal_list_df.append([PMID, journal_title, journal_issn, journal_issn_type, journal_abbr])
            except AttributeError:
                journal_list = [journal_title, None, None, journal_abbr]
                journal_list_df.append([PMID, journal_title, None, None, journal_abbr])

        for abstract in article.findall('./MedlineCitation/Article/Abstract/AbstractText'):
            abstract_type = abstract.get('Label')
            if abstract_type == None:
                abstract_type = 'No Abstract Type Label'
            abstract_text = abstract.text
            abstract_list.append([abstract_type, abstract_text])
            abstract_df_list.append([PMID, title_text, abstract_type, abstract_text])

        for author in article.findall('./MedlineCitation/Article/AuthorList/Author'):
            try:
                first_name = author.findall('./ForeName')[0].text
                last_name = author.findall('./LastName')[0].text
                author_text =  first_name + last_name
            except:
                try:
                    author_text = author.findall('./CollectiveName')[0].text
                except:
                    author_text = 'error'
            author_list.append([author_text])
            author_df_list.append([PMID, title_text, author_text])

        for ArtID in article.findall('./PubmedData/ArticleIdList/ArticleId'):
            ArtID_text = ArtID.text
            ArtID_type = ArtID.get('IdType')
            if ArtID_type != 'pubmed':
                artID_list.append([ArtID_type, ArtID_text])
                artID_df_list.append([PMID, title_text, ArtID_type, ArtID_text])
            else:
                continue

        for MeshHeading in article.findall('./MedlineCitation/MeshHeadingList/MeshHeading'):
            DescName = MeshHeading.findall('./DescriptorName')[0].text
            mesh_df_list.append([PMID, title_text, '-' , DescName])
            QualName_list = []
            for QualName in MeshHeading.findall('./QualifierName'):
                QualName_list.append(QualName.text)
                mesh_df_list.append([PMID, title_text, QualName.text, DescName])
            uni_mesh_dict.update({DescName:QualName_list})

        for keyword_elem in article.findall('./MedlineCitation/KeywordList/Keyword'):
            keyword = keyword_elem.text
            keyword_signif = keyword_elem.get('MajorTopicYN')
            keyword_list.append(keyword)
            keyword_df_list.append([PMID, title_text, keyword])

        ### SQL LIST
        sql_list.append([title_text, PMID, pub_type_list, journal_list, author_list, abstract_list, keyword_list, uni_mesh_dict, art_pubdate, artID_list, link_str])

    ### For book articles
    for book in root_ab.findall('./PubmedBookArticle'):

        uni_mesh_dict = {}
        keyword_list = []
        artID_list = []
        abstract_list = []
        book_list = []
        pub_type_list = []
        author_list = []

        journal_list_df.append([PMID, 'Book', 'Book', 'Book', 'Book'])

        for PubMedPubDate in book.findall('./PubmedBookData/History/PubMedPubDate'):
            if PubMedPubDate.get('PubStatus') == 'pubmed':
                year = PubMedPubDate.findall('./Year')[0].text
                month = PubMedPubDate.findall('./Month')[0].text

        art_pubdate = month + '/' + year
        PMID = book.find('./BookDocument/PMID').text
        link_str = 'https://www.ncbi.nlm.nih.gov/pubmed/' + PMID

        for Book in book.findall('./BookDocument/Book'):
            book_title = Book.find('BookTitle').text
            pub_name = Book.find('Publisher/PublisherName').text
            book_list = [book_title, pub_name]

        for type in book.findall('./BookDocument/PublicationType'):
            pub_type_list.append(type.text)
            pub_type_df_list.append([PMID, book_title, type.text])

        for abstract in book.findall('./BookDocument/Abstract/AbstractText'):
            abstract_type = abstract.get('Label')
            if abstract_type == None:
                abstract_type = ''
            abstract_list.append([abstract_type, abstract.text])
            abstract_df_list.append([PMID, book_title, abstract_type, abstract_text])

        for author in article.findall('./BookDocument/AuthorList/Author'):
            author_text = author.text
            author_list.append([author_text])
            author_df_list.append([PMID, book_title, author_text])

        for ArtID in book.findall('./PubmedBookData/ArticleIdList/ArticleId'):
            ArtID_text = ArtID.text
            ArtID_type = ArtID.get('IdType')
            if ArtID_type != 'pubmed':
                artID_list.append([ArtID_type, ArtID_text])
                artID_df_list.append([PMID, book_title, ArtID_type, ArtID_text])
            else:
                continue

        for keyword_elem in book.findall('./BookDocument/KeywordList/Keyword'):
            keyword = keyword_elem.text
            keyword_list.append(keyword)
            keyword_df_list.append([PMID, book_title, keyword])

        ### SQL LIST ['title', 'pmid', 'pub_type_list', 'journal_info_list', 'author_list', 'abstract_list', 'keyword_list', 'mesh list', 'pubdate', 'artid_list', 'link']
        sql_list.append([book_title, PMID, pub_type_list, 'Book', author_list, abstract_list, keyword_list, 'No mesh for books', art_pubdate, artID_list, link_str])

    ### DF creation

    sql_df = pd.DataFrame(sql_list, columns=['title', 'pmid', 'pub_type_list', 'journal_info_list', 'author_list', 'abstract_list', 'keyword_list', 'mesh list', 'pubdate', 'artid_list', 'link'])

    kw_df = pd.DataFrame(keyword_df_list, columns=['pmid', 'title', 'keyword'])
    artid_df = pd.DataFrame(artID_df_list, columns=['pmid', 'title', 'type', 'ID'])
    abs_df = pd.DataFrame(abstract_df_list, columns=['pmid', 'title', 'type', 'abstract'])

    #pt_df = pd.read_csv(PubTypeDoc, names = ['Pub_type', 'clin_val', 'HEMB_signif'])
    #pt_csv_df = pd.read_csv(PubTypeDoc, names = ['Pub_type', 'clin_val', 'HEMB_signif'])
    #pubt_df = pd.DataFrame(pub_type_df_list, columns=['pmid', 'title', 'pub_type']).merge(pt_csv_df, left_on='pub_type', right_on='Pub_type')
    #pubt_df['clin_val'] = pubt_df['clin_val'].astype('int')
    #pubt_df['HEMB_signif'] = pubt_df['HEMB_signif'].astype('int')

    #pt_csv_df = pd.read_csv(PubTypeDoc, names = ['Pub_type', 'clin_val', 'HEMB_signif'])

    mesh_df = pd.DataFrame(mesh_df_list, columns=['pmid', 'title', 'qual', 'desc'])
    author_df = pd.DataFrame(author_df_list, columns=['pmid', 'title',  'author name'])

    ### Create Excel document and all sheets ###
    # names doc with query from import file, number of results and date
    xlsx_file_name = filename[:-10] + '_' + str(len(sql_df)) + 'res' + '.xlsx'
    writer = pd.ExcelWriter(xlsx_file_name)

    sql_df.to_excel(writer, 'SQL Sheet')
    kw_df.to_excel(writer, 'kw Sheet')
    artid_df.to_excel(writer, 'artID Sheet')
    abs_df.to_excel(writer, 'abstract Sheet')
    #pubt_df.to_excel(writer, 'pub type Sheet')
    mesh_df.to_excel(writer, 'mesh Sheet')

    #workbook = writer.book
    writer.save()


    return_string = '   File name: ' + xlsx_file_name + '\n    Length of result: ' + str(len(sql_list))
    return return_string
