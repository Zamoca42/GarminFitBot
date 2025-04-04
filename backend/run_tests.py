#!/usr/bin/env python3
"""
테스트 실행 스크립트

이 스크립트는 dict_converter 유틸리티 함수에 대한 테스트를 실행합니다.
"""

import os
import sys
import unittest

# 현재 디렉토리를 시스템 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 테스트 로더와 실행기 생성
loader = unittest.TestLoader()
runner = unittest.TextTestRunner(verbosity=2)

# 디렉토리 또는 파일이름으로 테스트 찾기
if len(sys.argv) > 1:
    if os.path.isdir(sys.argv[1]):
        # 디렉토리 전체 테스트
        tests = loader.discover(sys.argv[1])
    else:
        # 특정 테스트 파일
        tests = loader.loadTestsFromName(sys.argv[1])
else:
    # 기본: tests 디렉토리의 모든 테스트 실행
    tests = loader.discover("tests")

# 테스트 실행
result = runner.run(tests)

# 종료 코드 설정 (실패가 있으면 1, 없으면 0)
sys.exit(not result.wasSuccessful())
