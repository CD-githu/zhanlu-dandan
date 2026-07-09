# 云南省人社厅通知监控工具 🚀

自动监控云南省人社厅、人事考试网、人才服务平台的通知，钉钉自动推送，GitHub Actions云端运行。

## ✨ 功能特性

- 🔄 **自动抓取**：5个数据源，每日定时抓取
- 🎯 **智能过滤**：关键词筛选，只推相关通知  
- 📢 **钉钉推送**：自动推送到钉钉群
- 💾 **增量去重**：只推新通知，避免重复
- ☁️ **云端运行**：GitHub Actions，24小时稳定运行
- 🎨 **易于配置**：JSON配置，修改即生效

## 🛠️ 技术栈

- **Python 3.11+**：核心开发语言
- **Requests + BeautifulSoup4**：网页抓取
- **Playwright**：动态页面渲染
- **GitHub Actions**：CI/CD自动化
- **SQLite**：轻量级数据库
- **钉钉机器人**：消息推送

## 📦 快速启动

### 方式1：GitHub Actions（推荐）

#### 1️⃣ 创建GitHub仓库
1. 访问 https://github.com/new
2. 创建新仓库 `hrss-monitor`
3. 选择公开或私有
4. 点击创建

#### 2️⃣ 上传代码
```bash
cd D:\Token\zhanlu\git
git init
git add .
git commit -m "Initial commit: HRSS notification monitor"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/hrss-monitor.git
git push -u origin main
```

#### 3️⃣ 启用GitHub Actions
- 访问仓库的 `Actions` 标签页
- 启用工作流
- 点击 `Run workflow` 测试运行

#### 4️⃣ 配置定时任务
- 编辑 `.github/workflows/hrss-monitor.yml`
- 修改 `cron` 表达式设置执行时间
- 推送配置到GitHub

### 方式2：本地运行

```bash
# 安装依赖
pip install -r requirements.txt
playwright install chromium

# 运行脚本
python monitor.py
```

## ⚙️ 配置说明

### 钉钉机器人配置
编辑 `config.json`：
```json
{
  "push": {
    "type": "dingtalk",
    "dingtalk_token": "你的access_token"
  }
}
```

### 关键词配置
```json
{
  "keywords": [
    "职称", "评审", "申报", "资格", "认定",
    "考试", "报名", "笔试", "面试", "聘用"
  ]
}
```

### 定时任务配置
```yaml
# .github/workflows/hrss-monitor.yml
schedule:
  - cron: '0 2 * * *'  # 北京时间 10:00
```

## 📊 数据源

| 数据源 | URL | 特点 |
|--------|-----|------|
| 人社厅通知 | http://hrss.yn.gov.cn | 正式公告 |
| 人事考试网 | https://hrss.yn.gov.cn/ynrsksw | 考试动态 |
| 人才服务平台 | https://zwfw.hrss.yn.gov.cn | 职称评审 |

## 🔍 使用指南

### 查看运行记录
1. 访问 GitHub 仓库
2. 点击 `Actions` 标签
3. 查看工作流运行记录
4. 点击具体记录查看详细日志

### 手动触发测试
1. 进入 `Actions` 标签
2. 选择 `HRSS Notification Monitor`
3. 点击 `Run workflow` 按钮
4. 选择分支并运行

### 修改推送时间
编辑 `.github/workflows/hrss-monitor.yml`：
```yaml
# 常用时间配置
'0 2 * * *'   # 北京时间 10:00
'0 6 * * *'   # 北京时间 14:00  
'0 10 * * *'  # 北京时间 18:00
'*/30 * * * *' # 每30分钟（仅开发使用）
```

## 🐛 故障排除

### GitHub Actions不运行
- 检查 Actions 是否启用
- 确认仓库设置允许 Actions
- 查看配置文件语法是否正确

### 钉钉推送失败
- 验证 access_token 是否正确
- 检查机器人安全设置
- 确认机器人是否在群中

### 抓取数据失败
- 查看Actions日志错误信息
- 检查目标网站是否变更结构
- 验证网络连接是否正常

## ⚠️ 重要限制

### GitHub Actions限制
- 免费：每月 2000 分钟
- 推荐：每日 1-2 次运行
- 适用：通知监控场景

### 钉钉限制
- 每分钟：最多 20 条消息
- 消息：自动分批推送
- 建议：设置"加签"安全策略

## 📈 项目结构

```
rs/
├── .github/workflows/
│   └── hrss-monitor.yml    # GitHub Actions配置
├── data/
│   └── notifications.db    # SQLite数据库
├── config.json             # 配置文件
├── spider.py               # 爬虫模块
├── filter.py               # 过滤模块
├── notifier.py             # 推送模块
├── storage.py              # 数据存储模块
├── monitor.py              # 主程序
└── requirements.txt        # Python依赖
```

## 🚀 下一步

1. ✅ 上传代码到GitHub
2. ✅ 启用GitHub Actions工作流
3. ✅ 配置钉钉机器人access_token
4. ✅ 测试运行，确认推送正常
5. ✅ 设置每日定时任务

## 📝 更新日志

- **2026-07-09**：初始版本
  - 支持5个数据源
  - 钉钉自动推送
  - GitHub Actions配置
  - 增量去重机制

---

**永不掉线，自动推送！** 🎯