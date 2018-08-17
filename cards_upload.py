from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from fields import generate_farm


client_id = '1042100344500-u207uj45uasn9jfrc9o1ggbkhpfce3nk.apps.googleusercontent.com'
secrete = '9r8Lynt8_0HvJz2NDpftFWYQ'




# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1KuGu6VHCxT47vsxxbdIq84stg-UPxhtoXCjDjSnjfUg'


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

    cards = []
    i = 0
    with open("The landing cards.txt") as f:
        for l, llint in enumerate(f):
            for line in llint.split('\n\n'):
                if line == '':
                    continue
                if '________________' in line:
                    if i % 2 == 0:
                        cards.append([''])
                    else:
                        cards[-1].append('')
                    i += 1
                cards[-1][-1] += line.replace('________________', '')



    write('Templates!A1:B100', cards, service)

def write(range_name, values, service):
    body = {
        'values': values
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=range_name,
        valueInputOption="RAW", body=body).execute()

    print('{0} cells updated.'.format(result.get('updatedCells')));




if __name__ == '__main__':
    main()
