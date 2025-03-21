import { PUBLIC_API_URL } from '$env/static/public';
import type { TaskStatusResponse } from '$lib/type';
import { error } from '@sveltejs/kit';

export const load = async ({ params }) => {
  try {
    const path = params.path.split('/');
    const userKey = path[0];
    const date = path[1];
    const taskName = path[2];

    let additionalPath = '';
    if (path.length > 3) {
      additionalPath = '_' + path.slice(3).join('_');
    }

    if (!userKey || !date || !taskName) {
      throw error(400, '잘못된 URL 형식입니다');
    }

    const taskId = `${userKey}_${date}_${taskName}${additionalPath}`;

    const response = await fetch(`${PUBLIC_API_URL}/task/${taskId}/status`);
    const data = await response.json();

    if (!response.ok) {
      throw error(response.status, {
        message: data.detail || '작업 상태를 불러올 수 없습니다.'
      });
    }

    return {
      status: data.data as TaskStatusResponse,
      task_id: taskId
    };
  } catch {
    throw error(500, {
      message: '작업 상태를 불러오는 중 오류가 발생했습니다.'
    });
  }
};