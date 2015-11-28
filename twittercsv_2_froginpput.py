
import sys
import csv

infile = sys.argv[1]
outfile = sys.argv[2]

fields = ['label', 'doc_id', 'author_id', 'date', 'time', 'authorname', 'text', 'tagged']

csv.field_size_limit(sys.maxsize)
rows = []
try:
    with open(infile, 'r', encoding = 'utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        for line in csv_reader:
            rows.append(line)
except:
    csvfile = open(filename, 'r', encoding = 'utf-8')
    csv_reader = csv.reader(line.replace('\0','') for line in csvfile.readlines())       
    for line in csv_reader:
        rows.append(line)

print(rows[0])
