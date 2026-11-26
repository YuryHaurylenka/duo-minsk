/** Convert local activity records into the API payload without losing user notes. */
export function toActivitySyncPayload(items) {
  return items.map(item => ({
    place_slug: item.place_slug,
    is_favorite: Boolean(item.is_favorite),
    visited: Boolean(item.visited || item.visited_at),
    rating: item.rating ?? null,
    note: item.note ?? '',
  }));
}
