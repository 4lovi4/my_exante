from libs import qring
from dateutil import parser
from decimal import Decimal
import csv
from datetime import datetime

symbol1 = 'XAI.INDEX'
symbol2 = 'XAI.EXANTE'

qr = qring.QRing('demo')

try:
    fd = open('/home/exante/xai_d.csv', 'r')
except:
    print('File Error')

cw1 = csv.reader(fd)

qcl1 = []
qcl2 = []
#next(cw)

for row in cw1:
    dline = row[0]
    pline = row[1]
    dts = parser.parse(dline)
    price1 = Decimal(str(round(float(pline))))
    print(price1)
    price2 = Decimal(str(round(float(price1) / 1000, 3)))
    print(price2)
    qc = qring.Candle('quotes', '1day', dts, price1, price1, price1, price1)
    qcl1.append(qc)
    qc = qring.Candle('quotes', '1day', dts, price2, price2, price2, price2)
    qcl2.append(qc)

qr.post(symbol1, qcl1)
qr.post(symbol2, qcl2)
print(qcl1[0], 'Length1 =', len(qcl1))
print(qcl2[len(qcl2) - 1], 'Length1 =', len(qcl2))
