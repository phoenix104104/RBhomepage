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
    
});