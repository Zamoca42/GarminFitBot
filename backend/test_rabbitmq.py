import pika
import os
from dotenv import load_dotenv

load_dotenv()

def test_rabbitmq_connection():
    """RabbitMQ 연결 테스트"""
    broker_url = os.getenv("BROKER_URL")
    
    if not broker_url:
        print("BROKER_URL 환경 변수가 설정되지 않았습니다.")
        return False
    
    try:
        if broker_url.startswith("amqp://") or broker_url.startswith("amqps://"):
            use_ssl = broker_url.startswith("amqps://")
            
            url_without_protocol = broker_url.split("://")[1]
            
            if "@" in url_without_protocol:
                credentials, host_part = url_without_protocol.split("@")
                username, password = credentials.split(":")
            else:
                username, password = "guest", "guest"
                host_part = url_without_protocol
            
            if "/" in host_part:
                hostname, vhost = host_part.split("/", 1)
            
            print(f"연결 정보: 호스트={hostname}, 포트={5672}, 가상호스트={vhost}, SSL={use_ssl}")
            
            credentials = pika.PlainCredentials(username, password)
            
            parameters = pika.ConnectionParameters(
                host=hostname,
                port=5672,
                virtual_host=vhost,
                credentials=credentials,
                connection_attempts=3,
                retry_delay=5,
                socket_timeout=15
            )
            
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            
            print(f"RabbitMQ 서버 {hostname}:{5672}{vhost}에 성공적으로 연결되었습니다.")
            
            channel.queue_declare(queue='test_queue')
            channel.basic_publish(
                exchange='',
                routing_key='test_queue',
                body='Hello RabbitMQ!'
            )
            print("테스트 메시지를 발행했습니다.")
            
            connection.close()
            return True
            
    except Exception as e:
        print(f"RabbitMQ 연결 실패: {str(e)}")
        return False

if __name__ == "__main__":
    test_rabbitmq_connection() 