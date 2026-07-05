const STORAGE_KEY = "sgodai.market-radar.config.v2";

const sectorCatalog = [
  {
    id: "ai_compute",
    name: "AI算力",
    horizon: "long",
    level: "high",
    impact: 82,
    trend: 76,
    sentiment: 64,
    risk: 48,
    driver: "海外云厂商资本开支与国产算力链订单改善",
    risks: "估值拥挤、出口限制、供给瓶颈",
    indicators: ["资本开支", "服务器订单", "GPU供给"],
  },
  {
    id: "hbm",
    name: "HBM",
    horizon: "medium",
    level: "high",
    impact: 78,
    trend: 72,
    sentiment: 61,
    risk: 52,
    driver: "AI服务器需求拉动高带宽存储供给紧张",
    risks: "扩产节奏、客户集中度",
    indicators: ["HBM价格", "先进封装产能", "海外龙头指引"],
  },
  {
    id: "memory",
    name: "存储芯片",
    horizon: "medium",
    level: "high",
    impact: 74,
    trend: 68,
    sentiment: 58,
    risk: 45,
    driver: "价格周期改善与下游提前锁单",
    risks: "库存回补后需求放缓",
    indicators: ["DRAM价格", "NAND价格", "库存天数"],
  },
  {
    id: "semi_equipment",
    name: "半导体设备",
    horizon: "long",
    level: "high",
    impact: 73,
    trend: 66,
    sentiment: 57,
    risk: 50,
    driver: "国产替代与先进制程设备验证推进",
    risks: "订单兑现、出口管制、研发投入压力",
    indicators: ["设备订单", "晶圆厂资本开支", "国产化率"],
  },
  {
    id: "biotech",
    name: "创新药",
    horizon: "long",
    level: "medium",
    impact: 67,
    trend: 59,
    sentiment: 55,
    risk: 62,
    driver: "临床读出与BD交易活跃",
    risks: "研发失败、医保与监管不确定性",
    indicators: ["临床数据", "授权交易", "融资环境"],
  },
  {
    id: "low_altitude",
    name: "低空经济",
    horizon: "short",
    level: "medium",
    impact: 61,
    trend: 57,
    sentiment: 60,
    risk: 54,
    driver: "地方政策和试点场景密集落地",
    risks: "商业模式验证不足",
    indicators: ["地方政策", "订单公告", "空域改革"],
  },
  {
    id: "storage",
    name: "储能",
    horizon: "medium",
    level: "medium",
    impact: 58,
    trend: 46,
    sentiment: 48,
    risk: 63,
    driver: "价格竞争后等待盈利结构修复",
    risks: "价格竞争、海外政策变化、产能利用率",
    indicators: ["电芯价格", "海外订单", "利用小时"],
  },
  {
    id: "copper",
    name: "铜",
    horizon: "medium",
    level: "medium",
    impact: 69,
    trend: 63,
    sentiment: 52,
    risk: 58,
    driver: "电网与AI数据中心带动需求预期",
    risks: "全球经济波动、库存变化",
    indicators: ["LME库存", "现货升贴水", "矿端扰动"],
  },
];

const assetCatalog = [
  {
    ticker: "688525.SH",
    name: "佰维存储",
    market: "A-share",
    sector: "存储芯片",
    state: "右侧增持观察",
    impact: 76,
    trend: 71,
    risk: 49,
    evidence: "evt_001, sig_001",
    events: [
      ["09:18", "存储价格继续上行"],
      ["10:45", "下游客户锁单线索"],
      ["14:20", "行业评分上调"],
    ],
  },
  {
    ticker: "603986.SH",
    name: "兆易创新",
    market: "A-share",
    sector: "存储芯片",
    state: "观察",
    impact: 64,
    trend: 58,
    risk: 43,
    evidence: "evt_002, sig_002",
    events: [
      ["09:36", "价格周期改善"],
      ["11:10", "海外映射偏正面"],
    ],
  },
  {
    ticker: "NVDA.US",
    name: "NVIDIA",
    market: "US",
    sector: "AI算力",
    state: "持有跟踪",
    impact: 83,
    trend: 79,
    risk: 51,
    evidence: "evt_003, sig_003",
    events: [
      ["08:30", "资本开支指引上修"],
      ["13:10", "供应链节点同步走强"],
    ],
  },
  {
    ticker: "TSM.US",
    name: "台积电",
    market: "US",
    sector: "半导体设备",
    state: "观察",
    impact: 72,
    trend: 65,
    risk: 47,
    evidence: "evt_006, sig_006",
    events: [
      ["09:12", "先进制程需求稳定"],
      ["13:40", "设备链映射偏正面"],
    ],
  },
  {
    ticker: "300750.SZ",
    name: "宁德时代",
    market: "A-share",
    sector: "储能",
    state: "减持观察",
    impact: 55,
    trend: 38,
    risk: 63,
    evidence: "evt_004, sig_004",
    events: [
      ["10:05", "价格竞争压力"],
      ["13:55", "风险评分上升"],
    ],
  },
  {
    ticker: "2269.HK",
    name: "药明生物",
    market: "HK",
    sector: "创新药",
    state: "风险预警",
    impact: 61,
    trend: 44,
    risk: 72,
    evidence: "evt_007, sig_007",
    events: [
      ["10:20", "监管不确定性上升"],
      ["14:10", "风险评分触发阈值"],
    ],
  },
];

const defaultConfig = {
  sectorIds: ["ai_compute", "hbm", "memory", "biotech", "low_altitude", "copper"],
  assetTickers: ["688525.SH", "603986.SH", "NVDA.US", "300750.SZ"],
  customSectors: [],
  customAssets: [],
  emailTargets: [
    {
      id: "email_001",
      name: "Main Inbox",
      address: "user@example.com",
      enabled: true,
      reportTypes: ["pre_market", "post_market", "weekly", "major_alert", "risk_alert"],
      sectors: ["AI算力", "存储芯片"],
      tickers: ["688525.SH", "603986.SH"],
      impactThreshold: 70,
      riskThreshold: 60,
    },
    {
      id: "email_002",
      name: "Risk Only",
      address: "risk@example.com",
      enabled: false,
      reportTypes: ["major_alert", "risk_alert", "position_window_change"],
      sectors: [],
      tickers: [],
      impactThreshold: 80,
      riskThreshold: 65,
    },
  ],
  llm: {
    defaultProvider: "openai_compatible",
    providers: [
      {
        id: "openai_compatible",
        name: "OpenAI Compatible",
        enabled: true,
        baseUrl: "https://api.openai.com/v1",
        model: "gpt-4.1",
        apiKeyEnv: "OPENAI_API_KEY",
      },
      {
        id: "local_ollama",
        name: "Ollama",
        enabled: false,
        baseUrl: "http://127.0.0.1:11434",
        model: "qwen2.5:14b",
        apiKeyEnv: "",
      },
      {
        id: "local_vllm",
        name: "vLLM",
        enabled: false,
        baseUrl: "http://127.0.0.1:8000/v1",
        model: "local-finance-model",
        apiKeyEnv: "",
      },
    ],
  },
  providers: [
    {
      id: "market_data",
      name: "MarketDataProvider",
      type: "akshare",
      enabled: false,
      cadence: "15 min",
      endpoint: "adapter://akshare",
    },
    {
      id: "announcement",
      name: "AnnouncementProvider",
      type: "exchange_adapter",
      enabled: false,
      cadence: "30 min",
      endpoint: "adapter://exchange",
    },
    {
      id: "news",
      name: "NewsProvider",
      type: "rss",
      enabled: true,
      cadence: "10 min",
      endpoint: "configs/sources.yaml",
    },
    {
      id: "policy",
      name: "PolicyProvider",
      type: "policy_rss",
      enabled: false,
      cadence: "60 min",
      endpoint: "configs/sources.yaml",
    },
  ],
};

let appConfig = loadConfig();
let currentData = buildData();
let toastTimer = null;

const uiState = {
  activeView: "dashboard",
  activeHorizon: "all",
  query: "",
  configTab: "sectors",
  graphFocus: appConfig.sectorIds[0] || "ai_compute",
  graphDepth: 2,
};

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function esc(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function normalize(value) {
  return String(value || "").trim().toLowerCase();
}

function slug(value) {
  return normalize(value)
    .replace(/[^a-z0-9\u4e00-\u9fa5]+/gi, "_")
    .replace(/^_+|_+$/g, "")
    .slice(0, 32);
}

function loadConfig() {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (!stored) return clone(defaultConfig);
  try {
    const parsed = JSON.parse(stored);
    return {
      ...clone(defaultConfig),
      ...parsed,
      llm: { ...clone(defaultConfig.llm), ...(parsed.llm || {}) },
      providers: parsed.providers || clone(defaultConfig.providers),
      emailTargets: parsed.emailTargets || clone(defaultConfig.emailTargets),
      customSectors: parsed.customSectors || [],
      customAssets: parsed.customAssets || [],
    };
  } catch {
    return clone(defaultConfig);
  }
}

function persistConfig(message = "已保存") {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(appConfig));
  currentData = buildData();
  renderAll();
  flashSaveState();
  showToast(message);
}

function flashSaveState() {
  const target = document.querySelector("#saveState");
  if (!target) return;
  target.textContent = "Saved";
  setTimeout(() => {
    target.textContent = "LocalStorage";
  }, 1200);
}

function buildData() {
  const sectors = [...sectorCatalog, ...appConfig.customSectors].filter((sector) =>
    appConfig.sectorIds.includes(sector.id),
  );
  const assets = [...assetCatalog, ...appConfig.customAssets].filter((asset) =>
    appConfig.assetTickers.includes(asset.ticker),
  );
  return {
    sectors,
    assets,
    alerts: buildAlerts(sectors, assets),
    emails: appConfig.emailTargets,
    providers: appConfig.providers,
    llm: appConfig.llm,
  };
}

function buildAlerts(sectors, assets) {
  const trendSector = [...sectors].sort((a, b) => b.trend - a.trend)[0];
  const riskSector = [...sectors].sort((a, b) => b.risk - a.risk)[0];
  const riskAsset = [...assets].sort((a, b) => b.risk - a.risk)[0];
  return [
    trendSector && {
      title: `${trendSector.name} Trend Score 位于前列`,
      detail: `Trend ${trendSector.trend}，核心变量：${trendSector.indicators.slice(0, 2).join(" / ")}`,
      severity: "high",
    },
    riskSector && {
      title: `${riskSector.name} Risk Score ${riskSector.risk}`,
      detail: riskSector.risks,
      severity: "risk",
    },
    riskAsset && {
      title: `${riskAsset.name} 风险监控`,
      detail: `${riskAsset.ticker} · 当前状态：${riskAsset.state}`,
      severity: riskAsset.risk >= 65 ? "risk" : "medium",
    },
  ].filter(Boolean);
}

function horizonLabel(value) {
  return { long: "长期", medium: "中期", short: "短期", all: "全部" }[value] || value;
}

function statusClass(state) {
  if (state.includes("增持")) return "add";
  if (state.includes("左侧")) return "left";
  if (state.includes("减持")) return "reduce";
  if (state.includes("风险")) return "risk";
  return "watch";
}

function sectorMatchesQuery(sector, query) {
  if (!query) return true;
  const text = [sector.name, sector.horizon, sector.driver, sector.risks, ...sector.indicators].join(" ");
  return normalize(text).includes(query);
}

function assetMatchesQuery(asset, query) {
  if (!query) return true;
  const text = [asset.name, asset.ticker, asset.market, asset.sector, asset.state].join(" ");
  return normalize(text).includes(query);
}

function filteredSectors() {
  const query = normalize(uiState.query);
  return currentData.sectors.filter((item) => {
    const horizonMatch = uiState.activeHorizon === "all" || item.horizon === uiState.activeHorizon;
    return horizonMatch && sectorMatchesQuery(item, query);
  });
}

function filteredAssets() {
  const query = normalize(uiState.query);
  const sectorByName = new Map(currentData.sectors.map((sector) => [sector.name, sector]));
  return currentData.assets.filter((asset) => {
    const sector = sectorByName.get(asset.sector);
    const horizonMatch =
      uiState.activeHorizon === "all" || !sector || sector.horizon === uiState.activeHorizon;
    return horizonMatch && assetMatchesQuery(asset, query);
  });
}

function scoreBars(item) {
  return `
    <div class="score-row">
      <div class="score"><label>Impact ${item.impact}</label><div class="bar" style="--value:${item.impact}%"><span></span></div></div>
      <div class="score"><label>Trend ${item.trend}</label><div class="bar trend" style="--value:${item.trend}%"><span></span></div></div>
      <div class="score"><label>Sent ${item.sentiment || 52}</label><div class="bar sentiment" style="--value:${item.sentiment || 52}%"><span></span></div></div>
      <div class="score"><label>Risk ${item.risk}</label><div class="bar risk" style="--value:${item.risk}%"><span></span></div></div>
    </div>
  `;
}

function renderMetrics() {
  const sectors = filteredSectors();
  const assets = filteredAssets();
  const avg = (items, key) =>
    Math.round(items.reduce((sum, item) => sum + (Number(item[key]) || 0), 0) / items.length || 0);
  const metrics = [
    ["行业覆盖", sectors.length, `${horizonLabel(uiState.activeHorizon)}研究范围`],
    ["关注标的", assets.length, "当前 Watchlist"],
    ["Impact", avg(sectors, "impact"), "行业影响均值"],
    ["Risk", assets.filter((asset) => asset.risk >= 60).length, "风险标的数量"],
  ];

  document.querySelector("#metricsGrid").innerHTML = metrics
    .map(
      ([label, value, note]) => `
        <article class="metric">
          <span>${esc(label)}</span>
          <strong>${esc(value)}</strong>
          <small>${esc(note)}</small>
        </article>
      `,
    )
    .join("");
}

function renderSectorCards(target, boardMode = false) {
  const sectors = filteredSectors();
  const count = document.querySelector("#radarCount");
  if (count) count.textContent = `${sectors.length} sectors`;
  document.querySelector(target).innerHTML =
    sectors
      .map(
        (sector) => `
          <article class="sector-card">
            <header>
              <h3>${esc(sector.name)}</h3>
              <span class="pill ${esc(sector.level)}">${horizonLabel(sector.horizon)}</span>
            </header>
            ${scoreBars(sector)}
            <p>${esc(sector.driver)}</p>
            ${
              boardMode
                ? `<p>观察指标：${esc(sector.indicators.join(" / "))}</p><p>风险：${esc(sector.risks)}</p>`
                : ""
            }
          </article>
        `,
      )
      .join("") || emptyState("暂无行业配置", "sectors");
}

function renderAlerts() {
  document.querySelector("#alertList").innerHTML =
    currentData.alerts
      .map(
        (alert) => `
          <article class="alert ${esc(alert.severity)}">
            <strong>${esc(alert.title)}</strong>
            <span>${esc(alert.detail)}</span>
          </article>
        `,
      )
      .join("") || emptyState("暂无异常信号", "providers");
}

function renderPositionTable() {
  const assets = filteredAssets();
  document.querySelector("#positionTable").innerHTML =
    assets
      .map(
        (asset) => `
          <tr>
            <td><strong>${esc(asset.name)}</strong><span>${esc(asset.ticker)}</span></td>
            <td>${esc(asset.sector)}</td>
            <td><span class="status ${statusClass(asset.state)}">${esc(asset.state)}</span></td>
            <td>${esc(asset.impact)}</td>
            <td>${esc(asset.trend)}</td>
            <td>${esc(asset.risk)}</td>
            <td><span>${esc(asset.evidence)}</span></td>
          </tr>
        `,
      )
      .join("") ||
    `<tr><td colspan="7"><div class="empty-inline">暂无关注标的</div></td></tr>`;
}

function renderWatchlist() {
  const assets = filteredAssets();
  document.querySelector("#watchGrid").innerHTML =
    assets
      .map(
        (asset) => `
          <article class="watch-card">
            <header>
              <h3>${esc(asset.name)} · ${esc(asset.ticker)}</h3>
              <span class="status ${statusClass(asset.state)}">${esc(asset.state)}</span>
            </header>
            ${scoreBars({ ...asset, sentiment: Math.max(42, Math.round((asset.impact + asset.trend - asset.risk) / 2)) })}
            <div class="timeline">
              ${(asset.events || [])
                .map(
                  ([time, text]) => `
                    <div class="timeline-row">
                      <span>${esc(time)}</span>
                      <strong>${esc(text)}</strong>
                    </div>
                  `,
                )
                .join("")}
            </div>
          </article>
        `,
      )
      .join("") || emptyState("暂无关注标的", "assets");
}

function emptyState(text, tab) {
  return `
    <div class="empty-state">
      <strong>${esc(text)}</strong>
      <button class="text-button" data-open-config="${esc(tab)}">去配置</button>
    </div>
  `;
}

function searchCatalog(query) {
  const q = normalize(query);
  if (!q) return [];
  const sectors = [...sectorCatalog, ...appConfig.customSectors]
    .filter((sector) => sectorMatchesQuery(sector, q))
    .map((sector) => ({
      kind: "sector",
      id: sector.id,
      title: sector.name,
      meta: `${horizonLabel(sector.horizon)} · ${sector.indicators.slice(0, 2).join(" / ")}`,
      added: appConfig.sectorIds.includes(sector.id),
    }));
  const assets = [...assetCatalog, ...appConfig.customAssets]
    .filter((asset) => assetMatchesQuery(asset, q))
    .map((asset) => ({
      kind: "asset",
      id: asset.ticker,
      title: `${asset.name} · ${asset.ticker}`,
      meta: `${asset.market || "Market"} · ${asset.sector}`,
      added: appConfig.assetTickers.includes(asset.ticker),
    }));
  return [...sectors, ...assets].slice(0, 10);
}

function setSearchResultsVisible(target, visible) {
  if (!target) return;
  target.hidden = !visible;
  target.classList.toggle("is-hidden", !visible);
  target.style.display = visible ? "" : "none";
}

function renderSearchResults() {
  const target = document.querySelector("#searchResults");
  const items = searchCatalog(uiState.query);
  if (!normalize(uiState.query)) {
    target.innerHTML = "";
    setSearchResultsVisible(target, false);
    return;
  }
  if (!items.length) {
    target.innerHTML = `<div class="search-empty">未匹配，可在配置页创建</div>`;
    setSearchResultsVisible(target, true);
    return;
  }
  target.innerHTML = items
    .map(
      (item) => `
        <button class="search-result" data-action="add-${item.kind}" data-id="${esc(item.id)}">
          <span>
            <strong>${esc(item.title)}</strong>
            <small>${esc(item.meta)}</small>
          </span>
          <em>${item.added ? "已添加" : "添加"}</em>
        </button>
      `,
    )
    .join("");
  setSearchResultsVisible(target, true);
}

function addSector(id) {
  const sector = [...sectorCatalog, ...appConfig.customSectors].find((item) => item.id === id);
  if (!sector) return;
  if (!appConfig.sectorIds.includes(id)) {
    appConfig.sectorIds.push(id);
    uiState.graphFocus = id;
    persistConfig(`已添加行业：${sector.name}`);
  } else {
    uiState.graphFocus = id;
    renderAll();
    showToast(`已定位行业：${sector.name}`);
  }
}

function addAsset(ticker) {
  const asset = [...assetCatalog, ...appConfig.customAssets].find((item) => item.ticker === ticker);
  if (!asset) return;
  const linkedSector = [...sectorCatalog, ...appConfig.customSectors].find(
    (sector) => sector.name === asset.sector,
  );
  if (linkedSector && !appConfig.sectorIds.includes(linkedSector.id)) {
    appConfig.sectorIds.push(linkedSector.id);
  }
  if (!appConfig.assetTickers.includes(ticker)) {
    appConfig.assetTickers.push(ticker);
    persistConfig(`已添加标的：${asset.name}`);
  } else {
    showToast(`已在关注池：${asset.name}`);
  }
}

function removeSector(id) {
  appConfig.sectorIds = appConfig.sectorIds.filter((item) => item !== id);
  persistConfig("行业已移除");
}

function removeAsset(ticker) {
  appConfig.assetTickers = appConfig.assetTickers.filter((item) => item !== ticker);
  persistConfig("标的已移除");
}

function toggleEmail(id) {
  const item = appConfig.emailTargets.find((target) => target.id === id);
  if (!item) return;
  item.enabled = !item.enabled;
  persistConfig(item.enabled ? "邮箱已启用" : "邮箱已停用");
}

function deleteEmail(id) {
  appConfig.emailTargets = appConfig.emailTargets.filter((target) => target.id !== id);
  persistConfig("邮箱目标已删除");
}

function toggleProvider(id) {
  const item = appConfig.providers.find((provider) => provider.id === id);
  if (!item) return;
  item.enabled = !item.enabled;
  persistConfig(item.enabled ? "数据源已启用" : "数据源已停用");
}

function toggleLlm(id) {
  const item = appConfig.llm.providers.find((provider) => provider.id === id);
  if (!item) return;
  item.enabled = !item.enabled;
  persistConfig(item.enabled ? "模型供应商已启用" : "模型供应商已停用");
}

function renderGraphControls() {
  const focus = document.querySelector("#graphFocus");
  if (!focus) return;
  const currentIds = new Set(currentData.sectors.map((sector) => sector.id));
  if (!currentIds.has(uiState.graphFocus) && currentData.sectors[0]) {
    uiState.graphFocus = currentData.sectors[0].id;
  }
  focus.innerHTML = currentData.sectors
    .map(
      (sector) =>
        `<option value="${esc(sector.id)}" ${sector.id === uiState.graphFocus ? "selected" : ""}>${esc(sector.name)}</option>`,
    )
    .join("");
  const depth = document.querySelector("#graphDepth");
  if (depth) depth.value = String(uiState.graphDepth);
}

function graphData() {
  const sector = currentData.sectors.find((item) => item.id === uiState.graphFocus) || currentData.sectors[0];
  if (!sector) return { nodes: [], edges: [], paths: [] };
  const assets = currentData.assets.filter((asset) => asset.sector === sector.name).slice(0, 3);
  const indicators = sector.indicators.slice(0, 3);
  const nodes = [
    { id: "sector", label: sector.name, x: 150, y: 255, color: "#007c78", depth: 0 },
    ...indicators.map((label, index) => ({
      id: `indicator_${index}`,
      label,
      x: 360,
      y: 140 + index * 112,
      color: "#0066cc",
      depth: 1,
    })),
    ...assets.map((asset, index) => ({
      id: `asset_${index}`,
      label: asset.name,
      x: 625,
      y: 155 + index * 120,
      color: asset.risk >= 65 ? "#c9342f" : "#248a3d",
      depth: 2,
    })),
    { id: "risk", label: "风险变量", x: 860, y: 180, color: "#b26a00", depth: 2 },
    { id: "report", label: "日报/周报", x: 1040, y: 255, color: "#6e6e73", depth: 3 },
  ];
  const edges = [
    ...indicators.map((_, index) => ["sector", `indicator_${index}`, 1]),
    ...assets.flatMap((_, assetIndex) =>
      indicators.map((__, indicatorIndex) => [`indicator_${indicatorIndex}`, `asset_${assetIndex}`, 2]),
    ),
    ["sector", "risk", 2],
    ...assets.map((_, index) => [`asset_${index}`, "report", 3]),
    ["risk", "report", 3],
  ].filter((edge) => edge[2] <= uiState.graphDepth);
  const allowed = new Set(["sector"]);
  edges.forEach(([from, to]) => {
    allowed.add(from);
    allowed.add(to);
  });
  const paths = [
    `${sector.name} → ${indicators[0] || "关键指标"} → ${assets[0]?.name || "代表公司"}`,
    `${sector.name} → 风险变量 → 日报/周报`,
  ];
  return { nodes: nodes.filter((node) => allowed.has(node.id)), edges, paths };
}

function drawGraph() {
  const canvas = document.querySelector("#graphCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const ratio = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  if (rect.width < 10 || rect.height < 10) return;
  canvas.width = Math.round(rect.width * ratio);
  canvas.height = Math.round(rect.height * ratio);
  ctx.scale(ratio, ratio);
  ctx.clearRect(0, 0, rect.width, rect.height);

  const data = graphData();
  const scaleX = rect.width / 1200;
  const scaleY = rect.height / 520;
  const nodes = new Map(data.nodes.map((node) => [node.id, node]));

  ctx.lineWidth = 1.4;
  ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--line");
  data.edges.forEach(([from, to]) => {
    const a = nodes.get(from);
    const b = nodes.get(to);
    if (!a || !b) return;
    ctx.beginPath();
    ctx.moveTo(a.x * scaleX, a.y * scaleY);
    ctx.lineTo(b.x * scaleX, b.y * scaleY);
    ctx.stroke();
  });

  data.nodes.forEach((node) => {
    const x = node.x * scaleX;
    const y = node.y * scaleY;
    ctx.beginPath();
    ctx.arc(x, y, 28, 0, Math.PI * 2);
    ctx.fillStyle = node.color;
    ctx.fill();
    ctx.lineWidth = 3;
    ctx.strokeStyle = "rgba(255,255,255,0.72)";
    ctx.stroke();
    ctx.font = "13px -apple-system, BlinkMacSystemFont, sans-serif";
    ctx.textAlign = "center";
    ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--text");
    ctx.fillText(node.label, x, y + 48);
  });

  const pathLabel = document.querySelector("#pathLabel");
  const pathList = document.querySelector("#pathList");
  if (pathLabel) pathLabel.textContent = data.paths[0] || "暂无路径";
  if (pathList) {
    pathList.innerHTML = data.paths.map((path) => `<span>${esc(path)}</span>`).join("");
  }
}

function renderConfigPane() {
  const pane = document.querySelector("#configPane");
  if (!pane) return;
  const renderers = {
    sectors: renderSectorConfig,
    assets: renderAssetConfig,
    emails: renderEmailConfig,
    llm: renderLlmConfig,
    providers: renderProviderConfig,
  };
  pane.innerHTML = renderers[uiState.configTab]();
  renderConfigPreview();
}

function renderSectorConfig() {
  const catalogItems = [...sectorCatalog, ...appConfig.customSectors];
  return `
    <div class="config-grid">
      <form class="config-form" id="sectorForm">
        <h3>新增行业 / 板块</h3>
        <div class="form-row two">
          <label>名称<input name="name" required placeholder="例如：机器人"></label>
          <label>周期<select name="horizon"><option value="long">长期</option><option value="medium">中期</option><option value="short">短期</option></select></label>
        </div>
        <label>核心驱动<input name="driver" placeholder="产业趋势、政策、订单、价格"></label>
        <label>观察指标<input name="indicators" placeholder="用逗号分隔"></label>
        <button class="primary-button" type="submit">添加行业</button>
      </form>
      <div class="config-list">
        <h3>可选行业</h3>
        ${catalogItems
          .map((sector) => {
            const added = appConfig.sectorIds.includes(sector.id);
            return `
              <article class="config-item">
                <div>
                  <strong>${esc(sector.name)}</strong>
                  <span>${horizonLabel(sector.horizon)} · ${esc(sector.indicators.join(" / "))}</span>
                </div>
                <button class="text-button" data-action="${added ? "remove-sector" : "add-sector"}" data-id="${esc(sector.id)}">${added ? "移除" : "添加"}</button>
              </article>
            `;
          })
          .join("")}
      </div>
    </div>
  `;
}

function renderAssetConfig() {
  const catalogItems = [...assetCatalog, ...appConfig.customAssets];
  return `
    <div class="config-grid">
      <form class="config-form" id="assetForm">
        <h3>新增关注标的</h3>
        <div class="form-row two">
          <label>代码<input name="ticker" required placeholder="例如：688981.SH"></label>
          <label>名称<input name="name" required placeholder="例如：中芯国际"></label>
        </div>
        <div class="form-row two">
          <label>市场<select name="market"><option>A-share</option><option>HK</option><option>US</option><option>ETF</option></select></label>
          <label>行业<input name="sector" required placeholder="例如：半导体设备"></label>
        </div>
        <button class="primary-button" type="submit">添加标的</button>
      </form>
      <div class="config-list">
        <h3>可选标的</h3>
        ${catalogItems
          .map((asset) => {
            const added = appConfig.assetTickers.includes(asset.ticker);
            return `
              <article class="config-item">
                <div>
                  <strong>${esc(asset.name)} · ${esc(asset.ticker)}</strong>
                  <span>${esc(asset.market)} · ${esc(asset.sector)} · Risk ${esc(asset.risk)}</span>
                </div>
                <button class="text-button" data-action="${added ? "remove-asset" : "add-asset"}" data-id="${esc(asset.ticker)}">${added ? "移除" : "添加"}</button>
              </article>
            `;
          })
          .join("")}
      </div>
    </div>
  `;
}

function reportTypeCheckboxes(selected = []) {
  const options = [
    ["pre_market", "盘前"],
    ["post_market", "盘后"],
    ["weekly", "周报"],
    ["major_alert", "重大"],
    ["risk_alert", "风险"],
    ["position_window_change", "窗口"],
  ];
  return options
    .map(
      ([value, label]) =>
        `<label class="check-pill"><input type="checkbox" name="reportTypes" value="${value}" ${selected.includes(value) ? "checked" : ""}>${label}</label>`,
    )
    .join("");
}

function renderEmailConfig() {
  return `
    <div class="config-grid">
      <form class="config-form" id="emailForm">
        <h3>目标邮箱</h3>
        <div class="form-row two">
          <label>名称<input name="name" required placeholder="Main Inbox"></label>
          <label>邮箱<input name="address" required type="email" placeholder="user@example.com"></label>
        </div>
        <div class="check-grid">${reportTypeCheckboxes(["post_market", "weekly", "risk_alert"])}</div>
        <div class="form-row two">
          <label>Impact 阈值<input name="impactThreshold" type="number" min="0" max="100" value="70"></label>
          <label>Risk 阈值<input name="riskThreshold" type="number" min="0" max="100" value="60"></label>
        </div>
        <button class="primary-button" type="submit">添加邮箱</button>
      </form>
      <div class="config-list">
        <h3>接收目标</h3>
        ${appConfig.emailTargets
          .map(
            (email) => `
              <article class="config-item">
                <div>
                  <strong>${esc(email.name)}</strong>
                  <span>${esc(email.address)} · ${email.reportTypes.map(esc).join(" / ")}</span>
                </div>
                <div class="item-actions">
                  <button class="toggle-button ${email.enabled ? "on" : ""}" data-action="toggle-email" data-id="${esc(email.id)}"></button>
                  <button class="text-button danger" data-action="delete-email" data-id="${esc(email.id)}">删除</button>
                </div>
              </article>
            `,
          )
          .join("")}
      </div>
    </div>
  `;
}

function renderLlmConfig() {
  return `
    <div class="config-grid">
      <form class="config-form" id="llmForm">
        <h3>新增 LLM Provider</h3>
        <div class="form-row two">
          <label>名称<input name="name" required placeholder="DeepSeek"></label>
          <label>模型<input name="model" required placeholder="deepseek-chat"></label>
        </div>
        <label>Base URL<input name="baseUrl" required placeholder="https://api.example.com/v1"></label>
        <label>API Key 环境变量<input name="apiKeyEnv" placeholder="DEEPSEEK_API_KEY"></label>
        <button class="primary-button" type="submit">添加 Provider</button>
      </form>
      <div class="config-list">
        <h3>模型接入</h3>
        ${appConfig.llm.providers
          .map(
            (provider) => `
              <article class="config-item editable">
                <div>
                  <strong>${esc(provider.name)}</strong>
                  <span>${esc(provider.baseUrl)}</span>
                </div>
                <div class="item-actions">
                  <button class="toggle-button ${provider.enabled ? "on" : ""}" data-action="toggle-llm" data-id="${esc(provider.id)}"></button>
                  <button class="text-button ${appConfig.llm.defaultProvider === provider.id ? "active-text" : ""}" data-action="set-default-llm" data-id="${esc(provider.id)}">默认</button>
                </div>
                <div class="inline-edit">
                  <input data-action="edit-llm" data-id="${esc(provider.id)}" data-field="model" value="${esc(provider.model)}" aria-label="model">
                  <input data-action="edit-llm" data-id="${esc(provider.id)}" data-field="apiKeyEnv" value="${esc(provider.apiKeyEnv)}" aria-label="api key env">
                </div>
              </article>
            `,
          )
          .join("")}
      </div>
    </div>
  `;
}

function renderProviderConfig() {
  return `
    <div class="config-grid">
      <form class="config-form" id="providerForm">
        <h3>新增数据源</h3>
        <div class="form-row two">
          <label>接口名称<input name="name" required placeholder="CommodityPriceProvider"></label>
          <label>类型<input name="type" required placeholder="rest_api"></label>
        </div>
        <div class="form-row two">
          <label>刷新频率<input name="cadence" value="30 min"></label>
          <label>Endpoint<input name="endpoint" placeholder="https://api.example.com"></label>
        </div>
        <button class="primary-button" type="submit">添加数据源</button>
      </form>
      <div class="config-list">
        <h3>Provider 状态</h3>
        ${appConfig.providers
          .map(
            (provider) => `
              <article class="config-item editable">
                <div>
                  <strong>${esc(provider.name)}</strong>
                  <span>${esc(provider.type)} · ${esc(provider.endpoint)}</span>
                </div>
                <div class="item-actions">
                  <button class="toggle-button ${provider.enabled ? "on" : ""}" data-action="toggle-provider" data-id="${esc(provider.id)}"></button>
                </div>
                <div class="inline-edit">
                  <input data-action="edit-provider" data-id="${esc(provider.id)}" data-field="cadence" value="${esc(provider.cadence)}" aria-label="cadence">
                  <input data-action="edit-provider" data-id="${esc(provider.id)}" data-field="endpoint" value="${esc(provider.endpoint)}" aria-label="endpoint">
                </div>
              </article>
            `,
          )
          .join("")}
      </div>
    </div>
  `;
}

function renderConfigPreview() {
  const preview = document.querySelector("#configPreview");
  if (!preview) return;
  preview.textContent = JSON.stringify(
    {
      watchlist: {
        sectors: currentData.sectors.map((sector) => sector.name),
        tickers: appConfig.assetTickers,
      },
      email_targets: appConfig.emailTargets,
      llm: appConfig.llm,
      data_sources: appConfig.providers,
    },
    null,
    2,
  );
}

function renderGraphOnly() {
  renderGraphControls();
  drawGraph();
  requestAnimationFrame(drawGraph);
}

function renderAll() {
  renderMetrics();
  renderSectorCards("#sectorMatrix");
  renderSectorCards("#radarBoard", true);
  renderAlerts();
  renderPositionTable();
  renderWatchlist();
  renderSearchResults();
  renderConfigPane();
  renderGraphOnly();
}

function switchView(viewId) {
  uiState.activeView = viewId;
  document.querySelectorAll(".nav-item").forEach((button) => {
    button.classList.toggle("active", button.dataset.view === viewId);
  });
  document.querySelectorAll(".view").forEach((view) => {
    view.classList.toggle("active", view.id === viewId);
  });
  if (viewId === "graph") renderGraphOnly();
}

function openConfig(tab = "sectors") {
  uiState.configTab = tab;
  document.querySelectorAll("#configTabs button").forEach((button) => {
    button.classList.toggle("active", button.dataset.configTab === tab);
  });
  switchView("settings");
  renderConfigPane();
}

function showToast(message) {
  const toast = document.querySelector("#toast");
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 1700);
}

function createSector(form) {
  const data = new FormData(form);
  const name = String(data.get("name") || "").trim();
  if (!name) return;
  const id = `custom_${slug(name)}_${Date.now().toString(36)}`;
  const sector = {
    id,
    name,
    horizon: String(data.get("horizon") || "medium"),
    level: "medium",
    impact: 55,
    trend: 50,
    sentiment: 50,
    risk: 45,
    driver: String(data.get("driver") || "用户自定义研究方向").trim(),
    risks: "待补充",
    indicators: String(data.get("indicators") || "")
      .split(/[,，]/)
      .map((item) => item.trim())
      .filter(Boolean)
      .slice(0, 5),
  };
  if (!sector.indicators.length) sector.indicators = ["政策", "订单", "价格"];
  appConfig.customSectors.push(sector);
  appConfig.sectorIds.push(id);
  uiState.graphFocus = id;
  form.reset();
  persistConfig(`已创建行业：${name}`);
}

function createAsset(form) {
  const data = new FormData(form);
  const ticker = String(data.get("ticker") || "").trim().toUpperCase();
  const name = String(data.get("name") || "").trim();
  const sector = String(data.get("sector") || "").trim();
  if (!ticker || !name || !sector) return;
  const asset = {
    ticker,
    name,
    market: String(data.get("market") || "A-share"),
    sector,
    state: "观察",
    impact: 50,
    trend: 50,
    risk: 45,
    evidence: "manual_config",
    events: [["配置", "用户手动添加关注标的"]],
  };
  appConfig.customAssets = appConfig.customAssets.filter((item) => item.ticker !== ticker);
  appConfig.customAssets.push(asset);
  if (!appConfig.assetTickers.includes(ticker)) appConfig.assetTickers.push(ticker);
  form.reset();
  persistConfig(`已创建标的：${name}`);
}

function createEmail(form) {
  const data = new FormData(form);
  const reportTypes = data.getAll("reportTypes").map(String);
  const target = {
    id: `email_${Date.now().toString(36)}`,
    name: String(data.get("name") || "").trim(),
    address: String(data.get("address") || "").trim(),
    enabled: true,
    reportTypes: reportTypes.length ? reportTypes : ["post_market"],
    sectors: currentData.sectors.map((sector) => sector.name).slice(0, 3),
    tickers: appConfig.assetTickers.slice(0, 5),
    impactThreshold: Number(data.get("impactThreshold") || 70),
    riskThreshold: Number(data.get("riskThreshold") || 60),
  };
  if (!target.name || !target.address) return;
  appConfig.emailTargets.push(target);
  form.reset();
  persistConfig(`已添加邮箱：${target.name}`);
}

function createLlm(form) {
  const data = new FormData(form);
  const name = String(data.get("name") || "").trim();
  if (!name) return;
  const id = `llm_${slug(name)}_${Date.now().toString(36)}`;
  appConfig.llm.providers.push({
    id,
    name,
    enabled: false,
    baseUrl: String(data.get("baseUrl") || "").trim(),
    model: String(data.get("model") || "").trim(),
    apiKeyEnv: String(data.get("apiKeyEnv") || "").trim(),
  });
  form.reset();
  persistConfig(`已添加 LLM：${name}`);
}

function createProvider(form) {
  const data = new FormData(form);
  const name = String(data.get("name") || "").trim();
  if (!name) return;
  const id = `source_${slug(name)}_${Date.now().toString(36)}`;
  appConfig.providers.push({
    id,
    name,
    type: String(data.get("type") || "").trim(),
    enabled: false,
    cadence: String(data.get("cadence") || "30 min").trim(),
    endpoint: String(data.get("endpoint") || "").trim(),
  });
  form.reset();
  persistConfig(`已添加数据源：${name}`);
}

function updateInlineInput(input) {
  const action = input.dataset.action;
  const id = input.dataset.id;
  const field = input.dataset.field;
  if (action === "edit-llm") {
    const provider = appConfig.llm.providers.find((item) => item.id === id);
    if (provider) provider[field] = input.value.trim();
  }
  if (action === "edit-provider") {
    const provider = appConfig.providers.find((item) => item.id === id);
    if (provider) provider[field] = input.value.trim();
  }
  persistConfig("配置已更新");
}

function exportConfig() {
  const blob = new Blob([document.querySelector("#configPreview").textContent], {
    type: "application/json;charset=utf-8",
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "sgodai-config.json";
  link.click();
  URL.revokeObjectURL(url);
  showToast("配置已导出");
}

function bindEvents() {
  document.querySelector("#commandSearch").addEventListener("input", (event) => {
    uiState.query = event.target.value;
    renderAll();
  });

  document.querySelector("#horizonSegment").addEventListener("click", (event) => {
    const button = event.target.closest("button[data-horizon]");
    if (!button) return;
    uiState.activeHorizon = button.dataset.horizon;
    document.querySelectorAll("#horizonSegment button").forEach((item) => {
      item.classList.toggle("active", item === button);
    });
    renderAll();
  });

  document.querySelector("#openConfigBtn").addEventListener("click", () => openConfig(uiState.configTab));
  document.querySelector("#refreshBtn").addEventListener("click", () => {
    currentData = buildData();
    renderAll();
    showToast("已刷新本地状态");
  });

  document.querySelector("#configTabs").addEventListener("click", (event) => {
    const button = event.target.closest("button[data-config-tab]");
    if (!button) return;
    uiState.configTab = button.dataset.configTab;
    document.querySelectorAll("#configTabs button").forEach((item) => {
      item.classList.toggle("active", item === button);
    });
    renderConfigPane();
  });

  document.querySelector("#graphFocus").addEventListener("change", (event) => {
    uiState.graphFocus = event.target.value;
    renderGraphOnly();
  });
  document.querySelector("#graphDepth").addEventListener("change", (event) => {
    uiState.graphDepth = Number(event.target.value);
    renderGraphOnly();
  });
  document.querySelector("#graphTraceBtn").addEventListener("click", renderGraphOnly);
  document.querySelector("#exportConfigBtn").addEventListener("click", exportConfig);

  document.addEventListener("click", (event) => {
    const openTarget = event.target.closest("[data-open-config]");
    if (openTarget) {
      openConfig(openTarget.dataset.openConfig);
      return;
    }
    const button = event.target.closest("[data-action]");
    if (!button) return;
    const action = button.dataset.action;
    const id = button.dataset.id;
    if (action === "add-sector") addSector(id);
    if (action === "remove-sector") removeSector(id);
    if (action === "add-asset") addAsset(id);
    if (action === "remove-asset") removeAsset(id);
    if (action === "toggle-email") toggleEmail(id);
    if (action === "delete-email") deleteEmail(id);
    if (action === "toggle-provider") toggleProvider(id);
    if (action === "toggle-llm") toggleLlm(id);
    if (action === "set-default-llm") {
      appConfig.llm.defaultProvider = id;
      persistConfig("默认模型已更新");
    }
  });

  document.addEventListener("submit", (event) => {
    event.preventDefault();
    if (event.target.id === "sectorForm") createSector(event.target);
    if (event.target.id === "assetForm") createAsset(event.target);
    if (event.target.id === "emailForm") createEmail(event.target);
    if (event.target.id === "llmForm") createLlm(event.target);
    if (event.target.id === "providerForm") createProvider(event.target);
  });

  document.addEventListener("change", (event) => {
    const input = event.target.closest("input[data-action]");
    if (input) updateInlineInput(input);
  });

  document.addEventListener("click", (event) => {
    if (!event.target.closest(".search-shell")) {
      setSearchResultsVisible(document.querySelector("#searchResults"), false);
    }
  });

  document.querySelectorAll(".nav-item").forEach((button) => {
    button.addEventListener("click", () => switchView(button.dataset.view));
  });

  window.addEventListener("resize", drawGraph);
}

async function boot() {
  bindEvents();
  renderAll();
  setInterval(() => {
    document.querySelector("#clock").textContent = new Date().toLocaleTimeString("zh-CN", {
      hour: "2-digit",
      minute: "2-digit",
    });
  }, 1000);
}

boot();
