// app.js
// Simple client that talks to the FastAPI backend at /api/chat

document.addEventListener('DOMContentLoaded', () => {
  const sendBtn = document.getElementById('send-btn');
  const input = document.getElementById('user-input');
  const responseBox = document.getElementById('response');

  const showMessage = (msg, error = false) => {
    responseBox.textContent = msg;
    responseBox.style.color = error ? 'hsl(0, 80%, 70%)' : 'var(--text-secondary)';
    responseBox.classList.remove('fade-in');
    void responseBox.offsetWidth; // reflow for animation reset
    responseBox.classList.add('fade-in');
  };

  sendBtn.addEventListener('click', async () => {
    const question = input.value.trim();
    if (!question) return;
    showMessage('⏳ thinking...');
    try {
      const BACKEND_URL = "https://rag-chatbot-669n.onrender.com";
      const resp = await fetch(`${BACKEND_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: question,
          conversation_id: null,
          language: 'en',
          model: null,
        }),
      });
      const data = await resp.json();
      if (resp.ok) {
        showMessage(data.answer);
      } else {
        showMessage(`❗ ${data.detail || 'Error'}`, true);
      }
    } catch (e) {
      showMessage(`❗ network error: ${e.message}`, true);
    }
    input.value = '';
  });
});
