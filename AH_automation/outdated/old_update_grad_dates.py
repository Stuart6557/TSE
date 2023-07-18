'''
This is an incomplete script originally intended to update grad dates after AH.

I decided to abandon this file because I wanted to change my approach. Also, 
the code here felt really messy and I didn't like what i wrote.
'''

from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def main():
    # Get info for All Hands form responses
    AH_link = input('Enter the All Hands responses Google Sheets link: ')
    AH_link = AH_link.split('/')

    AH_spreadsheet_id = ''
    for i in range(len(AH_link)):
        if AH_link[i] == 'd':
            AH_spreadsheet_id = AH_link[i+1]
            break
    
    # We only want rows >= 2 since row 1 is the table header
    AH_range = 'Form Responses 1!A2:1000'

    # Get info for Roster
    roster_link = input('Enter the roster Google Sheets link: ')
    roster_link = roster_link.split('/')

    roster_spreadsheet_id = ''
    for i in range(len(roster_link)):
        if roster_link[i] == 'd':
            roster_spreadsheet_id = roster_link[i+1]
            break

    # Need to specify which sheet we're editing
    roster_sheet = input('Enter the specific roster spreadsheet you want to update (ex. 2022-2023): ')
    # Like above, we only want rows >= 2 since row 1 is the table header
    roster_range = roster_sheet + '!A2:1000'

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

        sheet = service.spreadsheets()

        # Call the Sheets API for All Hands spreadsheet
        AH_result = sheet.values().get(spreadsheetId=AH_spreadsheet_id,
                                    range=AH_range).execute()
        AH_values = AH_result.get('values', [])

        if not AH_values:
            print('No All Hands data found.')
            return
        
        # Call the Sheets API for roster spreadsheet
        roster_result = sheet.values().get(spreadsheetId=roster_spreadsheet_id,
                                    range=roster_range).execute()
        roster_values = roster_result.get('values', [])

        if not roster_values:
            print('No All Hands data found.')
            return
        
        # Find which columns in AH responses have names, emails, and grad dates
        # To do this, we need to look at the table header (first row)
        AH_header_range = 'Form Responses 1!A1:1'

        AH_header_result = sheet.values().get(spreadsheetId=AH_spreadsheet_id,
                                    range=AH_header_range).execute()
        AH_header_values = AH_header_result.get('values', [])

        AH_name_col = -1
        AH_email_col = -1
        AH_grad_col = -1

        # Loop through header row to find the columns we are looking for
        for i in range(len(AH_header_values[0])):

            if AH_name_col != -1 and "name" in AH_header_values[0][i].lower():
                AH_name_col = i

            if AH_email_col != -1 and "email" in AH_header_values[0][i].lower():
                AH_email_col = i
            
            if AH_grad_col != -1 and "graduat" in AH_header_values[0][i].lower():
                AH_grad_col = i

            if AH_name_col != -1 and AH_email_col != -1 and AH_grad_col != -1:
                break
        
        # Print error messages and exit if column(s) not found
        if AH_name_col == -1:
            print("make sure you have a name column in the All Hands response form!")
        if AH_email_col == -1:
            print("make sure you have an email column in the All Hands response form!")
        if AH_grad_col == -1:
            print("make sure you have a grad date column in the All Hands response form!")
        if AH_name_col == -1 or AH_email_col == -1 or AH_grad_col == -1:
            return

        # Find which columns in roster have names, emails, and grad dates
        # Like above, we need to look at the table header to do this
        roster_header_range = roster_sheet + '!A1:1'

        roster_header_result = sheet.values().get(spreadsheetId=roster_spreadsheet_id,
                                    range=roster_header_range).execute()
        roster_header_values = roster_header_result.get('values', [])

        roster_name_col = -1
        roster_email_col = -1
        roster_grad_col = -1

        # Loop through header row to find the columns we are looking for
        for i in range(len(roster_header_values[0])):

            if roster_name_col != -1 and "name" in roster_header_values[0][i].lower():
                roster_name_col = i

            if roster_email_col != -1 and "email" in roster_header_values[0][i].lower():
                roster_email_col = i
            
            if roster_grad_col != -1 and "graduat" in roster_header_values[0][i].lower():
                roster_grad_col = i

            if roster_name_col != -1 and roster_email_col != -1 and roster_grad_col != -1:
                break

         # Print error messages and exit if column(s) not found
        if roster_name_col == -1:
            print("make sure you have a name column in the roster!")
        if roster_email_col == -1:
            print("make sure you have an email column in the roster!")
        if roster_grad_col == -1:
            print("make sure you have a grad date column in the roster!")
        if roster_name_col == -1 or roster_email_col == -1 or roster_grad_col == -1:
            return
        
        # Create dictionary to match names and grad dates to emails
        # Dictionary is in the format {"email": ["name", "grad date"]}
        AH_dict = {}

        # Add information to dictionary from roster
        for row in AH_values:
            AH_dict[row[AH_email_col]] = [row[AH_name_col]]

        # Variables to keep track of stats
        same_grad_cnt = 0           # number of people keeping the same grad date
        changed_grad_cnt = 0        # number of people with udpated grad date
        roster_not_AH = 0           # in roster but not AH response
        AH_not_roster = 0           # in AH response but not roster

        for row in AH_values:
            email = row[AH_email_col]

            if email in roster_dict:
                # Compare grad dates to see if they're the same
                if roster_values[]
            else:
                # Member must have typed their email wrong 
                # or entered a non UCSD email

        # print('Name, Major:')
        # for row in values:
        #     # Print columns A and E, which correspond to indices 0 and 4.
        #     print('%s, %s' % (row[0], row[4]))
    except HttpError as err:
        print(err)


if __name__ == '__main__':
    main()