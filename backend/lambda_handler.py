from mangum import Mangum
from app import app

# Lambda handler
# lifespan="off" は FastAPI の lifespan イベントを無効化（Lambdaでは不要）
handler = Mangum(app, lifespan="off")

