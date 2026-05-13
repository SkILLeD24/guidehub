const CARD_CONTENT_TYPES = ["Guide", "Review", "Build", "Tips & Tricks"];
const FALLBACK_IMAGE = "assets/images/guidehub-logo.png";

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function toGeneralCategory(genre) {
  const value = (genre || "").toLowerCase();
  if (value.includes("rpg") || value.includes("crpg") || value.includes("souls")) return "RPG";
  if (value.includes("shooter") || value.includes("tactical") || value.includes("battle royale") || value.includes("arena")) return "Shooter";
  if (value.includes("strategy") || value.includes("moba")) return "Strategy";
  if (value.includes("sandbox")) return "Sandbox";
  if (value.includes("sim")) return "Simulation";
  if (value.includes("platform")) return "Platformer";
  if (value.includes("horror")) return "Horror";
  if (value.includes("adventure") || value.includes("action")) return "Action Adventure";
  return "Other";
}

async function api(path, options = {}) {
  const response = await fetch(path, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || "Request failed");
  return data;
}

async function getCurrentUser() {
  return api("/api/auth/me");
}

function hubPageForRole(role) {
  return role === "admin" ? "admin.html" : "submit.html";
}

function dashboardText(role) {
  return role === "admin" ? "Open dashboard" : "Submit content";
}

function initBackToTopButton() {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "back-to-top";
  button.setAttribute("aria-label", "Back to top");
  button.textContent = "Back to top";
  document.body.appendChild(button);

  const toggleVisibility = () => {
    button.classList.toggle("visible", window.scrollY > 420);
  };

  window.addEventListener("scroll", toggleVisibility, { passive: true });
  toggleVisibility();

  button.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
}

async function refreshSessionUI() {
  const user = await getCurrentUser();
  const accountButton = document.getElementById("accountButton");
  const logoutButton = document.getElementById("logoutButton");

  if (accountButton) {
    accountButton.textContent = user.authenticated ? `${user.username} (${user.role})` : "Cont";
  }
  if (logoutButton) {
    logoutButton.classList.toggle("hidden", !user.authenticated);
    logoutButton.onclick = async () => {
      await api("/api/auth/logout", { method: "POST" });
      window.location.href = "/index.html";
    };
  }

  document.querySelectorAll("[data-hub-link]").forEach((link) => {
    link.setAttribute("href", hubPageForRole(user.role));
  });
  document.querySelectorAll("[data-dashboard-cta]").forEach((el) => {
    el.textContent = dashboardText(user.role);
  });

  const roleName = document.querySelector("[data-current-role-name]");
  const roleText = document.querySelector("[data-current-role-text]");
  if (roleName) roleName.textContent = user.authenticated ? (user.role === "admin" ? "Admin" : "User") : "Guest";
  if (roleText) {
    roleText.textContent = !user.authenticated
      ? "Poate doar vizualiza continutul public."
      : user.role === "admin"
      ? "Poate publica, modifica, sterge si modera articole."
      : "Poate trimite articole si urmari statusul de moderare.";
  }

  return user;
}

function initLoginModal() {
  const accountButton = document.getElementById("accountButton");
  const loginModal = document.getElementById("loginModal");
  const closeLoginModal = document.getElementById("closeLoginModal");
  const loginForm = document.getElementById("loginForm");
  const loginMessage = document.getElementById("loginMessage");
  if (!accountButton || !loginModal) return;

  accountButton.addEventListener("click", async () => {
    const user = await getCurrentUser();
    if (user.authenticated) {
      window.location.href = `/${hubPageForRole(user.role)}`;
      return;
    }
    loginModal.classList.remove("hidden");
  });

  closeLoginModal?.addEventListener("click", () => loginModal.classList.add("hidden"));

  loginForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      await api("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: document.getElementById("loginEmail").value.trim(),
          password: document.getElementById("loginPassword").value.trim(),
        }),
      });
      window.location.reload();
    } catch (error) {
      loginMessage.textContent = error.message;
    }
  });
}

function initRegisterForm() {
  const registerForm = document.getElementById("registerForm");
  if (!registerForm) return;
  registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = document.getElementById("registerMessage");
    try {
      await api("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: document.getElementById("registerUsername").value.trim(),
          email: document.getElementById("registerEmail").value.trim(),
          password: document.getElementById("registerPassword").value.trim(),
          confirmPassword: document.getElementById("registerConfirmPassword").value.trim(),
        }),
      });
      message.textContent = "Cont creat cu succes. Te poti loga acum.";
      registerForm.reset();
    } catch (error) {
      message.textContent = error.message;
    }
  });
}

function renderPlatforms(platforms) {
  return (platforms || []).map((platform) => `<span>${escapeHtml(platform)}</span>`).join("");
}

async function renderLatestArticles() {
  const container = document.getElementById("latestArticles");
  if (!container) return;
  container.innerHTML = "<p>Loading latest articles...</p>";
  let items = [];
  try {
    items = await api("/api/articles/latest?limit=8");
  } catch (_error) {
    container.innerHTML = "<p>Could not load latest approved articles right now.</p>";
    return;
  }
  container.innerHTML = items.length
    ? items.map((item) => `
      <article class="feed-item compact-feed-item">
        <div>
          <span class="tag tag-neutral">${escapeHtml(item.category)}</span>
          <h4>${escapeHtml(item.title)}</h4>
          <p>${escapeHtml(item.summary || "")}</p>
        </div>
        <div class="feed-meta">
          <strong>${escapeHtml(item.game)}</strong>
          <span>${escapeHtml(item.author)}</span>
        </div>
      </article>
    `).join("")
    : "<p>No approved articles yet.</p>";
}

async function renderHomePage() {
  const cardsGrid = document.getElementById("cardsGrid");
  if (!cardsGrid) return;
  cardsGrid.innerHTML = "<p>Loading games...</p>";
  const games = await api("/api/games");
  const genreFilters = document.getElementById("genreFilters");
  const searchInput = document.getElementById("searchInput");
  const searchBtn = document.getElementById("searchBtn");
  const emptyState = document.getElementById("emptyState");
  const heroStats = document.getElementById("heroStats");

  let currentGenre = "all";
  const genres = ["all", ...new Set(games.map((g) => toGeneralCategory(g.genre)).filter(Boolean))];
  genreFilters.innerHTML = genres.map((genre) => `
    <button class="filter-btn ${genre === "all" ? "active" : ""}" data-genre="${escapeHtml(genre)}">
      ${genre === "all" ? "All categories" : escapeHtml(genre)}
    </button>
  `).join("");

  const totalApproved = games.reduce((sum, game) => sum + (game.approved_articles || 0), 0);
  const totalSources = games.reduce((sum, game) => sum + (game.source_count || 0), 0);
  heroStats.innerHTML = `
    <div class="stat-card"><strong>${games.length}</strong><span>Games in database</span></div>
    <div class="stat-card"><strong>${totalApproved}</strong><span>Approved articles</span></div>
    <div class="stat-card"><strong>${totalSources}</strong><span>Guide sources</span></div>
  `;

  function renderCards() {
    const query = (searchInput?.value || "").trim().toLowerCase();
    const filtered = games.filter((game) => {
      const matchesGenre = currentGenre === "all" || toGeneralCategory(game.genre) === currentGenre;
      const text = `${game.title} ${game.genre} ${game.description} ${game.studio} ${(game.platforms || []).join(" ")}`.toLowerCase();
      return matchesGenre && text.includes(query);
    });

    cardsGrid.innerHTML = filtered.map((game) => `
      <article class="game-card clickable-card" data-link="game.html?game=${encodeURIComponent(game.slug)}">
        <div class="card-image"><img src="${escapeHtml(game.image_url || FALLBACK_IMAGE)}" alt="${escapeHtml(game.title)}" onerror="this.onerror=null;this.src='${FALLBACK_IMAGE}'" /></div>
        <div class="card-content">
          <div class="card-topline">
            <span class="card-genre">${escapeHtml(toGeneralCategory(game.genre))}</span>
            <span class="card-year">${escapeHtml(game.release_year || "-")}</span>
          </div>
          <h3>${escapeHtml(game.title)}</h3>
          <p>${escapeHtml(game.description || "No description yet.")}</p>
          <div class="card-studio">${escapeHtml(game.studio || "Unknown studio")}</div>
          <div class="card-platforms">${renderPlatforms(game.platforms)}</div>
          <div class="card-action-row">
            <a class="view-btn" href="game.html?game=${encodeURIComponent(game.slug)}">Open game page</a>
            <span class="likes">${game.approved_articles || 0} articles</span>
          </div>
        </div>
      </article>
    `).join("");

    emptyState.classList.toggle("hidden", filtered.length > 0);
    document.querySelectorAll(".clickable-card").forEach((card) => {
      card.addEventListener("click", (event) => {
        if (event.target.closest("a")) return;
        window.location.href = card.dataset.link;
      });
    });
  }

  genreFilters.querySelectorAll(".filter-btn").forEach((button) => {
    button.addEventListener("click", () => {
      genreFilters.querySelectorAll(".filter-btn").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      currentGenre = button.dataset.genre;
      renderCards();
    });
  });

  searchBtn?.addEventListener("click", renderCards);
  searchInput?.addEventListener("input", renderCards);
  renderCards();
  await renderLatestArticles();
}

async function renderGamePage(user) {
  const titleNode = document.getElementById("gameTitle");
  if (!titleNode) return;
  const params = new URLSearchParams(window.location.search);
  const slug = params.get("game");
  if (!slug) return;

  const { game, articles, sources } = await api(`/api/games/${encodeURIComponent(slug)}`);
  document.getElementById("breadcrumbGame").textContent = game.title;
  document.getElementById("heroLabel").textContent = game.studio;
  document.getElementById("gameTitle").textContent = game.title;
  document.getElementById("gameDescription").textContent = game.description || "No description.";
  const heroImage = document.getElementById("heroImage");
  heroImage.src = game.image_url || FALLBACK_IMAGE;
  heroImage.onerror = () => { heroImage.src = FALLBACK_IMAGE; };
  document.getElementById("panelMeta").textContent = `${articles.filter((a) => CARD_CONTENT_TYPES.includes(a.category)).length} approved articles`;
  document.getElementById("overviewText").textContent = game.description || "No overview.";

  document.getElementById("heroTags").innerHTML = [game.genre, game.difficulty, game.studio, game.release_year]
    .filter(Boolean)
    .map((x) => `<span class="tag tag-neutral">${escapeHtml(x)}</span>`)
    .join("");

  document.getElementById("quickInfoList").innerHTML = `
    <div><span>Genre</span><strong>${escapeHtml(game.genre || "-")}</strong></div>
    <div><span>Difficulty</span><strong>${escapeHtml(game.difficulty || "-")}</strong></div>
    <div><span>Studio</span><strong>${escapeHtml(game.studio || "-")}</strong></div>
    <div><span>Release year</span><strong>${escapeHtml(game.release_year || "-")}</strong></div>
    <div><span>Platforms</span><strong>${escapeHtml((game.platforms || []).join(", ") || "-")}</strong></div>
  `;

  document.getElementById("roleNote").textContent = user.role === "admin"
    ? "Admin: poti modera si publica din dashboard."
    : user.role === "user"
    ? "User: poti trimite articole pentru aprobare."
    : "Guest: poti doar vizualiza continutul public.";

  document.getElementById("sourceList").innerHTML = sources.length
    ? sources.map((source) => `<div class="source-item"><strong><a href="${escapeHtml(source.url)}" target="_blank" rel="noreferrer">${escapeHtml(source.title)}</a></strong></div>`).join("")
    : `<div class="source-item"><strong><a href="${escapeHtml(game.official_url)}" target="_blank" rel="noreferrer">Official source</a></strong></div>`;

  const contentArticles = articles.filter((a) => CARD_CONTENT_TYPES.includes(a.category));
  const codeArticles = articles.filter((a) => a.category === "Codes");
  const couponArticles = articles.filter((a) => a.category === "Discount Coupons");

  document.getElementById("gameCommunityMetrics").innerHTML = `
    <div class="metric-row"><span>Approved content</span><strong>${contentArticles.length}</strong></div>
    <div class="metric-row"><span>Codes</span><strong>${codeArticles.length}</strong></div>
    <div class="metric-row"><span>Coupons</span><strong>${couponArticles.length}</strong></div>
  `;

  document.getElementById("codesList").innerHTML = codeArticles.length
    ? codeArticles.map((a) => `<article class="promo-item"><h4>${escapeHtml(a.title)}</h4><p>${escapeHtml(a.summary || a.content)}</p></article>`).join("")
    : "<p>No active codes for this game right now.</p>";

  document.getElementById("couponsList").innerHTML = couponArticles.length
    ? couponArticles.map((a) => `<article class="promo-item"><h4>${escapeHtml(a.title)}</h4><p>${escapeHtml(a.summary || a.content)}</p></article>`).join("")
    : "<p>No active coupons for this game right now.</p>";

  const filters = document.getElementById("articleTypeFilters");
  const list = document.getElementById("gameArticleList");
  let currentType = "all";
  const types = [{ key: "all", label: "All content" }, ...CARD_CONTENT_TYPES.map((type) => ({ key: type, label: type }))];
  filters.innerHTML = types.map((type) => `<button type="button" class="type-filter ${type.key === "all" ? "active" : ""}" data-type="${escapeHtml(type.key)}">${escapeHtml(type.label)}</button>`).join("");

  function renderArticles() {
    const filtered = contentArticles.filter((article) => currentType === "all" || article.category === currentType);
    list.innerHTML = filtered.length
      ? filtered.map((article) => `
        <article class="article-item">
          <span class="tag tag-guide">${escapeHtml(article.category)}</span>
          <h4>${escapeHtml(article.title)}</h4>
          <p>${escapeHtml(article.summary || "")}</p>
          <p>${escapeHtml(article.content || "")}</p>
          ${(article.sources && article.sources.length) ? `<div class="article-inline-sources">${article.sources.map((source) => `<a href="${escapeHtml(source.url)}" target="_blank" rel="noreferrer">${escapeHtml(source.title)}</a>`).join("")}</div>` : ""}
          <small>Autor: ${escapeHtml(article.author || "-")}</small>
        </article>
      `).join("")
      : "<p>No approved articles for this filter.</p>";
  }

  filters.querySelectorAll(".type-filter").forEach((btn) => {
    btn.addEventListener("click", () => {
      filters.querySelectorAll(".type-filter").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      currentType = btn.dataset.type;
      renderArticles();
    });
  });

  renderArticles();
}

async function fillGameSelect(selectId) {
  const select = document.getElementById(selectId);
  if (!select) return;
  const games = await api("/api/games");
  select.innerHTML = games.map((g) => `<option value="${escapeHtml(g.slug)}">${escapeHtml(g.title)}</option>`).join("");
}

async function renderSubmitPage(user) {
  const submitSection = document.getElementById("submitSection");
  if (!submitSection) return;
  const banner = document.getElementById("submitBanner");
  const rolePill = document.getElementById("submitRolePill");
  const roleDesc = document.getElementById("submitRoleDescription");
  const form = document.getElementById("articleForm");
  const feed = document.getElementById("userSubmissionFeed");
  const formMessage = document.getElementById("formMessage");

  rolePill.textContent = `Current role: ${user.role}`;
  roleDesc.textContent = user.role === "guest"
    ? "Guest nu poate trimite articole."
    : user.role === "admin"
    ? "Admin-ul publica direct (approved)."
    : "Articolele tale intra in pending pana la aprobare.";

  if (user.role === "guest") {
    banner.textContent = "Trebuie sa te loghezi ca user/admin pentru a trimite articole.";
    banner.classList.remove("hidden");
    submitSection.classList.add("hidden");
  } else {
    submitSection.classList.remove("hidden");
  }

  await fillGameSelect("game");

  form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = {
      title: document.getElementById("title").value.trim(),
      gameSlug: document.getElementById("game").value,
      category: document.getElementById("category").value,
      summary: document.getElementById("summary").value.trim(),
      content: document.getElementById("content").value.trim(),
      sourceTitle: document.getElementById("sourceTitle") ? document.getElementById("sourceTitle").value.trim() : "Submitted source",
      sourceUrl: document.getElementById("source").value.trim(),
    };
    try {
      const result = await api("/api/articles/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      formMessage.textContent = `Articol trimis cu succes. Status: ${result.status}`;
      formMessage.classList.remove("hidden");
      form.reset();
      await loadMySubmissions(feed);
    } catch (error) {
      formMessage.textContent = error.message;
      formMessage.classList.remove("hidden");
    }
  });

  await loadMySubmissions(feed);
}

async function loadMySubmissions(container) {
  if (!container) return;
  const items = await api("/api/articles/mine");
  container.innerHTML = items.length ? items.map((item) => `
    <article class="feed-item">
      <div><h4>${escapeHtml(item.title)}</h4><p>${escapeHtml(item.summary || "")}</p></div>
      <div class="feed-meta"><strong>${escapeHtml(item.game)}</strong><span>${escapeHtml(item.category)} | ${escapeHtml(item.status)}</span></div>
    </article>
  `).join("") : "<p>Nu ai articole trimise momentan.</p>";
}

async function renderAdminPage(user) {
  const adminRolePill = document.getElementById("adminRolePill");
  if (!adminRolePill) return;

  const accessBanner = document.getElementById("accessBanner");
  const mainGrid = document.querySelector(".admin-main-grid");
  const secondaryGrid = document.querySelector(".admin-secondary-grid");
  const moderationQueue = document.getElementById("moderationQueue");
  const articleManagementList = document.getElementById("articleManagementList");
  const articleManagementFilters = document.getElementById("articleManagementFilters");
  const articleGameSearch = document.getElementById("articleGameSearch");
  const articleGameSelect = document.getElementById("articleGameSelect");
  const dashboardMetrics = document.getElementById("dashboardMetrics");
  let currentManagementStatus = "all";
  let selectedGameSlug = "all";

  adminRolePill.textContent = `Current role: ${user.role}`;
  const adminRoleDescription = document.getElementById("adminRoleDescription");
  if (adminRoleDescription) {
    adminRoleDescription.textContent = user.role === "admin" ? "Admin mode active." : "Access restricted.";
  }

  if (user.role !== "admin") {
    accessBanner.textContent = "Acces interzis. Doar admin poate folosi acest dashboard.";
    accessBanner.classList.remove("hidden");
    mainGrid?.classList.add("hidden");
    secondaryGrid?.classList.add("hidden");
    return;
  }

  const summary = await api("/api/admin/summary");
  dashboardMetrics.innerHTML = `
    <div class="metric-card"><strong>${summary.games}</strong><span>Games</span></div>
    <div class="metric-card"><strong>${summary.approved}</strong><span>Approved</span></div>
    <div class="metric-card"><strong>${summary.pending}</strong><span>Pending</span></div>
    <div class="metric-card"><strong>${summary.users}</strong><span>Users</span></div>
  `;

  const games = await api("/api/games");
  if (articleGameSelect) {
    articleGameSelect.innerHTML = `<option value="all">All games</option>` + games.map((game) => `<option value="${escapeHtml(game.slug)}">${escapeHtml(game.title)}</option>`).join("");
    articleGameSelect.addEventListener("change", async () => {
      selectedGameSlug = articleGameSelect.value;
      await loadArticleManagement(articleManagementList, currentManagementStatus, selectedGameSlug, articleGameSearch?.value || "");
    });
  }

  articleGameSearch?.addEventListener("input", async () => {
    await loadArticleManagement(articleManagementList, currentManagementStatus, selectedGameSlug, articleGameSearch.value);
  });

  await fillGameSelect("game");

  const articleForm = document.getElementById("articleForm");
  const previewBtn = document.getElementById("previewBtn");
  const formMessage = document.getElementById("formMessage");

  previewBtn?.addEventListener("click", () => {
    document.getElementById("previewTitle").textContent = document.getElementById("title").value.trim() || "Article title will appear here";
    document.getElementById("previewGame").textContent = document.getElementById("game").selectedOptions[0]?.textContent || "Selected game";
    document.getElementById("previewSummary").textContent = document.getElementById("summary").value.trim() || "Summary preview will appear here.";
    document.getElementById("previewCategory").textContent = document.getElementById("category").value || "Type";
  });

  articleForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const result = await api("/api/articles/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: document.getElementById("title").value.trim(),
          gameSlug: document.getElementById("game").value,
          category: document.getElementById("category").value,
          summary: document.getElementById("summary").value.trim(),
          content: document.getElementById("content").value.trim(),
          sourceTitle: document.getElementById("sourceTitle") ? document.getElementById("sourceTitle").value.trim() : "Admin source",
          sourceUrl: document.getElementById("source").value.trim(),
        }),
      });
      formMessage.textContent = `Published successfully. Status: ${result.status}`;
      formMessage.classList.remove("hidden");
      articleForm.reset();
      await loadPending(moderationQueue);
      await loadArticleManagement(articleManagementList, currentManagementStatus, selectedGameSlug, articleGameSearch?.value || "");
    } catch (error) {
      formMessage.textContent = error.message;
      formMessage.classList.remove("hidden");
    }
  });

  const gameForm = document.getElementById("gameForm");
  const gameFormMessage = document.getElementById("gameFormMessage");
  gameForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const slugRaw = document.getElementById("gameSlug").value.trim().toLowerCase();
    if (!/^[a-z0-9-]+$/.test(slugRaw)) {
      if (gameFormMessage) {
        gameFormMessage.textContent = "Slug must contain only lowercase letters, numbers and dashes.";
        gameFormMessage.classList.remove("hidden");
      }
      return;
    }
    const yearRaw = Number(document.getElementById("gameYear")?.value || 2026);
    if (!Number.isInteger(yearRaw) || yearRaw < 1970 || yearRaw > 2100) {
      if (gameFormMessage) {
        gameFormMessage.textContent = "Release year must be an integer between 1970 and 2100.";
        gameFormMessage.classList.remove("hidden");
      }
      return;
    }
    const shortDesc = document.getElementById("gameShortDesc")?.value.trim() || "";
    const longDesc = document.getElementById("gameLongDesc")?.value.trim() || "";
    const payload = {
      title: document.getElementById("gameName").value.trim(),
      slug: slugRaw,
      genre: document.getElementById("gameGenre").value.trim(),
      difficulty: document.getElementById("gameDifficulty").value.trim(),
      description: [shortDesc, longDesc].filter(Boolean).join("\n\n"),
      image_url: document.getElementById("gameImage").value.trim(),
      platforms: (document.getElementById("gamePlatforms")?.value || "").trim(),
      studio: (document.getElementById("gameStudio")?.value || "Independent Studio").trim(),
      release_year: yearRaw,
      official_url: (document.getElementById("gameOfficialUrl")?.value || "#").trim(),
    };
    try {
      await api("/api/games", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (gameFormMessage) {
        gameFormMessage.textContent = "Game added successfully.";
        gameFormMessage.classList.remove("hidden");
      }
      gameForm.reset();
    } catch (error) {
      if (gameFormMessage) {
        gameFormMessage.textContent = error.message;
        gameFormMessage.classList.remove("hidden");
      }
    }
  });

  articleManagementFilters?.querySelectorAll(".type-filter").forEach((button) => {
    button.addEventListener("click", async () => {
      articleManagementFilters.querySelectorAll(".type-filter").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      currentManagementStatus = button.dataset.status;
      await loadArticleManagement(articleManagementList, currentManagementStatus, selectedGameSlug, articleGameSearch?.value || "");
    });
  });

  await loadPending(moderationQueue);
  await loadArticleManagement(articleManagementList, currentManagementStatus, selectedGameSlug, articleGameSearch?.value || "");
}

async function renderArticleManagementPage(user) {
  const gameCards = document.getElementById("adminGameList");
  if (!gameCards) return;

  const rolePill = document.getElementById("adminRolePill");
  const accessBanner = document.getElementById("accessBanner");
  const dashboardMetrics = document.getElementById("dashboardMetrics");
  const modal = document.getElementById("articleModal");
  const modalTitle = document.getElementById("articleModalTitle");
  const modalList = document.getElementById("modalArticleList");
  const modalSearch = document.getElementById("modalArticleSearch");
  const modalStatus = document.getElementById("modalArticleStatus");
  const closeModal = document.getElementById("closeArticleModal");

  let currentStatus = "all";
  let currentGameSlug = "";

  if (rolePill) rolePill.textContent = `Current role: ${user.role}`;

  if (user.role !== "admin") {
    if (accessBanner) {
      accessBanner.textContent = "Acces interzis. Doar admin poate folosi acest workspace.";
      accessBanner.classList.remove("hidden");
    }
    return;
  }

  const summary = await api("/api/admin/summary");
  if (dashboardMetrics) {
    dashboardMetrics.innerHTML = `
      <div class="metric-card"><strong>${summary.games}</strong><span>Games</span></div>
      <div class="metric-card"><strong>${summary.approved}</strong><span>Approved</span></div>
      <div class="metric-card"><strong>${summary.pending}</strong><span>Pending</span></div>
      <div class="metric-card"><strong>${summary.users}</strong><span>Users</span></div>
    `;
  }

  const games = await api("/api/games");

  async function refreshModalList() {
    if (!currentGameSlug || !modalList) return;
    await loadArticleManagement(modalList, currentStatus, currentGameSlug, modalSearch?.value || "");
  }

  function openModalForGame(slug, title) {
    currentGameSlug = slug;
    currentStatus = "all";
    if (modalStatus) modalStatus.value = "all";
    if (modalSearch) modalSearch.value = "";
    if (modalTitle) modalTitle.textContent = `Articles - ${title}`;
    modal?.classList.remove("hidden");
    modal?.setAttribute("aria-hidden", "false");
    refreshModalList();
  }

  function closeModalPanel() {
    modal?.classList.add("hidden");
    modal?.setAttribute("aria-hidden", "true");
    currentGameSlug = "";
  }

  closeModal?.addEventListener("click", closeModalPanel);
  modal?.addEventListener("click", (event) => {
    if (event.target === modal) closeModalPanel();
  });

  modalSearch?.addEventListener("input", async () => {
    await refreshModalList();
  });

  modalStatus?.addEventListener("change", async () => {
    currentStatus = modalStatus.value;
    await refreshModalList();
  });

  if (gameCards) {
    gameCards.innerHTML = games.map((game) => `
      <article class="admin-game-card">
        <div>
          <h4>${escapeHtml(game.title)}</h4>
          <p>${escapeHtml(game.genre || "General")} | ${escapeHtml(game.difficulty || "-")}</p>
          <span class="likes">${game.approved_articles || 0} articles</span>
        </div>
        <button type="button" class="primary-btn small-btn open-game-articles-btn" data-slug="${escapeHtml(game.slug)}" data-title="${escapeHtml(game.title)}">
          Vezi articolele
        </button>
      </article>
    `).join("");

    gameCards.querySelectorAll(".open-game-articles-btn").forEach((button) => {
      button.addEventListener("click", () => {
        openModalForGame(button.dataset.slug, button.dataset.title);
      });
    });
  }
}

async function loadPending(container) {
  if (!container) return;
  const items = await api("/api/articles/pending");
  container.innerHTML = items.length ? items.map((item) => `
    <article class="moderation-card" data-id="${item.id}">
      <h4>${escapeHtml(item.title)}</h4>
      <p>${escapeHtml(item.summary || "")}</p>
      <p>${escapeHtml(item.game)} | ${escapeHtml(item.category)} | ${escapeHtml(item.author)}</p>
      <div class="queue-actions">
        <button type="button" class="primary-btn small-btn approve-btn">Approve</button>
        <button type="button" class="secondary-btn small-btn reject-btn">Reject</button>
      </div>
    </article>
  `).join("") : "<p>No pending submissions right now.</p>";

  container.querySelectorAll(".approve-btn").forEach((button) => {
    button.addEventListener("click", async () => {
      const id = button.closest(".moderation-card").dataset.id;
      await api(`/api/articles/${id}/approve`, { method: "PUT" });
      await loadPending(container);
      const managementContainer = document.getElementById("articleManagementList");
      if (managementContainer) await loadArticleManagement(managementContainer, "all", "all", "");
    });
  });
  container.querySelectorAll(".reject-btn").forEach((button) => {
    button.addEventListener("click", async () => {
      const id = button.closest(".moderation-card").dataset.id;
      await api(`/api/articles/${id}/reject`, { method: "PUT" });
      await loadPending(container);
      const managementContainer = document.getElementById("articleManagementList");
      if (managementContainer) await loadArticleManagement(managementContainer, "all", "all", "");
    });
  });
}

async function loadArticleManagement(container, status = "all", gameSlug = "all", search = "") {
  if (!container) return;
  container.innerHTML = "<p>Loading articles...</p>";
  const params = new URLSearchParams();
  if (status !== "all") params.set("status", status);
  if (gameSlug !== "all") params.set("game", gameSlug);
  if ((search || "").trim()) params.set("q", search.trim());
  params.set("limit", "100");
  const suffix = params.toString() ? `?${params.toString()}` : "";
  const items = await api(`/api/articles/admin${suffix}`);

  container.innerHTML = items.length ? items.map((item) => `
    <article class="moderation-card" data-id="${item.id}">
      <input class="edit-title" type="text" value="${escapeHtml(item.title)}" />
      <p>${escapeHtml(item.game)} | ${escapeHtml(item.category)} | ${escapeHtml(item.status)} | ${escapeHtml(item.author)}</p>
      <textarea class="edit-summary" rows="2" placeholder="Edit summary">${escapeHtml(item.summary || "")}</textarea>
      <textarea class="edit-content" rows="4" placeholder="Edit content">${escapeHtml(item.content || "")}</textarea>
      <div class="queue-actions">
        <button type="button" class="primary-btn small-btn save-edit-btn">Save</button>
        <button type="button" class="secondary-btn small-btn delete-article-btn">Delete</button>
      </div>
    </article>
  `).join("") : "<p>Nu exista articole pentru filtrul selectat.</p>";

  container.querySelectorAll(".save-edit-btn").forEach((button) => {
    button.addEventListener("click", async () => {
      const card = button.closest(".moderation-card");
      const id = card.dataset.id;
      await api(`/api/articles/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: card.querySelector(".edit-title").value.trim(),
          summary: card.querySelector(".edit-summary").value.trim(),
          content: card.querySelector(".edit-content").value.trim(),
        }),
      });
      await loadArticleManagement(container, status, gameSlug, search);
    });
  });
  container.querySelectorAll(".delete-article-btn").forEach((button) => {
    button.addEventListener("click", async () => {
      const id = button.closest(".moderation-card").dataset.id;
      await api(`/api/articles/${id}`, { method: "DELETE" });
      await loadArticleManagement(container, status, gameSlug, search);
    });
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  try {
    initBackToTopButton();
    const user = await refreshSessionUI();
    initLoginModal();
    initRegisterForm();
    await renderHomePage();
    await renderGamePage(user);
    await renderSubmitPage(user);
    await renderAdminPage(user);
    await renderArticleManagementPage(user);
  } catch (error) {
    console.error(error);
  }
});
