#!/usr/bin/env python
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from functools import partial
import json
import re
import pandas as pd

def _rename_domain(x):
    if x == 'signs_and_symptoms':
        x = 'symptoms'
    return x

def rename_domain_inplace(x):
    x['domain'] = _rename_domain(x['domain'])
    return x


def annotation_json2html(txt, anns,
                   start = 'start',
                   end = 'end',
                   label='label',
                   location='location',):
    if isinstance(anns, (list, tuple)):
        anns = sorted(anns, key = lambda x: x[start])
    prev_end = 0
    prev_start = 0
    html_ = ''
    for ii, ann in enumerate(anns):
        label_ = ann[label]
        if ann['negated']:
            label_ = '&#10060; ' + label_
        tip_text = f'<i>{ii}:</i> {label_}'
        if (location in ann) and (ann[location]):
            location_ = ann[location]
            tip_text += f'<br/><i>in: </i> ' + location_
        tip_text = f'<a href="#row_{ii}" class="ttt" >{tip_text}</a>'

        if 'domain' in ann:
            domain = ann['domain'].replace(' ', '_')

        if (ann[start] > prev_end):
            txt_span = txt[prev_end:ann[start]].replace('\n','<br/>\n')
            html_+= '<span>' + txt_span + '</span>'
            ### moved from prev
            prefix = ''
            word = txt[ann[start]:ann[end]]
        # overlapping cases
        elif (ann[end] > prev_end):
            prefix = ' '
            word = txt[prev_end:ann[end]]
        else:
            prefix = ''
            word = '<sup>&dagger;</sup>'
        #onclick="deleteConcept(this)"
        html_+= (prefix 
                 + f'<div class="ttooltip" id="entity_{ii}">'
                 + f'<span class={domain}>{word}</span>'
                 + f'<span class="tooltiptext" id="tooltiptext_{ii}">'
                 + f'{tip_text}</span></div>')

        prev_start = ann[start]
        prev_end = ann[end]
    return html_


def concat_concepts(results, start='offset_start'):
    """flattens the `.domains` field and adds `concepts.name` field to the list"""
    concepts = []
    for res in results['domains']:
        domain = res['name'].replace(' ', '_')
        concepts_ = res['concepts']
        for entry in concepts_:
            entry['domain'] = domain
            for col in ['conditional', 'hof', 'negated']:
                if col not in entry:
                    continue
                entry[col] = (entry[col] == 't')
        concepts.extend(concepts_)

    concepts = sorted(concepts, key = lambda x: x[start])
    return concepts

def add_css_head(html_):

    out = ('''<head>
  <link rel="stylesheet" href="../styles.css">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
  <script src="../scripts.js" type="text/javascript"></script>
</head>''' +
f'''<body>
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


if __name__ == '__main__':
    import argparse
    import os
    parser = argparse.ArgumentParser()
    parser.add_argument('report', help='report text file path', type=str)
    parser.add_argument('json', help='file path of the JSON-formatted CTAKES extract or folder that contains it', 
                        type=str)
    parser.add_argument('--report-dir', help='report text directory', type=str)
    parser.add_argument('--no-table', action="store_false", default=True,
                        dest='table')
    parser.add_argument('--no-save', action="store_true", default=False)
    parser.add_argument('--no-browser', action="store_false", default=True,
                        dest='browser')
    parser.add_argument('--html-dir', help='folder to store an html file', default='html')
    args = parser.parse_args()
    save = ~ args.no_save


    id = os.path.split(args.report)[-1].replace('.txt', '')
    if os.path.isdir(args.json):
        fn_json = os.path.join(args.json, id + '_combined_output.json')
    else:
        fn_json = args.json

    with open(args.report) as fh:
        txt = fh.read()

    with open(fn_json) as fh:
        concepts = json.load(fh)

    concepts = concat_concepts(concepts)
    concepts = [rename_domain_inplace(concept) for concept  in concepts]

    html_ = annotation_json2html(txt, concepts, start='offset_start',
                                 end='offset_end',
                                 label='canon_text')

    #html_ = '<br/>' + html_
    COL_ORDER=['canon_text',
               'negated',
               'location',
               'domain',
               'hof',
               'imputed_time',
               'value',
               'conditional',
               'cui',
               'location_snomed_id',
               'vocab_term',
               'vocab',
              #  'offset_end',
              #  'offset_start',
              #  'range_text',
              ]
    if args.table:
        pd.set_option('display.max_rows', len(concepts)+1)
        concepts_df = pd.DataFrame(concepts)
        concepts_df = concepts_df[COL_ORDER]

        concepts_df.columns = concepts_df.columns.map(partial(modify_column_names,
                                                      columns={'hof': 'hx',
                                                      'offset_end':'end',
                                                      'offset_start':'start'}))
        
        concepts_df_str = concepts_df.applymap(str)

        # blank out 'na' and 'f'/'False' values
        mask_na = concepts_df.applymap(lambda x: (x=='na') or (x is None))
        concepts_df_str[mask_na] = ''
        concepts_df_str[concepts_df == False] = ''

        for col in ['negated','location','domain', 'past']:
            if col not in concepts_df_str:
                continue
            concepts_df_str[col] = concepts_df_str[col].str.lower()

        drop_cols = concepts_df_str.columns[(concepts_df_str == '').all(0)]
        concepts_df_str.drop(drop_cols, axis=1, inplace=True)
        concept_html = concepts_df_str._repr_html_()

        concept_html = re.sub(r'<tr>\n      <th>(\d+)</th>\n(\s+)<td>(.*)</td>',
                              r'<tr class="entity_row" id="row_\1">\n      '+
                              r'<th id="row_\1">\1</th>\n\2<td><a href="#entity_\1">\3</td>',
                             #r'<tr>\n      <th>(\d+)</th>\n',
                             # r'<tr class="entity_row" id="row_\1">\n      '+
                             # r'<th class="entity_id_cell" >\1</th>\n',
                              concept_html)
        concept_html = concept_html.replace('<tr style="text-align: right;">', '<tr>')
        # re.sub(r"\<th\>(\d+)\<th\>", r"\1,\2", coords)
        # concept_html.replace('<th> name="chapter')
        html_ = (f'<div class="left"><div class="left-sub">{html_}</div></div>\n' +
                 f'<div class="right">{concept_html}</div>')

    html_ = add_css_head(html_)

    if save:
        from pathlib import Path

        parent = os.getcwd()
        os.makedirs(os.path.join(parent, args.html_dir), exist_ok=True)

        path = os.path.join(parent, args.html_dir, f'{id}.html')
        path = Path(path)
        url = path.absolute().as_uri()

        print(f'saving to:\t{path}')
        with open(path, 'w') as fh:
            fh.write(html_)
        
        if args.browser:
            import webbrowser
            webbrowser.open(url)
    else:
        print(html_)
