import fix20250404 from './2025-04-04-fix.md?raw';
import fix20250405 from './2025-04-05-fix.md?raw';
import improvement20250406 from './2025-04-06-improvement.md?raw';

export type UpdateType = 'feature' | 'bugfix' | 'improvement' | 'release';

export type UpdateMetadata = {
  id: string;
  date: string;
  title: string;
  type: UpdateType;
  summary: string;
  content: string;
};

export const updates: UpdateMetadata[] = [
  {
    id: '2025-04-06-improvement',
    date: '2025-04-06',
    title: '챗봇 프로필 조회 및 데이터 수집 명령어 개선',
    type: 'improvement',
    summary: 'GarminFitBot의 기능이 개선되었습니다. 이번 업데이트에서는 사용자 프로필 조회 기능과 자연어 기반 날짜 인식 기능이 추가되었습니다.',
    content: improvement20250406
  },
  {
    id: '2025-04-05-fix',
    date: '2025-04-05',
    title: '분석 에이전트 버그 수정 및 안정성 개선',
    type: 'bugfix',
    summary: 'AI 에이전트의 상태 관리, 프롬프트 최적화 및 텍스트 길이 제한을 통해 데이터 처리 오류를 해결하고 안정성을 향상시켰습니다.',
    content: fix20250405
  },
  {
    id: '2025-04-04-fix',
    date: '2025-04-04',
    title: '데이터 수집 시 발생하는 오류 수정',
    type: 'bugfix',
    summary: 'Garmin API에서 None 값 처리 및 타입 검증 오류를 수정하여 안정적인 데이터 수집이 가능하도록 개선했습니다.',
    content: fix20250404
  }
];

export function getUpdateById(id: string): UpdateMetadata | undefined {
  return updates.find(update => update.id === id);
}

export function getAllUpdates(): UpdateMetadata[] {
  return [...updates];
}

// 업데이트 유형별 색상 및 라벨 정보
export const updateTypeInfo = {
  feature: {
    label: '새 기능',
    color: 'bg-emerald-100 text-emerald-800',
    icon: '✨'
  },
  bugfix: {
    label: '버그 수정',
    color: 'bg-red-100 text-red-800',
    icon: '🐛'
  },
  improvement: {
    label: '기능 개선',
    color: 'bg-blue-100 text-blue-800',
    icon: '🔧'
  },
  release: {
    label: '정식 출시',
    color: 'bg-purple-100 text-purple-800',
    icon: '🚀'
  }
}; 