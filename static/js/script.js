let shouldStopStream = false; // Add this flag to control the streaming
let currentSessionId = null;

window.onload = function () {
    // Clear chat container on page load
    // document.getElementById("chat-container").innerHTML = "";
};

document.querySelector(".new-session-button").addEventListener("click", function () {
    location.reload(); // Refresh the page
});

const toggleThemeButton = document.getElementById("theme-toggle");

// Load the preferred theme from localStorage
const currentTheme = "light-mode" || "light-mode";
document.documentElement.classList.add(currentTheme); // Apply theme to the html tag
toggleThemeButton.textContent = currentTheme === "dark-mode" ? "Switch to Light Mode" : "Switch to Dark Mode";

// Toggle theme on button click
toggleThemeButton.addEventListener("click", () => {
    const html = document.documentElement; // Target the html element
    if (html.classList.contains("dark-mode")) {
        html.classList.replace("dark-mode", "light-mode");
        toggleThemeButton.textContent = "Switch to Dark Mode";
        localStorage.setItem("theme", "light-mode");
        html.style.backgroundColor = "#ffffff"; // Apply background color to html
    } else {
        html.classList.replace("light-mode", "dark-mode");
        toggleThemeButton.textContent = "Switch to Light Mode";
        localStorage.setItem("theme", "dark-mode");
        html.style.backgroundColor = "#252525"; // Apply background color to html
    }
});

/////////////////////////////////////////////////////////
//                  Utility functions                  //
/////////////////////////////////////////////////////////

function generateSessionId() {
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
        const r = (Math.random() * 16) | 0;
        const v = c === "x" ? r : (r & 0x3) | 0x8;
        return v.toString(16);
    });
}

function scrollToBottom(){
    const chatContainer = document.getElementById("chat-container");
    chatContainer.scrollTop = chatContainer.scrollHeight;
}
function handlePaste(event) {
    event.preventDefault();
    const text = event.clipboardData.getData("text/plain");
    document.execCommand("insertText", false, text);
}

function loadingAnimation() {
    const chatContainer = document.getElementById("chat-container");
    const loadingMessageContainer = document.createElement("div");
    loadingMessageContainer.classList.add("bot-loading-message-container");
    loadingMessageContainer.id = "slide-loading-animation";
    chatContainer.appendChild(loadingMessageContainer);
}

function resetSendButton() {
    const userInput = document.getElementById("userInput");
    const sendButton = document.getElementById("sendButton");
    const sendIcon = document.getElementById("sendIcon");

    userInput.setAttribute("contenteditable", "true");
    sendButton.disabled = false;
    sendIcon.onclick = null; // Remove the stopStream function from the click event
}

function cleanInput() {
    const userInput = document.getElementById("userInput");
    userInput.innerHTML = userInput.innerHTML.replace(/<span[^>]*>(.*?)<\/span>/g, "$1");
}

function updateSidebarWithSession(sessionId, firstQuestion, session_icon) {
    const sessionList = document.getElementById("session-list");

    // Create the list item for the session
    const sessionItem = document.createElement("li");
    sessionItem.className = "chat-item"; // Set the class name
    sessionItem.setAttribute("session_id", sessionId); // Set the session_id attribute
    sessionItem.onclick = () => loadSessionData(sessionId); // Click handler for the session item

    // Create a div for the emoji container
    const emojiDiv = document.createElement("div");
    emojiDiv.className = "chat-item-emoji"; // Set a class for styling

    // Create the emoji image
    const emojiImage = document.createElement("img");
    emojiImage.className = "emoji-button"; // Add a class for styling
    emojiImage.src = `/static/images/session-icons/${session_icon}`; // Use backticks for template literals

    // Append the emoji image to the emoji container
    emojiDiv.appendChild(emojiImage);

    // Create a div for the session text
    const sessionTextDiv = document.createElement("div");
    sessionTextDiv.className = "chat-item-question"; // Set a class for styling
    sessionTextDiv.textContent = firstQuestion; // Display the first question or a default name

    // Create a div for the delete icon container
    const deleteIconDiv = document.createElement("div");
    deleteIconDiv.className = "chat-item-delete-container"; // Set a class for styling

    // Create the delete icon
    const deleteIcon = document.createElement("img");
    deleteIcon.className = "delete-button"; // Add a class for styling
    deleteIcon.src = "/static/images/delete.svg"; // Set the source of the delete icon
    deleteIcon.alt = "Delete"; // Set an alt text for accessibility
    deleteIcon.onclick = (e) => {
        e.stopPropagation(); // Prevent triggering the `onclick` for the session item
        deleteSession(sessionId); // Call the delete function
    };

    // Append the delete icon to the delete icon container
    deleteIconDiv.appendChild(deleteIcon);

    // Create a div for the session indicator
    const indicatorDiv = document.createElement("div");
    indicatorDiv.className = "chat-item-indicator"; // Set a class for styling

    // Append all child elements to the session item
    sessionItem.appendChild(emojiDiv); // Add the emoji container
    sessionItem.appendChild(sessionTextDiv); // Add the session text container
    sessionItem.appendChild(deleteIconDiv); // Add the delete icon container
    sessionItem.appendChild(indicatorDiv); // Add the session indicator

    // Insert the new session item at the top of the list
    sessionList.insertBefore(sessionItem, sessionList.firstChild);
}

/////////////////////////////////////////////////////////
//                  sidebar functions                  //
/////////////////////////////////////////////////////////

async function clearAllChats() {
    // Show confirmation dialog
    const confirmation = confirm("Are you sure you want to clear all chats?");
    if (!confirmation) {
        return; // Exit if the user cancels
    }

    try {
        // Send POST request to Flask backend to delete all sessions
        const response = await fetch("/delete_all_sessions", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
        });

        if (response.ok) {
            alert("All sessions have been cleared.");
            location.reload(); // Reload the page to reflect the changes
        } else {
            const errorMessage = await response.text();
            alert("Failed to clear sessions: " + errorMessage);
        }
    } catch (error) {
        console.error("Error clearing sessions:", error);
        alert("An error occurred while clearing sessions. Please try again.");
    }
}

async function deleteSession(sessionId) {
    // Show confirmation dialog
    const confirmation = confirm("Are you sure you want to delete this session?");
    if (!confirmation) {
        return; // Exit if the user cancels
    }

    try {
        // Send POST request to Flask backend to delete the specific session
        const response = await fetch("/delete_session", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ session_id: sessionId }),
        });

        if (response.ok) {
            alert("Session deleted successfully.");
            // Remove the session from the DOM
            const sessionElement = document.querySelector(`[session_id="${sessionId}"]`);
            if (sessionElement) {
                sessionElement.remove();
            }
        } else {
            const errorMessage = await response.text();
            alert("Failed to delete session: " + errorMessage);
        }
    } catch (error) {
        console.error("Error deleting session:", error);
        alert("An error occurred while deleting the session. Please try again.");
    }
}

async function loadSessionData(sessionId) {
    try {
        const response = await fetch("/get_session_data", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ sessionId }),
        });
        const responseData = await response.json(); // Ensure JSON response
        const sessionData = responseData.session_data; // Access 'session_data'

        if (sessionData) {
            renderSession(sessionData, sessionId);
        } else {
            console.log("No conversations found for this session.");
        }
    } catch (error) {
        console.error("Error loading previous conversations:", error);
    }
}

function renderSession(sessionData, sessionId) {
    currentSessionId = sessionId;
    const slidesContainer = document.getElementById("chat-container");
    slidesContainer.innerHTML = "";
    sessionData.forEach((item) => {
        try {
            const prompt = item.prompt;
            const sql_query = item.sql_query;
            const sql_data = item.sql_data;
            const chatbot_assistant = item.chatbot_assistant;
            appendUserMessage(prompt);
            appendSQLQuerry(sql_query);
            appendSQLDataMessage(sql_data);
            appendChatbotMessage(chatbot_assistant);
        } catch (error) {
            console.error("Error rendering session data:", error);
        }
    });
}

function appendUserMessage(content) {
    const chatContainer = document.getElementById("chat-container");
    const welcomeContainer = document.getElementById("welcome-container");
    if (welcomeContainer) {
        welcomeContainer.style.display = "none";
    }

    const messageContainer = document.createElement("div");
    messageContainer.classList.add("user-message-container");

    // Create the main content wrapper
    const messageContentWrapper = document.createElement("div");
    messageContentWrapper.classList.add("user-message");
    messageContentWrapper.classList.add("message");

    // Create the text content container
    const textContentContainer = document.createElement("div");
    textContentContainer.classList.add("text-content-container");

    textContentContainer.textContent = content;

    // Append the text content and action container to the main content wrapper
    messageContentWrapper.appendChild(textContentContainer);

    // Append the message content wrapper and edit icon container to the message container
    messageContainer.appendChild(messageContentWrapper);

    const allUserMessages = document.createElement("div");
    allUserMessages.classList.add("all-user-messages");
    
    // Create the profile picture container
    const profilePicContainer = document.createElement("div");
    profilePicContainer.classList.add("profile-pic-container");

    // Create the profile picture element
    const profilePic = document.createElement("img");
    profilePic.classList.add("profile-pic");
    profilePic.src = "/static/images/user.svg"; // Path to the profile picture

    // Append the profile picture to the profile picture container
    profilePicContainer.appendChild(profilePic);

    // Append the profile picture container to the all user messages container
    allUserMessages.appendChild(profilePicContainer);
    allUserMessages.appendChild(messageContainer);

    // Append the message container to the chat container
    chatContainer.appendChild(allUserMessages);

    // Scroll to the bottom of the chat container
    scrollToBottom();
}

function appendChatbotMessage(content) {
  const chatContainer = document.getElementById("chat-container");

  const messageContainer = document.createElement("div");
  messageContainer.classList.add("chatbot-message-container");

  // Create the main content wrapper
  const messageContentWrapper = document.createElement("div");
  messageContentWrapper.classList.add("chatbot-message");
  messageContentWrapper.classList.add("message");

  // Create the text content container
  const textContentContainer = document.createElement("div");
  textContentContainer.classList.add("text-content-container");

  if (content) {
      textContentContainer.innerHTML = marked.parse(content);
  }

  // Append the text content container to the main content wrapper
  messageContentWrapper.appendChild(textContentContainer);

  // Append the message content wrapper to the message container
  messageContainer.appendChild(messageContentWrapper);

  // Append the message container to the chat container
  chatContainer.appendChild(messageContainer);

  // Scroll to the bottom of the chat container
  scrollToBottom()

}
function appendSQLDataMessage(content) {
    const chatContainer = document.getElementById("chat-container");

    // Create the show/hide button
    const showHideButton = document.createElement("div");
    showHideButton.classList.add("show-hide-data");
    showHideButton.style.cursor = "pointer";

    // Create the button text
    const buttonText = document.createElement("span");
    buttonText.textContent = "View Query Results";

    // Create the down arrow image
    const arrowImage = document.createElement("img");
    arrowImage.classList.add("down-arrow");
    arrowImage.src = "/static/images/down-arrow.svg"; // Path to the down arrow image
    arrowImage.style.transition = "transform 0.3s"; // Smooth transition for rotation

    // Append text and image to the button
    showHideButton.appendChild(buttonText);
    showHideButton.appendChild(arrowImage);

    // Create the message container
    const messageContainer = document.createElement("div");
    messageContainer.classList.add("chatbot-data-message-container");
    messageContainer.style.display = "none"; // Initially hidden

    // Create the main content wrapper
    const messageContentWrapper = document.createElement("div");
    messageContentWrapper.classList.add("chatbot-data-message");
    messageContentWrapper.classList.add("message");

    // Create the text content container
    const textContentContainer = document.createElement("div");
    textContentContainer.classList.add("data-text-content-container");

    if (content) {
        textContentContainer.innerHTML = marked.parse(content);
    }

    // Append the text content container to the main content wrapper
    messageContentWrapper.appendChild(textContentContainer);

    // Append the message content wrapper to the message container
    messageContainer.appendChild(messageContentWrapper);

    // Append the show/hide button and message container to the chat container
    chatContainer.appendChild(showHideButton);
    chatContainer.appendChild(messageContainer);

    // Add event listener to toggle the visibility of the message container and rotate the arrow
    showHideButton.addEventListener("click", () => {
        const isHidden = messageContainer.style.display === "none";
        messageContainer.style.display = isHidden ? "block" : "none";
        arrowImage.style.transform = isHidden ? "rotate(180deg)" : "rotate(0deg)";
    });

    // Scroll to the bottom of the chat container
    scrollToBottom();
}
function appendSQLQuerry(content) {
    const chatContainer = document.getElementById("chat-container");
    const welcomeContainer = document.getElementById("welcome-container");
    if (welcomeContainer) {
        welcomeContainer.style.display = "none";
    }

    const messageContainer = document.createElement("div");
    messageContainer.classList.add("chatbot-sql-container");

    // Create the main content wrapper
    const messageContentWrapper = document.createElement("div");
    messageContentWrapper.classList.add("chatbot-sql-message");
    messageContentWrapper.classList.add("message");

    // Create the text content container
    const textContentContainer = document.createElement("div");
    textContentContainer.classList.add("sql-text-content-container");

    textContentContainer.textContent = content;

    // Append the text content and action container to the main content wrapper
    messageContentWrapper.appendChild(textContentContainer);

    // Append the message content wrapper and edit icon container to the message container
    messageContainer.appendChild(messageContentWrapper);

    const allUserMessages = document.createElement("div");
    allUserMessages.classList.add("all-sql-messages");

    const botPicContainer = document.createElement("div");
    botPicContainer.classList.add("bot-pic-container");

    // Create the bot picture element
    const botPic = document.createElement("img");
    botPic.classList.add("bot-pic");
    botPic.src = "/static/images/sparkles.svg"; // Path to the bot picture

    // Append the bot picture to the bot picture container
    botPicContainer.appendChild(botPic);
    allUserMessages.appendChild(botPicContainer);
    allUserMessages.appendChild(messageContainer);

    // Append the message container to the chat container
    chatContainer.appendChild(allUserMessages);

    // Scroll to the bottom of the chat container
    scrollToBottom()

}

async function generateChatbotAnswer() {
    const userInput = document.getElementById("userInput");
    const sendButton = document.getElementById("sendButton");
    const sendIcon = document.getElementById("sendIcon");
    const message = userInput.innerText.trim();

    if (message === "") return;

    userInput.setAttribute("contenteditable", "false");
    sendButton.disabled = true;

    // Append the user message block
    appendUserMessage(message);
    userInput.innerText = "";

    loadingAnimation()

    let sessionIcon; // Define sessionIcon outside the block

    try {
        if (!currentSessionId) {
            currentSessionId = generateSessionId(); // Generate a new session ID

            // Fetch the session icon using the /get_random_session_icon route
            const iconResponse = await fetch("/get_random_session_icon", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ session_id: currentSessionId }),
            });

            if (!iconResponse.ok) {
                console.error("Error fetching session icon:", iconResponse.statusText);
                throw new Error("Failed to fetch session icon");
            }

            const iconData = await iconResponse.json();
            sessionIcon = iconData.relavant_schema; // Assuming the icon is returned as 'relavant_schema'

            // Update the sidebar with the new session and icon
            updateSidebarWithSession(currentSessionId, message, sessionIcon);
        }

        // If the session already exists, assign a default or placeholder icon
        if (!sessionIcon) {
            sessionIcon = "default_icon"; // Replace with an actual default icon if necessary
        }

        // Step 1: Extract relevant schema
        const schemaResponse = await fetch("/extract_relavant_schema", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                user_input: message,
                session_id: currentSessionId,
            }),
        });

        if (!schemaResponse.ok) {
            console.error("Error extracting relevant schema:", schemaResponse.statusText);
            appendChatbotMessage("Error: Could not extract relevant schema.");
            return;
        }

        const schemaData = await schemaResponse.json();
        const relavantSchema = schemaData.relavant_schema;
        if (!relavantSchema) {
            console.error("Relevant schema is missing in the response.");
            appendChatbotMessage("Error: Relevant schema is missing.");
            return;
        }

        // Step 2: Generate the SQL query using the relevant schema
        const sqlQueryResponse = await fetch("/generate_sql_query", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                user_input: message,
                relavant_schema: relavantSchema,
                session_id: currentSessionId,
            }),
        });

        if (!sqlQueryResponse.ok) {
            console.error("Error generating SQL query:", sqlQueryResponse.statusText);
            appendChatbotMessage("Error: Could not generate SQL query.");
            return;
        }
        
        // Stream the response
        appendSQLQuerry(""); // Add an empty chatbot message container for streaming
        const sqlReader = sqlQueryResponse.body.getReader();
        const SQLDecoder = new TextDecoder("utf-8");
        const sqlContainers = document.querySelectorAll(".chatbot-sql-container");
        const sqlContainer = sqlContainers[sqlContainers.length - 1];
        let resultSQLText = sqlContainer.querySelector(".sql-text-content-container");

        let SQLdone = false;
        let sqlQuery = "";

        while (!SQLdone) {
            const { value, done: readerDone } = await sqlReader.read();
            SQLdone = readerDone;

            if (value) {
                sqlQuery += SQLDecoder.decode(value);
                resultSQLText.innerHTML = marked.parse(sqlQuery);
            }
            // Scroll to the bottom
            scrollToBottom()

        }

        if (!sqlQuery) {
            console.log("SQL query is not returned, using default message.");
            sqlData = "Answer this question in general without SQL data."; // Default message if no SQL query is generated
        } else {
            // Step 3: Execute the SQL query using the generated SQL query
            const executeQueryResponse = await fetch("/execute_sql_query", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    sql_query: sqlQuery, // Pass the generated SQL query to execute
                }),
            });

            if (!executeQueryResponse.ok) {
                console.error("Error executing SQL query:", executeQueryResponse.statusText);
                appendChatbotMessage("Error: Could not execute SQL query.");
                return;
            }

            const executeQueryData = await executeQueryResponse.json();
            sqlData = executeQueryData.sql_data;
        }

        if (!sqlData) {
            console.error("SQL data is missing in the response.");
            appendChatbotMessage("Error: No data returned from SQL query.");
            return;
        }

        appendSQLDataMessage(sqlData)
        
        const loadingAnimationConst = document.getElementById("slide-loading-animation");
        if (loadingAnimationConst) {
            loadingAnimationConst.remove();
        }
        
        // Step 3: Invoke the agent for response
        const responseAgent = await fetch("/invoke_agent", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                session_id: currentSessionId,
                user_input: message,
                relavant_schema: relavantSchema,
                sql_data: sqlData,
            }),
        });

        if (!responseAgent.ok) {
            console.error("Error invoking agent:", responseAgent.statusText);
            appendChatbotMessage("Error: " + responseAgent.statusText);
            return;
        }

        // Stream the response
        appendChatbotMessage(""); // Add an empty chatbot message container for streaming
        const reader = responseAgent.body.getReader();
        const decoder = new TextDecoder("utf-8");
        const messageContainers = document.querySelectorAll(".chatbot-message-container");
        const messageContainer = messageContainers[messageContainers.length - 1];
        let resultText = messageContainer.querySelector(".text-content-container");

        let done = false;
        let llmOutput = "";
        const userInput = document.getElementById("userInput");
        userInput.setAttribute("contenteditable", "true");
        userInput.focus();

        while (!done) {
            const { value, done: readerDone } = await reader.read();
            done = readerDone;

            if (value) {
                llmOutput += decoder.decode(value);
                resultText.innerHTML = marked.parse(llmOutput);
            }
            // Scroll to the bottom
            scrollToBottom()

        }

        // Step 4: Update conversation in the session
        const responseUpdateSession = await fetch("/update_session", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                session_id: currentSessionId,
                prompt: message,
                chatbot_assistant: llmOutput,
                sql_query: sqlQuery,
                sql_data: sqlData,
                session_icon: sessionIcon,
            }),
        });

        if (!responseUpdateSession.ok) {
            console.error("Error updating session:", responseUpdateSession.statusText);
            appendChatbotMessage("Error: " + responseUpdateSession.statusText);
        }
    } catch (error) {
        console.error("Error during fetch or streaming:", error.message);
        appendChatbotMessage("Error: " + error.message);
    } finally {
        // Reset the input, Loading animation and send button
        resetSendButton()
    }
}

  



// Attach event listener for Enter key
function handleKeyPress(event) {
    const sendButton = document.getElementById("sendButton");
    if (event.key === "Enter" && !sendButton.disabled) {
        event.preventDefault();
        generateChatbotAnswer();
    }
}
