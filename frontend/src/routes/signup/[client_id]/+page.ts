import { PUBLIC_API_URL } from '$env/static/public';
import { error } from '@sveltejs/kit';

export const load = async ({ params }) => {
  try {
    const response = await fetch(`${PUBLIC_API_URL}/auth/verify-client/${params.client_id}`);

    if (!response.ok) {
      throw error(403, {
        message: '잘못된 접근입니다. 카카오톡 챗봇을 통해 접근해주세요.'
      });
    }

    return {
      client_id: params.client_id
    };
  } catch {
    throw error(400, {
      message: '잘못된 접근입니다.'
    });
  }
}; 