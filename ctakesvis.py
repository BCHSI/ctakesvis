#!/usr/bin/env python
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from functools import partial
import json
import re
import pandas as pd
from warnings import warn
import warnings
from tabulator_link import get_table_js, vis_report 
import tempfile
from shutil import copyfile, copy, copytree
from os.path import join as pjoin
import os
import webbrowser
from pathlib import Path

COL_ORDER_CTAKES = ['canon_text',
             'negated',
             'location',
             'domain',
             'hof',
             #'imputed_time',
             #'value',
             'conditional',
             'cui',
             'location_snomed_id',
             'vocab_term',
             'vocab',
            ]

def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
        return '%s:%s: %s:%s\n' % (filename, lineno, category.__name__, message)

warnings.formatwarning = warning_on_one_line


def copy_static(tmdir):
    "copy the `static` directory to the target directory"
    ctakesvis_home = os.path.dirname(os.path.realpath(__file__))
    try:
        copytree(pjoin(ctakesvis_home, 'static'),
                pjoin(tmdir,'static' ))
    except FileExistsError as ee:
        warn(f"static folder already exists in {tmdir}; skipping")
        pass


def _rename_domain(x):
    if x == 'signs_and_symptoms':
        x = 'symptoms'
    return x


def rename_domain_inplace(x):
    x['domain'] = _rename_domain(x['domain'])
    return x


def boolean_from_t_f(entry, columns=['conditional', 'hof', 'negated']):
    for col in columns:
        if col not in entry:
            continue
        entry[col] = (entry[col] == 't')
    return entry


def concat_concepts(results, start='offset_start'):
    """flattens the `.domains` field and adds `concepts.name` field to the list"""
    concepts = []
    for res in results['domains']:
        domain = res['name'].replace(' ', '_')
        concepts_ = res['concepts']
        concepts_ = [boolean_from_t_f(entry) for entry in concepts_]
        [entry.update({'domain': domain}) for entry in concepts_]
        concepts.extend(concepts_)

    concepts = sorted(concepts, key = lambda x: x[start])
    return concepts


def add_css_head(html_, *args, colors=None):
    include = [
    '<meta charset="utf-8"/>',
    '<link rel="stylesheet" href="../styles.css">',
    #'<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>',
    '<script src="../jquery.min.js"></script>',
    '<script src="../scripts.js" type="text/javascript"></script>',
    ]

    include.extend(args)

    if colors:
        include.append(
        f'<link rel="stylesheet" href="../{colors}">'
        )
    include = '\n'.join(include)
    out = (f'''<head>
</head>
{include}
<body>
{html_}
</body>''')
    return out


def modify_column_names(x,
                        columns={'hof': 'hx'}):
    """clean and substitute column names
    Notes:
        hof stands for `history of`, change to `hx`
    """
    if x in columns:
        return columns[x]
    else:
        return x.replace('_', ' ')


def read_extract(fn_json, col_order = []):
    if fn_json.endswith('.json'):
        # UCSF CTAKES JSON
        with open(fn_json) as fh:
            concepts = json.load(fh)

        concepts = concat_concepts(concepts)
        concepts = [rename_domain_inplace(concept) for concept
                    in concepts]

        if len(col_order)==0:
            col_order = concepts[0].keys()
    elif fn_json.endswith('.csv'):
        # Brain database
        concepts = pd.read_csv(fn_json)
        col_order = list(concepts.columns) 
        col_order.remove(args.start)
        col_order.remove(args.end)
        concepts = concepts.to_dict(orient='records')

    if isinstance(concepts, (list, tuple)):
        concepts = sorted(concepts, key = lambda x: x[args.start])
    return concepts, col_order


def read_ucsf_ctakes(fn_report, extract, col_order=[], suffix='.json'):
    """
    INPUT:
    - fn_report -- report file name
    - extract   -- concept extract file or directory name
    - suffix    -- suffix (to assemble extract_file_name if directory name is given)
    OUTPUT:
    input_data is a dictionary with keys:
     - text
     - concepts
     - id : generated from fn_report
     - col_order (optional)
    """
    id = os.path.split(fn_report)[-1].replace('.txt', '')
    with open(fn_report) as fh:
        txt = fh.read()

    if os.path.isdir(extract):
        fn_json = os.path.join(extract, id + suffix)
    else:
        fn_json = extract

    #warn(f'JSON:\t{fn_json}')
    if not os.path.exists(fn_json):
        print(f'missing:\t{fn_json}', )
        raise FileNotFoundError(f'missing:\t{fn_json}')

    concepts, col_order = read_extract(fn_json, col_order=col_order)
    return {'text': txt, 'concepts': concepts, 'col_order': col_order, 'id':id}


def generate_index(dirname):
    "deprecated"
    files = os.listdir(dirname)
    filestr = ''
    for ff in files:
        if not ff.endswith('/index.html'):
            filestr += f'  <li><a href={ff} target="_blank" rel="noopener noreferrer nofollow">{ff}</a></li>\n'

    html_ = f'''<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta content="IE=edge,chrome=1" http-equiv="X-UA-Compatible"><!--  JQUERY  -->
  <title>List of visualizations</title>
</head>
<body>
<h1>Annotated files:</h1>
<ul style="list-style-type:disc;">
{filestr}
</ul>

</body>'''
    return html_


def generate_summary(dirname, summary, fname='name',
                     tag = "contents-table"):
    print(summary)
    cols = set()
    for su in summary:
        cols = cols | su.keys()
    cols = [str(col) for col in cols]
    #summary = pd.DataFrame(summary)
    #cols = [str(col) for col in summary.columns]
    #summary.columns = cols
    cols.remove(fname)
    cols = [fname] + cols
    for su in summary:
        su = {kk: su[kk] for kk in cols if kk in su}
    #summary = summary.reindex(columns=cols)
    concept_table_js = get_table_js(summary, #.to_dict(orient='records'),
                                    tag=tag,
                                    layout=None,#"fitDataStretch",
                                    height=None,
                                    href='file',
                                    first_col_width="{:1.0%}".format(1/len(cols)),
                                    vertical=False,
                                    col_order=cols,
                                    #name_mapping = name_mapping,
                                    #highlight=highlight
                                    )
    table_html = f'''<div id="{tag}"></div>
    '''
    html_ = '<h1>Annotated files:</h1>' + table_html + concept_table_js

    html_ =  add_css_head(html_, colors=None)
    return html_


def visulize_ctakes_mongo(note, concepts, note_key='na',
                          browser=True,
                          copy_package=True,
                          label='canon_text',
                          start='offset_start',
                          end='offset_end'):
    
    for item in concepts:
        if '_id' in item:
            item.pop('_id')
    
    concepts = [rename_domain_inplace(boolean_from_t_f(concept)) for concept
                in concepts]
    
    name_mapping = {"canon_text": "text", "hof": "hx"}
    html_ = vis_report(note, concepts,
                       COL_ORDER_CTAKES,
                       name_mapping=name_mapping,
                       label=label,
                       start=start, end=end,
                       )
    
    tmdir = tempfile.gettempdir()
    html_dir = pjoin(tmdir, 'html')
    path = Path(html_dir, str(note_key) + '.html')
    
    
    os.makedirs(html_dir, exist_ok=True)
    with open(path, 'w') as fh:
        fh.write(html_)
    
    if copy_package:
        copy_static(tmdir)
    
    url = path.absolute().as_uri()
    if browser:
        webbrowser.open(url)
    return url


if __name__ == '__main__':
    from pathlib import Path
    import argparse
    import os
    parser = argparse.ArgumentParser()
    parser.add_argument('report', help='report text file path', type=str)
    parser.add_argument('extract', help='file path of the JSON-formatted CTAKES extract or folder that contains it', 
                        type=str)
    parser.add_argument('--html', help='folder to store an html file', default='html')
    parser.add_argument('-c', '--highlight', help='column name to be highlighted in color', default='domain')
    parser.add_argument('--colorscheme', help='CSS for color scheme', default='colors-ctakes.css')
    parser.add_argument('-l', '--label', help='column name for label', default='canon_text')
    parser.add_argument('-s', '--start', help='column name for start', default='offset_start')
    parser.add_argument('-e', '--end', help='column name for end', default='offset_end')
    parser.add_argument('-x', '--suffix', help='suffix of extract files', default='_combined_output.json')
    parser.add_argument('-b', '--summarize_by',    help='', default=None) #'label')
    parser.add_argument('-f', '--summarize_field', help='', default=None) #'match')
    parser.add_argument('-a', '--agg',   help='', default='last')
    parser.add_argument('--no-ctakes', action="store_false", default=True,
                        dest='ctakes')
    parser.add_argument('--no-browser', action="store_false", default=True,
                        dest='browser')
    args = parser.parse_args()

    parent = os.path.dirname(args.html.rstrip('/').rstrip('\\'))
    if os.path.isdir(parent):
        html_dir = args.html
    else:
        parent = os.getcwd()
        html_dir = os.path.join(parent, args.html)
    os.makedirs(html_dir, exist_ok=True)

    if os.path.isdir(args.report):
        print('`report` argument is a directory')
        reports = os.scandir(args.report)
    elif args.report.lower() in ('na', 'none', '.'):
        reports = []
    else:
        reports = [args.report]
    ###############################################
    # WORK IN PROGRESS to support more input types
    if isinstance(reports, list) and len(reports)==0:
        # everything is in JSON file
        if args.extract.endswith('.jsonl'):
            iterator = jsonl_iter(args.extract)
        elif args.extract.endswith('.json'):
            iterator = json_iter(args.extract)
        for line in iterator:
            text = line['text']
    ###############################################
    # ctakes-specific variables
    if args.ctakes:
        col_order = COL_ORDER_CTAKES
        name_mapping = {"canon_text": "text", "hof": "hx"}
    else:
        col_order = []
        name_mapping = {}

    summary = []
    for report in reports:
        if hasattr(report, 'path'):
            fp_report = report.path
        else:
            fp_report = report

        if not fp_report.endswith('.txt'):
            continue

        # catch file errors and return as warnings
        try:
            input_data = read_ucsf_ctakes(fp_report, args.extract,
                             col_order=col_order, suffix=args.suffix)
            # input_data is a dictionary with keys:
            # - text
            # - concepts
            # - id         -- a unique string
            # - col_order (optional)
        except FileNotFoundError as ee:
            #raise ee
            warn(str(ee))
            continue
        ##############################
        if len(input_data['concepts']) == 0:
            continue

        html_ = vis_report(input_data['text'], input_data['concepts'],
                           input_data['col_order'], 
                           name_mapping=name_mapping,
                           static='./static',
                           **args.__dict__)

        path = os.path.join(html_dir, input_data['id'] + '.html')
        path = Path(path)

        print(f'saving to:\t{path}')
        with open(path, 'w') as fh:
            fh.write(html_)

        # generate summary for summary / index table
        if args.summarize_field is not None:
            concepts = pd.DataFrame(input_data['concepts'])

            by = args.summarize_by
            if by is None:
                by = lambda x: True
            summary_ = (concepts
                        .groupby(by)[args.summarize_field]
                        .agg(args.agg))
            print(summary_)
            summary_ = summary_.to_dict()
        else:
            summary_ = {}
        summary_['name'] = input_data['id']
        summary.append(summary_)

    # copy the static directory
    copy_static(html_dir)

    # write summary / index page
    if os.path.isdir(args.report) and len(summary)>0:
        html_ = generate_summary(html_dir, summary)
        path = os.path.join(html_dir, 'index.html')
        path = Path(path)
        with open(path, 'w') as fh:
            fh.write(html_)

    if args.browser:
        
        url = path.absolute().as_uri()
        webbrowser.open(url)

