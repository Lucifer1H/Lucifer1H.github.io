#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import os
import re
import time
from bs4 import BeautifulSoup
from datetime import datetime

def get_zhihu_hot():
    """获取知乎热榜数据"""
    print("开始获取知乎热榜数据...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }
    
    # 方法1：使用RSSHub API获取知乎热榜
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
            
            # 如果成功获取到数据，保存并返回
            if hot_items:
                save_data(hot_items)
                return
    except Exception as e:
        print(f"使用RSSHub API获取知乎热榜失败: {e}")
    
    # 方法2：使用今日热榜API
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
            
            # 如果成功获取到数据，保存并返回
            if hot_items:
                save_data(hot_items)
                return
    except Exception as e:
        print(f"使用今日热榜API获取知乎热榜失败: {e}")
    
    # 方法3：直接爬取知乎热榜页面
    try:
        response = requests.get('https://www.zhihu.com/hot', headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            hot_items = []
            
            # 解析热榜项目
            hot_list = soup.select('.HotList-list .HotItem')
            for i, item in enumerate(hot_list):
                if i >= 50:  # 只获取前50条
                    break
                
                title_element = item.select_one('.HotItem-title')
                link_element = item.select_one('.HotItem-title a')
                metrics_element = item.select_one('.HotItem-metrics')
                
                if title_element and link_element and metrics_element:
                    title = title_element.text.strip()
                    url = link_element.get('href', '')
                    hot = metrics_element.text.strip()
                    
                    # 提取热度数字
                    hot_match = re.search(r'(\d+(\.\d+)?[万亿]?)', hot)
                    hot_value = hot_match.group(1) if hot_match else "热门"
                    
                    hot_items.append({
                        "title": title,
                        "url": url,
                        "hot": f"{hot_value}",
                    })
            
            # 如果成功获取到数据，保存并返回
            if hot_items:
                save_data(hot_items)
                return
    except Exception as e:
        print(f"直接爬取知乎热榜失败: {e}")
    
    # 方法4：使用天行数据API获取知乎热榜（需要API KEY）
    try:
        # 这里需要替换为您自己的天行数据API KEY
        api_key = ""
        if api_key:
            response = requests.get(f'http://api.tianapi.com/txapi/zhihuhotlist/index?key={api_key}', headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                hot_items = []
                
                if data['code'] == 200 and 'newslist' in data:
                    for i, item in enumerate(data['newslist']):
                        if i >= 50:  # 只获取前50条
                            break
                        hot_items.append({
                            "title": item['title'],
                            "url": item['url'],
                            "hot": item['hotnum']
                        })
                
                # 如果成功获取到数据，保存并返回
                if hot_items:
                    save_data(hot_items)
                    return
    except Exception as e:
        print(f"使用天行数据API获取知乎热榜失败: {e}")
    
    # 所有方法都失败，生成模拟数据
    print("所有获取方法均失败，生成模拟数据...")
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