//define row context menu
var headerMenu = [
    {
        label:"<i class='fas fa-eye-slash'></i> Hide Column",
        action:function(e, column){
            column.hide();
        }
    },
    {
        label:"<i class='fas fa-arrows-alt'></i> Move Column",
        action:function(e, column){
            column.move("col");
        }
    }
]


// File URL
function formatFirstColFile(row, formatterParams){
  let rowId = row.getData().id;
  let cellValue = row.getValue()
  return ("<a class='entity_row' id='row_" + rowId + 
          "' href='" + cellValue + ".html' style='text-align: left;'>"
          + cellValue + "</a>")
}

// anchor based on the row number id
function formatFirstColId(row, formatterParams){
  let rowId = row.getData().id;
  //let rowData = row.getData();
  let cellValue = row.getValue()
  return ("<a class='entity_row' id='row_" + rowId + 
          "' href='#entity_" + rowId + "' style='text-align: left;'>"
          + cellValue + "</a>")
}


function highlightValues(row, formatterParams){
    let rowId = row.getData().id;
    let cellValue = row.getValue()
    return "<a class='" + cellValue + "'>" + cellValue + "</a>"
}

// main function:
function createTable(tag, tabledata, schema, highlight=null,
                    name_mapping={}, layout="fitColumns", 
                    vertical=true, height="100%",
                    firstColWidth="20%",
                    href='id'){
  // add "id" column if missing 
  if (! tabledata[0].hasOwnProperty("id")){
      tabledata.forEach(function(part, index) {
        this[index]['id'] = index;
      }, tabledata); 
  };
  
  // add formatters to the schema
  console.log("href setter: " + href);
  console.log("width: " + firstColWidth);
  console.log("height: " + height);
  if (href == 'id'){
    schema[0]["formatter"] = formatFirstColId;
  } else if (href=='file'){
    schema[0]["formatter"] = formatFirstColFile;
  }
  schema[0]["width"] = firstColWidth;

  schema.forEach(function(part, index) {
    // this[index]['headerMenu'] = headerMenu
    if (vertical) this[index]['headerVertical'] = true;
    if (this[index]['field'] == highlight){
      this[index]["formatter"] = highlightValues;
    };
    if (this[index]['sorter'] == "boolean"){
      this[index]["formatter"] = "tickCross";
      this[index]["editor"] = true;
    };
    if (this[index]['field'] in name_mapping){
       this[index]["title"] = name_mapping[this[index]['field']]
    }
  }, schema); 

  return new Tabulator('#'+tag, {
      height: height, // set height of table to enable virtual DOM
      data:tabledata, //load initial data into table
      layout:layout, //fit columns to width of table (optional)
      columns: schema, //Define Table Columns
      rowClick:function(e, row){ //trigger an alert message when the row is clicked
          document.getElementById("entity_"+row.getData().id).scrollIntoView();   //Even IE6 supports this
          console.log("Row name -- " + row.getData().name + " Clicked!!!!");
      },
  });
}
