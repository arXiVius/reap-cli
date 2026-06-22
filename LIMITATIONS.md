# 🌾 reap v2.0 — Known Limitations & Risk Map

**Not Guaranteed Behavior Brief: Edge Cases, Failure Modes, and Unverified Assumptions**

This document defines areas where reap v2.0:
❌ may still fail in real-world websites
❌ is not fully proven on modern web stacks
❌ relies on assumptions rather than guaranteed behavior

It is not a feature list — it is a risk map.

---

### ⚠️ 1. JavaScript-Generated Content (NOT GUARANTEED)
**Problem:** Modern websites often generate content at runtime (e.g. React hydration rendering, Vue dynamic DOM updates, Next.js client-side fetches, infinite scroll feeds, lazy-loaded components).
**Why reap may fail:** Even with DOM parsing and optional Playwright snapshots, the engine still misses post-load async fetches, user-triggered rendering, hidden hydration states, and API-driven UI updates.
**Risk Level:** 🔴 HIGH

### ⚠️ 2. SPA Routing Edge Cases (NOT FULLY GUARANTEED)
**Problem:** Modern routers behave differently per framework (history API routing inconsistencies, base path mismatches, nested dynamic routes, route guards).
**Why it can break:** Reap assumes `/route` naturally maps to `/route/index.html` locally. Real SPAs may block route rendering, require runtime JS state, or redirect internally without DOM change.
**Risk Level:** 🔴 HIGH

### ⚠️ 3. CDN Asset Equivalence Assumptions (UNSAFE EDGE CASE)
**Problem:** The normalization engine assumes different CDN hosts serve the same asset.
**Risk:** `cdn1.site.com/image.png` might not strictly equal `cdn2.site.com/image.png` due to versioning or A/B testing.
**Failure mode:** Incorrect deduplication, wrong asset reuse, visual mismatch in offline site.
**Risk Level:** 🟠 MEDIUM–HIGH

### ⚠️ 4. Dynamic API Fetching (NOT HANDLED)
**Problem:** Web apps load content via runtime APIs (`/api/user`, `/graphql`, authenticated endpoints, infinite scroll feeds).
**Why reap cannot guarantee:** These fetches are not in the DOM, not in CSS, and rarely in static JS strings. They require runtime session context that an offline snapshot lacks.
**Risk Level:** 🔴 HIGH

### ⚠️ 5. Rate Limiting & Anti-Bot Systems (UNSTABLE BEHAVIOR)
**Problem:** Real websites block scraping IPs, throttle requests (429/403), serve different content per session, or require cookies / auth.
**Limitations:** Even with the retry system and exponential backoff, it is still possible to suffer partial site captures, silently skipped pages, and inconsistent asset loading.
**Risk Level:** 🔴 HIGH

### ⚠️ 6. CSS/JS Runtime Injection (PARTIAL COVERAGE ONLY)
**Problem:** Not all assets exist in static CSS/HTML. 
**Missing sources:** Runtime-injected `<style>` tags, JS-generated URLs, dynamically imported chunks, and shadow DOM assets.
**Risk Level:** 🟠 MEDIUM–HIGH

### ⚠️ 7. Build Integrity Validator Limitations
**What it does:** Checks file existence, external links, and validates structure.
**What it does NOT guarantee:** Visual correctness, JS runtime correctness, SPA navigation correctness, and API-driven content completeness.
**Risk Level:** 🟠 MEDIUM

### ⚠️ 8. Offline Behavior ≠ Online Behavior
**Problem:** Even if the build completely passes integrity checks, differences will still exist: animations may break, lazy loading timing changes, API-driven UI becomes static, auth-gated content disappears, and infinite scroll becomes a static snapshot.
**Risk Level:** 🟠 MEDIUM (expected limitation)

### ⚠️ 9. Large-Scale Site Behavior (UNTESTED LIMITS)
**Potential issues:** Memory spikes on huge graphs, queue saturation under heavy crawling, slow recovery on partial failures, disk-heavy asset duplication before the dedup phase maps the hashes.
**Risk Level:** 🟠 MEDIUM–HIGH

### ⚠️ 10. Cross-Browser Offline Fidelity (NOT GUARANTEED)
**Problem:** Even if all files are structurally correct, CSS rendering differences offline, JS execution differences (if snapshot used), and local server vs `file://` protocol behavior mismatches will occur.
**Risk Level:** 🟠 MEDIUM
