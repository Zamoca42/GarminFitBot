import os
import sys

if __name__ == "__main__":
    # 환경 변수 설정
    os.environ.setdefault("PYTHONPATH", os.path.dirname(os.path.abspath(__file__)))

    # 명령행 인자 처리
    if len(sys.argv) > 1:
        if sys.argv[1] == "agent":
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
                            print(
                                f"{message.type if hasattr(message, 'type') else 'Message'}: {message.content if hasattr(message, 'content') else message}"
                            )
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
        elif sys.argv[1] == "partition":
            import psycopg2
            from core.config import SYNC_DATABASE_URL

            try:
                conn = psycopg2.connect(SYNC_DATABASE_URL)
                conn.autocommit = True
                cur = conn.cursor()

                cur.execute("""
                    SELECT n.nspname as schema_name
                    FROM pg_extension e
                    JOIN pg_namespace n ON n.oid = e.extnamespace
                    WHERE e.extname = 'pg_partman'
                """)
                row = cur.fetchone()

                if row:
                    schema_name = row[0]
                    print(f"pg_partman이 '{schema_name}' 스키마에 설치되어 있습니다.")

                    # 파티션 관리 프로시저 호출
                    cur.execute(f"CALL {schema_name}.run_maintenance_proc()")
                    print("파티션 관리 작업이 성공적으로 실행되었습니다.")
                else:
                    print("pg_partman 확장이 설치되어 있지 않습니다.")

                cur.close()
                conn.close()

            except Exception as e:
                print(f"파티션 관리 작업 실행 중 오류 발생: {str(e)}")
    else:
        print("사용법: python run_celery.py [agent|graph-viz|partition]")
        print("  agent <user_id> <query>: AI 에이전트 실행")
        print(
            "  graph-viz [output_path]: 에이전트 그래프 시각화 (기본: agent_graph.png)"
        )
        print("  partition: 파티션 관리 작업 수동 실행")
