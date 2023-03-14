var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
startButton.addEventListener("click", function (e) {
    soundEffect.src = "/audio/Glass";
    currentWordLabel.innerHTML = words[0].back;
});
replayButton.addEventListener("click", function (e) {
    playsound(words[currentWordId].audio);
});
// Submit input when user hits enter
input.addEventListener("keydown", function (e) {
    if (e.code === "Enter" && isGamePlaying && !delayEnter && !wrongWord) {
        pauseinput();
        submit_input();
    }
});
document.addEventListener("keydown", function (e) {
    if (e.code === "Enter" && isGamePlaying && !delayEnter && wrongWord) {
        resetinput();
    }
});
// This function implements a delay to prevent the user from rapidly submitting multiple answers 
function pauseinput() {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            delayEnter = true;
            setTimeout(function () {
                delayEnter = false;
            }, 500);
            return [2 /*return*/];
        });
    });
}
var resetinput = function () {
    wrongWord = false;
    input.classList.remove("wrong_answer");
    input.disabled = false;
    currentWordId += 1;
    currentWordLabel.innerHTML = words[currentWordId].back;
    input.value = "";
    correctLabel.innerHTML = '';
};
var end_lesson = function () {
    isGamePlaying = false;
    currentWordLabel.innerHTML = "끝끝끝끝끝끝끝끝";
};
var correct_answer = function () {
    playsoundeffect('Glass');
    // Update score
    scoreBar.value += step;
    input.value = "";
    // If this was the last word in the lesson, end the lesson
    if (currentWordId + 1 == words.length) {
        end_lesson();
    }
    else {
        // Otherwise, move to the next word
        currentWordId += 1;
        currentWordLabel.innerHTML = words[currentWordId].back;
    }
};
var wrong_answer = function () {
    playsoundeffect('Sosumi');
    input.disabled = true;
    // Update the score step
    step = (100 - scoreBar.value) / (words.length - currentWordId);
    correctLabel.innerHTML = 'Correct answer: ' + words[currentWordId].front;
    // Move the current word to the end of the list, highlight the input as incorrect
    words.splice(currentWordId + 2, 0, words[currentWordId]);
    input.classList.add("wrong_answer");
    wrongWord = true;
};
function submit_input() {
    var value = input.value;
    // Check if submitted value is correct
    if (value == words[currentWordId].front) {
        correct_answer();
    }
    else {
        wrong_answer();
    }
    if (DEV_MODE) {
        input.value = words[currentWordId].front;
    }
}
//# sourceMappingURL=writing.js.map