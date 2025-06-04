#!/usr/bin/env python3
"""
Lambda部署包创建脚本

此脚本创建用于AWS Lambda部署的部署包：
1. 创建两个单独的zip文件用于Lambda部署：
   - app.zip: 包含Lambda函数代码，从'lambda'目录
   - dependencies.zip: 包含Python依赖，从'packaging/_dependencies'目录
2. 依赖被打包为Lambda层，具有正确的目录结构
3. 在创建新的zip文件之前，会删除任何现有的zip文件
4. 两个zip文件都存储在'packaging'目录中，供CDK在部署期间使用

注意：此脚本假设依赖已经使用pip命令安装到'packaging/_dependencies'目录，
使用适当的平台标志。
"""

import os
import zipfile
from pathlib import Path

def create_lambda_package():
    """创建Lambda部署包"""
    # 定义路径
    current_dir = Path.cwd()
    packaging_dir = current_dir / "packaging"

    # 获取strands_tools包的路径
    app_dir = current_dir / "lambda"
    app_deployment_zip = packaging_dir / "app.zip"

    dependencies_dir = packaging_dir / "_dependencies"
    dependencies_deployment_zip = packaging_dir / "dependencies.zip"

    print(f"创建Lambda部署包: {app_deployment_zip}")

    # 清理任何现有的包目录或zip文件
    if app_deployment_zip.exists():
        os.remove(app_deployment_zip)

    if dependencies_deployment_zip.exists():
        os.remove(dependencies_deployment_zip)

    # 创建ZIP文件
    print("创建ZIP文件...")
    os.makedirs(app_deployment_zip.parent, exist_ok=True)

    print(f"  创建 {dependencies_deployment_zip.name}...")
    with zipfile.ZipFile(dependencies_deployment_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(dependencies_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = Path("python") / os.path.relpath(file_path, dependencies_dir)
                zipf.write(file_path, arcname)

    print(f"  创建 {app_deployment_zip.name}...")
    with zipfile.ZipFile(app_deployment_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(app_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, app_dir)
                zipf.write(file_path, arcname)

    print(f"Lambda部署包创建成功: {dependencies_deployment_zip.name} {app_deployment_zip.name}")
    return True


if __name__ == "__main__":
    create_lambda_package()
