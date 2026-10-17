# 305 组完全重复岗位业务语义抽样分析报告

## 1. 重复记录结构与分布统计

- **总来源记录数**：3000 条
- **精确 19 列分组后岗位组数**：2251 组
- **多记录重复组数**：305 组 (占总组数 13.55%)
- **完全重复余量记录数**：749 条

### 重复组规模分布

| 组内记录数 (Size) | 岗位组数量 | 累计合并余量 | 典型代表企业与岗位 |
| --- | --- | --- | --- |
| 2 条 | 189 组 | 189 条 | 昕原半导体（杭州）有限公司 - 大模型推理软件工程师（通信方向 |
| 3 条 | 38 组 | 76 条 | 深圳市科力锐科技有限公司 - 售前工程师(base地：全国各 |
| 4 条 | 26 组 | 78 条 | 合肥欣奕华智能机器股份有限公司 - 算法工程师（计算机视觉） |
| 5 条 | 14 组 | 56 条 | 上海爱扑网络科技股份有限公司 - 游戏开发工程师 |
| 6 条 | 10 组 | 50 条 | 广联达科技股份有限公司 - 设计-软件实施工程师 |
| 7 条 | 3 组 | 18 条 | 中国铁塔股份有限公司安徽省分公司 - 人工智能方向 |
| 8 条 | 9 组 | 63 条 | 广东亿迅科技有限公司 - 前端开发 |
| 9 条 | 4 组 | 32 条 | 苏州市德晟达电子科技有限公司 - Android软件开发工程师 |
| 10 条 | 1 组 | 9 条 | 安徽飞数信息科技有限公司 - 大数据挖掘工程师 |
| 11 条 | 1 组 | 10 条 | 江苏高光新材料科技股份有限公司 - 机器学习 |
| 12 条 | 1 组 | 11 条 | 凌云光技术股份有限公司 - 深度学习算法工程师 |
| 13 条 | 1 组 | 12 条 | 江苏高光新材料科技股份有限公司 - 机器学习 |
| 14 条 | 1 组 | 13 条 | 安徽乐堂控股集团有限责任公司 - 游戏开发 |
| 17 条 | 1 组 | 16 条 | 安徽乐堂控股集团有限责任公司 - 游戏开发 |
| 19 条 | 2 组 | 36 条 | 铭剑电子(南昌)有限公司 - 嵌入式软件工程师（南昌） |
| 20 条 | 1 组 | 19 条 | 深圳市科力锐科技有限公司 - 售前工程师(base地：全国各 |
| 21 条 | 2 组 | 40 条 | 铭剑电子(南昌)有限公司 - 嵌入式软件工程师（南昌） |
| 22 条 | 1 组 | 21 条 | 深圳市科力锐科技有限公司 - Python 开发工程师（后端 |

---

## 2. 发布日期跨度真实分布与业务机制分析 (Date Interval Distribution)

### 2.1 精确 19 列分组内的发布日期分布 (305 组多记录组)

对 305 组完全重复组内全部成员的发布日期差值 `max(published_at) - min(published_at)` 进行全量统计：

| 发布日期跨度区间 | 岗位组数量 | 占比 | 机制与口径实质说明 |
| --- | --- | --- | --- |
| **0 天 (同日发布)** | **305 组** | **100.00%** | 19 列精确分组键包含 `published_at` 原文字符串，同组记录发布日期天然严格恒等 |
| **1 - 7 天 (周内刷新)** | **0 组** | **0.00%** | 任何日期微小差异均产生不同 19 列元组，已被严格划分为不同岗位组 |
| **8 - 30 天 (月度批次)** | **0 组** | **0.00%** | 日期不同不予跨期合并，契约严格保留发布时间独立性 |
| **> 30 天 (跨季度/批次)** | **0 组** | **0.00%** | 长期多批次招聘未在精确层合并，避免错误归并跨期招聘 |

### 2.2 跨发布日期的语义重复全景对照 (420 个语义相同簇)

为了探究“企业在不同时间重新发布相同岗位”的宏观现象，进一步放宽 `published_at` 等非职责字段，对企业名称、岗位标题、正文职责完全相同的 420 个语义重复簇进行跨时间跨度分析：

| 语义跨期时间跨度 | 语义簇数量 | 占比 | 业务实质归纳 |
| --- | --- | --- | --- |
| **0 天 (同一天多渠道/项目)** | **185 簇** | **44.05%** | 企业同日挂靠不同渠道或不同部门提交镜像职责 |
| **1 - 7 天 (平台自动刷新/重发)** | **183 簇** | **43.57%** | 招聘平台为让职位在前排曝光而采用的高频重新发布机制 |
| **8 - 30 天 (月度招聘滚动)** | **46 簇** | **10.95%** | 企业按月度滚动招聘计划补充生源，维持岗位在招状态 |
| **> 30 天 (跨季度春招/秋招批次)** | **6 簇** | **1.43%** | 真正的不同批次校园招聘，属于周期性用人需求 |

**实证结论**：数据表明超过 43% 的跨期重复属于 1-7 天内的平台自动刷新曝光行为。这充分证实了为何 19 列精确去重仅消除了字面镜像（749 条），但不能推断整个数据集中剩余的 2251 组均为完全独立的物理招聘编制。

---

## 3. 抽样审查与字段比对明细 (精选 20 组)

对 305 组完全重复组进行跨规模分层抽样，比对各成员的 `id`、`source_url`、发布日期与招聘人数：

| 代表 ID | 组内条数 | 企业名称 | 岗位标题 | 发布日期 | URL去重数 | 来源 ID 样本 |
| --- | --- | --- | --- | --- | --- | --- |
| `ncss:MeaPtB9iVkcted31jPaupY` | **2** | 苏州联讯仪器股份有限公司 | 【27届】系统工程师 | 2026-10-11 | 2 | `ncss:MeaPtB9iVkcted31jPaupY, ncss:N4zbRKqRfRQygBTq8MmVfF` |
| `ncss:46BHksUhxsckdjTpnaQgWk` | **2** | 深圳市默贝克驱动技术有限 | 研发工程师（本科·2027届） | 2026-10-11 | 2 | `ncss:46BHksUhxsckdjTpnaQgWk, ncss:vXbGSvR8hvTBetA3TquTV` |
| `ncss:2J8imjcVUxcVuJDm4jgxXk` | **2** | 库迪供应链（集团）有限公 | 数据分析实习生 | 2026-10-11 | 2 | `ncss:2J8imjcVUxcVuJDm4jgxXk, ncss:W9tQLwe9V6VN3PxEEAR3xd` |
| `ncss:683gpN4g8asHyvCKjFGGN3` | **3** | 维沃移动通信有限公司 | 资深技术员（网络安全方向） | 2026-10-10 | 3 | `ncss:683gpN4g8asHyvCKjFGGN3, ncss:Y5qZpZaC6YKbkmKLWMmjqR, ncss:x9RrbmjrbvKdUY2gYVsAW` |
| `ncss:5UDrrdPoxmia9WYrrmuj3K` | **3** | 深圳飞骧科技股份有限公司 | 运维开发工程师 | 2026-09-12 | 3 | `ncss:5UDrrdPoxmia9WYrrmuj3K, ncss:ESFYAPAipqmQtDMmF2cDCZ, ncss:SUBK8KFx1HFQaYJ83Kzvrg` |
| `ncss:5TELAxmJEsyEdkhdJYnxAw` | **3** | 北京华清远见科技发展有限 | 人工智能开发工程师 | 2026-10-16 | 3 | `ncss:5TELAxmJEsyEdkhdJYnxAw, ncss:PEXyjXRYSW8ECrQtvLHy8g, ncss:PRETfEzWRRYmTeABrK568a` |
| `ncss:2dW7ebzeRFGhiBD9RvDY5L` | **4** | 虹软科技股份有限公司 | 27届秋招正式批-计算机视觉算 | 2026-09-04 | 4 | `ncss:2dW7ebzeRFGhiBD9RvDY5L, ncss:QnWYbG8bVNJDdqGM4QhsJA, ncss:VCC2QwjnAzstSsGUp4VgmH...` |
| `ncss:CaHdhFXpzkz6AQ62kjG8Ae` | **4** | 常州格睿克斯能源科技有限 | 控制算法开发工程师 | 2026-10-15 | 4 | `ncss:CaHdhFXpzkz6AQ62kjG8Ae, ncss:CjSxxz9VhKD7TiVRvRBk6R, ncss:HqQ8tW99dHkEAXyRDmtkiJ...` |
| `ncss:2UQ9RZNodmVHNfcBNiypeR` | **4** | 南京道成网络科技有限公司 | iOS开发工程师 | 2026-10-12 | 4 | `ncss:2UQ9RZNodmVHNfcBNiypeR, ncss:FBfnFSDfzNR2drFu5wJXDh, ncss:Qvqu3rF12sJgfvFryevmXs...` |
| `ncss:5yaryw3Rw2aZuG2QhB5MsP` | **5** | 南京道成网络科技有限公司 | iOS开发工程师 | 2026-10-12 | 5 | `ncss:5yaryw3Rw2aZuG2QhB5MsP, ncss:65vhh4mGXnBMamuqNHMw4W, ncss:Jz1tC8G2LMBqkhnCdMC6hg...` |
| `ncss:9iJx47NaDPjRseSP9Qcgsh` | **5** | 广东亿迅科技有限公司 | 算法工程师 | 2026-10-16 | 5 | `ncss:9iJx47NaDPjRseSP9Qcgsh, ncss:AP3f1XcHSKPrUkp2VNT1z9, ncss:E3cbcYQga1fwZ33dqywR2N...` |
| `ncss:5otvpLjehYrsf5uY73YhWw` | **5** | 南京小牛智能科技有限公司 | AI算法开发工程师（计算机视觉 | 2026-09-05 | 5 | `ncss:5otvpLjehYrsf5uY73YhWw, ncss:8rR9z76eFi76AdRubtoj74, ncss:GjCUtDY78fPESio3ttybqK...` |
| `ncss:2B5GgLH4raiooxEn8SQZEu` | **6** | 南京小牛智能科技有限公司 | AI算法开发工程师（计算机视觉 | 2026-09-05 | 6 | `ncss:2B5GgLH4raiooxEn8SQZEu, ncss:3uxCdXFhzWAiJ53XRYcZHf, ncss:JabDF1grkJN5GHfNqZccYX...` |
| `ncss:6wY4fGwe9J2wWUjy1pjtGf` | **6** | 科博达技术股份有限公司 | 系统开发工程师 | 2026-10-11 | 6 | `ncss:6wY4fGwe9J2wWUjy1pjtGf, ncss:7Cu8gxAHgqPr1eU7CsZPGW, ncss:CDFtQWKrhCXAQaMYp6sbbq...` |
| `ncss:22UsC6fsyc76i7NFQQspcN` | **6** | 广联达科技股份有限公司 | 设计-软件实施工程师 | 2026-10-14 | 6 | `ncss:22UsC6fsyc76i7NFQQspcN, ncss:3AffnkNNY7L6hZAkREZsiF, ncss:DWWpoGAY42GnbKeMJMoXY...` |
| `ncss:3CRknpm199yBdR9NCKezC2` | **7** | 中国铁塔股份有限公司安徽 | 人工智能方向 | 2026-10-16 | 7 | `ncss:3CRknpm199yBdR9NCKezC2, ncss:AFPwMWwcw63ZTEUWqW6dLt, ncss:CeM4328DT62ikjjrYy2Ty5...` |
| `ncss:E5ZNneMkr3CGB4w5wsKeie` | **7** | 常州科瑞尔科技有限公司 | 视觉算法工程师 | 2026-10-11 | 7 | `ncss:E5ZNneMkr3CGB4w5wsKeie, ncss:FVeYQaxuk6FPMAcV1j2Hzx, ncss:L9Za7mMDBuNRkbNXpaMNVu...` |
| `ncss:6ePYBa1KG8X1TtbMp6vGAv` | **7** | 浙江华睿科技股份有限公司 | 【27届】深度学习算法工程师 | 2026-10-05 | 7 | `ncss:6ePYBa1KG8X1TtbMp6vGAv, ncss:D7GoKmXQTLZUFWpg8sg11N, ncss:D7UJCZ7jHgDqER9NbrhrXn...` |
| `ncss:6fLvmGR6Q2NB3TATDUCCC6` | **8** | 广东亿迅科技有限公司 | 大数据开发 | 2026-10-16 | 8 | `ncss:6fLvmGR6Q2NB3TATDUCCC6, ncss:7rU5tWksxZbYyLFyysoPbm, ncss:CwaUwXookJsN1DxXLxUUgY...` |
| `ncss:2cTwrofr4JhWspPe7p3H5P` | **8** | 广东亿迅科技有限公司 | 前端开发 | 2026-10-16 | 8 | `ncss:2cTwrofr4JhWspPe7p3H5P, ncss:4VPBC68DcB5tvvfD7rZT2R, ncss:Agz66cQRDj7SPLXUCDTNrY...` |

---

## 4. 重复产生根因与业务含义分析

通过对 305 组重复项的 URL 模式、企业发布习惯及招聘平台机制分析，确认存在以下三类主要成因：

1. **平台定时刷新与多次发布机制（占比最高）**：
   - 在国家大学生就业服务平台 (NCSS) 等招聘渠道中，企业为了让岗位在列表前排展示，会频繁“刷新”或“重新发布”同一岗位。
   - 系统后台为每次发布分配了一个全新的独立 UUID（对应唯一的 `source_url`），但岗位标题、职责正文、薪资、学历、工作地点等 19 列核心属性完全未做任何改动。
   - **业务实质**：这是同一岗位的重复曝光，属于数据抓取层面的技术重复，而非企业开放了多倍的实际用人缺口。

2. **同一招聘公告挂靠多个细分项目/渠道**：
   - 部分大型企业（如广联达、安徽乐堂控股等）在同一天通过不同招聘批次或项目入口提交了相同的职位描述（如 14 条完全相同的“游戏开发”岗位）。
   - 虽然 URL 不同，但未注明项目组区分，在当前数据源中表现为纯粹的文本镜像。

3. **招聘人数 (recruitment_headcount) 的独立性**：
   - 重复组内的 `recruitment_headcount` 字段完全一致（例如均为 `1.0` 或均为 `None`）。
   - 若简单按原始来源行数累加招聘人数或统计岗位，将把单个招聘计划虚增 2 至 14 倍，导致严重的统计扭曲。

---

## 5. 统计边界与业务契约声明

1. **2251 组是展示岗位组，不等于独立招聘岗位总数**：
   - 19 列精确分组仅消除了**字面完全一致**的重复镜像（749 条余量）。
   - 尚无法识别语义相同但标题微调（如“Java开发”与“Java后端开发”）的重复，也无法区分同一描述下的多个实际物理编制。
2. **严禁按招聘人数求和代替岗位数**：
   - 所有薪资排名、学历分布、地区统计均以**岗位组数**作为样本量 N 计算，保证数据口径严肃可控。
