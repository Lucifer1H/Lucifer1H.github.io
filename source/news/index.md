---
title: 今日热榜
date: 2025-06-01 12:00:00
layout: news
---

## 今日热榜
<p id="update-time"></p>

<div id='zhihu-container'>
  <div class="zhihu-list">
    <!-- 知乎热榜内容将通过JS动态加载 -->
  </div>
</div>

<style>
#zhihu-container{
  width: 100%; 
  height: 500px;
  font-size: 95%;
  overflow-y: auto;
  -ms-overflow-style: none;
  scrollbar-width: none;
}
#zhihu-container::-webkit-scrollbar{
  display: none;
}
.zhihu-list-item{
  display: flex;
  justify-content: space-between;
  flex-direction: row;
  flex-wrap: nowrap;
  margin-bottom: 10px;
  padding-bottom: 5px;
  border-bottom: 1px solid #eaecef;
}
.zhihu-title{
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-right: auto;
}
.zhihu-hot{
  flex-shrink: 0;
  color: #ff6b81;
}
.zhihu-hotness{
  display: inline-block;
  padding: 0 6px;
  transform: scale(.8) translateX(-3px);
  font-weight: bold;
  color: #fff;
  border-top: rgba(255, 255, 255, 0.87) 1px solid;
  border-left: rgba(255, 255, 255, 0.87) 1px solid;
  background: linear-gradient(to bottom right, #348AC7, #7474BF);
  border-radius: 8px;
}
#update-time {
  font-size: 0.9em;
  color: #888;
  margin-bottom: 15px;
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
  // 从JSON文件加载知乎热榜数据
  fetch('/data/zhihu.json')
    .then(response => response.json())
    .then(data => {
      // 显示更新时间
      if (data.update_time) {
        document.getElementById('update-time').innerText = '最后更新: ' + data.update_time;
      }
      console.log('知乎热榜数据:', data);
      
      let html = '';
      html += '<div class="zhihu-list">';
      var i = 1;
      console.log('开始生成列表HTML, data.list:', data.list);
      if (data.list && Array.isArray(data.list)) {
        for (let item of data.list) {
          console.log('正在处理 item:', item);
          html += '<div class="zhihu-list-item"><div class="zhihu-hotness">' + i + '</div>' + 
                  '<span class="zhihu-title"><a title="' + item.title + '"href="' + item.url + 
                  '" target="_blank" rel="external nofollow noreferrer">' + item.title + '</a></span>' + 
                  '<div class="zhihu-hot"><span>' + item.hot + '</span></div></div>';
          i++;
        }
      } else {
        console.error('data.list 不是一个有效的数组:', data.list);
      }
      html += '</div>';
      console.log('生成的HTML:', html);
      document.getElementById('zhihu-container').innerHTML = html;
      console.log('innerHTML 已设置');
    })
    .catch(function(error) {
      console.log('加载知乎热榜数据失败:', error);
      document.getElementById('zhihu-container').innerHTML = '<p>加载知乎热榜数据失败，请稍后再试。</p>';
    });
});
</script>

## 更多热榜

- [热门文章](/news/hot-article) 