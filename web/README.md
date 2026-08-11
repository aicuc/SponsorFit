# SponsorFit Web

The web demo is a deliberately small discovery layer for SponsorFit. It gives a maintainer a four-part preview from public GitHub evidence, provides five pre-generated project cases, and points to the Codex Skill or Python CLI for the full analysis.

## Run locally

```bash
cd web
npm install
npm run dev
```

Open `http://localhost:3000`.

The preview uses GitHub's public REST API. Copy `.env.example` to `.env.local` and set `GITHUB_TOKEN` if you need a higher API limit. The token only needs permission to read public repositories. Never commit the token.

## Verify

```bash
npm test
npm run typecheck
npm run lint
npm run build
```

## Deploy

Deploy `web/` as the Vercel project root. Set `NEXT_PUBLIC_SITE_URL` to the production URL and, optionally, set `GITHUB_TOKEN` as a server-side environment variable.

The current rate limiter and preview cache are intentionally best-effort, in-memory safeguards. They are appropriate for the first validation release but not a substitute for durable distributed rate limiting at high traffic.

## Intentional MVP limits

- Public GitHub repositories only.
- Repository metadata and a bounded README excerpt only; no repository clone or arbitrary URL fetching.
- Deterministic archetype recommendations rather than model-generated analysis.
- No accounts, database, report history, or private repositories.
- Buyer and offer results are explicitly labeled as hypotheses.
