const API_BASE_URL = "http://127.0.0.1:8000";


console.log(
    "Knowledge AI frontend loaded."
);

console.log(
    "Backend API:",
    API_BASE_URL
);


// --------------------------------------------------
// ELEMENTS
// --------------------------------------------------

const chatContainer =
    document.getElementById("chatContainer");

const messageInput =
    document.getElementById("messageInput");

const sendButton =
    document.getElementById("sendButton");

const clearButton =
    document.getElementById("clearButton");

const clearHistoryButton =
    document.getElementById("clearHistoryButton");

const newChatButton =
    document.getElementById("newChatButton");

const pdfInput =
    document.getElementById("pdfInput");

const uploadStatus =
    document.getElementById("uploadStatus");

const documentsList =
    document.getElementById("documentsList");

const refreshDocuments =
    document.getElementById("refreshDocuments");

const chatHistoryList =
    document.getElementById("chatHistoryList");

const suggestions =
    document.getElementById("suggestions");

// Simplified: no language/model/voice selectors in UI

let currentConversationId =
    `chat-${Date.now()}`;

const suggestionQuestions = [
    "What is the company about?",
    "How long is the internship?",
    "What are the leave policies?",
    "What services does the company offer?",
];

function getCurrentLanguage() {
    return "en";
}

function getCurrentModel() {
    return "gemma";
}

function renderSuggestions() {
    if (!suggestions) return;

    suggestions.innerHTML = "";

    suggestionQuestions.forEach((question) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "suggestion";
        button.textContent = question;

        button.addEventListener("click", () => {
            messageInput.value = question;
            sendMessage();
        });

        suggestions.appendChild(button);
    });
}

function generateConversationId() {
    return `chat-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

async function loadChatHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/chat/history`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Could not load chat history.");
        }

        const conversations = data.conversations || [];

        if (conversations.length === 0) {
            chatHistoryList.innerHTML = `
                <div class="history-empty">No chat history yet.</div>
            `;
            return;
        }

        chatHistoryList.innerHTML = "";

        conversations.forEach((conversation) => {
            const item = document.createElement("div");
            item.className = "history-item";

            const selectButton = document.createElement("button");
            selectButton.className = "history-select";
            selectButton.textContent = conversation.title || "Chat";
            selectButton.addEventListener("click", () => {
                currentConversationId = conversation.conversation_id;
                loadChatHistory();
            });

            const deleteButton = document.createElement("button");
            deleteButton.className = "history-delete";
            deleteButton.textContent = "✕";
            deleteButton.title = "Delete chat";
            deleteButton.addEventListener("click", async (event) => {
                event.stopPropagation();
                const confirmed = confirm(`Delete this chat history?`);
                if (!confirmed) return;

                try {
                    const deleteResponse = await fetch(
                        `${API_BASE_URL}/api/chat/${encodeURIComponent(conversation.conversation_id)}`,
                        { method: "DELETE" }
                    );

                    const deleteData = await deleteResponse.json();
                    if (!deleteResponse.ok) {
                        throw new Error(deleteData.detail || "Delete failed.");
                    }

                    if (currentConversationId === conversation.conversation_id) {
                        currentConversationId = generateConversationId();
                        clearChat();
                    }

                    await loadChatHistory();
                } catch (error) {
                    alert(`Delete failed: ${error.message}`);
                }
            });

            item.appendChild(selectButton);
            item.appendChild(deleteButton);
            chatHistoryList.appendChild(item);
        });
    } catch (error) {
        chatHistoryList.innerHTML = `
            <div class="history-empty">Unable to load history.</div>
        `;
    }
}

// --------------------------------------------------
// CHAT
// --------------------------------------------------

function addMessage(
    message,
    sender,
    sources = []
) {
    // Avoid appending duplicate consecutive AI messages
    if (sender === "ai") {
        const last = Array.from(chatContainer.querySelectorAll('.message.ai')).pop();
        if (last) {
            const lastText = last.querySelector('.message-text');
            if (lastText && lastText.textContent === message) {
                console.warn('Duplicate AI message suppressed');
                return;
            }
        }
    }

    const messageElement = document.createElement("div");
    messageElement.className = `message ${sender}`;

    const contentElement = document.createElement("div");
    contentElement.className = "message-content";

    // Add a small source badge so users know where the answer came from
    const badge = document.createElement("div");
    badge.className = "source-badge";
    badge.textContent = sources && sources.length > 0
        ? "Source: uploaded document"
        : "Source: AI provider";

    const textNode = document.createElement("div");
    textNode.className = "message-text";
    textNode.textContent = message;

    contentElement.appendChild(badge);
    contentElement.appendChild(textNode);


    if (
        sender === "ai"
    ) {
        if (sources.length > 0) {
            const sourcesElement =
                document.createElement("div");

            sourcesElement.className =
                "sources";

            const title =
                document.createElement("strong");

            title.textContent =
                "Sources";

            sourcesElement.appendChild(title);

            sources.forEach((source) => {
                const sourceElement =
                    document.createElement("div");

                sourceElement.className = "source";
                sourceElement.textContent =
                    `📄 ${source.source} — Page ${source.page}`;

                sourcesElement.appendChild(sourceElement);
            });

            contentElement.appendChild(sourcesElement);
        }

        const feedbackRow = document.createElement("div");
        feedbackRow.className = "feedback-row";

        const helpfulButton = document.createElement("button");
        helpfulButton.type = "button";
        helpfulButton.className = "feedback-button";
        helpfulButton.textContent = "Helpful";
        helpfulButton.addEventListener("click", () => {
            helpfulButton.textContent = "✓ Helpful";
            helpfulButton.disabled = true;
            notHelpfulButton.disabled = true;
        });

        const notHelpfulButton = document.createElement("button");
        notHelpfulButton.type = "button";
        notHelpfulButton.className = "feedback-button";
        notHelpfulButton.textContent = "Not Helpful";
        notHelpfulButton.addEventListener("click", () => {
            notHelpfulButton.textContent = "✓ Not Helpful";
            notHelpfulButton.disabled = true;
            helpfulButton.disabled = true;
        });

        feedbackRow.appendChild(helpfulButton);
        feedbackRow.appendChild(notHelpfulButton);
        contentElement.appendChild(feedbackRow);
    }


    messageElement.appendChild(
        contentElement
    );


    chatContainer.appendChild(
        messageElement
    );


    chatContainer.scrollTop =
        chatContainer.scrollHeight;
}


// --------------------------------------------------
// LOADING
// --------------------------------------------------

function addLoadingMessage() {

    const element =
        document.createElement("div");

    element.className =
        "message ai";

    element.id =
        "loadingMessage";


    const content =
        document.createElement("div");

    content.className =
        "message-content";

    content.textContent =
        "Thinking...";


    element.appendChild(
        content
    );

    chatContainer.appendChild(
        element
    );


    chatContainer.scrollTop =
        chatContainer.scrollHeight;
}


function removeLoadingMessage() {

    const element =
        document.getElementById(
            "loadingMessage"
        );

    if (element) {

        element.remove();

    }
}


// --------------------------------------------------
// SEND MESSAGE
// --------------------------------------------------

async function sendMessage() {

    const message =
        messageInput.value.trim();


    if (!message) {

        return;

    }

    if (!currentConversationId || currentConversationId.trim() === "") {
        currentConversationId = generateConversationId();
    }


    addMessage(
        message,
        "user"
    );


    messageInput.value = "";

    sendButton.disabled = true;

    addLoadingMessage();


    try {

        console.log(
            "Sending request to:",
            `${API_BASE_URL}/api/chat`
        );


        const response =
            await fetch(
                `${API_BASE_URL}/api/chat`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        message: message,
                        conversation_id: currentConversationId,
                        language: getCurrentLanguage(),
                        model: getCurrentModel()
                    })
                }
            );


        const data =
            await response.json();


        console.log(
            "Chat API response:",
            data
        );


        removeLoadingMessage();


        if (!response.ok) {
            const detail =
                (data && data.detail) ||
                "Chat request failed.";

            if (
                response.status === 402 ||
                /credit|budget|in-flight|retry-after/i.test(detail)
            ) {
                throw new Error(
                    "OpenRouter credits are exhausted or the request limit is reached. Please wait a couple of minutes or add credits."
                );
            }

            throw new Error(detail);

        }


        addMessage(
            data.answer ||
            "No answer was returned.",
            "ai",
            data.sources || []
        );

        await loadChatHistory();


    } catch (error) {

        console.error(
            "Chat request failed:",
            error
        );


        removeLoadingMessage();


        const message =
            error && error.message
                ? error.message
                : "Chat request failed.";

        const isProviderLimitError =
            /credit|budget|in-flight|retry-after|402/i.test(message);

        addMessage(
            isProviderLimitError
                ? "The AI provider is currently out of budget or request capacity. Please wait a minute and try again, or add credits in OpenRouter."
                : `Error: ${message}`,
            "ai"
        );

    } finally {

        sendButton.disabled = false;

        messageInput.focus();

    }
}


// --------------------------------------------------
// CLEAR CHAT
// --------------------------------------------------

async function clearChat() {

    try {
        const response = await fetch(
            `${API_BASE_URL}/api/chat/${encodeURIComponent(currentConversationId)}`,
            { method: "DELETE" }
        );

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "Clear chat failed.");
        }
    } catch (error) {
        console.error("Clear chat failed:", error);
    }

    currentConversationId = generateConversationId();

    chatContainer.innerHTML = `
        <div class="welcome">

            <div class="welcome-icon">
                ✦
            </div>

            <h2>
                How can I help you?
            </h2>

            <p>
                Ask a question or upload a document to ground the answer.
            </p>

            <div id="suggestions" class="suggestions"></div>

        </div>
    `;

    renderSuggestions();
    loadChatHistory();
}


// --------------------------------------------------
// NAVIGATION
// --------------------------------------------------

function switchPage(pageName) {

    document
        .querySelectorAll(".page")
        .forEach(page => {

            page.classList.remove(
                "active"
            );

        });


    document
        .querySelectorAll(".nav-item")
        .forEach(button => {

            button.classList.remove(
                "active"
            );

        });


    const page =
        document.getElementById(
            `${pageName}Page`
        );


    const button =
        document.querySelector(
            `[data-page="${pageName}"]`
        );


    if (page) {

        page.classList.add(
            "active"
        );

    }


    if (button) {

        button.classList.add(
            "active"
        );

    }


    if (
        pageName === "knowledge"
    ) {

        loadDocuments();

    }
}


// --------------------------------------------------
// DOCUMENT LIST
// --------------------------------------------------

async function loadDocuments() {

    if (!documentsList) {
        console.warn("documentsList element not found; skipping loadDocuments().");
        return;
    }

    documentsList.innerHTML =
        `<div class="loading-documents">
            Loading documents...
        </div>`;


    try {

        const response =
            await fetch(
                `${API_BASE_URL}/api/documents/`
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Could not load documents."
            );

        }


        renderDocuments(
            data.documents || []
        );


    } catch (error) {

        console.error(
            "Document loading failed:",
            error
        );


        documentsList.innerHTML =
            `<div class="empty-documents">
                Unable to load documents.
            </div>`;
    }
}


function renderDocuments(
    documents
) {

    if (!documentsList) {
        console.warn("documentsList element not found; skipping renderDocuments().");
        return;
    }

    if (documents.length === 0) {

        documentsList.innerHTML =
            `<div class="empty-documents">
                No documents in the knowledge base yet.
            </div>`;

        return;

    }


    documentsList.innerHTML = "";


    documents.forEach(
        (doc) => {

            const element =
                document.createElement(
                    "div"
                );

            element.className =
                "document";


            const icon =
                doc.type === "pdf"
                    ? "📕"
                    : doc.type === "docx"
                        ? "📘"
                        : "📄";


            element.innerHTML = `

                <div class="document-icon">
                    ${icon}
                </div>

                <div class="document-info">

                    <div class="document-name">
                        ${escapeHtml(
                            doc.filename
                        )}
                    </div>

                    <div class="document-meta">
                        ${doc.type.toUpperCase()}
                        ·
                        ${formatBytes(
                            doc.size
                        )}
                    </div>

                </div>

                <button
                    class="delete-document"
                    title="Delete document"
                >
                    🗑
                </button>
            `;


            const deleteButton =
                element.querySelector(
                    ".delete-document"
                );


            deleteButton.addEventListener(
                "click",
                () => deleteDocument(
                    doc.filename
                )
            );


            documentsList.appendChild(
                element
            );

        }
    );
}


// --------------------------------------------------
// UPLOAD
// --------------------------------------------------

pdfInput.addEventListener(
    "change",
    async () => {

        const file =
            pdfInput.files[0];


        if (!file) {

            return;

        }


        uploadStatus.textContent =
            `Uploading ${file.name}...`;


        try {

            const formData =
                new FormData();


            formData.append(
                "file",
                file
            );


            const response =
                await fetch(
                    `${API_BASE_URL}/api/documents/upload`,
                    {
                        method: "POST",
                        body: formData
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Upload failed."
                );

            }


            uploadStatus.textContent =
                `✓ ${data.filename} indexed successfully (${data.chunks} chunks)`;

            // Keep the user on the active chat page while the document list refreshes.
            await loadDocuments();


        } catch (error) {

            console.error(
                "Upload failed:",
                error
            );


            uploadStatus.textContent =
                `Error: ${error.message}`;

        } finally {

            pdfInput.value = "";

        }
    }
);


// --------------------------------------------------
// DELETE
// --------------------------------------------------

async function deleteDocument(
    filename
) {

    const confirmed =
        confirm(
            `Delete "${filename}"?`
        );


    if (!confirmed) {

        return;

    }


    try {

        const response =
            await fetch(
                `${API_BASE_URL}/api/documents/${encodeURIComponent(filename)}`,
                {
                    method: "DELETE"
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Delete failed."
            );

        }


        await loadDocuments();

    } catch (error) {

        alert(
            `Delete failed: ${error.message}`
        );

    }
}


// --------------------------------------------------
// HELPERS
// --------------------------------------------------

function formatBytes(
    bytes
) {

    if (
        bytes === 0
    ) {

        return "0 Bytes";

    }


    const units = [
        "Bytes",
        "KB",
        "MB",
        "GB"
    ];


    const index =
        Math.floor(
            Math.log(bytes) /
            Math.log(1024)
        );


    return (
        parseFloat(
            (
                bytes /
                Math.pow(
                    1024,
                    index
                )
            ).toFixed(1)
        )
        +
        " " +
        units[index]
    );
}


function escapeHtml(
    value
) {

    const div =
        document.createElement(
            "div"
        );

    div.textContent =
        value;

    return div.innerHTML;
}


// Voice input removed to keep UI simple and safe


// --------------------------------------------------
// EVENT LISTENERS
// --------------------------------------------------


if (sendButton) {
    sendButton.addEventListener("click", sendMessage);
}

if (clearButton) {
    clearButton.addEventListener("click", clearChat);
}

if (newChatButton) {
    newChatButton.addEventListener("click", clearChat);
}

if (refreshDocuments) {
    refreshDocuments.addEventListener("click", loadDocuments);
}

if (clearHistoryButton) {
    clearHistoryButton.addEventListener("click", async () => {
        const ok = confirm("Clear all chat history? This will delete all saved conversations.");
        if (!ok) return;

        try {
            const resp = await fetch(`${API_BASE_URL}/api/chat/history`);
            const data = await resp.json();
            if (!resp.ok) throw new Error(data.detail || "Could not fetch history.");

            const convos = data.conversations || [];
            for (const c of convos) {
                try {
                    await fetch(`${API_BASE_URL}/api/chat/${encodeURIComponent(c.conversation_id)}`, { method: "DELETE" });
                } catch (e) {
                    console.warn("Failed to delete conversation", c.conversation_id, e);
                }
            }

            // refresh UI
            chatHistoryList.innerHTML = "";
            await loadChatHistory();
            clearChat();

        } catch (err) {
            alert(`Failed to clear history: ${err.message}`);
        }
    });
}


messageInput.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();

        }

    }
);


document
    .querySelectorAll(
        ".nav-item"
    )
    .forEach(
        button => {

            button.addEventListener(
                "click",
                () => {

                    switchPage(
                        button.dataset.page
                    );

                }
            );

        }
);

// No UI selectors to wire up; defaults applied in `getCurrentModel`/`getCurrentLanguage`.

// Initial setup

renderSuggestions();
// Load documents list on startup
loadDocuments();

// Hero search wiring (if present)
const heroSearchInput = document.getElementById("heroSearchInput");
const heroSearchButton = document.getElementById("heroSearchButton");

if (heroSearchButton && heroSearchInput) {
    heroSearchButton.addEventListener("click", () => {
        const q = heroSearchInput.value && heroSearchInput.value.trim();
        if (!q) return;
        messageInput.value = q;
        sendMessage();
    });

    heroSearchInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            heroSearchButton.click();
        }
    });
}
