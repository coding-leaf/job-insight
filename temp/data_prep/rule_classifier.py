"""Rule-based Job Classifier.

Implements deterministic classification based on the 11 standard categories defined in
docs/job-classification.md. Enforces priority rules:
1. Multi-role detection (spanning distinct categories) -> None
2. Generic campus recruitment / management trainee without duty description -> None
3. Overly broad titles without description (e.g. '数据工程师', '系统工程师') -> None
4. Title vs description core duty contradictions -> None
5. Professional qualifier priority & explicit role title precedence:
   - Specific role titles (software testing, software dev, AI algorithms, etc.) take precedence
     over company/industry modifier words (e.g. '北方华创微电子-软件测试工程师' -> 软件测试).
   - Chip qualifier: '数字前端' -> 硬件与芯片 vs 'Web前端' -> 软件开发;
   - Hardware/chip testing: '芯片测试'/'硬件测试' -> 硬件与芯片 vs '软件测试' -> 软件测试.
   - Safety engineer disambiguation: IT/cybersecurity -> 网络与信息安全;
     production/industrial/EHS safety -> 其他明确岗位 (if explicit duties) or None (if vague).
   - Academic/teaching roles: '专任教师'/'教师' -> 其他明确岗位.
6. Title priority with description supplementary evidence.
"""

from __future__ import annotations

import re
from typing import Optional, Tuple

VALID_CATEGORIES = [
    "算法与人工智能",
    "数据分析与大数据",
    "软件开发",
    "软件测试",
    "运维与云平台",
    "网络与信息安全",
    "硬件与芯片",
    "通信",
    "技术支持与实施",
    "项目与产品",
    "其他明确岗位",
]


def extract_core_title(raw_title: str) -> str:
    """Isolate core job title from company prefix or recruitment codes."""
    t = (
        raw_title.replace("（", "(")
        .replace("）", ")")
        .replace("【", "[")
        .replace("】", "]")
        .strip()
    )

    # 1. Strip leading bracket blocks [tag] or (tag) if tag is batch/company/location or rest has a role
    m_bracket = re.match(r"^(\[[^\]]+\]|\([^)]+\))\s*(.+)$", t)
    if m_bracket:
        bracket_content = m_bracket.group(1)
        rest = m_bracket.group(2).strip()
        if rest:
            company_batch_indicators = [
                "校招",
                "秋招",
                "春招",
                "届",
                "专项",
                "科技",
                "公司",
                "集团",
                "深圳",
                "香港",
                "北京",
                "微电子",
                "半导体",
                "ASP",
                "基地",
                "招聘",
            ]
            role_indicators = [
                "开发",
                "测试",
                "算法",
                "运维",
                "工程",
                "架构",
                "技术",
                "经理",
                "专员",
                "教师",
                "岗",
                "总监",
                "设计师",
            ]
            if any(k in bracket_content for k in company_batch_indicators) or any(
                k in rest for k in role_indicators
            ):
                t = rest.lstrip("-— ").strip()

    # 2. Split on hyphens / dashes to isolate company prefixes
    parts = [p.strip() for p in re.split(r"[-—]", t) if p.strip()]
    if len(parts) >= 2:
        p0 = parts[0]
        company_indicators = [
            "公司",
            "集团",
            "微电子",
            "半导体",
            "科技",
            "工业",
            "重工",
            "设计院",
            "研究所",
        ]
        role_indicators = [
            "开发",
            "测试",
            "算法",
            "运维",
            "工程师",
            "经理",
            "专员",
            "总监",
            "设计师",
            "架构师",
            "技术员",
            "教师",
        ]
        if any(ci in p0 for ci in company_indicators) and not any(
            ri in p0 for ri in role_indicators
        ):
            return "-".join(parts[1:]).strip()
    return t


def classify_by_rule(
    title: str,
    description: Optional[str] = None,
    major_requirement: Optional[str] = None,
) -> Tuple[Optional[str], str]:
    """Classify a single job based on rules.

    Returns:
        (category, reason): category is one of the 11 valid categories or None.
    """
    raw_title = title.strip() if title else ""
    desc = description.strip() if description else ""

    # Normalize title for inspection
    t_clean = (
        raw_title.replace("（", "(")
        .replace("）", ")")
        .replace("【", "[")
        .replace("】", "]")
    )
    core_title = extract_core_title(raw_title)

    # 1. Multi-job detection in title
    multi_job_batch_patterns = [
        r"\(\d+人\)",
        r"/\d+k-\d+k",
        r"/\d+K-\d+K",
        r"电气工程师/自控工程师/新能源",
        r"大模型算法工程师/.*计算机视觉.*后端开发.*软件测试",
        r"算法工程师.*开发工程师.*测试工程师",
        r"恒生2027校园招聘I软件开发I软件测试",
        r"研发类-(系统、结构、硬件、软件、电气、测试)",
        r"系统策划、战斗策划、游戏原画.*游戏开发",
        r"机器人工程师[\r\n]+IE工程师[\r\n]+质量工程师",
        r"电气自动化类/机械类/电子信息类",
        r"电子信息类/通信技术类/光电类/计算机软件类",
        r"信息化技术管理岗、养护工程岗、研发工程岗",
        r"施工管理岗.*规划设计岗.*水力机械",
        r"硬件电路设计师、嵌入式软件设计师",
        r"嵌入式软件/硬件开发工程师",
        r"嵌入式软件/硬件工程师",
        r"硬件/软件研发工程师",
        r"软件工程师（算法/嵌入式/C\+\+/C#/Android）",
        r"JAVA/前端/PYTHON工程师",
        r"算法工程师/系统开发工程师",
        r"AI/IT运维/软件开发工程师",
        r"自动化/机构设计/上位机软件工程师",
        r"技术储备干部（Java开发/前端开发/产品/测试/解决方案）",
        r"技术管培生（Java/大数据/Go/运维/产品经理）",
        r"技术储备干部.*Java开发.*产品.*测试",
        r"兴唐通信.*校招岗位（算法、软件、芯片、硬件研发等方向）",
        r"研发类/运维类/营销类",
        r"运维/实施工程师",
        r"运维/技术支持",
        r"技术运维/开发",
        r"自动化测试/性能测试",
        r"测试工程师（软件测试/硬件测试",
        r"车载测试/芯片测试/硬件测试",
    ]

    for pat in multi_job_batch_patterns:
        if re.search(pat, t_clean):
            # Special check: is it intra-category multi-direction?
            if "自动化测试/性能测试" in t_clean and "硬件" not in t_clean:
                pass  # Intra-category within 软件测试
            elif "车载测试/芯片测试/硬件测试" in t_clean:
                pass
            elif re.search(
                r"恒生2027校园招聘I软件开发I软件测试", t_clean
            ) and desc.startswith("测试工程师："):
                pass
            else:
                return None, "标题包含跨领域多岗位并列招聘，职责边界不单一，规则留空"

    # Multi-job check on titles with slash between different disciplines
    if "/" in t_clean or "、" in t_clean:
        disparate_combos = [
            ("软件", "硬件"),
            ("硬件", "软件"),
            ("开发", "测试"),
            ("算法", "开发"),
            ("运维", "开发"),
            ("运维", "实施"),
            ("运维", "支持"),
            ("产品", "开发"),
            ("产品", "测试"),
        ]
        for c1, c2 in disparate_combos:
            if (
                c1 in t_clean
                and c2 in t_clean
                and not any(
                    ok in t_clean for ok in ["运维开发", "测试开发", "开发测试"]
                )
            ):
                return (
                    None,
                    f"标题包含跨专业方向({c1}/{c2})，且无单一主职责证据，规则留空",
                )

    # 2. Vague campus recruitment / management trainee without duty description
    generic_campus_titles = [
        "校园招聘",
        "2027届校园招聘",
        "数据所（兴唐公司）2027届校园招聘",
        "管培生",
        "技术管培生",
        "研发管培生",
        "计划管培生",
        "大数据管培生",
        "数据分析管培生",
        "研发工程师（本科·2027届）自动化·电子信息·电气类专业",
        "2027校园招聘：研发类—自动驾驶方向（无锡/上海）",
        "计算机、电子信息",
        "计算机、机械、自动化、材料、电子信息、通信工程、动漫日语专业",
        "电气自动化类",
    ]
    for gct in generic_campus_titles:
        if core_title == gct or core_title.startswith(gct):
            if not desc or len(desc) < 30 or "详见招聘简章" in desc or "见附件" in desc:
                return (
                    None,
                    f"标题为统招/专业大类标签('{raw_title}')且无具体岗位职责，规则留空",
                )

    # Check titles that only state trainee/campus without a clear technical track
    if any(k in core_title for k in ["管培生", "储备干部", "校园招聘"]) and not any(
        k in core_title
        for k in [
            "开发",
            "测试",
            "算法",
            "运维",
            "安全",
            "网络",
            "前端",
            "后端",
            "Java",
            "Python",
            "C++",
            "Go",
        ]
    ):
        if not desc or len(desc) < 30 or "详见" in desc:
            return None, f"标题为管培/统招('{raw_title}')且正文信息不足，规则留空"

    # 3. Overly broad single titles without description
    broad_isolated_titles = [
        "数据工程师",
        "大数据工程师",
        "系统工程师",
        "研发工程师",
        "工程师",
        "技术员",
        "助理工程师",
        "IT/数字化管理",
        "产品研发岗（数字化技术工程师）",
    ]
    for bit in broad_isolated_titles:
        if core_title == bit and (not desc or len(desc) < 30 or "根据单位安排" in desc):
            return (
                None,
                f"标题为宽泛岗位('{raw_title}')且无明确正文职责，无法确认具体方向，规则留空",
            )

    # 4. Check title vs description core duty contradictions
    if "产品经理" in core_title and ("电路" in desc or "PCB" in desc or "RTL" in desc):
        return None, "标题为产品经理但正文核心职责为硬件电路设计，发生冲突，规则留空"

    # 5. Teacher / Teaching roles -> 其他明确岗位
    if any(w in t_clean for w in ["专任教师", "教师", "助教", "讲师"]):
        return (
            "其他明确岗位",
            "标题明确为教师/教研/教学岗位，归入其他明确岗位",
        )

    # 6. Specific Role Priority & Professional Qualifier Matching

    # --- Digital chip frontend/backend qualifiers ---
    if any(
        w in core_title
        for w in [
            "数字前端",
            "数字后端",
            "芯片前端",
            "IC前端",
            "IC后端",
            "RTL",
            "EDA",
        ]
    ):
        return (
            "硬件与芯片",
            "标题包含数字芯片前后端设计/RTL等限定词，明确为硬件与芯片方向",
        )

    # --- Explicit Hardware/Chip Testing ---
    if any(
        w in core_title
        for w in [
            "芯片测试",
            "硬件测试",
            "ATE测试",
            "ATE",
            "硅光芯片测试",
            "MEMS芯片测试",
            "集成电路系统测试",
        ]
    ):
        return "硬件与芯片", "标题明确为芯片/硬件/ATE测试，归入硬件与芯片类"

    # --- Explicit Software Testing ---
    software_test_keywords = [
        "软件测试",
        "测试开发",
        "自动化测试",
        "功能测试",
        "性能测试",
        "测试工程师",
        "QA工程师",
        "测试员",
    ]
    if any(w in core_title for w in software_test_keywords):
        if "芯片" in desc and ("CP/FT" in desc or "晶圆" in desc or "封装" in desc):
            return (
                "硬件与芯片",
                "虽然标题包含测试，但正文明确为芯片量产/特性化测试，归入硬件与芯片",
            )
        return "软件测试", "核心职责为软件测试/测试开发/功能测试，归入软件测试"

    # --- Explicit Algorithm & AI ---
    algorithm_keywords = [
        "算法",
        "机器学习",
        "深度学习",
        "计算机视觉",
        "自然语言处理",
        "NLP",
        "CV",
        "视觉算法",
        "图像算法",
        "语音识别",
        "大模型",
        "大语言模型",
        "运筹优化",
        "智能排产",
        "强化学习",
        "自动驾驶算法",
        "智能驾驶算法",
        "规控算法",
        "运控算法",
        "运动控制算法",
        "机器人运动控制",
        "SLAM",
        "具身智能",
        "具身基础模型",
        "AI算法",
        "AI化学反应算法",
        "端到端自动驾驶仿真",
        "多模态",
        "生成式推荐",
        "AIGC算法",
        "点云算法",
    ]
    if any(w in core_title for w in algorithm_keywords):
        return (
            "算法与人工智能",
            "标题包含算法/机器学习/大模型等AI核心关键词，归入算法与人工智能",
        )

    # --- Data Analysis & Big Data ---
    data_keywords = [
        "数据分析",
        "数据挖掘",
        "大数据开发",
        "大数据",
        "数据治理",
        "数仓",
        "数据仓库",
        "ETL",
        "BI工程师",
        "商业智能",
        "数据科学",
    ]
    if any(w in core_title for w in data_keywords):
        if "算法" not in core_title:
            return (
                "数据分析与大数据",
                "标题包含数据分析/大数据开发/数仓等核心关键词，归入数据分析与大数据",
            )

    # --- Cyber Security vs Production Safety Disambiguation ---
    cyber_security_keywords = [
        "网络安全",
        "信息安全",
        "渗透测试",
        "等保",
        "等级保护",
        "漏洞",
        "攻防",
        "网络空间安全",
        "数据安全",
        "安全运维",
        "网络工程",
        "网络工程师",
        "网络维护",
    ]
    # Check if title explicitly indicates cyber/network/information security
    if any(w in core_title for w in cyber_security_keywords):
        if "通信" not in core_title and "无线" not in core_title:
            return (
                "网络与信息安全",
                "标题包含网络工程/网络安全/信息安全等核心词，归入网络与信息安全",
            )

    # Check if description explicitly indicates cyber security
    if any(
        w in desc
        for w in [
            "渗透测试",
            "漏洞挖掘",
            "安全攻防",
            "网络安全",
            "信息安全",
            "等保",
            "网络空间安全",
        ]
    ):
        if "通信" not in core_title and "无线" not in core_title:
            return (
                "网络与信息安全",
                "正文包含明确的渗透测试/漏洞挖掘/信息安全核心职责，归入网络与信息安全",
            )

    # Scoped safety engineer disambiguation: only applies to roles with safety/EHS in title
    if any(w in core_title for w in ["安全", "EHS", "消防", "环保", "职业健康"]):
        prod_safety_keywords = [
            "安全生产",
            "矿山",
            "施工现场",
            "现场施工",
            "施工安全",
            "EHS",
            "消防",
            "隐患排查",
            "注册安全工程师",
            "职业健康",
            "安全巡查",
            "安全巡检",
            "现场安全",
            "安全管理体系",
            "安全无事故",
            "劳动保护",
        ]
        has_prod_safety = any(
            w in core_title or w in desc for w in prod_safety_keywords
        )
        if has_prod_safety:
            if (
                desc
                and len(desc.strip()) >= 10
                and desc.strip() not in ["无", "暂无", "见附件", "详见招聘简章"]
            ):
                return (
                    "其他明确岗位",
                    "岗位职责明确为工业/生产安全(EHS/安全生产/矿山施工)，归入其他明确岗位",
                )
            return (
                None,
                "生产安全岗位正文职责缺失或信息不足，依据不足，规则留空",
            )
        return (
            None,
            "安全类岗位缺少具体正文职责，无法区分网络安全与生产安全，依据不足，规则留空",
        )

    # --- Hardware & Chip Development ---
    hardware_dev_keywords = [
        "芯片",
        "集成电路",
        "IC设计",
        "微电子",
        "半导体",
        "FPGA",
        "电路设计",
        "硬件开发",
        "硬件工程师",
        "硬件研发",
        "单板硬件",
        "PCB",
        "射频电路",
        "微波元件",
        "电磁仿真",
        "电芯材料开发",
        "电芯仿真",
        "功率IC",
        "强电/电能",
        "电气硬件",
    ]
    if any(w in core_title for w in hardware_dev_keywords):
        return "硬件与芯片", "标题包含芯片/电路/硬件研发核心关键词，归入硬件与芯片"

    # --- Ops & Cloud Platform ---
    ops_keywords = [
        "运维",
        "SRE",
        "DevOps",
        "云平台",
        "云原生",
        "系统运维",
        "基础设施运维",
        "DBA",
        "数据库管理员",
        "云计算运维",
    ]
    if any(w in core_title for w in ops_keywords):
        return "运维与云平台", "标题包含运维/SRE/DevOps/云平台关键词，归入运维与云平台"

    # --- Telecom ---
    telecom_keywords = [
        "通信工程师",
        "通信工程",
        "移动通信",
        "无线通信",
        "5G",
        "6G",
        "光通信",
        "射频工程师",
        "射频研发",
        "通信技术",
        "通信协议",
    ]
    if any(w in core_title for w in telecom_keywords):
        return "通信", "标题包含通信/无线/5G/光通信等核心词，归入通信"

    # --- Technical Support & Implementation ---
    support_keywords = [
        "售前工程师",
        "售前技术支持",
        "售后工程师",
        "售后技术支持",
        "实施工程师",
        "交付工程师",
        "现场工程师",
        "技术服务",
        "FAE",
        "软件交付经理",
        "系统交付",
        "产品技术支持",
        "数智产品实施",
    ]
    if any(w in core_title for w in support_keywords):
        return (
            "技术支持与实施",
            "标题包含售前/技术支持/实施/交付等核心词，归入技术支持与实施",
        )

    # --- Project & Product ---
    product_keywords = [
        "产品经理",
        "项目经理",
        "需求分析师",
        "产品设计师",
        "技术项目经理",
        "软件产品经理",
        "硬件产品经理",
    ]
    if any(w in core_title for w in product_keywords):
        return "项目与产品", "标题包含产品经理/项目经理核心词，归入项目与产品"

    # --- Other Explicit Roles ---
    other_explicit_keywords = [
        "销售",
        "财务",
        "会计",
        "出纳",
        "行政",
        "人事",
        "HR",
        "招聘专员",
        "招聘主管",
        "法务",
        "机械设计",
        "机械工程师",
        "机械研发",
        "结构工程师",
        "结构设计",
        "暖通",
        "化工工艺",
        "化工工程师",
        "精细化工",
        "土木",
        "测绘",
        "地质",
        "普工",
        "焊工",
        "车工",
        "CNC",
        "飞行器电气系统工程师",
        "施工管理",
        "施工技术",
        "施工员",
        "安全生产管理",
        "EHS工程师",
        "消防工程师",
    ]
    if any(w in core_title for w in other_explicit_keywords):
        return (
            "其他明确岗位",
            "标题明确为非IT专业技术或职能岗位(机械/销售/财务等)，归入其他明确岗位",
        )

    # --- Software Development ---
    software_dev_keywords = [
        "Web前端",
        "前端开发",
        "前端工程师",
        "后端开发",
        "后端工程师",
        "软件开发",
        "软件工程师",
        "Java",
        "Python开发",
        "Python后端",
        "Python 开发",
        "C++",
        "C/C++",
        "Go开发",
        "Golang",
        "PHP",
        "Android",
        "iOS",
        "安卓",
        "移动开发",
        "全栈",
        "应用开发",
        "嵌入式软件",
        "嵌入式开发",
        "上位机",
        "游戏开发",
        "系统开发工程师",
        "系统研发",
        "驱动工程师",
        "客开后端",
        "QT开发",
        "低代码开发",
        "软件研发",
        "研发技术-软件工程",
        "AI应用开发",
        "AIGC开发",
    ]
    if any(w in core_title for w in software_dev_keywords):
        return (
            "软件开发",
            "标题包含软件开发/前后端/移动端/编程语言等核心词，归入软件开发",
        )

    # Fallback checking description if title is generic
    if desc:
        if (
            "前端开发" in desc
            or "后端开发" in desc
            or "Java" in desc
            or "Spring" in desc
        ):
            return "软件开发", "正文包含明确的前后端软件开发核心职责，归入软件开发"
        if "测试用例" in desc or "软件测试" in desc:
            return "软件测试", "正文包含明确的软件测试职责描述，归入软件测试"
        if "算法" in desc and ("模型训练" in desc or "深度学习" in desc):
            return (
                "算法与人工智能",
                "正文包含明确的算法建模/深度学习职责，归入算法与人工智能",
            )
        if "硬件设计" in desc or "驱动板原理图设计" in desc or "主回路设计" in desc:
            if "研发工程师" in core_title or "系统工程师" in core_title:
                return (
                    "硬件与芯片",
                    "正文明确主要职责为硬件电路/主回路/驱动板设计，归入硬件与芯片",
                )

    return None, "标题与正文未命中明确的单一技术类别规则，依据不足，规则留空"
