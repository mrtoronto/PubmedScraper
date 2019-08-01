import pandas as pd
import xml.etree.ElementTree as ET
import requests
import datetime

def pubmed_xml_parse(filename):

    now = datetime.datetime.now()

    ### Parse XML File using an ElementTree
    tree_ab = ET.parse(filename)
    root_ab = tree_ab.getroot()

    ### These lists will contain lists where each list has data for 1 article
    ### Some will be for their own sheet
    master_df = []
    pub_type_df_list = []
    abstract_df_list = []
    artID_df_list = []
    keyword_df_list = []
    author_df_list = []
    mesh_df_list = []

    journal_list_df = []

    ### For each article in the imported file
    for article in root_ab.findall('./PubmedArticle'):

        ### These will be used to make a row in the `master_df`
        uni_mesh_dict = {}
        keyword_list = []
        artID_list = []
        abstract_list = []
        journal_list = []
        pub_type_list = []
        author_list = []

        ### Iterate through different parts of the articles
        ### Publication Date
        for PubMedPubDate in article.findall('./PubmedData/History/PubMedPubDate'):
            ### Grab data article was published on PubMed
            if PubMedPubDate.get('PubStatus') == 'pubmed':
                year = PubMedPubDate.findall('./Year')[0].text
                month = PubMedPubDate.findall('./Month')[0].text
        art_pubdate = month + '/' + year

        ### Link and PMID
        PMID = article.find('./MedlineCitation/PMID').text
        link_str = 'https://www.ncbi.nlm.nih.gov/pubmed/' + PMID

        ### Article Title
        for title in article.findall('./MedlineCitation/Article/ArticleTitle'):
            title_text = ' '.join(title.itertext())

        ### Publication Types
        for type in article.findall('./MedlineCitation/Article/PublicationTypeList/PublicationType'):
            pub_type_list.append(type.text)
            pub_type_df_list.append([PMID, title_text, type.text])

        ### Journal Information
        for journal in article.findall('./MedlineCitation/Article/Journal'):
            try:
                journal_title = journal.find('Title').text
                journal_abbr = journal.find('ISOAbbreviation').text
                journal_issn = journal.find('ISSN').text
                journal_issn_type = journal.find('ISSN').get('IssnType')
                journal_list = [journal_title, journal_issn, journal_issn_type, journal_abbr]
                journal_list_df.append([PMID, journal_title, journal_issn, journal_issn_type, journal_abbr])
            ### Sometimes there's no ISSN so just in case that's the case :
            except AttributeError:
                journal_list = [journal_title, None, None, journal_abbr]
                journal_list_df.append([PMID, journal_title, None, None, journal_abbr])

        ### Abstracts
        for abstract in article.findall('./MedlineCitation/Article/Abstract/AbstractText'):
            abstract_type = abstract.get('Label')
            if abstract_type == None:
                abstract_type = 'No Abstract Type Label'
            abstract_text = abstract.text
            abstract_list.append([abstract_type, abstract_text])
            abstract_df_list.append([PMID, title_text, abstract_type, abstract_text])

        ### Author information
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

        ### Article IDs and information
        for ArtID in article.findall('./PubmedData/ArticleIdList/ArticleId'):
            ArtID_text = ArtID.text
            ArtID_type = ArtID.get('IdType')
            if ArtID_type != 'pubmed':
                artID_list.append([ArtID_type, ArtID_text])
                artID_df_list.append([PMID, title_text, ArtID_type, ArtID_text])
            else:
                continue

        ### MeSH Headings and Terms
        for MeshHeading in article.findall('./MedlineCitation/MeshHeadingList/MeshHeading'):
            DescName = MeshHeading.findall('./DescriptorName')[0].text
            mesh_df_list.append([PMID, title_text, '-' , DescName])
            QualName_list = []
            for QualName in MeshHeading.findall('./QualifierName'):
                QualName_list.append(QualName.text)
                mesh_df_list.append([PMID, title_text, QualName.text, DescName])
            uni_mesh_dict.update({DescName:QualName_list})

        ### Other keywords attached to the article
        for keyword_elem in article.findall('./MedlineCitation/KeywordList/Keyword'):
            keyword = keyword_elem.text
            keyword_signif = keyword_elem.get('MajorTopicYN')
            keyword_list.append(keyword)
            keyword_df_list.append([PMID, title_text, keyword])

        ### Master List
        master_df.append([title_text, PMID, pub_type_list, journal_list, author_list, abstract_list, keyword_list, uni_mesh_dict, art_pubdate, artID_list, link_str])

    ### For book articles
    for book in root_ab.findall('./PubmedBookArticle'):

        ### These will be used to make a row in the `master_df`
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

        ### Adds row with this article's data to master_df
        master_df.append([book_title, PMID, pub_type_list, 'Book', author_list, abstract_list, keyword_list, 'No mesh for books', art_pubdate, artID_list, link_str])

    ### Master DF creation
    master_df = pd.DataFrame(master_df, columns=['title', 'pmid', 'pub_type_list', 'journal_info_list', 'author_list', 'abstract_list', 'keyword_list', 'mesh list', 'pubdate', 'artid_list', 'link'])

    ### Individual sheets with data
    kw_df = pd.DataFrame(keyword_df_list, columns=['pmid', 'title', 'keyword'])
    artid_df = pd.DataFrame(artID_df_list, columns=['pmid', 'title', 'type', 'ID'])
    abs_df = pd.DataFrame(abstract_df_list, columns=['pmid', 'title', 'type', 'abstract'])
    pubt_df = pd.DataFrame(pub_type_df_list, columns=['pmid', 'title', 'pub_type'])
    mesh_df = pd.DataFrame(mesh_df_list, columns=['pmid', 'title', 'qual', 'desc'])
    author_df = pd.DataFrame(author_df_list, columns=['pmid', 'title',  'author name'])

    ### Create Excel document and all sheets
    xlsx_file_name = filename[:-10] + '_' + str(len(master_df)) + 'res' + '.xlsx'
    writer = pd.ExcelWriter(xlsx_file_name)

    ### Add sheets
    master_df.to_excel(writer, 'Master Table')
    author_df.to_excel(writer, 'Author List (Long)')
    kw_df.to_excel(writer, 'Keyword List (Long)')
    artid_df.to_excel(writer, 'Article ID List (Long)')
    abs_df.to_excel(writer, 'Abstract List (Long)')
    pubt_df.to_excel(writer, 'Pubtype List (Long)')
    mesh_df.to_excel(writer, 'MeSH Keyword List (Long)')

    writer.save()


    return_string = '\tFile name: ' + xlsx_file_name + '\n\tLength of result: ' + str(len(master_df))

    return return_string
