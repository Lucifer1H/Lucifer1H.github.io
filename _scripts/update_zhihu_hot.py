#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import os
import re
import time
from bs4 import BeautifulSoup
from datetime import datetime

def get_zhihu_hot_from_whyapi():
    print("尝试从WhyAPI获取知乎热榜数据...")
    try:
        api_key = "36de5db81215" # Your provided API Key
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(f'https://whyta.cn/api/zhihu?key={api_key}', headers=headers, timeout=15)
        
        if response.status_code == 200:
            try:
                api_data_list = response.json()
            except json.JSONDecodeError:
                 print("从WhyAPI获取知乎热榜数据时解析JSON失败 (initial parse)")
                 return None

            processed_items = []
            items_to_process = [] 

            if isinstance(api_data_list, list):
                items_to_process = api_data_list
            elif isinstance(api_data_list, dict):
                if 'items' in api_data_list and isinstance(api_data_list.get('items'), list): # Prioritize 'items' key
                    items_to_process = api_data_list['items']
                elif 'data' in api_data_list and isinstance(api_data_list.get('data'), list):
                    items_to_process = api_data_list['data']
                elif 'list' in api_data_list and isinstance(api_data_list.get('list'), list):
                    items_to_process = api_data_list['list']
                elif 'result' in api_data_list and isinstance(api_data_list.get('result'), list):
                    items_to_process = api_data_list['result']
                elif "title" in api_data_list and "url" in api_data_list: 
                    processed_items.append({
                        "title": api_data_list.get("title"),
                        "url": api_data_list.get("url"),
                        "hot": api_data_list.get("extra", {}).get("info", "热门") 
                    })
                else:
                    print(f"WhyAPI返回数据格式未能识别为列表或有效单项: {api_data_list}")
                    return None
            else:
                print(f"WhyAPI返回数据类型不是列表或字典: {type(api_data_list)}")
                return None


            if not processed_items and items_to_process:
                for i, item in enumerate(items_to_process):
                    if i >= 50:
                        break
                    title = item.get("title")
                    url = item.get("url")
                    hot = item.get("extra", {}).get("info", "热门") 
                    
                    if isinstance(hot, (int, float)):
                        hot = str(hot)

                    if title and url:
                        processed_items.append({
                            "title": title,
                            "url": url,
                            "hot": hot 
                        })
            
            if processed_items:
                print(f"成功从WhyAPI获取到 {len(processed_items)} 条知乎热榜数据")
                return processed_items
            else:
                print("WhyAPI获取成功但未能提取有效数据或数据为空")

        else:
            print(f"请求WhyAPI失败，状态码: {response.status_code}, 内容: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print("从WhyAPI获取知乎热榜数据超时")
    except requests.exceptions.RequestException as e:
        print(f"从WhyAPI获取知乎热榜数据时发生网络请求错误: {e}")
    except Exception as e:
        print(f"从WhyAPI获取知乎热榜数据时发生未知错误: {e}")
    return None

def get_zhihu_hot():
    """获取知乎热榜数据"""
    print("开始获取知乎热榜数据...")
    
    # 方法1：尝试从WhyAPI获取
    whyapi_items = get_zhihu_hot_from_whyapi()
    if whyapi_items:
        save_data(whyapi_items)
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
                if i >= 50:
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
                    if i >= 50:
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
        print(f"使用今日热榜API获取知乎热榜失败: {e}")
    
    # 方法4：直接爬取知乎热榜页面
    print("尝试直接爬取知乎热榜页面...")
    try:
        response = requests.get('https://www.zhihu.com/hot', headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            hot_items = []
            
            hot_list = soup.select('.HotList-list .HotItem')
            for i, item in enumerate(hot_list):
                if i >= 50: 
                    break
                
                title_element = item.select_one('.HotItem-title')
                link_element = item.select_one('.HotItem-title a')
                metrics_element = item.select_one('.HotItem-metrics')
                
                if title_element and link_element and metrics_element:
                    title = title_element.text.strip()
                    url = link_element.get('href', '')
                    if not url.startswith('http'):
                        url = 'https://www.zhihu.com' + url if url.startswith('/') else 'https://www.zhihu.com/question/' + url

                    hot = metrics_element.text.strip()
                    
                    hot_match = re.search(r'(\d+(\.\d+)?[万亿]?热度)', hot)
                    hot_value = hot_match.group(1) if hot_match else hot

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
        api_key = os.environ.get('TIANXING_API_KEY', "")
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
                            "hot": str(item.get('hotnum', '热门'))
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

    print(f"将要保存的数据中的 update_time: {data['update_time']}")
    if items:
        print(f"将要保存的数据中的第一条新闻标题: {items[0].get('title', '无标题')}")
    else:
        print("将要保存的新闻列表为空")
    
    # 获取脚本所在的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取项目根目录 (脚本目录的上一级)
    project_root = os.path.dirname(script_dir)

    source_data_path = os.path.join(project_root, 'source', '_data')
    public_data_path = os.path.join(project_root, 'public', 'data')

    os.makedirs(source_data_path, exist_ok=True)
    os.makedirs(public_data_path, exist_ok=True)
    
    source_json_path = os.path.join(source_data_path, 'zhihu.json')
    public_json_path = os.path.join(public_data_path, 'zhihu.json')

    with open(source_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    with open(public_json_path, 'w', encoding='utf-8') as f:
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