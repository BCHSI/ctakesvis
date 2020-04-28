// import {fixedHeaderTable} from './jquery.fixedheadertable.min.js';

function highlightConceptColor(elem) {
      elem.style.backgroundColor = '#DDDDDD';
      console.log(elem.id);
};

function changeColorTable(row_id){
    [].forEach.call( document.getElementsByClassName("entity_row"),
    function(row){
        row.style.backgroundColor = '';
        row.style.color='';
    });
    var row = document.getElementById(row_id);
    row.style.backgroundColor = '#DDDDDD';
    };


function highlightConceptText(row_id){
    [].forEach.call( document.getElementsByClassName("ttooltip"),
    function(row){
        row.style.border = '';
    });
    console.log('row_id ', row_id); 
    var row = document.getElementById(row_id);
    row.style.border =  "double #000000"
}

function highlightConceptEverywhere(){
    console.log("id:" + this.id);
    var id_ = this.id.split("_")[1];
    // call to global var `tbl` (some rows are hidden)
    tbl.scrollToRow(parseInt(id_), "center", false); 
    var row_id = "row_" + id_;
    changeColorTable(row_id);
    var row_id = "entity_" + id_;
    highlightConceptText(row_id);
};

$(document).on('click', ".tooltiptext", highlightConceptEverywhere);
// $(document).on('click', ".tooltiptext", changeColorTable);
$(document).on('click', ".entity_row", highlightConceptEverywhere);

$(window).load(function(){
  //trigger download of data.csv file
  var url = document.location.href;
  var filebase = url.split('/').pop().split('#')[0].replace(/\.(html|htm)$/, "");
  $("#download-csv").click(function(){
      console.log('download-csv');
      // call to global var `tbl` (some rows are hidden)
      tbl.download("csv", filebase + ".csv");
  });
  
  //trigger download of data.json file
  $("#download-json").click(function(){
      console.log('download-json');
      tbl.download("json", filebase + ".json");
  });
});

