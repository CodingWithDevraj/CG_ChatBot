document.addEventListener("DOMContentLoaded", function () {
    const userInput = document.getElementById("userInput");
    const messagesContainer = document.getElementById("messages");
    const sendButton = document.querySelector("sendBtn");

    async function sendMessage(event) {
        event.preventDefault(); // Prevent multiple submissions
        
        let userMessage = userInput.value.trim(); // Trim spaces
        if (!userMessage) return; // Prevent empty messages

        messagesContainer.innerHTML += `<p><b>You:</b> ${userMessage}</p>`;

        
        try {
            let response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: userMessage })
            });

            let data = await response.json();
            messagesContainer.innerHTML += `<p><b>Bot:</b> ${data.reply}</p>`;
        } catch (error) {
            messagesContainer.innerHTML += `<p style="color: red;"><b>Error:</b> Unable to fetch response.</p>`;
        }

        userInput.value = "";
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    
        
        sendButton.removeEventListener("click", sendMessage); // Prevent duplicate event bindings
        sendButton.addEventListener("click", sendMessage); // Attach only once

    }
);
