from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, inch
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, Frame, KeepInFrame
from reportlab.lib.styles import getSampleStyleSheet


spacer, width, height = 10 * mm,  A4[0] / 3.5, A4[1] / 3.5

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


    c = canvas.Canvas("event_cards.pdf")

    i = 0
    p = (0, 0)
    while True:
        print(i)
        result = read('EventCards!A{0}:E{0}'.format(i + 2), service)
        if not result:
            break
        p = writepdf(result[0], p, c)
        i += 1




    c.save()


def read(range_name, service):
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                range=range_name).execute()

    return result.get('values', [])

def prep(text):
    return text.replace('-', '<br/>-')

def writepdf(text, p, canvas):
    try:
        frmts = eval(text[4])
    except IndexError:
        frmts = [[]]
    for _ in range(int(text[3])):
        for frmt in frmts:
            styles = getSampleStyleSheet()
            styleN = styles['Normal']
            styleN.spaceBefore = 10
            styleN.spaceAfter = 10
            styleH = styles['Heading1']

            title = Paragraph(text[0], styleH)
            story = []
            story.append(Paragraph(prep(text[1]).format(*frmt), styleN))
            if text[2]:
                story.append(Paragraph('<br/>____________________________<br/>', styleN))
                story.append(Paragraph('<br/>' + prep(text[2]).format(*frmt), styleN))
            canvas.saveState()
            f = Frame(spacer + p[0] * width, spacer + p[1] * height, width, height, showBoundary=1)
            f.addFromList([title, KeepInFrame(height, width, story)], canvas)
            canvas.restoreState()
            if p == (2, 2):
                canvas.showPage()
                p = (0, 0)
            else:
                if p[1] == 2:
                    p = (p[0] + 1, 0)
                else:
                    p = (p[0], p[1] + 1)

    return p




if __name__ == '__main__':
    main()
