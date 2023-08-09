# This works but I don't like the algorithm

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
ROSTER_RANGE = os.getenv('ROSTER_SHEET') + '!A1:1000'

# The ID and range of the All Hands (AH) Response Form.
AH_SPREADSHEET_ID = os.getenv('AH_SPREADSHEET_ID')
AH_RANGE = os.getenv('AH_SHEET') + '!A1:1000'

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
        roster_result = sheet.values().get(spreadsheetId=ROSTER_SPREADSHEET_ID,
                                    range=ROSTER_RANGE).execute()
        roster_values = roster_result.get('values', [])
        AH_result = sheet.values().get(spreadsheetId=AH_SPREADSHEET_ID,
                                    range=AH_RANGE).execute()
        AH_values = AH_result.get('values', [])

        if not roster_values:
            print('No data found.')
            return
        
        # Create file for output, overwriting if it already exists
        f = open('AH_Results.csv', 'w')
        
        # Loop through the top row of both spreadsheets to get the 
        # name, email, and grad date columns
        roster_name_col = roster_email_col = roster_grad_date_col = -1
        row = roster_values[0]

        for i in range(len(row)):
            if 'name' in row[i].lower():
                roster_name_col = i
            elif 'ucsd email' in row[i].lower():
                roster_email_col = i
            elif 'grad' in row[i].lower():
                roster_grad_date_col = i
            
            if (roster_name_col != -1 and roster_email_col != -1 and 
                    roster_grad_date_col != -1):
                break       # Break out of loop if all 3 columns are found

        if (roster_name_col == -1 or roster_email_col == -1 or 
                roster_grad_date_col == -1):
            print('Make sure the roster has a name, '
                    'email, and grad date column')
            return

        AH_name_col = AH_email_col = AH_grad_date_col = -1
        row = AH_values[0]

        for i in range(len(row)):
            if 'name' in row[i].lower():
                AH_name_col = i
            elif 'email' in row[i].lower():
                AH_email_col = i
            elif 'grad' in row[i].lower():
                AH_grad_date_col = i

            if (AH_name_col != -1 and AH_email_col != -1 and 
                    AH_grad_date_col != -1):
                break       # Break out of loop if all 3 columns are found

        if AH_name_col == -1 or AH_email_col == -1 or AH_grad_date_col == -1:
            print('Make sure the AH Response Form has a name, '
                    'email, and grad date column')
            return
        
        # Create dictionary to store information from the Roster.
        # Key is UCSD email. Value is [row, name, grad date]
        roster = {}

        # Iterate through rows in the Roster, adding to the roster dictionary
        r = 1               # Keep track of the row
        for row in roster_values:
            if not row:
                break

            # This condition ensures the header row isn't in the dictionary
            if r > 1:
                roster[row[roster_email_col].strip()] = [
                    str(r), 
                    row[roster_name_col].strip(), 
                    row[roster_grad_date_col].upper().strip()
                ]

            r += 1

        # Create dictionary to store information from the AH Response Form.
        # Key is email. Value is [row, name, grad date]
        all_hands = {}

        # Iterate through rows in the AH Response Form, adding to the 
        # all_hands dictionary
        r = 1               # Keep track of the row
        for row in AH_values:
            if not row:
                break

            if r > 1:
                all_hands[row[AH_email_col].strip()] = [
                    str(r), 
                    row[AH_name_col].strip(), 
                    row[AH_grad_date_col].upper().strip()
                ]

            r += 1

        # Create the lists that will be outputted
        AH_not_roster = []
        roster_not_AH = []
        needs_update = []
        no_update_needed = []

        # Populate needs_update, no_update_needed, and roster_not_AH
        # by iterating through the roster dictionary
        for roster_email in roster:
            roster_row = roster[roster_email][0]
            roster_name = roster[roster_email][1]
            roster_grad_date = roster[roster_email][2].upper()

            # Case 1: this email doesn't exist in AH Response Form
            if roster_email not in all_hands:
                roster_not_AH.append(f'{roster_name},{roster_email}')

            else:
                AH_grad_date = all_hands[roster_email][2].upper()
                # I'm adding this because I realized that people often
                # write something like 'SP 26' instead of 'SP26'
                if len(AH_grad_date) == 5 and AH_grad_date.find(' ') == 2:
                    AH_grad_date = AH_grad_date.replace(' ','')
                
                # Case 2: grad dates match
                if roster_grad_date == AH_grad_date:
                    no_update_needed.append(f'{roster_name},{roster_grad_date}')
                
                # Case 3: grad dates don't match
                else:
                    needs_update.append(f'{roster_name},{roster_row},'
                                        f'{roster_grad_date},{AH_grad_date}')
 
        # Populate AH_not_roster by iterating through the all_hands dictionary
        for AH_email in all_hands:
            if AH_email not in roster:
                AH_row = all_hands[AH_email][0]
                AH_name = all_hands[AH_email][1]
                AH_not_roster.append(f'{AH_name},{AH_row},{AH_email}')

        # Output results in alphabetical order to CSV
        f = open('AH_Results.csv', 'a')

        f.write('1. People whose emails are on the AH '
                'Response Form but not on the Roster\n')
        if (len(AH_not_roster) != 0):
            f.write('Name, Row on AH Response Form, Email on AH Response Form\n')
            AH_not_roster = sorted(AH_not_roster)
            for entry in AH_not_roster:
                f.write(entry + '\n')
        
        f.write('\n2. People whose emails are on the Roster '
                'but not on the AH Response Form\n')
        if (len(roster_not_AH) != 0):
            f.write('Name, UCSD Email\n')
            roster_not_AH = sorted(roster_not_AH)
            for entry in roster_not_AH:
                f.write(entry + '\n')
        
        f.write('\n3. People whose grad dates need to be updated\n')
        if (len(needs_update) != 0):
            f.write('Name, Row on Roster, Grad Date on Roster, '
                    'Grad Date on AH Form\n')
            needs_update = sorted(needs_update)
            for entry in needs_update:
                f.write(entry + '\n')

        f.write("\n4. People whose grad dates don't need to be updated\n")
        if (len(no_update_needed) != 0):
            f.write('Name, Grad Date\n')
            no_update_needed = sorted(no_update_needed)
            for entry in no_update_needed:
                f.write(entry + '\n')
        
    except HttpError as err:
        print(err)


if __name__ == '__main__':
    main()