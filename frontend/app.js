// ── Config ────────────────────────────────────────────────────────────────────
const SUPABASE_URL = "https://idgnijbyrxlnecelaxqh.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlkZ25pamJ5cnhsbmVjZWxheHFoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM4MzA2NjAsImV4cCI6MjA4OTQwNjY2MH0.o-BUSomVcpeAcRBmqHaOYypHfJsg3touTyvFSljhMMo";
const API_BASE = "http://127.0.0.1:8001";

const { createClient } = supabase;
const sb = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// ── State ─────────────────────────────────────────────────────────────────────
let currentDraft = null;
let currentDraftId = null;
let currentSlug = null;
let iteration = 1;

// ── Auth guard ────────────────────────────────────────────────────────────────
async function requireAuth() {
  const { data: { session } } = await sb.auth.getSession();
  if (!session) window.location.href = "index.html";
  return session;
}

// ── Login page ────────────────────────────────────────────────────────────────
const loginForm = document.getElementById("login-form");
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const errEl = document.getElementById("error-msg");
    const { error } = await sb.auth.signInWithPassword({ email, password });
    if (error) {
      errEl.textContent = error.message;
      errEl.classList.remove("hidden");
    } else {
      window.location.href = "dashboard.html";
    }
  });
}

// ── Dashboard ─────────────────────────────────────────────────────────────────
if (document.getElementById("step-topic")) {
  requireAuth();

  // Logout
  document.getElementById("logout-btn")
    .addEventListener("click", async () => {
      await sb.auth.signOut();
      window.location.href = "index.html";
    });

  // Show step helper
  function showStep(id) {
    document.querySelectorAll(".step").forEach(s => s.classList.add("hidden"));
    document.getElementById(id).classList.remove("hidden");
  }

  // Option A: Suggest topics
  document.getElementById("btn-suggest").addEventListener("click", async () => {
    document.getElementById("suggestions-panel").classList.remove("hidden");
    document.getElementById("custom-panel").classList.add("hidden");
    document.getElementById("loading-topics").classList.remove("hidden");

    try {
      const res = await fetch(`${API_BASE}/api/topics`);
      if (!res.ok) throw new Error(await res.text());
      const { topics } = await res.json();

      document.getElementById("loading-topics").classList.add("hidden");
      const list = document.getElementById("topic-list");
      list.innerHTML = "";
      topics.forEach(topic => {
        const li = document.createElement("li");
        li.textContent = topic;
        li.addEventListener("click", () => startGenerate(topic, ""));
        list.appendChild(li);
      });
    } catch (err) {
      document.getElementById("loading-topics").textContent =
        "Could not load suggestions: " + err.message;
    }
  });

  // Option B: Custom topic
  document.getElementById("btn-custom").addEventListener("click", () => {
    document.getElementById("custom-panel").classList.remove("hidden");
    document.getElementById("suggestions-panel").classList.add("hidden");
  });

  document.getElementById("btn-submit-custom").addEventListener("click", () => {
    const topic = document.getElementById("custom-topic").value.trim();
    const details = document.getElementById("custom-details").value.trim();
    if (!topic) return alert("Please enter a topic.");
    startGenerate(topic, details);
  });

  // Generate
  async function startGenerate(topic, details) {
    showStep("step-generating");
    try {
      const res = await fetch(`${API_BASE}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic, details })
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      currentDraft = data.draft;
      currentDraftId = data.draft_id;
      currentSlug = data.topic_slug;
      iteration = 1;
      showReview(data);
    } catch (err) {
      showStep("step-topic");
      alert("Generation failed: " + err.message);
    }
  }

  // Show review
  function showReview(data) {
    showStep("step-review");
    document.getElementById("review-headline").textContent = data.draft.headline;
    document.getElementById("review-caption").textContent = data.draft.caption;
    document.getElementById("review-hashtags").textContent =
      data.draft.hashtags.join(" ");
    document.getElementById("card-image").src =
      `${API_BASE}/card/${data.topic_slug}?t=${Date.now()}`;
    document.getElementById("iteration-label").textContent =
      `Version ${iteration}`;
  }

  // Approve
  document.getElementById("btn-approve").addEventListener("click", async () => {
    try {
      const res = await fetch(`${API_BASE}/api/publish`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          draft_id: currentDraftId,
          topic_slug: currentSlug,
          draft: currentDraft,
          card_path: `output/linkedin/${currentSlug}/post.jpg`
        })
      });
      if (!res.ok) throw new Error(await res.text());
      showStep("step-done");
    } catch (err) {
      alert("Publish failed — draft is saved. Error: " + err.message);
    }
  });

  // Improve
  document.getElementById("btn-improve").addEventListener("click", async () => {
    const feedback = document.getElementById("feedback-input").value.trim();
    if (!feedback) return alert("Please describe what you want to improve.");
    showStep("step-generating");
    try {
      const res = await fetch(`${API_BASE}/api/regenerate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          draft_id: currentDraftId,
          topic_slug: currentSlug,
          original_draft: currentDraft,
          feedback
        })
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      currentDraft = data.draft;
      currentDraftId = data.draft_id;
      iteration++;
      document.getElementById("feedback-input").value = "";
      showReview(data);
    } catch (err) {
      showStep("step-review");
      alert("Regeneration failed: " + err.message);
    }
  });

  // New post
  document.getElementById("btn-new").addEventListener("click", () => {
    currentDraft = null;
    currentDraftId = null;
    currentSlug = null;
    iteration = 1;
    document.getElementById("topic-list").innerHTML = "";
    document.getElementById("custom-topic").value = "";
    document.getElementById("custom-details").value = "";
    showStep("step-topic");
  });
}
