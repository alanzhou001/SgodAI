# SgodAI Market Radar PRD

## 1. 产品名称

**SgodAI Market Radar**。

SgodAI Market Radar 是一款本地优先的 AI 股市信息情报与投研辅助系统。系统面向持续研究市场、行业、公司、产业链、政策、公告、新闻、情绪和风险事件的用户，帮助用户把分散信息转化为结构化情报资产。

系统不构成投资建议，不提供自动交易功能，不直接输出买入或卖出指令。所有内容仅作为研究线索、信息整理、风险提示和仓位观察参考。

## 2. 产品定位

SgodAI Market Radar 的定位是：

```text
Local-first AI-assisted Market Intelligence & Research Copilot
```

它不是财经新闻聚合器，不是短线荐股产品，也不是自动交易系统。产品围绕以下目标构建：

- 信息聚集与清洗
- 事件识别与结构化
- 行业、个股、产业链和海外映射联动
- 多维事件评分
- 仓位窗口辅助识别
- 风险提示与异常提醒
- 日报、周报和专题报告生成
- 个人或团队研究数据沉淀

核心问题：

1. 长期、中期、短期有哪些值得持续关注的行业？
2. 每个行业有哪些代表性标的与上下游节点？
3. 用户关注标的近期发生了什么？
4. 哪些事件真正重要，哪些只是噪音？
5. 哪些行业或标的出现趋势、情绪或风险变化？
6. 哪些标的进入建仓观察、增持观察、减持观察或风险预警状态？
7. 哪些信息需要进入日报、周报或即时异常提醒？
8. 每个判断背后的证据来源、评分依据和风险因素是什么？

## 3. 适用人群

### 个人投资者

适合希望系统化跟踪市场信息、行业变化和自选股动态的个人投资者。重点需求包括盘前/盘后报告、自选股公告与新闻跟踪、异常波动识别、风险提示和仓位观察参考。

### 股票及行业研究员

适合买方、卖方或产业研究人员长期维护行业、公司和产业链研究对象。重点需求包括行业景气跟踪、政策和供需变化监控、产业链影响路径识别、事件历史沉淀和研究报告生成。

### 量化投资研究人员

适合需要构建事件数据库、情绪数据库和另类数据特征的用户。重点需求包括事件标准化、Impact/Trend/Sentiment/Risk 评分、事件研究、因子构建和回测数据沉淀。

### VC/PE 投资分析师

适合关注产业趋势、上市公司映射、海外龙头和行业景气变化的一级市场投资分析师。重点需求包括趋势识别、上市公司映射、供应链传导路径和行业主题储备。

### 金融专业学生及研究人员

适合金融、经济、产业研究方向的学生和研究人员。重点需求包括学习市场信息结构化、事件研究、行业分析和研究型数据库建设。

### 长期跟踪行业和公司的投资者

适合有固定研究方向、长期观察特定行业或公司的用户。重点需求包括自定义研究范围、长期事件积累、定期报告、异常提醒和本地研究知识库。

## 4. 核心功能

### 4.1 Sector Radar 行业雷达

行业雷达用于识别、跟踪和结构化展示行业机会与风险变化。行业观察周期分为：

- 长期行业：1 至 3 年，关注产业趋势、技术变革、政策扶持、资本开支周期、国产替代、全球供需变化。
- 中期行业：1 至 6 个月，关注景气改善、价格变化、订单改善、库存周期、政策落地、盈利修复。
- 短期行业：1 天至 1 个月，关注事件驱动、政策催化、突发新闻、价格异动、海外映射和主题发酵。

行业输出字段：

- 行业名称
- 观察周期
- 推荐关注原因
- 当前产业周期位置
- 核心驱动因素
- 主要风险
- 产业链上下游变化
- 政策变化
- 商品价格或关键指标变化
- 海外映射公司
- A 股、港股、美股代表公司
- 当前关注等级
- 最近异常事件
- 后续重点观察指标

### 4.2 Watchlist Intelligence 关注标的情报中心

用户可维护关注对象：

- 个股、ETF、指数
- 行业板块、概念板块、产业链节点
- 海外映射公司
- 商品价格指标、宏观变量、政策变量

系统持续跟踪：

- 行情趋势、成交量、换手率、波动率
- 公告、财报、业绩预告、新闻、研报摘要
- 行业动态、政策变化、海外映射
- 市场情绪、风险事件、资金行为
- 解禁、减持、回购、并购等资本事件

自动生成：

- 盘前报告、盘后报告、周报
- 个股事件摘要、行业变化摘要
- 重大异常提醒、风险提示
- 下一阶段观察清单

### 4.3 Position Window Engine 仓位窗口辅助识别

仓位窗口引擎不输出买入、卖出指令。它根据多维信号识别观察状态，帮助用户组织下一步研究问题。

输入因素：

- 趋势、估值、成交量、资金行为
- 行业景气、公告、财报、产业链催化
- 政策变化、市场情绪、风险事件
- 海外映射、历史波动区间
- 事件评分、个股与行业相对强弱

输出状态：

- 不关注
- 观察
- 左侧建仓观察
- 右侧增持观察
- 持有跟踪
- 减持观察
- 风险预警

每个状态必须附带：

- 状态触发原因
- 支撑因素
- 风险因素
- 需要继续观察的变量
- 触发状态变化的条件
- 相关事件列表
- 相关行业变化
- 相关公告和新闻
- 交易思路参考
- 免责声明

### 4.4 Knowledge Graph 产业链知识图谱

知识图谱建立行业、产业链、上市公司、海外映射、商品价格、政策和事件之间的关系。

```text
行业 -> 产业链 -> 上市公司 -> 海外映射 -> 商品价格 -> 政策 -> 事件
```

主要能力：

- 行业节点管理
- 产业链节点管理
- 公司映射关系管理
- 海外龙头映射
- 商品价格映射
- 政策映射
- 事件映射
- 新闻与公告挂载
- 影响路径展示
- 上下游传导分析
- 手动补充和编辑关系

目标是帮助用户从“看到一条新闻”升级为“理解这条新闻可能影响哪些行业、哪些公司、哪些风险和哪些机会”。

### 4.5 Event Intelligence 智能事件分析

系统将非结构化信息转化为结构化事件卡片。

事件类型包括：

- 财报、业绩预告、公司公告
- 并购、回购、减持、解禁
- 政策、行业价格变化、海外事件
- 股价异动、成交量异动、资金异动
- 供应链事件、监管事件、舆情事件

每个事件计算：

- Impact Score：影响力评分
- Trend Score：趋势评分
- Sentiment Score：情绪评分
- Risk Score：风险评分

事件卡片字段：

- 事件标题、来源、类型
- 关联行业、公司、产业链节点
- 四类评分
- 简要摘要
- 可能影响路径
- 风险提示
- 是否触发提醒
- 是否进入日报或周报
- 是否影响仓位窗口状态

### 4.6 日报 / 周报自动生成

日报结构：

```text
市场概览
重点行业
重点个股
重要公告
产业链变化
异常信号
风险提示
下阶段重点关注列表
```

报告类型：

- 盘前报告、盘后报告、周度总结
- 行业专题简报、个股跟踪报告
- 重大事件报告、风险事件报告
- 异常值提醒报告

触发规则：

- 固定时间推送盘前、盘后和周报
- 异常值超过阈值即时推送
- 关注标的出现重大公告即时推送
- 行业雷达评分显著变化推送
- 仓位窗口状态变化推送

### 4.7 目标邮箱管理

用户可添加多个报告接收邮箱，并为每个邮箱配置接收范围。

邮箱支持：

- 盘前报告
- 盘后报告
- 周报
- 重大事件提醒
- 异常值提醒
- 风险预警
- 仓位窗口状态变化提醒

接口：

```text
create_email_target
update_email_target
delete_email_target
enable_email_target
disable_email_target
send_test_email
list_email_targets
get_email_delivery_logs
retry_failed_email
```

### 4.8 Signal Database 信号数据库

保存内容：

- 新闻、公告、财报、业绩预告
- 情绪、趋势、行业变化、产业链变化
- 事件评分、个股状态变化、行业状态变化
- 异常提醒记录、报告历史、用户关注列表变化

用途：

- 事件研究
- 量化研究
- 策略回测
- 行业复盘
- 个股复盘
- 风险事件分析
- 情绪与价格关系分析
- 研究过程沉淀

### 4.9 投研工作台

工作台采用偏机构投研风格，避免资讯流和短线荐股风格。

核心视图：

- 市场总览仪表盘
- 行业雷达矩阵
- 个股关注列表
- 仓位窗口状态表
- 产业链知识图谱
- 事件时间线
- 异常值监控面板
- 情绪趋势图
- 风险热力图
- 行业景气变化图
- 公司事件日历
- 报告中心
- 信号数据库查询页
- 通知目标管理页
- 数据源管理页
- AI 模型接入配置页
- 本地 Agent 接入配置页

## 5. 创新优势

### Local-first 本地优先

关注列表、研究数据、历史事件、评分结果和报告记录默认保存在本地。优势包括隐私保护、研究数据沉淀、离线可读、适合个人和团队长期研究。

### AI 辅助投研，而非新闻聚合

AI 参与信息清洗、事件识别、归因分析、风险识别、产业链影响分析和报告生成。但底层事实、状态、评分和推送必须由 Core Engine 负责。

### 行业 + 个股 + 产业链 + 海外映射四层联动

系统通过图谱和事件映射理解影响路径：

```text
海外龙头异动 -> 产业链变化 -> 国内相关公司 -> 行业景气变化 -> 个股事件评分变化 -> 仓位窗口状态变化
```

### 多源信息融合

系统整合行情、公告、新闻、政策、财报、产业链、商品价格、海外市场、情绪、资金和风险事件，最终进入统一事件系统、评分系统、报告系统和信号数据库。

### 可审计的仓位窗口

仓位窗口状态必须可复现、可审计，并能追溯到具体事件、评分、行情数据和规则条件。

### 可扩展架构

系统可扩展至新数据源、新行业插件、知识图谱、向量数据库、本地 LLM、MCP 工具、量化研究、团队协作和 API 服务。

## 6. 系统模块划分

```text
User Interface
Web UI / CLI / Email / Telegram / QQ / Webhook
        ↓
Agent Copilot Layer
Research Assistant / Report Agent / Alert Agent / Coordinator Agent
        ↓
Core Service Layer
Data Service / Event Service / Signal Service / Position Window Engine /
Report Service / Notification Service / Knowledge Graph Service
        ↓
Data & State Layer
SQLite / PostgreSQL / Event DB / Signal DB / Report DB / Knowledge Graph /
Vector Store
        ↓
Data Provider Layer
Market Data / Announcements / News / Financial Reports / Policy /
Industry Data / Commodity Prices / Overseas Market / Sentiment
```

MVP 优先级：

1. DataProvider interface
2. Watchlist management
3. Event database
4. Signal scoring engine
5. Position window engine
6. Report composer
7. Email notification
8. Single AI Research Assistant

## 7. 数据对象设计

核心对象：

- Asset
- Sector
- Watchlist
- Event
- Signal
- Report
- NotificationTarget
- EmailTarget
- DataSource
- ModelProvider
- AgentProvider
- KnowledgeGraphNode
- KnowledgeGraphEdge
- PositionWindowState
- DeliveryLog

关系：

```text
Asset belongs to Sector
Asset can belong to Watchlist
Event links to Asset / Sector / KnowledgeGraphNode
Signal links to Event / Asset / Sector
Report aggregates Event / Signal / PositionWindowState
NotificationTarget receives Report / Alert
PositionWindowState links to Asset and Signal
```

## 8. 数据源接口设计

预留数据源：

- MarketDataProvider
- AnnouncementProvider
- NewsProvider
- FinancialReportProvider
- PolicyProvider
- IndustryDataProvider
- CommodityPriceProvider
- OverseasMarketProvider
- SentimentProvider
- ResearchReportProvider
- CalendarProvider

接入方式：

- REST API
- RSS
- Web scraping adapter
- 本地 CSV / Excel 导入
- 数据库导入
- 手动录入
- Webhook
- MCP 工具接口

所有数据进入系统前必须标准化为内部对象：Asset、Event、Signal、Report、Sector、IndustryNode、KnowledgeGraphEdge、NotificationTarget、DataSource、ModelProvider、AgentProvider。

## 9. LLM API 接口设计

统一 LLMProvider，支持 OpenAI-compatible、Anthropic-compatible、Gemini-compatible、DeepSeek、Qwen、Moonshot、智谱、Ollama、LM Studio、vLLM 和本地模型 HTTP API。

功能：

```text
summarize_event
classify_event
score_event
extract_entities
extract_risks
analyze_policy
analyze_financial_report
generate_stock_brief
generate_sector_brief
generate_daily_report
generate_weekly_report
explain_position_window
analyze_supply_chain_impact
deduplicate_semantic_events
```

AI 输出必须包含结构化结果、证据引用、置信度、风险提示、免责声明、原始事件 ID，并可存储入库。

## 10. 本地 Agent 接口设计

AgentProvider 支持：

- HTTP API
- WebSocket
- 本地命令行调用
- MCP 工具调用
- 文件夹监听
- 消息队列
- Webhook

MVP 只需要一个统一 AI Research Assistant，用于生成日报/周报、解释事件影响、生成个股和行业摘要、解释仓位窗口变化原因、回答关注标的和行业问题。

Agent 必须通过 DataService、EventService、SignalService、ReportService、NotificationService、KnowledgeGraphService 等工具接口访问系统，不允许绕过数据库凭空生成事实。

## 11. 邮箱目标管理设计

EmailTarget 字段：

- id
- name
- address
- enabled
- report_types
- sectors
- tickers
- frequency
- alert_threshold
- last_send_status
- last_sent_at

DeliveryLog 字段：

- id
- target_id
- channel
- report_id
- alert_id
- status
- retry_count
- error_message
- sent_at

发送策略：

- 先生成报告并落库
- 根据目标邮箱过滤报告类型、行业和标的
- 渲染邮件正文
- 发送并记录 DeliveryLog
- 失败进入重试队列
- 超过重试次数后保留失败原因

## 12. 报告生成流程

```text
Collect events
Normalize events
Link entities
Classify events
Enrich signals
Deduplicate
Score Impact / Trend / Sentiment / Risk
Detect position window changes
Store events, signals and states
Select report sections
Compose deterministic report skeleton
Optional LLM natural language polish
Ground AI output to event IDs
Persist report
Notify targets
Record delivery logs
```

报告生成必须能在 LLM 关闭时运行，输出基于模板的结构化报告。

## 13. 仓位窗口识别逻辑

仓位窗口状态由规则和模型评分共同生成，不依赖 Agent 自由判断。

参考评分：

- Momentum Score：价格趋势、相对强弱、突破/回撤
- Volume Score：成交量、换手率、放量结构
- Fundamental Score：财报、订单、利润率、景气变化
- Catalyst Score：政策、产业链、海外映射、公告催化
- Sentiment Score：新闻、社媒、研报语义倾向
- Risk Score：监管、减持、解禁、估值、负面事件

示例状态逻辑：

- 观察：Impact 或 Trend 上升，但缺少价格或基本面确认。
- 左侧建仓观察：估值/价格处于历史低位，风险未继续恶化，基本面或产业链出现改善线索。
- 右侧增持观察：趋势确认、成交量放大、行业评分改善、催化持续出现。
- 持有跟踪：趋势和基本面稳定，风险可控，无显著减弱信号。
- 减持观察：估值偏高、趋势转弱、情绪下降或催化兑现。
- 风险预警：Risk Score 快速上升，重大负面事件、监管事件、业绩风险或流动性风险出现。

每次状态变化必须记录 previous_state、current_state、triggered_by_signal_ids、triggered_by_event_ids、rule_version 和 explanation。

## 14. 数据库存储建议

MVP 默认 SQLite：

- 本地部署简单
- 便于备份和迁移
- 适合个人和小团队使用
- 支持后续迁移 PostgreSQL

后续扩展：

- PostgreSQL：多用户和团队协作
- pgvector / FAISS / Chroma：语义检索
- DuckDB：本地分析和批量回测
- 本地文件系统：原始文件、报告和附件归档

## 15. 配置文件结构建议

建议配置拆分：

```text
configs/
  config.yaml
  sources.yaml
  watchlist.yaml
  sectors.yaml
  email_targets.yaml
  llm.yaml
  agents.yaml
```

关键配置：

- 数据源启用/停用
- 行业和标的列表
- 报告类型和推送频率
- 异常阈值
- 邮箱目标
- LLM Provider
- Agent Provider
- 本地存储路径

## 16. MVP 开发路线

### M1：基础数据与自选股系统

- Watchlist 配置
- Asset 基础信息
- MarketDataProvider 抽象
- NewsProvider 抽象
- Event 数据表
- SQLite 存储
- 基础 CLI 或 Web UI

### M2：事件系统与评分系统

- 事件采集
- 事件标准化
- 事件分类
- Impact Score
- Trend Score
- Sentiment Score
- Risk Score
- 事件卡片生成

### M3：日报 / 周报与邮箱推送

- Report Composer
- 盘后日报
- 周报
- Email Notification
- 邮箱目标管理
- 发送测试邮件
- 失败重试和日志

### M4：仓位窗口辅助识别

- Position Window Engine
- 建仓观察
- 增持观察
- 减持观察
- 风险预警
- 状态变更记录
- 状态解释生成

### M5：AI Research Assistant

- LLMProvider interface
- 事件摘要
- 个股摘要
- 行业摘要
- 日报自然语言生成
- 仓位窗口解释
- AI 输出与事件 ID 绑定

## 17. 后续扩展路线

- 多数据源接入
- 公告解析
- 财报解析
- 产业链知识图谱
- 语义去重
- 向量数据库
- 本地 LLM
- OpenClaw 接入
- MCP 工具接入
- QQ Bot / Telegram Bot
- 多 Agent 协同
- 量化回测模块
- 事件研究模块
- 团队协作
- Web Dashboard
- API 服务

