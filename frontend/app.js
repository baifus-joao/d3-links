const state = {
  links: [],
  overview: null,
  selectedLinkId: null,
  searchTerm: "",
};

const refs = {
  searchInput: document.querySelector("#search-input"),
  filtersForm: document.querySelector("#filters-form"),
  filterStart: document.querySelector("#filter-start"),
  filterEnd: document.querySelector("#filter-end"),
  periodFeedback: document.querySelector("#period-feedback"),
  heroPeriodText: document.querySelector("#hero-period-text"),
  heroTopLink: document.querySelector("#hero-top-link"),
  heroTopSource: document.querySelector("#hero-top-source"),
  heroRangeLabel: document.querySelector("#hero-range-label"),
  metricPeriodClicks: document.querySelector("#metric-period-clicks"),
  metricPeriodChange: document.querySelector("#metric-period-change"),
  metricActiveLinks: document.querySelector("#metric-active-links"),
  metricTotalLinks: document.querySelector("#metric-total-links"),
  metricTopLink: document.querySelector("#metric-top-link"),
  metricTopLinkClicks: document.querySelector("#metric-top-link-clicks"),
  metricTopSource: document.querySelector("#metric-top-source"),
  metricTopSourceClicks: document.querySelector("#metric-top-source-clicks"),
  overviewTrend: document.querySelector("#overview-trend"),
  overviewSources: document.querySelector("#overview-sources"),
  overviewRanking: document.querySelector("#overview-ranking"),
  overviewRecent: document.querySelector("#overview-recent"),
  detailTitle: document.querySelector("#detail-title"),
  detailEmpty: document.querySelector("#detail-empty"),
  detailContent: document.querySelector("#detail-content"),
  detailTotalClicks: document.querySelector("#detail-total-clicks"),
  detailMobileClicks: document.querySelector("#detail-mobile-clicks"),
  detailDesktopClicks: document.querySelector("#detail-desktop-clicks"),
  detailDays: document.querySelector("#detail-days"),
  detailSources: document.querySelector("#detail-sources"),
  detailRecent: document.querySelector("#detail-recent"),
  openLink: document.querySelector("#open-link"),
  exportLink: document.querySelector("#export-link"),
  qrPreview: document.querySelector("#qr-preview"),
  linksList: document.querySelector("#links-list"),
  linkForm: document.querySelector("#link-form"),
  formFeedback: document.querySelector("#form-feedback"),
};

function slugifyShortCode(value) {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim()
    .toLowerCase()
    .replace(/[\s/]+/g, "-")
    .replace(/[^a-z0-9_-]+/g, "-")
    .replace(/-{2,}/g, "-")
    .replace(/^[-_]+|[-_]+$/g, "");
}

function initDefaultPeriod() {
  const today = new Date();
  const start = new Date(today);
  start.setDate(today.getDate() - 29);
  refs.filterStart.value = toInputDate(start);
  refs.filterEnd.value = toInputDate(today);
  highlightQuickRange(30);
}

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(path, { ...options, headers });

  if (!response.ok) {
    let detail = "Falha ao processar a requisicao.";
    try {
      const payload = await response.json();
      detail = formatApiDetail(payload.detail) || detail;
    } catch (error) {
      detail = response.statusText || detail;
    }
    throw new Error(detail);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

function formatApiDetail(detail) {
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const loc = Array.isArray(item.loc) ? item.loc.filter((part) => part !== "body").join(".") : "";
        return loc ? `${loc}: ${item.msg}` : item.msg;
      })
      .join(" | ");
  }

  if (typeof detail === "object" && detail !== null) {
    return detail.message || JSON.stringify(detail);
  }

  return String(detail || "");
}

function toInputDate(value) {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, "0");
  const day = String(value.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function parseDateOnly(value) {
  return new Date(`${value}T00:00:00`);
}

function formatDateTime(value) {
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

function formatDateOnly(value) {
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(parseDateOnly(value));
}

function formatShortDate(value) {
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "2-digit",
  }).format(parseDateOnly(value));
}

function formatNumber(value) {
  return new Intl.NumberFormat("pt-BR").format(value || 0);
}

function formatRangeLabel(startDate, endDate) {
  if (!startDate || !endDate) {
    return "Historico completo";
  }
  return `${formatDateOnly(startDate)} a ${formatDateOnly(endDate)}`;
}

function formatChange(value) {
  if (value === null || value === undefined) {
    return "Sem base comparativa para o periodo.";
  }
  const prefix = value > 0 ? "+" : "";
  return `${prefix}${value}% vs periodo anterior`;
}

function buildQueryString(extra = {}) {
  const params = new URLSearchParams();

  if (refs.filterStart.value) {
    params.set("start_date", refs.filterStart.value);
  }
  if (refs.filterEnd.value) {
    params.set("end_date", refs.filterEnd.value);
  }

  for (const [key, value] of Object.entries(extra)) {
    if (value !== undefined && value !== null && value !== "") {
      params.set(key, String(value));
    }
  }

  const query = params.toString();
  return query ? `?${query}` : "";
}

function highlightQuickRange(days) {
  document.querySelectorAll("[data-range-days]").forEach((button) => {
    button.classList.toggle("is-active", Number(button.dataset.rangeDays) === days);
  });
}

function setFeedback(message, type = "") {
  refs.formFeedback.textContent = message;
  refs.formFeedback.className = "feedback";
  if (type) {
    refs.formFeedback.classList.add(`feedback--${type}`);
  }
}

function getFilteredLinks() {
  const term = state.searchTerm.trim().toLowerCase();
  const sorted = [...state.links].sort((left, right) => {
    if (right.total_clicks !== left.total_clicks) {
      return right.total_clicks - left.total_clicks;
    }
    return left.short_code.localeCompare(right.short_code);
  });

  if (!term) {
    return sorted;
  }

  return sorted.filter((link) => {
    const haystack = [link.short_code, link.description || "", ...(link.tags || [])].join(" ").toLowerCase();
    return haystack.includes(term);
  });
}

function renderTrendChart(container, items) {
  if (!items.length) {
    container.innerHTML = `<div class="empty-state">Sem acessos no periodo selecionado.</div>`;
    return;
  }

  const visible = items.length > 14 ? items.slice(-14) : items;
  const max = Math.max(...visible.map((item) => item.clicks), 1);

  container.innerHTML = `
    <div class="trend-chart">
      ${visible
        .map(
          (item) => `
            <div class="trend-chart__item">
              <span class="trend-chart__value">${formatNumber(item.clicks)}</span>
              <div class="trend-chart__track">
                <div class="trend-chart__fill" style="height: ${Math.max(10, (item.clicks / max) * 100)}%"></div>
              </div>
              <small>${formatShortDate(item.date)}</small>
            </div>
          `,
        )
        .join("")}
    </div>
  `;
}

function renderDistribution(container, items, emptyMessage) {
  if (!items.length) {
    container.innerHTML = `<div class="empty-state">${emptyMessage}</div>`;
    return;
  }

  const max = Math.max(...items.map((item) => item.clicks), 1);
  container.innerHTML = items
    .map(
      (item) => `
        <div class="distribution-row">
          <div class="distribution-row__top">
            <strong>${item.label}</strong>
            <span class="distribution-list__meta">${formatNumber(item.clicks)} cliques</span>
          </div>
          <div class="distribution-row__track">
            <div class="distribution-row__fill" style="width: ${(item.clicks / max) * 100}%"></div>
          </div>
        </div>
      `,
    )
    .join("");
}

function renderRecentList(container, items, emptyMessage) {
  if (!items.length) {
    container.innerHTML = `<div class="empty-state">${emptyMessage}</div>`;
    return;
  }

  container.innerHTML = items
    .map(
      (item) => `
        <article class="recent-item">
          <div class="recent-item__meta">
            <span class="link-chip mono">/${item.short_code || "-"}</span>
            <span>${item.source}</span>
            <span>${item.device_type}</span>
            <span>${item.country || "pais n/d"}</span>
          </div>
          <strong>${formatDateTime(item.timestamp)}</strong>
          <div class="recent-item__meta">
            <span>${item.referer || "acesso direto"}</span>
            <span>IP ${item.ip}</span>
          </div>
        </article>
      `,
    )
    .join("");
}

function renderOverview() {
  const overview = state.overview;
  if (!overview) {
    return;
  }

  const summary = overview.summary;
  refs.heroTopLink.textContent = summary.top_link_short_code ? `/${summary.top_link_short_code}` : "Sem lider";
  refs.heroTopSource.textContent = summary.top_source || "Sem canal";
  refs.heroRangeLabel.textContent = formatRangeLabel(summary.start_date, summary.end_date);
  refs.heroPeriodText.textContent = `${formatNumber(summary.period_clicks)} acessos observados em ${formatNumber(summary.active_links)} origens ativas dentro de ${formatRangeLabel(summary.start_date, summary.end_date)}.`;

  refs.metricPeriodClicks.textContent = formatNumber(summary.period_clicks);
  refs.metricPeriodChange.textContent = formatChange(summary.period_change_percent);
  refs.metricActiveLinks.textContent = formatNumber(summary.active_links);
  refs.metricTotalLinks.textContent = `${formatNumber(summary.total_links)} links cadastrados`;
  refs.metricTopLink.textContent = summary.top_link_short_code ? `/${summary.top_link_short_code}` : "-";
  refs.metricTopLinkClicks.textContent = `${formatNumber(summary.top_link_clicks)} cliques`;
  refs.metricTopSource.textContent = summary.top_source || "-";
  refs.metricTopSourceClicks.textContent = `${formatNumber(summary.top_source_clicks)} cliques`;
  refs.periodFeedback.textContent = `Leitura carregada para ${formatRangeLabel(summary.start_date, summary.end_date)}.`;

  renderTrendChart(refs.overviewTrend, overview.clicks_by_day);
  renderDistribution(refs.overviewSources, overview.clicks_by_source, "Nenhuma origem registrada no periodo.");
  renderRecentList(refs.overviewRecent, overview.recent_clicks, "Ainda nao ha acessos recentes para mostrar.");

  if (!overview.top_links.length) {
    refs.overviewRanking.innerHTML = `<div class="empty-state">Nenhuma origem cadastrada ainda.</div>`;
    return;
  }

  refs.overviewRanking.innerHTML = overview.top_links
    .map(
      (item, index) => `
        <button class="ranking-row" type="button" data-link-id="${item.id}">
          <div class="ranking-row__top">
            <div class="ranking-row__label">
              <span class="ranking-row__rank">#${index + 1} /${item.short_code}</span>
              <strong>${item.description || "Origem sem descricao"}</strong>
            </div>
            <span class="ranking-row__share">${item.share_percent}% do periodo</span>
          </div>
          <div class="ranking-row__meta">
            <span>${formatNumber(item.period_clicks)} cliques no periodo</span>
            <span>${formatNumber(item.total_clicks)} cliques no historico</span>
            <span>${item.last_click_at ? formatDateTime(item.last_click_at) : "sem clique recente"}</span>
          </div>
        </button>
      `,
    )
    .join("");
}

function renderLinks() {
  const links = getFilteredLinks();
  if (!links.length) {
    refs.linksList.innerHTML = `<div class="empty-state">Nenhum link encontrado para a busca atual.</div>`;
    return;
  }

  refs.linksList.innerHTML = links
    .map(
      (link) => `
        <article class="link-card ${link.id === state.selectedLinkId ? "is-selected" : ""}" data-link-id="${link.id}">
          <div class="link-card__top">
            <div class="link-card__title">
              <strong>/${link.short_code}</strong>
              <span class="ranking-row__meta">${formatNumber(link.total_clicks)} cliques totais</span>
            </div>
            <span class="link-chip mono">${new URL(link.original_url).hostname}</span>
          </div>
          <p class="link-card__description">${link.description || "Sem descricao operacional."}</p>
          <div class="link-card__tags">
            ${(link.tags || []).map((tag) => `<span class="tag">${tag}</span>`).join("")}
          </div>
          <div class="link-card__footer">
            <span class="mono">${link.short_url}</span>
            <div class="link-card__actions">
              <button class="mini-button" type="button" data-action="copy" data-value="${link.short_url}">Copiar</button>
              <a class="mini-button" href="${link.short_url}" target="_blank" rel="noreferrer">Abrir</a>
            </div>
          </div>
        </article>
      `,
    )
    .join("");
}

async function copyToClipboard(value) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(value);
    return;
  }

  const helper = document.createElement("textarea");
  helper.value = value;
  helper.setAttribute("readonly", "");
  helper.style.position = "absolute";
  helper.style.left = "-9999px";
  document.body.appendChild(helper);
  helper.select();
  document.execCommand("copy");
  document.body.removeChild(helper);
}

async function loadDashboard() {
  const [links, overview] = await Promise.all([
    api("/links"),
    api(`/analytics/overview${buildQueryString({ top_n: 6 })}`),
  ]);

  state.links = links;
  state.overview = overview;

  if (!state.selectedLinkId) {
    state.selectedLinkId = overview.summary.top_link_id || links[0]?.id || null;
  } else if (!links.some((link) => link.id === state.selectedLinkId)) {
    state.selectedLinkId = overview.summary.top_link_id || links[0]?.id || null;
  }

  renderOverview();
  renderLinks();
  await loadLinkDetail();
}

async function loadLinkDetail() {
  if (!state.selectedLinkId) {
    refs.detailEmpty.classList.remove("hidden");
    refs.detailContent.classList.add("hidden");
    refs.detailTitle.textContent = "Selecione uma origem";
    refs.openLink.href = "#";
    refs.exportLink.href = "#";
    return;
  }

  const stats = await api(`/links/${state.selectedLinkId}/stats${buildQueryString()}`);
  const mobile = stats.clicks_by_device.find((item) => item.label === "mobile")?.clicks || 0;
  const desktop = stats.clicks_by_device.find((item) => item.label === "desktop")?.clicks || 0;

  refs.detailEmpty.classList.add("hidden");
  refs.detailContent.classList.remove("hidden");
  refs.detailTitle.textContent = `/${stats.link.short_code}`;
  refs.openLink.href = stats.link.short_url;
  refs.exportLink.href = `/links/${stats.link.id}/clicks/export${buildQueryString()}`;
  refs.qrPreview.src = `/links/${stats.link.id}/qr-code`;
  refs.detailTotalClicks.textContent = formatNumber(stats.total_clicks);
  refs.detailMobileClicks.textContent = formatNumber(mobile);
  refs.detailDesktopClicks.textContent = formatNumber(desktop);

  renderTrendChart(refs.detailDays, stats.clicks_by_day);
  renderDistribution(refs.detailSources, stats.clicks_by_source, "Sem distribuicao de origem para esta unidade.");
  renderRecentList(
    refs.detailRecent,
    stats.recent_clicks.map((item) => ({ ...item, short_code: stats.link.short_code })),
    "Nenhum acesso recente para esta origem.",
  );
}

function setQuickRange(days) {
  const end = new Date();
  const start = new Date(end);
  start.setDate(end.getDate() - (days - 1));
  refs.filterStart.value = toInputDate(start);
  refs.filterEnd.value = toInputDate(end);
  highlightQuickRange(days);
}

document.querySelectorAll("[data-range-days]").forEach((button) => {
  button.addEventListener("click", async () => {
    setQuickRange(Number(button.dataset.rangeDays));
    await loadDashboard().catch((error) => {
      refs.periodFeedback.textContent = error.message;
    });
  });
});

document.querySelectorAll("[data-scroll-target]").forEach((button) => {
  button.addEventListener("click", () => {
    const target = document.getElementById(button.dataset.scrollTarget);
    document.querySelectorAll("[data-scroll-target]").forEach((item) => item.classList.remove("is-active"));
    button.classList.add("is-active");
    target?.scrollIntoView({ behavior: "smooth", block: "start" });
  });
});

refs.searchInput.addEventListener("input", () => {
  state.searchTerm = refs.searchInput.value;
  renderLinks();
});

refs.filtersForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  await loadDashboard().catch((error) => {
    refs.periodFeedback.textContent = error.message;
  });
});

refs.overviewRanking.addEventListener("click", async (event) => {
  const target = event.target.closest("[data-link-id]");
  if (!target) {
    return;
  }

  state.selectedLinkId = target.dataset.linkId;
  renderLinks();
  await loadLinkDetail();
});

refs.linksList.addEventListener("click", async (event) => {
  const copyButton = event.target.closest("[data-action='copy']");
  if (copyButton) {
    event.stopPropagation();
    await copyToClipboard(copyButton.dataset.value);
    setFeedback("Link copiado para a area de transferencia.", "success");
    return;
  }

  const target = event.target.closest("[data-link-id]");
  if (!target) {
    return;
  }

  state.selectedLinkId = target.dataset.linkId;
  renderLinks();
  await loadLinkDetail();
});

refs.linkForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData(refs.linkForm);
  const normalizedShortCode = slugifyShortCode(String(formData.get("short_code") || ""));
  refs.linkForm.elements.namedItem("short_code").value = normalizedShortCode;
  const payload = {
    original_url: formData.get("original_url"),
    short_code: normalizedShortCode,
    description: formData.get("description") || null,
    tags: String(formData.get("tags") || "")
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean),
  };

  try {
    setFeedback("Cadastrando origem...");
    const created = await api("/links", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    state.selectedLinkId = created.id;
    refs.linkForm.reset();
    setFeedback("Origem cadastrada com sucesso.", "success");
    await loadDashboard();
  } catch (error) {
    setFeedback(error.message, "error");
  }
});

initDefaultPeriod();

loadDashboard().catch((error) => {
  refs.periodFeedback.textContent = error.message;
  setFeedback(error.message, "error");
});
