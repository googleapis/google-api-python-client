// Implement simple cached AJAX functions.

var _cache = {};

/*
* Get a promise for the HTTP get responseText.
*/
function httpGetPromise(url) {
    const promise = new Promise((_resolve, _reject) => {
        httpGet(url, (responseText) => {
            _resolve(responseText);
        },
        (error) => {
            _reject(error);
        });
    });
    return promise
}

function httpGet(url, onload, onerror) { 
    if (_cache[url]) {
        _cachedHttpGet(url, onload, onerror);
    }
    else{
        _httpGet(url, onload, onerror);
    }
}

function _cachedHttpGet(url, onload, onerror) {
    setTimeout(() => { onload(_cache[url]) }, 0);
}

function _httpGet(url, onload, onerror) {   

    var xobj = new XMLHttpRequest();
    xobj.open('GET', url, true); // Asynchronous
    
    xobj.onload = function () {
        // add document to cache.
        _cache[url] = xobj.responseText;
        onload(xobj.responseText);
    };

    xobj.onerror = function (error) {
        console.log(error)
        onerror(error)
    };

    xobj.send(null);  
}
