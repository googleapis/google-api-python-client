"""
This is a simple example to fetch values from Google Spreadsheet Using SERVICE ACCOUNT
Uses API v4 with google-auth, requests libraries

Note: Worked with JSON SERVICE ACCOUNT FILE NOT p12
"""

"""
Author : Barathwaja S 
Author Email id : sbarathwaj4@gmail.com
"""

from google.oauth2 import service_account
from googleapiclient import _auth
from apiclient import discovery
from google.auth.transport.requests import AuthorizedSession
import googleapiclient
import httplib2



def getdata():
    credentials = service_account.Credentials.from_service_account_file('YOUR_SERVICE_ACCOUNT_FILE_PATH',
            scopes = ['https://www.googleapis.com/auth/spreadsheets'])

    http =  _auth.authorized_http(credentials)
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
    service = discovery.build('sheets', 'v4', http=http,discoveryServiceUrl=discoveryUrl)

    spreadsheetId = 'YOUR_SPREADSHEET_ID'
    rangeName = 'YOUR_SPREADSHEET_RANGE'

    result = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print(values)




if __name__ == '__main__':
    getdata()
