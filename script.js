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

const BURN_ADDRESS = '0xCafE541c1c89766d34995f101Be5A669657846Ac'.toLowerCase();
const NETWORKS = {
    eth: {
        name: 'Ethereum',
        apiBase: 'https://api.etherscan.io/api',
        apiKey: '1TCNRGCPUZZEYKVZ3UATZU2ZWCZZ198PQN'
    },
    bsc: {
        name: 'Binance Smart Chain',
        apiBase: 'https://api.bscscan.com/api',
        apiKey: '1TCNRGCPUZZEYKVZ3UATZU2ZWCZZ198PQN'
    }
};
const ERC20_TRANSFER_TOPIC = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';

function padHexAddress(address) {
    return '0x' + address.toLowerCase().replace(/^0x/, '').padStart(64, '0');
}

function getNetworkConfig(chain) {
    return NETWORKS[chain] || NETWORKS.eth;
}

async function fetchTransactionReceipt(txHash, chain) {
    const network = getNetworkConfig(chain);
    if (!network.apiKey || network.apiKey.startsWith('REPLACE_WITH_YOUR_')) {
        throw new Error(`${network.name} API key is not configured. Replace the API key in script.js.`);
    }

    const url = `${network.apiBase}?module=proxy&action=eth_getTransactionReceipt&txhash=${txHash}&apikey=${network.apiKey}`;
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    const data = await response.json();
    if (!data || !data.result) {
        throw new Error('Transaction receipt not found');
    }
    return data.result;
}

async function fetchTransactionReceiptWithFallback(txHash, preferredChain) {
    const chainOrder = [preferredChain, ...Object.keys(NETWORKS).filter(chain => chain !== preferredChain)];
    let lastError = null;

    for (const chain of chainOrder) {
        try {
            const receipt = await fetchTransactionReceipt(txHash, chain);
            return {
                receipt,
                chain,
                network: getNetworkConfig(chain)
            };
        } catch (error) {
            lastError = error;
            const message = (error.message || '').toLowerCase();
            if (message.includes('api key is not configured') || message.includes('network response was not ok')) {
                throw error;
            }
        }
    }

    throw lastError || new Error('Unable to retrieve transaction receipt from configured networks.');
}

function transactionIncludesBurn(receipt) {
    if (receipt.to && receipt.to.toLowerCase() === BURN_ADDRESS) {
        return true;
    }

    if (Array.isArray(receipt.logs)) {
        const burnTopic = padHexAddress(BURN_ADDRESS);
        return receipt.logs.some(log => {
            if (log.address && log.address.toLowerCase() === BURN_ADDRESS) {
                return true;
            }
            if (log.topics && log.topics.length >= 3 && log.topics[0] === ERC20_TRANSFER_TOPIC) {
                return log.topics[2] === burnTopic || log.topics[1] === burnTopic;
            }
            return false;
        });
    }

    return false;
}

function showPopup4State(title, message, showSuccess) {
    document.getElementById('popup4Title').textContent = title;
    document.getElementById('popup4Message').textContent = message;
    document.getElementById('loadingSpinner').style.display = showSuccess ? 'none' : 'flex';
    const successIcon = document.getElementById('successIcon');
    if (successIcon) {
        successIcon.style.display = showSuccess ? 'flex' : 'none';
    }
}

// Transaction hash confirmation handler
document.getElementById('popup3').addEventListener('click', async function(e) {
    if (e.target.id === 'confirmTxBtn') {
        const txHash = document.getElementById('txHashInput').value.trim();
        
        if (!txHash) {
            alert('Please enter a transaction hash');
            return;
        }

        const normalizedHash = txHash.startsWith('0x') ? txHash : `0x${txHash}`;
        if (!/^0x[0-9a-fA-F]{64}$/.test(normalizedHash)) {
            alert('Please enter a valid 66-character transaction hash');
            return;
        }
        
        const selectedChain = document.getElementById('chainSelect').value;
        const network = getNetworkConfig(selectedChain);

        document.getElementById('popup3').classList.remove('active');
        document.getElementById('popup4').classList.add('active');
        updateFooterVisibility();

        showPopup4State(`Confirming on ${network.name}...`, 'Please wait while we verify your transaction', false);

        try {
            const result = await fetchTransactionReceiptWithFallback(normalizedHash, selectedChain);
            const receipt = result.receipt;
            const foundNetwork = result.network;
            const foundChain = result.chain;
            const chainLabel = foundChain === selectedChain ? foundNetwork.name : `${foundNetwork.name} (detected)`;

            if (receipt.status && receipt.status !== '0x1') {
                showPopup4State('Transaction Failed', 'The transaction was mined but failed. Please check the hash or try a different one.', false);
                return;
            }

            const burnFound = transactionIncludesBurn(receipt);
            if (burnFound) {
                showPopup4State('Burn Confirmed', `Transaction hash confirms a transfer to the official burn address on ${chainLabel}.`, true);
            } else {
                showPopup4State('No Burn Detected', `This transaction does not appear to send tokens to the burn address on ${chainLabel}.`, false);
            }
        } catch (error) {
            console.error(error);
            showPopup4State('Verification Error', error.message || 'Unable to verify transaction. Please try again later.', false);
        }
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

// Copy burn address button
const copyBtn = document.getElementById('copyBtn');
const burnAddress = document.getElementById('burnAddress');
if (copyBtn && burnAddress) {
    copyBtn.addEventListener('click', function() {
        const textToCopy = burnAddress.textContent.trim();
        if (!textToCopy) {
            alert('Burn address is not available to copy.');
            return;
        }

        navigator.clipboard.writeText(textToCopy).then(function() {
            copyBtn.textContent = 'Copied!';
            setTimeout(function() {
                copyBtn.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                    </svg>
                `;
            }, 1200);
        }).catch(function() {
            alert('Unable to copy address. Please try again.');
        });
    });
}
