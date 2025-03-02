import asyncio
import os
import sys

from task.celery_app import celery_app

if __name__ == "__main__":
    # 환경 변수 설정
    os.environ.setdefault("PYTHONPATH", os.path.dirname(os.path.abspath(__file__)))
    
    # 명령행 인자 처리
    if len(sys.argv) > 1:
        if sys.argv[1] == "worker":
            # Celery 작업자 실행
            celery_app.worker_main(["worker", "--loglevel=info", "-E"])
        elif sys.argv[1] == "beat":
            # Celery beat 실행 (스케줄러)
            celery_app.Beat().run()
        elif sys.argv[1] == "flower":
            # Flower 모니터링 도구 실행
            os.system("celery -A task.celery_app flower")
        elif sys.argv[1] == "collect":
            # 데이터 수집 작업 수동 실행
            days_back = int(sys.argv[2]) if len(sys.argv) > 2 else 0
            from task.garmin_collector import collect_garmin_data
            
            # 비동기 함수 실행
            asyncio.run(collect_garmin_data(days_back))
        elif sys.argv[1] == "partition":
            # 파티션 관리 작업 수동 실행
            from task.partition_manager import manage_partitions
            
            # 비동기 함수 실행
            asyncio.run(manage_partitions())
        elif sys.argv[1] == "create-partition":
            # 특정 월의 파티션 수동 생성
            if len(sys.argv) < 4:
                print("사용법: python run_celery.py create-partition <year> <month>")
                sys.exit(1)
                
            year = int(sys.argv[2])
            month = int(sys.argv[3])
            
            from task.partition_manager import create_specific_month_partition
            
            # 비동기 함수 실행
            asyncio.run(create_specific_month_partition(year, month))
        elif sys.argv[1] == "test-broker":
            # RabbitMQ 연결 테스트
            from test_rabbitmq import test_rabbitmq_connection
            test_rabbitmq_connection()
    else:
        print("사용법: python run_celery.py [worker|beat|flower|collect|partition|create-partition|test-broker]")
        print("  worker: Celery 작업자 실행")
        print("  beat: Celery 스케줄러 실행")
        print("  flower: Celery 모니터링 도구 실행")
        print("  collect [days_back]: 데이터 수집 작업 수동 실행")
        print("  partition: 파티션 관리 작업 수동 실행")
        print("  create-partition <year> <month>: 특정 월의 파티션 수동 생성")
        print("  test-broker: RabbitMQ 연결 테스트") 