import { error } from '@sveltejs/kit';
import { getUpdateById } from '$lib/updates';
import type { UpdateMetadata } from '$lib/updates';

export const load = async ({ params }) => {
  try {
    const id = params.id;
    const update = getUpdateById(id);

    if (!update) {
      throw error(404, {
        message: '업데이트를 찾을 수 없습니다.'
      });
    }

    return {
      update
    };
  } catch (e) {
    throw error(404, {
      message: '업데이트를 찾을 수 없습니다.'
    });
  }
}; 