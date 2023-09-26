document.addEventListener("DOMContentLoaded", () => {
    const chatInput = document.getElementById("user-input");
    const sendButton = document.getElementById("send-button");
    const chatMessages = document.getElementById("chat-messages");

    // Function to add a new message to the chatbox
    const appendMessage = (message, className) => {
        const messageLi = document.createElement("li");
        messageLi.classList.add("chat", className);
        messageLi.textContent = message;
        chatMessages.appendChild(messageLi);
    };

    // Function to handle user input and bot response
    // const handleChat = () => {
    //     const userMessage = chatInput.value.trim();
    //     if (!userMessage) return;

    //     appendMessage("You: " + userMessage, "user");
    //     chatInput.value = "";

    //     // Send user message to the server (Flask) to get bot response using GPT
    //     fetch("/gpt", {
    //         method: "POST",
    //         headers: {
    //             "Content-Type": "application/json",
    //         },
    //         body: JSON.stringify({ 'text': userMessage }),
    //     })
    //     .then(response => response.json())
    //     // .then(data => {
    //     //     const botResponse = data.model_response;
    //     //     appendMessage("Bot: " + botResponse, "bot");
    //     //     // Scroll to the bottom to show the latest messages
    //     //     chatMessages.scrollTop = chatMessages.scrollHeight;
    //     // })
    //     .then(data => {
    //             if ('model_response' in data) {
    //                 const modelResponse = `ChatBot: ${data.model_response}`;
    //                 outputElement.innerHTML += `<p>${modelResponse}</p>`;
    //             } else if ('error' in data) {
    //                 const errorResponse = `Error: ${data.error}`;
    //                 outputElement.innerHTML += `<p>${errorResponse}</p>`;
    //             }
    //         })
    //     .catch(error => {
    //         console.error("Error fetching bot response:", error);
    //         appendMessage("Bot: Something went wrong. Please try again.", "bot");
    //     });

    //     document.getElementById('prompt').value = ''; // Clear the input field after sending the prompt
    // };

    // Send user message when clicking the send button
    sendButton.addEventListener("click", handleChat);

    // Send user message when pressing Enter key
    chatInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            handleChat();
            event.preventDefault();
        }
    });
});
