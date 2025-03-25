import boto3
from dotenv import dotenv_values

# .env 파일 로드
env_path = ".env"
env_vars = dotenv_values(env_path)

# AWS 세션 생성 (환경변수 또는 프로파일로 인증)
ssm = boto3.client("ssm", region_name="ap-northeast-2")

# SSM Parameter prefix (optional)
prefix = "/ecs/celery-worker"

for key, value in env_vars.items():
    param_name = f"{prefix}/{key}"
    print(f"🔧 Uploading {param_name}...")

    ssm.put_parameter(Name=param_name, Value=value, Type="SecureString", Overwrite=True)

print("✅ 업로드 완료!")
