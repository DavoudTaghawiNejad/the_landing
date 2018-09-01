import pickle
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from card_experiment import Directions
from card_experiment import Cards
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, Frame, KeepInFrame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


spacer, width, height = 10 * mm, A4[0] / 3.2, A4[1] / 3.2

client_id = '1042100344500-u207uj45uasn9jfrc9o1ggbkhpfce3nk.apps.googleusercontent.com'
secrete = '9r8Lynt8_0HvJz2NDpftFWYQ'


# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1evhVaog3s5oWQsm2ZdHGqnV1KZ5SbDAwn-eegiZ-UuA'


arrows = ['←', '↓', '→', '↑', '']
with open('card_directions.pp', 'rb') as fp:
        direc_data = Directions(5, genetical_code=pickle.load(fp)).genetical_code

directions = {}
for card_type, cards in direc_data.items():
    directions[card_type] = []
    for d, number in enumerate(cards):
        directions[card_type].extend([arrows[d] for _ in range(number)])
print(directions)
input()


def main():
    store = file.Storage('token.json')
    creds = store.get()  # set to None, for re-authentication
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    c = canvas.Canvas("event.pdf")

    i = 0
    p = (0, 0)
    result = read('EventCards!A2:F42', service)
    for line in result:

        if not line:
            break
        elif not line[0]:
            break
        p = writepdf(line, p, c)


    c.save()


def read(range_name, service):
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                 range=range_name).execute()

    return result.get('values', [])


def prep(text):
    return (text.replace('--', '<br/>-')
            .replace('::', '<br/>')
            .replace('-*-', '</para><para alignment="center">'))


def write_directions(data, frmt, p, canvas):
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleB = ParagraphStyle(name='Bold',
                            parent=styles['Normal'],
                            fontName='Times-Bold',
                            spaceBefore=0,
                            spaceAfter=0,
                            leftIndent=10)
    styleN.spaceBefore = 15
    styleN.spaceAfter = 10

    card_type = data[5]

    try:
        direction = directions[card_type].pop()
    except KeyError:
        tribe = frmt[0]
        direction = directions[(card_type, tribe)].pop()

    if direction == '':
        return

    if card_type == 'TRIBE_EVENT':
        story = [Paragraph('', styleB),
                 Paragraph(direction, styleB)]
    else:
        if direction in ['↓', '↑']:
            story = [Paragraph('', styleB),
                     Paragraph(direction + direction + direction, styleN)]
        elif direction in ['←', '→']:
            story = [Paragraph(' ' + direction, styleB),
                     Paragraph(' ' + direction, styleB),
                     Paragraph(' ' + direction, styleB)]

    canvas.saveState()
    f = Frame(spacer + p[0] * width + width - 40, spacer + p[1] * height, 40, 40, showBoundary=1)
    f.addFromList([KeepInFrame(40, 40, story)], canvas)
    canvas.restoreState()


def writepdf(text, p, canvas):
    try:
        frmts = eval(text[4])
    except (IndexError, SyntaxError):
        if text[4]:
            raise Exception('Error %s' % text[4])
        else:
            frmts = [[]]
    for _ in range(int(text[3])):
        for frmt in frmts:
            styles = getSampleStyleSheet()
            styleN = styles['Normal']
            if text[5] == 'TRIBE':
                styleN.spaceBefore = 0
                styleN.spaceAfter = 0
            else:
                styleN.spaceBefore = 10
                styleN.spaceAfter = 10
            styleH = styles['Heading1']

            title = Paragraph(text[0].format(*frmt), styleH)
            story = []
            story.append(Paragraph(prep(text[1]).format(*frmt), styleN))
            if text[2]:
                story.append(Paragraph('____________________________<br/>', styleN))
                story.append(Paragraph(prep(text[2]).format(*frmt), styleN))

            if text[5] == 'TRIBE':
                canvas.drawImage('tribe.jpg', spacer + p[0] * width, spacer + p[1] * height + 60 * mm, width * 0.8, height * 0.25)
                canvas.drawImage('x.jpg', spacer + p[0] * width + 7.15 * frmt[0] * mm - 6 * mm, spacer + p[1] * height + 71.97 * mm, width * 0.08, height * 0.065)
                canvas.drawImage('x.jpg', spacer + p[0] * width + 7.15 * frmt[1] * mm - 6 * mm, spacer + p[1] * height + 61.5 * mm, width * 0.08, height * 0.065)
                f = Frame(spacer + p[0] * width + width - 20 * mm, spacer + p[1] * height - 20 * mm, width, height, showBoundary=0)
                f.addFromList([Paragraph(str(frmt[2]), style=styleH)], canvas)

                f = Frame(spacer + p[0] * width, spacer + p[1] * height - 35 * mm, width, height, showBoundary=0)
                f.addFromList([KeepInFrame(height, width, story)], canvas)
                story = []
            f = Frame(spacer + p[0] * width, spacer + p[1] * height, width, height, showBoundary=1)
            f.addFromList([title, KeepInFrame(height, width, story)], canvas)




            write_directions(text, frmt, p, canvas)
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
