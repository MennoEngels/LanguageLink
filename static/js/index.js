// Get elements from the DOM
var input = document.getElementById('text');
var currentWordLabel = document.getElementById('currentword');
var scoreBar = document.getElementById('score');
var player = document.getElementById('player');
var soundEffect = document.getElementById('soundeffect');
var startButton = document.getElementById('start');
var replayButton = document.getElementById('replay');
var correctLabel = document.getElementById('correct');
// Game state
var isGamePlaying = true;
var currentWordId = 0;
var delayEnter = false;
var wrongWord = false;
// Settings
var MAX_LEARNING_WORDS = 10;
var MAX_REVIEW_WORDS = 20;
var SHUFFLE = true;
// Dev mode
var DEV_MODE = false;
var words = [];
var step = 0;
// This function runs when the window loads
window.onload = function () {
    console.log("ONLOAD");
    // Get the ID of the current page from the URL path
    var id = window.location.pathname.split("/").pop();
    console.log(id);
    // Fetch the JSON data
    fetchJSON('GET', "/slides/".concat(id), function onSuccess(slides) {
        words = slides;
        console.log(words);
        // Calculate how much the score bar should increase per word
        step = 100 / words.length;
    }, function onError(status, response) {
        alert("".concat(status, " - ").concat(response));
    });
};
var playsoundeffect = function (audio) {
    soundEffect.src = "/audio/".concat(audio);
    soundEffect.play();
};
var playsound = function (audio) {
    player.src = "/audio/".concat(audio);
    player.play();
};
function fetchJSON(method, url, onSuccess, onError) {
    var request = new XMLHttpRequest();
    request.open(method, url, true);
    request.onload = function () {
        // If loading is complete
        if (request.readyState === 4) {
            // if the request was successful
            if (request.status === 200) {
                var data = void 0;
                // Parse the JSON in the response
                try {
                    data = JSON.parse(request.responseText);
                }
                catch (error) {
                    onError(request.status, error.toString());
                }
                onSuccess(data);
            }
            else {
                onError(request.status, request.responseText);
            }
        }
    };
    request.send();
}
//# sourceMappingURL=index.js.map