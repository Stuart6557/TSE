import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from operator import itemgetter
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
        
        # Create list to store information from the Roster.
        # Each item is a list in the format [UCSD email, row, name, grad date]
        roster = []

        # Iterate through rows in the Roster, adding to the roster list
        r = 1               # Keep track of the row
        for row in roster_values:
            if not row:
                break

            # This condition ensures the header row isn't in the dictionary
            if r > 1:
                roster.append([
                    row[roster_email_col].strip(),
                    str(r), 
                    row[roster_name_col].strip(), 
                    row[roster_grad_date_col].upper().strip()
                ])

            r += 1

        # Sort roster list in alphabetical order by email
        roster = sorted(roster, key=itemgetter(0))

        # Create list to store information from the AH Response Form.
        # Each item is a list in the format [email, row, name, grad date]
        all_hands = []

        # Iterate through rows in the AH Response Form, adding to the 
        # all_hands list
        r = 1               # Keep track of the row
        for row in AH_values:
            if not row:
                break

            if r > 1:
                all_hands.append([
                    row[AH_email_col].strip(),
                    str(r), 
                    row[AH_name_col].strip(), 
                    row[AH_grad_date_col].strip()
                ])

            r += 1

        # Sort all_hands list in alphabetical order by email
        all_hands = sorted(all_hands, key=itemgetter(0))

        # Create the lists that will be outputted
        AH_not_roster = []    # Entries follow format 'AH_name, AH_email, AH_grad_date, AH_row'
        roster_not_AH = []    # Entries follow format 'roster_name, roster_email, 
                              # roster_grad_date, roster_row'
        needs_update = []     # Entries follow format 'roster_name, AH_grad_date, 
                              # roster_grad_date, roster_row'
        no_update_needed = [] # Entries follow format 'roster_name, roster_grad_date'
                              # roster_row'

        # Populate needs_update, no_update_needed, and roster_not_AH
        # by iterating through the roster and all_hands lists
        rosterIdx = 0
        ahIdx = 0

        while rosterIdx < len(roster) and ahIdx < len(all_hands):
          if roster[rosterIdx][0] == all_hands[ahIdx][0]:     # Emails match
            AH_grad_date = all_hands[ahIdx][3].upper()
            # I'm adding this because I realized that people often
            # write something like 'SP 26' instead of 'SP26'
            if len(AH_grad_date) == 5 and AH_grad_date.find(' ') == 2:
                AH_grad_date = AH_grad_date.replace(' ','')

            if roster[rosterIdx][3] == AH_grad_date:
              # Grad dates match
              no_update_needed.append(f'{roster[rosterIdx][2]},{roster[rosterIdx][3]},'
                                      f'{roster[rosterIdx][1]}')
            else:
              # Grad dates don't match
              needs_update.append(f'{roster[rosterIdx][2]},{all_hands[ahIdx][3]},'
                                        f'{roster[rosterIdx][3]},{roster[rosterIdx][1]}')
            
            rosterIdx += 1
            ahIdx += 1
          
          else:
            # Emails don't match, compare to see which email comes first alphabetically
            if roster[rosterIdx][0] < all_hands[ahIdx][0]:
              roster_not_AH.append(f'{roster[rosterIdx][2]},{roster[rosterIdx][0]},'
                                   f'{roster[rosterIdx][3]},{roster[rosterIdx][1]}')
              rosterIdx += 1
            else:
              AH_not_roster.append(f'{all_hands[ahIdx][2]},{all_hands[ahIdx][0]},'
                                   f'{all_hands[ahIdx][3]},{all_hands[ahIdx][1]}')
              ahIdx += 1

        while rosterIdx < len(roster):
          roster_not_AH.append(f'{roster[rosterIdx][2]},{roster[rosterIdx][0]},'
                               f'{roster[rosterIdx][3]},{roster[rosterIdx][1]}')
          rosterIdx += 1

        while ahIdx < len(all_hands):
          AH_not_roster.append(f'{all_hands[ahIdx][2]},{all_hands[ahIdx][0]},'
                               f'{all_hands[ahIdx][3]},{all_hands[ahIdx][1]}')
          ahIdx += 1
        
        # Output results to CSV
        f = open('AH_Results.csv', 'a')

        f.write('1. People on AH Form but not Roster\n')
        if (len(AH_not_roster) != 0):
            f.write('Name,Email,Grad Date on AH Form,Row on AH Form\n')
            AH_not_roster = sorted(AH_not_roster)
            for entry in AH_not_roster:
                f.write(entry + '\n')
        
        f.write('\n2. People on Roster but not AH Form\n')
        if (len(roster_not_AH) != 0):
            f.write('Name,UCSD Email,Grad Date on Roster,Row on Roster\n')
            roster_not_AH = sorted(roster_not_AH)
            for entry in roster_not_AH:
                f.write(entry + '\n')
        
        f.write('\n3. Needs update\n')
        if (len(needs_update) != 0):
            f.write('Name,Grad Date on AH Form,Grad Date on Roster,'
                    'Row on Roster\n')
            needs_update = sorted(needs_update)
            for entry in needs_update:
                f.write(entry + '\n')

        f.write("\n4. Doesn't need update\n")
        if (len(no_update_needed) != 0):
            f.write('Name,Grad Date,Row on Roster\n')
            no_update_needed = sorted(no_update_needed)
            for entry in no_update_needed:
                f.write(entry + '\n')

        f.close()
        
    except HttpError as err:
        print(err)


if __name__ == '__main__':
    main()