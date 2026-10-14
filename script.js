// mobile menu
const menuBtn = document.querySelector(".menu-btn");
const navLinks = document.getElementById("nav-links");
if (menuBtn && navLinks) {
  menuBtn.addEventListener("click", () => {
    const open = navLinks.classList.toggle("open");
    menuBtn.setAttribute("aria-expanded", open);
    menuBtn.textContent = open ? "Close" : "Menu";
  });
  navLinks.querySelectorAll("a").forEach(a => a.addEventListener("click", () => {
    navLinks.classList.remove("open");
    menuBtn.setAttribute("aria-expanded", false);
    menuBtn.textContent = "Menu";
  }));
}

// reveal on scroll
const revealer = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add("is-visible"); revealer.unobserve(e.target); } });
}, { threshold: .08 });
document.querySelectorAll(".reveal").forEach(el => revealer.observe(el));

// figure lightbox
const figures = document.querySelectorAll(".figure button");
if (figures.length) {
  const box = document.createElement("div");
  box.className = "lightbox";
  box.setAttribute("role", "dialog");
  box.setAttribute("aria-modal", "true");
  box.setAttribute("aria-label", "Enlarged chart");
  box.innerHTML = '<button type="button">Close ✕</button><img alt="">';
  document.body.appendChild(box);
  const big = box.querySelector("img");
  const closeBtn = box.querySelector("button");
  let last = null;
  const close = () => { box.classList.remove("open"); if (last) last.focus(); };
  figures.forEach(b => b.addEventListener("click", () => {
    const img = b.querySelector("img");
    big.src = img.src; big.alt = img.alt; last = b;
    box.setAttribute("aria-label", "Enlarged chart: " + img.alt);
    box.classList.add("open"); closeBtn.focus();
  }));
  box.addEventListener("click", close);
  document.addEventListener("keydown", e => {
    if (!box.classList.contains("open")) return;
    if (e.key === "Escape") close();
    // the close button is the only control in the dialog, so Tab stays on it
    if (e.key === "Tab") { e.preventDefault(); closeBtn.focus(); }
  });
}

// case-study table of contents: highlight the section in view
const tocLinks = document.querySelectorAll(".toc a");
if (tocLinks.length) {
  const byId = {};
  tocLinks.forEach(a => byId[a.getAttribute("href").slice(1)] = a);
  const spy = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        tocLinks.forEach(a => a.classList.remove("on"));
        byId[e.target.id]?.classList.add("on");
      }
    });
  }, { rootMargin: "-30% 0px -60% 0px" });
  document.querySelectorAll(".beat[id]").forEach(s => spy.observe(s));
}
