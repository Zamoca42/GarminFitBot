import asyncio
import os
import sys

from task import celery_app

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
        elif sys.argv[1] == "partition":
            # 파티션 관리 작업 수동 실행
            from task.partition_manager import manage_partitions

            # 비동기 함수 실행
            asyncio.run(manage_partitions())
        elif sys.argv[1] == "agent":
            # 에이전트 실행
            if len(sys.argv) < 4:
                print("사용법: python run_celery.py agent <user_id> <query>")
                print(
                    "예시: python run_celery.py agent 123456 '오늘 운동량은 어땠나요?'"
                )
                sys.exit(1)

            from app.agent.react_agent import create_agent

            try:
                agent = create_agent()

                # user_id를 정수로 변환
                user_id = int(sys.argv[2])
                query = sys.argv[3]
                result = agent.run(
                    query=query,
                    user_id=user_id,
                    user_timezone="Asia/Seoul",
                )
                
                # 결과 처리
                if isinstance(result, dict) and "messages" in result:
                    # 메시지 출력
                    for message in result["messages"]:
                        if hasattr(message, "pretty_print"):
                            message.pretty_print()
                        else:
                            print(f"{message.type if hasattr(message, 'type') else 'Message'}: {message.content if hasattr(message, 'content') else message}")
                else:
                    # 문자열이나 다른 형태의 결과 출력
                    print(result)
                    
            except ValueError as e:
                print(f"에러가 발생했습니다: {str(e)}")
            except Exception as e:
                print(f"에러가 발생했습니다: {str(e)}")
        elif sys.argv[1] == "graph-viz":
            # 에이전트 그래프 시각화
            output_path = "agent_graph.png"
            if len(sys.argv) > 2:
                output_path = sys.argv[2]

            from app.agent.react_agent import create_agent

            try:
                agent = create_agent()
                success = agent.visualize_graph(output_path)
                if success:
                    print(f"그래프가 '{output_path}' 파일로 저장되었습니다.")
                else:
                    print("그래프 시각화에 실패했습니다.")
            except Exception as e:
                print(f"에러가 발생했습니다: {str(e)}")
        elif sys.argv[1] == "create-partition":
            # 특정 월의 파티션 수동 생성
            if len(sys.argv) < 4:
                print("사용법: python run_celery.py create-partition <year> <month>")
                sys.exit(1)

            year = int(sys.argv[2])
            month = int(sys.argv[3])

            from task.partition_manager import create_specific_month_partition

            # 함수 실행
            create_specific_month_partition(year, month)
        elif sys.argv[1] == "drop-partition":
            # 특정 월의 파티션 수동 삭제
            if len(sys.argv) < 4:
                print("사용법: python run_celery.py drop-partition <year> <month>")
                sys.exit(1)

            year = int(sys.argv[2])
            month = int(sys.argv[3])

            from task.partition_manager import drop_specific_month_partition

            # 함수 실행
            drop_specific_month_partition(year, month)
        elif sys.argv[1] == "drop-all":
            # 모든 테이블 삭제
            print("⚠️ 주의: 모든 테이블이 삭제됩니다. 계속하시겠습니까? (y/N)")
            response = input().lower()
            if response != "y":
                print("작업이 취소되었습니다.")
                sys.exit(0)

            from task.partition_manager import drop_all_tables

            # 함수 실행
            drop_all_tables()
    else:
        print(
            "사용법: python run_celery.py [worker|beat|flower|agent|graph-viz|create-partition|drop-partition|drop-all]"
        )
        print("  worker: Celery 작업자 실행")
        print("  beat: Celery 스케줄러 실행")
        print("  flower: Celery 모니터링 도구 실행")
        print("  agent <user_id> <query>: AI 에이전트 실행")
        print(
            "  graph-viz [output_path]: 에이전트 그래프 시각화 (기본: agent_graph.png)"
        )
        print("  partition: 파티션 관리 작업 수동 실행")
        print("  create-partition <year> <month>: 특정 월의 파티션 수동 생성")
        print("  drop-partition <year> <month>: 특정 월의 파티션 수동 삭제")
        print("  drop-all: 모든 테이블 삭제")
