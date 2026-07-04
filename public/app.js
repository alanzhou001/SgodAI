const seed = {
  sectors: [
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
  ],
  assets: [
    {
      ticker: "688525.SH",
      name: "佰维存储",
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
      ticker: "300750.SZ",
      name: "宁德时代",
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
  ],
  alerts: [
    {
      title: "AI算力行业 Trend Score 连续两周上升",
      detail: "关联事件 8 条，海外映射与订单线索共振",
      severity: "high",
    },
    {
      title: "创新药 Risk Score 升至 62",
      detail: "临床读出窗口临近，个股分化加大",
      severity: "risk",
    },
    {
      title: "铜库存指标出现拐点",
      detail: "价格信号与库存信号尚未完全确认",
      severity: "medium",
    },
  ],
  providers: [
    { name: "MarketDataProvider", type: "akshare", enabled: false, cadence: "15 min" },
    { name: "AnnouncementProvider", type: "exchange_adapter", enabled: false, cadence: "30 min" },
    { name: "NewsProvider", type: "rss", enabled: true, cadence: "10 min" },
    { name: "LLMProvider", type: "openai_compatible", enabled: true, cadence: "on demand" },
    { name: "AgentProvider", type: "local_http", enabled: true, cadence: "on demand" },
  ],
  emails: [
    {
      name: "Main Inbox",
      address: "user@example.com",
      enabled: true,
      scope: "盘前 / 盘后 / 周报 / 风险预警",
    },
    {
      name: "Risk Only",
      address: "risk@example.com",
      enabled: false,
      scope: "重大异常 / 风险预警 / 窗口变化",
    },
  ],
  graph: {
    nodes: [
      { id: "hbm", label: "HBM", x: 150, y: 250, color: "#007c78" },
      { id: "server", label: "AI服务器", x: 350, y: 140, color: "#0066cc" },
      { id: "memory", label: "存储芯片", x: 570, y: 250, color: "#248a3d" },
      { id: "pkg", label: "先进封装", x: 350, y: 360, color: "#b26a00" },
      { id: "ashare", label: "A股映射", x: 800, y: 180, color: "#6d5bd0" },
      { id: "risk", label: "供给风险", x: 810, y: 340, color: "#c9342f" },
      { id: "report", label: "日报/周报", x: 1020, y: 250, color: "#6e6e73" },
    ],
    edges: [
      ["hbm", "server"],
      ["hbm", "pkg"],
      ["server", "memory"],
      ["pkg", "memory"],
      ["memory", "ashare"],
      ["memory", "risk"],
      ["ashare", "report"],
      ["risk", "report"],
    ],
  },
};

const adapters = {
  async fetchDashboard() {
    return seed;
  },
  async fetchRealDataPlaceholder() {
    return {
      marketDataProvider: "MarketDataProvider.fetch_quotes",
      newsProvider: "NewsProvider.fetch_news",
      llmProvider: "LLMProvider.generate_daily_report",
      agentProvider: "AgentProvider.query_stock_intelligence",
    };
  },
};

let currentData = seed;

function horizonLabel(value) {
  return { long: "长期", medium: "中期", short: "短期" }[value] || value;
}

function statusClass(state) {
  if (state.includes("增持")) return "add";
  if (state.includes("左侧")) return "left";
  if (state.includes("减持")) return "reduce";
  if (state.includes("风险")) return "risk";
  return "watch";
}

function filteredSectors() {
  const sector = document.querySelector("#sectorFilter").value;
  const horizon = document.querySelector("#horizonFilter").value;
  return currentData.sectors.filter((item) => {
    const sectorMatch = sector === "all" || item.id === sector;
    const horizonMatch = horizon === "all" || item.horizon === horizon;
    return sectorMatch && horizonMatch;
  });
}

function renderMetrics() {
  const sectors = filteredSectors();
  const avg = (key) => Math.round(sectors.reduce((sum, item) => sum + item[key], 0) / sectors.length || 0);
  const riskAlerts = currentData.assets.filter((asset) => asset.risk >= 60).length;
  const metrics = [
    ["行业覆盖", sectors.length, "当前筛选范围"],
    ["Impact", avg("impact"), "事件影响均值"],
    ["Trend", avg("trend"), "趋势评分均值"],
    ["Risk", riskAlerts, "风险标的数量"],
  ];

  document.querySelector("#metricsGrid").innerHTML = metrics
    .map(
      ([label, value, note]) => `
        <article class="metric">
          <span>${label}</span>
          <strong>${value}</strong>
          <small>${note}</small>
        </article>
      `,
    )
    .join("");
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

function renderSectorCards(target, boardMode = false) {
  const sectors = filteredSectors();
  document.querySelector("#radarCount").textContent = `${sectors.length} sectors`;
  document.querySelector(target).innerHTML = sectors
    .map(
      (sector) => `
        <article class="sector-card">
          <header>
            <h3>${sector.name}</h3>
            <span class="pill ${sector.level}">${horizonLabel(sector.horizon)}</span>
          </header>
          ${scoreBars(sector)}
          <p>${sector.driver}</p>
          ${
            boardMode
              ? `<p>观察指标：${sector.indicators.join(" / ")}</p><p>风险：${sector.risks}</p>`
              : ""
          }
        </article>
      `,
    )
    .join("");
}

function renderAlerts() {
  document.querySelector("#alertList").innerHTML = currentData.alerts
    .map(
      (alert) => `
        <article class="alert">
          <strong>${alert.title}</strong>
          <span>${alert.detail}</span>
        </article>
      `,
    )
    .join("");
}

function renderPositionTable() {
  document.querySelector("#positionTable").innerHTML = currentData.assets
    .map(
      (asset) => `
        <tr>
          <td><strong>${asset.name}</strong><span>${asset.ticker}</span></td>
          <td>${asset.sector}</td>
          <td><span class="status ${statusClass(asset.state)}">${asset.state}</span></td>
          <td>${asset.impact}</td>
          <td>${asset.trend}</td>
          <td>${asset.risk}</td>
          <td><span>${asset.evidence}</span></td>
        </tr>
      `,
    )
    .join("");
}

function renderWatchlist() {
  document.querySelector("#watchGrid").innerHTML = currentData.assets
    .map(
      (asset) => `
        <article class="watch-card">
          <header>
            <h3>${asset.name} · ${asset.ticker}</h3>
            <span class="status ${statusClass(asset.state)}">${asset.state}</span>
          </header>
          ${scoreBars({ ...asset, sentiment: Math.max(42, Math.round((asset.impact + asset.trend - asset.risk) / 2)) })}
          <div class="timeline">
            ${asset.events
              .map(
                ([time, text]) => `
                  <div class="timeline-row">
                    <span>${time}</span>
                    <strong>${text}</strong>
                  </div>
                `,
              )
              .join("")}
          </div>
        </article>
      `,
    )
    .join("");
}

function renderProviders() {
  document.querySelector("#providerList").innerHTML = currentData.providers
    .map(
      (provider) => `
        <article class="provider-item">
          <header>
            <h3>${provider.name}</h3>
            <span class="toggle ${provider.enabled ? "on" : ""}"></span>
          </header>
          <p>${provider.type} · ${provider.cadence}</p>
        </article>
      `,
    )
    .join("");

  document.querySelector("#emailList").innerHTML = currentData.emails
    .map(
      (email) => `
        <article class="email-item">
          <header>
            <h3>${email.name}</h3>
            <span class="toggle ${email.enabled ? "on" : ""}"></span>
          </header>
          <p>${email.address}</p>
          <p>${email.scope}</p>
        </article>
      `,
    )
    .join("");
}

function fillFilters() {
  const select = document.querySelector("#sectorFilter");
  select.innerHTML =
    '<option value="all">全部行业</option>' +
    currentData.sectors.map((sector) => `<option value="${sector.id}">${sector.name}</option>`).join("");
}

function drawGraph() {
  const canvas = document.querySelector("#graphCanvas");
  const ctx = canvas.getContext("2d");
  const ratio = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  if (rect.width < 10 || rect.height < 10) return;
  canvas.width = Math.round(rect.width * ratio);
  canvas.height = Math.round(rect.height * ratio);
  ctx.scale(ratio, ratio);
  ctx.clearRect(0, 0, rect.width, rect.height);

  const scaleX = rect.width / 1200;
  const scaleY = rect.height / 520;
  const nodes = new Map(currentData.graph.nodes.map((node) => [node.id, node]));

  ctx.lineWidth = 1.4;
  ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--line");
  currentData.graph.edges.forEach(([from, to]) => {
    const a = nodes.get(from);
    const b = nodes.get(to);
    ctx.beginPath();
    ctx.moveTo(a.x * scaleX, a.y * scaleY);
    ctx.lineTo(b.x * scaleX, b.y * scaleY);
    ctx.stroke();
  });

  currentData.graph.nodes.forEach((node) => {
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
}

function switchView(viewId) {
  document.querySelectorAll(".nav-item").forEach((button) => {
    button.classList.toggle("active", button.dataset.view === viewId);
  });
  document.querySelectorAll(".view").forEach((view) => {
    view.classList.toggle("active", view.id === viewId);
  });
  if (viewId === "graph") {
    requestAnimationFrame(drawGraph);
  }
}

function renderAll() {
  renderMetrics();
  renderSectorCards("#sectorMatrix");
  renderSectorCards("#radarBoard", true);
  renderAlerts();
  renderPositionTable();
  renderWatchlist();
  renderProviders();
  drawGraph();
}

async function boot() {
  currentData = await adapters.fetchDashboard();
  fillFilters();
  renderAll();
  document.querySelector("#sectorFilter").addEventListener("change", renderAll);
  document.querySelector("#horizonFilter").addEventListener("change", renderAll);
  document.querySelector("#refreshBtn").addEventListener("click", renderAll);
  document.querySelectorAll(".nav-item").forEach((button) => {
    button.addEventListener("click", () => switchView(button.dataset.view));
  });
  window.addEventListener("resize", drawGraph);
  setInterval(() => {
    document.querySelector("#clock").textContent = new Date().toLocaleTimeString("zh-CN", {
      hour: "2-digit",
      minute: "2-digit",
    });
  }, 1000);
}

boot();
