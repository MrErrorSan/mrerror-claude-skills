---
name: web-audit
description: >-
  Audit web pages and web apps. By default it audits only the UI (layout,
  visual consistency, match to the design or mock) and the UX (flows, states,
  feedback, match to the spec) at one target screen size. Responsiveness
  across screen sizes, accessibility, SEO, performance, technical health and
  content are separate categories it runs only when the user asks for them.
  Use when a page or UI has been built or changed and needs checking before
  the user reviews it, or when the user asks to audit, review or polish a
  page, site or screen, or names one of those categories. It ranks findings
  by user harm and reports. It finds the browser tools available on the
  machine and asks before installing any. It doesn't apply fixes on its own.
---

# Web audit

The audit catches what the user would otherwise find in their own review. It
stays as small as the question: UI and UX by default, and anything more only
when it's asked for. It reports findings and doesn't apply them. The user
decides what to fix, unless the audit runs inside a build whose plan already
says how review findings get fixed.

**Local files only.** The report, screenshots and scores are files in the
repo, on this machine. No Artifacts, hosted pages or shared links unless the
user asks for one.

## 1. Set the scope

| Category | Runs | Covers |
| --- | --- | --- |
| **UI** | by default | alignment and spacing on a grid; the type scale, palette and components used consistently; nothing overlapping, cut off or broken (images, icons, fonts); the look matches the mock or design |
| **UX** | by default | the spec and mock against what was built; the main path walked as its real user; hierarchy; the empty, loading and error states; feedback on every action; copy that says what to do next |
| **Target screen size** | by default, one size | the size the user names; otherwise the product's main device from the spec; otherwise desktop (1366–1440 px) |
| **Responsiveness** | when asked | the sizes the user names, otherwise phone (390 px), tablet (768 px) and desktop (1440 px): reflow, no horizontal scroll, nothing crushed, touch targets on small screens |
| **Accessibility** | when asked | keyboard reach, visible focus, contrast, labels and alt text, hit target size |
| **SEO** | when asked | titles, meta descriptions, headings, canonical and social-sharing tags, `lang`, structured data, `robots.txt` and the sitemap, crawlable links |
| **Performance** | when asked | automated audit scores, slow first paint of the main content, heavy images and scripts |
| **Technical** | when asked | console errors, failed network requests, broken links |
| **Content** | when asked | spelling, tone, and the same term for the same thing throughout |

- **"Audit this page", or no category named:** UI and UX at the target screen
  size. Nothing else.
- **The user names categories** ("check responsiveness on 390 and 768", "SEO
  only", "full audit"): run exactly those. "Full" means every category.
- **The spec or plan asks for a category** (for example "must meet WCAG AA"):
  include it, and say why in the report.
- If you notice something serious outside the scope while auditing (the page
  crashes, or it can't be indexed at all), report it in one line under
  "Outside the scope". Don't audit that category.

## 2. Find the tools

The audit needs a real browser that can navigate, click and take screenshots.
SEO, accessibility and performance go faster with an automated page audit, if
one is available. Look at what this machine has now:

- **tools in this session** that drive a browser (navigate, act, screenshot,
  read the console, run page audits);
- **browser automation already installed:** in the project's dependencies,
  globally, or as a CLI;
- **an installed browser** that can run headless.

Use the most capable one you find for the scope, and say which in the report.
**If nothing can do the job,** tell the user what's missing, recommend the
option you'd pick and why, and install it only after they approve. If they'd
rather not, audit from the code alone and mark every finding *code-only*.

## 3. Run it

1. **Gather what it should be:** the spec (its acceptance lines and
   decisions), the chosen mock, and the user's request. These are the
   yardstick. The category checks only fill the gaps.
2. **Look at the running pages,** not the code's intentions, at the screen
   sizes in scope, through their real states.
3. **UX: intent first.** Go through the spec line by line, then the mock.
   List what's **missing** (asked for, not built), **different** (built
   another way), and **extra** (built, not asked for). If the spec asks for
   something the mock never showed, check it anyway. Then walk the main path
   as its real user (a customer on a cheap phone, a receptionist, an owner).
4. **Then each category in scope,** using its row in the table above. Run an
   automated audit for the categories it covers, if one is available, and
   record the scores.

## Findings

Rank each finding by user harm:
- **P0:** users lose work, see wrong data or a wrong price, or can't finish
  the main path (or, with SEO in scope, a public page can't be found or
  indexed).
- **P1:** users get stuck or misled; a spec line isn't met.
- **P2:** polish.

Mark each finding **tested** (seen in the running page) or **code-only** (read
in the code, not reproduced). Re-check every P0 before reporting it. A finding
that's a design choice the mock and spec don't settle goes to the user as a
decision.

## The report

Put it where the project's doc rule says, otherwise in
`docs/<feature>/YYYY-MM-DD-<feature>-web-audit.md`. Save screenshots in an
`assets/` folder next to it, named by screen size (`d-…png`, `t-…png`,
`m-…png`), and any audit scores in a sibling `.json`. Include only the
sections for the categories in scope.

```markdown
# Web audit: <page, screen or feature>
Date, the build audited (branch @ sha, how it was served), the spec and mock
compared against, and the browser tool used.
Scope: UI, UX at <screen size>. Not audited: <the other categories>; ask to add any.

## Against the spec and mock
- Missing: <what was asked>, <where it should be>.
- Different: <what was built instead>.

## Findings
- P0 tested: <problem>, <where>. Fix: <suggestion>.
- P1 code-only: <problem>, <where>. Fix: <suggestion>.
- Your call: <a choice the mock and spec leave open>.

## <Each extra category in scope>
<scores, if any, and findings>

## Outside the scope
- <one line per serious issue noticed but not audited>

Re-running this audit: <port, test login, known local-only errors>.
```

Be specific: "the submit button gives no feedback on click, so users
double-submit" beats "improve the button".
