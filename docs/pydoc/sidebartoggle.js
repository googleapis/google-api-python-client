// Cookie manipulation functions, from https://www.w3schools.com/js/js_cookies.asp

function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    var expires = "expires="+d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}
  
function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
        c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
        }
    }
    return "";
}

// Toogle sidebar collapse

function initSideBarCollapse() {
    var collapsed = getCookie("pydoctor-sidebar-collapsed");
    if (collapsed == "yes") {
        document.body.classList.add("sidebar-collapsed");
    }
    if (collapsed == ""){
        setCookie("pydoctor-sidebar-collapsed", "no", 365);
    }
    updateSideBarCollapse();
}

function toggleSideBarCollapse() {
    if (document.body.classList.contains('sidebar-collapsed')){
        document.body.classList.remove('sidebar-collapsed');
        setCookie("pydoctor-sidebar-collapsed", "no", 365);
    }
    else {
        document.body.classList.add("sidebar-collapsed");
        setCookie("pydoctor-sidebar-collapsed", "yes", 365);
    }
    
    updateSideBarCollapse();
}

function updateSideBarCollapse() {
    let link = document.querySelector('#collapseSideBar a')
    // Since this script is called before the page finishes the parsing,
    // link is undefined when it's first called. 
    if (link!=undefined){
        var collapsed = document.body.classList.contains('sidebar-collapsed');
        link.innerText = collapsed ? '»' : '«';
    }
    // Fixes renderring issue with safari. 
    // https://stackoverflow.com/a/8840703
    var sidebarcontainer = document.querySelector('.sidebarcontainer');
    sidebarcontainer.style.display='none';
    sidebarcontainer.offsetHeight; // no need to store this anywhere, the reference is enough
    // Set the sidebar display on load to avoid showing it for few miliseconds when loading..
    sidebarcontainer.style.display='flex';
    
}

initSideBarCollapse();
