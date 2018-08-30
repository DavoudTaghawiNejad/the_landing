from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import getSampleStyleSheet


spacer, width, height = 20 * mm,  A4[0] / 6, A4[1] / 6


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """

    c = canvas.Canvas("field_markers.pdf")

    p = (0, 0)
    for letter in range(ord('A'), ord('X')):
        p = writepdf(1, False, chr(letter), p, c)


    c.save()


def writepdf(number, effort, letter, p, canvas):
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleN.spaceBefore = 10
    styleN.spaceAfter = 10
    styleH = styles['Heading1']
    styleH.alignment = 1
    styleH.spaceBefore = 26
    styleN.alignment = 1
    story = []
    story.append(Paragraph('<font color="black">%s</font>' % letter, styleH))
    story.append(Paragraph(' ', styleH))
    story.append(Paragraph('<font color="black">%s</font>' % letter, styleH))

    f = Frame(spacer + p[0] * 20 * mm, spacer + p[1] * 20 * mm * 2 + 0.3 * 20 * mm, 20 * mm, 40 * mm, showBoundary=1)
    f.addFromList(story, canvas)


    if p == (4, 4):
        canvas.showPage()
        p = (0, 0)
    else:
        if p[1] == 4:
            p = (p[0] + 1, 0)
        else:
            p = (p[0], p[1] + 1)

    return p




if __name__ == '__main__':
    main()
