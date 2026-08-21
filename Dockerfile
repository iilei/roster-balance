FROM public.ecr.aws/lambda/python:3.14

COPY pyproject.toml ${LAMBDA_TASK_ROOT}/
COPY src ${LAMBDA_TASK_ROOT}/src

RUN pip install --no-cache-dir .

CMD ["roster_balance.infrastructure.aws.lambda_handler.handler"]
