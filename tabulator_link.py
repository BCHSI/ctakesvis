import json
import pandas as pd

## Achtung: hardcoded JS and CSS locations
boilerplate_data = \
"""
  <script type="text/javascript" src="../tabulator/dist/js/tabulator.min.js"></script>
  <link href="../tabulator/dist/css/tabulator.min.css" rel="stylesheet">
  <script type="text/javascript" src="../table_schema.js"></script>
  <script type="text/javascript">
     var highlight = {highlight};
     var schema = {schema};
     var tabledata = {tabledata};
     var name_mapping = {name_mapping};
     var href = {href};
     createTable("{tag}", tabledata, schema, 
                 highlight=highlight, name_mapping=name_mapping,
                 vertical={vertical}, layout={layout},
                 height={height}, firstColWidth={first_col_width}, 
                 href=href);
  </script>
"""


def _col_types_for_js(typestring):
    if typestring == 'bool':
        return "boolean"
    elif ("float" in typestring) | ("int" in typestring):
        return "number"
    elif ("date" in typestring):
        return "date"
    else:
        return "string"


def get_col_types_for_js(concept_dict_list):
   return (pd.DataFrame(concept_dict_list[:10])
    .dtypes.astype(str).map(_col_types_for_js)
    .to_dict()
    )


def get_schema(concepts, col_order, **kwargs):
    # {title:"Name", field:"name", sorter:"string", width:150, hozAlign:"left", formatter:"progress", sortable:false},
    col_types = get_col_types_for_js(concepts)
    col_list = []
    if col_order is None or len(col_order)==0:
        col_order = col_types.keys()

    for cc in col_order:
        col_list.append({
            "title":  cc.replace('_', ' '),
            "field":  cc,
            "sorter": col_types[cc]
            })
    return col_list


def get_table_js(concepts, col_order = [], name_mapping = {}, 
                 tag = 'concept-table', highlight=None, 
                 vertical=True, layout="fitColumns", 
                 height='100%', href='id',
                 first_col_width="20%", **kwargs):
    "generate javascript table data and code"
    schema = get_schema(concepts=concepts, col_order=col_order)
    schema = json.dumps(schema).replace('}, ', '},\n    ')
    return boilerplate_data.format(
                        tag = tag,
                        highlight = json.dumps(highlight),
                        schema = schema,
                        name_mapping = json.dumps(name_mapping),
                        tabledata=json.dumps(concepts),
                        vertical=json.dumps(vertical),
                        layout=json.dumps(layout),
                        height=json.dumps(height),
                        href = json.dumps(href),
                        first_col_width = json.dumps(first_col_width),
                        **{kk:json.dumps(vv) for kk,vv in kwargs.items()}
                        )

