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

    min_effort_dist_mean = 7
    min_effort_std = 3
    marginal_effectiveness_mean = 2000
    marginal_effectiveness_std = 500

    line = 1
    for col in map(chr, range(ord("B"), ord("P"), 2)):
        for row in range(2, 14, 3):
            values = generate_farm(min_effort_dist_mean, min_effort_std, marginal_effectiveness_mean, marginal_effectiveness_std)
            range_name = 'fields!%s%i:Q16' % (col, row)
            write(range_name, values, service)
            line += 1
            range_name = 'fields analysis!B%i:G41' % line
            write(range_name,
                  [[list(v) for v in zip(*values)][0] + [list(v) for v in zip(*values)][1]],
                  service,
                  );

    write('fields!N11:P14', [['min_effort_dist_mean', '', min_effort_dist_mean],
                             ['min_effort_std', '', min_effort_std],
                             ['marginal_effectiveness_mean', '', marginal_effectiveness_mean],
                             ['marg_std', '', marginal_effectiveness_std]], service)

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
