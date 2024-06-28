// This file contains the code that drives the search system UX.
// It's included in every HTML file.
// Depends on library files searchlib.js and ajax.js (and of course lunr.js)

// Ideas for improvments: 
// - Include filtering buttons:
//    - search only in the current module
//    - have a query frontend that helps build complex queries
// - Filter out results that have score > 0.001 by default and show them on demand.
// - Should we change the default term presence to be MUST and not SHOULD ?
//        -> Hack something like 'name index -value' -> '+name +index -value'
//        ->      'name ?index -value' -> '+name index -value'
// - Highlight can use https://github.com/bep/docuapi/blob/5bfdc7d366ef2de58dc4e52106ad474d06410907/assets/js/helpers/highlight.js#L1
// Better: Add support for AND and OR with parenthesis, ajust this code https://stackoverflow.com/a/20374128

//////// GLOBAL VARS /////////

let input = document.getElementById('search-box');
let results_container = document.getElementById('search-results-container');
let results_list = document.getElementById('search-results'); 
let searchInDocstringsButton = document.getElementById('search-docstrings-button'); 
let searchInDocstringsCheckbox = document.getElementById('toggle-search-in-docstrings-checkbox');
var isSearchReadyPromise = null;

// setTimeout variable to warn when a search takes too long
var _setLongSearchInfosTimeout = null;

//////// UI META INFORMATIONS FUNCTIONS /////////

// Taken from https://stackoverflow.com/a/14130005
// For security.
function htmlEncode(str) {
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function _setInfos(message, box_id, text_id) {
  document.getElementById(text_id).textContent = message;
  if (message.length>0){
    document.getElementById(box_id).style.display = 'block';
  }
  else{
    document.getElementById(box_id).style.display = 'none';
  }
}

/**
 * Set the search status.
 */
function setStatus(message) {
  document.getElementById('search-status').textContent = message;
}

/**
 * Show a warning, hide warning box if empty string.
 */
function setWarning(message) {
  _setInfos(message, 'search-warn-box', 'search-warn');
}

/**
 * Say that Something went wrong.
 */
function setErrorStatus() {
  resetLongSearchTimerInfo()
  setStatus("Something went wrong.");
  setErrorInfos();
}

/**
 * Show additional error infos (used to show query parser errors infos) or tell to go check the console.
 * @param message: (optional) string
 */
function setErrorInfos(message) {
  if (message != undefined){
    setWarning(message);
  }
  else{
    setWarning("Error: See development console for details.");
  }
}

/**
 * Reset the long search timer warning.
 */
function resetLongSearchTimerInfo(){
  if (_setLongSearchInfosTimeout){
    clearTimeout(_setLongSearchInfosTimeout);
  }
}
function launchLongSearchTimerInfo(){
  // After 10 seconds of searching, warn that this is taking more time than usual.
  _setLongSearchInfosTimeout = setTimeout(setLongSearchInfos, 10000);
}

/**
 * Say that this search is taking longer than usual.
 */
function setLongSearchInfos(){
  setWarning("This is taking longer than usual... You can keep waiting for the search to complete, or retry the search with other terms.");
}

//////// UI SHOW/HIDE FUNCTIONS /////////

function hideResultContainer(){
  results_container.style.display = 'none';
  if (!document.body.classList.contains("search-help-hidden")){
    document.body.classList.add("search-help-hidden");
  }
}

function showResultContainer(){
  results_container.style.display = 'block';
  updateClearSearchBtn();
}

function toggleSearchHelpText() {
  document.body.classList.toggle("search-help-hidden");
  if (document.body.classList.contains("search-help-hidden") && input.value.length==0){
    hideResultContainer();
  }
  else{
    showResultContainer();
  }
}

function resetResultList(){
  resetLongSearchTimerInfo();
  results_list.innerHTML = '';
  setWarning('');
  setStatus('');
}

function clearSearch(){
  stopSearching();

  input.value = '';
  updateClearSearchBtn();
}

function stopSearching(){
  // UI
  hideResultContainer();
  resetResultList();

  // NOT UI
  _stopSearchingProcess();
}

function _stopSearchingProcess(){
  abortSearch();
  restartSearchWorker();
}

/**
 * Show and hide the (X) button depending on the current search input.
 * We do not show the (X) button when there is no search going on.
 */
 function updateClearSearchBtn(){
  
  if (input.value.length>0){
    document.getElementById('search-clear-button').style.display = 'inline-block';
  }
  else{
    document.getElementById('search-clear-button').style.display = 'none';
  }
}

//////// SEARCH WARPPER FUNCTIONS /////////

// Values configuring the search-as-you-type feature.
var SEARCH_DEFAULT_DELAY = 100; // in miliseconds
var SEARCH_INCREASED_DELAY = 200;
var SEARCH_INDEX_SIZE_TRESH_INCREASE_DELAY = 10; // in MB
var SEARCH_INDEX_SIZE_TRESH_DISABLE_SEARCH_AS_YOU_TYPE = 20;
var SEARCH_AUTO_WILDCARD = true;

// Search delay depends on index size.
function _getIndexSizePromise(indexURL){
  return httpGetPromise(indexURL).then((responseText) => {
    if (responseText==null){
      return 0;
    }
    let indexSizeApprox = responseText.length / 1000000; // in MB
    return indexSizeApprox;
  });
}
function _getSearchDelayPromise(indexURL){ // -> Promise of a Search delay number.
  return _getIndexSizePromise(indexURL).then((size) => {
    var searchDelay = SEARCH_DEFAULT_DELAY;
    if (size===0){
      return searchDelay;
    }
    if (size>SEARCH_INDEX_SIZE_TRESH_INCREASE_DELAY){
      // For better UX
      searchDelay = SEARCH_INCREASED_DELAY; // in miliseconds, this avoids searching several times when typing several leters very rapidly 
    }
    return searchDelay;
  });
}

function _getIsSearchReadyPromise(){
  return Promise.all([
    httpGetPromise("all-documents.html"),
    httpGetPromise("searchindex.json"),
    httpGetPromise("fullsearchindex.json"),
    httpGetPromise("lunr.js"),
  ]);
}

// Launch search as user types if the size of the index is small enought,
// else say "Press 'Enter' to search".
function searchAsYouType(){
  if (input.value.length>0){
    showResultContainer();
  }
  _getIndexSizePromise("searchindex.json").then((indexSizeApprox) => {
    if (indexSizeApprox > SEARCH_INDEX_SIZE_TRESH_DISABLE_SEARCH_AS_YOU_TYPE){
      // Not searching as we type if "default" index size if greater than 20MB.
      if (input.value.length===0){ // No actual query, this only resets some UI components.
        launchSearch(); 
      }
      else{
        setTimeout(() => {
          _stopSearchingProcess();
          resetResultList();
          setStatus("Press 'Enter' to search.");
        });
      }
    }
    else{
      launchSearch();
    }
  });
}

searchEventsEnv.addEventListener("searchStarted", (ev) => {
  setStatus("Searching...");
});

var _lastSearchStartTime = null;
var _lastSearchInput = null;
/** 
 * Do the actual searching business
 * Main entrypoint to [re]launch the search.
 * Called everytime the search bar is edited.
*/
function launchSearch(noDelay){
  let _searchStartTime = performance.now();

  // Get the query terms 
  let _query = input.value;

  // In chrome, two events are triggered simultaneously for the input event.
  // So we discard consecutive (within the same 0.001s) requests that have the same search query.
  if ((
    (_searchStartTime-_lastSearchStartTime) < (0.001*1000)
    ) && (_query === _lastSearchInput) ){
      return;
  }

  updateClearSearchBtn();

  // Setup query meta infos.
  _lastSearchStartTime = _searchStartTime
  _lastSearchInput = _query;

  if (_query.length===0){
    stopSearching();
    return;
  }

  if (!window.Worker) {
    setStatus("Cannot search: JavaScript Worker API is not supported in your browser. ");
    return;
  }
  
  resetResultList();
  showResultContainer();
  setStatus("...");

  // Determine indexURL
  let indexURL = _isSearchInDocstringsEnabled() ? "fullsearchindex.json" : "searchindex.json";
  
  // If search in docstring is enabled: 
  //  -> customize query function to include docstring for clauses applicable for all fields
  let _fields = _isSearchInDocstringsEnabled() ? ["name", "names", "qname", "docstring"] : ["name", "names", "qname"];

  resetLongSearchTimerInfo();
  launchLongSearchTimerInfo();
  
  // Get search delay, wait the all search resources to be cached and actually launch the search 
  return _getSearchDelayPromise(indexURL).then((searchDelay) => {
  if (isSearchReadyPromise==null){
    isSearchReadyPromise = _getIsSearchReadyPromise()
  }
  return isSearchReadyPromise.then((r)=>{ 
  return lunrSearch(_query, indexURL, _fields, "lunr.js", !noDelay?searchDelay:0, SEARCH_AUTO_WILDCARD).then((lunrResults) => { 

      // outdated query results
      if (_searchStartTime != _lastSearchStartTime){return;}
      
      if (!lunrResults){
        setErrorStatus();
        throw new Error("No data to show");
      }

      if (lunrResults.length == 0){
        setStatus('No results matches "' + htmlEncode(_query) + '"');
        resetLongSearchTimerInfo();
        return;
      }

      setStatus("One sec...");

      // Get result data
      return fetchResultsData(lunrResults, "all-documents.html").then((documentResults) => {

        // outdated query results
        if (_searchStartTime != _lastSearchStartTime){return;}

        // Edit DOM
        resetLongSearchTimerInfo();
        displaySearchResults(_query, documentResults, lunrResults)
        
        // Log stats
        console.log('Search for "' + _query + '" took ' + 
          ((performance.now() - _searchStartTime)/1000).toString() + ' seconds.')

        // End
      })
  }); // lunrResults promise resolved
  });
  }).catch((err) => {_handleErr(err);});

} // end search() function

function _handleErr(err){
  console.dir(err);
    setStatus('')
    if (err.message){
      resetLongSearchTimerInfo();
      setWarning(err.message) // Here we show the error because it's likely a query parser error.
    }
    else{
      setErrorStatus();
    }
}

/**
 * Given the query string, documentResults and lunrResults as used in search(), 
 * edit the DOM to add them in the search results list.
 */
function displaySearchResults(_query, documentResults, lunrResults){
  resetResultList();
  documentResults.forEach((dobj) => {
    results_list.appendChild(buildSearchResult(dobj));
  });

  if (lunrResults.length > 500){
    setWarning("Your search yielded a lot of results! Maybe try with other terms?");
  }

  let publicResults = documentResults.filter(function(value){
    return !value.querySelector('.privacy').innerHTML.includes("PRIVATE");
  })

  if (publicResults.length==0){
    setStatus('No results matches "' + htmlEncode(_query) + '". Some private objects matches your search though.');
  }
  else{
    setStatus(
      'Search for "' + htmlEncode(_query) + '" yielded ' + publicResults.length + ' ' +
      (publicResults.length === 1 ? 'result' : 'results') + '.');
  }
}

function _isSearchInDocstringsEnabled() {
  return searchInDocstringsCheckbox.checked;
}

function toggleSearchInDocstrings() {
  if (searchInDocstringsCheckbox.checked){
    searchInDocstringsButton.classList.add('label-success')
  }
  else{
    if (searchInDocstringsButton.classList.contains('label-success')){
      searchInDocstringsButton.classList.remove('label-success')
    }
  }
  if (input.value.length>0){
    launchSearch(true)
  }
}

////// SETUP //////

// Attach launchSearch() to search text field update events.

input.oninput = (event) => {
  setTimeout(() =>{
    searchAsYouType();
  }, 0);
};
input.onkeyup = (event) => {
  if (event.key === 'Enter') {
    launchSearch(true);
  }
};
input.onfocus = (event) => {
  // Ensure the search bar is set-up.
  // Load fullsearchindex.json, searchindex.json and all-documents.html to have them in the cache asap.
  isSearchReadyPromise = _getIsSearchReadyPromise();
}
document.onload = (event) => { 
  // Set-up search bar.
  setTimeout(() =>{
    isSearchReadyPromise = _getIsSearchReadyPromise(); 
  }, 500);
}

// Close the dropdown if the user clicks on echap key
document.addEventListener('keyup', (evt) => {
  evt = evt || window.event;
  if (evt.key === "Escape" || evt.key === "Esc") {
      hideResultContainer();
  }
});

// Init search and help text. 
// search box is not visible by default because
// we don't want to show it if the browser do not support JS.
window.addEventListener('load', (event) => {
  document.getElementById('search-box-container').style.display = 'block';
  document.getElementById('search-help-box').style.display = 'block';
  hideResultContainer();
});

// This listener does 3 things.
window.addEventListener("click", (event) => {
  if (event){
      // 1. Hide the dropdown if the user clicks outside of it  
      if (!event.target.closest('#search-results-container') 
          && !event.target.closest('#search-box')
          && !event.target.closest('#search-help-button')){
            hideResultContainer();
            return;
      }
      
      // 2. Show the dropdown if the user clicks inside the search box
      if (event.target.closest('#search-box')){
        if (input.value.length>0){
          showResultContainer();
          return;
        }
      }
      
      // 3.Hide the dropdown if the user clicks on a link that brings them to the same page.
      // This includes links in summaries.
      link = event.target.closest('#search-results a')
      if (link){
        page_parts = document.location.pathname.split('/')
        current_page = page_parts[page_parts.length-1]
        href = link.getAttribute("href");
        
        if (!href.startsWith(current_page)){
          // The link points to something not in the same page, so don't hide the dropdown.
          // The page will be reloaded anyway, but this ensure that if we go back, the dropdown will
          // still be expanded.
          return;
        }
        if (event.ctrlKey || event.shiftKey || event.metaKey){ 
          // The link is openned in a new window/tab so don't hide the dropdown.
          return;
        }
        hideResultContainer();
      }
  }
});
