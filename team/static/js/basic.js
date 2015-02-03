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

});

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
        console.log(boxs[i].value)
    }
    console.log("////////////")
}