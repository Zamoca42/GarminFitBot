export interface TaskStatusResponse {
  task_id: string;
  status: 'PENDING' |'PROGRESS' | 'STARTED' | 'SUCCESS' | 'FAILURE';
  result?: TaskResult;
  error?: {
    [key: string]: string;
  };
}

export type TaskName = 'collect-fit-data' | 'analyze-health';

export interface TaskDisplayInfo {
  title: string;
  description: string;
  resultTitle: string;
  collectorMapping?: Record<string, string>;
}

export interface CollectorResult {
  name: string;
  status: '성공' | '실패' | '없음';
}

export interface TaskResult {
  [key: string]: string;
}