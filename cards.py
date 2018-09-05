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
from random import shuffle
import random

spacer, width, height = 10 * mm, A4[0] / 3.2, A4[1] / 3.2

client_id = '1042100344500-u207uj45uasn9jfrc9o1ggbkhpfce3nk.apps.googleusercontent.com'
secrete = '9r8Lynt8_0HvJz2NDpftFWYQ'


# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1evhVaog3s5oWQsm2ZdHGqnV1KZ5SbDAwn-eegiZ-UuA'


arrows = ['←', '↓', '→', '↑', '←←','↓↓', '→→', '↑↑', '']
with open('card_directions.pp', 'rb') as fp:
    genetical_code = pickle.load(fp)
direc_data = Directions(5, genetical_code=genetical_code).genetical_code
print(genetical_code)

random.seed(0)
directions = {}
for card_type, cards in direc_data.items():
    directions[card_type] = []
    for d, number in enumerate(cards):
        directions[card_type].extend([arrows[d] for _ in range(number)])
    shuffle(directions[card_type])

print(directions[('TRIBE_EVENT', 1)])


def main():
    store = file.Storage('token.json')
    creds = store.get()  # set to None, for re-authentication
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    c = canvas.Canvas("event.pdf")

    p = (0, 0)
    result = read('EventCards!A2:F44', service)
    for line in result:

        if not line:
            break
        elif not line[0]:
            break
        p = writepdf(line, p, c)

    for key, val in directions.items():
        assert not val, ('to many enough directions', key, len(val))

    c.save()


def read(range_name, service):
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                 range=range_name).execute()

    return result.get('values', [])


def prep(text):
    return (text.replace('--', '<br/>-')
            .replace('::', '<br/>')
            .replace('-*-', '</para><para alignment="center">'))


def write_directions(data, p, canvas):
    styles = getSampleStyleSheet()

    styleB = ParagraphStyle(name='Bold',
                            parent=styles['Heading1'],
                            fontName='Times-Bold',
                            spaceBefore=0,
                            spaceAfter=0,
                            leftIndent=0)
    styleN = styleB
    styleN.spaceBefore = -10
    styleN.spaceAfter = -10
    styleN.alignment = 1

    card_type = data[5]

    if card_type == 'TRIBE_EVENTS1':
        card_type = ('TRIBE_EVENT', 1)
    if card_type == 'TRIBE_EVENTS2':
        card_type = ('TRIBE_EVENT', 2)

    try:
        print('-', card_type)
        direction = directions[card_type].pop()
    except IndexError:
        raise IndexError(card_type)

    if direction == '':
        return

    if card_type[0] == 'TRIBE_EVENT':
        if direction in ['↓', '↑']:
            story = [Paragraph(direction, styleN)]
        elif direction in ['↓↓', '↑↑']:
            story = [Paragraph(direction[0], styleN),
                     Paragraph(direction[0], styleN)]
        elif direction in ['←', '→', '←←', '→→']:
            story = [Paragraph(direction, styleB)]
        else:
            raise Exception(direction)
    else:
        if direction in ['↓', '↑']:
            story = [Paragraph('', styleB),
                     Paragraph(direction + direction + direction, styleN)]
        elif direction in ['↓↓', '↑↑']:
            story = [Paragraph('', styleB),
                     Paragraph(direction[0] + direction[0] + direction[0], styleN),
                     Paragraph(direction[0] + direction[0] + direction[0], styleN)]
        elif direction in ['←', '→', '←←', '→→']:
            story = [Paragraph(' ' + direction, styleB),
                     Paragraph(' ' + direction, styleB),
                     Paragraph(' ' + direction, styleB)]
        else:
            raise Exception(direction)

    canvas.saveState()
    f = Frame(spacer + p[0] * width + width - 50, spacer + p[1] * height, 50, 50, showBoundary=1)
    f.addFromList([KeepInFrame(40, 40, story)], canvas)
    canvas.restoreState()


def writepdf(text, p, canvas):
    try:
        frmt = eval(text[4])
    except (IndexError, SyntaxError):
        if text[4]:
            raise Exception('Error %s' % text[4])
        else:
            frmt = []
    for _ in range(int(text[3])):
        print(text[5], text[3])
        styles = getSampleStyleSheet()
        styleN = styles['Normal']
        if text[5] == 'TRIBE':
            styleN.spaceBefore = 0
            styleN.spaceAfter = 0
        else:
            styleN.spaceBefore = 10
            styleN.spaceAfter = 10
        styleH = styles['Heading1']

        title = Paragraph(text[0], styleH)
        story = []
        story.append(Paragraph(prep(text[1]), styleN))
        if text[2]:
            story.append(Paragraph('____________________________<br/>', styleN))
            story.append(Paragraph(prep(text[2]), styleN))

        if text[5] == 'TRIBE':
            canvas.drawImage('tribe.jpg', spacer + p[0] * width, spacer + p[1] * height + 60 * mm,
                             width * 0.8, height * 0.25)
            canvas.drawImage('x.jpg', spacer + p[0] * width + 7.15 * frmt[0] * mm - 6 * mm,
                             spacer + p[1] * height + 71.97 * mm, width * 0.08, height * 0.065)
            canvas.drawImage('x.jpg', spacer + p[0] * width + 7.15 * frmt[1] * mm - 6 * mm,
                             spacer + p[1] * height + 61.5 * mm, width * 0.08, height * 0.065)
            f = Frame(spacer + p[0] * width + width - 20 * mm, spacer + p[1] * height - 20 * mm,
                      width, height, showBoundary=0)
            f.addFromList([Paragraph(str(frmt[2]), style=styleH)], canvas)

            f = Frame(spacer + p[0] * width, spacer + p[1] * height - 35 * mm, width, height, showBoundary=0)
            f.addFromList([KeepInFrame(height, width, story)], canvas)
            story = []
        f = Frame(spacer + p[0] * width, spacer + p[1] * height, width, height, showBoundary=1)
        f.addFromList([title, KeepInFrame(height, width, story)], canvas)

        write_directions(text, p, canvas)
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
