# 基金投顾多Agent系统 (Strands Agents实现)

基于Strands Agents框架实现的基金投顾多Agent系统。该系统使用多个专业Agent协作，为用户提供基金分析和推荐服务。

## 系统架构

系统包含以下组件：

## 项目结构

```
fund-advisor-agent-strands/
├── agents/                  # 各类Agent实现
├── data_tools/              # 基金数据工具
├── knowledge_base/          # 基金知识库
├── main.py                  # 主程序入口
├── requirements.txt         # 依赖包列表
├── config/                  # 配置文件
├── README.md                # 项目说明文档
├── .env                     # 环境变量配置
```

## 安装与设置

### 前提条件

- Python 3.10+
- AWS账户（用于访问Amazon Bedrock）

### 安装步骤

1. 克隆仓库：
   ```bash
   git clone xxx.git
   cd fund-advisor-agent-strands
   ```

2. 创建并激活虚拟环境：
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   uv venv myenv
   source myenv/bin/activate  
   ```

3. 安装依赖：
   ```bash
   uv pip install -r requirements.txt
   ```

4. 配置AWS凭证：
   - 设置环境变量：`AWS_ACCESS_KEY_ID`、`AWS_SECRET_ACCESS_KEY`
   - 或修改`.env`文件，内容如下：
     ```
     AWS_ACCESS_KEY_ID=your_access_key
     AWS_SECRET_ACCESS_KEY=your_secret_key
     ```
   - 或使用AWS CLI配置：`aws configure`

5. 创建KB和DDB
   ```bash
   sh deploy_prereqs.sh
   ```

## 使用方法

- 运行主程序：

```bash
source .env && python -u main.py
```