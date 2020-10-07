$(function() {
        /* get the current dataSource to parse*/
        /* var form = document.forms['efpForm']; */
        /* var db = form['dataSource'].value; */

        /*function log( message ) {
                $( "<div/>" ).text( message ).prependTo( "#log" );
                $( "#log" ).scrollTop( 0 );
        } */
        $( ".gene-input" ).autocomplete({
                source: "../cgi-bin/autocompleter.py", /* parses the current dataSource as well*/
                minLength: 7
                /* ONLY NEEDED TO DISPLAY RESULT IN ANOTHER DIV
                select: function( event, ui ) {
                        log( ui.item ?
                        "Selected: " + ui.item.value + " aka " + ui.item.id :
                        "Nothing selected, input was " + this.value );
                }*/
        });
});
