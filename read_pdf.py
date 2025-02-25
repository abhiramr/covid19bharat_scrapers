import urllib
import csv
import os
import re

import requests
import camelot
import pdftotext


def read_pdf_from_url(opt):
  '''
  :param: opt

  Example `opt` dict sample

  ```
  {
    'name': 'Tamil Nadu',               - full name of the state
    'state_code': 'TN'                  - 2 letter state code in capital letters
    'url': 'http://path/to/file.pdf'    - this is the url to the PDF file
    'type': pdf                         - the type of file link you are passing
    'config': {
      'start_key': 'Districts'          - the word at which the table starts i.e. start reading page
      'end_key': 'Total'                - the word at which the table ends i.e. stop reading page
      'page': '2, 3'                    - pages for the PDF containing the table to be read
    }
  }
  ```


  '''

  # if len(opt['url']) > 0:
  # if url provided is a remote url like (http://)

  if urllib.parse.urlparse(opt['url']).scheme != '':
    #print("--> Requesting download from {} ".format(url))
    r = requests.get(opt['url'], allow_redirects=True, verify=False)
    open(opt['state_code'] + ".pdf", 'wb').write(r.content)
    opt['url'] = os.path.abspath(opt['state_code'] + '.pdf')

  opt['config']['page'] = str(opt['config']['page'])
  if len(opt['config']['page']) > 0:
    pid = ""
    if ',' in opt['config']['page']:
      startPage = int(opt['config']['page'].split(',')[0])
      endPage = int(opt['config']['page'].split(',')[1])
      for pages in range(startPage, endPage + 1, 1):
        print(pages)
        pid = pid + "," + str(pages) if len(pid) > 0 else str(pages)
        print(pid)
    else:
      pid = opt['config']['page']
  else:
    pid = input("Enter district page:")
  print("Running for {} pages".format(pid))

  tables = camelot.read_pdf(opt['url'], strip_text = '\n', pages = pid, split_text = True)
  # for index, table in enumerate(tables):

  stateOutputFile = open(opt['state_code'].lower() + '.csv', 'w')
  # csvWriter = csv.writer(stateOutputFile)
  # arrayToWrite = []

  startedReadingDistricts = False
  for index, table in enumerate(tables):
    tables[index].to_csv(opt['state_code'].lower() + str(index) + '.pdf.txt')
    with open(opt['state_code'].lower() + str(index) + '.pdf.txt', newline='') as stateCSVFile:
      rowReader = csv.reader(stateCSVFile, delimiter=',', quotechar='"')
      for row in rowReader:
        line = "|".join(row)
        line = re.sub("\|+", '|', line)
        if opt['config']['start_key'] in line:
          startedReadingDistricts = True
        if len(opt['config']['end_key']) > 0 and opt['config']['end_key'] in line:
          startedReadingDistricts = False
          continue
        if startedReadingDistricts == False:
          continue

        line = eval(opt['state_code'].lower() + "_format_line")(line.split('|'))
        if line == "\n":
          continue
        print(line, file = stateOutputFile, end = "")

  stateOutputFile.close()

## ------------------------ Custom format line functions for specific states START
def ka_format_line(row):
  district = ""
  modifiedRow = []
  for value in row:
    if len(value) > 0:
      modifiedRow.append(value)

  if type(modifiedRow[0]) == int:
    district = " ".join(re.sub(' +', ' ', modifiedRow[0]).split(' ')[1:])
    modifiedRow.insert(0, 'a')
  else:
    district = re.sub('\*', '', modifiedRow[1])
  print(modifiedRow)

  return district + "," + modifiedRow[3] + "," + modifiedRow[5] + "," + modifiedRow[8] + "\n"

def hr_format_line(row):
  row[1] = re.sub('\*', '', row[1])
  if '[' in row[3]:
    row[3] = row[3].split('[')[0]
  if '[' in row[4]:
    row[4] = row[4].split('[')[0]
  if '[' in row[7]:
    row[7] = row[7].split('[')[0]
  if '[' in row[6]:
    row[6] = row[6].split('[')[0]

  line = row[1] + "," + row[3] + "," + row[4] + "," + str(int(row[6]) + int (row[7])) + "\n"
  return line

def pb_format_line(row):
  return row[1] + "," + row[2] + "," + row[3] + "," + row[4] + "," + row[5] + "\n"

def kl_format_line(row):
  return row[0] + "," + row[1] + "," + row[2] + "\n"

def ap_format_line(row):
  line = row[1] + "," + row[3] + "," + row[5] + "," + row[6] + "\n"
  return line

def wb_format_line(row):
  row[2] = re.sub(',', '', re.sub('\+.*', '', row[2]))
  row[3] = re.sub(',', '', re.sub('\+.*', '', row[3]))
  row[4] = re.sub('\#', '', re.sub(',', '', re.sub('\+.*', '', row[4])))
  row[5] = re.sub(',', '', re.sub('\+.*', '', row[5]))
  line = row[1] + "," + row[2] + "," + row[3] + "," + row[4] + "\n"
  return line

def tn_format_line(row):
  row[1] = re.sub('"', '', re.sub('\+.*', '', row[1]))
  row[2] = re.sub('"', '', re.sub('\+.*', '', row[2]))
  # line = row.replace('"', '').replace('*', '').replace('#', '').replace(',', '').replace('$', '')
  line = row[1] + "," + row[2] + "," + row[3] + "," + row[4] +  "," + row[5] + "\n"
  return line

## ------------------------ Custom format line functions for specific states END
