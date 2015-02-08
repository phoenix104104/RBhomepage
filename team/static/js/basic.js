$(document).ready(function() {

    $("textarea").keydown(function(e) {
        
        if(e.keyCode === 9) { // tab was pressed
            // get caret position/selection
            var start = this.selectionStart;
                end = this.selectionEnd;

            var $this = $(this);

            // set textarea value to: text before caret + tab + text after caret
            $this.val($this.val().substring(0, start)
                        + "\t"
                        + $this.val().substring(end));

            // put caret at right position again
            this.selectionStart = this.selectionEnd = start + 1;

            // prevent the focus lose
            return false;
        }
    });

    $(".lined").linedtextarea({
        selectedClass: 'lineselect'
    });

    $('#loginForm').formValidation({
        excluded: [':disabled'],
        framework: 'bootstrap',
        fields: {
            username: {
                validators: {
                    notEmpty: {
                        message: 'The username is required'
                    }
                }
            },
            password: {
                validators: {
                    notEmpty: {
                        message: 'The password is required'
                    }
                }
            }
        }
    });

    if( warning != "None" && is_login != "True" ){
        $('#login-modal').modal('show');
    }


    // set default checkbox_wl
    var boxs = document.getElementsByClassName("checkbox_wl");
    for (i=0 ; i<boxs.length ; i++){
        if( boxs[i].value == '1' ){
            boxs[i].checked = true;
            boxs[i].value = '1';
        } else {
            boxs[i].checked = false;
            boxs[i].value = '0';
        }
    }


    // store last tab in cookies
    $('a[data-toggle="tab"]').on('shown.bs.tab', function () {
        //save the latest tab; use cookies if you like 'em better:
        localStorage.setItem('lastTab', $(this).attr('href'));
        console.log("store last tab");
    });

    //go to the latest tab, if it exists:
    var lastTab = localStorage.getItem('lastTab');
    if ($('a[href=' + lastTab + ']').length > 0) {
        $('a[href=' + lastTab + ']').tab('show');
        console.log("restore last tab");
    }
    else
    {
        // Set the first tab if cookie do not exist
        var element = document.getElementById("Game-Log");
        $('a[data-toggle="tab"]:first').tab('show');
        console.log("show first tab");
    }
   

    // enable table sort
    $("#all_batting_table").tablesorter();
    $("#all_pitching_table").tablesorter();
    
});


/*
$(function() { 
    $('a[data-toggle="tab"]').on('shown.bs.tab', function(e){
        //save the latest tab using a cookie:
        $.cookie('last_tab', $(e.target).attr('href'));
    });
    //activate latest tab, if it exists:
    var lastTab = $.cookie('last_tab');
    if (lastTab) {
        $('a[href=' + lastTab + ']').tab('show');
    }
    else
    {
        // Set the first tab if cookie do not exist
        $('a[data-toggle="tab"]:first').tab('show');
    }
});*/

function check_wl(current_box){
    
    var boxs = document.getElementsByClassName("checkbox_wl");
    if( current_box.checked ){
        current_box.value = '1';
    } else {
        current_box.value = '0';
    }
    for (i=0 ; i<boxs.length ; i++){
        if( boxs[i] != current_box ) {
            boxs[i].checked = false;
            boxs[i].value = '0';
        } else {
            boxs[i].checked = current_box.checked;
            boxs[i].value = current_box.value;
        }
    }
}

function submit_options(selector){
    selector.form.submit();
}