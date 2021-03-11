from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import sys
import os
import requests
import dateutil.parser

def writeDefaultFormat(mediaItem, mediaName):
  home = os.path.expanduser("~")
  base = os.path.join(home, "/downloads/gpbackup/")
  
  if not os.path.exists(base):
    os.makedirs(base)
  f = open(base + mediaName, "wb")
  f.write(mediaItem.content)
  f.close()
  
def writeYearFormat(mediaItem, mediaName, creationTime):
  home = os.path.expanduser("~")
  dt = dateutil.parser.isoparse(creationTime)
  base = os.path.join(home, "downloads/gpbackup", str(dt.year))

  if not os.path.exists(base):
    os.makedirs(base)
  f = open(base + "/" + mediaName, "wb")
  f.write(mediaItem.content)
  f.close()

def backupAllMediaItems(gp, pageToken, o):
  while pageToken != '':
    pageToken = '' if pageToken == 'default' else pageToken
    res = gp.mediaItems().list(pageSize=100, pageToken=pageToken).execute()
    for item in res['mediaItems']:
      mediaName = item['filename']
      mimeType = item['mimeType']
      mediaUrl = item['baseUrl']
      mediaMeta = item['mediaMetadata']

      if 'video' in mimeType:
        mediaUrl += "=dv"
      elif 'image' in mimeType:
        mediaUrl += "=d"
      else:
        print("Unknown mime type found: " + mimeType)
        print(item + '\n')
        continue

      mediaItem = requests.get(mediaUrl)
      
      if o == 1:
        writeDefaultFormat(mediaItem, mediaName)
      elif o == 2:
        writeYearFormat(mediaItem, mediaName, mediaMeta['creationTime'])

    pageToken = res.get('nextPageToken', '')

def main():
  if len(sys.argv) == 1:
    credFullPath = "credentials.json"
  else:
    credFullPath = sys.argv[1]

  flow = InstalledAppFlow.from_client_secrets_file(
    credFullPath,
    scopes=['https://www.googleapis.com/auth/photoslibrary'])

  credentials = flow.run_local_server(host='localhost',
    port=8080, 
    authorization_prompt_message='Please visit this URL: {url}', 
    success_message='The auth flow is complete; you may close this window.',
    open_browser=True)

  gp = build('photoslibrary', 'v1', credentials=credentials)
  pageToken = 'default'

  print("1. Backup")
  o = int(input("Enter your input: "))

  if o == 1:
    print("1. Default : All in one directory")
    print("2. Year")
    o = int(input("Enter formatting: "))
    backupAllMediaItems(gp, pageToken, o)

if __name__=="__main__": 
    main() 
