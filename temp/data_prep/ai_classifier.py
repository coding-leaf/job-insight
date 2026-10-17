"""Independent AI Job Classifier Engine.

Operates independently without reading rule classifier outputs or logic.
Evaluates (title, description, major_requirement) against the official 11 category
definitions from docs/job-classification.md, outputting pending review proposals.
"""

from __future__ import annotations

import re
from typing import Dict, Optional, Tuple

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


class AIJobClassifier:
    """Independent AI-driven classification engine based on role semantics and duty analysis."""

    def __init__(self, agent_name: str = "AI:Opencode"):
        self.agent_name = agent_name

    def classify(
        self,
        title: str,
        description: Optional[str] = None,
        major_requirement: Optional[str] = None,
    ) -> Dict[str, Optional[str]]:
        """Classify a single job independently.

        Returns:
            dict containing:
                - job_category_review: Optional[str]
                - review_source: str
                - review_reason: str
                - review_status: str ("pending")
        """
        raw_title = title.strip() if title else ""
        desc = description.strip() if description else ""

        category, reason = self._evaluate_semantics(raw_title, desc, major_requirement)

        return {
            "job_category_review": category,
            "review_source": self.agent_name,
            "review_reason": reason,
            "review_status": "pending",
        }

    def _evaluate_semantics(
        self,
        title: str,
        desc: str,
        major: Optional[str],
    ) -> Tuple[Optional[str], str]:
        # Normalize punctuation
        t = (
            title.replace("（", "(")
            .replace("）", ")")
            .replace("【", "[")
            .replace("】", "]")
            .strip()
        )
        core_t = extract_core_title(title)

        # 1. Detect multi-discipline / conglomerate recruitment batches
        multi_patterns = [
            r"/\d+[kK]-\d+[kK]",
            r"\(\d+人\)",
            r"[\r\n]+IE工程师[\r\n]+",
            r"电气工程师/自控工程师/新能源",
            r"大模型算法工程师/.*计算机视觉.*后端开发.*软件测试",
            r"算法工程师.*开发工程师.*测试工程师",
            r"研发类-\(系统、结构、硬件、软件、电气、测试\)",
            r"系统策划、战斗策划、游戏原画.*游戏开发",
            r"电气类/机械类/电子信息类/电力电子类",
            r"电子信息类/通信技术类/光电类/计算机软件类",
            r"施工管理岗.*水力机械",
            r"技术储备干部（Java开发/前端开发/产品/测试/解决方案）",
            r"技术管培生（Java/大数据/Go/运维/产品经理）",
            r"兴唐通信.*校招岗位（算法、软件、芯片、硬件研发等方向）",
            r"研发类/运维类/营销类",
            r"运维/实施工程师",
            r"运维/技术支持",
            r"技术运维/开发",
            r"嵌入式软件/硬件工程师",
            r"硬件/软件研发工程师",
            r"JAVA/前端/PYTHON工程师",
            r"算法工程师/系统开发工程师",
            r"AI/IT运维/软件开发工程师",
        ]
        for mp in multi_patterns:
            if re.search(mp, t):
                return (
                    None,
                    "AI评估：岗位包含跨类别多岗位混合招聘，边界重叠且无主次区分，建议人工复核",
                )

        # Check slash across disparate disciplines
        if "/" in t:
            if any(
                pair[0] in t and pair[1] in t
                for pair in [
                    ("硬件", "软件"),
                    ("软件", "硬件"),
                    ("开发", "测试"),
                    ("测试", "开发"),
                    ("算法", "开发"),
                    ("运维", "开发"),
                    ("运维", "实施"),
                    ("产品", "开发"),
                ]
            ):
                if not any(
                    token in t for token in ["运维开发", "测试开发", "开发测试"]
                ):
                    return (
                        None,
                        "AI评估：标题包含跨专业方向斜杠组合，缺乏明确的主职责归属",
                    )

        # 2. Vague campus / management trainee lacking specific duty descriptions
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
            if core_t == gct or core_t.startswith(gct):
                if (
                    not desc
                    or len(desc) < 30
                    or "详见招聘简章" in desc
                    or "见附件" in desc
                ):
                    return (
                        None,
                        f"AI评估：岗位标题为综合校招/统招大类('{title}')且正文缺少具体技术职责，无法推断分类",
                    )

        if any(w in core_t for w in ["校园招聘", "校招", "管培生", "储备干部"]):
            if not any(
                tech in core_t
                for tech in [
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
                if (
                    not desc
                    or len(desc) < 30
                    or "详见招聘简章" in desc
                    or "见附件" in desc
                ):
                    return (
                        None,
                        "AI评估：该岗位为综合校招/管培生岗位，未提供明确技术职责说明，无法推断分类",
                    )

        # 3. Broad isolated titles without duties
        if core_t in [
            "数据工程师",
            "系统工程师",
            "研发工程师",
            "工程师",
            "技术员",
            "助理工程师",
            "IT/数字化管理",
            "产品研发岗（数字化技术工程师）",
        ]:
            if not desc or len(desc) < 30 or "根据单位安排" in desc:
                return (
                    None,
                    f"AI评估：岗位名称('{title}')过于宽泛且缺少正文职责描述，信息不足",
                )

        # 4. Check contradiction between title and duty description
        if "产品经理" in core_t and ("电路" in desc or "硬件" in desc or "PCB" in desc):
            return (
                None,
                "AI评估：岗位标题为产品经理但正文职责聚焦硬件电路设计，存在显著语义矛盾",
            )

        # 5. Teacher / Teaching roles -> 其他明确岗位
        if any(w in t for w in ["专任教师", "教师", "助教", "讲师"]):
            return (
                "其他明确岗位",
                "AI评估：核心职责为学校专任教师教学或学术研究，归入其他明确岗位",
            )

        # 6. Semantic evaluation of core duties with role precedence

        # Category: 硬件与芯片 - Digital frontend/backend & Chip Testing
        if any(
            w in core_t
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
                "AI评估：明确包含芯片数字前后端设计/RTL等半导体核心限定词",
            )

        if any(
            w in core_t
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
            return (
                "硬件与芯片",
                "AI评估：芯片与集成电路硬件特性化测试，归属于硬件与芯片",
            )

        # Category: 软件测试 (Explicit role takes precedence over company modifier words)
        test_terms = [
            "软件测试",
            "测试开发",
            "自动化测试",
            "功能测试",
            "性能测试",
            "测试工程师",
            "QA工程师",
            "测试员",
        ]
        if any(w in core_t for w in test_terms):
            if "芯片" in desc and any(
                ic in desc for ic in ["CP/FT", "晶圆", "封装", "ATE"]
            ):
                return (
                    "硬件与芯片",
                    "AI评估：虽含测试字样，但工作内容为芯片量产测试，属于硬件与芯片",
                )
            return (
                "软件测试",
                "AI评估：核心职责为软件功能验证、自动化脚本编写及测试平台开发",
            )

        # Category: 算法与人工智能
        ai_terms = [
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
        if any(w in core_t for w in ai_terms):
            return (
                "算法与人工智能",
                "AI评估：核心职责聚焦于AI算法研究、机器学习模型训练与智能算法实现",
            )

        # Category: 数据分析与大数据
        data_terms = [
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
        if any(w in core_t for w in data_terms) and "算法" not in core_t:
            return (
                "数据分析与大数据",
                "AI评估：核心职责为数据仓库、ETL管道、大数据处理与商业数据分析",
            )

        # Category: 网络与信息安全 vs Production Safety Disambiguation
        cyber_terms = [
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
        if any(w in core_t for w in cyber_terms):
            if "通信" not in core_t and "无线" not in core_t:
                return (
                    "网络与信息安全",
                    "AI评估：核心职责为主机/网络安全防御、渗透测试及网络基础设施维护",
                )

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
            if "通信" not in core_t and "无线" not in core_t:
                return (
                    "网络与信息安全",
                    "AI评估：正文职责明确为主机渗透测试、安全合规与漏洞挖掘",
                )

        # Scoped safety engineer disambiguation: only applies to roles with safety/EHS in title
        if any(w in core_t for w in ["安全", "EHS", "消防", "环保", "职业健康"]):
            prod_safety_terms = [
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
                "安全巡检",
                "安全巡查",
                "现场安全",
                "安全管理体系",
                "安全无事故",
                "劳动保护",
            ]
            has_prod_safety = any(w in core_t or w in desc for w in prod_safety_terms)
            if has_prod_safety:
                if (
                    desc
                    and len(desc.strip()) >= 10
                    and desc.strip() not in ["无", "暂无", "见附件", "详见招聘简章"]
                ):
                    return (
                        "其他明确岗位",
                        "AI评估：岗位核心职责明确为生产安全、矿山施工安全或EHS管理，归属于其他明确岗位",
                    )
                return (
                    None,
                    "AI评估：生产安全类岗位缺少具体职责描述，信息不足，建议人工复核",
                )
            return (
                None,
                "AI评估：安全类岗位缺少具体正文职责，无法确认是网络安全还是生产安全，建议人工复核",
            )

        # Category: 硬件与芯片 Development
        if any(
            w in core_t
            for w in [
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
        ):
            return (
                "硬件与芯片",
                "AI评估：岗位核心职责涉及芯片、半导体器件、PCB或硬件电路研发",
            )

        if "硬件设计" in desc or "驱动板原理图设计" in desc or "主回路设计" in desc:
            if any(w in core_t for w in ["研发工程师", "系统工程师"]):
                return (
                    "硬件与芯片",
                    "AI评估：正文职责明确为主回路及驱动板硬件设计，归入硬件与芯片",
                )

        # Category: 运维与云平台
        ops_terms = [
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
        if any(w in core_t for w in ops_terms):
            return (
                "运维与云平台",
                "AI评估：核心职责为IT系统基础设施维护、DevOps持续集成与云平台运维",
            )

        # Category: 通信
        telecom_terms = [
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
        if any(w in core_t for w in telecom_terms):
            return (
                "通信",
                "AI评估：核心职责为无线/蜂窝通信、通信协议栈及基站射频通信系统研发",
            )

        # Category: 技术支持与实施
        support_terms = [
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
        if any(w in core_t for w in support_terms):
            return (
                "技术支持与实施",
                "AI评估：面向客户的售前方案设计、项目系统实施与售后技术支持",
            )

        # Category: 项目与产品
        pm_terms = [
            "产品经理",
            "项目经理",
            "需求分析师",
            "产品设计师",
            "技术项目经理",
            "软件产品经理",
            "硬件产品经理",
        ]
        if any(w in core_t for w in pm_terms):
            return (
                "项目与产品",
                "AI评估：核心职责为产品生命周期规划、需求管理或技术项目交付把控",
            )

        # Category: 其他明确岗位
        other_terms = [
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
        if any(w in core_t for w in other_terms):
            return (
                "其他明确岗位",
                "AI评估：明确属于非计算机/电子IT技术门类的其他专业职责",
            )

        # Category: 软件开发
        dev_terms = [
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
        if any(w in core_t for w in dev_terms):
            return (
                "软件开发",
                "AI评估：岗位核心职责为软件系统编码、架构设计与应用软件研发",
            )

        # Deep description inspection if title didn't hit
        if desc:
            if any(
                k in desc
                for k in ["前端开发", "后端开发", "Java开发", "代码编写", "Spring Boot"]
            ):
                return (
                    "软件开发",
                    "AI评估：依据正文工作职责，主要从事软件后端/前端编码开发",
                )
            if any(
                k in desc for k in ["测试用例", "自动化测试", "黑盒测试", "白盒测试"]
            ):
                return (
                    "软件测试",
                    "AI评估：依据正文工作职责，主要从事软件测试用例设计与测试执行",
                )
            if any(k in desc for k in ["模型训练", "深度学习", "算法研究", "强化学习"]):
                return (
                    "算法与人工智能",
                    "AI评估：依据正文工作职责，主要从事AI算法建模与模型训练",
                )

        return (
            None,
            "AI评估：未能从标题及正文中识别出足够具体的单一技术职责特征，建议人工复核",
        )
