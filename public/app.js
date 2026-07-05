const STORAGE_KEY = "sgodai.market-radar.config.v2";
const API_BASE_URL = window.location.protocol === "file:" ? "http://127.0.0.1:8000" : "";

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

const assetUniverseAdditions = [
  ["AMD.US", "AMD", "US", "AI算力", "观察", 78, 72, 50],
  ["AVGO.US", "Broadcom", "US", "AI算力", "观察", 77, 70, 48],
  ["MRVL.US", "Marvell", "US", "AI算力", "观察", 70, 64, 49],
  ["ARM.US", "Arm Holdings", "US", "AI算力", "观察", 73, 67, 54],
  ["SMCI.US", "Super Micro Computer", "US", "AI算力", "风险观察", 69, 58, 66],
  ["MSFT.US", "Microsoft", "US", "AI算力", "持有跟踪", 75, 69, 42],
  ["GOOGL.US", "Alphabet", "US", "AI算力", "持有跟踪", 73, 67, 43],
  ["AMZN.US", "Amazon", "US", "AI算力", "持有跟踪", 74, 68, 44],
  ["000977.SZ", "浪潮信息", "A-share", "AI算力", "观察", 68, 61, 52],
  ["603019.SH", "中科曙光", "A-share", "AI算力", "观察", 69, 63, 53],
  ["688041.SH", "海光信息", "A-share", "AI算力", "观察", 72, 65, 56],
  ["688256.SH", "寒武纪-U", "A-share", "AI算力", "风险观察", 74, 66, 64],
  ["300308.SZ", "中际旭创", "A-share", "AI算力", "右侧观察", 76, 73, 50],
  ["300502.SZ", "新易盛", "A-share", "AI算力", "右侧观察", 74, 72, 52],
  ["300394.SZ", "天孚通信", "A-share", "AI算力", "观察", 70, 66, 50],
  ["002281.SZ", "光迅科技", "A-share", "AI算力", "观察", 65, 60, 48],
  ["000938.SZ", "紫光股份", "A-share", "AI算力", "观察", 62, 58, 46],
  ["MU.US", "Micron Technology", "US", "存储芯片", "观察", 73, 67, 51],
  ["WDC.US", "Western Digital", "US", "存储芯片", "观察", 68, 61, 50],
  ["STX.US", "Seagate", "US", "存储芯片", "观察", 62, 56, 48],
  ["005930.KS", "Samsung Electronics", "KR", "存储芯片", "观察", 72, 65, 47],
  ["000660.KS", "SK hynix", "KR", "存储芯片", "右侧观察", 76, 72, 49],
  ["000021.SZ", "深科技", "A-share", "存储芯片", "观察", 58, 53, 46],
  ["600584.SH", "长电科技", "A-share", "存储芯片", "观察", 61, 55, 48],
  ["002156.SZ", "通富微电", "A-share", "存储芯片", "观察", 60, 55, 49],
  ["002185.SZ", "华天科技", "A-share", "存储芯片", "观察", 57, 51, 47],
  ["ASML.US", "ASML", "US", "半导体设备", "持有跟踪", 78, 70, 46],
  ["AMAT.US", "Applied Materials", "US", "半导体设备", "观察", 74, 66, 45],
  ["LRCX.US", "Lam Research", "US", "半导体设备", "观察", 73, 65, 46],
  ["KLAC.US", "KLA", "US", "半导体设备", "观察", 72, 64, 45],
  ["TER.US", "Teradyne", "US", "半导体设备", "观察", 65, 58, 45],
  ["002371.SZ", "北方华创", "A-share", "半导体设备", "观察", 75, 66, 51],
  ["688012.SH", "中微公司", "A-share", "半导体设备", "观察", 73, 64, 49],
  ["688072.SH", "拓荆科技", "A-share", "半导体设备", "观察", 70, 62, 52],
  ["688082.SH", "盛美上海", "A-share", "半导体设备", "观察", 67, 59, 49],
  ["300604.SZ", "长川科技", "A-share", "半导体设备", "观察", 65, 58, 50],
  ["688120.SH", "华海清科", "A-share", "半导体设备", "观察", 66, 59, 48],
  ["688200.SH", "华峰测控", "A-share", "半导体设备", "观察", 62, 55, 47],
  ["600276.SH", "恒瑞医药", "A-share", "创新药", "观察", 68, 58, 49],
  ["603259.SH", "药明康德", "A-share", "创新药", "风险观察", 65, 50, 65],
  ["2359.HK", "药明康德", "HK", "创新药", "风险观察", 64, 50, 66],
  ["300759.SZ", "康龙化成", "A-share", "创新药", "风险观察", 59, 48, 63],
  ["6160.HK", "百济神州", "HK", "创新药", "观察", 70, 60, 55],
  ["688235.SH", "百济神州-U", "A-share", "创新药", "观察", 70, 60, 55],
  ["1801.HK", "信达生物", "HK", "创新药", "观察", 66, 57, 53],
  ["9969.HK", "诺诚健华", "HK", "创新药", "观察", 60, 52, 57],
  ["3692.HK", "翰森制药", "HK", "创新药", "观察", 62, 53, 50],
  ["1177.HK", "中国生物制药", "HK", "创新药", "观察", 61, 52, 49],
  ["1093.HK", "石药集团", "HK", "创新药", "观察", 60, 51, 49],
  ["688506.SH", "百利天恒", "A-share", "创新药", "观察", 64, 58, 61],
  ["688266.SH", "泽璟制药-U", "A-share", "创新药", "观察", 58, 51, 62],
  ["688578.SH", "艾力斯", "A-share", "创新药", "观察", 62, 55, 57],
  ["MRNA.US", "Moderna", "US", "创新药", "观察", 60, 48, 62],
  ["REGN.US", "Regeneron", "US", "创新药", "持有跟踪", 66, 56, 44],
  ["VRTX.US", "Vertex", "US", "创新药", "持有跟踪", 67, 57, 43],
  ["002085.SZ", "万丰奥威", "A-share", "低空经济", "风险观察", 66, 59, 63],
  ["002097.SZ", "山河智能", "A-share", "低空经济", "观察", 58, 52, 55],
  ["300900.SZ", "广联航空", "A-share", "低空经济", "观察", 56, 51, 55],
  ["688297.SH", "中无人机", "A-share", "低空经济", "观察", 60, 53, 52],
  ["600038.SH", "中直股份", "A-share", "低空经济", "观察", 61, 54, 50],
  ["000099.SZ", "中信海直", "A-share", "低空经济", "观察", 59, 54, 56],
  ["002111.SZ", "威海广泰", "A-share", "低空经济", "观察", 55, 49, 50],
  ["300699.SZ", "光威复材", "A-share", "低空经济", "观察", 57, 51, 49],
  ["002389.SZ", "航天彩虹", "A-share", "低空经济", "观察", 58, 52, 51],
  ["300274.SZ", "阳光电源", "A-share", "储能", "观察", 70, 61, 55],
  ["300014.SZ", "亿纬锂能", "A-share", "储能", "观察", 64, 55, 56],
  ["002594.SZ", "比亚迪", "A-share", "储能", "观察", 68, 58, 52],
  ["300207.SZ", "欣旺达", "A-share", "储能", "观察", 58, 51, 55],
  ["688390.SH", "固德威", "A-share", "储能", "风险观察", 55, 45, 65],
  ["688032.SH", "禾迈股份", "A-share", "储能", "风险观察", 56, 46, 64],
  ["688223.SH", "晶科能源", "A-share", "储能", "观察", 57, 49, 61],
  ["002812.SZ", "恩捷股份", "A-share", "储能", "观察", 54, 47, 60],
  ["002709.SZ", "天赐材料", "A-share", "储能", "观察", 55, 48, 59],
  ["002460.SZ", "赣锋锂业", "A-share", "储能", "观察", 59, 50, 60],
  ["002466.SZ", "天齐锂业", "A-share", "储能", "观察", 60, 51, 59],
  ["TSLA.US", "Tesla", "US", "储能", "观察", 67, 57, 58],
  ["ENPH.US", "Enphase Energy", "US", "储能", "风险观察", 54, 44, 68],
  ["SEDG.US", "SolarEdge", "US", "储能", "风险观察", 51, 39, 72],
  ["ALB.US", "Albemarle", "US", "储能", "观察", 58, 49, 59],
  ["SQM.US", "SQM", "US", "储能", "观察", 57, 48, 58],
  ["601899.SH", "紫金矿业", "A-share", "铜", "观察", 72, 66, 48],
  ["603993.SH", "洛阳钼业", "A-share", "铜", "观察", 68, 61, 52],
  ["600362.SH", "江西铜业", "A-share", "铜", "观察", 66, 59, 50],
  ["000630.SZ", "铜陵有色", "A-share", "铜", "观察", 62, 55, 49],
  ["601600.SH", "中国铝业", "A-share", "铜", "观察", 61, 54, 50],
  ["000807.SZ", "云铝股份", "A-share", "铜", "观察", 60, 53, 49],
  ["000933.SZ", "神火股份", "A-share", "铜", "观察", 60, 53, 48],
  ["600547.SH", "山东黄金", "A-share", "铜", "观察", 58, 51, 47],
  ["FCX.US", "Freeport-McMoRan", "US", "铜", "观察", 69, 62, 50],
  ["SCCO.US", "Southern Copper", "US", "铜", "观察", 67, 60, 49],
  ["BHP.US", "BHP", "US", "铜", "观察", 64, 57, 46],
  ["RIO.US", "Rio Tinto", "US", "铜", "观察", 63, 56, 46],
  ["VALE.US", "Vale", "US", "铜", "观察", 61, 54, 48],
];

const assetUniverse = uniqBy([...assetCatalog, ...assetUniverseAdditions.map(createUniverseAsset)], (asset) => asset.ticker);

const industryAssistProfiles = [
  {
    terms: ["ai算力", "算力", "gpu", "服务器"],
    horizon: "long",
    driver: "云厂商资本开支、国产算力替代和大模型推理需求共同驱动",
    risks: "海外出口限制、算力供应瓶颈、估值拥挤",
    indicators: ["云厂商资本开支", "GPU/ASIC供给", "服务器订单", "数据中心电力"],
    upstream: ["GPU/ASIC", "先进封装", "光模块", "服务器ODM"],
    downstream: ["云计算", "大模型应用", "数据中心", "企业AI软件"],
    relatedTickers: [
      "NVDA.US",
      "AMD.US",
      "AVGO.US",
      "MRVL.US",
      "ARM.US",
      "SMCI.US",
      "MSFT.US",
      "GOOGL.US",
      "AMZN.US",
      "000977.SZ",
      "603019.SH",
      "688041.SH",
      "688256.SH",
      "300308.SZ",
      "300502.SZ",
      "300394.SZ",
      "002281.SZ",
      "000938.SZ",
      "TSM.US",
    ],
  },
  {
    terms: ["hbm", "高带宽存储"],
    horizon: "medium",
    driver: "AI服务器拉动高带宽存储需求，先进封装和供给节奏决定景气弹性",
    risks: "扩产节奏、客户集中度、海外龙头资本开支波动",
    indicators: ["HBM价格", "先进封装产能", "AI服务器出货", "海外龙头指引"],
    upstream: ["DRAM晶圆", "先进封装", "半导体设备", "封装材料"],
    downstream: ["AI服务器", "GPU模组", "云计算", "高性能计算"],
    relatedTickers: [
      "688525.SH",
      "603986.SH",
      "MU.US",
      "000660.KS",
      "005930.KS",
      "NVDA.US",
      "AMD.US",
      "AVGO.US",
      "MRVL.US",
      "TSM.US",
      "ASML.US",
      "AMAT.US",
      "LRCX.US",
      "600584.SH",
      "002156.SZ",
      "002185.SZ",
    ],
  },
  {
    terms: ["存储芯片", "dram", "nand", "存储"],
    horizon: "medium",
    driver: "价格周期改善、库存回补和AI终端容量升级共同影响盈利弹性",
    risks: "库存回补后需求放缓、价格回落、周期波动",
    indicators: ["DRAM价格", "NAND价格", "库存天数", "下游锁单"],
    upstream: ["晶圆制造", "半导体设备", "材料", "封测"],
    downstream: ["AI服务器", "消费电子", "汽车电子", "工业控制"],
    relatedTickers: [
      "688525.SH",
      "603986.SH",
      "MU.US",
      "WDC.US",
      "STX.US",
      "005930.KS",
      "000660.KS",
      "000021.SZ",
      "600584.SH",
      "002156.SZ",
      "002185.SZ",
      "NVDA.US",
      "TSM.US",
    ],
  },
  {
    terms: ["半导体设备", "设备", "晶圆厂"],
    horizon: "long",
    driver: "国产替代、晶圆厂资本开支和先进制程验证推进共同驱动",
    risks: "订单兑现、出口管制、研发投入和客户验证周期",
    indicators: ["设备订单", "晶圆厂资本开支", "国产化率", "验收节奏"],
    upstream: ["核心零部件", "精密加工", "电子材料", "工业软件"],
    downstream: ["晶圆制造", "先进封装", "存储芯片", "功率半导体"],
    relatedTickers: [
      "ASML.US",
      "AMAT.US",
      "LRCX.US",
      "KLAC.US",
      "TER.US",
      "TSM.US",
      "002371.SZ",
      "688012.SH",
      "688072.SH",
      "688082.SH",
      "300604.SZ",
      "688120.SH",
      "688200.SH",
      "603986.SH",
      "688525.SH",
    ],
  },
  {
    terms: ["创新药", "biotech", "医药"],
    horizon: "long",
    driver: "临床数据读出、BD授权交易和支付环境变化影响行业风险偏好",
    risks: "研发失败、医保支付、监管审评和融资环境变化",
    indicators: ["临床数据", "BD交易", "融资环境", "医保政策"],
    upstream: ["CXO", "靶点发现", "临床试验", "原料药"],
    downstream: ["商业化销售", "医院终端", "医保支付", "海外授权"],
    relatedTickers: [
      "600276.SH",
      "603259.SH",
      "2359.HK",
      "300759.SZ",
      "2269.HK",
      "6160.HK",
      "688235.SH",
      "1801.HK",
      "9969.HK",
      "3692.HK",
      "1177.HK",
      "1093.HK",
      "688506.SH",
      "688266.SH",
      "688578.SH",
      "MRNA.US",
      "REGN.US",
      "VRTX.US",
    ],
  },
  {
    terms: ["低空经济", "低空", "无人机", "evtol"],
    horizon: "short",
    driver: "地方试点、空域改革和应用场景订单推动主题验证",
    risks: "商业模式验证不足、适航审批、基础设施建设节奏",
    indicators: ["地方政策", "订单公告", "空域改革", "适航进度"],
    upstream: ["电池", "航电系统", "复合材料", "飞控芯片"],
    downstream: ["城市交通", "物流巡检", "应急救援", "文旅场景"],
    relatedTickers: [
      "002085.SZ",
      "002097.SZ",
      "300900.SZ",
      "688297.SH",
      "600038.SH",
      "000099.SZ",
      "002111.SZ",
      "300699.SZ",
      "002389.SZ",
    ],
  },
  {
    terms: ["储能", "电池", "新能源"],
    horizon: "medium",
    driver: "海外订单、利用小时和电芯价格变化决定盈利修复节奏",
    risks: "价格竞争、海外政策变化、产能利用率不足",
    indicators: ["电芯价格", "海外订单", "利用小时", "装机规模"],
    upstream: ["锂电材料", "电芯", "PCS", "温控系统"],
    downstream: ["新能源电站", "工商业储能", "电网侧储能", "海外渠道"],
    relatedTickers: [
      "300750.SZ",
      "300274.SZ",
      "300014.SZ",
      "002594.SZ",
      "300207.SZ",
      "688390.SH",
      "688032.SH",
      "688223.SH",
      "002812.SZ",
      "002709.SZ",
      "002460.SZ",
      "002466.SZ",
      "TSLA.US",
      "ENPH.US",
      "SEDG.US",
      "ALB.US",
      "SQM.US",
    ],
  },
  {
    terms: ["铜", "铝", "锂", "资源"],
    horizon: "medium",
    driver: "矿端扰动、库存变化和电网/数据中心需求共同影响资源品价格",
    risks: "全球经济波动、美元流动性、库存拐点",
    indicators: ["LME库存", "现货升贴水", "矿端扰动", "下游开工率"],
    upstream: ["矿山", "冶炼", "再生金属", "物流"],
    downstream: ["电网", "新能源车", "数据中心", "家电"],
    relatedTickers: [
      "601899.SH",
      "603993.SH",
      "600362.SH",
      "000630.SZ",
      "601600.SH",
      "000807.SZ",
      "000933.SZ",
      "600547.SH",
      "002460.SZ",
      "002466.SZ",
      "FCX.US",
      "SCCO.US",
      "BHP.US",
      "RIO.US",
      "VALE.US",
      "ALB.US",
      "SQM.US",
    ],
  },
];

const defaultConfig = {
  sectorIds: ["ai_compute", "hbm", "memory", "biotech", "low_altitude", "copper"],
  deletedSectorIds: [],
  deletedAssetTickers: [],
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
      type: "akshare + sina_a_share_fallback",
      enabled: true,
      cadence: "15 min",
      endpoint: "adapter://akshare, adapter://sina_a_share",
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
  detail: {
    type: null,
    id: null,
    fromView: "dashboard",
  },
  remoteAssetSearch: {
    query: "",
    loading: false,
    items: [],
    errors: [],
    requestId: 0,
  },
};

const commandHiddenViews = new Set(["graph", "settings"]);
const marketDataCache = new Map();
const intelligenceCache = new Map();
let searchTimer = null;

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

function apiUrl(path) {
  return `${API_BASE_URL}${path}`;
}

async function apiGet(path) {
  const response = await fetch(apiUrl(path), {
    headers: { Accept: "application/json" },
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = typeof payload.detail === "string" ? payload.detail : JSON.stringify(payload.detail || {});
    throw new Error(detail || `API ${response.status}`);
  }
  return payload;
}

async function apiPost(path, body) {
  const response = await fetch(apiUrl(path), {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = typeof payload.detail === "string" ? payload.detail : JSON.stringify(payload.detail || {});
    throw new Error(detail || `API ${response.status}`);
  }
  return payload;
}

function slug(value) {
  return normalize(value)
    .replace(/[^a-z0-9\u4e00-\u9fa5]+/gi, "_")
    .replace(/^_+|_+$/g, "")
    .slice(0, 32);
}

function createUniverseAsset([ticker, name, market, sector, state, impact, trend, risk]) {
  return {
    ticker,
    name,
    market,
    sector,
    state,
    impact,
    trend,
    risk,
    evidence: "seed_universe",
    events: [
      ["候选", "产业链候选池标的，等待真实数据源验证"],
      ["映射", `${sector} 相关标的候选`],
    ],
  };
}

function listFromValue(value) {
  if (Array.isArray(value)) return value.map((item) => String(item).trim()).filter(Boolean);
  return String(value || "")
    .split(/[,，、/;；\n]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function uniqBy(items, keyFn) {
  const seen = new Set();
  return items.filter((item) => {
    const key = keyFn(item);
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function allAssets() {
  const deleted = new Set((appConfig.deletedAssetTickers || []).map((ticker) => String(ticker).toUpperCase()));
  return uniqBy([...appConfig.customAssets, ...assetUniverse], (asset) => asset.ticker).filter(
    (asset) => !deleted.has(String(asset.ticker).toUpperCase()),
  );
}

function allSectors() {
  const deleted = new Set(appConfig.deletedSectorIds || []);
  return [...sectorCatalog, ...appConfig.customSectors].filter((sector) => !deleted.has(sector.id));
}

function isCustomSector(id) {
  return appConfig.customSectors.some((sector) => sector.id === id);
}

function isCustomAsset(ticker) {
  return appConfig.customAssets.some((asset) => asset.ticker === ticker);
}

function findSectorById(id) {
  return allSectors().find((sector) => sector.id === id);
}

function findSectorByName(name) {
  return allSectors().find((sector) => sector.name === name);
}

function findAssetByTicker(ticker) {
  return allAssets().find((asset) => asset.ticker === ticker);
}

function findRemoteAssetByTicker(ticker) {
  return uiState.remoteAssetSearch.items.find((asset) => asset.ticker === ticker);
}

function inferRemoteAssetSector(item) {
  const matched = allAssets().find(
    (asset) =>
      asset.ticker === item.ticker ||
      normalize(asset.name) === normalize(item.name) ||
      normalize(item.name).includes(normalize(asset.name)),
  );
  return matched?.sector || "待分类";
}

function normalizeRemoteAsset(item) {
  const sector = inferRemoteAssetSector(item);
  return {
    ticker: String(item.ticker || "").toUpperCase(),
    name: String(item.name || item.ticker || "").trim(),
    market: String(item.market || "A-share"),
    sector,
    state: "观察",
    impact: 50,
    trend: 50,
    risk: 45,
    evidence: `asset_search:${item.source || "public"}`,
    events: [
      ["搜索", "真实标的搜索返回，等待行情、公告和财报验证"],
      ["来源", `${item.market || "Market"} · ${item.exchange || ""}`.trim()],
    ],
    source: item.source || "public_asset_search",
  };
}

function activeLlmProvider() {
  return (
    appConfig.llm.providers.find((provider) => provider.id === appConfig.llm.defaultProvider) ||
    appConfig.llm.providers.find((provider) => provider.enabled) ||
    appConfig.llm.providers[0]
  );
}

function matchIndustryProfile(input) {
  const text = normalize(input);
  return (
    industryAssistProfiles.find((profile) =>
      profile.terms.some((term) => text.includes(normalize(term)) || normalize(term).includes(text)),
    ) || null
  );
}

function genericIndustryProfile(name) {
  return {
    terms: [name],
    horizon: "medium",
    driver: `${name} 处于用户自定义研究范围，需跟踪政策、供需、价格和订单变化`,
    risks: "数据源尚未接入，产业链映射和财务验证需要继续补充",
    indicators: ["政策变化", "订单变化", "价格变化", "供需格局"],
    upstream: ["原材料", "核心零部件", "设备/服务"],
    downstream: ["终端应用", "渠道客户", "行业需求"],
    relatedTickers: [],
  };
}

function sectorProfile(sector) {
  const seed = [sector.name, sector.driver, ...(sector.indicators || [])].join(" ");
  const matched = matchIndustryProfile(seed) || genericIndustryProfile(sector.name);
  const indicators = listFromValue(sector.indicators).length ? listFromValue(sector.indicators) : matched.indicators;
  return {
    ...matched,
    horizon: sector.horizon || matched.horizon,
    driver: sector.driver || matched.driver,
    risks: sector.risks || matched.risks,
    indicators,
    upstream: listFromValue(sector.upstream).length ? listFromValue(sector.upstream) : matched.upstream,
    downstream: listFromValue(sector.downstream).length ? listFromValue(sector.downstream) : matched.downstream,
    relatedTickers: listFromValue(sector.relatedTickers).length
      ? listFromValue(sector.relatedTickers)
      : matched.relatedTickers,
  };
}

function relatedAssetsForSector(sector) {
  const profile = sectorProfile(sector);
  const text = normalize([sector.name, profile.terms.join(" "), profile.downstream.join(" "), profile.upstream.join(" ")].join(" "));
  const byTicker = new Map(allAssets().map((asset) => [asset.ticker, asset]));
  const explicit = profile.relatedTickers.map((ticker) => byTicker.get(ticker)).filter(Boolean);
  const semantic = allAssets().filter((asset) => {
    const assetText = normalize([asset.name, asset.ticker, asset.sector].join(" "));
    return asset.sector === sector.name || text.includes(normalize(asset.sector)) || assetText.includes(normalize(sector.name));
  });
  const watched = currentData.assets.filter((asset) => asset.sector === sector.name);
  return uniqBy([...watched, ...explicit, ...semantic], (asset) => asset.ticker).slice(0, 5);
}

function assetsForSectorDetail(sector) {
  const profile = sectorProfile(sector);
  const byTicker = new Map(allAssets().map((asset) => [asset.ticker, asset]));
  const explicit = profile.relatedTickers.map((ticker) => byTicker.get(ticker)).filter(Boolean);
  const direct = allAssets().filter((asset) => asset.sector === sector.name);
  const text = normalize([sector.name, profile.terms.join(" "), profile.upstream.join(" "), profile.downstream.join(" ")].join(" "));
  const semantic = allAssets().filter((asset) => text.includes(normalize(asset.sector)));
  return uniqBy([...direct, ...explicit, ...semantic], (asset) => asset.ticker);
}

function localLlmAssist(kind, payload) {
  if (kind === "sector") {
    const name = String(payload.name || "").trim();
    const profile = matchIndustryProfile(name) || genericIndustryProfile(name || "新行业");
    const relatedTickers = relatedAssetsForProfile(name, profile).map((asset) => asset.ticker);
    return { ...profile, relatedTickers };
  }
  if (kind === "asset") {
    return inferAssetDraft(payload.name, payload);
  }
  return {};
}

function relatedAssetsForProfile(name, profile) {
  const text = normalize([name, profile.terms.join(" "), profile.upstream.join(" "), profile.downstream.join(" ")].join(" "));
  const explicit = new Set(profile.relatedTickers || []);
  return uniqBy(
    allAssets().filter((asset) => {
      const assetText = normalize([asset.name, asset.ticker, asset.sector].join(" "));
      return explicit.has(asset.ticker) || text.includes(normalize(asset.sector)) || assetText.includes(normalize(name));
    }),
    (asset) => asset.ticker,
  );
}

function inferAssetDraft(name, payload = {}) {
  const rawName = String(name || "").trim();
  const q = normalize(rawName);
  const matched = allAssets().find((asset) => {
    const haystack = normalize([asset.name, asset.ticker].join(" "));
    return q && (haystack.includes(q) || q.includes(normalize(asset.name)));
  });
  if (matched) return clone(matched);
  const sectors = allSectors();
  const matchedSector =
    sectors.find((sector) => normalize(rawName).includes(normalize(sector.name))) ||
    sectors.find((sector) => {
      const profile = sectorProfile(sector);
      return profile.terms.some((term) => normalize(rawName).includes(normalize(term)));
    }) ||
    sectors[0];
  return {
    ticker: String(payload.ticker || "").trim().toUpperCase(),
    name: rawName,
    market: String(payload.market || "A-share"),
    sector: String(payload.sector || matchedSector?.name || "待分类").trim(),
    state: "观察",
    impact: 50,
    trend: 50,
    risk: 45,
    evidence: "llm_assist_pending_source",
    events: [["配置", "LLM 辅助生成初稿，等待真实数据源验证"]],
  };
}

async function requestLlmAssistance(kind, payload) {
  try {
    const response = await apiPost("/api/llm/config-assist", {
      kind,
      ...payload,
      market_scope: ["A-share", "HK"],
    });
    return {
      provider: `${response.provider || "DeepSeek"}${response.model ? ` · ${response.model}` : ""}`,
      result: normalizeAssistResult(kind, response.result || {}),
      fallback: false,
    };
  } catch (error) {
    const provider = activeLlmProvider();
    const label = provider?.name ? `Local fallback（${provider.name} API 不可用）` : "Local fallback";
    return { provider: label, result: localLlmAssist(kind, payload), fallback: true, error: error.message };
  }
}

function normalizeAssistResult(kind, result) {
  if (kind === "sector") {
    const validatedAssets = Array.isArray(result.validatedAssets) ? result.validatedAssets : [];
    return {
      horizon: result.horizon || "medium",
      driver: result.driver || result.summary || "",
      risks: Array.isArray(result.risks) ? result.risks.join("；") : result.risks || "",
      indicators: listFromValue(result.indicators),
      upstream: listFromValue(result.upstream),
      downstream: listFromValue(result.downstream),
      relatedTickers: listFromValue(result.relatedTickers).length
        ? listFromValue(result.relatedTickers)
        : validatedAssets.map((asset) => asset.ticker).filter(Boolean),
      validatedAssets,
      confidence: result.confidence,
      riskNotes: result.risk_notes || [],
    };
  }
  return {
    ...result,
    ticker: String(result.ticker || "").trim().toUpperCase(),
    market: result.market || "A-share",
    sector: result.sector || "待分类",
    validatedAssets: Array.isArray(result.validatedAssets) ? result.validatedAssets : [],
  };
}

function upsertValidatedAssets(assets, sectorName) {
  (assets || []).forEach((item) => {
    if (!item.ticker || findAssetByTicker(item.ticker)) return;
    appConfig.customAssets.push({
      ticker: item.ticker,
      name: item.name || item.ticker,
      market: item.market || "A-share",
      sector: sectorName || "待分类",
      state: "观察",
      impact: 50,
      trend: 50,
      risk: 45,
      evidence: `deepseek_validated:${item.source || "asset_search"}`,
      events: [["DeepSeek", item.rationale || "AI 补全候选标的已通过真实标的搜索校验"]],
    });
  });
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
      deletedSectorIds: parsed.deletedSectorIds || [],
      deletedAssetTickers: parsed.deletedAssetTickers || [],
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
  const sectors = allSectors().filter((sector) => appConfig.sectorIds.includes(sector.id));
  const assets = allAssets().filter((asset) => appConfig.assetTickers.includes(asset.ticker));
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
  const trendProfile = trendSector ? sectorProfile(trendSector) : null;
  const riskProfile = riskSector ? sectorProfile(riskSector) : null;
  return [
    trendSector && {
      title: `${trendSector.name} Trend Score 位于前列`,
      detail: `Trend ${trendSector.trend}，核心变量：${trendProfile.indicators.slice(0, 2).join(" / ")}`,
      severity: "high",
    },
    riskSector && {
      title: `${riskSector.name} Risk Score ${riskSector.risk}`,
      detail: riskProfile.risks,
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
  const profile = sectorProfile(sector);
  const text = [
    sector.name,
    profile.horizon,
    profile.driver,
    profile.risks,
    ...profile.indicators,
    ...profile.upstream,
    ...profile.downstream,
    ...profile.relatedTickers,
  ].join(" ");
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
  const assets = filteredAssets().map(scoredAsset);
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
        (sector) => {
          const profile = sectorProfile(sector);
          return `
            <article class="sector-card interactive-card" role="button" tabindex="0" data-action="open-sector-detail" data-id="${esc(sector.id)}" aria-label="查看 ${esc(sector.name)} 详情">
              <header>
                <h3>${esc(sector.name)}</h3>
                <span class="pill ${esc(sector.level)}">${horizonLabel(profile.horizon)}</span>
              </header>
              ${scoreBars(sector)}
              <p>${esc(profile.driver)}</p>
              ${
                boardMode
                  ? `<p>上游/下游：${esc(profile.upstream.slice(0, 2).join(" / "))} → ${esc(profile.downstream.slice(0, 2).join(" / "))}</p><p>观察指标：${esc(profile.indicators.join(" / "))}</p><p>风险：${esc(profile.risks)}</p>`
                  : ""
              }
            </article>
          `;
        },
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
  const assets = filteredAssets().map(scoredAsset);
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
  const assets = filteredAssets().map(scoredAsset);
  document.querySelector("#watchGrid").innerHTML =
    assets
      .map(
        (asset) => `
          <article class="watch-card interactive-card" role="button" tabindex="0" data-action="open-asset-detail" data-id="${esc(asset.ticker)}" aria-label="查看 ${esc(asset.name)} 详情">
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

function remoteSearchReady(query) {
  return (
    uiState.remoteAssetSearch.query === normalize(query) &&
    (uiState.remoteAssetSearch.loading || uiState.remoteAssetSearch.items.length || uiState.remoteAssetSearch.errors.length)
  );
}

function remoteAssetSearchResults(query) {
  if (!remoteSearchReady(query)) return [];
  const q = normalize(query);
  return uiState.remoteAssetSearch.items
    .filter((asset) => assetMatchesQuery({ ...asset, sector: inferRemoteAssetSector(asset), state: "观察" }, q))
    .map((asset) => {
      const sector = inferRemoteAssetSector(asset);
      return {
        kind: "asset",
        id: asset.ticker,
        title: `${asset.name} · ${asset.ticker}`,
        meta: `真实标的 · ${asset.market || "Market"} · ${sector} · ${asset.source || "public"}`,
        added: appConfig.assetTickers.includes(asset.ticker),
      };
    });
}

function searchCatalog(query) {
  const q = normalize(query);
  if (!q) return [];
  const sectors = allSectors()
    .filter((sector) => sectorMatchesQuery(sector, q))
    .map((sector) => {
      const profile = sectorProfile(sector);
      return {
        kind: "sector",
        id: sector.id,
        title: sector.name,
        meta: `${horizonLabel(profile.horizon)} · ${profile.upstream.slice(0, 1).join(" / ")} → ${profile.downstream.slice(0, 1).join(" / ")}`,
        added: appConfig.sectorIds.includes(sector.id),
      };
    });
  const assets = allAssets()
    .filter((asset) => assetMatchesQuery(asset, q))
    .map((asset) => ({
      kind: "asset",
      id: asset.ticker,
      title: `${asset.name} · ${asset.ticker}`,
      meta: `${asset.market || "Market"} · ${asset.sector}`,
      added: appConfig.assetTickers.includes(asset.ticker),
    }));
  return uniqBy([...sectors, ...assets, ...remoteAssetSearchResults(query)], (item) => `${item.kind}:${item.id}`).slice(
    0,
    12,
  );
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
  const footer = uiState.remoteAssetSearch.loading
    ? `<div class="search-empty">正在查询真实 A股 / 港股标的...</div>`
    : uiState.remoteAssetSearch.errors.length
      ? `<div class="search-empty">部分真实数据源不可用，已显示可用结果</div>`
      : "";
  if (!items.length) {
    target.innerHTML = `${footer}<div class="search-empty">未匹配，可在配置页创建</div>`;
    setSearchResultsVisible(target, true);
    return;
  }
  target.innerHTML =
    items
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
      .join("") + footer;
  setSearchResultsVisible(target, true);
}

function scheduleRemoteAssetSearch(query) {
  const q = normalize(query);
  clearTimeout(searchTimer);
  if (q.length < 2) {
    uiState.remoteAssetSearch = {
      ...uiState.remoteAssetSearch,
      query: q,
      loading: false,
      items: [],
      errors: [],
    };
    renderSearchResults();
    return;
  }
  const requestId = Date.now();
  uiState.remoteAssetSearch = {
    ...uiState.remoteAssetSearch,
    query: q,
    loading: true,
    requestId,
  };
  renderSearchResults();
  searchTimer = setTimeout(() => fetchRemoteAssetSearch(query, requestId), 280);
}

async function fetchRemoteAssetSearch(query, requestId) {
  try {
    const params = new URLSearchParams({
      q: query.trim(),
      limit: "18",
      markets: "A-share,HK",
    });
    const payload = await apiGet(`/api/assets/search?${params.toString()}`);
    if (uiState.remoteAssetSearch.requestId !== requestId) return;
    uiState.remoteAssetSearch = {
      ...uiState.remoteAssetSearch,
      query: normalize(query),
      loading: false,
      items: payload.results || [],
      errors: payload.errors || [],
    };
  } catch (error) {
    if (uiState.remoteAssetSearch.requestId !== requestId) return;
    uiState.remoteAssetSearch = {
      ...uiState.remoteAssetSearch,
      query: normalize(query),
      loading: false,
      items: [],
      errors: [{ source: "api", error: error.message }],
    };
  }
  renderSearchResults();
}

function addSector(id) {
  const sector = allSectors().find((item) => item.id === id);
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
  let asset = findAssetByTicker(ticker);
  if (!asset) {
    const remoteAsset = findRemoteAssetByTicker(ticker);
    if (remoteAsset) {
      asset = normalizeRemoteAsset(remoteAsset);
      appConfig.customAssets = appConfig.customAssets.filter((item) => item.ticker !== asset.ticker);
      appConfig.customAssets.push(asset);
    }
  }
  if (!asset) return;
  const linkedSector = allSectors().find((sector) => sector.name === asset.sector);
  if (linkedSector && !appConfig.sectorIds.includes(linkedSector.id)) {
    appConfig.sectorIds.push(linkedSector.id);
  }
  if (!appConfig.assetTickers.includes(ticker)) {
    appConfig.assetTickers.push(ticker);
    persistConfig(`已添加标的：${asset.name}`);
    ensureAssetIntelligence(asset, { force: true });
  } else {
    showToast(`已在关注池：${asset.name}`);
  }
}

function removeSector(id) {
  appConfig.sectorIds = appConfig.sectorIds.filter((item) => item !== id);
  persistConfig("行业已移除");
}

function deleteSector(id) {
  const sector = allSectors().find((item) => item.id === id);
  if (!sector) return;
  appConfig.sectorIds = appConfig.sectorIds.filter((item) => item !== id);
  if (isCustomSector(id)) {
    appConfig.customSectors = appConfig.customSectors.filter((item) => item.id !== id);
  } else {
    appConfig.deletedSectorIds = uniqBy([...(appConfig.deletedSectorIds || []), id], (item) => item);
  }
  if (uiState.graphFocus === id) {
    uiState.graphFocus = appConfig.sectorIds[0] || allSectors()[0]?.id || "ai_compute";
  }
  persistConfig(`已删除行业：${sector.name}`);
}

function removeAsset(ticker) {
  appConfig.assetTickers = appConfig.assetTickers.filter((item) => item !== ticker);
  persistConfig("标的已移除");
}

function deleteAsset(ticker) {
  const asset = allAssets().find((item) => item.ticker === ticker);
  if (!asset) return;
  appConfig.assetTickers = appConfig.assetTickers.filter((item) => item !== ticker);
  if (isCustomAsset(ticker)) {
    appConfig.customAssets = appConfig.customAssets.filter((item) => item.ticker !== ticker);
  } else {
    appConfig.deletedAssetTickers = uniqBy(
      [...(appConfig.deletedAssetTickers || []), ticker.toUpperCase()],
      (item) => item,
    );
  }
  persistConfig(`已删除标的：${asset.name}`);
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

function spreadY(total, index, top = 120, bottom = 405) {
  if (total <= 1) return (top + bottom) / 2;
  return top + ((bottom - top) * index) / (total - 1);
}

function graphData() {
  const sector = currentData.sectors.find((item) => item.id === uiState.graphFocus) || currentData.sectors[0];
  if (!sector) return { nodes: [], edges: [], paths: [], source: "暂无本地行业配置" };
  const profile = sectorProfile(sector);
  const upstream = profile.upstream.slice(0, 4);
  const downstream = profile.downstream.slice(0, 4);
  const indicators = profile.indicators.slice(0, 3);
  const assets = relatedAssetsForSector(sector);
  const nodes = [
    ...upstream.map((label, index) => ({
      id: `upstream_${index}`,
      label,
      caption: "上游",
      x: 140,
      y: spreadY(upstream.length, index),
      color: "#0066cc",
      depth: 1,
    })),
    { id: "sector", label: sector.name, caption: horizonLabel(profile.horizon), x: 410, y: 260, color: "#007c78", depth: 0 },
    ...downstream.map((label, index) => ({
      id: `downstream_${index}`,
      label,
      caption: "下游",
      x: 675,
      y: spreadY(downstream.length, index),
      color: "#6d5bd0",
      depth: 1,
    })),
    ...assets.map((asset, index) => ({
      id: `asset_${index}`,
      label: asset.name,
      caption: asset.ticker,
      x: 990,
      y: spreadY(Math.max(assets.length, 1), index, 96, 424),
      color: asset.risk >= 65 ? "#c9342f" : "#248a3d",
      depth: 2,
    })),
    ...indicators.map((label, index) => ({
      id: `indicator_${index}`,
      label,
      caption: "指标",
      x: 410,
      y: 82 + index * 62,
      color: "#b26a00",
      depth: 3,
    })),
    { id: "risk", label: "风险变量", caption: "Risk", x: 410, y: 450, color: "#c9342f", depth: 3 },
  ];
  const edges = [
    ...upstream.map((_, index) => [`upstream_${index}`, "sector", 1]),
    ...downstream.map((_, index) => ["sector", `downstream_${index}`, 1]),
    ...assets.map((_, index) => ["sector", `asset_${index}`, 2]),
    ...indicators.map((_, index) => ["sector", `indicator_${index}`, 3]),
    ["sector", "risk", 3],
  ].filter((edge) => edge[2] <= uiState.graphDepth);
  const allowed = new Set(["sector"]);
  edges.forEach(([from, to]) => {
    allowed.add(from);
    allowed.add(to);
  });
  const paths = [
    `上游：${upstream.join(" / ") || "待补充"} → ${sector.name}`,
    `下游：${sector.name} → ${downstream.join(" / ") || "待补充"}`,
    `相关标的：${assets.map((asset) => `${asset.name}(${asset.ticker})`).join(" / ") || "待 LLM/DataProvider 筛选"}`,
    `观察指标：${indicators.join(" / ") || "待补充"}；风险：${profile.risks}`,
  ];
  return {
    nodes: nodes.filter((node) => allowed.has(node.id) && node.depth <= uiState.graphDepth),
    edges,
    paths,
    source: "来源：本地配置 + Demo Catalog；后续由 DataProvider/LLM enrichment 写入 KnowledgeGraphNode/Edge",
  };
}

function roundedRect(ctx, x, y, width, height, radius) {
  const r = Math.min(radius, width / 2, height / 2);
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + width - r, y);
  ctx.quadraticCurveTo(x + width, y, x + width, y + r);
  ctx.lineTo(x + width, y + height - r);
  ctx.quadraticCurveTo(x + width, y + height, x + width - r, y + height);
  ctx.lineTo(x + r, y + height);
  ctx.quadraticCurveTo(x, y + height, x, y + height - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
}

function ellipsizeText(ctx, text, maxWidth) {
  const value = String(text || "");
  if (ctx.measureText(value).width <= maxWidth) return value;
  let result = value;
  while (result.length > 1 && ctx.measureText(`${result}…`).width > maxWidth) {
    result = result.slice(0, -1);
  }
  return `${result}…`;
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
  const styles = getComputedStyle(document.documentElement);
  const textColor = styles.getPropertyValue("--text");
  const mutedColor = styles.getPropertyValue("--muted");
  const surfaceColor = styles.getPropertyValue("--surface-strong");

  ctx.lineWidth = 1.5;
  ctx.strokeStyle = styles.getPropertyValue("--line");
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
    const width = Math.max(108, Math.min(146, 132 * scaleX));
    const height = 54;
    const left = x - width / 2;
    const top = y - height / 2;
    roundedRect(ctx, left, top, width, height, 8);
    ctx.fillStyle = surfaceColor;
    ctx.fill();
    ctx.lineWidth = node.id === "sector" ? 2.2 : 1.4;
    ctx.strokeStyle = node.color;
    ctx.stroke();
    ctx.fillStyle = node.color;
    roundedRect(ctx, left, top, 5, height, 4);
    ctx.fill();
    ctx.textAlign = "left";
    ctx.font = "12px -apple-system, BlinkMacSystemFont, sans-serif";
    ctx.fillStyle = mutedColor;
    ctx.fillText(ellipsizeText(ctx, node.caption || "", width - 22), left + 14, top + 19);
    ctx.font = "600 13px -apple-system, BlinkMacSystemFont, sans-serif";
    ctx.fillStyle = textColor;
    ctx.fillText(ellipsizeText(ctx, node.label, width - 22), left + 14, top + 38);
  });

  const pathLabel = document.querySelector("#pathLabel");
  const pathList = document.querySelector("#pathList");
  const graphSource = document.querySelector("#graphSource");
  if (pathLabel) pathLabel.textContent = data.paths[0] || "暂无路径";
  if (graphSource) graphSource.textContent = data.source || "";
  if (pathList) {
    pathList.innerHTML = data.paths.map((path) => `<span>${esc(path)}</span>`).join("");
  }
}

function assetSentiment(asset) {
  if (Number.isFinite(Number(asset.sentiment))) return Number(asset.sentiment);
  return Math.max(42, Math.round((asset.impact + asset.trend - asset.risk) / 2));
}

function scoredAsset(asset) {
  const cached = intelligenceCache.get(asset.ticker);
  if (!cached || cached.status !== "ok") return asset;
  const snapshot = cached.snapshot;
  const scores = snapshot.scores || {};
  const events = (snapshot.events || []).slice(0, 5).map((event) => [
    event.source_published_at ? String(event.source_published_at).slice(5, 10) : event.event_type || "事件",
    event.title || "真实事件",
  ]);
  return {
    ...asset,
    impact: Number(scores.impact ?? asset.impact),
    trend: Number(scores.trend ?? asset.trend),
    sentiment: Number(scores.sentiment ?? assetSentiment(asset)),
    risk: Number(scores.risk ?? asset.risk),
    state: snapshot.position_state?.current_state || asset.state,
    evidence: `${snapshot.score_source || "real_signal"} · ${snapshot.source_status?.market_data || "data"}`,
    events: events.length ? events : asset.events,
    intelligence: snapshot,
  };
}

function ensureAssetIntelligence(asset, options = {}) {
  if (!asset?.ticker) return;
  const cached = intelligenceCache.get(asset.ticker);
  if (!options.force && cached && ["loading", "ok"].includes(cached.status)) return;
  intelligenceCache.set(asset.ticker, { status: "loading" });
  const params = new URLSearchParams({
    name: asset.name || "",
    sector: asset.sector || "",
    days: String(options.days || 90),
    include_news: "true",
    include_disclosures: "true",
  });
  apiGet(`/api/assets/${encodeURIComponent(asset.ticker)}/intelligence?${params.toString()}`)
    .then((snapshot) => {
      intelligenceCache.set(asset.ticker, { status: "ok", snapshot });
    })
    .catch((error) => {
      intelligenceCache.set(asset.ticker, { status: "error", error: error.message });
    })
    .finally(() => renderAll());
}

function intelligenceNote(asset) {
  const cached = intelligenceCache.get(asset.ticker);
  if (!cached) return "点击详情后自动拉取真实行情、新闻、公告和财报事件，并生成可追溯评分。";
  if (cached.status === "loading") return "正在生成真实数据评分闭环...";
  if (cached.status === "error") return `真实评分暂不可用：${cached.error}`;
  const snapshot = cached.snapshot;
  const status = snapshot.source_status || {};
  const primaryFailed = (status.errors || []).some((error) => error.source === "akshare_market_data");
  const errors = status.errors?.length ? `；部分源失败 ${status.errors.length} 项` : "";
  const fallback = primaryFailed && status.market_data === "sina_a_share_market_data" ? "（AkShare 主源失败，已切换新浪 A 股备用源）" : "";
  return `真实评分来源：${snapshot.score_source}；事件 ${status.event_count || 0} 条；信号 ${
    status.signal_count || 0
  } 条；行情 ${status.market_data || "unknown"}${fallback}${errors}`;
}

function chipList(items, emptyText = "待补充") {
  const values = listFromValue(items);
  if (!values.length) return `<span class="detail-chip muted">${esc(emptyText)}</span>`;
  return values.map((item) => `<span class="detail-chip">${esc(item)}</span>`).join("");
}

function metricTiles(items) {
  return `
    <div class="detail-metrics">
      ${items
        .map(
          ([label, value, note]) => `
            <article class="metric detail-metric">
              <span>${esc(label)}</span>
              <strong>${esc(value)}</strong>
              <small>${esc(note)}</small>
            </article>
          `,
        )
        .join("")}
    </div>
  `;
}

function compactAssetCard(asset) {
  return `
    <article class="watch-card interactive-card compact-asset-card" role="button" tabindex="0" data-action="open-asset-detail" data-id="${esc(asset.ticker)}" aria-label="查看 ${esc(asset.name)} 详情">
      <header>
        <h3>${esc(asset.name)} · ${esc(asset.ticker)}</h3>
        <span class="status ${statusClass(asset.state)}">${esc(asset.state)}</span>
      </header>
      ${scoreBars({ ...asset, sentiment: assetSentiment(asset) })}
      <p>${esc(asset.market)} · ${esc(asset.sector)} · ${esc(asset.evidence)}</p>
    </article>
  `;
}

function detailSectorFallback(asset) {
  return {
    id: `fallback_${slug(asset.sector)}`,
    name: asset.sector || "待分类行业",
    horizon: "medium",
    level: "medium",
    impact: asset.impact || 50,
    trend: asset.trend || 50,
    sentiment: assetSentiment(asset),
    risk: asset.risk || 45,
    driver: "该行业由标的配置推断，等待真实数据源和 LLM enrichment 完善",
    risks: "行业映射尚未验证，需补充公告、新闻、财报和产业链证据",
    indicators: ["公告事件", "成交量", "价格趋势", "风险评分"],
  };
}

function assetAnalysis(asset, sector, profile) {
  if (asset.intelligence) {
    const status = asset.intelligence.source_status || {};
    return `${asset.name} 当前已基于真实数据闭环生成评分：事件 ${status.event_count || 0} 条、信号 ${
      status.signal_count || 0
    } 条，行情来源 ${status.market_data || "unknown"}。当前状态为「${
      asset.state
    }」，评分来自行情、新闻、公告或财报事件的结构化证据，并可追溯到 Event / Signal；以上仅作为研究线索和风险提示，不构成投资建议。`;
  }
  const pressure =
    asset.risk >= 65
      ? "风险评分处于较高区间，应优先关注负面事件、监管变化、业绩兑现和流动性扰动。"
      : "风险评分未处于高位，但仍需跟踪估值、事件兑现和行业景气变化。";
  const trend =
    asset.trend >= 65
      ? "趋势评分偏强，说明当前事件和价格线索对既有方向有一定强化。"
      : "趋势评分仍在中性区间，更适合作为观察对象而非形成确定性结论。";
  return `${asset.name} 当前映射到 ${sector.name}，核心行业驱动为：${profile.driver} ${trend} ${pressure} 当前信息仍来自本地配置和 demo 信号，后续应接入真实行情、公告、财报和新闻事件进行验证。`;
}

function tradingReferences(asset, sector, profile) {
  const references = [];
  if (asset.risk >= 65) {
    references.push("风险优先：在风险评分回落、负面事件澄清或基本面证据改善前，仅适合保留在风险监控清单。");
  }
  if (asset.trend >= 68 && asset.risk < 60) {
    references.push("右侧观察：若价格趋势、成交量和行业指标继续同步改善，可作为增持观察变量，不构成增持指令。");
  }
  if (asset.impact >= 70 && asset.trend < 60) {
    references.push("左侧观察：事件影响较高但趋势尚未确认，适合等待财报、订单或价格指标进一步验证。");
  }
  if (asset.state.includes("减持")) {
    references.push("仓位管理：当前状态偏向风险收缩，应重点观察风险评分是否继续上升和行业景气是否走弱。");
  }
  references.push(`后续触发变量：${profile.indicators.slice(0, 3).join(" / ")}。`);
  references.push("以上仅为研究线索和仓位观察框架，不构成投资建议或买卖指令。");
  return references;
}

function hashString(value) {
  return String(value || "").split("").reduce((hash, char) => (hash * 31 + char.charCodeAt(0)) >>> 0, 7);
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function mockKlineData(asset, count = 48) {
  const seed = hashString(asset.ticker || asset.name);
  let close = 18 + (seed % 90) + asset.trend / 3;
  const drift = (asset.trend - asset.risk) / 700;
  return Array.from({ length: count }, (_, index) => {
    const wave = Math.sin((index + (seed % 11)) / 4) * 0.018;
    const shock = (((seed >> (index % 13)) % 9) - 4) / 500;
    const open = close;
    close = Math.max(1, open * (1 + drift + wave + shock));
    const high = Math.max(open, close) * (1 + 0.012 + ((seed + index) % 5) / 700);
    const low = Math.min(open, close) * (1 - 0.012 - ((seed + index * 3) % 5) / 700);
    return {
      label: `D-${count - index}`,
      open,
      close,
      high,
      low,
      volume: 0.8 + ((seed + index * 17) % 100) / 100,
    };
  });
}

function isoDateOffset(monthsBack = 0) {
  const date = new Date();
  date.setMonth(date.getMonth() - monthsBack);
  return date.toISOString().slice(0, 10);
}

function mapOhlcvRows(rows) {
  const parsed = (rows || [])
    .map((row) => ({
      label: String(row.trade_date || row.date || ""),
      open: Number(row.open),
      close: Number(row.close),
      high: Number(row.high),
      low: Number(row.low),
      volumeRaw: Number(row.volume || 0),
    }))
    .filter((row) => Number.isFinite(row.open) && Number.isFinite(row.close) && Number.isFinite(row.high) && Number.isFinite(row.low))
    .sort((a, b) => a.label.localeCompare(b.label));
  const maxVolume = Math.max(...parsed.map((row) => row.volumeRaw), 1);
  return parsed.slice(-72).map((row) => ({
    label: row.label,
    open: row.open,
    close: row.close,
    high: row.high,
    low: row.low,
    volume: Math.max(0.2, (row.volumeRaw / maxVolume) * 2.2),
  }));
}

function ensureRealKline(asset) {
  if (!asset?.ticker || marketDataCache.has(asset.ticker)) return;
  marketDataCache.set(asset.ticker, { status: "loading", bars: [], source: "akshare" });
  const params = new URLSearchParams({
    start: isoDateOffset(12),
    end: isoDateOffset(0),
  });
  apiGet(`/api/assets/${encodeURIComponent(asset.ticker)}/ohlcv?${params.toString()}`)
    .then((payload) => {
      const bars = mapOhlcvRows(payload.rows);
      marketDataCache.set(asset.ticker, {
        status: bars.length ? "ok" : "empty",
        bars,
        source: payload.source || "akshare",
      });
    })
    .catch((error) => {
      marketDataCache.set(asset.ticker, {
        status: "error",
        bars: [],
        source: "demo_fallback",
        error: error.message,
      });
    })
    .finally(() => requestAnimationFrame(drawDetailCharts));
}

function drawKlineChart(canvas) {
  const asset = findAssetByTicker(canvas.dataset.ticker);
  if (!asset) return;
  ensureRealKline(asset);
  const ctx = canvas.getContext("2d");
  const ratio = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  if (rect.width < 10 || rect.height < 10) return;
  canvas.width = Math.round(rect.width * ratio);
  canvas.height = Math.round(rect.height * ratio);
  ctx.scale(ratio, ratio);
  ctx.clearRect(0, 0, rect.width, rect.height);

  const styles = getComputedStyle(document.documentElement);
  const line = styles.getPropertyValue("--line");
  const text = styles.getPropertyValue("--muted");
  const green = styles.getPropertyValue("--green");
  const red = styles.getPropertyValue("--red");
  const blue = styles.getPropertyValue("--blue");
  const cached = marketDataCache.get(asset.ticker);
  const realBars = cached?.bars?.length ? cached.bars : null;
  const bars = realBars || mockKlineData(asset);
  const top = 18;
  const bottom = rect.height - 42;
  const left = 42;
  const right = rect.width - 12;
  const chartWidth = right - left;
  const chartHeight = bottom - top;
  const max = Math.max(...bars.map((bar) => bar.high));
  const min = Math.min(...bars.map((bar) => bar.low));
  const range = max - min || 1;
  const y = (value) => top + ((max - value) / range) * chartHeight;

  ctx.strokeStyle = line;
  ctx.lineWidth = 1;
  [0, 0.25, 0.5, 0.75, 1].forEach((step) => {
    const yy = top + chartHeight * step;
    ctx.beginPath();
    ctx.moveTo(left, yy);
    ctx.lineTo(right, yy);
    ctx.stroke();
  });

  ctx.fillStyle = text;
  ctx.font = "11px -apple-system, BlinkMacSystemFont, sans-serif";
  ctx.textAlign = "right";
  [max, (max + min) / 2, min].forEach((value) => {
    ctx.fillText(value.toFixed(1), left - 8, y(value) + 4);
  });

  const slot = chartWidth / bars.length;
  const candleWidth = clamp(slot * 0.58, 3, 9);
  bars.forEach((bar, index) => {
    const x = left + index * slot + slot / 2;
    const up = bar.close >= bar.open;
    ctx.strokeStyle = up ? green : red;
    ctx.fillStyle = up ? green : red;
    ctx.beginPath();
    ctx.moveTo(x, y(bar.high));
    ctx.lineTo(x, y(bar.low));
    ctx.stroke();
    const bodyTop = y(Math.max(bar.open, bar.close));
    const bodyHeight = Math.max(2, Math.abs(y(bar.open) - y(bar.close)));
    ctx.fillRect(x - candleWidth / 2, bodyTop, candleWidth, bodyHeight);
    const volumeHeight = Math.min(26, bar.volume * 12);
    ctx.globalAlpha = 0.18;
    ctx.fillRect(x - candleWidth / 2, rect.height - 12 - volumeHeight, candleWidth, volumeHeight);
    ctx.globalAlpha = 1;
  });

  ctx.strokeStyle = blue;
  ctx.lineWidth = 1.6;
  ctx.beginPath();
  bars.forEach((bar, index) => {
    const x = left + index * slot + slot / 2;
    const yy = y(bar.close);
    if (index === 0) ctx.moveTo(x, yy);
    else ctx.lineTo(x, yy);
  });
  ctx.stroke();

  ctx.fillStyle = text;
  ctx.textAlign = "left";
  ctx.font = "11px -apple-system, BlinkMacSystemFont, sans-serif";
  const sourceLabel =
    cached?.status === "ok"
      ? `Real OHLCV · ${cached.source}`
      : cached?.status === "loading"
        ? "Loading real OHLCV..."
        : asset.market === "US"
          ? "US market data adapter pending"
          : "Demo fallback · Real provider unavailable";
  ctx.fillText(sourceLabel, left, rect.height - 14);
}

function drawDetailCharts() {
  document.querySelectorAll(".kline-chart").forEach((canvas) => drawKlineChart(canvas));
}

function renderSectorDetail(sector) {
  const profile = sectorProfile(sector);
  const assets = assetsForSectorDetail(sector);
  return `
    <section class="panel detail-hero">
      <div class="detail-topline">
        <button class="text-button" data-action="back-detail">返回</button>
        <span>Sector Detail · ${horizonLabel(profile.horizon)}</span>
      </div>
      <div class="detail-title-row">
        <div>
          <h2>${esc(sector.name)}</h2>
          <p>${esc(profile.driver)}</p>
        </div>
        <span class="pill ${esc(sector.level)}">${horizonLabel(profile.horizon)}</span>
      </div>
      ${metricTiles([
        ["相关标的", assets.length, "产业链映射"],
        ["Impact", sector.impact, "行业影响"],
        ["Trend", sector.trend, "趋势评分"],
        ["Risk", sector.risk, "风险评分"],
      ])}
    </section>

    <section class="detail-grid">
      <div class="panel detail-section">
        <div class="panel-head"><h2>上下游结构</h2><span>Knowledge Graph</span></div>
        <div class="detail-block"><strong>上游</strong><div class="detail-chip-row">${chipList(profile.upstream)}</div></div>
        <div class="detail-block"><strong>下游</strong><div class="detail-chip-row">${chipList(profile.downstream)}</div></div>
      </div>
      <div class="panel detail-section">
        <div class="panel-head"><h2>观察变量</h2><span>Research Variables</span></div>
        <div class="detail-chip-row">${chipList(profile.indicators)}</div>
        <p>${esc(profile.risks)}</p>
      </div>
    </section>

    <section class="panel">
      <div class="panel-head">
        <h2>行业相关标的</h2>
        <span>${assets.length} assets</span>
      </div>
      <div class="detail-asset-grid">
        ${assets.map(compactAssetCard).join("") || emptyState("暂无相关标的，可在配置页添加", "assets")}
      </div>
    </section>
  `;
}

function renderAssetDetail(asset) {
  ensureAssetIntelligence(asset);
  asset = scoredAsset(asset);
  const sector = findSectorByName(asset.sector) || detailSectorFallback(asset);
  const profile = sectorProfile(sector);
  const events = asset.events || [];
  const sectorAction = findSectorByName(asset.sector)
    ? `<button class="text-button" data-action="open-sector-detail" data-id="${esc(sector.id)}">查看行业</button>`
    : "";
  return `
    <section class="panel detail-hero">
      <div class="detail-topline">
        <button class="text-button" data-action="back-detail">返回</button>
        <span>Asset Detail · ${esc(asset.market)}</span>
      </div>
      <div class="detail-title-row">
        <div>
          <h2>${esc(asset.name)} · ${esc(asset.ticker)}</h2>
          <p>${esc(asset.sector)} · ${esc(asset.evidence)}</p>
        </div>
        <div class="detail-actions">
          ${sectorAction}
          <span class="status ${statusClass(asset.state)}">${esc(asset.state)}</span>
        </div>
      </div>
      ${metricTiles([
        ["Impact", asset.impact, "事件影响"],
        ["Trend", asset.trend, "趋势强化"],
        ["Risk", asset.risk, "风险压力"],
        ["Sentiment", assetSentiment(asset), "情绪估计"],
      ])}
    </section>

    <section class="detail-layout">
      <div class="panel chart-panel">
        <div class="panel-head">
          <h2>K线图</h2>
          <span>Real OHLCV first</span>
        </div>
        <canvas class="kline-chart" data-ticker="${esc(asset.ticker)}" width="900" height="360" aria-label="${esc(asset.name)} K线图"></canvas>
        <p class="graph-source">优先调用 MarketDataProvider / AkShare 真实行情；不可用时使用本地演示数据兜底。</p>
        <p class="graph-source">${esc(intelligenceNote(asset))}</p>
      </div>

      <aside class="panel detail-section">
        <div class="panel-head"><h2>观察指标</h2><span>${esc(sector.name)}</span></div>
        <div class="detail-chip-row">${chipList(profile.indicators)}</div>
        <div class="detail-block"><strong>风险</strong><p>${esc(profile.risks)}</p></div>
      </aside>
    </section>

    <section class="detail-grid">
      <div class="panel detail-section">
        <div class="panel-head"><h2>详细分析</h2><span>AI-assisted</span></div>
        <p>${esc(assetAnalysis(asset, sector, profile))}</p>
        <div class="timeline">
          ${events
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
      </div>
      <div class="panel detail-section">
        <div class="panel-head"><h2>交易思路参考</h2><span>非指令</span></div>
        <ul class="reference-list">
          ${tradingReferences(asset, sector, profile).map((item) => `<li>${esc(item)}</li>`).join("")}
        </ul>
      </div>
    </section>
  `;
}

function renderDetailView() {
  const target = document.querySelector("#detailContent");
  if (!target) return;
  if (uiState.detail.type === "sector") {
    const sector = findSectorById(uiState.detail.id);
    target.innerHTML = sector ? renderSectorDetail(sector) : emptyState("未找到行业详情", "sectors");
  } else if (uiState.detail.type === "asset") {
    const asset = findAssetByTicker(uiState.detail.id);
    target.innerHTML = asset ? renderAssetDetail(asset) : emptyState("未找到标的详情", "assets");
  } else {
    target.innerHTML = emptyState("请选择行业或标的", "sectors");
  }
  requestAnimationFrame(drawDetailCharts);
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
}

function renderSectorConfig() {
  const catalogItems = allSectors();
  return `
    <div class="config-grid">
      <form class="config-form" id="sectorForm">
        <h3>新增行业 / 板块</h3>
        <div class="form-row two">
          <label>名称<input name="name" required placeholder="例如：机器人"></label>
          <label>周期<select name="horizon"><option value="">自动</option><option value="long">长期</option><option value="medium">中期</option><option value="short">短期</option></select></label>
        </div>
        <label>核心驱动<input name="driver" placeholder="产业趋势、政策、订单、价格"></label>
        <label>观察指标<input name="indicators" placeholder="政策，订单，价格"></label>
        <div class="form-row two">
          <label>上游行业<input name="upstream" placeholder="例如：材料，设备，核心零部件"></label>
          <label>下游行业<input name="downstream" placeholder="例如：终端应用，渠道客户"></label>
        </div>
        <label>相关标的<input name="relatedTickers" placeholder="688525.SH，603986.SH"></label>
        <div class="form-actions">
          <button class="primary-button" type="submit">添加行业</button>
          <button class="text-button" type="button" data-action="assist-sector-form">AI 补全</button>
        </div>
      </form>
      <div class="config-list">
        <h3>可选行业</h3>
        ${catalogItems
          .map((sector) => {
            const added = appConfig.sectorIds.includes(sector.id);
            const profile = sectorProfile(sector);
            return `
              <article class="config-item">
                <div>
                  <strong>${esc(sector.name)}</strong>
                  <span>${horizonLabel(profile.horizon)} · ${esc(profile.upstream.slice(0, 2).join(" / "))} → ${esc(profile.downstream.slice(0, 2).join(" / "))}</span>
                </div>
                <div class="item-actions">
                  <button class="text-button" data-action="${added ? "remove-sector" : "add-sector"}" data-id="${esc(sector.id)}">${added ? "移除" : "添加"}</button>
                  <button class="text-button danger" data-action="delete-sector" data-id="${esc(sector.id)}">删除</button>
                </div>
              </article>
            `;
          })
          .join("")}
      </div>
    </div>
  `;
}

function renderAssetConfig() {
  const catalogItems = allAssets();
  return `
    <div class="asset-config-layout">
      <form class="config-form compact-config-form" id="assetForm">
        <h3>新增关注标的</h3>
        <div class="form-row asset-form-row">
          <label>名称<input name="name" required placeholder="例如：中芯国际"></label>
          <label>代码<input name="ticker" placeholder="例如：688981.SH"></label>
          <label>市场<select name="market"><option value="">自动</option><option>A-share</option><option>HK</option><option>US</option><option>ETF</option></select></label>
          <label>行业<input name="sector" placeholder="例如：半导体设备"></label>
          <div class="form-actions asset-form-actions">
            <button class="primary-button" type="submit">添加标的</button>
            <button class="text-button" type="button" data-action="assist-asset-form">AI 补全</button>
          </div>
        </div>
      </form>
      <div class="config-list asset-config-list">
        <div class="config-list-head">
          <h3>可选标的</h3>
          <span>${catalogItems.length} 个</span>
        </div>
        ${catalogItems
          .map((asset) => {
            const added = appConfig.assetTickers.includes(asset.ticker);
            return `
              <article class="config-item">
                <div>
                  <strong>${esc(asset.name)} · ${esc(asset.ticker)}</strong>
                  <span>${esc(asset.market)} · ${esc(asset.sector)} · Risk ${esc(asset.risk)}</span>
                </div>
                <div class="item-actions">
                  <button class="text-button" data-action="${added ? "remove-asset" : "add-asset"}" data-id="${esc(asset.ticker)}">${added ? "移除" : "添加"}</button>
                  <button class="text-button danger" data-action="delete-asset" data-id="${esc(asset.ticker)}">删除</button>
                </div>
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
  renderDetailView();
  renderGraphOnly();
}

function updateCommandCenterVisibility(viewId) {
  const commandCenter = document.querySelector(".command-center");
  if (!commandCenter) return;
  const shouldHide = commandHiddenViews.has(viewId);
  commandCenter.hidden = shouldHide;
  commandCenter.classList.toggle("is-hidden", shouldHide);
  commandCenter.setAttribute("aria-hidden", shouldHide ? "true" : "false");
  if (shouldHide) setSearchResultsVisible(document.querySelector("#searchResults"), false);
}

function switchView(viewId) {
  uiState.activeView = viewId;
  if (viewId !== "detail") {
    uiState.detail.type = null;
    uiState.detail.id = null;
    uiState.detail.fromView = viewId;
  }
  document.querySelectorAll(".nav-item").forEach((button) => {
    button.classList.toggle("active", button.dataset.view === viewId);
  });
  document.querySelectorAll(".view").forEach((view) => {
    view.classList.toggle("active", view.id === viewId);
  });
  updateCommandCenterVisibility(viewId);
  if (viewId === "graph") renderGraphOnly();
  if (viewId === "detail") renderDetailView();
}

function openConfig(tab = "sectors") {
  uiState.configTab = tab;
  document.querySelectorAll("#configTabs button").forEach((button) => {
    button.classList.toggle("active", button.dataset.configTab === tab);
  });
  switchView("settings");
  renderConfigPane();
}

function openSectorDetail(id) {
  const sector = findSectorById(id);
  if (!sector) return;
  uiState.detail = {
    type: "sector",
    id,
    fromView: uiState.activeView === "detail" ? uiState.detail.fromView : uiState.activeView,
  };
  uiState.graphFocus = id;
  switchView("detail");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function openAssetDetail(ticker) {
  const asset = findAssetByTicker(ticker);
  if (!asset) return;
  uiState.detail = {
    type: "asset",
    id: ticker,
    fromView: uiState.activeView === "detail" ? uiState.detail.fromView : uiState.activeView,
  };
  switchView("detail");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function backFromDetail() {
  const fromView = uiState.detail.fromView || "dashboard";
  switchView(fromView);
}

function showToast(message) {
  const toast = document.querySelector("#toast");
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 1700);
}

async function assistSectorForm(form) {
  if (!form) return;
  const name = form.elements.name?.value.trim();
  if (!name) {
    showToast("请先填写行业名称");
    form.elements.name?.focus();
    return;
  }
  const { provider, result } = await requestLlmAssistance("sector", { name });
  upsertValidatedAssets(result.validatedAssets, name);
  if (!form.elements.horizon.value) form.elements.horizon.value = result.horizon || "medium";
  form.elements.driver.value = form.elements.driver.value || result.driver || "";
  form.elements.indicators.value = form.elements.indicators.value || (result.indicators || []).join("，");
  form.elements.upstream.value = form.elements.upstream.value || (result.upstream || []).join("，");
  form.elements.downstream.value = form.elements.downstream.value || (result.downstream || []).join("，");
  const relatedTickers = (result.relatedTickers || []).join("，");
  if (relatedTickers) form.elements.relatedTickers.value = relatedTickers;
  form.dataset.assistRisks = result.risks || "";
  form.dataset.assistSource = provider;
  showToast(`${provider} 已生成行业画像草稿`);
}

async function assistAssetForm(form) {
  if (!form) return;
  const name = form.elements.name?.value.trim();
  if (!name) {
    showToast("请先填写标的名称");
    form.elements.name?.focus();
    return;
  }
  const { provider, result } = await requestLlmAssistance("asset", {
    name,
    ticker: form.elements.ticker?.value,
    market: form.elements.market?.value,
    sector: form.elements.sector?.value,
  });
  form.elements.ticker.value = form.elements.ticker.value || result.ticker || "";
  form.elements.market.value = form.elements.market.value || result.market || "A-share";
  form.elements.sector.value = form.elements.sector.value || result.sector || "";
  upsertValidatedAssets(result.validatedAssets, result.sector || form.elements.sector?.value || "待分类");
  showToast(`${provider} 已生成标的配置草稿`);
}

function createSector(form) {
  const data = new FormData(form);
  const name = String(data.get("name") || "").trim();
  if (!name) return;
  const assist = localLlmAssist("sector", { name });
  const id = `custom_${slug(name)}_${Date.now().toString(36)}`;
  const sector = {
    id,
    name,
    horizon: String(data.get("horizon") || assist.horizon || "medium"),
    level: "medium",
    impact: 55,
    trend: 50,
    sentiment: 50,
    risk: 45,
    driver: String(data.get("driver") || assist.driver || "用户自定义研究方向").trim(),
    risks: form.dataset.assistRisks || assist.risks || "待补充",
    indicators: listFromValue(data.get("indicators")).length
      ? listFromValue(data.get("indicators")).slice(0, 5)
      : assist.indicators.slice(0, 5),
    upstream: listFromValue(data.get("upstream")).length
      ? listFromValue(data.get("upstream")).slice(0, 5)
      : assist.upstream.slice(0, 5),
    downstream: listFromValue(data.get("downstream")).length
      ? listFromValue(data.get("downstream")).slice(0, 5)
      : assist.downstream.slice(0, 5),
    relatedTickers: listFromValue(data.get("relatedTickers")).length
      ? listFromValue(data.get("relatedTickers")).slice(0, 80)
      : assist.relatedTickers.slice(0, 80),
    source: form.dataset.assistSource ? "deepseek_validated_assist" : "manual_or_llm_assist",
  };
  if (!sector.indicators.length) sector.indicators = ["政策", "订单", "价格"];
  appConfig.customSectors.push(sector);
  appConfig.sectorIds.push(id);
  uiState.graphFocus = id;
  delete form.dataset.assistRisks;
  delete form.dataset.assistSource;
  form.reset();
  persistConfig(`已创建行业：${name}`);
}

function createAsset(form) {
  const data = new FormData(form);
  const name = String(data.get("name") || "").trim();
  if (!name) return;
  const draft = inferAssetDraft(name, {
    ticker: data.get("ticker"),
    market: data.get("market"),
    sector: data.get("sector"),
  });
  const ticker =
    String(data.get("ticker") || draft.ticker || "").trim().toUpperCase() ||
    `LOCAL.${slug(name).toUpperCase() || Date.now().toString(36).toUpperCase()}`;
  const sector = String(data.get("sector") || draft.sector || "待分类").trim();
  const asset = {
    ticker,
    name,
    market: String(data.get("market") || draft.market || "A-share"),
    sector,
    state: draft.state || "观察",
    impact: draft.impact || 50,
    trend: draft.trend || 50,
    risk: draft.risk || 45,
    evidence: draft.evidence || "manual_config",
    events: draft.events || [["配置", "用户手动添加关注标的"]],
  };
  appConfig.customAssets = appConfig.customAssets.filter((item) => item.ticker !== ticker);
  appConfig.customAssets.push(asset);
  if (!appConfig.assetTickers.includes(ticker)) appConfig.assetTickers.push(ticker);
  form.reset();
  persistConfig(`已创建标的：${name}`);
  ensureAssetIntelligence(asset, { force: true });
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

function bindEvents() {
  document.querySelector("#commandSearch").addEventListener("input", (event) => {
    uiState.query = event.target.value;
    renderAll();
    scheduleRemoteAssetSearch(uiState.query);
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
    currentData.assets.slice(0, 12).forEach((asset) => ensureAssetIntelligence(asset, { force: true }));
    renderAll();
    showToast("正在刷新真实情报评分");
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
    if (action === "open-sector-detail") openSectorDetail(id);
    if (action === "open-asset-detail") openAssetDetail(id);
    if (action === "back-detail") backFromDetail();
    if (action === "add-sector") addSector(id);
    if (action === "remove-sector") removeSector(id);
    if (action === "delete-sector") deleteSector(id);
    if (action === "add-asset") addAsset(id);
    if (action === "remove-asset") removeAsset(id);
    if (action === "delete-asset") deleteAsset(id);
    if (action === "toggle-email") toggleEmail(id);
    if (action === "delete-email") deleteEmail(id);
    if (action === "toggle-provider") toggleProvider(id);
    if (action === "toggle-llm") toggleLlm(id);
    if (action === "assist-sector-form") assistSectorForm(button.closest("form"));
    if (action === "assist-asset-form") assistAssetForm(button.closest("form"));
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

  document.addEventListener("keydown", (event) => {
    if (!["Enter", " "].includes(event.key)) return;
    const card = event.target.closest(".interactive-card[data-action]");
    if (!card) return;
    event.preventDefault();
    card.click();
  });

  document.addEventListener("click", (event) => {
    if (!event.target.closest(".search-shell")) {
      setSearchResultsVisible(document.querySelector("#searchResults"), false);
    }
  });

  document.querySelectorAll(".nav-item").forEach((button) => {
    button.addEventListener("click", () => switchView(button.dataset.view));
  });

  window.addEventListener("resize", () => {
    drawGraph();
    drawDetailCharts();
  });
}

async function boot() {
  bindEvents();
  renderAll();
  updateCommandCenterVisibility(uiState.activeView);
  setInterval(() => {
    document.querySelector("#clock").textContent = new Date().toLocaleTimeString("zh-CN", {
      hour: "2-digit",
      minute: "2-digit",
    });
  }, 1000);
}

boot();
