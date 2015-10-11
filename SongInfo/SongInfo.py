from bs4 import BeautifulSoup #scraping
from urllib2 import urlopen # fetch from url's
import re # requests

base_url = "http://www.azlyrics.com"

html = urlopen('http://search.azlyrics.com/search.php?q=master%20of+&p=0&w=songs').read() # get html file from url
soup = BeautifulSoup(html, 'lxml') # parse html into data structure

#all results
def find_results(tag):
    if(tag.name == 'td' and tag.has_attr('class')):
        return True if('visitedlyr' in tag['class'] and 'text-left' in tag['class']) else False

results = soup.find_all(find_results)

def cleaner(x):
    x = x.encode('utf8')
    bad_lines = ['azlyrics.com', '<br/>']
    if any(b in x for b in bad_lines):
        return False
    if x == '\n':
        return False

    return True

#get song lyrics
for result in results:
    if(True): #TODO: match against input artist and song
        lyrics_page = BeautifulSoup(urlopen(result.a['href']).read(), 'lxml')
        
        divs = lyrics_page.find_all('div')
        for div in divs:
            contents = div.contents
            for c in contents:
                if(c.string is not None):
                    if 'of azlyrics.com content by any third-party lyrics provider is prohibited' in c.string:
                        raw_text = filter(cleaner, contents)

                        raw_text = map(lambda x: x.encode('utf8'), raw_text)
                        lyrics_list = []
                        for line in raw_text:
                            line = filter(lambda x: x.isalpha() or x == ' ', line)
                            lyrics_list.append(line)

                        lyrics = '\n'.join(lyrics_list)
                        print lyrics
        break;


