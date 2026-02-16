#!/bin/bash

# -*- coding: utf-8 -*-
# 春节祝福语生成器启动脚本

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "  春节祝福语生成器启动脚本"
echo "========================================"
echo ""

# 设置环境变量
export API_URL="API_URL"
export MODEL_NAME="MODEL_NAME"
export API_KEY="API_KEY"

# 检查环境变量是否设置成功
if [ -z "$API_URL" ]; then
    echo -e "${RED}错误: API_URL 环境变量未设置${NC}"
    exit 1
fi

if [ -z "$MODEL_NAME" ]; then
    echo -e "${RED}错误: MODEL_NAME 环境变量未设置${NC}"
    exit 1
fi

if [ -z "$API_KEY" ]; then
    echo -e "${RED}错误: API_KEY 环境变量未设置${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 环境变量设置成功${NC}"
echo -e "${YELLOW}API_URL:${NC} $API_URL"
echo -e "${YELLOW}MODEL_NAME:${NC} $MODEL_NAME"
echo -e "${YELLOW}API_KEY:${NC} ${API_KEY:0:10}...${API_KEY: -10}"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 Python3，请先安装 Python3${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python3 已安装: $(python3 --version)${NC}"
echo ""

# 检查是否在虚拟环境中
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}提示: 建议在虚拟环境中运行此应用${NC}"
    echo ""
fi

# 检查依赖是否安装
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}错误: 未找到 requirements.txt 文件${NC}"
    exit 1
fi

echo -e "${YELLOW}检查依赖...${NC}"
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}警告: 依赖未完全安装，正在安装...${NC}"
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}错误: 依赖安装失败${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ 依赖安装完成${NC}"
else
    echo -e "${GREEN}✓ 依赖已安装${NC}"
fi
echo ""

# 检查必要文件是否存在
if [ ! -f "app.py" ]; then
    echo -e "${RED}错误: 未找到 app.py 文件${NC}"
    exit 1
fi

if [ ! -f "lunar_utils.py" ]; then
    echo -e "${RED}错误: 未找到 lunar_utils.py 文件${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 必要文件检查完成${NC}"
echo ""

# 启动应用
echo "========================================"
echo -e "${GREEN}启动春节祝福语生成器...${NC}"
echo "========================================"
echo ""
echo -e "${YELLOW}应用将在以下地址运行:${NC}"
echo -e "${GREEN}  http://localhost:5000${NC}"
echo -e "${GREEN}  http://0.0.0.0:5000${NC}"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止应用${NC}"
echo ""

# 启动Flask应用
python3 app.py
