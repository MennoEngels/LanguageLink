
startButton.addEventListener("click", function (e) {
    soundEffect.src = `/audio/Glass`
    currentWordLabel.innerHTML = words[0].back;
})

replayButton.addEventListener("click", function (e) {
    playsound(words[currentWordId].audio)
})

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
async function pauseinput(): Promise<void> {
    delayEnter = true;
    setTimeout(function () {
        delayEnter = false;
    }, 500);
}

const resetinput = () => {
    wrongWord = false;
    input.classList.remove("wrong_answer")
    input.disabled = false;
    currentWordId += 1;
    currentWordLabel.innerHTML = words[currentWordId].back;
    input.value = "";
    correctLabel.innerHTML = '';
}

const end_lesson = () => {
    isGamePlaying = false;
    currentWordLabel.innerHTML = "끝끝끝끝끝끝끝끝"
}

const correct_answer = () => {
    playsoundeffect('Glass')

    // Update score
    scoreBar.value += step;

    input.value = "";

    // If this was the last word in the lesson, end the lesson
    if (currentWordId+1 == words.length) {
        end_lesson()
    } else {
        // Otherwise, move to the next word
        currentWordId += 1;
        currentWordLabel.innerHTML = words[currentWordId].back;
    }
}

const wrong_answer = () => {
    playsoundeffect('Sosumi')
    input.disabled = true;

    // Update the score step
    step = (100 - scoreBar.value) / (words.length - currentWordId);

    correctLabel.innerHTML = 'Correct answer: ' + words[currentWordId].front;

    // Move the current word to the end of the list, highlight the input as incorrect
    words.splice(currentWordId + 2, 0, words[currentWordId])
    input.classList.add("wrong_answer")

    wrongWord = true;
}

function submit_input() {
    const value = input.value;
    // Check if submitted value is correct
    if (value == words[currentWordId].front) {
        correct_answer()
    } else {
        wrong_answer()
    }
    if (DEV_MODE) {
        input.value = words[currentWordId].front
    }
}
