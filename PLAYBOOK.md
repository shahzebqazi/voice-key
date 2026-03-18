# AI agent playbook — Voice Hotkey

Instructions for **AI coding agents** (e.g. Cursor) working in this repo. Follow these rules unless the user explicitly overrides them.

---

## 1. Agent conduct

### 1.1 Ask before guessing

- If requirements are **ambiguous**, **contradictory**, or **missing**, **ask the user** for clarification instead of inventing product decisions.
- Offer **at most two concrete options** when proposing a choice, then wait for the user's answer.

### 1.2 Complete the Git workflow when work is done

When you finish a **coherent unit of work** (a feature, fix, or doc update the user requested):

1. **`git add`** — stage only paths you changed.
2. **`git commit`** — use a clear, scoped message (see §4).
3. **`git push origin main`** — publish to GitHub.

**Do not** leave completed work uncommitted or unpushed unless the user asked you not to push.

If **push fails**: **stop**, report the error and suggested next steps.

If the workspace is **not a git repository**, skip git commands until the user initializes git; still complete file changes.

### 1.3 Commits: one logical change per commit

- Prefer **one commit per logical change**; avoid mixing unrelated edits.

---

## 2. Design: responsive & aesthetic principles

Apply these when editing **`index.html`**, **`styles/backgrounds.css`**, **`mockups/*.html`**, or **`documents/*.html`**.

### 2.1 Responsive

- Treat the **mockup viewport** as **390×844** (mobile-first reference).
- Use **flex/grid** with **wrap** and sensible `min-width` / `max-width`.
- Prefer **relative units** (`rem`, `%`, `min()`, `clamp()`).
- Ensure **touch targets** are at least ~**44×44px**.

### 2.2 Aesthetic

- Keep **visual hierarchy** clear.
- Maintain **consistent spacing**, **border-radius**, and **typography** with existing patterns.
- **Contrast**: ensure readability on Blueprint, Paper, and Dark Dots themes.
- **Accessibility**: preserve `aria-label`, focus styles, semantic HTML.

---

## 3. GitHub & GitHub Pages

### 3.1 Repository hygiene

- **Branch:** default work on **`main`**.
- Do not commit **secrets**. Use `.gitignore` for local config files.

### 3.2 GitHub Pages (static site)

- Site is **static HTML/CSS/JS**; no build step.
- **Canonical URL:** `https://sqazi.sh/voice-key/`
- Build status header driven by `build-status.json` + `scripts/build-status.js`.
- Ensure relative paths work from the deployed base URL.

---

## 4. Commit message convention

| Prefix     | Use for                  |
|------------|--------------------------|
| `docs:`    | Markdown under `docs/`   |
| `mockups:` | HTML under `mockups/`    |
| `style:`   | CSS / visual shell       |
| `feat:`    | New user-facing behavior |
| `fix:`     | Bug fixes                |
| `chore:`   | Repo config, cleanup     |

Examples: `feat: implement double-tap listener`, `mockups: add settings mockup`, `docs: sync REQUIREMENTS.md`.

---

## 5. Deliverables (source of truth)

- `docs/REQUIREMENTS.md`
- `docs/MENU_INVENTORY.md`
- `docs/MOCKUPS.md`
- `build-status.json`
- `styles/backgrounds.css`
- `scripts/build-status.js`
- `scripts/shell.js`
- `index.html`
- `mockups/*.html`
- `documents/*.html` — executive overview, software requirements, design guide
- `app/` — Python application source
- `requirements.txt`

---

## 6. Artifact build order

1. `docs/MENU_INVENTORY.md`
2. `docs/REQUIREMENTS.md`
3. `docs/MOCKUPS.md` (Mermaid)
4. `index.html`, `styles/backgrounds.css`, `mockups/*.html`
5. Verify navigation + iframe target + responsive shell

**After each step:** commit and push (per §1.2).

---

## 7. Sync: inventory → docs → HTML

When menus change:

1. `MENU_INVENTORY.md` → commit + push
2. `REQUIREMENTS.md` → commit + push
3. Mermaid docs → commit + push
4. `mockups/*.html` + `index.html` → commit + push

---

## 8. Verification before "done"

1. Links and paths resolve for GitHub Pages base path.
2. Mermaid blocks valid (if touched).
3. Build status header resolves or falls back gracefully.
4. Changes committed and pushed.
5. User asked for clarification where needed (§1.1).

---

## Phase 0: New repo (once)

1. `git init` on `main`
2. Minimal `README.md`, `.gitignore`
3. Commit; add remote; `git push -u origin main`
4. Configure GitHub Pages; record live URL in `docs/REQUIREMENTS.md`
