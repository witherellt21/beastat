import requests
from bs4 import BeautifulSoup

wunder = requests.get("http://www.basketball-reference.com/players/j/sitemap.xml")
parcala = BeautifulSoup(wunder.content, "xml")


print(parcala)
urls_from_xml = []

loc_tags = parcala.find_all('loc')

for loc in loc_tags:
    urls_from_xml.append(loc.get_text()) 
   
print(urls_from_xml)