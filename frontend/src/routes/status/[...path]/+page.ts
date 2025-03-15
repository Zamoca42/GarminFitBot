import { PUBLIC_API_URL } from '$env/static/public';
import type { TaskStatusResponse } from '$lib/type';
import { error } from '@sveltejs/kit';

export const load = async ({ params }) => {
  try {
    const [user_key, date, task_name] = params.path.split('/');

    if (!user_key || !date || !task_name) {
      throw error(400, '잘못된 URL 형식입니다');
    }
    
    const task_id = `${user_key}_${date}_${task_name}`;
    
    const response = await fetch(`${PUBLIC_API_URL}/task/${task_id}/status`);
    const data = await response.json();

    if (!response.ok) {
      throw error(response.status, {
        message: data.detail || '작업 상태를 불러올 수 없습니다.'
      });
    }

    return {
      status: data.data as TaskStatusResponse,
      task_id
    };
  } catch {
    throw error(500, {
      message: '작업 상태를 불러오는 중 오류가 발생했습니다.'
    });
  }
};