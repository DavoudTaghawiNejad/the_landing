from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, inch
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import getSampleStyleSheet
from pdf2image import convert_from_path



client_id = '1042100344500-u207uj45uasn9jfrc9o1ggbkhpfce3nk.apps.googleusercontent.com'
secrete = '9r8Lynt8_0HvJz2NDpftFWYQ'




# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1KuGu6VHCxT47vsxxbdIq84stg-UPxhtoXCjDjSnjfUg'


def main(spacer, width, height, pagesize, jpg):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """

    store = file.Storage('token.json')
    creds = store.get()  # set to None, for re-authentication
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    name = "effort_cards"
    c = canvas.Canvas(name + '.pdg', pagesize=pagesize)

    p = (0, 0)

    if jpg:
        p = writepdf(2, False, 1, p, jpg, c)
        times = 1
    else:
        p = writepdf(2, False, 12 * 5, p, jpg, c)
        times = 10

    for i in range(2, 12, 2):
        p = writepdf(i, True, times, p, jpg, c)

    if jpg:
        convert_to_jpg(name)
    c.save()

def convert_to_jpg(name):
    pages = convert_from_path(name + '.pdf', dpi=72 * 5)
    for i, page in enumerate(pages):
        page.save(name + '%00i.jpg' % i, 'JPEG', resize=(1125, 2250))


def writepdf(number, effort, times,  p, jpg, canvas):
    for frmt in range(times):
        styles = getSampleStyleSheet()
        styleN = styles['Normal']
        styleN.spaceBefore = 10
        styleN.spaceAfter = 10
        styleH = styles['Heading1']
        styleH.alignment = 1
        styleN.alignment = 1
        story = []
        for i in range(5):
            story.append(Paragraph('<br/>', styleH))
        if effort:
            story.append(Paragraph('%i' % number, styleH))
            story.append(Paragraph('Harvest %i000 calories' % number, styleN))
        else:
            story.append(Paragraph('<font color="blue">%i</font>' % number, styleH))

        canvas.saveState()
        f = Frame(spacer + p[0] * width, spacer + p[1] * height, width, height, showBoundary=1)
        f.addFromList(story, canvas)
        canvas.restoreState()
        if jpg:
            canvas.showPage()
        elif p == (3, 3):
            canvas.showPage()
            p = (0, 0)
        else:
            if p[1] == 3:
                p = (p[0] + 1, 0)
            else:
                p = (p[0], p[1] + 1)

    return p




if __name__ == '__main__':
    jpg = True
    if jpg:
        pagesize = (675, 1125)
        spacer, width, height = 0,  pagesize[0], pagesize[1]
    else:
        pagesize = A4
        spacer, width, height = 20 * mm,  A4[0] / 5, A4[1] / 5  # Updated with respect to thin print

    main(spacer, width, height, pagesize, jpg)
