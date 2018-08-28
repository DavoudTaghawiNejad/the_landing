from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, inch
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import getSampleStyleSheet
from pdf2image import convert_from_path

PLAYERS = 8

def main(spacer, width, height, pagesize, jpg):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """

    name = "effort_cards"
    c = canvas.Canvas(name + '.pdf', pagesize=pagesize)

    stories = []
    if jpg:
        stories += [writepdf(2, False)]
        for i in range(2, 12, 2):
            stories += [writepdf(i, True)]
    else:
        stories += [writepdf(2, False) for _ in range(5 * PLAYERS)]  # numbers updated after print
        for _ in range(2 * PLAYERS):  # from 10 to 2 * 8
            for i in range(2, 12, 2):
                stories += [writepdf(i, True)]

    layout(stories, c, jpg)

    c.save()
    if jpg:
        convert_to_jpg(name)


def convert_to_jpg(name):
    pages = convert_from_path(name + '.pdf', dpi=72 * 3)
    for i, page in enumerate(pages):
        page.save(name + '%00i.jpg' % i, 'JPEG', resize=(1125, 2250))


def writepdf(number, effort):
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

    return story


def layout(stories, canvas, jpg):
    p = (0, 0)
    for story in stories:
        canvas.saveState()
        f = Frame(spacer + p[0] * width, spacer + p[1] * height, width, height, showBoundary=int(not(jpg)))
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


if __name__ == '__main__':
    jpg = False
    if jpg:
        pagesize = (675 / 3, 1125  / 3)
        spacer, width, height = 0,  pagesize[0], pagesize[1]
    else:
        pagesize = A4
        spacer, width, height = 20 * mm,  A4[0] / 5, A4[1] / 5  # current print

    main(spacer, width, height, pagesize, jpg)
