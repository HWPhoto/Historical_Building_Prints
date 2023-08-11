"""
******************************
Historic Building Prints & Images to PDF
H Wesley Phillips 24 January 2023
Last update: 27 January 2023
******************************
"""

import json
import os
import sqlite3
import PIL
from PIL import Image, ImageOps, ImageEnhance
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, Paragraph, \
    PageBreak, PageTemplate, Spacer, Image
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import sys
import io

stdoutOrigin=sys.stdout
sys.stdout = open("log.txt", "w")

################################################################################
defaultPageSize = letter
registerFont(TTFont('LBrite', 'LBRITE.ttf'))
registerFont(TTFont('Times New Roman', 'TIMES.ttf'))
registerFont(TTFont('Arial', 'ARIAL.ttf'))
registerFont(TTFont('ArialBD', 'ARIALBD.ttf'))
registerFont(TTFont('Bahn', 'BAHNSCHRIFT.ttf'))
registerFont(TTFont('BahnB', 'BAHNSCHRIFT.ttf'))
registerFont(TTFont('FramD', 'FRAMD.ttf'))
################################################################################
doc = BaseDocTemplate('South Carolina Historic Building Plans and Images.pdf', showBoundary=0)
doc.pagesize = letter
doc.topMargin = 0.5 * inch
doc.bottomMargin = 0.5 * inch
doc.leftMargin = 0.75 * inch
style = getSampleStyleSheet()
style.add(ParagraphStyle(name='Description', fontName='LBrite', fontSize=8))
style.add(ParagraphStyle(name='Listing', fontName='LBrite', fontSize=8))
style.add(ParagraphStyle(name='Record', fontName='FramD', fontSize=8,
                         borderWidth=1, borderColor='#000000',
                         borderPadding=(2, 2, 2, 2), backColor='#FFFF00'))
style.add(ParagraphStyle(name='Heading4A', fontName='FramD', fontSize=14))
style.add(ParagraphStyle(name='Heading3A', fontName='FramD', fontSize=12,
                         leading=16))
style.add(ParagraphStyle(name='Heading2A', fontName='FramD', fontSize=10))
style.add(ParagraphStyle(name='Heading1A', fontName='FramD', fontSize=14,
                         borderWidth=1, borderColor='#000000',
                         borderPadding=(10, 2, 10, 2), backColor='lightgreen'))
style.add(ParagraphStyle(name='Sindex', fontName='LBrite', fontSize=8))
style.add(ParagraphStyle(name='Heading3B', fontName='Times New Roman',
                         fontSize=18, alignment=1))
style.add(ParagraphStyle(name='Heading3C', fontName='Times New Roman',
                         fontSize=40, alignment=1))
################################################################################
def foot1(canvas, doc):
    print('here')
    canvas.saveState()
    canvas.setFont('Times New Roman', 9)
    canvas.drawString(7.5 * inch, 0.25 * inch, "Page %d" % doc.page)
    canvas.restoreState()
################################################################################
def foot2(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times New Roman', 9)
    canvas.drawString(7.0 * inch, 0.25 * inch, "Page %d" % doc.page)
    canvas.restoreState()
################################################################################
# normal frame as for SimpleFlowDocument
frameT = Frame(1.0 * inch, 0.5 * inch, 6.75 * inch, 10 * inch, id='normal',
               showBoundary=0)
frameTB = Frame(0.75 * inch, .5 * inch, 6.75 * inch, 10 * inch, id='normal',
                showBoundary=0)
frameBlank = Frame(0.5 * inch, .5 * inch, 7.5 * inch, 10.0 * inch, id='normal2',
                   showBoundary=0)
# Two Columns
frame1 = Frame(0.75 * inch, 0.5 * inch, 3.25 * inch, 10 * inch, id='col1',
               showBoundary=1)
frame2 = Frame(4.25 * inch, 0.5 * inch, 3.25 * inch, 10 * inch, id='col2',
               showBoundary=1)
frameP = Frame(0.75 * inch, 0.5 * inch, 7.5 * inch, 10 * inch, id='photo',
               showBoundary=0)
################################################################################
wDir = os.getcwd()
# Get Images if they exist
dbx = 'C:/Database/SC_Places.db'
con = sqlite3.connect(dbx, detect_types=sqlite3.PARSE_DECLTYPES |
                                        sqlite3.PARSE_COLNAMES)
cur = con.cursor()
query = "SELECT Id, Photo FROM SC_Places_Prints"
rows = cur.execute(query).fetchall()
images = []
for row in rows:
    images.append(row[1])
# Set up data requested
query = "SELECT Id,Name, State, County FROM SC_Places_Prints ORDER BY Sequence ASC"
result = cur.execute(query).fetchall()
if result == '':
    exit()
# Convert to json
items = [dict(zip([key[0] for key in cur.description], row)) for row in result]
data = json.dumps({'SC_Places_Prints_Json': items})
res = json.loads(data)
# Build pages
Story = []
a = Image("HistoricBuildingsPlans.jpg")
a._restrictSize(7.5 * inch, 8 * inch)
Story.append(a)
Story.append(PageBreak())
Story.append(PageBreak())
Story.append(PageBreak())
Story.append(PageBreak())
for _Id in res['SC_Places_Prints_Json']:
    i = _Id['Id'] - 1
    if images[i] is not None and images[i] != 'NULL':
        print(i)
        data = images[i]
        pilimg = PIL.Image.open(io.BytesIO(data))
        try:
            pilimg = pilimg.convert('L')
            pilimg = ImageOps.autocontrast(pilimg, cutoff = 2)
            enhancer = ImageEnhance.Brightness(pilimg)
            pilimg = enhancer.enhance(1.05)
            pilimg = ImageOps.expand(pilimg, border=7)
            pwidth, pheight = pilimg.size
            if pwidth > (pheight+10):
                #Story.append(Spacer(1, 125))
                pilimg = pilimg.rotate(90, PIL.Image.NEAREST, expand = True)
            pilimg.save('temp/' + str(i) + "temp2.png")
        except:
            print('File Error')
            quit()
        try:
            a = Image('temp/' + str(i) + "temp2.png")
            a._restrictSize(7 * inch, 8.0 * inch)
            Story.append(a)
        except:
            print('Image error')
            quit()
        Story.append(Spacer(1, 3))
        ptext = 'Name: %s' % _Id['Name']
        Story.append(Paragraph(ptext, style['Heading3B']))
        Story.append(Spacer(1, 10))
        ptext = '%s, %s' % (_Id['County'], _Id['State'])
        Story.append(Paragraph(ptext, style['Heading3B']))
        Story.append(PageBreak())
Story.append(PageBreak())
Story.append(PageBreak())
Story.append(PageBreak())
doc.addPageTemplates([PageTemplate(id='OneCol', frames=frameT),
                      PageTemplate(id='TwoCol', frames=[frame1, frame2],
                                   onPage=foot2),
                      PageTemplate(id='Blank', frames=frameBlank),
                      PageTemplate(id='Photo', frames=frameP)])
##############################################################################
# start the construction of the pdf
doc.build(Story)
##############################################################################
import glob

files = glob.glob('temp/*.png', recursive=True)

for f in files:
    try:
        os.remove(f)
    except OSError as e:
        print("Error: %s : %s" % (f, e.strerror))
##############################################################################
quit()