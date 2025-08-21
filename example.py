#!/usr/bin/env python3
"""
Kerykeion MCP 包使用示例

展示如何使用打包后的 kerykeion-mcp 包
"""

import json
from datetime import datetime

# 导入包
import kerykeion_mcp


def demo_current_time():
    """演示获取当前时间功能"""
    print("=== 获取当前时间 ===")
    result = kerykeion_mcp.get_current_time()
    if result["success"]:
        data = result["data"]
        print(f"当前时间: {data['datetime_str']}")
        print(f"星期: {data['weekday_cn']}")
        print(f"时间戳: {data['timestamp']}")
    else:
        print(f"错误: {result['error']}")


def demo_astrological_subject():
    """演示创建占星主体功能"""
    print("\n=== 创建占星主体 ===")
    result = kerykeion_mcp.create_astrological_subject(
        name="张三",
        year=1990,
        month=6,
        day=15,
        hour=14,
        minute=30,
        city="北京",
        nation="CN",
        tz_str="Asia/Shanghai"
    )

    if result["success"]:
        data = result["data"]
        input_data = data["input"]
        print(f"姓名: {input_data['name']}")
        print(f"出生地: {input_data['city']}, {input_data['nation']}")
        print(f"出生时间: {input_data['year']}-{input_data['month']:02d}-{input_data['day']:02d} {input_data['hour']:02d}:{input_data['minute']:02d}")
        print(f"使用坐标: {input_data['used_coordinates']}")

        # 显示一些星盘数据
        astrological_data = data["astrological_data"]
        print(f"星盘数据类型: {type(astrological_data)}")
        print(f"星盘数据长度: {len(str(astrological_data)) if astrological_data else 0} 字符")

        # 解析 JSON 字符串
        if isinstance(astrological_data, str):
            try:
                parsed_data = json.loads(astrological_data)
                if isinstance(parsed_data, dict) and "sun" in parsed_data:
                    sun = parsed_data["sun"]
                    if isinstance(sun, dict):
                        print(f"太阳位置: {sun.get('sign', '未知')}座 {sun.get('position', 0):.2f}°")
                    else:
                        print(f"太阳数据: {sun}")
                else:
                    print("星盘数据结构预览:")
                    print(f"可用键: {list(parsed_data.keys())[:5]}")
            except json.JSONDecodeError:
                print(f"JSON 解析失败: {astrological_data[:200]}...")
        elif isinstance(astrological_data, dict):
            if "sun" in astrological_data:
                sun = astrological_data["sun"]
                if isinstance(sun, dict):
                    print(f"太阳位置: {sun.get('sign', '未知')}座 {sun.get('position', 0):.2f}°")
                else:
                    print(f"太阳数据: {sun}")
            else:
                print(f"可用键: {list(astrological_data.keys())[:5]}")
    else:
        print(f"错误: {result['error']}")


def demo_natal_aspects():
    """演示获取本命相位功能"""
    print("\n=== 获取本命相位 ===")
    result = kerykeion_mcp.get_natal_aspects(
        name="李四",
        year=1985,
        month=3,
        day=20,
        hour=9,
        minute=15,
        city="上海",
        nation="CN",
        tz_str="Asia/Shanghai"
    )

    if result["success"]:
        data = result["data"]
        print(f"姓名: {data['input']['name']}")
        print(f"相位数量: {data['aspects_count']}")

        # 显示前几个相位
        aspects = data["aspects"][:3]  # 只显示前3个
        for i, aspect in enumerate(aspects, 1):
            print(f"相位 {i}: {aspect.get('p1_name', '未知')} 与 {aspect.get('p2_name', '未知')} 的 {aspect.get('aspect', '未知')} 相位")
    else:
        print(f"错误: {result['error']}")


def demo_synastry_aspects():
    """演示获取合盘相位功能"""
    print("\n=== 获取合盘相位 ===")
    person1_data = {
        "name": "小明",
        "year": 1992,
        "month": 8,
        "day": 10,
        "hour": 16,
        "minute": 45,
        "city": "广州",
        "nation": "CN",
        "tz_str": "Asia/Shanghai"
    }

    person2_data = {
        "name": "小红",
        "year": 1993,
        "month": 12,
        "day": 5,
        "hour": 11,
        "minute": 20,
        "city": "深圳",
        "nation": "CN",
        "tz_str": "Asia/Shanghai"
    }

    result = kerykeion_mcp.get_synastry_aspects(person1_data, person2_data)

    if result["success"]:
        data = result["data"]
        print(f"人1: {person1_data['name']}")
        print(f"人2: {person2_data['name']}")
        print(f"相位数量: {data['aspects_count']}")

        # 显示前几个相位
        aspects = data["aspects"][:2]  # 只显示前2个
        for i, aspect in enumerate(aspects, 1):
            print(f"合盘相位 {i}: {aspect.get('p1_name', '未知')} 与 {aspect.get('p2_name', '未知')} 的 {aspect.get('aspect', '未知')} 相位")
    else:
        print(f"错误: {result['error']}")


def demo_composite_chart():
    """演示创建组合盘功能"""
    print("\n=== 创建组合盘 ===")
    person1_data = {
        "name": "王五",
        "year": 1988,
        "month": 1,
        "day": 25,
        "hour": 20,
        "minute": 10,
        "city": "成都",
        "nation": "CN",
        "tz_str": "Asia/Shanghai"
    }

    person2_data = {
        "name": "赵六",
        "year": 1989,
        "month": 7,
        "day": 12,
        "hour": 8,
        "minute": 30,
        "city": "杭州",
        "nation": "CN",
        "tz_str": "Asia/Shanghai"
    }

    result = kerykeion_mcp.create_composite_chart(person1_data, person2_data)

    if result["success"]:
        data = result["data"]
        print(f"组合盘名称: {data['composite_name']}")
        print(f"人1: {person1_data['name']}")
        print(f"人2: {person2_data['name']}")

        # 显示组合盘的一些数据
        composite_data = data["composite_astrological_data"]
        print(f"组合数据类型: {type(composite_data)}")

        # 解析 JSON 字符串
        if isinstance(composite_data, str):
            try:
                parsed_data = json.loads(composite_data)
                if isinstance(parsed_data, dict) and "sun" in parsed_data:
                    sun = parsed_data["sun"]
                    if isinstance(sun, dict):
                        print(f"组合太阳位置: {sun.get('sign', '未知')}座 {sun.get('position', 0):.2f}°")
                    else:
                        print(f"组合太阳数据: {sun}")
                else:
                    print(f"组合数据可用键: {list(parsed_data.keys())[:3]}")
            except json.JSONDecodeError:
                print(f"JSON 解析失败: {composite_data[:200]}...")
        elif isinstance(composite_data, dict):
            if "sun" in composite_data:
                sun = composite_data["sun"]
                if isinstance(sun, dict):
                    print(f"组合太阳位置: {sun.get('sign', '未知')}座 {sun.get('position', 0):.2f}°")
                else:
                    print(f"组合太阳数据: {sun}")
            else:
                print(f"组合数据可用键: {list(composite_data.keys())[:3]}")
    else:
        print(f"错误: {result['error']}")


def main():
    """主函数"""
    print("Kerykeion MCP 包使用示例")
    print("=" * 40)
    print("包版本: 1.0.0")
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 运行演示
    demo_current_time()
    demo_astrological_subject()
    demo_natal_aspects()
    demo_synastry_aspects()
    demo_composite_chart()

    print("\n=== 示例运行完成 ===")
    print("如需在 MCP 环境中使用，请配置您的 MCP 客户端。")
    print("使用方法：")
    print("1. 安装：pip install kerykeion-mcp")
    print("2. 运行：uvx kerykeion-mcp")
    print("3. MCP 配置：参考 kerykeion_mcp_config.json")


if __name__ == "__main__":
    main()
