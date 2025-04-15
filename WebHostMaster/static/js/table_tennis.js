// Table Tennis specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Get match elements
    const matchContainer = document.getElementById('match-container');
    
    if (!matchContainer) return;
    
    const matchId = matchContainer.dataset.matchId;
    const player1ScoreElement = document.getElementById('player1-score');
    const player2ScoreElement = document.getElementById('player2-score');
    const player1ScoreBtn = document.getElementById('player1-score-btn');
    const player2ScoreBtn = document.getElementById('player2-score-btn');
    const currentSetElement = document.getElementById('current-set');
    const setIndicatorsElement = document.getElementById('set-indicators');
    const matchStatusElement = document.getElementById('match-status');
    
    // Check if match is already complete
    const matchComplete = matchContainer.dataset.matchComplete === 'True';
    if (matchComplete) {
        if (player1ScoreBtn) player1ScoreBtn.disabled = true;
        if (player2ScoreBtn) player2ScoreBtn.disabled = true;
        return;
    }
    
    // Add event listeners to score buttons
    if (player1ScoreBtn) {
        player1ScoreBtn.addEventListener('click', () => updateScore('player1'));
    }
    
    if (player2ScoreBtn) {
        player2ScoreBtn.addEventListener('click', () => updateScore('player2'));
    }
    
    // Function to update score
    function updateScore(player) {
        // Disable buttons during API call
        if (player1ScoreBtn) player1ScoreBtn.disabled = true;
        if (player2ScoreBtn) player2ScoreBtn.disabled = true;
        
        fetch(`/api/match/${matchId}/score`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ player: player }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Update the UI with the new scores
            if (player1ScoreElement) player1ScoreElement.textContent = data.player1_score;
            if (player2ScoreElement) player2ScoreElement.textContent = data.player2_score;
            
            // If set is completed
            if (data.set_completed) {
                // Show set winner message
                if (matchStatusElement) {
                    matchStatusElement.textContent = `Set ${data.current_set} won by ${data.set_winner}!`;
                    matchStatusElement.classList.remove('d-none');
                }
                
                // Update set indicators
                updateSetIndicators();
                
                // If match is completed
                if (data.match_completed) {
                    if (matchStatusElement) {
                        matchStatusElement.textContent = `Match won by ${data.match_winner}!`;
                        matchStatusElement.classList.add('text-success', 'fw-bold');
                    }
                    
                    // Disable score buttons permanently
                    if (player1ScoreBtn) player1ScoreBtn.disabled = true;
                    if (player2ScoreBtn) player2ScoreBtn.disabled = true;
                    
                    // Show match summary
                    showMatchSummary();
                } else {
                    // Update current set indicator
                    if (currentSetElement) {
                        currentSetElement.textContent = parseInt(data.current_set) + 1;
                    }
                    
                    // Enable buttons for next set
                    setTimeout(() => {
                        if (player1ScoreBtn) player1ScoreBtn.disabled = false;
                        if (player2ScoreBtn) player2ScoreBtn.disabled = false;
                    }, 1000);
                }
            } else {
                // Re-enable buttons
                if (player1ScoreBtn) player1ScoreBtn.disabled = false;
                if (player2ScoreBtn) player2ScoreBtn.disabled = false;
            }
        })
        .catch(error => {
            console.error('Error updating score:', error);
            // Re-enable buttons
            if (player1ScoreBtn) player1ScoreBtn.disabled = false;
            if (player2ScoreBtn) player2ScoreBtn.disabled = false;
            
            // Show error message
            if (matchStatusElement) {
                matchStatusElement.textContent = 'Error updating score. Please try again.';
                matchStatusElement.classList.remove('d-none');
                matchStatusElement.classList.add('text-danger');
            }
        });
    }
    
    // Function to update set indicators
    function updateSetIndicators() {
        if (!setIndicatorsElement) return;
        
        fetch(`/match/${matchId}`)
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newSetIndicators = doc.getElementById('set-indicators');
                
                if (newSetIndicators) {
                    setIndicatorsElement.innerHTML = newSetIndicators.innerHTML;
                }
            })
            .catch(error => console.error('Error updating set indicators:', error));
    }
    
    // Function to show match summary
    function showMatchSummary() {
        const matchSummaryElement = document.getElementById('match-summary');
        if (!matchSummaryElement) {
            console.log("Match summary element not found, redirecting to rankings");
            // If the match summary element doesn't exist, redirect to the rankings page
            setTimeout(() => {
                window.location.href = '/rankings';
            }, 2000);
            return;
        }
        
        fetch(`/match/${matchId}`)
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newMatchSummary = doc.getElementById('match-summary');
                
                if (newMatchSummary) {
                    matchSummaryElement.innerHTML = newMatchSummary.innerHTML;
                    matchSummaryElement.classList.remove('d-none');
                }
            })
            .catch(error => console.error('Error loading match summary:', error));
    }
});
