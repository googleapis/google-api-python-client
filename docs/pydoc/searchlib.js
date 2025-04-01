// Wrapper around lunr index searching system for pydoctor API objects 
//      and function to format search results items into rederable HTML elements.
// This file is meant to be used as a library for the pydoctor search bar (search.js) as well as
//      provide a hackable inferface to integrate API docs searching into other platforms, i.e. provide a 
//      "Search in API docs" option from Read The Docs search page.
// Depends on ajax.js, bundled with pydoctor. 
// Other required ressources like lunr.js, searchindex.json and all-documents.html are passed as URL
//      to functions. This makes the code reusable outside of pydoctor build directory.    
// Implementation note: Searches are designed to be launched synchronously, if lunrSearch() is called sucessively (while already running),
// old promise will never resolves and the searhc worker will be restarted.

// Hacky way to make the worker code inline with the rest of the source file handling the search.
// Worker message params are the following: 
// - query: string
// - indexJSONData: dict
// - defaultFields: list of strings
// - autoWildcard: boolean
let _lunrWorkerCode = `

// The lunr.js code will be inserted here.

onmessage = (message) => {
    if (!message.data.query) {
        throw new Error('No search query provided.');
    }
    if (!message.data.indexJSONData) {
        throw new Error('No index data provided.');
    }
    if (!message.data.defaultFields) {
        throw new Error('No default fields provided.');
    }
    if (!message.data.hasOwnProperty('autoWildcard')){
        throw new Error('No value for auto wildcard provided.');
    }
    // Create index
    let index = lunr.Index.load(message.data.indexJSONData);
    
    // Declare query function building 
    function _queryfn(_query){ // _query is the Query object
        // Edit the parsed query clauses that are applicable for all fields (default) in order
        // to remove the field 'kind' from the clause since this it's only useful when specifically requested.
        var parser = new lunr.QueryParser(message.data.query, _query)
        parser.parse()
        var hasTraillingWildcard = false;
        _query.clauses.forEach(clause => {
            if (clause.fields == _query.allFields){
                // we change the query fields when they are applicable to all fields
                // to a list of predefined fields because we might include additional filters (like kind:)
                // which should not be matched by default.
                clause.fields = message.data.defaultFields;
            }
            // clause.wildcard is actually always NONE due to https://github.com/olivernn/lunr.js/issues/495
            // But this works...
            if (clause.term.slice(-1) == '*'){
                // we want to avoid the auto wildcard system only if a trailling wildcard is already added
                // not if a leading wildcard exists
                hasTraillingWildcard = true
            }
        });
        // Auto wilcard feature, see issue https://github.com/twisted/pydoctor/issues/648
        var new_clauses = [];
        if ((message.data.autoWildcard == true) && (hasTraillingWildcard == false)){
            _query.clauses.forEach(clause => {
                // Setting clause.wildcard is useless.
                // But this works...
                let new_clause = {...clause}
                new_clause.term = new_clause.term + '*'
                clause.boost = 2
                new_clause.boost = 0
                new_clauses.push(new_clause)
            });
        }
        new_clauses.forEach(clause => {
            _query.clauses.push(clause)
        });
        console.log('Parsed query:')
        console.dir(_query.clauses)
    }

    // Launch the search
    let results = index.query(_queryfn)
    
    // Post message with results
    postMessage({'results':results});
};
`;

// Adapted from https://stackoverflow.com/a/44137284
// Override worker methods to detect termination and count message posting and restart() method.
// This allows some optimizations since the worker doesn't need to be restarted when it hasn't been used.
function _makeWorkerSmart(workerURL) {
    // make normal worker
    var worker = new Worker(workerURL);
    // assume that it's running from the start
    worker.terminated = false;
    worker.postMessageCount = 0;
    // count the number of times postMessage() is called
    worker.postMessage = function() {
        this.postMessageCount = this.postMessageCount + 1;
        // normal post message
        return Worker.prototype.postMessage.apply(this, arguments);
    }
    // sets terminated to true
    worker.terminate = function() {
        if (this.terminated===true){return;}
        this.terminated = true;
        // normal terminate
        return Worker.prototype.terminate.apply(this, arguments);
    }
    // creates NEW WORKER with the same URL as itself, terminate worker first.
    worker.restart = function() {
        this.terminate();
        return _makeWorkerSmart(workerURL);
    }
    return worker;
}

var _searchWorker = null

/**
 * The searchEventsEnv Document variable let's let caller register a event listener "searchStarted" for sending
 * a signal when the search actually starts, could be up to 0.2 or 0.3 secs ater user finished typing.
 */
let searchEventsEnv = document.implementation.createHTMLDocument(
    'This is a document to popagate search related events, we avoid using "document" for performance reasons.');

// there is a difference in abortSearch() vs restartSearchWorker().
// abortSearch() triggers a abortSearch event, which have a effect on searches that are not yet running in workers.
// whereas restartSearchWorker() which kills the worker if it's in use, but does not abort search that is not yet posted to the worker.
function abortSearch(){
    searchEventsEnv.dispatchEvent(new CustomEvent('abortSearch', {}));
}
// Kills and restarts search worker (if needed).
function restartSearchWorker() {
    var w = _searchWorker;
    if (w!=null){
        if (w.postMessageCount>0){
            // the worker has been used, it has to be restarted
            // TODO: Actually it needs to be restarted only if it's running a search right now.
            // Otherwise we can reuse the same worker, but that's not a very big deal in this context.
            w = w.restart();
        } 
        // Else, the worker has never been used, it can be returned as is. 
        // This can happens when typing fast with a very large index JSON to load.
    }
    _searchWorker = w;
}

function _getWorkerPromise(lunJsSourceCode){ // -> Promise of a fresh worker to run a query.
    let promise = new Promise((resolve, reject) => {
        // Do the search business, wrap the process inside an inline Worker.
        // This is a hack such that the UI can refresh during the search.
        if (_searchWorker===null){
            // Create only one blob and URL.
            let lunrWorkerCode = lunJsSourceCode + _lunrWorkerCode;
            let _workerBlob = new Blob([lunrWorkerCode], {type: 'text/javascript'});
            let _workerObjectURL = window.URL.createObjectURL(_workerBlob);
            _searchWorker = _makeWorkerSmart(_workerObjectURL)
        }
        else{
            restartSearchWorker();
        }
        resolve(_searchWorker);
    });
    return promise
}

/**
 * Launch a search and get a promise of results. One search can be lauch at a time only.
 * Old promise never resolves if calling lunrSearch() again while already running.
 * @param query: Query string.
 * @param indexURL: URL pointing to the Lunr search index, generated by pydoctor.
 * @param defaultFields: List of strings: default fields to apply to query clauses when none is specified. ["name", "names", "qname"] for instance.
 * @param lunrJsURL: URL pointing to a copy of lunr.js.
 * @param searchDelay: Number of miliseconds to wait before actually launching the query. This is useful to set for "search as you type" kind of search box
 *                     because it let a chance to users to continue typing without triggering useless searches (because previous search is aborted on launching a new one).
 * @param autoWildcard: Whether to automatically append wildcards to all query clauses when no wildcard is already specified. boolean.
 */
function lunrSearch(query, indexURL, defaultFields, lunrJsURL, searchDelay, autoWildcard){
    // Abort ongoing search
    abortSearch();

    // Register abort procedure.
    var _aborted = false;
    searchEventsEnv.addEventListener('abortSearch', (ev) => {
        _aborted = true;
        searchEventsEnv.removeEventListener('abortSearch', this);
    });

    // Pref:
    // Because this function can be called a lot of times in a very few moments, 
    // Actually launch search after a delay to let a chance to users to continue typing,
    // which would trigger a search abort event, which would avoid wasting a worker 
    // for a search that is not wanted anymore.
    return new Promise((_resolve, _reject) => {
        setTimeout(() => {
        _resolve(
        _getIndexDataPromise(indexURL).then((lunrIndexData) => {
        // Include lunr.js source inside the worker such that it has no dependencies.
        return httpGetPromise(lunrJsURL).then((responseText) => {
        // Do the search business, wrap the process inside an inline Worker.
        // This is a hack such that the UI can refresh during the search.
        return _getWorkerPromise(responseText).then((worker) => {
            let promise = new Promise((resolve, reject) => {
                worker.onmessage = (message) => {
                    if (!message.data.results){
                        reject("No data received from worker");
                    }
                    else{
                        console.log("Got result from worker:")
                        console.dir(message.data.results)
                        resolve(message.data.results)
                    }
                }
                worker.onerror = function(error) {
                    reject(error);
                };
            });
            let _msgData = {
                'query': query,
                'indexJSONData': lunrIndexData,
                'defaultFields': defaultFields,
                'autoWildcard': autoWildcard, 
            }
            
            if (!_aborted){
                console.log(`Posting query "${query}" to worker:`)
                console.dir(_msgData)
                worker.postMessage(_msgData);
                searchEventsEnv.dispatchEvent(
                    new CustomEvent("searchStarted", {'query':query})
                );
            }

            return promise
        });
        });
        })
        );}, searchDelay);
    });
}

/** 
* @param results: list of lunr.Index~Result.
* @param allDocumentsURL: URL pointing to all-documents.html, generated by pydoctor.
* @returns: Promise of a list of HTMLElement corresponding to the all-documents.html
*   list elements matching your search results.
*/
function fetchResultsData(results, allDocumentsURL){
    return _getAllDocumentsPromise(allDocumentsURL).then((allDocuments) => {
        // Look for results data in parsed all-documents.html
        return _asyncFor(results, (result) => {
            // Find the result model row data.
            var dobj = allDocuments.getElementById(result.ref);
            if (!dobj){
                throw new Error("Cannot find document ID: " + result.ref);
            }
            // Return result data
            return dobj;
        })
    })
}

/**
 * Transform list item as in all-documents.html into a formatted search result row.
 */
function buildSearchResult(dobj) {

    // Build one result item
    var tr = document.createElement('tr'),
        kindtd = document.createElement('td'),
        contenttd = document.createElement('td'),
        article = document.createElement('article'),
        header = document.createElement('header'),
        section = document.createElement('section'),
        code = document.createElement('code'),
        a = document.createElement('a'),
        p = document.createElement('p');
  
    p.innerHTML = dobj.querySelector('.summary').innerHTML;
    a.setAttribute('href', dobj.querySelector('.url').innerHTML);
    a.setAttribute('class', 'internal-link');
    a.innerHTML = dobj.querySelector('.fullName').innerHTML;
    
    let kind_value = dobj.querySelector('.kind').innerHTML;
    let type_value = dobj.querySelector('.type').innerHTML;
  
    // Adding '()' on functions and methods
    if (type_value.endsWith("Function")){
        a.innerHTML = a.innerHTML + '()';
    }
  
    kindtd.innerHTML = kind_value;
    
    // Putting everything together
    tr.appendChild(kindtd);
    tr.appendChild(contenttd);
    contenttd.appendChild(article);
    article.appendChild(header);
    article.appendChild(section);
    header.appendChild(code);
    code.appendChild(a);
    section.appendChild(p);
  
    // Set kind as the CSS class of the kind td tag
    let ob_css_class = dobj.querySelector('.kind').innerHTML.toLowerCase().replace(' ', '');
    kindtd.setAttribute('class', ob_css_class);
  
    // Set private
    if (dobj.querySelector('.privacy').innerHTML.includes('PRIVATE')){
      tr.setAttribute('class', 'private');
    }
    
    return tr;
}


// This gives the UI the opportunity to refresh while we're iterating over a large list.
function _asyncFor(iterable, callback) { // -> Promise of List of results returned by callback
    const promise_global = new Promise((resolve_global, reject_global) => {
      let promises = [];
      iterable.forEach((element) => {
          promises.push(new Promise((resolve, _reject) => {
            setTimeout(() => {
                try{ resolve(callback(element)); }
                catch (error){ _reject(error); }
            }, 0);
          }));
      }); 
      Promise.all(promises).then((results) =>{
        resolve_global(results);
      }).catch((err) => {
          reject_global(err);
      });
    });
    return promise_global;
  }

// Cache indexes JSON data since it takes a little bit of time to load JSON into stuctured data
var _indexDataCache = {};
function _getIndexDataPromise(indexURL) { // -> Promise of a structured data for the lunr Index.
    if (!_indexDataCache[indexURL]){
        return httpGetPromise(indexURL).then((responseText) => {
            _indexDataCache[indexURL] = JSON.parse(responseText)
            return (_indexDataCache[indexURL]);
        });
    }
    else{
        return new Promise((_resolve, _reject) => {
            _resolve(_indexDataCache[indexURL]);
        });
    }
}

// Cache Document object
var _allDocumentsCache = {};
function _getAllDocumentsPromise(allDocumentsURL) { // -> Promise of the all-documents.html Document object.
    if (!_allDocumentsCache[allDocumentsURL]){
        return httpGetPromise(allDocumentsURL).then((responseText) => {
            let _parser = new self.DOMParser();
            _allDocumentsCache[allDocumentsURL] = _parser.parseFromString(responseText, "text/html");
            return (_allDocumentsCache[allDocumentsURL]);
        });
    }
    else{
        return new Promise((_resolve, _reject) => {
            _resolve(_allDocumentsCache[allDocumentsURL]);
        });
    }
}
