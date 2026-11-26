import test from 'node:test';
import assert from 'node:assert/strict';
import { toActivitySyncPayload } from './activity.js';

test('activity migration preserves notes, ratings, favorites and visit state', () => {
  const result = toActivitySyncPayload([{
    place_slug: 'quiet-cafe', is_favorite: true, visited_at: '2026-11-20T18:00:00Z',
    rating: 5, note: 'Очень уютно — вернуться на выходных',
  }]);
  assert.deepEqual(result, [{ place_slug: 'quiet-cafe', is_favorite: true, visited: true, rating: 5, note: 'Очень уютно — вернуться на выходных' }]);
});

test('activity migration sends explicit defaults and keeps an empty note', () => {
  assert.deepEqual(toActivitySyncPayload([{ place_slug: 'new-place' }]), [{
    place_slug: 'new-place', is_favorite: false, visited: false, rating: null, note: '',
  }]);
});
