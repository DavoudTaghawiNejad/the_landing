from random import gauss
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from fields import generate_farm, xround
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, inch
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, Frame, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import white, grey

spacer = 5 * mm
side_length = 6.4 * 10 * mm


client_id = '1042100344500-u207uj45uasn9jfrc9o1ggbkhpfce3nk.apps.googleusercontent.com'
secrete = '9r8Lynt8_0HvJz2NDpftFWYQ'




# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1evhVaog3s5oWQsm2ZdHGqnV1KZ5SbDAwn-eegiZ-UuA'

to_google = False

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

    c = canvas.Canvas("tiles.pdf")

    min_effort_dist_mean = 7
    min_effort_std = 3
    marginal_effectiveness_mean = 2000
    marginal_effectiveness_std = 500

    pos = (0, 0)

    for line in range(24):  # Updated and not yet printed
            values = generate_farm(min_effort_dist_mean, min_effort_std,
                                   marginal_effectiveness_mean, marginal_effectiveness_std)
            conversion_cost = xround(gauss(6, 3), 2)
            write_farm_tiles(values, conversion_cost, 'woods.png', 'field.png', pos, c)
            if to_google:
                range_name = 'fields analysis!B%i:G41' % (line + 1)
                write(range_name,
                      [[list(v) for v in zip(*values)][0] + [list(v) for v in zip(*values)][1]],
                      service,
                      )
            pos = next_position(pos, w=3, h=2, canvas=c)

    for line in range(4):
            write_tile(front_img='wasteland.png', pos=pos, canvas=c)
            pos = next_position(pos, w=3, h=4, canvas=c)


    for line in range(4):
            write_tile(front_img='lake.png', pos=pos, canvas=c)
            pos = next_position(pos, w=3, h=4, canvas=c)


    for line in range(4):
            write_tile(front_img='mountains.png', pos=pos, canvas=c)
            pos = next_position(pos, w=3, h=4, canvas=c)

    for line in range(12):
            write_tile(front_img='exhausted.jpg', pos=pos, canvas=c)
            pos = next_position(pos, w=3, h=4, canvas=c)

    c.save()
    write('fields analysis!N11:P14', [['min_effort_dist_mean', '', min_effort_dist_mean],
                             ['min_effort_std', '', min_effort_std],
                             ['marginal_effectiveness_mean', '', marginal_effectiveness_mean],
                             ['marg_std', '', marginal_effectiveness_std]], service)


def write_farm_tiles(values=None, conversion_cost=None, front_img=None, back_img=None, pos=None, canvas=None):
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleN.spaceBefore = 10
    styleN.spaceAfter = 10
    styleN.textColor = white
    styleH = styles['Heading1']
    styleH.textColor = white
    styleH.alignment = 1
    styleN.alignment = 1


    table = Table(values, style=[('TEXTCOLOR', (0,0), (2,2), white),
                                 ('SIZE', (0,0), (2,2), 14)])

    canvas.drawImage(front_img, spacer + pos[0] * side_length, spacer + pos[1] * 2 * side_length + side_length, side_length, side_length)
    canvas.drawImage(back_img, spacer + pos[0] * side_length, spacer + pos[1] * 2 * side_length, side_length, side_length)
    f = Frame(spacer + pos[0] * side_length, pos[1] * 2 * side_length - 2.5 * spacer, side_length, side_length, showBoundary=0)
    f.addFromList([table], canvas)

    f = Frame(spacer + pos[0] * side_length, pos[1] * 2 * side_length + 45 * mm, side_length, side_length, showBoundary=0)
    f.addFromList([Paragraph('%i' % conversion_cost, styleH)], canvas)


def write_tile(front_img=None, pos=None, canvas=None):
    canvas.drawImage(front_img, spacer + pos[0] * side_length, spacer + pos[1] * side_length, side_length, side_length)


def next_position(pos, w, h, canvas):
    if pos == (w - 1, h - 1):
        canvas.showPage()
        pos = (0, 0)
    else:
        if pos[1] == h - 1:
            pos = (pos[0] + 1, 0)
        else:
            pos = (pos[0], pos[1] + 1)
    return pos



def write(range_name, values, service):
    body = {
        'values': values
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=range_name,
        valueInputOption="RAW", body=body).execute()

    print('{0} cells updated.'.format(result.get('updatedCells')))


if __name__ == '__main__':
    main()
