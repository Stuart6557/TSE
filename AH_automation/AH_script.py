from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from dotenv import load_dotenv

load_dotenv()

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of the roster.
ROSTER_SPREADSHEET_ID = os.getenv('ROSTER_SPREADSHEET_ID')
ROSTER_SHEET = os.getenv('ROSTER_SHEET')
ROSTER_RANGE = ROSTER_SHEET + '!A1:1000'

# The ID and range of the All Hands (AH) Response form.
AH_SPREADSHEET_ID = os.getenv('AH_SPREADSHEET_ID')
AH_RANGE = 'Form Responses 1!A1:1000'

def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=ROSTER_SPREADSHEET_ID,
                                    range=ROSTER_RANGE).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return
        
        # Create file for output, overwriting if it already exists
        f = open('AH_Results.csv', 'w')
        f = open('AH_Results.csv', 'a')
        f.write('test')
        
        r = 0               # keep track of the row each entry is on
        for row in values:
            if not row:
                break

            # Save info from columns A, F, and H
            # roster.append([row[0], row[4], row[5]])
            print('%d, %s, %s, %s' % (r, row[0], row[5], row[6]))

            r += 1
    
    except HttpError as err:
        print(err)


if __name__ == '__main__':
    main()