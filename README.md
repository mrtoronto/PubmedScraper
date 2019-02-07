# Pubmed_Scraper

The main script allows you to import an ID list as a .txt file (by entering I) or to enter a query search (by entering Q).  

- By entering I, the user is prompted for a filename. An example ID list has been provided.

- By entering Q, the user is prompted for three more values.  
  1. Query to search. Terms can stand alone or be followed by specific fields.
        - [mesh] searchs mesh keywords
        - [pdat] searchs publication date
            - "cancer[mesh]+AND+2009[pdat]" searches articles about cancer from 2009.
  2. How many results    -- self-explanatory. For larger amounts, adding an API key will increase rate from 3/s to 10/s.
  3. Sort                 -- Default is relevance but other options are there. 
    
    
The first script run will create two .XML files. One has IDs from esearch and the other has abstracts and metadata from efetch.

The second script takes the second XML file and parses it into an excel document. 
