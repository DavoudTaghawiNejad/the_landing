from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from fields import generate_farm


client_id = '1042100344500-u207uj45uasn9jfrc9o1ggbkhpfce3nk.apps.googleusercontent.com'
secrete = '9r8Lynt8_0HvJz2NDpftFWYQ'




# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1evhVaog3s5oWQsm2ZdHGqnV1KZ5SbDAwn-eegiZ-UuA'


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    store = file.Storage('token.json')
    creds = store.get()  # set to None, for re-authentication
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    for col in map(chr, range(ord("A"), ord("Q"), 2)):
        for row in range(1, 16, 3):
            range_name = 'fields!%s%i:Q16' % (col, row)
            print(range_name)
            body = {
            'values': generate_farm(25, 30, 500, 50)
            }
            result = service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID, range=range_name,
                valueInputOption="RAW", body=body).execute()
            print('{0} cells updated.'.format(result.get('updatedCells')));


if __name__ == '__main__':
    main()
