"""
MCP Scholar 服务
提供谷歌学术搜索、论文详情、引用信息和论文总结功能
"""

import logging
import sys
import json
from mcp.server.fastmcp import FastMCP, Context
from mcp_scholar.scholar import (
    search_scholar,
    get_paper_detail,
    get_paper_references,
    parse_profile,
    extract_profile_id_from_url,
)
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)
# 设置日志级别
logging.basicConfig(level=logging.DEBUG)

# 创建MCP服务器
mcp = FastMCP(
    "ScholarServer",
    dependencies=["scholarly", "httpx", "beautifulsoup4"],
    verbose=True,
    debug=True,
)

# 预设提示词常量
PRESET_SUMMARY_PROMPT = """
分析并总结以下学术论文的内容，请遵循以下结构：

1. **研究概览**：用简明扼要的语言概括所有提供论文的总体研究方向和贡献。
   
2. **主要研究主题**：识别这些论文中出现的关键研究主题和模式，归纳这些主题的发展趋势。
   
3. **研究方法分析**：总结论文中使用的主要研究方法和技术，评估它们的有效性和创新点。
   
4. **重要发现与贡献**：提炼出论文中最重要的科学发现和对该领域的具体贡献。
   
5. **未来研究方向**：基于这些论文的内容，指出该领域可能的未来研究方向和尚未解决的问题。

请确保总结全面、客观、准确，并突出这些论文的学术价值和实际应用意义。对于引用量较高的论文，请给予更多关注。
"""


# 定义提示词函数
def paper_summary_prompt() -> str:
    return PRESET_SUMMARY_PROMPT


def profile_paper_prompt() -> str:
    return """
    请对以下学者的高引用论文进行综合分析，包括：

    1. **学者研究方向**：基于这些高引用论文，总结该学者的主要研究领域和专长。
       
    2. **研究影响力分析**：评估这些论文的学术影响力，特别关注引用量高的工作及其在相关领域的地位。
       
    3. **研究发展历程**：按时间顺序分析这些论文，揭示该学者研究兴趣和方法的演变过程。
       
    4. **与同行的研究对比**：如果可能，比较该学者的研究与该领域其他重要工作的异同。
       
    5. **研究价值与应用**：分析这些研究成果的实际应用价值和对相关产业的潜在影响。

    请提供一个全面、客观的学术分析，突出该学者的研究特色和学术贡献。
    """


def search_prompt() -> str:
    return """
    请对以下搜索结果进行详细分析和总结:

    1. **文献概述**: 简要概述这些搜索结果的共同主题和各自特点，特别关注最新的研究成果。

    2. **研究脉络**: 梳理这些论文反映的研究发展脉络，展示领域内的思想演变过程。

    3. **方法论比较**: 比较不同论文采用的研究方法和技术路线，分析各自的优缺点。

    4. **核心发现**: 提炼出最具创新性和影响力的研究发现，评估其对该领域的贡献。

    5. **应用价值**: 分析这些研究成果的实际应用前景和潜在价值。

    6. **研究缺口**: 指出现有研究中的不足之处和未来可能的研究方向。

    请根据引用量和发表时间对文献进行适当加权，对高引用的经典文献和最新研究成果给予更多关注。
    """


# 工具函数
@mcp.tool()
async def scholar_search(
    ctx: Context,
    keywords: str,
    count: int = 5,
    fuzzy_search: bool = False,
    sort_by: str = "relevance",
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
) -> Dict[str, Any]:
    """
    搜索谷歌学术并返回论文摘要

    Args:
        keywords: 搜索关键词
        count: 返回结果数量，默认为5
        fuzzy_search: 是否使用模糊搜索，默认为False
        sort_by: 排序方式，可选值:
            - "relevance": 按相关性排序（默认）
            - "citations": 按引用量排序
            - "date": 按发表日期排序（新到旧）
            - "title": 按标题字母顺序排序
        year_start: 开始年份，可选
        year_end: 结束年份，可选

    Returns:
        Dict: 包含论文列表的字典
    """
    try:
        search_mode = "模糊搜索" if fuzzy_search else "精确搜索"
        logger.info(f"正在进行{search_mode}谷歌学术: {keywords}...")

        # 添加年份信息到日志
        year_info = ""
        if year_start and year_end:
            year_info = f"，年份范围: {year_start}-{year_end}"
        elif year_start:
            year_info = f"，起始年份: {year_start}"
        elif year_end:
            year_info = f"，截止年份: {year_end}"

        if year_info:
            logger.info(f"应用年份过滤{year_info}")

        results = await search_scholar(
            keywords,
            count,
            fuzzy_search=fuzzy_search,
            sort_by=sort_by,
            year_start=year_start,
            year_end=year_end,
        )

        papers = []
        for p in results:
            papers.append(
                {
                    "title": p["title"],
                    "authors": p["authors"],
                    "abstract": p["abstract"],
                    "abstract_source": p.get("abstract_source", "Google Scholar"),
                    "abstract_quality": p.get("abstract_quality", "基本"),
                    "citations": p["citations"],
                    "year": p.get("year", "Unknown"),
                    "paper_id": p.get("paper_id", None),
                    "venue": p.get("venue", ""),
                    "url": p.get("url", ""),  # 添加URL
                    "doi_url": p.get("doi_url", ""),  # 添加DOI URL
                }
            )

        return {
            "status": "success",
            "papers": papers,
            "search_mode": search_mode,
            "total_results": len(papers),
            "sort_by": sort_by,
            "year_filter": (
                {"start": year_start, "end": year_end}
                if (year_start or year_end)
                else None
            ),
        }
    except Exception as e:
        logger.error(f"搜索失败: {str(e)}", exc_info=True)
        return {"status": "error", "message": "学术搜索服务暂时不可用", "error": str(e)}


@mcp.tool()
async def adaptive_search(
    ctx: Context,
    keywords: str,
    count: int = 5,
    min_results: int = 3,
    sort_by: str = "relevance",
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
) -> Dict[str, Any]:
    """
    自适应搜索谷歌学术，先尝试精确搜索，如果结果太少则自动切换到模糊搜索

    Args:
        keywords: 搜索关键词
        count: 返回结果数量，默认为5
        min_results: 最少需要返回的结果数量，少于此数量会触发模糊搜索，默认为3
        sort_by: 排序方式，可选值:
            - "relevance": 按相关性排序（默认）
            - "citations": 按引用量排序
            - "date": 按发表日期排序（新到旧）
            - "title": 按标题字母顺序排序
        year_start: 开始年份，可选
        year_end: 结束年份，可选

    Returns:
        Dict: 包含论文列表和搜索模式的字典
    """
    try:
        # 先进行精确搜索
        logger.info(f"开始自适应搜索流程，首先进行精确搜索: {keywords}...")

        # 添加年份信息到日志
        if year_start or year_end:
            year_range = ""
            if year_start and year_end:
                year_range = f"{year_start}-{year_end}"
            elif year_start:
                year_range = f"从{year_start}年起"
            elif year_end:
                year_range = f"至{year_end}年止"
            logger.info(f"使用年份过滤: {year_range}")

        precise_results = await search_scholar(
            keywords,
            count,
            fuzzy_search=False,
            sort_by=sort_by,
            year_start=year_start,
            year_end=year_end,
        )

        search_mode = "精确搜索"
        final_results = precise_results

        # 如果精确搜索结果太少，切换到模糊搜索
        if len(precise_results) < min_results:
            logger.info(
                f"精确搜索结果不足({len(precise_results)}<{min_results})，切换到模糊搜索"
            )
            fuzzy_results = await search_scholar(
                keywords,
                count,
                fuzzy_search=True,
                sort_by=sort_by,
                year_start=year_start,
                year_end=year_end,
            )
            search_mode = "模糊搜索(由于精确搜索结果不足)"
            final_results = fuzzy_results

        papers = []
        for p in final_results:
            papers.append(
                {
                    "title": p["title"],
                    "authors": p["authors"],
                    "abstract": p["abstract"],
                    "citations": p["citations"],
                    "year": p.get("year", "Unknown"),
                    "paper_id": p.get("paper_id", None),
                    "venue": p.get("venue", ""),
                    "url": p.get("url", ""),  # 添加URL
                    "doi_url": p.get("doi_url", ""),  # 添加DOI URL
                }
            )

        return {
            "status": "success",
            "papers": papers,
            "search_mode": search_mode,
            "total_results": len(papers),
            "sort_by": sort_by,
            "year_filter": (
                {"start": year_start, "end": year_end}
                if (year_start or year_end)
                else None
            ),
        }
    except Exception as e:
        logger.error(f"自适应搜索失败: {str(e)}", exc_info=True)
        return {"status": "error", "message": "学术搜索服务暂时不可用", "error": str(e)}


@mcp.tool()
async def paper_detail(ctx: Context, paper_id: str) -> Dict[str, Any]:
    """
    获取论文详细信息

    Args:
        paper_id: 论文ID

    Returns:
        Dict: 论文详细信息
    """
    try:
        # 移除进度显示
        logger.info(f"正在获取论文ID为 {paper_id} 的详细信息...")
        detail = await get_paper_detail(paper_id)

        if detail:
            # 确保URL信息被返回
            if "url" not in detail and detail.get("pub_url"):
                detail["url"] = detail["pub_url"]

            # 如果有DOI，添加DOI URL
            if "doi" in detail and "doi_url" not in detail:
                detail["doi_url"] = f"https://doi.org/{detail['doi']}"

            return {"status": "success", "detail": detail}
        else:
            # 移除错误通知
            logger.warning(f"未找到ID为 {paper_id} 的论文")
            return {"status": "error", "message": f"未找到ID为 {paper_id} 的论文"}
    except Exception as e:
        # 移除错误通知
        logger.error(f"获取论文详情失败: {str(e)}", exc_info=True)
        return {"status": "error", "message": "论文详情服务暂时不可用", "error": str(e)}


@mcp.tool()
async def paper_references(
    ctx: Context, paper_id: str, count: int = 5, sort_by: str = "relevance"
) -> Dict[str, Any]:
    """
    获取引用指定论文的文献列表

    Args:
        paper_id: 论文ID
        count: 返回结果数量，默认为5
        sort_by: 排序方式，可选值:
            - "relevance": 按相关性排序（默认）
            - "citations": 按引用量排序
            - "date": 按发表日期排序（新到旧）
            - "title": 按标题字母顺序排序

    Returns:
        Dict: 引用论文列表
    """
    try:
        # 移除进度显示
        logger.info(f"正在获取论文ID为 {paper_id} 的引用...")
        references = await get_paper_references(paper_id, count, sort_by=sort_by)

        refs = []
        for ref in references:
            refs.append(
                {
                    "title": ref["title"],
                    "authors": ref["authors"],
                    "abstract": ref["abstract"],
                    "citations": ref["citations"],
                    "year": ref.get("year", "Unknown"),
                    "paper_id": ref.get("paper_id", None),
                    "url": ref.get("url", ""),  # 添加URL
                    "doi_url": ref.get("doi_url", ""),  # 添加DOI URL
                }
            )

        return {
            "status": "success",
            "references": refs,
            "sort_by": sort_by,
        }
    except Exception as e:
        error_msg = f"获取论文引用失败: {str(e)}"
        # 移除错误通知
        logger.error(error_msg, exc_info=True)
        return {"status": "error", "message": "论文引用服务暂时不可用", "error": str(e)}


@mcp.tool()
async def profile_papers(
    ctx: Context, profile_url: str, count: int = 5, sort_by: str = "relevance"
) -> Dict[str, Any]:
    """
    获取学者的论文

    Args:
        profile_url: 谷歌学术个人主页URL
        count: 返回结果数量，默认为5
        sort_by: 排序方式，可选值:
            - "relevance": 按相关性排序（默认）
            - "citations": 按引用量排序
            - "date": 按发表日期排序（新到旧）
            - "title": 按标题字母顺序排序

    Returns:
        Dict: 论文列表
    """
    try:
        # 移除进度显示
        logger.info(f"正在解析个人主页 {profile_url}...")
        profile_id = extract_profile_id_from_url(profile_url)

        if not profile_id:
            # 移除错误通知
            logger.error("无法从URL中提取学者ID")
            return {"status": "error", "message": "无法从URL中提取学者ID"}

        papers = await parse_profile(profile_id, count, sort_by=sort_by)

        result_papers = []
        for p in papers:
            result_papers.append(
                {
                    "title": p["title"],
                    "authors": p["authors"],
                    "abstract": p["abstract"],
                    "citations": p["citations"],
                    "year": p.get("year", "Unknown"),
                    "venue": p.get("venue", ""),
                    "paper_id": p.get("paper_id", None),
                    "url": p.get("url", ""),  # 添加URL
                    "doi_url": p.get("doi_url", ""),  # 添加DOI URL
                }
            )

        return {
            "status": "success",
            "papers": result_papers,
            "sort_by": sort_by,
        }
    except Exception as e:
        error_msg = f"获取学者论文失败: {str(e)}"
        # 移除错误通知
        logger.error(error_msg, exc_info=True)
        return {"status": "error", "message": "学者论文服务暂时不可用", "error": str(e)}


@mcp.tool()
async def summarize_papers(
    ctx: Context,
    topic: str,
    count: int = 5,
    sort_by: str = "relevance",
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
) -> str:
    """
    搜索并总结特定主题的论文

    Args:
        topic: 研究主题
        count: 返回结果数量，默认为5
        sort_by: 排序方式，可选值:
            - "relevance": 按相关性排序（默认）
            - "citations": 按引用量排序
            - "date": 按发表日期排序（新到旧）
            - "title": 按标题字母顺序排序
        year_start: 开始年份，可选
        year_end: 结束年份，可选

    Returns:
        str: 论文总结的Markdown格式文本
    """
    try:
        # 移除进度显示
        logger.info(f"正在搜索并总结关于 {topic} 的论文...")

        # 记录年份过滤信息
        if year_start or year_end:
            year_info = ""
            if year_start and year_end:
                year_info = f"{year_start}-{year_end}年间"
            elif year_start:
                year_info = f"{year_start}年后"
            elif year_end:
                year_info = f"{year_end}年前"
            logger.info(f"应用年份过滤: {year_info}")

        # 搜索论文
        results = await search_scholar(
            topic,
            count,
            sort_by=sort_by,
            year_start=year_start,
            year_end=year_end,
        )

        if not results:
            if year_start or year_end:
                year_info = ""
                if year_start and year_end:
                    year_info = f"{year_start}-{year_end}年间"
                elif year_start:
                    year_info = f"{year_start}年后"
                elif year_end:
                    year_info = f"{year_end}年前"
                return f"未找到{year_info}关于 {topic} 的论文。"
            else:
                return f"未找到关于 {topic} 的论文。"

        # 构建总结
        summary = f"# {topic} 相关研究总结\n\n"

        # 添加年份范围信息
        if year_start or year_end:
            year_info = ""
            if year_start and year_end:
                year_info = f"{year_start}-{year_end}年间"
            elif year_start:
                year_info = f"{year_start}年后"
            elif year_end:
                year_info = f"{year_end}年前"
            summary += f"以下是{year_info}关于 {topic} 的 {len(results)} 篇研究论文的总结：\n\n"
        else:
            summary += f"以下是关于 {topic} 的 {len(results)} 篇研究论文的总结：\n\n"

        for i, paper in enumerate(results):
            summary += f"### {i+1}. {paper['title']}\n"
            summary += f"**作者**: {paper['authors']}\n"
            summary += f"**年份**: {paper.get('year', '未知')}\n"
            summary += f"**引用量**: {paper['citations']}\n"
            if paper.get("url"):
                summary += (
                    f"**链接**: [{paper.get('url', '')}]({paper.get('url', '')})\n"
                )
            if paper.get("doi_url"):
                summary += (
                    f"**DOI**: [{paper.get('doi', '')}]({paper.get('doi_url', '')})\n"
                )
            summary += f"**摘要**: {paper['abstract']}\n\n"

        return summary
    except Exception as e:
        # 移除错误通知
        logger.error(f"论文总结失败: {str(e)}", exc_info=True)
        return "论文总结服务暂时不可用"


@mcp.tool()
async def health_check(ctx: Context) -> str:
    """
    健康检查端点，用于验证服务是否正常运行

    Returns:
        str: 服务状态信息
    """
    return "MCP Scholar服务运行正常"


def cli_main():
    """
    CLI入口点，使用STDIO交互
    """
    print("MCP Scholar STDIO服务准备启动...", file=sys.stderr)

    try:
        # 启动STDIO服务器
        sys.stderr.write("MCP Scholar STDIO服务已启动，等待输入...\n")
        sys.stderr.flush()
        mcp.run()
    except Exception as e:
        print(f"服务启动失败: {str(e)}", file=sys.stderr)


def main():
    """
    服务入口点函数，使用WebSocket交互
    """
    try:
        # 启动WebSocket服务器
        mcp.run(host="0.0.0.0", port=8765)
    except Exception as e:
        print(f"服务启动失败: {str(e)}", file=sys.stderr)


if __name__ == "__main__":
    main()
