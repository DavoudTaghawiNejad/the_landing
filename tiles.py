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

spacer, width, height = 20 * mm,  A4[0] / 10, A4[1] / 10


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

    c = canvas.Canvas("tiles.pdf")

    min_effort_dist_mean = 7
    min_effort_std = 3
    marginal_effectiveness_mean = 2000
    marginal_effectiveness_std = 500

    pos = (0, 0)

    for line in range(15):
            values = generate_farm(min_effort_dist_mean, min_effort_std,
                                   marginal_effectiveness_mean, marginal_effectiveness_std)
            conversion_cost = xround(gauss(6, 3), 2)
            pos = write_tile(values, conversion_cost, 'woods.jpg', 'field.png', pos, c)
            range_name = 'fields analysis!B%i:G41' % (line + 1)
            write(range_name,
                  [[list(v) for v in zip(*values)][0] + [list(v) for v in zip(*values)][1]],
                  service,
                  )

    for line in range(10):
            pos = write_tile(front_img='wasteland.png', pos=pos, canvas=c)

    for line in range(5):
            pos = write_tile(front_img='water.jpg', pos=pos, canvas=c)

    for line in range(5):
            pos = write_tile(front_img='mountains.png', pos=pos, canvas=c)

    c.save()
    write('fields analysis!N11:P14', [['min_effort_dist_mean', '', min_effort_dist_mean],
                             ['min_effort_std', '', min_effort_std],
                             ['marginal_effectiveness_mean', '', marginal_effectiveness_mean],
                             ['marg_std', '', marginal_effectiveness_std]], service)


def write_tile(values=None, conversion_cost=None, front_img=None, back_img=None, pos=None, canvas=None):
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleN.spaceBefore = 10
    styleN.spaceAfter = 10
    styleN.textColor = white
    styleH = styles['Heading1']
    styleH.textColor = white
    styleH.alignment = 1
    styleN.alignment = 1



    canvas.saveState()
    canvas.rect(spacer + pos[0] * 47 * mm, 5 * mm + pos[1] * 94 * mm, 47 * mm, 94 * mm, fill=0, stroke=1)
    canvas.drawImage(front_img, spacer + pos[0] * 47 * mm, 5 * mm + pos[1] * 94 * mm + 47 * mm, 47 * mm, 47 * mm)
    if back_img is not None:
        canvas.drawImage(back_img, spacer + pos[0] * 47 * mm, 5 * mm + pos[1] * 94 * mm, 47 * mm, 47 * mm)
    f = Frame(spacer + pos[0] * 47 * mm, pos[1] * 94 * mm - 5 * mm, 47 * mm, 47 * mm, showBoundary=0)
    if values is not None:
        table = Table(values, style=[('TEXTCOLOR', (0,0), (1,2), white),
                                     ('SIZE', (0,0), (1,2), 14)])
        f.addFromList([table], canvas)

    f = Frame(spacer + pos[0] * 47 * mm, pos[1] * 94 * mm + 35 * mm, 47 * mm, 47 * mm, showBoundary=0)
    if conversion_cost is not None:
        f.addFromList([Paragraph('%i' % conversion_cost, styleH)], canvas)

    canvas.restoreState()
    if pos == (2, 2):
        canvas.showPage()
        pos = (0, 0)
    else:
        if pos[1] == 2:
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
