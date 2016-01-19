var formsModule = (function() {
    var postform = document.forms.postform;
    if (postform) {
        var message_field = document.getElementById('message');

        var plinks_insert = function(elem) {
            elem.preventDefault();
            var val = '>>' + elem.target.firstChild.nodeValue;
            if (message_field.setSelectionRange) {
                var start = message_field.selectionStart,
                    end = message_field.selectionEnd;
                val += ' ';
                message_field.value =
                        message_field.value.substr(0, start) +
                        val +
                        message_field.value.substr(end);
                message_field.setSelectionRange(start + val.length, start + val.length);
            } else {
                message_field.value += val + ' ';
            }
            message_field.focus();

            return false;
        };
        
        var plinks = document.getElementsByClassName('postl');
        var plinks_i;
        for (plinks_i = 0; plinks_i < plinks.length; plinks_i++) {
            plinks[plinks_i].addEventListener('click', plinks_insert);
        }
    }
})();
