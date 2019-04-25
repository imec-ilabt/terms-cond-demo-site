
function set_loading(is_loading) {
    if (is_loading) {
        document.getElementById("userurn").innerHTML = 'loading...';
    } else {
        document.getElementById("userurn").innerHTML = '-';
    }

    document.getElementById("testbed-denied").hidden = true;
    document.getElementById("testbed-allowed").hidden = true;

    var loadedonce = document.getElementsByClassName("loadedonce");
    for(let i = 0; i < loadedonce.length; i++) {
        if (is_loading) {
            loadedonce.item(i).hidden = false;
        }
    }

    var loaded = document.getElementsByClassName("loaded");
    for(let i = 0; i < loaded.length; i++) {
        loaded.item(i).hidden = is_loading;
    }

    var loading = document.getElementsByClassName("loading");
    for(let i = 0; i < loading.length; i++) {
        loading.item(i).hidden = !is_loading;
    }
}

var change_event_prevent_hack = false;

function load_info() {
    set_loading(true);
    var xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        set_loading(false);
        if (this.status === 200) {
            var accepts = JSON.parse(xhttp.responseText);

            document.getElementById("userurn").innerHTML = accepts.user;

            change_event_prevent_hack = true;
            document.getElementById("main_accept").checked = accepts.main_accept;
            change_event_prevent_hack = false;

            document.getElementById("testbed-denied").hidden = accepts.testbed_access;
            document.getElementById("testbed-allowed").hidden = !accepts.testbed_access;

            document.getElementById("until-date").innerHTML = accepts.until;

            //let jFed know
            if (window.jfed && window.jfed.approveWithDateISO8601 && window.jfed.decline) {
                if (accepts.testbed_access) {
                    window.jfed.approveWithDateISO8601(accepts.until);
                } else {
                    window.jfed.decline();
                }
            }
        } else {
            if (this.status === 404) {
                //404 is currently not used by API, but we can handle it.
                document.getElementById("userurn").innerHTML = '-';
                change_event_prevent_hack = true;
                document.getElementById("main_accept").checked = false;
                change_event_prevent_hack = false;

                document.getElementById("testbed-denied").hidden = false;
                document.getElementById("testbed-allowed").hidden = true;
                document.getElementById("until-date").innerHTML = '-';

                //let jFed know
                if (window.jfed && window.jfed.decline) {
                    window.jfed.decline();
                }
            } else {
                console.log("load_info onload FAILURE status="+this.status);
            }
        }
    };
    xhttp.open("GET", "/api/terms_and_cond/v1.0/accept", true);
    xhttp.send();
}

function on_toggle_accept(event) {
    if (change_event_prevent_hack) { return; }
    var main_accept = document.getElementById("main_accept").checked;
    var terms = {
        'main_accept': main_accept,
    };
    set_loading(true);
    send_accept_terms(terms);
}

function send_accept_terms(terms) {
    var xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        if (this.status === 200 || this.status === 204) {
            load_info();
        } else {
            console.log("accept_terms onload FAILURE status="+this.status);
        }
    };
    xhttp.open("PUT", "/api/terms_and_cond/v1.0/accept", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.send(JSON.stringify(terms));
}

function decline_all_terms() {
    //alternative way to decline, using DELETE
    set_loading(true);
    var xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        if (this.status === 200 || this.status === 204) {
            load_info();
        } else {
            console.log("decline_all_terms onload FAILURE status="+this.status);
        }
    };
    xhttp.open("DELETE", "/api/terms_and_cond/v1.0/accept", true);
    xhttp.send();

    if (window.jfed && window.jfed.decline) {
        window.jfed.decline();
    }
}

function close_window() {
    if (window.jfed && window.jfed.close) {
        window.jfed.close();
    }
}

function initJFed() {
//  if (window.jfed && window.jfed.decline) {
//      //we do not have to do this: load_info does this
//      //let jFed know the users hasn't accepted the Terms and Conditions yet.
//      window.jfed.decline();
//  }


    if (window.jfed && window.jfed.decline) {
        document.getElementById("close-jfed-win").hidden = false;
    }
}

window.onload = function() {
    if (window.jfed) {
        initJFed();
    } else {
        //window.jfed is not (yet) available now. jFed injects it only later.
        //This is a trick to make browser call  initJFed() when window.jfed becomes available:
        Object.defineProperty(window, 'jfed', {
            configurable: true,
            enumerable: true,
            writeable: true,
            get: function() {
                return this._jfed;
            },
            set: function(val) {
                this._jfed = val;
                initJFed();
            }
        });

        if (window.jfed) {
            initJFed();
        }
    }

    load_info();
};
