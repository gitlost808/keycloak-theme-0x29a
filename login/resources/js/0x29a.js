// The main page's motion on Keycloak's login pages. The realm name is typed
// in behind a glowing cursor while the box opens; once it has, the page
// title is typed, then the box's rows appear one after another with their
// labels, links and buttons typed in. A click ripples from the pointer, and
// a click or key press finishes the whole intro at once.
// Ported from dummypage's src/common/scripts (typer.ts, intro.ts, rippler.ts,
// util.ts). Keycloak loads this as a classic script in <head>.
(() => {
  "use strict";

  const CURSOR = "|";
  const TYPE_TIME = 0x29a; // ms to type one whole text, as on the main page
  const ROW_STAGGER = 0x29a / 4; // ms between two rows starting to appear

  const root = document.documentElement;
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  // Hands the box's content over from 0x29a.css's plain fade to this script.
  if (!reducedMotion) root.classList.add("x29a-js");

  const pendingSleeps = new Set();
  let skipped = false;

  const sleep = (ms) =>
    new Promise((resolve) => {
      if (skipped || ms <= 0) {
        resolve();
        return;
      }
      const timeout = window.setTimeout(done, ms);
      function done() {
        window.clearTimeout(timeout);
        pendingSleeps.delete(done);
        resolve();
      }
      pendingSleeps.add(done);
    });

  // Replaces a plain-text element's content with hidden letters, keeping
  // the text whole for screen readers. A prefix is typed first, dimmed, and
  // not read out. Returns null for markup it must not touch, such as an
  // HTML realm name.
  function prepare(element, prefix = "") {
    if (!element || element.children.length > 0) return null;
    const text = element.textContent.trim();
    if (!text) return null;

    const spoken = document.createElement("span");
    spoken.className = "pf-v5-screen-reader";
    spoken.textContent = text;

    const typed = document.createElement("span");
    typed.className = "x29a-typed";
    typed.setAttribute("aria-hidden", "true");
    const letters = Array.from(prefix + text, (letter, index) => {
      const span = document.createElement("span");
      span.textContent = letter;
      span.dataset.letter = letter;
      if (index < prefix.length) span.classList.add("x29a-prefix");
      typed.append(span);
      return span;
    });

    element.replaceChildren(spoken, typed);
    return letters;
  }

  async function type(letters) {
    const timeout = TYPE_TIME / letters.length;
    for (const span of letters) {
      if (skipped) break;
      span.textContent = CURSOR;
      span.classList.add("glow", "show");
      await sleep(timeout);
      span.textContent = span.dataset.letter;
    }
    // A skip ends the loop early: show the rest at once.
    letters.forEach((span) => {
      span.textContent = span.dataset.letter;
      span.classList.add("show");
    });
  }

  // The box's rows in document order: each form group (label, control and
  // error together) and each other block. Containers without text of their
  // own, such as the form and its wrappers, are split into their children.
  const ROW_SELECTOR = ".pf-v5-c-form__group, .pf-v5-c-alert, .pf-v5-c-data-list, ul, ol, p";
  function rowsOf(container) {
    return Array.from(container.children).flatMap((child) => {
      // The header holds the title, which is typed on its own first.
      if (child.matches("script, style, input[type=hidden], .pf-v5-c-login__main-header")) return [];
      const ownText = Array.from(child.childNodes).some(
        (node) => node.nodeType === Node.TEXT_NODE && node.textContent.trim(),
      );
      const splittable =
        child.matches("div, form, section, nav") && !child.matches(ROW_SELECTOR) && !ownText;
      return splittable && child.children.length > 0 ? rowsOf(child) : [child];
    });
  }

  // A row's plain-text pieces worth typing: labels, links, buttons, messages.
  function textsOf(row) {
    const candidates = [row, ...row.querySelectorAll("*")];
    return candidates
      .filter(
        (element) =>
          element.children.length === 0 &&
          element.textContent.trim() &&
          !element.matches("script, style, option, textarea, .kc-tooltip-text, .pf-v5-screen-reader"),
      )
      .map((element) => prepare(element))
      .filter(Boolean);
  }

  function ripple(x, y) {
    const element = document.createElement("div");
    element.className = "x29a-ripple";
    element.addEventListener("animationend", () => element.remove());
    document.body.append(element);
    element.style.top = `${y - element.clientHeight / 2}px`;
    element.style.left = `${x - element.clientWidth / 2}px`;
    return element;
  }

  function skip(except) {
    skipped = true;
    // Shows every row and letter the intro has not reached yet.
    root.classList.add("x29a-skipped");
    Array.from(pendingSleeps).forEach((wake) => wake());
    document.getAnimations().forEach((animation) => {
      if (except.has(animation)) return;
      try {
        animation.finish();
      } catch {
        // Infinite animations cannot finish; leave them running.
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    // The box opens from a line to its full height (x29a-lineglow in
    // 0x29a.css). It is still collapsed here, so measure what it holds; the
    // borders count too, since its max-height is a border-box height.
    // Kode Mono may still be loading; measure again once it has.
    const box = document.querySelector(".pf-v5-c-login__main");
    const measureBox = () => {
      const borders = box.offsetHeight - box.clientHeight;
      box.style.setProperty("--x29a-box-height", `${box.scrollHeight + borders}px`);
    };
    if (box) {
      measureBox();
      document.fonts?.ready.then(measureBox);
    }

    if (reducedMotion) return;

    document.addEventListener("click", (event) => {
      // Keyboard "clicks" carry no position; skip without a ripple.
      const keep = new Set();
      if (event.detail > 0) {
        ripple(event.clientX, event.clientY).getAnimations().forEach((a) => keep.add(a));
      }
      queueMicrotask(() => skip(keep));
    });
    // The username field has focus from the start; whoever types into it
    // before the box has opened should see the whole form at once.
    document.addEventListener("keydown", () => skip(new Set()), { once: true });

    const heading = prepare(document.getElementById("kc-header-wrapper"));
    if (heading) type(heading);
    if (!box) return;

    // The "./" in front is typed with the title; 0x29a.css drops its own.
    const title = prepare(document.getElementById("kc-page-title"), "./");
    const rows = rowsOf(box).map((row) => {
      row.classList.add("x29a-row");
      return { row, texts: textsOf(row) };
    });

    async function intro() {
      if (title) await type(title);
      for (const { row, texts } of rows) {
        row.classList.add("x29a-revealed");
        texts.forEach((letters) => type(letters));
        await sleep(ROW_STAGGER);
      }
    }

    const opening = box.getAnimations().find((a) => a.animationName === "x29a-lineglow");
    if (opening) opening.finished.then(intro, intro);
    else intro();
  });
})();
