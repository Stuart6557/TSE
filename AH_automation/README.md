## About

In TSE, VP Operations updates grad dates on the Roster after every All Hands (AH), which happens twice a quarter. It's extremely tedious to do this task manually by looking back and forth at the Roster and the AH Response Form, so I (Vivian Liu) created this script to to the boring heavylifting.

Running this file will produce a file named `AH_Results.csv`, which will contain the following lists:

1. People that are on the AH Response Form but aren't on the Roster. Since this script matches people by email, the people on this list probably typed their email wrong or input a non-UCSD email.

2. People that are on the Roster but aren't on the AH Response Form. If this person isn't in list 1, then this person hasn't filled out the AH Form yet. Ask these people through Slack to fill it out.

3. People whose grad dates need to be updated. Update these on the roster. This list excludes people in lists 1 and 2.

4. People whose grad dates don't need to be updated. This list excludes people in lists 1 and 2.

## How to Use This Script

1. Download `AH_script.py`

2. Configure UCSD Google account blah blah

3. Edit env file & how to fill out/where to find information

4. Run the following command

```
python3 AH_script.py
```

If ur running this for the first time, it will ask u for ur Google account. It will generate a `credentials.json` and `token.json`. Ignore these