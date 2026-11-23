import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_KEY =
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ??
  (() => {
    try {
      const keys = JSON.parse(Deno.env.get("SUPABASE_SECRET_KEYS") ?? "{}");
      return Object.values(keys)[0] as string | undefined;
    } catch {
      return undefined;
    }
  })();

const headers = (extra: Record<string, string> = {}) => ({
  apikey: SERVICE_KEY!,
  Authorization: `Bearer ${SERVICE_KEY!}`,
  "Content-Type": "application/json",
  ...extra,
});

function clean(value: unknown, max = 6000): string {
  return String(value ?? "")
    .replace(/<[^>]*>/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&mdash;/g, "—")
    .replace(/&nbsp;/g, " ")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/\\s+/g, " ")
    .trim()
    .slice(0, max);
}

function walk(value: unknown, out: Record<string, unknown>[]) {
  if (Array.isArray(value)) {
    for (const item of value) walk(item, out);
    return;
  }
  if (!value || typeof value !== "object") return;
  const item = value as Record<string, unknown>;
  const types = Array.isArray(item["@type"]) ? item["@type"] : [item["@type"]];
  if (types.some((t) => typeof t === "string" && /Event$/i.test(t))) out.push(item);
  for (const [key, child] of Object.entries(item)) {
    if (key !== "@context") walk(child, out);
  }
}

function imageUrlFrom(value: unknown, baseUrl: string): string | null {
  if (Array.isArray(value)) {
    for (const item of value) {
      const resolved = imageUrlFrom(item, baseUrl);
      if (resolved) return resolved;
    }
    return null;
  }
  if (value && typeof value === "object") {
    const record = value as Record<string, unknown>;
    for (const key of ["contentUrl", "thumbnailUrl", "url", "@id"]) {
      const resolved = imageUrlFrom(record[key], baseUrl);
      if (resolved) return resolved;
    }
    return null;
  }
  if (typeof value !== "string") return null;
  const candidate = clean(value, 1000);
  if (!candidate || candidate.toLowerCase() === "[object object]") return null;
  try {
    const resolved = new URL(candidate, baseUrl);
    return ["http:", "https:"].includes(resolved.protocol) ? resolved.toString() : null;
  } catch {
    return null;
  }
}

function categoryFor(event: Record<string, unknown>, sourceKey: string): string {
  const type = String(event["@type"] ?? "");
  const text = `${type} ${event.name ?? ""} ${event.description ?? ""}`.toLowerCase();
  if (/concert|music|музык|концерт/.test(text)) return "Концерт";
  if (/theater|theatre| спектак|театр|балет|опера/.test(text)) return "Театр";
  if (/exhibition|выстав/.test(text)) return "Выставка";
  if (/sport|спорт|матч/.test(text)) return "Спорт";
  if (/quest|квест/.test(text)) return "Квест";
  if (/screening|movie|кино|фильм/.test(text)) return "Кино";
  if (/lecture|лекц|мастер-класс|workshop/.test(text)) return "Мастер-класс";
  if (sourceKey.includes("concert")) return "Концерт";
  if (sourceKey.includes("culture")) return "Культура";
  return "Событие";
}

function normalizeMatch(value: string): string {
  return value.normalize("NFKD").replace(/\p{Diacritic}/gu, "").toLowerCase();
}

function matchesAny(value: string, candidates: string[]): boolean {
  const normalized = normalizeMatch(value).trim();
  if (!normalized) return false;
  return candidates.some((candidate) => normalized.includes(normalizeMatch(candidate).trim()));
}

function extractEvents(
  html: string,
  sourceKey: string,
  citySlug: string,
  cityNames: string[],
  countryNames: string[],
) {
  const found: Record<string, unknown>[] = [];
  const scripts = html.matchAll(/<script[^>]*type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi);
  for (const match of scripts) {
    try {
      const parsed = JSON.parse(match[1].trim());
      walk(parsed, found);
    } catch {
      // Ignore malformed JSON-LD blocks; other blocks may still be valid.
    }
  }
  const unique = new Map<string, Record<string, unknown>>();
  for (const event of found) {
    const name = clean(event.name, 240);
    const url = clean(event.url, 1000);
    const start = event.startDate ? new Date(String(event.startDate)) : null;
    if (!name || !url || !start || Number.isNaN(start.getTime())) continue;
    const location = (event.location && typeof event.location === "object")
      ? event.location as Record<string, unknown>
      : {};
    const address = (location.address && typeof location.address === "object")
      ? location.address as Record<string, unknown>
      : {};
    const locality = clean(address.addressLocality ?? location.name ?? "");
    const country = clean(address.addressCountry ?? "");
    const fullAddress = clean(address.streetAddress ?? location.name ?? "");
    const cityMatches = matchesAny(locality, cityNames) || matchesAny(fullAddress, cityNames);
    if ((locality || fullAddress) && !cityMatches) continue;
    if (country && !matchesAny(country, countryNames) && !cityMatches) continue;
    const offers = (event.offers && typeof event.offers === "object")
      ? event.offers as Record<string, unknown>
      : {};
    const low = Number(offers.lowPrice ?? offers.price ?? NaN);
    const high = Number(offers.highPrice ?? offers.price ?? NaN);
    const statusText = String(event.eventStatus ?? "");
    const record = {
      city_slug: citySlug,
      source_key: sourceKey,
      source_url: url,
      title: name,
      description: clean(event.description, 1800),
      category: categoryFor(event, sourceKey),
      venue: clean(location.name ?? "", 240),
      address: fullAddress,
      starts_at: start.toISOString(),
      ends_at: event.endDate ? new Date(String(event.endDate)).toISOString() : null,
      price_min: Number.isFinite(low) && low >= 0 ? low : null,
      price_max: Number.isFinite(high) && high >= 0 ? high : null,
      currency: clean(offers.priceCurrency ?? "BYN", 8),
      image_url: imageUrlFrom(event.image, url),
      ticket_url: clean(offers.url ?? url, 1000),
      status: /EventCancelled/i.test(statusText) ? "cancelled" : ((event.endDate ? new Date(String(event.endDate)).getTime() : start.getTime()) < Date.now() ? "ended" : "scheduled"),
      last_verified_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    unique.set(url, record);
  }
  return [...unique.values()];
}

async function rest(path: string, init: RequestInit = {}) {
  const response = await fetch(`${SUPABASE_URL}/rest/v1/${path}`, {
    ...init,
    headers: headers(init.headers as Record<string, string> ?? {}),
  });
  const text = await response.text();
  if (!response.ok) throw new Error(`Supabase REST ${response.status}: ${text.slice(0, 500)}`);
  return text ? JSON.parse(text) : null;
}

Deno.serve(async (req: Request) => {
  if (req.method !== "POST") return new Response("Method not allowed", { status: 405 });
  if (!SERVICE_KEY) return Response.json({ error: "Missing service key" }, { status: 500 });

  const supplied = req.headers.get("x-cron-secret") ?? "";
  if (!supplied) return Response.json({ error: "Unauthorized" }, { status: 401 });
  const config = await rest("duo_event_sync_config?select=cron_token&id=eq.true");
  if (!config?.[0]?.cron_token || supplied !== config[0].cron_token) {
    return Response.json({ error: "Unauthorized" }, { status: 401 });
  }

  const [sources, cities] = await Promise.all([
    rest("duo_event_sources?select=source_key,source_name,source_url,city_slug&enabled=eq.true"),
    rest("cities?select=slug,name,name_localized,country_code,country_name,country_name_localized&is_active=eq.true"),
  ]);
  type CityRecord = {
    slug: string;
    name: string;
    name_localized: string;
    country_code: string;
    country_name: string;
    country_name_localized: string;
  };
  const cityBySlug = new Map<string, CityRecord>(
    (cities ?? []).map((city: CityRecord) => [city.slug, city] as const),
  );
  const results = [];
  for (const source of sources ?? []) {
    const started = await rest("duo_event_sync_runs", {
      method: "POST",
      headers: { Prefer: "return=representation" },
      body: JSON.stringify([{ source_key: source.source_key, city_slug: source.city_slug, status: "running" }]),
    });
    const runId = started?.[0]?.id;
    try {
      const response = await fetch(source.source_url, {
        headers: {
          "User-Agent": "Mozilla/5.0 (compatible; DUO-Minsk-Events/1.0; +https://minsk-date-ideas.vercel.app)",
          "Accept": "text/html,application/xhtml+xml",
        },
        signal: AbortSignal.timeout(25000),
      });
      if (!response.ok) throw new Error(`Source returned HTTP ${response.status}`);
      const city = cityBySlug.get(source.city_slug);
      if (!city) throw new Error(`City ${source.city_slug} is not active or does not exist`);
      const html = await response.text();
      const events = extractEvents(
        html,
        source.source_key,
        source.city_slug,
        [city.name, city.name_localized],
        [city.country_code, city.country_name, city.country_name_localized],
      );
      if (events.length) {
        await rest("duo_events?on_conflict=source_key,source_url", {
          method: "POST",
          headers: { Prefer: "resolution=merge-duplicates,return=minimal" },
          body: JSON.stringify(events),
        });
      }
      await rest(`duo_event_sources?source_key=eq.${encodeURIComponent(source.source_key)}`, {
        method: "PATCH",
        body: JSON.stringify({
          last_checked_at: new Date().toISOString(),
          last_success_at: events.length ? new Date().toISOString() : undefined,
          last_error: events.length ? null : "Страница доступна, но структурированные события не найдены; старые записи сохранены.",
        }),
      });
      if (runId) await rest(`duo_event_sync_runs?id=eq.${runId}`, {
        method: "PATCH",
        body: JSON.stringify({
          finished_at: new Date().toISOString(),
          found_count: events.length,
          upserted_count: events.length,
          status: events.length ? "success" : "partial",
          details: events.length ? "Structured event data parsed." : "No structured event records found.",
        }),
      });
      results.push({ source: source.source_key, found: events.length, status: events.length ? "success" : "partial" });
    } catch (error) {
      const message = clean(error instanceof Error ? error.message : error, 1000);
      await rest(`duo_event_sources?source_key=eq.${encodeURIComponent(source.source_key)}`, {
        method: "PATCH",
        body: JSON.stringify({ last_checked_at: new Date().toISOString(), last_error: message }),
      });
      if (runId) await rest(`duo_event_sync_runs?id=eq.${runId}`, {
        method: "PATCH",
        body: JSON.stringify({ finished_at: new Date().toISOString(), status: "failed", details: message }),
      });
      results.push({ source: source.source_key, status: "failed", error: message });
    }
  }

  const nowIso = encodeURIComponent(new Date().toISOString());
  await rest("duo_events?status=eq.scheduled&ends_at=not.is.null&ends_at=lt." + nowIso, {
    method: "PATCH",
    body: JSON.stringify({ status: "ended", updated_at: new Date().toISOString() }),
  });
  await rest("duo_events?status=eq.scheduled&ends_at=is.null&starts_at=lt." + nowIso, {
    method: "PATCH",
    body: JSON.stringify({ status: "ended", updated_at: new Date().toISOString() }),
  });

  return Response.json({ ok: true, checked_at: new Date().toISOString(), sources: results });
});
