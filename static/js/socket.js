// Connect to Socket.IO server
const socket = io();

// Handle connection status
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

// Handle vote updates on results page
socket.on('vote_update', (data) => {
    console.log('Vote update received:', data);
    
    // Check if we're on the results page
    const resultsContainer = document.getElementById('results-container');
    if (!resultsContainer) return;
    
    // Update vote counts and percentages
    const optionVotes = data.option_votes;
    let totalVotes = 0;
    
    // Calculate total votes
    Object.values(optionVotes).forEach(count => {
        totalVotes += count;
    });
    
    // Update each option's display
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
    
    // Update total votes count
    const totalVotesElement = document.getElementById('total-votes');
    if (totalVotesElement) {
        totalVotesElement.textContent = totalVotes;
    }
});

// Handle question updates
let lastQuestionId = null;

socket.on('question_update', (data) => {
    console.log('Question update received:', data);
    
    // Only reload if this is a new question (different ID)
    if (lastQuestionId !== null && lastQuestionId !== data.id) {
        console.log('New question detected, reloading page');
        if (window.location.pathname === '/vote' || 
            window.location.pathname === '/' || 
            window.location.pathname === '/results') {
            location.reload();
        }
    }
    
    // Update the last question ID
    lastQuestionId = data.id;
});
