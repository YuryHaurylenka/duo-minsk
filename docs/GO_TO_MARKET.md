# DUO — International product strategy

## Product thesis
DUO is a shared date-planning companion, not a dating app. Two people discover local experiences, build plans together, save a shared history and turn "what should we do?" into a decision in minutes.

## Initial wedge
Start with one city where data quality can be maintained. Minsk is the working MVP, not the international product boundary. Prove repeat use with couples before expanding geography.

## Target users
- Couples who want fresh ideas and spend too long choosing what to do.
- New couples exploring a city together.
- Long-term couples who want to break routine.
- Visitors who need a date itinerary in an unfamiliar city.

## Differentiation to validate
1. One shared workspace for two people.
2. Date plans that combine live local events and permanent venues.
3. A shared memory of favorites, visits and ratings.
4. City-aware recommendations constrained by date, mood, time and budget.
5. A reliable local data layer rather than generic AI suggestions.

## Expansion sequence
1. Stabilize Minsk: verify place data, ticket links, event freshness, signup and couple invite flows.
2. English-first product shell: locale routing, language preference, currency formatting and translated onboarding.
3. Launch one English-speaking pilot city only after sourcing a dependable event/place feed and validating unit economics.
4. Add city operations tooling: source health, deduplication, stale-record review, venue claim/report flow.
5. Expand city-by-city using the same data contracts; do not launch a city with empty or unverified listings.

## Monetization hypotheses
- Freemium: free discovery and a limited number of saved plans; paid shared collections, advanced planning and recurring date prompts.
- Affiliate / booking revenue from ticketing, experiences and reservations where partner programs permit it.
- Clearly labelled sponsored placement for local businesses, with relevance and quality safeguards.
- B2B city/venue tools only after consumer usage is proven.

Do not add paid ranking or sponsored listings before users trust the catalog. Never sell personal couple activity or private notes.

## North-star and guardrail metrics
- North star: completed date plans per active couple per month.
- Activation: both people join the same couple space and save the first plan.
- Retention: couples with at least one meaningful action in weeks 1, 4 and 8.
- Marketplace: click-through to booking, booking conversion where measurable, partner revenue per active couple.
- Quality: broken-link rate, stale-event rate, source coverage, event cancellation mismatch.
- Guardrails: auth failures, API p95 latency, data deletion requests, privacy incidents.

## Non-negotiable launch gates
- English UI and translated transactional emails.
- Privacy policy, terms, cookie/consent review and a real legal entity/contact.
- GDPR/UK GDPR assessment and data minimization before serving those markets.
- Payment provider and tax review before subscriptions.
- Per-city source rights, partner agreements and transparent sponsored-content labels.
- End-to-end tests for signup, email confirmation, invite acceptance, shared activity and account deletion.
- Backups, restore drill, monitoring, error reporting and incident response.

## What not to do
- Do not claim global coverage while only Minsk data is curated.
- Do not fabricate venue ratings, prices, bookings or availability.
- Do not scale paid acquisition before retention and referral loops are measured.
- Do not treat AI-generated itineraries as verified local facts.
