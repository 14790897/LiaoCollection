(() => {
  const content = document.querySelector("#mdbook-content");
  const main = content?.querySelector(":scope > main");
  if (!content || !main) return;

  const title = main.querySelector(":scope > h1");
  const list = title?.nextElementSibling;
  if (!list || list.tagName !== "UL") return;

  const details = document.createElement("details");
  details.className = "leeao-page-toc";

  const summary = document.createElement("summary");
  summary.textContent = `本页目录（${list.querySelectorAll("a").length}）`;
  details.append(summary, list);

  const rail = window.matchMedia("(min-width: 1480px)");
  const desktop = window.matchMedia("(min-width: 701px)");
  const placeToc = () => {
    if (rail.matches) {
      content.append(details);
      content.classList.add("leeao-with-toc-rail");
      details.open = true;
    } else {
      title.after(details);
      content.classList.remove("leeao-with-toc-rail");
      details.open = desktop.matches;
    }
  };
  rail.addEventListener("change", placeToc);
  placeToc();
})();
