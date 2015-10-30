
import xlwt
import re
import datetime
import csv

import gen_functions

class Linewriter:

    def __init__(self, lines):
        self.lines = lines

    def write_xls(self, headers, header_style, outfile):
        if len(self.lines) > 65535:
            num_chunks = int(len(self.lines) / 65534) + 1
            chunks = gen_functions.make_chunks(self.lines, nc = num_chunks)
        else:
            chunks = [self.lines]
        book = xlwt.Workbook(encoding = 'utf-8')
        hs = {}
        for hd in header_style.keys():
            style = xlwt.easyxf(num_format_str = header_style[hd])
            hs[hd] = style
        for sheetno, chunk in enumerate(chunks):
            tabname = 'sheet_' + str(sheetno)
            tab = book.add_sheet(tabname)
            for i, header in enumerate(headers):
                tab.write(0, i, header)
            for i, line in enumerate(chunk):
                i += 1
                for j, column in enumerate(line):
                    if re.search('^http', str(column)) and not ' ' in str(column):
                        url = 'HYPERLINK(\"' + column + '\"; \"' + column + '\")'
                        tab.write(i, j, xlwt.Formula(url))
                    else:
                        xf = hs[headers[j]]
                        if type(column) == str:
                            try:
                                column.encode('latin-1')
                            except:
                                print('corrupt text on line', i, 'skipping')                             
                                continue      
                        tab.write(i, j, column, xf)
        book.save(outfile)

    def write_txt(self, outfile, delimiter = '\t'):
        with open(outfile, 'w', encoding = 'utf-8') as out:
            for line in self.lines:
                out.write(delimiter.join([str(x) for x in line]) + '\n')

    def write_csv(self, outfile):
        """
        CSV writer
        =====
        Function to write rows to a file in csv format

        Parameters
        -----
        rows : list of lists
        outfile : str
            The name of the file to write the rows to
        """
        with open(outfile, 'w', encoding = 'utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for line in self.lines:
                writer.writerow(line)
