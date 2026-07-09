#!/bin/bash
# 云服务器部署脚本

echo "=== 云南省人社厅通知监控 - 云服务器部署脚本 ==="

# 1. 安装Python和依赖
echo "安装Python和依赖..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip

# 2. 克隆或上传项目文件（需要手动配置）
echo "请确保项目文件已上传到服务器"
read -p "项目路径（如：/home/user/rs）: " project_path

cd $project_path

# 3. 安装Python依赖
echo "安装Python依赖..."
pip3 install requests beautifulsoup4 schedule playwright
playwright install chromium

# 4. 设置定时任务
echo "设置定时任务..."
(crontab -l 2>/dev/null; echo "0 10 * * * cd $project_path && python3 monitor.py >> logs/monitor.log 2>&1") | crontab -

# 5. 创建日志目录
mkdir -p logs

# 6. 设置文件权限
chmod +x *.py

echo "=== 部署完成 ==="
echo "定时任务: 每天10:00执行"
echo "日志文件: $project_path/logs/monitor.log"
echo ""
echo "测试运行："
echo "cd $project_path && python3 monitor.py"