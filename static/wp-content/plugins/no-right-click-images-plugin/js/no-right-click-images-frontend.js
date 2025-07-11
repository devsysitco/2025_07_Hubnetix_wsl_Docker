document.addEventListener("contextmenu", kpg_nrci_cm, false);
if (nrci_opts['drag'] == '1') {
    document.addEventListener("dragstart", kpg_nrci_cm, false);
    document.addEventListener("touchmove", kpg_nrci_cm, false);
}
if (nrci_opts['touch'] == '1') {
    document.addEventListener("touchstart", kpg_nrci_cm, false);
}
if (nrci_opts['gesture'] == '1') {
    document.addEventListener("gesturestart", kpg_nrci_cm, false);
}

function kpg_nrci_block(event) {
    event.cancelBubble = true;
    if (event.preventDefault != undefined) {
        event.preventDefault();
    }
    if (event.stopPropagation != undefined) {
        event.stopPropagation();
    }
    return false;
}

function kpg_nrci_cm(event) {
    try {
        if (event.target.tagName == "IMG") {
            event.cancelBubble = true;
            if (event.preventDefault != undefined) {
                event.preventDefault();
            }
            if (event.stopPropagation != undefined) {
                event.stopPropagation();
            }
            return false;
        }
    } catch (error) {
        console.log("NRI error:" + error);
    }
    try {
        if (event.target.getAttribute("style") == null || event.target.getAttribute("style") == "") {
            return true;
        }
        if (event.target.style.backgroundImage != null && event.target.style.backgroundImage != 'none' && event.target.style.backgroundImage != '') {
            event.cancelBubble = true;
            if (event.preventDefault != undefined) {
                event.preventDefault();
            }
            if (event.stopPropagation != undefined) {
                event.stopPropagation();
            }
            return false;
        }
    } catch (error) {
        console.log("NRI error:" + error);
    }
    return true;
}