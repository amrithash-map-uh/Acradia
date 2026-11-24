const state = {
  schemes: [],
  preferredLanguage: "en",
  lastAnswerText: "",
};

const els = {
  profileForm: document.getElementById("profile-form"),
  browseAllBtn: document.getElementById("browse-all-btn"),
  resultsSummary: document.getElementById("results-summary"),
  eligibilityDisclaimer: document.getElementById("eligibility-disclaimer"),
  schemesList: document.getElementById("schemes-list"),
  assistantForm: document.getElementById("assistant-form"),
  assistantScheme: document.getElementById("assistant-scheme"),
  assistantQuestion: document.getElementById("assistant-question"),
  assistantResponse: document.getElementById("assistant-response"),
  assistantMode: document.getElementById("assistant-mode"),
  assistantAnswer: document.getElementById("assistant-answer"),
  assistantCitations: document.getElementById("assistant-citations"),
  assistantDisclaimer: document.getElementById("assistant-disclaimer"),
  speakAnswerBtn: document.getElementById("speak-answer-btn"),
  stopVoiceBtn: document.getElementById("stop-voice-btn"),
  ngoForm: document.getElementById("ngo-form"),
  ngoScheme: document.getElementById("ngo-scheme"),
  ngoFeedback: document.getElementById("ngo-feedback"),
  ngoRequestsList: document.getElementById("ngo-requests-list"),
  ngoDirectory: document.getElementById("ngo-directory"),
};

async function apiFetch(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "Request failed");
  }
  return data;
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text ?? "";
  return div.innerHTML;
}

function populateSchemeSelects(schemes) {
  const options = schemes
    .map((s) => `<option value="${escapeHtml(s.slug)}">${escapeHtml(s.name)}</option>`)
    .join("");
  els.assistantScheme.innerHTML = `<option value="">All Schemes (auto-retrieve)</option>${options}`;
  els.ngoScheme.innerHTML = `<option value="">General Guidance</option>${options}`;
}

function renderSchemes(items, isMatchView = false) {
  if (!items.length) {
    els.schemesList.innerHTML = `<p class="muted">No schemes matched your current profile. Try browsing all schemes or asking the AI assistant.</p>`;
    return;
  }

  els.schemesList.innerHTML = items
    .map((item) => {
      const scheme = isMatchView ? item.scheme : item;
      const reasons = isMatchView ? item.match_reasons : scheme.eligibility_rules?.conditions || [];
      const reasonsHtml = reasons.length
        ? `<ul class="reasons-list">${reasons.map((r) => `<li>${escapeHtml(r)}</li>`).join("")}</ul>`
        : "";

      return `
        <article class="scheme-card">
          <div class="scheme-top">
            <h3>${escapeHtml(scheme.name)}</h3>
            <span class="badge">${escapeHtml(scheme.category)}</span>
          </div>
          <p>${escapeHtml(scheme.description)}</p>
          <div><strong>Benefits:</strong> ${escapeHtml(scheme.benefits)}</div>
          <div>
            <strong>${isMatchView ? "Why it matched:" : "Key conditions:"}</strong>
            ${reasonsHtml}
          </div>
          <div><strong>How to apply:</strong> ${escapeHtml(scheme.application_guidance)}</div>
          <div class="scheme-meta">
            Source: <a href="${escapeHtml(scheme.source_url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(scheme.source_url)}</a>
            &middot; Last reviewed: ${escapeHtml(scheme.last_reviewed)}
          </div>
          <div class="scheme-actions">
            <button type="button" class="btn btn-secondary btn-sm" data-action="ask" data-slug="${escapeHtml(scheme.slug)}" data-name="${escapeHtml(scheme.name)}">Ask AI</button>
            <button type="button" class="btn btn-secondary btn-sm" data-action="speak" data-slug="${escapeHtml(scheme.slug)}">Listen</button>
            <button type="button" class="btn btn-secondary btn-sm" data-action="ngo" data-slug="${escapeHtml(scheme.slug)}">Request NGO Help</button>
          </div>
        </article>
      `;
    })
    .join("");
}

async function speakText(text) {
  try {
    const voicePayload = await apiFetch("/api/voice/speak", {
      method: "POST",
      body: JSON.stringify({
        text,
        language: state.preferredLanguage,
      }),
    });

    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(voicePayload.text);
      utterance.lang = voicePayload.bcp47_lang;
      utterance.onstart = () => {
        els.stopVoiceBtn.hidden = false;
      };
      utterance.onend = () => {
        els.stopVoiceBtn.hidden = true;
      };
      utterance.onerror = () => {
        els.stopVoiceBtn.hidden = true;
      };
      window.speechSynthesis.speak(utterance);
      els.stopVoiceBtn.hidden = false;
    } else {
      alert("Text-to-speech is not supported in this browser.");
    }
  } catch (err) {
    alert(`Voice output error: ${err.message}`);
  }
}

async function loadAllSchemes() {
  const schemes = await apiFetch("/api/schemes");
  state.schemes = schemes;
  populateSchemeSelects(schemes);
  els.resultsSummary.textContent = `Showing all ${schemes.length} curated schemes.`;
  els.eligibilityDisclaimer.hidden = true;
  renderSchemes(schemes, false);
}

async function loadNgoData() {
  const [ngos, requests] = await Promise.all([
    apiFetch("/api/ngos"),
    apiFetch("/api/ngo/requests"),
  ]);

  els.ngoDirectory.innerHTML = ngos
    .map(
      (ngo) => `
      <div class="mini-card">
        <strong>${escapeHtml(ngo.name)}</strong>
        <div>Location: ${escapeHtml(ngo.city)}, ${escapeHtml(ngo.location)}</div>
        <div>Focus: ${escapeHtml(ngo.focus_areas)}</div>
        <div>Contact: ${escapeHtml(ngo.contact_email)}</div>
      </div>
    `
    )
    .join("");

  if (!requests.length) {
    els.ngoRequestsList.innerHTML = `<p class="muted">No help requests submitted yet.</p>`;
    return;
  }

  els.ngoRequestsList.innerHTML = requests
    .map((req) => {
      const statusClass = req.status === "assigned" || req.status === "resolved" ? "badge-success" : "badge-warn";
      const assignedText = req.assigned_ngo
        ? `${escapeHtml(req.assigned_ngo.name)} (${escapeHtml(req.assigned_ngo.location)})`
        : "Pending NGO assignment";

      return `
        <div class="mini-card">
          <div class="scheme-top">
            <strong>Request #${req.id} — ${escapeHtml(req.citizen_name)}</strong>
            <span class="badge ${statusClass}">${escapeHtml(req.status)}</span>
          </div>
          <div>Location: ${escapeHtml(req.location)}</div>
          <div>Assigned NGO: ${assignedText}</div>
          <div>Details: ${escapeHtml(req.message)}</div>
        </div>
      `;
    })
    .join("");
}

els.profileForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    name: document.getElementById("name").value.trim() || null,
    age: Number(document.getElementById("age").value),
    income: Number(document.getElementById("income").value),
    location: document.getElementById("location").value.trim(),
    occupation: document.getElementById("occupation").value.trim(),
    preferred_language: document.getElementById("preferred_language").value,
  };

  state.preferredLanguage = payload.preferred_language;

  try {
    // Save profile and evaluate matching schemes
    await apiFetch("/api/profiles", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    const result = await apiFetch("/api/schemes/match", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    // Keep NGO location synced with profile location for convenience
    document.getElementById("ngo-location").value = payload.location;
    if (payload.name) {
      document.getElementById("ngo-citizen-name").value = payload.name;
    }

    els.resultsSummary.textContent = `Found ${result.matched_count} potentially relevant scheme(s) for your profile.`;
    els.eligibilityDisclaimer.textContent = result.disclaimer;
    els.eligibilityDisclaimer.hidden = false;
    renderSchemes(result.matches, true);
  } catch (err) {
    alert(`Could not evaluate eligibility: ${err.message}`);
  }
});

els.browseAllBtn.addEventListener("click", () => {
  loadAllSchemes().catch((err) => alert(err.message));
});

els.schemesList.addEventListener("click", (event) => {
  const btn = event.target.closest("button[data-action]");
  if (!btn) return;
  const action = btn.dataset.action;
  const slug = btn.dataset.slug;
  const scheme = state.schemes.find((s) => s.slug === slug);

  if (action === "ask") {
    els.assistantScheme.value = slug;
    if (!els.assistantQuestion.value.trim()) {
      els.assistantQuestion.value = `Explain eligibility and how to apply for ${btn.dataset.name}.`;
    }
    els.assistantQuestion.focus();
    els.assistantForm.scrollIntoView({ behavior: "smooth", block: "center" });
  } else if (action === "speak" && scheme) {
    const narration = `${scheme.name}. ${scheme.description} Benefits: ${scheme.benefits} How to apply: ${scheme.application_guidance}`;
    speakText(narration);
  } else if (action === "ngo") {
    els.ngoScheme.value = slug;
    els.ngoForm.scrollIntoView({ behavior: "smooth", block: "center" });
  }
});

els.assistantForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    question: els.assistantQuestion.value.trim(),
    scheme_slug: els.assistantScheme.value || null,
    preferred_language: state.preferredLanguage,
  };

  try {
    const data = await apiFetch("/api/assistant/ask", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    state.lastAnswerText = data.answer;
    els.assistantMode.textContent = data.mode === "rag_llm" ? "AI Grounded (LLM)" : "AI Grounded (Dataset)";
    els.assistantAnswer.textContent = data.answer;
    els.assistantCitations.innerHTML = data.citations.length
      ? `<strong>Sources:</strong> ${data.citations
          .map(
            (c) =>
              `<a href="${escapeHtml(c.source_url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(c.name)}</a> (reviewed ${escapeHtml(c.last_reviewed)})`
          )
          .join(" &middot; ")}`
      : "";
    els.assistantDisclaimer.textContent = data.disclaimer;
    els.assistantResponse.hidden = false;
  } catch (err) {
    alert(`Assistant error: ${err.message}`);
  }
});

els.speakAnswerBtn.addEventListener("click", () => {
  if (state.lastAnswerText) {
    speakText(state.lastAnswerText);
  }
});

els.stopVoiceBtn.addEventListener("click", () => {
  if ("speechSynthesis" in window) {
    window.speechSynthesis.cancel();
  }
  els.stopVoiceBtn.hidden = true;
});

els.ngoForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    citizen_name: document.getElementById("ngo-citizen-name").value.trim(),
    contact_info: document.getElementById("ngo-contact").value.trim(),
    location: document.getElementById("ngo-location").value.trim(),
    scheme_slug: els.ngoScheme.value || null,
    message: document.getElementById("ngo-message").value.trim(),
    consent_given: document.getElementById("ngo-consent").checked,
  };

  try {
    const created = await apiFetch("/api/ngo/requests", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    const assignedName = created.assigned_ngo
      ? `routed to ${created.assigned_ngo.name} (${created.assigned_ngo.contact_email})`
      : "recorded as pending";
    els.ngoFeedback.textContent = `Help request #${created.id} submitted and ${assignedName}.`;
    els.ngoFeedback.hidden = false;
    els.ngoForm.reset();
    document.getElementById("ngo-location").value = payload.location;
    await loadNgoData();
  } catch (err) {
    els.ngoFeedback.textContent = `Could not submit request: ${err.message}`;
    els.ngoFeedback.hidden = false;
  }
});

// Initial load
loadAllSchemes().catch((err) => console.error(err));
loadNgoData().catch((err) => console.error(err));
