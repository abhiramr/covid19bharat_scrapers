'''
All this work because the indian govt can't have one unified single dashboard! sigh!

What does this file do?

Provided the following parameters
- `state_code`: 2 letter upper or lower case state code for which you want to extract data for
- `url`: the url or the file path of the pdf, image or html
- `type`: can be either 1 of the 3  pdf, image or html for the url that you provided above

this file will do the following

1. extracts parameters passed from command line or if not, takes defaults from `states.yaml` file
2. based on the provided `url` and the `type`
...

'''

#!/usr/bin/python3
import os
import re
import sys
import csv
import yaml
import json
import urllib
import logging
import camelot
import argparse
import html5lib
import requests
import datetime
import pdftotext
from bs4 import BeautifulSoup
from delta_calculator import DeltaCalculator

from statewise_get_data import *

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_cache')
INPUTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_inputs')
STATES_YAML = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'states.yaml')

# read the config file first
with open(STATES_YAML, 'r') as stream:
  try:
    states_all = yaml.safe_load(stream)
  except yaml.YAMLError as exc:
    print(exc)

def fetch_data(st_obj):
  logging.info(st_obj)
  '''
  for a given state object, fetch the details from url

  :state:  object as contained in states.yaml
    {
      name: ...
      state_code: ...
      url: ...
    }
  '''
  fn_map = {
    'ap': ap_get_data,
    'an': an_get_data,
    'ar': ar_get_data,
    'as': as_get_data,
    'br': br_get_data,
    'ch': ch_get_data,
    'ct': ct_get_data,
    'dd': dd_get_data,
    'dh': dh_get_data,
    'dn': dn_get_data,
    'ga': ga_get_data,
    'gj': gj_get_data,
    'hp': hp_get_data,
    'hr': hr_get_data,
    'jh': jh_get_data,
    'jk': jk_get_data,
    'ka': ka_get_data,
    'kl': kl_get_data,
    'la': la_get_data,
    'mh': mh_get_data,
    'ml': ml_get_data,
    'mn': mn_get_data,
    'mp': mp_get_data,
    'mz': mz_get_data,
    'nl': nl_get_data,
    'or': or_get_data,
    'pb': pb_get_data,
    'py': py_get_data,
    'rj': rj_get_data,
    'sk': sk_get_data,
    'tn': tn_get_data,
    'tg': tg_get_data,
    'tr': tr_get_data,
    'up': up_get_data,
    'ut': ut_get_data,
    'wb': wb_get_data
  }

  try:
    return fn_map[st_obj['state_code'].lower()](st_obj)
  except KeyError:
    print('no function definition in fn_map for state code {}'.format(st_obj['state_code']))


if __name__ == '__main__':
  '''
  Example to extract from html dashboard (the url will be taken from automation.yaml file by default)
    $python automation.py --state_code GJ

  Example to overwrite settings already provided in yaml file:
    $python automation.py --state_code AP --type pdf --url 'https://path/to/file.pdf'
  '''
  parser = argparse.ArgumentParser()
  parser.add_argument('--state_code', type=str, nargs='?', default='all', help='provide 2 letter state code, defaults to all')
  parser.add_argument('--type', type=str, choices=['pdf', 'image', 'html'], help='type of url to be specified [pdf, image, html]')
  parser.add_argument('--url', type=str, help='url/path to the image or pdf to be parsed')


  args = parser.parse_args()
  state_code = args.state_code.lower()
  url = args.url
  url_type = args.type
  
  logging.info('scraper', args.url)

  # execute for all states, if state_code not mentioned
  if state_code == 'all':
    for sc in states_all:
      if states_all[sc]['url']:
        print('running {}_get_data'.format(sc))
        fetch_data(states_all[sc])
  else:
    if url_type is not None and url is not None:
      # if there's a url & type provided as args, use that
      states_all[state_code].update({
        'url': url,
        'type': url_type
      })
    # always use default url & type from yaml file
    live_data = fetch_data(states_all[state_code])

  print('*************************************************************************************')
  # TODO - get delta for states
  dc = DeltaCalculator()
  delta = dc.get_state_data_from_site(
    states_all[state_code]['name'],
    live_data,
    'full'
  )
  if delta:
    print(f"Delta processing complete. Written to delta.txt")
  else:
    print(f"Delta unchanged.")
