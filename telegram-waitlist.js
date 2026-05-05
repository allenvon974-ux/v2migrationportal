// Generate realistic Telegram usernames
function generateUsername(index) {
    const prefixes = ['crypto', 'pepe', 'zeus', 'doge', 'moon', 'bull', 'hodl', 'ape', 'diamond', 'rocket', 'mars', 'lambo', 'alpha', 'omega', 'king', 'queen', 'warrior', 'ninja', 'ghost', 'shadow', 'wolf', 'eagle', 'tiger', 'lion', 'bear', 'fox', 'cat', 'dog', 'bird', 'fish'];
    const suffixes = ['master', 'lord', 'god', 'pro', 'max', 'ultra', 'mega', 'super', 'elite', 'legend', 'hero', 'star', 'moon', 'sun', 'fire', 'ice', 'storm', 'thunder', 'lightning', 'power', 'force', 'energy', 'spirit', 'soul', 'mind', 'heart', 'blade', 'sword', 'shield', 'armor'];
    const numbers = ['', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '99', '100', '200', '300', '500', '666', '777', '888', '999', '2024', '2025'];
    const cryptoTerms = ['btc', 'eth', 'bnb', 'sol', 'ada', 'dot', 'link', 'matic', 'avax', 'atom', 'algo', 'near', 'ftm', 'arb', 'op', 'base', 'poly', 'zksync', 'stark', 'aptos'];
    const memeTerms = ['pepe', 'doge', 'shib', 'floki', 'bonk', 'wojak', 'chad', 'gigachad', 'based', 'cringe', 'sus', 'ngmi', 'wagmi', 'gm', 'gn', 'ser', 'anon', 'degen', 'normie', 'whale'];
    
    const patterns = [
        () => `${prefixes[Math.floor(Math.random() * prefixes.length)]}${numbers[Math.floor(Math.random() * numbers.length)]}`,
        () => `${cryptoTerms[Math.floor(Math.random() * cryptoTerms.length)]}_${suffixes[Math.floor(Math.random() * suffixes.length)]}${numbers[Math.floor(Math.random() * numbers.length)]}`,
        () => `${memeTerms[Math.floor(Math.random() * memeTerms.length)]}${suffixes[Math.floor(Math.random() * suffixes.length)]}${numbers[Math.floor(Math.random() * numbers.length)]}`,
        () => `${prefixes[Math.floor(Math.random() * prefixes.length)]}_${suffixes[Math.floor(Math.random() * suffixes.length)]}${numbers[Math.floor(Math.random() * numbers.length)]}`,
        () => `${prefixes[Math.floor(Math.random() * prefixes.length)]}${suffixes[Math.floor(Math.random() * suffixes.length)]}${numbers[Math.floor(Math.random() * numbers.length)]}`,
        () => `x${prefixes[Math.floor(Math.random() * prefixes.length)]}${numbers[Math.floor(Math.random() * numbers.length)]}`,
        () => `${prefixes[Math.floor(Math.random() * prefixes.length)]}x${numbers[Math.floor(Math.random() * numbers.length)]}`,
        () => `${cryptoTerms[Math.floor(Math.random() * cryptoTerms.length)]}${numbers[Math.floor(Math.random() * numbers.length)]}`,
    ];
    
    return patterns[Math.floor(Math.random() * patterns.length)]();
}

// Generate all usernames
function generateAllUsernames(count = 5247) {
    const usernames = new Set();
    
    // Add the required username
    usernames.add('alluvnessie');
    
    // Generate unique usernames
    while (usernames.size < count) {
        const username = generateUsername(usernames.size);
        if (username.length >= 3 && username.length <= 32) {
            usernames.add(username);
        }
    }
    
    return Array.from(usernames);
}

// Initialize the waitlist
let allUsernames = [];
let displayedUsernames = [];

function initializeWaitlist() {
    // Generate usernames
    allUsernames = generateAllUsernames(5247);
    
    // Shuffle to randomize order
    allUsernames = allUsernames.sort(() => Math.random() - 0.5);
    
    // Ensure alluvnessie is visible (add it early in the list)
    const alluvIndex = allUsernames.indexOf('alluvnessie');
    if (alluvIndex > 100) {
        allUsernames.splice(alluvIndex, 1);
        allUsernames.unshift('alluvnessie');
    }
    
    displayedUsernames = [...allUsernames];
    renderMembers();
}

function renderMembers() {
    const membersList = document.getElementById('membersList');
    membersList.innerHTML = '';
    
    displayedUsernames.forEach((username, index) => {
        const memberItem = document.createElement('div');
        memberItem.className = 'member-item';
        
        // Generate random avatar emoji
        const avatars = ['👤', '👨', '👩', '🧑', '👨‍💼', '👩‍💼', '👨‍💻', '👩‍💻', '👨‍🎨', '👩‍🎨', '👨‍🔬', '👩‍🔬', '👨‍🚀', '👩‍🚀', '🧑‍🚀', '🦸', '🦹', '🧙', '🧚', '🧛', '🧜', '🧝', '🧞', '🧟', '💼', '🕴️', '👔', '🎩', '🎭', '🎪'];
        const avatar = avatars[Math.floor(Math.random() * avatars.length)];
        
        // Join time - special case for alluvnessie
        let joinTime;
        if (username === 'alluvnessie') {
            joinTime = '7 days ago';
        } else {
            const daysAgo = Math.floor(Math.random() * 30);
            joinTime = daysAgo === 0 ? 'Today' : daysAgo === 1 ? 'Yesterday' : `${daysAgo} days ago`;
        }
        
        memberItem.innerHTML = `
            <div class="member-avatar">${avatar}</div>
            <div class="member-info">
                <div class="member-username">@${username}</div>
                <div class="member-join-time">Joined ${joinTime}</div>
            </div>
            <div class="member-status ${Math.random() > 0.7 ? 'online' : ''}"></div>
        `;
        
        membersList.appendChild(memberItem);
    });
    
    // Update stats
    document.getElementById('totalMembers').textContent = allUsernames.length.toLocaleString();
    document.getElementById('onlineNow').textContent = Math.floor(allUsernames.length * 0.3).toLocaleString();
}

// Search functionality
document.getElementById('searchInput').addEventListener('input', function(e) {
    const searchTerm = e.target.value.toLowerCase().trim();
    
    if (searchTerm === '') {
        displayedUsernames = [...allUsernames];
    } else {
        displayedUsernames = allUsernames.filter(username => 
            username.toLowerCase().includes(searchTerm)
        );
    }
    
    renderMembers();
});

// Apply button functionality
document.querySelector('.apply-btn').addEventListener('click', function() {
    alert('Application submitted! You will be notified when your request is approved.');
});

// Initialize on load
document.addEventListener('DOMContentLoaded', initializeWaitlist);
