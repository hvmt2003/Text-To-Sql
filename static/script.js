function askQuestion() {
    const questionInput = document.getElementById("question");
    const askBtn = document.getElementById("askBtn");
    const loading = document.getElementById("loading");
    const errorBox = document.getElementById("errorBox");
    const sqlBox = document.getElementById("sqlBox");
    const sqlContent = document.getElementById("sqlContent");
    const resultTable = document.getElementById("resultTable");
    const tableHeader = document.getElementById("tableHeader");
    const tableBody = document.getElementById("tableBody");

    const question = questionInput.value.trim();
    if (!question) return;

    // Reset UI
    errorBox.style.display = "none";
    sqlBox.style.display = "none";
    resultTable.style.display = "none";
    tableHeader.innerHTML = "";
    tableBody.innerHTML = "";

    // Set Loading State
    askBtn.disabled = true;
    loading.style.display = "block";

    fetch("/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show SQL
                sqlContent.textContent = data.sql;
                sqlBox.style.display = "block";

                // Render Table
                if (data.result && data.result.length > 0) {
                    const keys = Object.keys(data.result[0]);

                    // Headers
                    keys.forEach(key => {
                        const th = document.createElement("th");
                        th.textContent = key;
                        tableHeader.appendChild(th);
                    });

                    // Rows
                    data.result.forEach(row => {
                        const tr = document.createElement("tr");
                        keys.forEach(key => {
                            const td = document.createElement("td");
                            td.textContent = row[key];
                            tr.appendChild(td);
                        });
                        tableBody.appendChild(tr);
                    });

                    resultTable.style.display = "table";
                } else {
                    errorBox.textContent = "No results found for your query.";
                    errorBox.style.display = "block";
                }
            } else {
                errorBox.textContent = data.error || "An error occurred.";
                errorBox.style.display = "block";
            }
        })
        .catch(err => {
            errorBox.textContent = "Failed to connect to server.";
            errorBox.style.display = "block";
        })
        .finally(() => {
            askBtn.disabled = false;
            loading.style.display = "none";
        });
}

// Allow Enter key to submit
document.getElementById("question").addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
        askQuestion();
    }
});
