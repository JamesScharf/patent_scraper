import sys
from bs4 import BeautifulSoup
import requests
from time import sleep
import random
import re 

# just defining some globals here
# appreciate this: https://stackoverflow.com/questions/19891446/python-requests-vs-robots-txt
UAS = ("Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1", 
       "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0",
       "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
       "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
       )

ua = UAS[random.randrange(len(UAS))]

headers = {'user-agent': ua}


def search_urls(term):
    """
    term: the search term you care about.

    Generates a list of urls that we will use to retrieve article data.
    """

    urls = []
    origin = f"http://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&p=1&u=%2Fnetahtml%2FPTO%2Fsearch-bool.html&r=0&f=S&l=50&TERM1={term}&FIELD1=ABTX&co1=AND&TERM2=&FIELD2=&d=PTXT"
    urls.append(origin)

    # now generate the list

    for i in range(1, 450):
        page = f"http://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&u=%2Fnetahtml%2FPTO%2Fsearch-adv.htm&r=0&f=S&l=50&d=PTXT&OS=ABST%2F{term}&RS=ABST%2F{term}&Query=ABST%2F{term}&TD=22401&Srch1={term}.ABTX.&NextList{i}=Next+50+Hits"
        urls.append(page)
    
    return urls


def get_links(page):
    """
    page: url of a search response page

    Extracts the links on the web page
    """

    r = requests.get(page, headers={'user-agent': ua})
    soup = BeautifulSoup(r.text, features="lxml")
    links = set()
    for a in soup.find_all("a", href=lambda x: x and "solar" in x,
                           text=re.compile(r'\d')):

        title = str(a.text).replace(",", "")
        links.add(("http://patft.uspto.gov" + a.get("href"), title))

    return list(links)


def save_patent(page_url, page_title, save_folder):
    """
    save the patent to file.
    """
    r = requests.get(page_url, headers={'user-agent': ua})

    f = open("./" + save_folder + "/" + page_title.replace(" ", "_") + ".html", "w")
    f.write(r.text)
    f.close()



def main():

    args = sys.argv[1:]
    term = args[0]  # our search term
    folder = args[1]  # the folder we're saving the html files in

    urls = search_urls(term)


    # go through each page, save it
    for page_num, u in enumerate(urls):

        print("Extracting links on page #", page_num)
        patent_locs = get_links(u)
        sleep(10)

        # scrape and save each of the patents
        for p_url, title in patent_locs:
            save_patent(p_url, title, folder)
            print("\tScraped: ", p_url)
            sleep(random.randint(7, 13))


if __name__ == '__main__':
    main()