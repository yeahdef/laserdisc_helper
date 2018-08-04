import requests
from requests.utils import quote
import os
import operator
import time
import sys
APIKEY = ""
omdbURL = "http://www.omdbapi.com/?apikey={}&t={}"
def main():
  f = open('movies.csv', 'r')
  for m in f.readlines():
    time.sleep(0.2)
    r = requests.get(omdbURL.format(APIKEY, quote(m.strip())))
    if r.status_code == 200:
      if r.json()['Response'] == "True":
        try:
          print('"{}","{}","{}"'.format(
            r.json()['Title'],
            r.json()['imdbRating'],
            r.json()['Year'][:4]
          ))
        except:
          pass

  f.close()
if __name__ == '__main__':
  main()
