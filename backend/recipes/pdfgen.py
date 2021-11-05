from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def shopping_list(canvas, text):
    '''метод создания pdf-файла с помощью библиотеки reportlab'''
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
    canvas.setFont('DejaVuSans', 32)
    canvas.drawString(3 * inch, 10 * inch, 'Что купить')
    canvas.setFont('DejaVuSans', 20)
    textobject = canvas.beginText()
    textobject.setTextOrigin(inch, 9 * inch)
    textobject.textLines(text)
    canvas.drawText(textobject)
