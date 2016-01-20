var echModules = {};


echModules.settings = (function (modules_obj) {
    var modules = modules_obj;
    var settings = {};

    var init = function () {
        var mathes = document.cookie.match(new RegExp(
            '(?:^|; )user_settings=([^;$]*)'
        ));
        if (mathes) {
            settings = JSON.parse(atob(mathes[1]));
        }
    };

    var save = function () {
        document.cookie = 'user_settings=' + btoa(JSON.stringify(settings)) + ';expires=31536000';
    };

    return {
        run: function () {
            init();
        },
        get: function (name, defaultValue) {
            return settings[name] || defaultValue;
        },
        set: function (name, value) {
            settings[name] = value;
            save();
        }
    };
})(echModules);


echModules.forms = (function(modules_obj) {
    var modules = modules_obj;
    var postform = document.forms.postform;
    var message_field = document.getElementById('message');

    var add_to_message_field = function (text) {
        if (message_field.setSelectionRange) {
            var start = message_field.selectionStart,
                end = message_field.selectionEnd;
            text += ' ';
            message_field.value =
                    message_field.value.substr(0, start) +
                    text +
                    message_field.value.substr(end);
            message_field.setSelectionRange(start + text.length, start + text.length);
        } else {
            message_field.value += text + ' ';
        }
        message_field.focus();
    };

    var init = function () {
        if (postform) {
            var plinks_insert = function(elem) {
                var cssClass = elem.target.getAttribute('class');
                if (cssClass && cssClass.indexOf('postl') >= 0) {
                    elem.preventDefault();
                    add_to_message_field('>>' + elem.target.firstChild.nodeValue);

                    return false;
                }
            };

            document.addEventListener('click', plinks_insert);
        }
    };

    return {
        run: function () {
            init();
        },
        insert: function (text) {
            add_to_message_field(text);
        }
    };
})(echModules);


echModules.board = (function(modules_obj) {
    var modules = modules_obj;
    var hidden_threads;

    var toggle_thread = function (id) {
        var thread = document.getElementById('thread' + id),
            mess = document.getElementById('hide-thread' + id);
        if (thread) {
            if (thread.style.display != 'none') {
                thread.style.display = 'none';
                mess.style.display = 'block';
            } else {
                thread.style.display = 'block';
                mess.style.display = 'none';
            }
        }
    };

    var click_to_hide = function (elem) {
        var cssClass = elem.target.getAttribute('class');
        if (cssClass && cssClass.indexOf('hidde-thread') >= 0) {
            elem.preventDefault();
            var thread = elem.target.dataset.thread;
            toggle_thread(elem.target.dataset.thread);

            if (hidden_threads[thread]) {
                delete hidden_threads[thread];
            } else {
                hidden_threads[thread] = 1;
            }
            modules.settings.set('hidden_threads', hidden_threads);

            return false;
        }
    };

    document.addEventListener('click', click_to_hide);

    var init = function() {
        hidden_threads = modules.settings.get('hidden_threads', {});
        for (thread in hidden_threads) {
            toggle_thread(thread);
        }
    };

    return {
        run: function () {
            init();
        }
    };
})(echModules);


for (module in echModules) {
    echModules[module].run();
}
