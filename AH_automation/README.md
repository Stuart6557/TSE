## About

In TSE, VP Operations updates grad dates on the Roster after every All Hands (AH), which happens twice a quarter. It's extremely tedious to do this task manually by looking back and forth at the Roster and the AH Response Form, so I (Vivian Liu) created `AH_script.py` to to the boring heavylifting.

Running this file will produce a file named `AH_Results.csv`, or overwrites it if it already exists, which will contain the following lists:

1. People whose emails are on the AH Response Form but aren't on the Roster. Since this script matches people by email, the people on this list probably typed their email wrong or input a non-UCSD email.

* To find out why I'm matching people by email instead of names, read my rant in AH.java in the outdated folder.

2. People whose emails are on the Roster but aren't on the AH Response Form. If this person isn't in list 1, then this person hasn't filled out the AH Form yet. Ask these people through Slack to fill it out.

3. People whose grad dates need to be updated. Update these on the roster. This list excludes people in lists 1 and 2.

4. People whose grad dates don't need to be updated. This list excludes people in lists 1 and 2.

## How to Use This Script

1. Follow the set up instructions [here](https://developers.google.com/sheets/api/quickstart/python). Make sure you are using your UCSD account to do this.

2. Download `AH_script.py` and place it in the same directory as the `credentials.json` file generated from step 1.

3. Create a file named `.env` following the template in `.env.example`.

* A Google Sheet's spreadsheet ID can be found in its link. For example, the link for [this example spreadsheet](https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit#gid=0) is `https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit#gid=0`. The ID is the string that comes after `d/`, so in this case, it's `"1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"`.

* The name of the specific spreadsheet can be found at the bottom. For example, it's `"Class Data"` on the example spreadsheet.

4. Run the following command. Make sure you are in the directory that `AH_script.py` is in.

```
python3 AH_script.py
```

If you're running this for the first time, you will be asked to choose a Google account. Select your UCSD account. It will then generate a `token.json`. Ignore this file, but don't delete it or it will ask you to choose an account again when you run the script the next time.
