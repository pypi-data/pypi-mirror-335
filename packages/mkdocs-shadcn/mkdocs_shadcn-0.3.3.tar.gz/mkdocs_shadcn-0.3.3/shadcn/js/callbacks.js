const onSearchBarClick = (event) => {
  const dialog = document.getElementById("search-dialog");
  if (dialog) {
    dialog.showModal();
  }
};

const closeDialogFactory = (targetID, event) => {
  const dialog = document.getElementById(targetID);
  if (dialog && event.target === dialog) {
    dialog.close();
  }
};

const onSearchDialogClick = (event) => {
  return closeDialogFactory("search-dialog", event);
};

const onInputHandler = (event) => {
  const query = event.target.value;
  if (window.debounceTimer) {
    clearTimeout(debounceTimer);
  }
  window.debounceTimer = setTimeout(() => {
    if (searchWorker && query.length > 2) {
      console.log(`Posting message { "query": "${query}" }`);
      // https://lunrjs.com/guides/searching.html
      // we should append a wilcard and also a boost on exact term
      const lunrQuery = `${query}^10 ${query}* ${query}~1`;
      searchWorker.postMessage({ query: lunrQuery });
    } else if (query.length > 2) {
      console.warn("searchWorker is not defined");
    } else {
      const results = document.getElementById("mkdocs-search-results");
      if (results) {
        while (results.firstChild) {
          results.removeChild(results.firstChild);
        }
      }
    }
  }, 300);
};

const searchShortcutHandler = (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
    event.preventDefault(); // Prevents default browser behavior (e.g., search bar in some apps)
    const dialog = document.getElementById("search-dialog");
    if (dialog) {
      dialog.showModal();
    }
  }
};

const onThemeSwitch = (event) => {
  const root = document.documentElement;
  root.classList.toggle("dark");
  if (root.classList.contains("dark")) {
    localStorage.setItem("theme", "dark");
  } else {
    localStorage.setItem("theme", "light");
  }
};

const onBottomSidebarDialogClick = (event) => {
  const dialog = document.getElementById("bottom-sidebar");
  if (dialog && event.target === dialog) {
    dialog.classList.add("backdrop:opacity-0");
    dialog.classList.remove("backdrop:opacity-80");
    dialog.setAttribute("data-closing", "1");
    const inner = dialog.children.item(0);
    inner.classList.add("translate-y-[60vh]");
    inner.classList.remove("translate-y-0");
    dialog.attributes["op"];
    setTimeout(() => dialog.close(), 250);
    const innerBody = document.getElementById("inner-body");
    if (innerBody) {
      innerBody.classList.remove(
        "rounded-lg",
        "overflow-hidden",
        "scale-[0.95]",
        "translate-y-4"
      );
    }
  }
};

const onMobileMenuButtonClick = (event) => {
  const dialog = document.getElementById("bottom-sidebar");
  if (dialog) {
    dialog.showModal();
    // dialog.classList.add("reveal");
    dialog.classList.remove("backdrop:opacity-0");
    dialog.classList.add("backdrop:opacity-80");
    dialog.removeAttribute("data-closing");
    const inner = dialog.children.item(0);
    inner.classList.remove("translate-y-[60vh]");
    inner.classList.add("translate-y-0");
  }

  const innerBody = document.getElementById("inner-body");
  if (innerBody) {
    innerBody.classList.add(
      "rounded-lg",
      "overflow-hidden",
      "scale-[0.95]",
      "translate-y-4"
    );
  }
  //   document.getElementById("inner-body").classList.add("minimize");
};
