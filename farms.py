from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, inch
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, Frame, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import white, red

spacer, width, height = 20 * mm,  A4[0] / 10, A4[1] / 10


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """

    c = canvas.Canvas("farms.pdf")

    pos = (0, 0)

    for i in range(12):
            pos = write_tile(i + 1, pos=pos, canvas=c)

    for i in range(12):
        pos = write_tile(i + 1, pos=pos, canvas=c)

    c.save()

def write_tile(i, pos=None, canvas=None):
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
    canvas.setFillColor(red)
    canvas.rect(spacer + pos[0] * 40 * mm, 5 * mm + pos[1] * 80 * mm, 40 * mm, 80 * mm, fill=1, stroke=1)

    f = Frame(spacer + pos[0] * 40 * mm, pos[1] * 80 * mm - 5 * mm, 40 * mm, 40 * mm, showBoundary=0)
    f.addFromList([Paragraph('%i' % i, styleH)], canvas)

    f = Frame(spacer + pos[0] * 40 * mm, pos[1] * 80 * mm + 35 * mm, 40 * mm, 40 * mm, showBoundary=0)
    f.addFromList([Paragraph('%i' % i, styleH)], canvas)

    canvas.restoreState()
    if pos == (3, 2):
        canvas.showPage()
        pos = (0, 0)
    else:
        if pos[1] == 2:
            pos = (pos[0] + 1, 0)
        else:
            pos = (pos[0], pos[1] + 1)
    return pos


if __name__ == '__main__':
    main()
