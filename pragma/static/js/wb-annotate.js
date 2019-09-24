var Wayback;

(function(funcName, baseObj) {
    "use strict";
    // The public function name defaults to window.docReady
    // but you can modify the last line of this function to pass in a different object or method name
    // if you want to put them in a different namespace and those will be used instead of 
    // window.docReady(...)
    funcName = funcName || "docReady";
    baseObj = baseObj || window;
    var readyList = [];
    var readyFired = false;
    var readyEventHandlersInstalled = false;
    
    // call this when the document is ready
    // this function protects itself against being called more than once
    function ready() {
        if (!readyFired) {
            // this must be set to true before we start calling callbacks
            readyFired = true;
            for (var i = 0; i < readyList.length; i++) {
                // if a callback here happens to add new ready handlers,
                // the docReady() function will see that it already fired
                // and will schedule the callback to run right after
                // this event loop finishes so all handlers will still execute
                // in order and no new ones will be added to the readyList
                // while we are processing the list
                readyList[i].fn.call(window, readyList[i].ctx);
            }
            // allow any closures held by these functions to free
            readyList = [];
        }
    }
    
    function readyStateChange() {
        if ( document.readyState === "complete" ) {
            ready();
        }
    }
    
    // This is the one public interface
    // docReady(fn, context);
    // the context argument is optional - if present, it will be passed
    // as an argument to the callback
    baseObj[funcName] = function(callback, context) {
        if (typeof callback !== "function") {
            throw new TypeError("callback for docReady(fn) must be a function");
        }
        // if ready has already fired, then just schedule the callback
        // to fire asynchronously, but right away
        if (readyFired) {
            setTimeout(function() {callback(context);}, 1);
            return;
        } else {
            // add the function and context to the list
            readyList.push({fn: callback, ctx: context});
        }
        // if document already ready to go, schedule the ready function to run
        // IE only safe when readyState is "complete", others safe when readyState is "interactive"
        if (document.readyState === "complete" || (!document.attachEvent && document.readyState === "interactive")) {
            setTimeout(ready, 1);
        } else if (!readyEventHandlersInstalled) {
            // otherwise if we don't have event handlers installed, install them
            if (document.addEventListener) {
                // first choice is DOMContentLoaded event
                document.addEventListener("DOMContentLoaded", ready, false);
                // backup is window load event
                window.addEventListener("load", ready, false);
            } else {
                // must be IE
                document.attachEvent("onreadystatechange", readyStateChange);
                window.attachEvent("onload", ready);
            }
            readyEventHandlersInstalled = true;
        }
    }
})("docReady", window);

docReady(function() {
    'use strict';
    var apiurl = "https://pragma.archivelab.org";
    var highlight = {
	el: undefined,
	backgroundColor: undefined
    }

    // From: https://stackoverflow.com/a/4588211
    var elToSelector = function fullPath(el){
	var names = [];
	while (el.parentNode){
	    if (el.id){
		names.unshift('#'+el.id);
		break;
	    }else{
		if (el==el.ownerDocument.documentElement) names.unshift(el.tagName);
		else{
		    for (var c=1,e=el;e.previousElementSibling;e=e.previousElementSibling,c++);
		    names.unshift(el.tagName+":nth-child("+c+")");
		}
		el=el.parentNode;
	    }
	}
	return names.join(" > ");
    }

    document.addEventListener('mouseup', function () {
	if (typeof window.getSelection != "undefined") { 
	    var selection = window.getSelection();
	    if (selection.toString()) {
		var el = selection.anchorNode.parentElement;
		selector = elToSelector(el)
		window.location.hash = 'jump-' + selector;
		highlightId(selector);
	    }
	}
    });
    
    var requests = {
	get: function(url, callback) {
	    var httpRequest = new XMLHttpRequest();
	    if (httpRequest) {
		httpRequest.onreadystatechange = function() {
		    if (httpRequest.readyState === XMLHttpRequest.DONE) {
			if (httpRequest.status === 200) {
			    callback(JSON.parse(httpRequest.responseText));
			}
		    }
		}
		httpRequest.open('GET', url, true);
		httpRequest.send();
	    } else {
		console.log('http GET failed');
	    }
	}
    };

    var highlightId = function(selector) {
	if (highlight.el) {
	    highlight.el.style.backgroundColor = highlight.backgroundColor;
	}
        var e = document.querySelector(selector);
	highlight.el = e;
	highlight.backgroundColor = e.style.backgroundColor;
        e.style.backgroundColor = "yellow";
    }

    var jumpId = function(selector) {
        var e = document.querySelector(selector);
	var sizeWaybackTopbar = -2 * document.getElementById('wm-ipp-base').scrollHeight;
	e.scrollIntoView(true, {behavior: "smooth", block: 'center'});
	window.scrollBy(0, sizeWaybackTopbar);
    }

    if (window.location.hash && window.location.hash.startsWith('#jump-')) {
	var selector = decodeURIComponent(window.location.hash.split('#jump-')[1]);
	highlightId(selector);
	jumpId(selector);
    } else if (window.location.hash && window.location.hash.startsWith('#wbaid-')) {
	var wbaid = window.location.hash.split('-')[1];
	Wayback = {
	    getAnnotation: function(id, callback) {
		var url = apiurl + '/wayback-annotations/' + id;
		requests.get(url, callback);
	    }
	}
	Wayback.scrollToCitation = function() {
	    Wayback.getAnnotation(wbaid, function(response) {
		var annoid = '#' + response.annotation.annotation.id;
		highlightId(annoid);
		jumpId(annoid);
            });
	}
        Wayback.scrollToCitation(wbaid);
    }
});
