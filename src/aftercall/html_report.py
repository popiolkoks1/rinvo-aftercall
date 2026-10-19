"""Self-contained review page for a run: runs/<dir>/report.html.

One HTML file with the run data embedded, plain CSS + vanilla JS. Approve/Reject only
change the page state (no backend yet); see README "Next steps".
"""

from __future__ import annotations

import json
from pathlib import Path


def build(run_dir: Path) -> Path:
    data = json.loads((run_dir / "items.json").read_text())
    drafts = {}
    for name in ("recap_email", "internal_notes", "meeting_brief"):
        f = run_dir / "drafts" / f"{name}.md"
        drafts[name] = f.read_text() if f.exists() else ""
    payload = json.dumps({**data, "drafts": drafts}, ensure_ascii=False).replace("</", "<\\/")
    out = run_dir / "report.html"
    out.write_text(TEMPLATE.replace("__DATA__", payload), encoding="utf-8")
    return out


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>aftercall review</title>
<style>
:root{--bg:#f6f7f9;--card:#fff;--ink:#1d2330;--muted:#6b7280;--line:#e5e7eb;--accent:#2f5bea;
--ok:#15803d;--ok-bg:#dcfce7;--bad:#b91c1c;--bad-bg:#fee2e2;--wait:#a16207;--wait-bg:#fef3c7;
--key:#6d28d9;--key-bg:#ede9fe;--time:#0e7490;--time-bg:#cffafe}
*{box-sizing:border-box}
body{margin:0;font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--ink)}
header{background:var(--card);border-bottom:1px solid var(--line);padding:16px 24px;position:sticky;top:0;z-index:2}
header h1{margin:0;font-size:18px}
.meta{color:var(--muted);margin-top:2px}
.stats{display:flex;gap:10px;margin-top:10px;flex-wrap:wrap}
.stat{background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:4px 12px}
.stat b{font-size:16px;margin-right:4px}
nav{display:flex;gap:4px;margin-top:12px;flex-wrap:wrap}
nav button{border:0;background:none;padding:8px 12px;border-radius:6px;cursor:pointer;color:var(--muted);font-weight:500}
nav button.on{background:var(--accent);color:#fff}
.tools{display:flex;gap:8px;margin-top:10px}
.tools input{flex:1;max-width:420px;padding:8px 10px;border:1px solid var(--line);border-radius:6px;font:inherit}
main{padding:20px 24px;max-width:1100px}
h2{font-size:13px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);margin:24px 0 8px}
.card{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--line);border-radius:8px;padding:12px 14px;margin-bottom:8px}
.card.approved{border-left-color:var(--ok)}.card.rejected{border-left-color:var(--bad);opacity:.55}
.row{display:flex;align-items:flex-start;gap:10px}
.title{flex:1;font-weight:600}
.sub{color:var(--muted);font-size:12px;margin-top:2px}
.badge{font-size:11px;font-weight:600;padding:2px 8px;border-radius:999px;white-space:nowrap}
.clear{color:var(--ok);background:var(--ok-bg)}.blocked{color:var(--bad);background:var(--bad-bg)}
.waiting{color:var(--wait);background:var(--wait-bg)}.needs_approval{color:var(--key);background:var(--key-bg)}
.not_before{color:var(--time);background:var(--time-bg)}.neutral{color:var(--muted);background:var(--bg)}
.btns button{border:1px solid var(--line);background:var(--card);border-radius:6px;padding:3px 10px;cursor:pointer;font:inherit;font-size:12px}
.btns button.a.on{background:var(--ok);color:#fff;border-color:var(--ok)}
.btns button.r.on{background:var(--bad);color:#fff;border-color:var(--bad)}
details{margin-top:8px}summary{cursor:pointer;color:var(--accent);font-size:12px}
blockquote{margin:6px 0;padding:4px 10px;border-left:3px solid var(--line);color:#374151;background:var(--bg);border-radius:0 4px 4px 0}
.reason{font-size:12px;margin:4px 0}.reason.bad{color:var(--bad)}
.tag{display:inline-block;font-size:11px;background:var(--bg);border:1px solid var(--line);border-radius:4px;padding:0 5px;margin:2px 2px 0 0;color:var(--muted)}
pre{white-space:pre-wrap;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:16px;font:13px/1.55 ui-monospace,Menlo,monospace}
.warn{background:var(--wait-bg);color:var(--wait);border-radius:6px;padding:6px 10px;margin:4px 0;font-size:12px}
.empty{color:var(--muted);font-style:italic}
s{color:var(--muted)}
</style>
</head>
<body>
<header>
  <h1 id="h"></h1><div class="meta" id="meta"></div>
  <div class="stats" id="stats"></div>
  <nav id="tabs"></nav>
  <div class="tools"><input id="q" placeholder="Filter by title, detail, tag, quote…"><span class="meta" id="review"></span></div>
</header>
<main id="main"></main>
<script>
const D = __DATA__;
const items = Object.fromEntries(D.items.map(i => [i.id, i]));
const byRef = Object.fromEntries(D.items.map(i => [i.ref, i]));
const active = i => !i.superseded_by_ref && i.evidence.some(e => e.found);
const state = {};  // card id -> "approved" | "rejected"
const ROUTES = [["ticket","Tickets"],["change_checklist","Config / KB / launch checklist"],["backlog","Product backlog"],
  ["followup","Follow-ups"],["internal_note","Internal notes"],["meeting_brief","Meeting brief"],["recap","Client recap"]];
const LABEL = {clear:"clear",blocked:"blocked",waiting:"waiting",needs_approval:"needs approval",not_before:"not before"};
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
let tab = "actions";

document.getElementById("h").textContent = `${D.client} · call review`;
document.getElementById("meta").textContent =
  `Call ${D.meeting_date} · as of ${D.as_of} · primary contact ${D.primary_contact} · language ${D.language}`;
const blocked = D.actions.filter(a => a.gate.status === "blocked");
document.getElementById("stats").innerHTML = [
  [D.items.length, "items"], [D.items.filter(active).length, "active"], [D.actions.length, "actions"],
  [blocked.length, "blocked"], [D.items.filter(i => i.superseded_by_ref).length, "superseded"]
].map(([n, l]) => `<span class="stat"><b>${n}</b>${l}</span>`).join("");

const TABS = [["actions","Actions by route"],["blocked","Blocked by gate"],["guards","Guardrails & decisions"],
  ["superseded","Superseded"],["recap","Recap draft"],["internal","Internal notes & meeting brief"]];
document.getElementById("tabs").innerHTML = TABS.map(([k, l]) => `<button data-t="${k}">${l}</button>`).join("");
document.getElementById("tabs").onclick = e => { if (e.target.dataset.t) { tab = e.target.dataset.t; render(); } };
document.getElementById("q").oninput = render;

function matches(text) {
  const q = document.getElementById("q").value.trim().toLowerCase();
  return !q || text.toLowerCase().includes(q);
}
function quotes(i) {
  return (i?.evidence || []).map(e => `<blockquote>${e.found ? "" : "⚠ not found in transcript: "}“${esc(e.quote)}”${e.speaker ? ` <span class="sub">— ${esc(e.speaker)}</span>` : ""}</blockquote>`).join("");
}
function tags(list) { return (list || []).map(t => `<span class="tag">${esc(t)}</span>`).join(""); }
function card(id, title, badge, badgeCls, sub, body, searchText) {
  if (!matches(searchText)) return "";
  const st = state[id] || "";
  return `<div class="card ${st}" data-id="${esc(id)}">
    <div class="row"><div class="title">${esc(title)}<div class="sub">${sub}</div></div>
      <span class="badge ${badgeCls}">${esc(badge)}</span>
      <span class="btns"><button class="a ${st==="approved"?"on":""}" data-act="approved">Approve</button>
      <button class="r ${st==="rejected"?"on":""}" data-act="rejected">Reject</button></span></div>
    <details><summary>Details, evidence & gate</summary>${body}</details></div>`;
}
function actionCard(a) {
  const i = items[a.item_id];
  const sub = [a.route.replace("_", " "), a.kind, a.date ? `due ${a.date}` : "", a.date && a.date < D.as_of && a.route !== "recap" ? "past due, status unknown" : "",
    i?.earliest_start ? `not before ${i.earliest_start}` : "", i ? `item ${i.id}` : ""].filter(Boolean).join(" · ");
  const reasons = a.gate.reasons.map(r => `<div class="reason ${a.gate.status==="blocked"?"bad":""}">${a.gate.status==="blocked"?"⛔ blocked by ":"• "}${esc(r)}</div>`).join("")
    + a.gate.notes.map(n => `<div class="reason">• gate note: ${esc(n)}</div>`).join("");
  const body = `${i ? `<p>${esc(i.detail)}</p>` : ""}${i?.trigger_condition ? `<p><b>Only if:</b> ${esc(i.trigger_condition)}</p>` : ""}
    ${reasons}${quotes(i)}<div>${tags(a.scope_tags)}</div>${i?.flags?.length ? `<div class="sub">flags: ${esc(i.flags.join("; "))}</div>` : ""}`;
  const text = [a.title, i?.detail, a.scope_tags.join(" "), a.gate.reasons.join(" "), ...(i?.evidence || []).map(e => e.quote)].join(" ");
  return card(a.id, a.title, LABEL[a.gate.status] || a.gate.status, a.gate.status, sub, body, text);
}
function itemCard(i, badge) {
  const sub = [i.type.replace(/_/g, " "), i.status, i.window_start ? `${i.window_start} → ${i.window_end || "…"}` : "",
    i.lifted_by ? `lifted by ${i.lifted_by}` : "", i.forbids_action_kinds?.length ? `forbids ${i.forbids_action_kinds.join(", ")}` : "", i.id].filter(Boolean).join(" · ");
  const body = `<p>${esc(i.detail)}</p>${quotes(i)}<div>${tags(i.scope_tags)}</div>`;
  return card(i.id, i.title, badge, "neutral", sub, body, [i.title, i.detail, i.scope_tags.join(" "), ...i.evidence.map(e => e.quote)].join(" "));
}
function section(title, html) { return `<h2>${esc(title)}</h2>${html || '<div class="empty">nothing here</div>'}`; }

function render() {
  document.querySelectorAll("#tabs button").forEach(b => b.classList.toggle("on", b.dataset.t === tab));
  const m = document.getElementById("main");
  if (tab === "actions") {
    m.innerHTML = ROUTES.map(([r, l]) => {
      const acts = D.actions.filter(a => a.route === r);
      return acts.length ? section(`${l} (${acts.length})`, acts.map(actionCard).join("")) : "";
    }).join("");
  } else if (tab === "blocked") {
    m.innerHTML = section(`Blocked by the gate (${blocked.length})`, blocked.map(actionCard).join(""));
  } else if (tab === "guards") {
    const g = D.items.filter(i => active(i) && ["guardrail","blackout_window"].includes(i.type));
    const dec = D.items.filter(i => active(i) && ["declined","parked"].includes(i.status) && !["guardrail","blackout_window"].includes(i.type));
    const chk = D.items.filter(i => !i.evidence.some(e => e.found));
    m.innerHTML = section(`Guardrails & blackouts (${g.length})`, g.map(i => itemCard(i, i.type === "blackout_window" ? "blackout" : "guardrail")).join(""))
      + section(`Decisions: not doing / parked (${dec.length})`, dec.map(i => itemCard(i, i.status)).join(""))
      + section(`Needs a human check: quote not found (${chk.length})`, chk.map(i => itemCard(i, "unverified")).join(""));
  } else if (tab === "superseded") {
    const sup = D.items.filter(i => i.superseded_by_ref);
    m.innerHTML = section(`Superseded or merged (${sup.length})`, sup.map(i => {
      const n = byRef[i.superseded_by_ref];
      return itemCard({...i, title: `${i.title}  →  ${n ? n.title : "?"}`, detail: `${i.detail}\n\nReplaced by ${n ? n.id : "?"}. ${(i.flags || []).filter(f => /supersed|duplicate/.test(f)).join("; ")}`}, "superseded");
    }).join(""));
  } else if (tab === "recap") {
    m.innerHTML = section("Recap draft (not sent)", (D.draft_flags || []).map(f => `<div class="warn">check: ${esc(f)}</div>`).join("") + `<pre>${esc(D.drafts.recap_email)}</pre>`);
  } else {
    m.innerHTML = section("Internal notes", `<pre>${esc(D.drafts.internal_notes) || "—"}</pre>`)
      + section("Meeting brief", D.drafts.meeting_brief ? `<pre>${esc(D.drafts.meeting_brief)}</pre>` : "")
      + section("Pipeline warnings", (D.warnings || []).map(w => `<div class="warn">${esc(w)}</div>`).join(""));
  }
  const n = Object.values(state);
  document.getElementById("review").textContent =
    `${n.filter(s => s === "approved").length} approved · ${n.filter(s => s === "rejected").length} rejected (this page only, not saved)`;
}
document.getElementById("main").onclick = e => {
  const act = e.target.dataset.act; if (!act) return;
  const id = e.target.closest(".card").dataset.id;
  state[id] = state[id] === act ? undefined : act;
  if (!state[id]) delete state[id];
  render();
};
render();
</script>
</body>
</html>
"""
