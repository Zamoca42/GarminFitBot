# 챗봇 분석 명령어 인식 및 에이전트 개선

이번 개선점은 분석 명령어에서 **엔티티 기반 명령어 인식 시스템**입니다. 
이전에는 발화 패턴을 일일이 등록해야 했기 때문에 사용자의 표현이 조금만 달라져도 명령어를 인식하지 못하는 한계가 있었습니다. 

- 엔티티(키워드) 태깅 시스템을 적용하여 다양한 표현 방식 인식
- 동의어를 엔티티에 등록하여 유사 표현도 동일한 명령어로 처리
- 날짜/기간 표현과 "건강", "수면", "운동", "스트레스" 등 분석 대상 키워드 조합 인식
- 어조나 문장 구조가 달라져도 핵심 키워드만 파악하여 명령어 실행

이러한 개선으로 "어제 내 수면은 어땠어?", "어제 수면 분석해줘", "어제 잠은 잘 잤니?" 등 다양한 표현이 모두 동일한 수면 분석 명령으로 처리됩니다.

## 주요 기능 개선사항

### 1. 발화 패턴에서 엔티티 추가

- **엔티티기반 명령어 처리 시스템 구현**
  - 카카오톡 챗봇에서 엔티티 태깅 적용
  - 분석 엔드포인트에서 엔티티 파싱
  - 날짜/기간 표현과 "건강", "수면", "운동", "스트레스" 등 분석 대상 키워드 조합 인식
  - 다양한 자연어 표현에 대한 인식률 향상

**주요 엔티티 및 관련 키워드:**

| 엔티티 (분석 주제) | 관련 키워드 (예시)              |
| :----------------- | :-------------------------------- |
| `heart-rate`       | 심박수, HRV, 심장               |
| `activity`         | 운동, 활동, 걸음, 달리기, 사이클, 수영, 걷기 |
| `stress`           | 스트레스                           |
| `sleep`            | 수면, 잠                           |
| `health`           | 건강, 몸                           |

현재 정의된 주요 엔티티와 관련 키워드는 위와 같으며, 앞으로 지속적으로 업데이트될 예정입니다.

## 기타 개선사항

### 날짜 분석 시스템 업데이트
- **다양한 날짜 표현 처리 기능**
  - "오늘", "어제", "이번 달", "지난주" 등 다양한 시간 표현 인식 
  - 날짜/기간 의도 자동 파악 (`date_type` 파라미터 설정)
- **맥락 인식 명령어 처리**
  - "내 건강 상태 어때?" → 현재 건강 상태 분석
  - "이번달 운동 효과 알려줘" → 특정 기간 운동 효과 분석
  - "어제 수면 패턴 분석해줘" → 특정 날짜 수면 데이터 분석

### 분석 에이전트 업데이트
- **계획 노드 개선**
  - 특정 날짜 분석 시 이전 데이터 참조 로직 추가
  - 데이터 간 상관관계 고려한 분석 알고리즘 개선
  - 분석 모델 변경: `gemini-1.5-pro` 적용
- **분석 노드 최적화**
  - 구체적 도구/범위 명시 가이드 추가
  - `analysis_history` 상태에서 이전 사이클 분석 결과가 누락되는 버그 수정
- **리포트 생성 고도화**
  - 정적 예시 프롬프트에서 동적 예시 기반 맞춤형 리포트로 프롬프트 수정
  - 리포트 생성 모델 변경: `gemini-2.0-flash-thinking` 적용

### 시스템 안정성 개선
- **데이터 관리 최적화**
  - 태스크별 결과 만료 시간(TTL) 설정 기능 구현 (Redis)
  - `task_postrun` 시그널 핸들러 추가
  - 데이터 수집 완료 시 결과 TTL 기반 재요청 시간 안내
  - 비권장 Class 기반 태스크 등록 제거
  - 데코레이터 기반 태스크 등록으로 전환