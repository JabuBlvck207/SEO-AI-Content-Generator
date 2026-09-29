const API_URL = window.location.protocol === "file:"
    ? "http://127.0.0.1:5000/api/generate"
    : "/api/generate";

const form = document.getElementById("generatorForm");
const generateBtn = document.getElementById("generateBtn");
const buttonText = document.getElementById("buttonText");
const spinner = document.getElementById("spinner");
const clearBtn = document.getElementById("clearBtn");
const results = document.getElementById("results");
const errorBox = document.getElementById("errorBox");

const hook = document.getElementById("hook");
const headers = document.getElementById("headers");
const introduction = document.getElementById("introduction");
const tips = document.getElementById("tips");

let latestResult = null;

function setLoading(isLoading) {
    generateBtn.disabled = isLoading;
    buttonText.textContent = isLoading ? "Generating..." : "Generate content";
    spinner.classList.toggle("hidden", !isLoading);
}

function showError(message) {
    errorBox.textContent = message;
    errorBox.classList.remove("hidden");
}

function hideError() {
    errorBox.classList.add("hidden");
    errorBox.textContent = "";
}

function renderResults(data) {
    latestResult = data;

    hook.textContent = data.hook || "";

    headers.innerHTML = "";
    (data.headers || []).forEach((item) => {
        const li = document.createElement("li");
        li.textContent = item;
        headers.appendChild(li);
    });

    introduction.textContent = data.introduction || "";

    tips.innerHTML = "";
    (data.tips || []).forEach((item) => {
        const li = document.createElement("li");
        li.textContent = item;
        tips.appendChild(li);
    });

    results.classList.remove("hidden");
    results.scrollIntoView({ behavior: "smooth", block: "start" });
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    hideError();

    const payload = {
        keyword: document.getElementById("keyword").value.trim(),
        topic: document.getElementById("topic").value.trim(),
        tone: document.getElementById("tone").value
    };

    if (!payload.keyword || !payload.topic) {
        showError("Please complete the target keyword and article topic.");
        return;
    }

    setLoading(true);

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const contentType = response.headers.get("content-type") || "";

        if (!contentType.includes("application/json")) {
            const text = await response.text();
            const message = text.includes("<!doctype") || text.includes("<html")
                ? "The backend is not responding correctly. Open the app through http://127.0.0.1:5000 instead of opening the HTML file directly."
                : text || "The server returned an unexpected response.";
            throw new Error(message);
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Something went wrong.");
        }

        renderResults(data);
    } catch (error) {
        showError(error.message || "Unable to generate content. Please try again.");
    } finally {
        setLoading(false);
    }
});

clearBtn.addEventListener("click", () => {
    form.reset();
    results.classList.add("hidden");
    hideError();
    latestResult = null;
    document.getElementById("keyword").focus();
});

function getCopyText(target) {
    if (target === "hook") {
        return hook.textContent;
    }

    if (target === "introduction") {
        return introduction.textContent;
    }

    if (target === "headers") {
        return [...headers.querySelectorAll("li")]
            .map((item, index) => `${index + 1}. ${item.textContent}`)
            .join("\n");
    }

    if (target === "tips") {
        return [...tips.querySelectorAll("li")]
            .map((item) => `- ${item.textContent}`)
            .join("\n");
    }

    return "";
}

async function copyText(text, button) {
    if (!text) return;

    try {
        await navigator.clipboard.writeText(text);
        const original = button.textContent;
        button.textContent = "Copied";
        setTimeout(() => {
            button.textContent = original;
        }, 1200);
    } catch {
        showError("Copy failed. Please select and copy the text manually.");
    }
}

document.querySelectorAll(".copy-btn").forEach((button) => {
    button.addEventListener("click", () => {
        copyText(getCopyText(button.dataset.copyTarget), button);
    });
});

document.getElementById("copyAllBtn").addEventListener("click", (event) => {
    if (!latestResult) return;

    const text = [
        "SEO BLOG CONTENT",
        "",
        "HOOK",
        latestResult.hook,
        "",
        "ARTICLE OUTLINE",
        ...latestResult.headers.map((item, index) => `${index + 1}. ${item}`),
        "",
        "SEO INTRODUCTION",
        latestResult.introduction,
        "",
        "SEO TIPS",
        ...latestResult.tips.map((item) => `- ${item}`)
    ].join("\n");

    copyText(text, event.currentTarget);
});
