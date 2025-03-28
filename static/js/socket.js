const socket = io();

socket.on('connect', () => {
    console.log('Connected to server');
    document.getElementById('connection-status').textContent = 'Connected';
    document.getElementById('connection-status').classList.remove('text-danger');
    document.getElementById('connection-status').classList.add('text-success');
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
    document.getElementById('connection-status').textContent = 'Disconnected';
    document.getElementById('connection-status').classList.remove('text-success');
    document.getElementById('connection-status').classList.add('text-danger');
});

socket.on('vote_update', (data) => {
    console.log('Vote update received:', data);
    const resultsContainer = document.getElementById('results-container');
    if (!resultsContainer) return;
    const optionVotes = data.option_votes;
    let totalVotes = 0;
    Object.values(optionVotes).forEach(count => {
        totalVotes += count;
    });
    Object.keys(optionVotes).forEach(optionId => {
        const voteCount = optionVotes[optionId];
        const voteCountElement = document.getElementById(`vote-count-${optionId}`);
        const progressBar = document.getElementById(`progress-bar-${optionId}`);
        const percentageElement = document.getElementById(`percentage-${optionId}`);
        if (voteCountElement) {
            voteCountElement.textContent = voteCount;
        }
        if (progressBar && percentageElement) {
            const percentage = totalVotes > 0 ? Math.round((voteCount / totalVotes) * 100) : 0;
            progressBar.style.width = `${percentage}%`;
            progressBar.setAttribute('aria-valuenow', percentage);
            percentageElement.textContent = `${percentage}%`;
        }
    });
    const totalVotesElement = document.getElementById('total-votes');
    if (totalVotesElement) {
        totalVotesElement.textContent = totalVotes;
    }
});

let lastQuestionId = null;

socket.on('question_update', (data) => {
    console.log('Question update received:', data);
    if (lastQuestionId !== null && lastQuestionId !== data.id) {
        console.log('New question detected, reloading page');
        if (window.location.pathname === '/vote' || 
            window.location.pathname === '/' || 
            window.location.pathname === '/results') {
            location.reload();
        }
    }
    lastQuestionId = data.id;
});

// Add an event listener for the `new_question` event to play a sound notification
socket.on('new_question', (data) => {
    console.log('New question received:', data);
    playNotificationSound();
});

// Add a function to play a sound when a new question arrives
function playNotificationSound() {
    const audio = new Audio('/static/sounds/notification.mp3');
    audio.play();
}
