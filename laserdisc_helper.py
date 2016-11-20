from __future__ import print_function
import requests
from requests.utils import quote
import httplib2
import os
import operator
import time
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


def get_credentials():
  """Gets valid user credentials from storage.

  If nothing has been stored, or if the stored credentials are invalid,
  the OAuth2 flow is completed to obtain the new credentials.

  Returns:
      Credentials, the obtained credential.
  """
  home_dir = os.path.expanduser('~')
  credential_dir = os.path.join(home_dir, '.credentials')
  if not os.path.exists(credential_dir):
    os.makedirs(credential_dir)
  credential_path = os.path.join(credential_dir, 'sheets.googleapis.com-python-quickstart.json')

  store = Storage(credential_path)
  credentials = store.get()
  if not credentials or credentials.invalid:
    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
    flow.user_agent = APPLICATION_NAME
    if flags:
      credentials = tools.run_flow(flow, store, flags)
    else: # Needed only for compatibility with Python 2.6
      credentials = tools.run(flow, store)
    print('Storing credentials to ' + credential_path)
  return credentials

def main():
  omdbURL = "http://www.omdbapi.com/?t=%s&y=&r=json&tomatoes=true"
  credentials = get_credentials()
  http = credentials.authorize(httplib2.Http())
  discoveryUrl = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
  service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)
  # note: remember to make spreadsheet public for reading.
  spreadsheetId = '1YKnD_FniAPQAd1XjyzBHb00Bl_L1YYrBNQ7hOYPGBCo'
  rangeName = 'Sheet1!A:A'
  result = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=rangeName).execute()
  values = result.get('values')
  missing = 0
  if not values:
    print('No data found.')
  else:
    f = open('movies.csv', 'wr+')
    for m in values[1:]:
      time.sleep(0.5)
      r = requests.get(omdbURL % quote(m[0]))
      if r.status_code == 200:
        if r.json()['Response'] == "True":
          m[0] = r.json()['Title']
          m.append(r.json()['Year'][:4])
          if r.json()['imdbRating'] != 'N/A':
            m.append(float(r.json()['imdbRating']))
          else:
            m.append("N/A")
          if r.json()['tomatoRating'] != 'N/A':
            m.append(float(r.json()['tomatoRating']))
          else:
            m.append("N/A")
          if r.json()['tomatoUserMeter'] != 'N/A':
            m.append(int(r.json()['tomatoUserMeter']))
          else:
            m.append("N/A")
          if r.json()['tomatoMeter'] != 'N/A':
            m.append(int(r.json()['tomatoMeter']))
          else:
            m.append("N/A")
          if r.json()['Metascore'] != 'N/A':
            m.append(int(r.json()['Metascore']))
          else:
            m.append("N/A")
          print('{:<70}[{}]'.format(r.json()['Title'], r.json()['Year'][:4]))
        else:
          missing += 1
    f.close()
    body = {'values': values}
    result = service.spreadsheets().values().update(
      spreadsheetId=spreadsheetId,
      range="Sheet1!A:G",
      valueInputOption="RAW",
      body=body,
    ).execute()
    print("{} were not found in omdbapi.".format(missing))
if __name__ == '__main__':
  main()
