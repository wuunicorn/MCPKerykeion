#!/usr/bin/env python3
"""
Kerykeion 占星 MCP 工具
基于 Kerykeion 库计算星座盘并返回 JSON 结果
"""

import json
import sys
import os
import tempfile
from datetime import datetime

try:
    from kerykeion import AstrologicalSubject, KerykeionChartSVG
    from kerykeion import SynastryAspects, NatalAspects
    from kerykeion import CompositeSubjectFactory
except ImportError:
    print("错误: 请先安装 kerykeion 库: pip install kerykeion")
    sys.exit(1)

# 设置临时目录作为缓存目录，避免只读文件系统错误
try:
    # 创建一个临时目录用于缓存
    temp_cache_dir = tempfile.mkdtemp(prefix="kerykeion_cache_")
    
    # 设置多个可能的缓存环境变量
    os.environ['KERYKEION_CACHE_DIR'] = temp_cache_dir
    os.environ['XDG_CACHE_HOME'] = temp_cache_dir
    os.environ['TMPDIR'] = temp_cache_dir
    os.environ['TMP'] = temp_cache_dir
    os.environ['TEMP'] = temp_cache_dir
    os.environ['HOME'] = temp_cache_dir  # 某些库可能使用HOME/.cache
    
    # 创建.cache子目录，因为某些库可能期望这个结构
    cache_subdir = os.path.join(temp_cache_dir, '.cache')
    os.makedirs(cache_subdir, exist_ok=True)
    
    # 设置Python的缓存目录
    os.environ['PYTHONUSERBASE'] = temp_cache_dir
    
except Exception as e:
    # 如果无法创建临时目录，继续执行但可能会遇到缓存问题
    pass


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
        import traceback
        error_msg = str(e) if e and str(e) else "发生未知错误"
        error_details = {
            "error_message": error_msg,
            "error_type": type(e).__name__ if e else "Unknown",
            "traceback": traceback.format_exc()
        }
        return {"success": False, "error": error_msg, "debug_info": error_details}


def load_china_cities():
    """加载中国城市数据"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        cities_file = os.path.join(script_dir, 'china_cities.json')
        with open(cities_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def find_city_coordinates(city_name, nation):
    """查找城市坐标"""
    if nation == 'CN':
        china_cities = load_china_cities()
        # 遍历所有省份和城市
        for province, cities in china_cities.items():
            if city_name in cities:
                city_data = cities[city_name]
                return city_data['latitude'], city_data['longitude']
        
        # 如果没找到，尝试模糊匹配
        for province, cities in china_cities.items():
            for city, data in cities.items():
                if city_name in city or city in city_name:
                    return data['latitude'], data['longitude']
        
        # 特殊处理：丰宁满族自治县属于承德市
        if '丰宁' in city_name and '河北省' in china_cities:
            if '承德' in china_cities['河北省']:
                data = china_cities['河北省']['承德']
                return data['latitude'], data['longitude']
    
    return None, None

def create_astrological_subject(name, year, month, day, hour, minute, city, nation, 
                               longitude=None, latitude=None, tz_str=None,
                               zodiac_type=None, sidereal_mode=None):
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
    
    Returns:
        dict: 包含完整占星数据的字典
    """
    try:
        # 设置默认值
        if zodiac_type is None:
            zodiac_type = "Tropic"
        
        # 如果没有提供经纬度，尝试从本地数据库查找
        if longitude is None or latitude is None:
            found_lat, found_lng = find_city_coordinates(city, nation)
            if found_lat is not None and found_lng is not None:
                latitude = found_lat
                longitude = found_lng
        
        # 为中国城市设置默认时区
        if nation == 'CN' and tz_str is None:
            tz_str = 'Asia/Shanghai'
        
        # 设置临时工作目录，避免缓存问题
        original_cwd = os.getcwd()
        temp_dir = None
        original_env = {}
        
        try:
            # 创建临时工作目录
            temp_dir = tempfile.mkdtemp(prefix="kerykeion_work_")
            os.chdir(temp_dir)
            
            # 备份并重新设置环境变量，确保缓存写入到临时目录
            env_vars_to_set = {
                'KERYKEION_CACHE_DIR': temp_dir,
                'XDG_CACHE_HOME': temp_dir,
                'TMPDIR': temp_dir,
                'TMP': temp_dir,
                'TEMP': temp_dir,
                'PYTHONUSERBASE': temp_dir
            }
            
            for key, value in env_vars_to_set.items():
                original_env[key] = os.environ.get(key)
                os.environ[key] = value
            
            # 创建必要的缓存子目录
            cache_dirs = ['.cache', 'cache', '.kerykeion']
            for cache_dir in cache_dirs:
                cache_path = os.path.join(temp_dir, cache_dir)
                os.makedirs(cache_path, exist_ok=True)
            
            # 创建占星主体对象
            if longitude is not None and latitude is not None:
                # 使用经纬度
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
                # 使用城市名查询（作为备选方案）
                try:
                    subject = AstrologicalSubject(
                        name, year, month, day, hour, minute, city, nation
                    )
                except Exception as city_error:
                    # 如果城市查询失败，返回更详细的错误信息
                    error_msg = str(city_error) if city_error else "未知错误"
                    raise Exception(f"无法找到城市 '{city}' 的地理信息。请提供经纬度坐标或检查城市名称是否正确。原始错误: {error_msg}")
            
            # 使用 Kerykeion 内置的 JSON 序列化功能
            astrological_data = subject.json()
            
        finally:
            # 恢复原始工作目录
            os.chdir(original_cwd)
            
            # 恢复原始环境变量
            for key, original_value in original_env.items():
                if original_value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = original_value
            
            # 清理临时目录
            if temp_dir and os.path.exists(temp_dir):
                try:
                    import shutil
                    shutil.rmtree(temp_dir)
                except:
                    pass
        
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
                "used_coordinates": longitude is not None and latitude is not None
            },
            "astrological_data": astrological_data
        }
        
        return {"success": True, "data": result}
    except Exception as e:
        import traceback
        error_msg = str(e) if e and str(e) else "发生未知错误"
        error_details = {
            "error_message": error_msg,
            "error_type": type(e).__name__ if e else "Unknown",
            "traceback": traceback.format_exc()
        }
        return {"success": False, "error": error_msg, "debug_info": error_details}


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
    # 保存原始工作目录
    original_cwd = os.getcwd()
    temp_dir = None
    original_env = {}
    
    try:
        # 创建临时目录并设置为工作目录
        temp_dir = tempfile.mkdtemp(prefix="kerykeion_natal_")
        os.chdir(temp_dir)
        
        # 备份并重新设置环境变量
        env_vars_to_set = {
            'KERYKEION_CACHE_DIR': temp_dir,
            'XDG_CACHE_HOME': temp_dir,
            'TMPDIR': temp_dir,
            'TMP': temp_dir,
            'TEMP': temp_dir,
            'PYTHONUSERBASE': temp_dir
        }
        
        for key, value in env_vars_to_set.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value
        
        # 创建必要的缓存子目录
        cache_dirs = ['.cache', 'cache', '.kerykeion']
        for cache_dir in cache_dirs:
            cache_path = os.path.join(temp_dir, cache_dir)
            os.makedirs(cache_path, exist_ok=True)
        
        # 如果没有提供经纬度，尝试从本地数据库查找
        if longitude is None or latitude is None:
            coords = find_city_coordinates(city, nation)
            if coords and coords[0] is not None and coords[1] is not None:
                longitude, latitude = coords
        
        # 为中国城市设置默认时区
        if nation == 'CN' and not tz_str:
            tz_str = 'Asia/Shanghai'
        
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
        astrological_data = subject.json()
        
        # 获取本命相位
        natal_aspects = NatalAspects(subject)
        all_aspects = natal_aspects.all_aspects
        
        # 将AspectModel对象转换为可序列化的字典
        serializable_aspects = []
        for aspect in all_aspects:
            if hasattr(aspect, 'model_dump'):
                serializable_aspects.append(aspect.model_dump())
            elif hasattr(aspect, 'dict'):
                serializable_aspects.append(aspect.dict())
            else:
                # 如果是普通字典或其他可序列化对象，直接添加
                serializable_aspects.append(aspect)
        
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
            "aspects": serializable_aspects
        }
        
        return {"success": True, "data": result}
    except Exception as e:
        import traceback
        error_msg = str(e) if e and str(e) and str(e) != "None" else "发生未知错误"
        error_details = {
            "error_message": error_msg,
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        return {"success": False, "error": error_msg, "debug_info": error_details}
    finally:
        # 恢复原始工作目录
        os.chdir(original_cwd)
        
        # 恢复原始环境变量
        for key, original_value in original_env.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value
        
        # 清理临时目录
        if temp_dir and os.path.exists(temp_dir):
            try:
                import shutil
                shutil.rmtree(temp_dir)
            except:
                pass


def get_synastry_aspects(person1_data, person2_data):
    """获取合盘相位信息
    
    Args:
        person1_data: 第一个人的出生信息字典
        person2_data: 第二个人的出生信息字典
    
    Returns:
        dict: 包含合盘相位信息的字典
    """
    try:
        # 设置临时工作目录，避免缓存问题
        original_cwd = os.getcwd()
        temp_dir = None
        
        try:
            # 创建临时工作目录
            temp_dir = tempfile.mkdtemp(prefix="kerykeion_synastry_")
            os.chdir(temp_dir)
            
            # 为中国城市设置默认时区
            p1 = person1_data.copy()
            p2 = person2_data.copy()
            
            if p1.get('nation') == 'CN' and not p1.get('tz_str'):
                p1['tz_str'] = 'Asia/Shanghai'
            if p2.get('nation') == 'CN' and not p2.get('tz_str'):
                p2['tz_str'] = 'Asia/Shanghai'
            
            # 创建第一个人的占星主体对象
            if p1.get('longitude') is not None and p1.get('latitude') is not None:
                if p1.get('tz_str'):
                    subject1 = AstrologicalSubject(
                        p1['name'], p1['year'], p1['month'], p1['day'], p1['hour'], p1['minute'],
                        lng=p1['longitude'], lat=p1['latitude'], tz_str=p1['tz_str'], city=p1.get('city', '')
                    )
                else:
                    subject1 = AstrologicalSubject(
                        p1['name'], p1['year'], p1['month'], p1['day'], p1['hour'], p1['minute'],
                        lng=p1['longitude'], lat=p1['latitude'], city=p1.get('city', '')
                    )
            else:
                # 尝试从本地数据库查找城市坐标
                found_lat, found_lng = find_city_coordinates(p1.get('city', ''), p1.get('nation', ''))
                if found_lat is not None and found_lng is not None:
                    if p1.get('tz_str'):
                        subject1 = AstrologicalSubject(
                            p1['name'], p1['year'], p1['month'], p1['day'], p1['hour'], p1['minute'],
                            lng=found_lng, lat=found_lat, tz_str=p1['tz_str'], city=p1.get('city', '')
                        )
                    else:
                        subject1 = AstrologicalSubject(
                            p1['name'], p1['year'], p1['month'], p1['day'], p1['hour'], p1['minute'],
                            lng=found_lng, lat=found_lat, city=p1.get('city', '')
                        )
                else:
                    subject1 = AstrologicalSubject(
                        p1['name'], p1['year'], p1['month'], p1['day'], p1['hour'], p1['minute'],
                        p1.get('city', ''), p1.get('nation', '')
                    )
            
            # 创建第二个人的占星主体对象
            if p2.get('longitude') is not None and p2.get('latitude') is not None:
                if p2.get('tz_str'):
                    subject2 = AstrologicalSubject(
                        p2['name'], p2['year'], p2['month'], p2['day'], p2['hour'], p2['minute'],
                        lng=p2['longitude'], lat=p2['latitude'], tz_str=p2['tz_str'], city=p2.get('city', '')
                    )
                else:
                    subject2 = AstrologicalSubject(
                        p2['name'], p2['year'], p2['month'], p2['day'], p2['hour'], p2['minute'],
                        lng=p2['longitude'], lat=p2['latitude'], city=p2.get('city', '')
                    )
            else:
                # 尝试从本地数据库查找城市坐标
                found_lat, found_lng = find_city_coordinates(p2.get('city', ''), p2.get('nation', ''))
                if found_lat is not None and found_lng is not None:
                    if p2.get('tz_str'):
                        subject2 = AstrologicalSubject(
                            p2['name'], p2['year'], p2['month'], p2['day'], p2['hour'], p2['minute'],
                            lng=found_lng, lat=found_lat, tz_str=p2['tz_str'], city=p2.get('city', '')
                        )
                    else:
                        subject2 = AstrologicalSubject(
                            p2['name'], p2['year'], p2['month'], p2['day'], p2['hour'], p2['minute'],
                            lng=found_lng, lat=found_lat, city=p2.get('city', '')
                        )
                else:
                    subject2 = AstrologicalSubject(
                        p2['name'], p2['year'], p2['month'], p2['day'], p2['hour'], p2['minute'],
                        p2.get('city', ''), p2.get('nation', '')
                    )
        
            # 使用 Kerykeion 内置的 JSON 序列化功能获取基础数据
            person1_astrological_data = subject1.json()
            person2_astrological_data = subject2.json()
            
            # 获取合盘相位
            synastry_aspects = SynastryAspects(subject1, subject2)
            relevant_aspects = synastry_aspects.all_aspects
            
            # 将AspectModel对象转换为可序列化的字典
            serializable_aspects = []
            for aspect in relevant_aspects:
                if hasattr(aspect, 'model_dump'):
                    serializable_aspects.append(aspect.model_dump())
                elif hasattr(aspect, 'dict'):
                    serializable_aspects.append(aspect.dict())
                else:
                    # 如果是普通字典或其他可序列化对象，直接添加
                    serializable_aspects.append(aspect)
            
            result = {
                "person1_input": person1_data,
                "person2_input": person2_data,
                "person1_astrological_data": person1_astrological_data,
                "person2_astrological_data": person2_astrological_data,
                "aspects_count": len(relevant_aspects),
                "aspects": serializable_aspects
            }
            
            return {"success": True, "data": result}
        
        finally:
            # 恢复原始工作目录并清理临时目录
            os.chdir(original_cwd)
            if temp_dir and os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    except Exception as e:
        import traceback
        error_msg = str(e) if e and str(e) else "发生未知错误"
        error_details = {
            "error_message": error_msg,
            "error_type": type(e).__name__ if e else "Unknown",
            "traceback": traceback.format_exc()
        }
        return {"success": False, "error": error_msg, "debug_info": error_details}


def create_composite_chart(person1_data, person2_data):
    """创建组合盘（中点合成盘）
    
    Args:
        person1_data: 第一个人的出生信息字典
        person2_data: 第二个人的出生信息字典
    
    Returns:
        dict: 包含组合盘信息的字典
    """
    try:
        # 设置临时工作目录，避免缓存问题
        original_cwd = os.getcwd()
        temp_dir = None
        
        try:
            # 创建临时工作目录
            temp_dir = tempfile.mkdtemp(prefix="kerykeion_composite_")
            os.chdir(temp_dir)
            
            # 为中国城市设置默认时区
            p1 = person1_data.copy()
            p2 = person2_data.copy()
            
            if p1.get('nation') == 'CN' and not p1.get('tz_str'):
                p1['tz_str'] = 'Asia/Shanghai'
            if p2.get('nation') == 'CN' and not p2.get('tz_str'):
                p2['tz_str'] = 'Asia/Shanghai'
            
            # 创建第一个人的占星主体对象
            if p1.get('longitude') is not None and p1.get('latitude') is not None:
                if p1.get('tz_str'):
                    subject1 = AstrologicalSubject(
                        p1['name'], p1['year'], p1['month'], p1['day'], p1['hour'], p1['minute'],
                        lng=p1['longitude'], lat=p1['latitude'], tz_str=p1['tz_str'], city=p1.get('city', '')
                    )
                else:
                    subject1 = AstrologicalSubject(
                        p1['name'], p1['year'], p1['month'], p1['day'], p1['hour'], p1['minute'],
                        lng=p1['longitude'], lat=p1['latitude'], city=p1.get('city', '')
                    )
            else:
                # 尝试从本地数据库查找城市坐标
                found_lat, found_lng = find_city_coordinates(p1.get('city', ''), p1.get('nation', ''))
                if found_lat is not None and found_lng is not None:
                    if p1.get('tz_str'):
                        subject1 = AstrologicalSubject(
                            p1['name'], p1['year'], p1['month'], p1['day'], p1['hour'], p1['minute'],
                            lng=found_lng, lat=found_lat, tz_str=p1['tz_str'], city=p1.get('city', '')
                        )
                    else:
                        subject1 = AstrologicalSubject(
                            p1['name'], p1['year'], p1['month'], p1['day'], p1['hour'], p1['minute'],
                            lng=found_lng, lat=found_lat, city=p1.get('city', '')
                        )
                else:
                    subject1 = AstrologicalSubject(
                        p1['name'], p1['year'], p1['month'], p1['day'], p1['hour'], p1['minute'],
                        p1.get('city', ''), p1.get('nation', '')
                    )
            
            # 创建第二个人的占星主体对象
            if p2.get('longitude') is not None and p2.get('latitude') is not None:
                if p2.get('tz_str'):
                    subject2 = AstrologicalSubject(
                        p2['name'], p2['year'], p2['month'], p2['day'], p2['hour'], p2['minute'],
                        lng=p2['longitude'], lat=p2['latitude'], tz_str=p2['tz_str'], city=p2.get('city', '')
                    )
                else:
                    subject2 = AstrologicalSubject(
                        p2['name'], p2['year'], p2['month'], p2['day'], p2['hour'], p2['minute'],
                        lng=p2['longitude'], lat=p2['latitude'], city=p2.get('city', '')
                    )
            else:
                # 尝试从本地数据库查找城市坐标
                found_lat, found_lng = find_city_coordinates(p2.get('city', ''), p2.get('nation', ''))
                if found_lat is not None and found_lng is not None:
                    if p2.get('tz_str'):
                        subject2 = AstrologicalSubject(
                            p2['name'], p2['year'], p2['month'], p2['day'], p2['hour'], p2['minute'],
                            lng=found_lng, lat=found_lat, tz_str=p2['tz_str'], city=p2.get('city', '')
                        )
                    else:
                        subject2 = AstrologicalSubject(
                            p2['name'], p2['year'], p2['month'], p2['day'], p2['hour'], p2['minute'],
                            lng=found_lng, lat=found_lat, city=p2.get('city', '')
                        )
                else:
                    subject2 = AstrologicalSubject(
                        p2['name'], p2['year'], p2['month'], p2['day'], p2['hour'], p2['minute'],
                        p2.get('city', ''), p2.get('nation', '')
                    )
        
            # 创建组合盘工厂
            factory = CompositeSubjectFactory(subject1, subject2)
            composite_model = factory.get_midpoint_composite_subject_model()
            
            # 使用 Kerykeion 内置的 JSON 序列化功能获取基础数据
            person1_astrological_data = subject1.json()
            person2_astrological_data = subject2.json()
            composite_astrological_data = composite_model.json()
            
            result = {
                "person1_input": person1_data,
                "person2_input": person2_data,
                "person1_astrological_data": person1_astrological_data,
                "person2_astrological_data": person2_astrological_data,
                "composite_name": f"{subject1.name} & {subject2.name} Composite",
                "composite_astrological_data": composite_astrological_data
            }
            
            return {"success": True, "data": result}
        
        finally:
            # 恢复原始工作目录并清理临时目录
            os.chdir(original_cwd)
            if temp_dir and os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    except Exception as e:
        import traceback
        error_msg = str(e) if e and str(e) else "发生未知错误"
        error_details = {
            "error_message": error_msg,
            "error_type": type(e).__name__ if e else "Unknown",
            "traceback": traceback.format_exc()
        }
        return {"success": False, "error": error_msg, "debug_info": error_details}





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
                                            "enum": ["Tropical", "Sidereal"]
                                        },
                                        "sidereal_mode": {
                                            "type": "string",
                                            "description": "恒星模式（当 zodiac_type 为 Sidereal 时使用）"
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
                            arguments.get("sidereal_mode", "LAHIRI")
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