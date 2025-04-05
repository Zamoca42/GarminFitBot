import { getAllUpdates } from '$lib/updates';
import type { UpdateMetadata } from '$lib/updates';

export const load = async () => {
  const updates: UpdateMetadata[] = getAllUpdates();

  return {
    updates
  };
}; 