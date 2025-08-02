#!/usr/bin/env python3
"""
Kerykeion 占星 MCP 工具
基于 Kerykeion 库计算星座盘并返回 JSON 结果
"""

import json
import sys
import os
from datetime import datetime

try:
    from kerykeion import AstrologicalSubject, KerykeionChartSVG
    from kerykeion import Report
    from kerykeion import SynastryAspects, NatalAspects
    from kerykeion import CompositeSubjectFactory
except ImportError:
    print("错误: 请先安装 kerykeion 库: pip install kerykeion")
    sys.exit(1)


def get_current_time():
    """获取当前时间并返回格式化结果"""
    try:
        now = datetime.now()
        result = {
            "year": now.year,
            "month": now.month,
            "day": now.day,
            "hour": now.hour,
            "minute": now.minute,
            "second": now.second,
            "datetime_str": now.strftime("%Y-%m-%d %H:%M:%S"),
            "weekday": now.strftime("%A"),
            "weekday_cn": ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"][now.weekday()],
            "timestamp": int(now.timestamp())
        }
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_astrological_subject(name, year, month, day, hour, minute, city, nation, 
                               longitude=None, latitude=None, tz_str=None,
                               zodiac_type="Tropical", sidereal_mode="LAHIRI", 
                               houses_system="P", perspective_type="Apparent Geocentric"):
    """创建占星主体对象并返回完整的占星数据
    
    Args:
        name: 姓名
        year: 年份
        month: 月份
        day: 日期
        hour: 小时
        minute: 分钟
        city: 城市名
        nation: 国家代码
        longitude: 经度（可选，提供则不使用城市查询）
        latitude: 纬度（可选，提供则不使用城市查询）
        tz_str: 时区字符串（可选）
        zodiac_type: 黄道类型 ("Tropical" 或 "Sidereal")
        sidereal_mode: 恒星模式（当 zodiac_type 为 "Sidereal" 时使用）
        houses_system: 宫位系统
        perspective_type: 观测视角类型
    
    Returns:
        dict: 包含完整占星数据的字典
    """
    try:
        # 创建占星主体对象
        if longitude is not None and latitude is not None:
            # 使用经纬度
            if tz_str:
                subject = AstrologicalSubject(
                    name, year, month, day, hour, minute,
                    lng=longitude, lat=latitude, tz_str=tz_str, city=city,
                    zodiac_type=zodiac_type, sidereal_mode=sidereal_mode,
                    houses_system=houses_system, perspective_type=perspective_type
                )
            else:
                subject = AstrologicalSubject(
                    name, year, month, day, hour, minute,
                    lng=longitude, lat=latitude, city=city,
                    zodiac_type=zodiac_type, sidereal_mode=sidereal_mode,
                    houses_system=houses_system, perspective_type=perspective_type
                )
        else:
            # 使用城市名查询
            subject = AstrologicalSubject(
                name, year, month, day, hour, minute, city, nation,
                zodiac_type=zodiac_type, sidereal_mode=sidereal_mode,
                houses_system=houses_system, perspective_type=perspective_type
            )
        
        # 使用 Kerykeion 内置的 JSON 序列化功能
        astrological_data = subject.json(dump=False)
        
        result = {
            "input": {
                "name": name,
                "year": year,
                "month": month,
                "day": day,
                "hour": hour,
                "minute": minute,
                "city": city,
                "nation": nation,
                "longitude": longitude,
                "latitude": latitude,
                "tz_str": tz_str,
                "zodiac_type": zodiac_type,
                "sidereal_mode": sidereal_mode,
                "houses_system": houses_system,
                "perspective_type": perspective_type
            },
            "astrological_data": astrological_data
        }
        
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_natal_aspects(name, year, month, day, hour, minute, city, nation,
                     longitude=None, latitude=None, tz_str=None):
    """获取本命相位信息
    
    Args:
        name: 姓名
        year: 年份
        month: 月份  
        day: 日期
        hour: 小时
        minute: 分钟
        city: 城市名
        nation: 国家代码
        longitude: 经度（可选）
        latitude: 纬度（可选）
        tz_str: 时区字符串（可选）
    
    Returns:
        dict: 包含相位信息的字典
    """
    try:
        # 创建占星主体对象
        if longitude is not None and latitude is not None:
            if tz_str:
                subject = AstrologicalSubject(
                    name, year, month, day, hour, minute,
                    lng=longitude, lat=latitude, tz_str=tz_str, city=city
                )
            else:
                subject = AstrologicalSubject(
                    name, year, month, day, hour, minute,
                    lng=longitude, lat=latitude, city=city
                )
        else:
            subject = AstrologicalSubject(
                name, year, month, day, hour, minute, city, nation
            )
        
        # 使用 Kerykeion 内置的 JSON 序列化功能获取基础数据
        astrological_data = subject.json(dump=False)
        
        # 获取本命相位
        natal_aspects = NatalAspects(subject)
        all_aspects = natal_aspects.get_all_aspects()
        
        result = {
            "input": {
                "name": name,
                "year": year,
                "month": month,
                "day": day,
                "hour": hour,
                "minute": minute,
                "city": city,
                "nation": nation,
                "longitude": longitude,
                "latitude": latitude,
                "tz_str": tz_str
            },
            "astrological_data": astrological_data,
            "aspects_count": len(all_aspects),
            "aspects": all_aspects
        }
        
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_synastry_aspects(person1_data, person2_data):
    """获取合盘相位信息
    
    Args:
        person1_data: 第一个人的出生信息字典
        person2_data: 第二个人的出生信息字典
    
    Returns:
        dict: 包含合盘相位信息的字典
    """
    try:
        # 创建第一个人的占星主体对象
        p1 = person1_data
        if p1.get('longitude') is not None and p1.get('latitude') is not None:
            if p1.get('tz_str'):
                subject1 = AstrologicalSubject(
                    p1['name'], p1['year'], p1['month'], p1['day'], p1['hour'], p1['minute'],
                    lng=p1['longitude'], lat=p1['latitude'], tz_str=p1['tz_str'], city=p1['city']
                )
            else:
                subject1 = AstrologicalSubject(
                    p1['name'], p1['year'], p1['month'], p1['day'], p1['hour'], p1['minute'],
                    lng=p1['longitude'], lat=p1['latitude'], city=p1['city']
                )
        else:
            subject1 = AstrologicalSubject(
                p1['name'], p1['year'], p1['month'], p1['day'], p1['hour'], p1['minute'],
                p1['city'], p1['nation']
            )
        
        # 创建第二个人的占星主体对象
        p2 = person2_data
        if p2.get('longitude') is not None and p2.get('latitude') is not None:
            if p2.get('tz_str'):
                subject2 = AstrologicalSubject(
                    p2['name'], p2['year'], p2['month'], p2['day'], p2['hour'], p2['minute'],
                    lng=p2['longitude'], lat=p2['latitude'], tz_str=p2['tz_str'], city=p2['city']
                )
            else:
                subject2 = AstrologicalSubject(
                    p2['name'], p2['year'], p2['month'], p2['day'], p2['hour'], p2['minute'],
                    lng=p2['longitude'], lat=p2['latitude'], city=p2['city']
                )
        else:
            subject2 = AstrologicalSubject(
                p2['name'], p2['year'], p2['month'], p2['day'], p2['hour'], p2['minute'],
                p2['city'], p2['nation']
            )
        
        # 使用 Kerykeion 内置的 JSON 序列化功能获取基础数据
        person1_astrological_data = subject1.json(dump=False)
        person2_astrological_data = subject2.json(dump=False)
        
        # 获取合盘相位
        synastry_aspects = SynastryAspects(subject1, subject2)
        relevant_aspects = synastry_aspects.get_relevant_aspects()
        
        result = {
            "person1_input": person1_data,
            "person2_input": person2_data,
            "person1_astrological_data": person1_astrological_data,
            "person2_astrological_data": person2_astrological_data,
            "aspects_count": len(relevant_aspects),
            "aspects": relevant_aspects
        }
        
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_composite_chart(person1_data, person2_data):
    """创建组合盘（中点合成盘）
    
    Args:
        person1_data: 第一个人的出生信息字典
        person2_data: 第二个人的出生信息字典
    
    Returns:
        dict: 包含组合盘信息的字典
    """
    try:
        # 创建第一个人的占星主体对象
        p1 = person1_data
        if p1.get('longitude') is not None and p1.get('latitude') is not None:
            if p1.get('tz_str'):
                subject1 = AstrologicalSubject(
                    p1['name'], p1['year'], p1['month'], p1['day'], p1['hour'], p1['minute'],
                    lng=p1['longitude'], lat=p1['latitude'], tz_str=p1['tz_str'], city=p1['city']
                )
            else:
                subject1 = AstrologicalSubject(
                    p1['name'], p1['year'], p1['month'], p1['day'], p1['hour'], p1['minute'],
                    lng=p1['longitude'], lat=p1['latitude'], city=p1['city']
                )
        else:
            subject1 = AstrologicalSubject(
                p1['name'], p1['year'], p1['month'], p1['day'], p1['hour'], p1['minute'],
                p1['city'], p1['nation']
            )
        
        # 创建第二个人的占星主体对象
        p2 = person2_data
        if p2.get('longitude') is not None and p2.get('latitude') is not None:
            if p2.get('tz_str'):
                subject2 = AstrologicalSubject(
                    p2['name'], p2['year'], p2['month'], p2['day'], p2['hour'], p2['minute'],
                    lng=p2['longitude'], lat=p2['latitude'], tz_str=p2['tz_str'], city=p2['city']
                )
            else:
                subject2 = AstrologicalSubject(
                    p2['name'], p2['year'], p2['month'], p2['day'], p2['hour'], p2['minute'],
                    lng=p2['longitude'], lat=p2['latitude'], city=p2['city']
                )
        else:
            subject2 = AstrologicalSubject(
                p2['name'], p2['year'], p2['month'], p2['day'], p2['hour'], p2['minute'],
                p2['city'], p2['nation']
            )
        
        # 创建组合盘工厂
        factory = CompositeSubjectFactory(subject1, subject2)
        composite_model = factory.get_midpoint_composite_subject_model()
        
        # 使用 Kerykeion 内置的 JSON 序列化功能获取基础数据
        person1_astrological_data = subject1.json(dump=False)
        person2_astrological_data = subject2.json(dump=False)
        composite_astrological_data = composite_model.json(dump=False)
        
        result = {
            "person1_input": person1_data,
            "person2_input": person2_data,
            "person1_astrological_data": person1_astrological_data,
            "person2_astrological_data": person2_astrological_data,
            "composite_name": f"{subject1.name} & {subject2.name} Composite",
            "composite_astrological_data": composite_astrological_data
        }
        
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def generate_report(name, year, month, day, hour, minute, city, nation,
                   longitude=None, latitude=None, tz_str=None):
    """生成占星报告
    
    Args:
        name: 姓名
        year: 年份
        month: 月份
        day: 日期
        hour: 小时
        minute: 分钟
        city: 城市名
        nation: 国家代码
        longitude: 经度（可选）
        latitude: 纬度（可选）
        tz_str: 时区字符串（可选）
    
    Returns:
        dict: 包含占星报告的字典
    """
    try:
        # 创建占星主体对象
        if longitude is not None and latitude is not None:
            if tz_str:
                subject = AstrologicalSubject(
                    name, year, month, day, hour, minute,
                    lng=longitude, lat=latitude, tz_str=tz_str, city=city
                )
            else:
                subject = AstrologicalSubject(
                    name, year, month, day, hour, minute,
                    lng=longitude, lat=latitude, city=city
                )
        else:
            subject = AstrologicalSubject(
                name, year, month, day, hour, minute, city, nation
            )
        
        # 使用 Kerykeion 内置的 JSON 序列化功能获取基础数据
        astrological_data = subject.json(dump=False)
        
        # 生成报告（Report 主要用于打印格式化报告）
        report = Report(subject)
        
        result = {
            "input": {
                "name": name,
                "year": year,
                "month": month,
                "day": day,
                "hour": hour,
                "minute": minute,
                "city": city,
                "nation": nation,
                "longitude": longitude,
                "latitude": latitude,
                "tz_str": tz_str
            },
            "astrological_data": astrological_data,
            "report_available": True,
            "note": "完整的占星数据已通过 astrological_data 字段提供。如需打印格式的报告，可使用 Kerykeion 的 Report 类。"
        }
        
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    """主函数 - 处理 MCP 请求"""
    
    # 读取标准输入
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            method = request.get("method")
            params = request.get("params", {})
            
            if method == "initialize":
                # 初始化响应
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {
                            "name": "kerykeion-mcp-server",
                            "version": "1.0.0",
                            "description": "Kerykeion 占星计算服务器 - 基于 Kerykeion 库"
                        }
                    }
                }
            
            elif method == "tools/list":
                # 返回可用工具列表
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "tools": [
                            {
                                "name": "get_current_time",
                                "description": "获取当前系统时间，返回详细的时间信息",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {},
                                    "required": []
                                }
                            },
                            {
                                "name": "create_astrological_subject",
                                "description": "创建占星主体对象并返回完整的占星数据，包含行星和宫位信息",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {
                                            "type": "string",
                                            "description": "姓名"
                                        },
                                        "year": {
                                            "type": "integer",
                                            "description": "出生年份"
                                        },
                                        "month": {
                                            "type": "integer",
                                            "description": "出生月份 (1-12)"
                                        },
                                        "day": {
                                            "type": "integer",
                                            "description": "出生日期 (1-31)"
                                        },
                                        "hour": {
                                            "type": "integer",
                                            "description": "出生小时 (0-23)"
                                        },
                                        "minute": {
                                            "type": "integer",
                                            "description": "出生分钟 (0-59)"
                                        },
                                        "city": {
                                            "type": "string",
                                            "description": "出生城市"
                                        },
                                        "nation": {
                                            "type": "string",
                                            "description": "国家代码 (如: US, GB, CN)"
                                        },
                                        "longitude": {
                                            "type": "number",
                                            "description": "经度（可选，提供则不使用城市查询）"
                                        },
                                        "latitude": {
                                            "type": "number",
                                            "description": "纬度（可选，提供则不使用城市查询）"
                                        },
                                        "tz_str": {
                                            "type": "string",
                                            "description": "时区字符串（可选，如: Europe/Rome, America/New_York）"
                                        },
                                        "zodiac_type": {
                                            "type": "string",
                                            "description": "黄道类型",
                                            "enum": ["Tropical", "Sidereal"],
                                            "default": "Tropical"
                                        },
                                        "sidereal_mode": {
                                            "type": "string",
                                            "description": "恒星模式（当 zodiac_type 为 Sidereal 时使用）",
                                            "default": "LAHIRI"
                                        },
                                        "houses_system": {
                                            "type": "string",
                                            "description": "宫位系统",
                                            "default": "P"
                                        },
                                        "perspective_type": {
                                            "type": "string",
                                            "description": "观测视角类型",
                                            "default": "Apparent Geocentric"
                                        }
                                    },
                                    "required": ["name", "year", "month", "day", "hour", "minute", "city", "nation"]
                                }
                            },
                            {
                                "name": "get_natal_aspects",
                                "description": "获取本命相位信息，分析个人星盘中行星之间的角度关系",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string", "description": "姓名"},
                                        "year": {"type": "integer", "description": "出生年份"},
                                        "month": {"type": "integer", "description": "出生月份 (1-12)"},
                                        "day": {"type": "integer", "description": "出生日期 (1-31)"},
                                        "hour": {"type": "integer", "description": "出生小时 (0-23)"},
                                        "minute": {"type": "integer", "description": "出生分钟 (0-59)"},
                                        "city": {"type": "string", "description": "出生城市"},
                                        "nation": {"type": "string", "description": "国家代码"},
                                        "longitude": {"type": "number", "description": "经度（可选）"},
                                        "latitude": {"type": "number", "description": "纬度（可选）"},
                                        "tz_str": {"type": "string", "description": "时区字符串（可选）"}
                                    },
                                    "required": ["name", "year", "month", "day", "hour", "minute", "city", "nation"]
                                }
                            },
                            {
                                "name": "get_synastry_aspects",
                                "description": "获取合盘相位信息，分析两个人星盘之间的相位关系",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "person1_data": {
                                            "type": "object",
                                            "description": "第一个人的出生信息",
                                            "properties": {
                                                "name": {"type": "string"},
                                                "year": {"type": "integer"},
                                                "month": {"type": "integer"},
                                                "day": {"type": "integer"},
                                                "hour": {"type": "integer"},
                                                "minute": {"type": "integer"},
                                                "city": {"type": "string"},
                                                "nation": {"type": "string"},
                                                "longitude": {"type": "number"},
                                                "latitude": {"type": "number"},
                                                "tz_str": {"type": "string"}
                                            },
                                            "required": ["name", "year", "month", "day", "hour", "minute", "city", "nation"]
                                        },
                                        "person2_data": {
                                            "type": "object",
                                            "description": "第二个人的出生信息",
                                            "properties": {
                                                "name": {"type": "string"},
                                                "year": {"type": "integer"},
                                                "month": {"type": "integer"},
                                                "day": {"type": "integer"},
                                                "hour": {"type": "integer"},
                                                "minute": {"type": "integer"},
                                                "city": {"type": "string"},
                                                "nation": {"type": "string"},
                                                "longitude": {"type": "number"},
                                                "latitude": {"type": "number"},
                                                "tz_str": {"type": "string"}
                                            },
                                            "required": ["name", "year", "month", "day", "hour", "minute", "city", "nation"]
                                        }
                                    },
                                    "required": ["person1_data", "person2_data"]
                                }
                            },
                            {
                                "name": "create_composite_chart",
                                "description": "创建组合盘（中点合成盘），用于分析两个人的关系",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "person1_data": {
                                            "type": "object",
                                            "description": "第一个人的出生信息",
                                            "properties": {
                                                "name": {"type": "string"},
                                                "year": {"type": "integer"},
                                                "month": {"type": "integer"},
                                                "day": {"type": "integer"},
                                                "hour": {"type": "integer"},
                                                "minute": {"type": "integer"},
                                                "city": {"type": "string"},
                                                "nation": {"type": "string"},
                                                "longitude": {"type": "number"},
                                                "latitude": {"type": "number"},
                                                "tz_str": {"type": "string"}
                                            },
                                            "required": ["name", "year", "month", "day", "hour", "minute", "city", "nation"]
                                        },
                                        "person2_data": {
                                            "type": "object",
                                            "description": "第二个人的出生信息",
                                            "properties": {
                                                "name": {"type": "string"},
                                                "year": {"type": "integer"},
                                                "month": {"type": "integer"},
                                                "day": {"type": "integer"},
                                                "hour": {"type": "integer"},
                                                "minute": {"type": "integer"},
                                                "city": {"type": "string"},
                                                "nation": {"type": "string"},
                                                "longitude": {"type": "number"},
                                                "latitude": {"type": "number"},
                                                "tz_str": {"type": "string"}
                                            },
                                            "required": ["name", "year", "month", "day", "hour", "minute", "city", "nation"]
                                        }
                                    },
                                    "required": ["person1_data", "person2_data"]
                                }
                            },
                            {
                                "name": "generate_report",
                                "description": "生成详细的占星报告，包含个人星盘的各种信息",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string", "description": "姓名"},
                                        "year": {"type": "integer", "description": "出生年份"},
                                        "month": {"type": "integer", "description": "出生月份 (1-12)"},
                                        "day": {"type": "integer", "description": "出生日期 (1-31)"},
                                        "hour": {"type": "integer", "description": "出生小时 (0-23)"},
                                        "minute": {"type": "integer", "description": "出生分钟 (0-59)"},
                                        "city": {"type": "string", "description": "出生城市"},
                                        "nation": {"type": "string", "description": "国家代码"},
                                        "longitude": {"type": "number", "description": "经度（可选）"},
                                        "latitude": {"type": "number", "description": "纬度（可选）"},
                                        "tz_str": {"type": "string", "description": "时区字符串（可选）"}
                                    },
                                    "required": ["name", "year", "month", "day", "hour", "minute", "city", "nation"]
                                }
                            }
                        ]
                    }
                }
            
            elif method == "tools/call":
                # 处理工具调用
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "get_current_time":
                    try:
                        result = get_current_time()
                        response = {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": {
                                "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}],
                                "isError": False
                            }
                        }
                    except Exception as e:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": {
                                "content": [{"type": "text", "text": f"获取时间错误: {str(e)}"}],
                                "isError": True
                            }
                        }
                
                elif tool_name == "create_astrological_subject":
                    try:
                        result = create_astrological_subject(
                            arguments.get("name"),
                            arguments.get("year"),
                            arguments.get("month"),
                            arguments.get("day"),
                            arguments.get("hour"),
                            arguments.get("minute"),
                            arguments.get("city"),
                            arguments.get("nation"),
                            arguments.get("longitude"),
                            arguments.get("latitude"),
                            arguments.get("tz_str"),
                            arguments.get("zodiac_type", "Tropical"),
                            arguments.get("sidereal_mode", "LAHIRI"),
                            arguments.get("houses_system", "P"),
                            arguments.get("perspective_type", "Apparent Geocentric")
                        )
                        
                        response = {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": {
                                "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}],
                                "isError": False
                            }
                        }
                    except Exception as e:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": {
                                "content": [{"type": "text", "text": f"创建占星主体错误: {str(e)}"}],
                                "isError": True
                            }
                        }
                
                elif tool_name == "get_natal_aspects":
                    try:
                        result = get_natal_aspects(
                            arguments.get("name"),
                            arguments.get("year"),
                            arguments.get("month"),
                            arguments.get("day"),
                            arguments.get("hour"),
                            arguments.get("minute"),
                            arguments.get("city"),
                            arguments.get("nation"),
                            arguments.get("longitude"),
                            arguments.get("latitude"),
                            arguments.get("tz_str")
                        )
                        
                        response = {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": {
                                "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}],
                                "isError": False
                            }
                        }
                    except Exception as e:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": {
                                "content": [{"type": "text", "text": f"获取本命相位错误: {str(e)}"}],
                                "isError": True
                            }
                        }
                
                elif tool_name == "get_synastry_aspects":
                    try:
                        result = get_synastry_aspects(
                            arguments.get("person1_data"),
                            arguments.get("person2_data")
                        )
                        
                        response = {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": {
                                "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}],
                                "isError": False
                            }
                        }
                    except Exception as e:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": {
                                "content": [{"type": "text", "text": f"获取合盘相位错误: {str(e)}"}],
                                "isError": True
                            }
                        }
                
                elif tool_name == "create_composite_chart":
                    try:
                        result = create_composite_chart(
                            arguments.get("person1_data"),
                            arguments.get("person2_data")
                        )
                        
                        response = {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": {
                                "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}],
                                "isError": False
                            }
                        }
                    except Exception as e:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": {
                                "content": [{"type": "text", "text": f"创建组合盘错误: {str(e)}"}],
                                "isError": True
                            }
                        }
                
                elif tool_name == "generate_report":
                    try:
                        result = generate_report(
                            arguments.get("name"),
                            arguments.get("year"),
                            arguments.get("month"),
                            arguments.get("day"),
                            arguments.get("hour"),
                            arguments.get("minute"),
                            arguments.get("city"),
                            arguments.get("nation"),
                            arguments.get("longitude"),
                            arguments.get("latitude"),
                            arguments.get("tz_str")
                        )
                        
                        response = {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": {
                                "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}],
                                "isError": False
                            }
                        }
                    except Exception as e:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": {
                                "content": [{"type": "text", "text": f"生成报告错误: {str(e)}"}],
                                "isError": True
                            }
                        }
                
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "content": [{"type": "text", "text": f"未知工具: {tool_name}"}],
                            "isError": True
                        }
                    }
            
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32601, "message": "Method not found"}
                }
            
            # 输出响应
            print(json.dumps(response, ensure_ascii=False))
            sys.stdout.flush()
            
        except json.JSONDecodeError:
            print(json.dumps({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"}
            }, ensure_ascii=False))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
            }, ensure_ascii=False))
            sys.stdout.flush()


if __name__ == "__main__":
    main()