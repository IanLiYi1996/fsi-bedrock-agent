FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.12

# 复制依赖文件
COPY requirements-all.txt ${LAMBDA_TASK_ROOT}/

# 安装依赖
RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements-all.txt 

# 复制Lambda函数代码
COPY lambda/ ${LAMBDA_TASK_ROOT}/

# 设置处理程序
CMD [ "agent_handler.handler" ]
