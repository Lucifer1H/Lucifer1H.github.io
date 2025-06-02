#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import os
import re
import time
from bs4 import BeautifulSoup
from datetime import datetime

def get_zhihu_hot_from_tenapi():
    print("尝试从TenAPI获取知乎热榜数据...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get('https://tenapi.cn/v2/zhihuhot', headers=headers, timeout=15) # Increased timeout slightly
        if response.status_code == 200:
            api_data = response.json()
            if api_data.get("code") == 200 and "data" in api_data:
                hot_items = []
                for i, item in enumerate(api_data["data"]):
                    if i >= 50: # 只获取前50条
                        break
                    hot_items.append({
                        "title": item.get("name"),
                        "url": item.get("url"),
                        "hot": item.get("hot")
                    })
                if hot_items:
                    print(f"成功从TenAPI获取到 {len(hot_items)} 条知乎热榜数据")
                    return hot_items
            else:
                print(f"TenAPI返回数据格式错误或获取失败: {api_data.get('msg', '未知错误')}")
        else:
            print(f"请求TenAPI失败，状态码: {response.status_code}")
    except requests.exceptions.Timeout:
        print("从TenAPI获取知乎热榜数据超时")
    except requests.exceptions.RequestException as e:
        print(f"从TenAPI获取知乎热榜数据时发生网络请求错误: {e}")
    except json.JSONDecodeError:
        print("从TenAPI获取知乎热榜数据时解析JSON失败")
    except Exception as e:
        print(f"从TenAPI获取知乎热榜数据时发生未知错误: {e}")
    return None

def get_zhihu_hot():
    """获取知乎热榜数据"""
    print("开始获取知乎热榜数据...")
    
    # 方法1：尝试从TenAPI获取
    tenapi_items = get_zhihu_hot_from_tenapi()
    if tenapi_items:
        save_data(tenapi_items)
        return

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }
    
    # 方法2：使用RSSHub API获取知乎热榜
    print("尝试从RSSHub API获取知乎热榜...")
    try:
        response = requests.get('https://rsshub.app/zhihu/hotlist/api', headers=headers, timeout=10)
        if response.status_code == 200:
            hot_items = []
            data = response.json()
            
            for i, item in enumerate(data['data']):
                if i >= 50:  # 只获取前50条
                    break
                hot_items.append({
                    "title": item['target']['title'],
                    "url": item['target']['url'],
                    "hot": f"{item['detail_text']}",
                })
            
            if hot_items:
                print(f"成功从RSSHub API获取到 {len(hot_items)} 条知乎热榜数据")
                save_data(hot_items)
                return
    except Exception as e:
        print(f"使用RSSHub API获取知乎热榜失败: {e}")
    
    # 方法3：使用今日热榜API
    print("尝试从今日热榜API获取知乎热榜...")
    try:
        response = requests.get('https://api.tophub.today/v2/GetAllInfoGzip?id=1&page=0', headers=headers, timeout=10)
        if response.status_code == 200:
            hot_items = []
            data = response.json()
            
            if 'data' in data and 'list' in data['data']:
                for i, item in enumerate(data['data']['list']):
                    if i >= 50:  # 只获取前50条
                        break
                    title = item.get('title', '')
                    url = item.get('url', '')
                    hot = item.get('hot', '')
                    
                    if title and url:
                        hot_items.append({
                            "title": title,
                            "url": url,
                            "hot": hot if hot else "热门"
                        })
            
            if hot_items:
                print(f"成功从今日热榜API获取到 {len(hot_items)} 条知乎热榜数据")
                save_data(hot_items)
                return
    except Exception as e:
        print(f"使用今日热榜API获取知乎热榜失败: {e}") # 这里之前有域名解析错误 NameResolutionError
    
    # 方法4：直接爬取知乎热榜页面
    print("尝试直接爬取知乎热榜页面...")
    try:
        response = requests.get('https://www.zhihu.com/hot', headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            hot_items = []
            
            hot_list = soup.select('.HotList-list .HotItem') # 可能需要根据知乎页面更新选择器
            for i, item in enumerate(hot_list):
                if i >= 50: 
                    break
                
                title_element = item.select_one('.HotItem-title')
                link_element = item.select_one('.HotItem-title a') # 通常链接在标题内
                metrics_element = item.select_one('.HotItem-metrics')
                
                if title_element and link_element and metrics_element:
                    title = title_element.text.strip()
                    url = link_element.get('href', '')
                    if not url.startswith('http'): # 确保URL是完整的
                        url = 'https://www.zhihu.com' + url if url.startswith('/') else 'https://www.zhihu.com/question/' + url

                    hot = metrics_element.text.strip()
                    
                    hot_match = re.search(r'(\\d+(\\.\\d+)?[万亿]?热度)', hot) # 尝试匹配更精确的热度格式
                    hot_value = hot_match.group(1) if hot_match else hot # 如果匹配失败，保留原始metrics

                    hot_items.append({
                        "title": title,
                        "url": url,
                        "hot": hot_value,
                    })
            
            if hot_items:
                print(f"成功直接爬取到 {len(hot_items)} 条知乎热榜数据")
                save_data(hot_items)
                return
    except Exception as e:
        print(f"直接爬取知乎热榜失败: {e}")
    
    # 方法5：使用天行数据API获取知乎热榜（需要API KEY）
    print("尝试从天行数据API获取知乎热榜...")
    try:
        api_key = os.environ.get('TIANXING_API_KEY', "") # 尝试从环境变量获取API Key
        if api_key:
            response = requests.get(f'http://api.tianapi.com/txapi/zhihuhotlist/index?key={api_key}', headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                hot_items = []
                
                if data.get('code') == 200 and 'newslist' in data:
                    for i, item in enumerate(data['newslist']):
                        if i >= 50:
                            break
                        hot_items.append({
                            "title": item['title'],
                            "url": item['url'],
                            "hot": str(item.get('hotnum', '热门')) # 确保hot是字符串
                        })
                
                if hot_items:
                    print(f"成功从天行数据API获取到 {len(hot_items)} 条知乎热榜数据")
                    save_data(hot_items)
                    return
                elif data.get('code') != 200:
                     print(f"天行数据API返回错误: {data.get('msg', '未知错误')}")
            else:
                print(f"请求天行数据API失败，状态码: {response.status_code}")
        else:
            print("天行数据API Key未配置，跳过此方法。")
    except Exception as e:
        print(f"使用天行数据API获取知乎热榜失败: {e}")
    
    print("所有真实数据获取方法均失败，生成模拟数据...")
    generate_mock_data()

def save_data(items):
    """保存数据到JSON文件"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    data = {
        "title": "知乎热榜",
        "list": items,
        "update_time": current_time
    }
    
    # 确保目录存在
    os.makedirs('source/_data', exist_ok=True)
    os.makedirs('public/data', exist_ok=True)
    
    # 保存到source/_data目录
    with open('source/_data/zhihu.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 保存到public/data目录
    with open('public/data/zhihu.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"成功获取并保存了{len(items)}条知乎热榜数据")

def generate_mock_data():
    """生成模拟数据"""
    mock_items = [
        {
            "title": "2025年全球经济展望如何？各国经济复苏情况怎样？",
            "url": "https://www.zhihu.com/search?q=全球经济展望",
            "hot": "9999+"
        },
        {
            "title": "人工智能技术的最新突破会给社会带来哪些影响？",
            "url": "https://www.zhihu.com/search?q=人工智能技术突破",
            "hot": "8888+"
        },
        {
            "title": "如何看待近期全球气候变化带来的极端天气事件？",
            "url": "https://www.zhihu.com/search?q=全球气候变化",
            "hot": "7777+"
        },
        {
            "title": "新能源汽车市场竞争加剧，传统车企如何应对？",
            "url": "https://www.zhihu.com/search?q=新能源汽车市场",
            "hot": "6666+"
        },
        {
            "title": "数字人民币全面推广后会给日常生活带来哪些变化？",
            "url": "https://www.zhihu.com/search?q=数字人民币",
            "hot": "5555+"
        },
        {
            "title": "远程办公成为常态，企业如何有效管理分散的团队？",
            "url": "https://www.zhihu.com/search?q=远程办公管理",
            "hot": "4444+"
        },
        {
            "title": "如何评价最新发布的量子计算突破？",
            "url": "https://www.zhihu.com/search?q=量子计算突破",
            "hot": "3333+"
        },
        {
            "title": "元宇宙概念持续升温，现实应用前景如何？",
            "url": "https://www.zhihu.com/search?q=元宇宙应用",
            "hot": "2222+"
        },
        {
            "title": "年轻人为什么越来越注重工作与生活的平衡？",
            "url": "https://www.zhihu.com/search?q=工作生活平衡",
            "hot": "1111+"
        },
        {
            "title": "健康生活方式成为新潮流，如何科学饮食和运动？",
            "url": "https://www.zhihu.com/search?q=科学饮食运动",
            "hot": "999+"
        }
    ]
    
    save_data(mock_items)

if __name__ == "__main__":
    get_zhihu_hot() 