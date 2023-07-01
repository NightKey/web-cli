
setInterval(
    function() {
        $.getJSON(
            "/fetch",
            function(data) {
                let content = $("#content");
                let userValue = "";
                if (content.find('#FIX_input')[0] !== undefined) {
                    userValue = content.find('#FIX_input')[0].value;
                }
                let blocks = "";
                console.log(data);
                for (let index in data) {
                    let block = data[index];
                    blocks += "<div id=\"" + block["hash"] + "\">\n";
                    blocks += "<div class=\"user\">" + consolName + "> <input type=\"text\" id=\"" + block["hash"] + "_input\" value=\"" + block["command"] + "\" readonly></div>";
                    blocks += "<div class=\"response\">";
                    for (let index in block["response"]) {
                        let line = block["response"][index];
                        blocks += "<div>" + line + "</div>";
                    }
                    blocks += "</div></div>\n";
                }
                maxHistorySize = Object.keys(data).length;
                if (shouldShowFix) {
                    blocks += "<div id=\"FIX\"><div class=\"user\">" + consolName + "> <input type=\"text\" id=\"FIX_input\" autocomplete=\"off\"></div></div>";
                }
                content.html(blocks);
                if (shouldShowFix) {
                    let input = content.find('#FIX_input')[0];
                    input.focus();
                    input.value = userValue;
                }
            }
        );
    },
    250
);

seekHistory = function(up) {
    if (up) {
        currentHistoryIndex --;
    } else {
        currentHistoryIndex ++;
    }
    if (maxHistorySize*-1 > currentHistoryIndex) {
        currentHistoryIndex = maxHistorySize*-1;
    } else if (currentHistoryIndex > 0) {
        currentHistoryIndex = 0
    }
    if (currentHistoryIndex !== 0) {
        $.get(
            `/getHistory?index=${currentHistoryIndex}`,
            currentHistoryIndex,
            function(data) {
                $("#FIX_input")[0].value = data;
            }
        )
    } else {
        $("#FIX_input")[0].value = "";
    }
}

send = function() {
    let command = $("#FIX_input")[0].value;
    $("#FIX_input")[0].value = "";
    shouldShowFix = false;
    $.ajax({
        url: "/send",
        type: "PUT",
        contentType: "text/plain",
        data: command,
        success: function(response) {
            console.log("SENT");
            console.log(response);
            shouldShowFix = true;
        }
    })
}

$(document).ready(function() {
    $('#content').on("keyup", "#FIX_input", function(event) { 
        console.log(event);
        if (event.keyCode == '38') {
            console.log("UP ARROW");
            seekHistory(true);
        }
        else if (event.keyCode == '40') {
            console.log("DOWN ARROW");
            seekHistory(false);
        }
        else if (event.keyCode == '13') {
            console.log("RETURN");
            send();
        }
     });
});