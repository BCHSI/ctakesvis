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
    var row_id = "row_" + id_;
    changeColorTable(row_id);
    var row_id = "entity_" + id_;
    highlightConceptText(row_id);
};

$(document).on('click', ".tooltiptext", highlightConceptEverywhere);
// $(document).on('click', ".tooltiptext", changeColorTable);
$(document).on('click', ".entity_row", highlightConceptEverywhere);

//
// $(document).ready(
$(window).load(function(){

    if ( $('table').length ) {
        var $table_body_scroll=$('table'),
            header_table=$( '<table aria-hidden="true" border=1 class="header_table"><thead><tr><td></td></tr></thead></table>' ),
        scroll_div='<div class="body_scroll"></div>';
        
    //inject table that will hold stationary row header; inject the div that will get scrolled
    $table_body_scroll.before( header_table ).before( scroll_div );
    
    $table_body_scroll.each(function (index) {
        //to minimize FUOC, I like to set the relevant variables before manipulating the DOM
        var columnWidths = [];
        var $targetDataTable=$(this);
        var $targetHeaderTable=$("table.header_table").eq(index);
        var $targetDataTableFooter=$targetDataTable.find('tfoot');
        
        var tableWidth = $(this).width()
        // set table width
        $($targetHeaderTable).css("width", $(this).width())

        // Get column widths
        $($targetDataTable).find('thead tr th').each(function (index) {
            columnWidths[index] = $(this).width();
            // columnWidths[index] = (100*$(this).width() / tableWidth).toString() + '%' ;
        });
        
        //place target table inside of relevant scrollable div (using jQuery eq() and index)
        $('div.body_scroll').eq(index).prepend( $targetDataTable ).width( $($targetDataTable).width() );
        
        // hide original caption, header, and footer from sighted users
        $($targetDataTable).children('caption, thead, tfoot').hide();
        
        // insert header data into static table
        $($targetHeaderTable).find('thead').replaceWith( $( $targetDataTable ).children('caption, thead').clone().show() );
        
        // modify column width for header
        $($targetHeaderTable).find('thead tr th').each(function (index) {
            $(this).css('width', columnWidths[index]);
        });
        
        // make sure table data still lines up correctly
        $($targetDataTable).find('tbody tr td').each(function (index) {
            if (index>=0){
                $(this).css('width', columnWidths[index+1]);
            };
        });
        
        //if our target table has a footer, create a visual copy of it after the scrollable div
        if ( $targetDataTableFooter.length ) {
             $('div.body_scroll').eq(index).after('<div class="table_footer">'+ $targetDataTableFooter.text() +'</div>');
        }
    });
}
});
