// Get elements from the DOM
const input = document.getElementById('text') as HTMLInputElement | null;
const currentWordLabel = document.getElementById('currentword') as HTMLHeadingElement | null;
const scoreBar = document.getElementById('score') as HTMLProgressElement | null;
const player = document.getElementById('player') as HTMLAudioElement | null;
const soundEffect = document.getElementById('soundeffect') as HTMLAudioElement | null;
const startButton = document.getElementById('start') as HTMLButtonElement | null;
const replayButton = document.getElementById('replay') as HTMLButtonElement | null;
const correctLabel = document.getElementById('correct') as HTMLHeadingElement | null;

// Game state
let isGamePlaying = true;
let currentWordId = 0;
let delayEnter = false;
let wrongWord = false;

// Settings
const MAX_LEARNING_WORDS = 10;
const MAX_REVIEW_WORDS = 20;
const SHUFFLE = true;

// Dev mode
const DEV_MODE = false;

interface Word {
    id: number;
    front: string;
    back: string;
    audio: string;
    state: string;
    interval: number;
    easeFactor: number;
    repetitions: number;
    dueDate: Date;
    lastReviewDate: Date;
}

let words: Word[] = [];

let step = 0;

// This function runs when the window loads
window.onload = () => {
    console.log("ONLOAD");

    // Get the ID of the current page from the URL path
    const id = window.location.pathname.split("/").pop();

    console.log(id);

    // Fetch the JSON data
    fetchJSON('GET', `/slides/${id}`,
        function onSuccess(slides: Word[]) {
            words = slides;
            console.log(words);

            // Calculate how much the score bar should increase per word
            step = 100 / words.length;
        },

        function onError(status: number, response: string) {
            alert(`${status} - ${response}`);
        }
    );
};

const playsoundeffect = (audio: string) => {
    soundEffect.src = `/audio/${audio}`;
    soundEffect.play();
}

const playsound = (audio: string) => {
    player.src = `/audio/${audio}`;
    player.play();
}


function fetchJSON(method: string, url: string, onSuccess: (data: Word[]) => void, onError: (status: number, response: string) => void) {
    const request = new XMLHttpRequest();
    request.open(method, url, true);
    request.onload = () => {
        // If loading is complete
        if (request.readyState === 4) {
            // if the request was successful
            if (request.status === 200) {
                let data: Word[];

                // Parse the JSON in the response
                try {
                    data = JSON.parse(request.responseText);
                } catch (error) {
                    onError(request.status, error.toString());
                }

                onSuccess(data);
            } else {
                onError(request.status, request.responseText);
            }
        }
    };

    request.send();
}