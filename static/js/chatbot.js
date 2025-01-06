// Handle sending a message
function sendMessage() {
    const userInput = document.getElementById('user-input').value.trim();
    if (!userInput) return;

    addMessage(userInput, 'user');
    document.getElementById('user-input').value = '';

    const typingDiv = showTypingIndicator();

    // Simulate bot response after delay
    setTimeout(async () => {
        typingDiv.remove();
        const botResponse = await generateBotResponse(userInput);
        addMessage(botResponse, 'bot');
        saveChatHistory();
    }, 1000);
}

// Generate bot response
async function generateBotResponse(input) {
    console.log(input);
    let query=input;
    const response = await fetch('/chatbot_response', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            query,
            
        })
    });
    // console.log( await response.json());
    const bot_response = await response.json();
    const bot_response_text = bot_response["response"];
    console.log(bot_response_text);
    return bot_response_text;
}

// Add message to chat
function addMessage(message, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);

    const messageText = document.createElement('div');
    messageText.classList.add('message-text');
    messageText.textContent = message;

    messageDiv.appendChild(messageText);
    document.getElementById('chat-body').appendChild(messageDiv);

    scrollToBottom();
}

// Show typing indicator
function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.classList.add('typing-indicator');
    typingDiv.innerHTML = '<span></span><span></span><span></span>';
    document.getElementById('chat-body').appendChild(typingDiv);
    scrollToBottom();
    return typingDiv;
}

// Scroll to bottom
function scrollToBottom() {
    const chatBody = document.getElementById('chat-body');
    chatBody.scrollTop = chatBody.scrollHeight;
}

// Handle Enter key
function handleEnter(event) {
    if (event.key === 'Enter') sendMessage();
}

// Save chat history
function saveChatHistory() {
    const chatBody = document.getElementById('chat-body').innerHTML;
    localStorage.setItem('chatHistory', chatBody);
}

// Load chat history
function loadChatHistory() {
    const savedChat = localStorage.getItem('chatHistory');
    if (savedChat) {
        document.getElementById('chat-body').innerHTML = savedChat;
        scrollToBottom();
    }
}

// Clear chat history
function clearChat() {
    document.getElementById('chat-body').innerHTML = '';
    localStorage.removeItem('chatHistory');
}

// Get Account Balance
function getAccountBalance() {
    const balance = 5000; // You would pull this from your bank API
    return `Your current account balance is $${balance}.`;
}

// Get Transaction History
function getTransactionHistory() {
    return "Recent Transactions:\n1. Deposit: $1000\n2. Withdrawal: $200\n3. Payment: $150";
}
document.getElementById("textForm").addEventListener("submit", async function(event) {
    event.preventDefault();  // Prevent form submission (default behavior)
    
    // Get the input value
    const inputText = document.getElementById("account-number").value;
    let account_no = inputText;
    const response = await fetch('/chatbot_acc_no', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            account_no,
            
        })
    });
    
    let result = await response.json();
    let result_text = result.response;
    let chat = document.getElementById('chat-container');
    let details = document.getElementById('details');
    
    if(result_text == "Details loaded, ask queries."){
        document.getElementById("result").innerText = "Entered Account Number : " + inputText;
        chat.style.display = 'flex';
        details.style.display = 'none';
    }
    else{
        document.getElementById("result").innerText = "Entered Account Number does not exists";
    }

    // Display the input or process it
    

    // Optionally, clear the input field
    document.getElementById("account-number").value = "";
});
// function getAccountNumber(){
//     const accountNumbers = [
//         "1234567890",
//         "9876543210",
//         "4567891230",
//         "7891234560",
//         "3216549870"
//     ];
//     let chat = document.getElementById('chat-container');
//     let details = document.getElementById('details');
//     let userAccountNumber = document.getElementById('account-number').value;
//     if(accountNumbers.includes(userAccountNumber))
//     {
//         chat.style.display = 'flex';
//         details.style.display = 'none';
//     }
//     else{
//         let error = document.createElement('h4');
//         error.textContent = "Sorry We Couldn't Find Your Account.";
//         error.style.fontWeight = 500;
//         error.style.marginTop = '10px';
//         details.appendChild(error);
//     }
// }



// Initialize chatbot
window.onload = () => {
    loadChatHistory();
};
