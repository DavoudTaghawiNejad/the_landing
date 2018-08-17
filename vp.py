from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, inch
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import getSampleStyleSheet


spacer, width, height = 20 * mm,  A4[0] / 6, A4[1] / 6


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """

    c = canvas.Canvas("victory_points.pdf")

    p = (0, 0)
    p = writepdf(1, False, 70, p, c)


    c.save()


def writepdf(number, effort, times,  p, canvas):
    for frmt in range(times):
        styles = getSampleStyleSheet()
        styleN = styles['Normal']
        styleN.spaceBefore = 10
        styleN.spaceAfter = 10
        styleH = styles['Heading1']
        styleH.alignment = 1
        styleN.alignment = 1
        story = []
        for i in range(3):
            story.append(Paragraph('<br/>', styleH))
        story.append(Paragraph('<font color="black">%i</font>' % number, styleH))

        canvas.saveState()
        f = Frame(spacer + p[0] * inch, spacer + p[1] * inch + 0.3 * inch, inch, inch, showBoundary=1)
        f.addFromList(story, canvas)
        canvas.restoreState()
        if p == (6, 9):
            canvas.showPage()
            p = (0, 0)
        else:
            if p[1] == 9:
                p = (p[0] + 1, 0)
            else:
                p = (p[0], p[1] + 1)

    return p




if __name__ == '__main__':
    main()
