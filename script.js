const footer = document.querySelector('.footer');

// Function to check if any popup is active
function updateFooterVisibility() {
    const popups = document.querySelectorAll('.popup.active');
    if (popups.length > 0) {
        footer.classList.add('hidden');
    } else {
        footer.classList.remove('hidden');
    }
}

// Back buttons
document.getElementById('backBtn1').addEventListener('click', function() {
    document.getElementById('popup2').classList.remove('active');
    document.getElementById('popup1').classList.add('active');
    updateFooterVisibility();
});

document.getElementById('backBtn2').addEventListener('click', function() {
    document.getElementById('popup3').classList.remove('active');
    document.getElementById('popup2').classList.add('active');
    updateFooterVisibility();
});

// Observe popup changes
document.getElementById('popup1').addEventListener('click', function(e) {
    if (e.target.id === 'migrateBtn') {
        document.getElementById('popup1').classList.remove('active');
        document.getElementById('popup2').classList.add('active');
        updateFooterVisibility();
    }
});

document.getElementById('popup2').addEventListener('click', function(e) {
    if (e.target.id === 'confirmBurnBtn') {
        document.getElementById('popup2').classList.remove('active');
        document.getElementById('popup3').classList.add('active');
        updateFooterVisibility();
    }
});

// Transaction hash confirmation handler
document.getElementById('popup3').addEventListener('click', function(e) {
    if (e.target.id === 'confirmTxBtn') {
        const txHash = document.getElementById('txHashInput').value.trim();
        
        // Validate transaction hash
        if (!txHash) {
            alert('Please enter a transaction hash');
            return;
        }
        
        // Hide popup3 and show popup4 with "Confirming..." message
        document.getElementById('popup3').classList.remove('active');
        document.getElementById('popup4').classList.add('active');
        
        // Reset popup4 to show confirming state
        document.getElementById('popup4Title').textContent = 'Confirming...';
        document.getElementById('popup4Message').textContent = 'Please wait while we verify your transaction';
        document.getElementById('loadingSpinner').style.display = 'flex';
        document.getElementById('successIcon').style.display = 'none';
        
        updateFooterVisibility();
        
        // After 3 seconds, update to confirmed state
        setTimeout(function() {
            document.getElementById('popup4Title').textContent = 'Transaction Confirmed';
            document.getElementById('popup4Message').textContent = 'Your address has been added to the airdrop slot';
            document.getElementById('loadingSpinner').style.display = 'none';
            document.getElementById('successIcon').style.display = 'flex';
        }, 3000);
    }
});

// Coming Soon functionality
function showComingSoon() {
    document.getElementById('comingSoonOverlay').classList.add('show');
    document.getElementById('comingSoonModal').classList.add('show');
}

function closeComingSoon() {
    document.getElementById('comingSoonOverlay').classList.remove('show');
    document.getElementById('comingSoonModal').classList.remove('show');
}

// Close Coming Soon when clicking overlay
document.getElementById('comingSoonOverlay').addEventListener('click', closeComingSoon);
