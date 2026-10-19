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
:root{--bg:#f4f5f7;--card:#fff;--ink:#16191f;--ink2:#3d4451;--muted:#6b7280;--line:#e3e5e9;--accent:#2f5bea;--accent-bg:#e8eefd;
--ok:#15803d;--ok-bg:#dcfce7;--bad:#b91c1c;--bad-bg:#fee2e2;--wait:#92400e;--wait-bg:#fef3c7;
--key:#6d28d9;--key-bg:#ede9fe;--time:#0e7490;--time-bg:#cffafe;--chip:#f1f2f4}
@media (prefers-color-scheme:dark){:root{--bg:#111318;--card:#1a1d24;--ink:#eceef2;--ink2:#c5cad3;--muted:#8b93a1;--line:#2b2f38;
--accent:#7c9cff;--accent-bg:#1f2a4a;--ok:#4ade80;--ok-bg:#12301e;--bad:#f87171;--bad-bg:#3a1717;--wait:#fbbf24;--wait-bg:#33270c;
--key:#c4b5fd;--key-bg:#2a2145;--time:#67e8f9;--time-bg:#0f2d33;--chip:#242832}}
*{box-sizing:border-box}
body{margin:0;font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--ink)}
header{background:var(--card);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:2}
.wrap{max-width:960px;margin:0 auto;padding:0 20px}
.top{padding:18px 0 0}
h1{margin:0;font-size:20px;letter-spacing:-.01em}
.meta{color:var(--muted);font-size:13px;margin-top:2px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px;margin:14px 0 4px}
.stat{background:var(--bg);border-radius:10px;padding:8px 12px}
.stat b{display:block;font-size:22px;line-height:1.2}
.stat span{font-size:12px;color:var(--muted)}
.stat.bad b{color:var(--bad)}.stat.wait b{color:var(--wait)}.stat.ok b{color:var(--ok)}
nav{display:flex;gap:2px;overflow-x:auto;margin-top:10px}
nav button{border:0;border-bottom:2px solid transparent;background:none;padding:10px 12px;cursor:pointer;color:var(--muted);font:inherit;font-size:14px;font-weight:500;white-space:nowrap}
nav button.on{color:var(--accent);border-bottom-color:var(--accent)}
.tools{display:flex;gap:12px;align-items:center;padding:10px 0;flex-wrap:wrap}
.tools input{flex:1;min-width:200px;max-width:380px;padding:7px 10px;border:1px solid var(--line);border-radius:8px;font:inherit;font-size:14px;background:var(--card);color:var(--ink)}
.tools .meta{margin:0}
main{padding:8px 20px 60px;max-width:960px;margin:0 auto}
.sec{margin-top:26px}
.sec>h2{font-size:17px;margin:0 0 2px;display:flex;align-items:baseline;gap:8px}
.sec>h2 .n{font-size:13px;font-weight:600;color:var(--muted);background:var(--chip);border-radius:999px;padding:1px 9px}
.sec>p.hint{margin:0 0 10px;color:var(--muted);font-size:13px}
h3{font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin:16px 0 6px}
.card{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--line);border-radius:10px;padding:12px 14px;margin-bottom:8px}
.card.s-blocked{border-left-color:var(--bad)}.card.s-waiting,.card.s-wait{border-left-color:var(--wait)}
.card.s-needs_approval{border-left-color:var(--key)}.card.s-not_before{border-left-color:var(--time)}
.card.approved{border-left-color:var(--ok);background:color-mix(in srgb,var(--ok-bg) 35%,var(--card))}
.card.rejected{opacity:.45}
.row{display:flex;align-items:flex-start;gap:12px}
.main-col{flex:1;min-width:0}
.title{font-weight:600;font-size:15px}
.detail{color:var(--ink2);font-size:14px;margin-top:3px}
.chips{display:flex;flex-wrap:wrap;gap:5px;margin-top:7px}
.chip{font-size:12px;font-weight:500;padding:1px 8px;border-radius:999px;background:var(--chip);color:var(--ink2);white-space:nowrap}
.chip.clear{color:var(--ok);background:var(--ok-bg)}.chip.blocked{color:var(--bad);background:var(--bad-bg)}
.chip.waiting{color:var(--wait);background:var(--wait-bg)}.chip.needs_approval{color:var(--key);background:var(--key-bg)}
.chip.not_before{color:var(--time);background:var(--time-bg)}.chip.late{color:var(--bad);background:var(--bad-bg)}
.chip.label{color:var(--accent);background:var(--accent-bg)}
.why{margin-top:7px;font-size:13px;color:var(--bad)}
.why.soft{color:var(--wait)}
.btns{display:flex;gap:4px;flex-shrink:0}
.btns button{border:1px solid var(--line);background:var(--card);color:var(--ink2);border-radius:7px;width:30px;height:28px;cursor:pointer;font-size:14px;line-height:1}
.btns button.a.on{background:var(--ok);color:#fff;border-color:var(--ok)}
.btns button.r.on{background:var(--bad);color:#fff;border-color:var(--bad)}
details{margin-top:8px}summary{cursor:pointer;color:var(--muted);font-size:12px;user-select:none}
details[open] summary{margin-bottom:4px}
blockquote{margin:6px 0;padding:5px 10px;border-left:3px solid var(--line);color:var(--ink2);background:var(--bg);border-radius:0 6px 6px 0;font-size:13px;font-style:italic}
blockquote .who{font-style:normal;color:var(--muted)}
.small{font-size:12px;color:var(--muted);margin-top:4px}
.doc{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:20px 24px;max-width:72ch}
.doc p{margin:0 0 10px}.doc ul{margin:0 0 12px;padding-left:20px}.doc li{margin:3px 0}
.doc .hdr{color:var(--muted);font-size:13px;border-bottom:1px solid var(--line);padding-bottom:10px;margin-bottom:14px}
.doc h4{margin:16px 0 6px;font-size:15px}
.warn{background:var(--wait-bg);color:var(--wait);border-radius:8px;padding:7px 12px;margin:6px 0;font-size:13px}
.empty{color:var(--muted);font-style:italic;font-size:14px}
.arrow{color:var(--muted);margin:0 4px}
s{color:var(--muted)}
@media (max-width:600px){.wrap,main{padding-left:16px;padding-right:16px}.row{flex-direction:column}.btns{align-self:flex-end}}
</style>
</head>
<body>
<header><div class="wrap">
  <div class="top"><h1 id="h"></h1><div class="meta" id="meta"></div></div>
  <div class="stats" id="stats"></div>
  <nav id="tabs"></nav>
  <div class="tools"><input id="q" placeholder="Filter by any word…"><span class="meta" id="review"></span></div>
</div></header>
<main id="main"></main>
<script>
const D = __DATA__;
const items = Object.fromEntries(D.items.map(i => [i.id, i]));
const byRef = Object.fromEntries(D.items.map(i => [i.ref, i]));
const active = i => !i.superseded_by_ref && i.evidence.some(e => e.found);
const state = {};
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const STATUS = {clear:"ready", blocked:"blocked", waiting:"waiting on something", needs_approval:"needs client approval", not_before:"not before a date"};
const ROUTE = {ticket:"ticket", change_checklist:"config / KB", backlog:"backlog", followup:"follow-up",
  internal_note:"internal note", meeting_brief:"meeting brief", recap:"recap"};
const GROUPS = [["ticket","Bugs"],["change_checklist","Config & knowledge base"],["followup","Promises & follow-ups"],["backlog","Product backlog"]];
const PREFIX = [[/^Look into \(no fix promised\):\s*/i, "look into only"], [/^Remind [^:]+:\s*/i, "reminder"],
  [/^Launch once received:\s*/i, "launch after input"], [/^Chase confirmation \(no invite until confirmed\):\s*/i, "not confirmed, no invite"]];
const fmtDate = s => { const d = new Date(s + "T12:00:00");
  return isNaN(d) ? s : d.toLocaleDateString("en-GB", {weekday:"short", day:"numeric", month:"short"}); };
function clean(title) {
  let t = title, labels = [];
  for (const [re, l] of PREFIX) if (re.test(t)) { t = t.replace(re, ""); labels.push(l); }
  return [t.charAt(0).toUpperCase() + t.slice(1), labels];
}
let tab = "overview";

// ---- one card per item: merge the routes an item was sent to
const workActs = D.actions.filter(a => !["internal_note","meeting_brief","recap"].includes(a.route));
function bucket(a) {
  const i = items[a.item_id];
  if (a.gate.status !== "clear") return "hold";
  if (i && i.type === "waiting_on_client") return "client";
  return "us";
}
function mergeByItem(acts) {
  const m = new Map();
  for (const a of acts) {
    const k = a.item_id || a.id;
    if (!m.has(k)) m.set(k, {...a, routes: [a.route], reasons: [...a.gate.reasons], notes: [...a.gate.notes]});
    else { const x = m.get(k); x.routes.push(a.route); x.reasons.push(...a.gate.reasons); x.notes.push(...a.gate.notes);
      if (!x.date && a.date) x.date = a.date; }
  }
  return [...m.values()];
}
const B = {us: [], client: [], hold: []};
for (const a of workActs) B[bucket(a)].push(a);
for (const k in B) B[k] = mergeByItem(B[k]);
const sortDue = (a, b) => (a.date || "9999").localeCompare(b.date || "9999");

// ---- header
document.getElementById("h").textContent = `${D.client} · call review`;
document.getElementById("meta").textContent =
  `Call on ${fmtDate(D.meeting_date)} · status as of ${fmtDate(D.as_of)} · contact: ${D.primary_contact} · nothing here is sent automatically`;
document.getElementById("stats").innerHTML = [
  [B.us.length, "to do on our side", "ok"], [B.client.length, "waiting on the client", "wait"], [B.hold.length, "on hold by client rules", "bad"],
  [D.items.filter(i => active(i) && ["guardrail","blackout_window"].includes(i.type)).length, "client rules captured", ""]
].map(([n, l, c]) => `<div class="stat ${c}"><b>${n}</b><span>${l}</span></div>`).join("");

const TABS = [["overview","Overview"],["rules","Client rules & decisions"],["changed","Changed during the call"],
  ["recap","Recap email"],["internal","Internal only"],["all","All actions"]];
document.getElementById("tabs").innerHTML = TABS.map(([k, l]) => `<button data-t="${k}">${l}</button>`).join("");
document.getElementById("tabs").onclick = e => { const t = e.target.closest("button")?.dataset.t; if (t) { tab = t; render(); } };
document.getElementById("q").oninput = render;

function matches(text) {
  const q = document.getElementById("q").value.trim().toLowerCase();
  return !q || text.toLowerCase().includes(q);
}
function quotes(i) {
  return (i?.evidence || []).map(e => `<blockquote>${e.found ? "" : "⚠ not found in transcript: "}“${esc(e.quote)}”${e.speaker ? ` <span class="who">— ${esc(e.speaker)}</span>` : ""}</blockquote>`).join("");
}
function card({id, title, status, chips, detail, why, whySoft, more, search}) {
  if (!matches(search)) return "";
  const st = state[id] || "";
  return `<div class="card s-${status || ""} ${st}" data-id="${esc(id)}"><div class="row"><div class="main-col">
    <div class="title">${esc(title)}</div>${detail ? `<div class="detail">${esc(detail)}</div>` : ""}
    ${why ? `<div class="why ${whySoft ? "soft" : ""}">${why}</div>` : ""}
    <div class="chips">${chips.join("")}</div>
    ${more ? `<details><summary>Show quote${more.includes("gate note") ? " & gate notes" : ""}</summary>${more}</details>` : ""}
    </div><div class="btns"><button class="a ${st==="approved"?"on":""}" data-act="approved" title="Approve">✓</button>
    <button class="r ${st==="rejected"?"on":""}" data-act="rejected" title="Reject">✕</button></div></div></div>`;
}
const chip = (t, c = "") => `<span class="chip ${c}">${esc(t)}</span>`;
function actionCard(a) {
  const i = items[a.item_id];
  const [title, labels] = clean(a.title);
  const chips = [];
  if (a.gate.status !== "clear") chips.push(chip(STATUS[a.gate.status] || a.gate.status, a.gate.status));
  labels.forEach(l => chips.push(chip(l, "label")));
  if (a.date) chips.push(chip(`due ${fmtDate(a.date)}${i?.due_phrase ? ` (“${i.due_phrase}”)` : ""}`, a.date < D.as_of && a.route !== "recap" ? "late" : ""));
  if (a.date && a.date < D.as_of && a.route !== "recap") chips.push(chip("past due, check status", "late"));
  if (i?.earliest_start) chips.push(chip(`not before ${fmtDate(i.earliest_start)}`, "not_before"));
  if (i?.owner_person) chips.push(chip(i.owner_person));
  chips.push(chip((a.routes || [a.route]).map(r => ROUTE[r] || r).join(" + ")));
  const reasons = [...new Set(a.reasons || a.gate.reasons)];
  const notes = [...new Set(a.notes || a.gate.notes)];
  const why = reasons.length ? (a.gate.status === "blocked" ? "⛔ " : "") + reasons.map(esc).join("<br>") : "";
  const more = quotes(i) + (i?.trigger_condition ? `<div class="small">Only if: ${esc(i.trigger_condition)}</div>` : "")
    + notes.map(n => `<div class="small">gate note: ${esc(n)}</div>`).join("")
    + (i?.flags?.length ? `<div class="small">flags: ${esc(i.flags.join("; "))}</div>` : "");
  const search = [a.title, i?.detail, a.scope_tags.join(" "), reasons.join(" "), ...(i?.evidence || []).map(e => e.quote)].join(" ");
  return card({id: a.item_id || a.id, title, status: a.gate.status, chips, detail: i?.detail, why,
    whySoft: a.gate.status !== "blocked", more, search});
}
function itemCard(i, label, extra = []) {
  const chips = [chip(label, "label"), ...extra];
  if (i.window_start) chips.push(chip(`${fmtDate(i.window_start)} → ${i.window_end ? fmtDate(i.window_end) : "…"}`, "not_before"));
  if (i.lifted_by) chips.push(chip(`only ${i.lifted_by} can lift it`));
  if (i.forbids_action_kinds?.length) chips.push(chip(`forbids: ${i.forbids_action_kinds.join(", ")}`));
  return card({id: i.id, title: i.title, status: "", chips, detail: i.detail, more: quotes(i),
    search: [i.title, i.detail, i.scope_tags.join(" "), ...i.evidence.map(e => e.quote)].join(" ")});
}
function section(title, hint, html, n) {
  return `<div class="sec"><h2>${esc(title)}${n !== undefined ? ` <span class="n">${n}</span>` : ""}</h2>${hint ? `<p class="hint">${esc(hint)}</p>` : ""}${html || '<div class="empty">nothing here</div>'}</div>`;
}
function doc(text, hdr = "") {
  const lines = String(text || "").split("\n");
  let html = "", list = false;
  const close = () => { if (list) { html += "</ul>"; list = false; } };
  for (const raw of lines) {
    const l = raw.trimEnd();
    if (/^\s*[-*•] /.test(l)) { if (!list) { html += "<ul>"; list = true; } html += `<li>${esc(l.replace(/^\s*[-*•] /, ""))}</li>`; continue; }
    close();
    if (!l.trim() || l.trim() === "---") continue;
    if (/^#+ /.test(l)) html += `<h4>${esc(l.replace(/^#+ /, ""))}</h4>`;
    else if (/:$/.test(l) && l.length < 60) html += `<h4>${esc(l)}</h4>`;
    else html += `<p>${esc(l)}</p>`;
  }
  close();
  return `<div class="doc">${hdr ? `<div class="hdr">${hdr}</div>` : ""}${html || '<p class="empty">empty</p>'}</div>`;
}

function render() {
  document.querySelectorAll("#tabs button").forEach(b => b.classList.toggle("on", b.dataset.t === tab));
  const m = document.getElementById("main");
  if (tab === "overview") {
    const us = GROUPS.map(([r, l]) => {
      const xs = B.us.filter(a => a.routes[0] === r || (!GROUPS.some(([g]) => g === a.routes[0]) && r === "followup")).sort(sortDue);
      const html = xs.map(actionCard).join("");
      return html ? `<h3>${esc(l)}</h3>${html}` : "";
    }).join("");
    m.innerHTML = section("To do on our side", "Ready to go: nothing in the client's rules blocks these.", us, B.us.length)
      + section("Waiting on the client", "Things the client promised to send. Reminders only, at most as often as they asked.", B.client.sort(sortDue).map(actionCard).join(""), B.client.length)
      + section("On hold", "Blocked by a client rule, a missing input or an approval. The reason is under each title.", B.hold.sort(sortDue).map(actionCard).join(""), B.hold.length);
  } else if (tab === "rules") {
    const g = D.items.filter(i => active(i) && ["guardrail","blackout_window"].includes(i.type));
    const dec = D.items.filter(i => active(i) && ["declined","parked"].includes(i.status) && !["guardrail","blackout_window"].includes(i.type));
    const chk = D.items.filter(i => !i.evidence.some(e => e.found));
    m.innerHTML = section("Client rules", "What the client said we must not do, or not do yet. The gate checks every action against these.",
        g.map(i => itemCard(i, i.type === "blackout_window" ? "blackout window" : "rule")).join(""), g.length)
      + section("Not doing / parked", "Declined or put on hold during the call.", dec.map(i => itemCard(i, i.status === "parked" ? "parked" : "declined")).join(""), dec.length)
      + (chk.length ? section("Needs a human check", "The quote for these was not found in the transcript.", chk.map(i => itemCard(i, "unverified")).join(""), chk.length) : "");
  } else if (tab === "changed") {
    const sup = D.items.filter(i => i.superseded_by_ref);
    m.innerHTML = section("Changed or merged during the call", "Earlier statements that a later one replaced, or duplicates merged into one item.",
      sup.map(i => { const n = byRef[i.superseded_by_ref];
        return card({id: i.id, title: i.title, status: "", chips: [chip("replaced by", "label"), chip(n ? n.title : "?")],
          detail: n ? `Now: ${n.detail}` : "", more: quotes(i), search: [i.title, i.detail, n?.title].join(" ")}); }).join(""), sup.length);
  } else if (tab === "recap") {
    const t = D.drafts.recap_email || "";
    const [, to = "", subj = ""] = t.match(/^To: (.*)\nSubject: (.*)\n/) || [];
    const body = t.replace(/^To: .*\nSubject: .*\n/, "");
    m.innerHTML = section("Recap email draft", "Not sent. A human edits and sends it.",
      (D.draft_flags || []).map(f => `<div class="warn">Check: ${esc(f)}</div>`).join("")
      + doc(body, `<b>To:</b> ${esc(to)}<br><b>Subject:</b> ${esc(subj)}`));
  } else if (tab === "internal") {
    const ia = mergeByItem(D.actions.filter(a => ["internal_note","meeting_brief"].includes(a.route)));
    m.innerHTML = section("Internal notes", "For the vendor team only. Never goes to the client.", doc(D.drafts.internal_notes))
      + (D.drafts.meeting_brief ? section("Meeting brief", "", doc(D.drafts.meeting_brief)) : "")
      + section("Internal items", "", ia.map(actionCard).join(""), ia.length)
      + ((D.warnings || []).length ? section("Pipeline warnings", "", D.warnings.map(w => `<div class="warn">${esc(w)}</div>`).join(""), D.warnings.length) : "");
  } else {
    m.innerHTML = Object.keys(ROUTE).map(r => {
      const acts = D.actions.filter(a => a.route === r);
      return acts.length ? section(ROUTE[r], "", acts.map(a => actionCard({...a, routes: [a.route]})).join(""), acts.length) : "";
    }).join("");
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
