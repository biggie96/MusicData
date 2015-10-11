from bs4 import BeautifulSoup #scraping
from urllib2 import urlopen # fetch from url's
import re # requests
# fuzzy searching
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

"""
Looks for lyrics of given song on azlyrics.com
return None if not found
"""
def get_lyrics(song_name, song_artist):
    # lowercase the arguement
    song_name = song_name.lower()
    song_artist = song_artist.lower()

    base_url = 'http://search.azlyrics.com/search.php?q=<name_of_song>+&p=0&w=songs'
    url = base_url.replace('<name_of_song>', song_name)

    # get html page as a BeautifulSoup object
    html = urlopen(url).read()
    soup = BeautifulSoup(html, 'lxml')
    
    # filters whole page to get the results from the search on the page
    def find_results(tag):
        # return true if the tag contains the attributes that song results have
        if(tag.name == 'td' and tag.has_attr('class')):
            return True if('visitedlyr' in tag['class'] and 'text-left' in tag['class']) else False

    results = soup.find_all(find_results) #get search results
    
    for result in results:
        # get name and artist from result
        result_name = str(result.a.b.string).lower()
        result_artist = str(result.a.next_sibling.next_sibling.string).lower()
        
        # use fuzz to find similarity between strings on scale of 0 - 100, 100 being perfect match
        name_similarity = fuzz.ratio(song_name, result_name)
        artist_similarity = fuzz.ratio(song_artist, result_artist)


        ##########DEBUG###########
        """ print 'target: %s, found: %s, ratio: %d' %(song_name, result_name, name_similarity)
        print 'target: %s, found: %s, ratio: %d' %(song_artist, result_artist, artist_similarity) """


        if(name_similarity > 80 and artist_similarity > 80): #its probably the right song
            # grab page with lyrics on it
            lyrics_page = BeautifulSoup(urlopen(result.a['href']).read(), 'lxml')
            divs = lyrics_page.find_all('div')
            
            # find the div with the lyrics
            for div in divs:
                contents = div.contents
                for item in contents: 
                    if(item.string is not None): #there is something in this string, maybe even lyrics!
                        if('Usage of azlyrics.com content by any third-party lyrics provider is prohibited' in item.string):
                            """ Takes the div with the lyrics and removes all the garbage """
                            def cleaner(line):
                                line  = line.encode('utf8') #TODO: figure out why I need to do this
                                
                                # If any of the following flags are in a line, remove that line because it doesn't have lyrics
                                flags = ['azlyrics.com', '<br/>'] 
                                if any(flag in line for flag in flags): 
                                    return False

                                # If the line is just a newline, remove that too
                                if line == '\n':
                                    return False

                                return True

                            lyrics = filter(cleaner, contents)
                            lyrics = map(lambda x: x.encode('utf8'), lyrics) #TODO: figure out why I need to do this

                            verses = [] #holds a list of the verses
                            for line in lyrics:
                                line = filter(lambda x: x.isalpha() or x == ' ', line) #remove characters that aren't letters from a verse
                                verses.append(line)
                                lyrics = '\n'.join(verses)
                            
                            print lyrics
                            return lyrics
                
    return None
