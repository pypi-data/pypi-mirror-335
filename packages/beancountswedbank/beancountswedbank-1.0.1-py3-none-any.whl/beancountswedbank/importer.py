#!/usr/bin/env python3
import csv
import re
from itertools import islice

from beangulp import mimetypes
from beangulp.importers import csvbase


class TitleCaseColumn(csvbase.Column):
    def parse(self, value):
        return super().parse(value).title()


class SwedbankCSVReader(csvbase.CSVReader):
    encoding = 'iso-8859-15'
    skiplines = 1

    HEAD = re.compile(r'^\* Transaktion(er|srapport) Period ([0-9]{4}-[0-9]{2}-[0-9]{2}) ?. ?([0-9]{4}-[0-9]{2}-[0-9]{2}) Skapad ([0-9]{4}-[0-9]{2}-[0-9]{2}) ([0-9]{2}:[0-9]{2}) ([+-][0-9]{2}:[0-9]{2}|CES?T)$')
    FIELDS = {'private':
                ['Radnummer',
                 'Clearingnummer',
                 'Kontonummer',
                 'Produkt',
                 'Valuta',
                 'Bokföringsdag',
                 'Transaktionsdag',
                 'Valutadag',
                 'Referens',
                 'Beskrivning',
                 'Belopp',
                 'Bokfört saldo',
                ],
              'company':
                ['Radnr',
                 'Clnr',
                 'Kontonr',
                 'Produkt',
                 'Valuta',
                 'Bokfdag',
                 'Transdag',
                 'Valutadag',
                 'Referens',
                 'Text',
                 'Belopp',
                 'Saldo',
                ]
              }
    KIND = 'private'

    def read(self, filepath):
        columns = {'date': csvbase.Date(5, "%Y-%m-%d"),
                   'amount': csvbase.Amount(10),
                   'currency': csvbase.Column(4),
                   'narration': TitleCaseColumn(9),
                   'payee': TitleCaseColumn(8),
                   'balance': csvbase.Amount(11),
                  }
        with open(filepath, encoding=self.encoding) as fd:
            lines = islice(fd, self.skiplines, None)
            reader = csv.reader(lines)

            headers = {name.strip(): index
                       for index, name in enumerate(next(reader))}
            row = type('Row', (tuple,), {k: property(v.getter(headers))
                                         for k, v in columns.items()})
            for csvrow in reader:
                yield row(csvrow)


class CSVImporter(csvbase.Importer, SwedbankCSVReader):
    """The actual importer protocol for CSV exported reports from Swedbanken online banking"""

    def __init__(self, bankaccount, account, currency, flag='*'):
        super().__init__(account, currency, flag)
        self.bankaccount = bankaccount

    def identify(self, filepath):
        mimetype, _ = mimetypes.guess_type(filepath)
        if mimetype != 'text/csv':
            return False
        with open(filepath, 'rt', encoding=SwedbankCSVReader.encoding) as fd:
            try:
                line = fd.readline()
                if not SwedbankCSVReader.HEAD.match(line):
                    return False
            except:
                pass

            line = fd.readline().strip()
            if not any(line.startswith(','.join(f)) for f in SwedbankCSVReader.FIELDS.values()):
                return False
            reader = csv.reader(fd)
            row = next(reader)
            return self.bankaccount in {row[2], row[3]}

