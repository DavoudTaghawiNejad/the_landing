from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import getSampleStyleSheet
from pdf2image import convert_from_path
from reportlab.lib.colors import black, white, red
from copy import copy


def main(spacer, width, height, pagesize):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    name = "effort_cards"
    c = canvas.Canvas(name + '.pdf', pagesize=pagesize)

    p = (0, 0)

    for _ in range(12):
        for i in range(2, 12, 2):
            writepdf(i, p, c)
            p = next_position(p, c)

    c.save()

def next_position(p, canvas):
    if p == (3, 3):
        canvas.showPage()
        p = (0, 0)
    else:
        if p[1] == 3:
            p = (p[0] + 1, 0)
        else:
            p = (p[0], p[1] + 1)

    return p

def writepdf(number, p, canvas):
    styles = getSampleStyleSheet()
    styleB = styles['Heading1']
    styleB.alignment = 1
    styleB.textColor = black
    styleb = styles['Normal']
    styleb.alignment = 1
    styleb.textColor = black

    styleW = copy(styleB)
    styleW.textColor = white
    stylew = copy(styleb)
    stylew.textColor = white
    canvas.setFillColor(black)
    canvas.rect(spacer + p[0] * width, spacer + p[1] * height, width, height / 2, fill=1, stroke=1)
    story = []
    for i in range(3):
        story.append(Paragraph('<br/>', styleB))
    story.append(Paragraph('%i' % number, styleW))
    story.append(Paragraph('Health', stylew))
    f = Frame(spacer + p[0] * width, spacer + p[1] * height, width, height / 2, showBoundary=1)
    f.addFromList(story, canvas)

    story = []
    for i in range(3):
        story.append(Paragraph('<br/>', styleB))
    story.append(Paragraph('%i' % (12 - number), styleB))
    story.append(Paragraph('Effort', styleb))
    f = Frame(spacer + p[0] * width, spacer + p[1] * height + height / 2, width, height / 2, showBoundary=1)
    f.addFromList(story, canvas)





if __name__ == '__main__':
    pagesize = A4
    spacer, width, height = 20 * mm,  A4[0] / 5, A4[1] / 5  # Updated with respect to thin print

    main(spacer, width, height, pagesize)
