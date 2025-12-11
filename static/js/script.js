document.getElementById("chatForm").addEventListener("submit", async function(e) {
    e.preventDefault();
    
    // 1. Get DOM Elements
    const inputField = document.getElementById("userInput");
    const chatbox = document.getElementById("chatbox");
    const query = inputField.value;
    
    // 2. Add User Message to UI
    chatbox.innerHTML += `
        <div class="msg msg-user">
            <div class="bubble bubble-user">${query}</div>
        </div>`;
    inputField.value = "";
    chatbox.scrollTop = chatbox.scrollHeight; // Auto-scroll to bottom

    // 3. Prepare Data for Backend
    const formData = new FormData();
    formData.append("msg", query);

    try {
        // 4. Send Request to Flask App
        const response = await fetch("/get_response", { method: "POST", body: formData });
        const data = await response.json();

        // 5. Add Bot Response to UI
        // Replace newlines with <br> for HTML rendering
        const formattedReply = data.response.replace(/\n/g, "<br>");
        chatbox.innerHTML += `
            <div class="msg msg-bot">
                <div class="bubble bubble-bot">${formattedReply}</div>
            </div>`;
        chatbox.scrollTop = chatbox.scrollHeight;

        // 6. UPDATE METRICS DASHBOARD
        const modeBadge = document.getElementById("mode-indicator");
        
        // Logic: Check if 'cyborg' metric exists and is non-zero (Meaning a Search happened)
        if (data.metrics && data.metrics.cyborg > 0) {
            // --- SEARCH MODE ACTIVE ---
            modeBadge.innerText = "Mode: SEARCH 🔍";
            modeBadge.className = "status-badge status-active"; // Turn Green

            // Extract Values (Default to 0 if missing)
            const cyborgTime = data.metrics.cyborg;
            const faissTime = data.metrics.faiss || 0; 
            const chromaTime = data.metrics.chroma || 0;

            // Update Latency Text
            document.getElementById("cyborg-val").innerText = cyborgTime.toFixed(4) + "s";
            document.getElementById("faiss-val").innerText = faissTime.toFixed(4) + "s";
            document.getElementById("chroma-val").innerText = chromaTime.toFixed(4) + "s";

            // --- CALCULATE COMPARISONS (Faster/Slower) ---

            // A. vs FAISS
            if (faissTime > 0) {
                const diff = ((cyborgTime - faissTime) / faissTime) * 100;
                const el = document.getElementById("overhead-faiss");

                if (diff > 0) {
                    // Positive Diff = Cyborg took MORE time = Slower
                    el.innerText = diff.toFixed(0) + "% Slower";
                    el.className = "metric-value text-warning"; 
                } else {
                    // Negative Diff = Cyborg took LESS time = Faster
                    el.innerText = Math.abs(diff).toFixed(0) + "% Faster";
                    el.className = "metric-value text-success"; 
                }
            } else {
                document.getElementById("overhead-faiss").innerText = "N/A";
            }

            // B. vs CHROMA
            if (chromaTime > 0) {
                const diff = ((cyborgTime - chromaTime) / chromaTime) * 100;
                const el = document.getElementById("overhead-chroma");

                if (diff > 0) {
                    el.innerText = diff.toFixed(0) + "% Slower";
                    el.className = "metric-value text-warning";
                } else {
                    el.innerText = Math.abs(diff).toFixed(0) + "% Faster";
                    el.className = "metric-value text-success";
                }
            } else {
                document.getElementById("overhead-chroma").innerText = "N/A";
            }

        } else {
            // --- CHAT MODE (IDLE) ---
            modeBadge.innerText = "Mode: CHAT 💬";
            modeBadge.className = "status-badge status-idle"; // Turn Gray
            
            // Note: We don't reset the numbers to 0 here so the previous search result stays visible.
        }

    } catch (error) {
        console.error("Error:", error);
        chatbox.innerHTML += `
            <div class="msg msg-bot">
                <div class="bubble bubble-bot text-danger">Error connecting to server. Check console.</div>
            </div>`;
    }
});