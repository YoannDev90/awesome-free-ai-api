# Provider Directory — Spec

Replace the current flat README table with a data-driven provider directory.

## Files

```
config/
├── PROVIDERS.json          # Metadata + human-written content (committed, public)
├── api-keys.secret.json    # SOPS-encrypted API keys (committed, safe)
├── PROVIDERS.md            # Auto-generated provider directory (committed, synced by CI)

scripts/
└── build-providers.py      # Generator script
```

## config/PROVIDERS.json — Full Schema

### Top-level

```json
{
  "$schema": "v1",
  "providers": [ ... ]
}
```

### Provider Object

```json
{
  "name": "Groq",
  "url": "https://console.groq.com/api",
  "docs_url": "https://console.groq.com/docs/quickstart",
  "discord_url": null,
  "telegram_url": null,
  "needs_api_key": true,
  "api_key_env": "groq",
  "models": {
    "endpoint": "https://api.groq.com/openai/v1/models",
    "format": "openai",
    "response_path": "$.data[*]",
    "model_id_path": "$.id",
    "model_context_path": "$.context_length",
    "model_context_unit": "character",
    "pricing_path": null,
    "headers": {
      "Authorization": "Bearer {key}"
    }
  },
  "ratings": {
    "stability": 4,
    "model_choice": 5,
    "limits": 3
  },
  "limits": "30 req/min, 14400 req/day",
  "capabilities": [
    "text",
    "reasoning",
    "code"
  ],
  "pricing_model": "free_with_limits",
  "tested": true,
  "tested_by": "YoannDev90",
  "last_checked": "2026-07-14",
  "note": "Fast inference, good for production. Strong model selection."
}
```

### Fields Reference

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | Display name |
| `url` | string | yes | Main website |
| `docs_url` | string? | no | Link to API docs |
| `discord_url` | string? | no | Discord server invite link |
| `telegram_url` | string? | no | Telegram channel/group link |
| `needs_api_key` | boolean | yes | Whether an API key is required |
| `api_key_env` | string? | no | Key name in api-keys.secret.json |
| `models` | object or null | yes | Config for fetching model list; null = no public endpoint |
| `ratings` | object | yes | Human ratings (see below) |
| `limits` | string | yes | Human-readable limits |
| `capabilities` | string[] | yes | List of capabilities |
| `pricing_model` | string | yes | Pricing category |
| `tested` | boolean | yes | Set manually by maintainer |
| `tested_by` | string? | no | Maintainer who tested |
| `last_checked` | date | yes | Last fetch/test date (YYYY-MM-DD) |
| `note` | string? | no | Free-text maintainer note |

### Models Object

| Field | Type | Required | Description |
|---|---|---|---|
| `endpoint` | string | yes | URL to fetch model list from |
| `format` | string | yes | One of: `openai`, `huggingface`, `custom_list` (extensible) |
| `response_path` | string | yes | JSONPath to the array of model objects |
| `model_id_path` | string | yes | JSONPath to the model identifier |
| `model_context_path` | string? | no | JSONPath to the context length |
| `model_context_unit` | string? | no | Unit: `token`, `character`, `byte`, `number` |
| `pricing_path` | string? | no | JSONPath to the price info |
| `headers` | object? | no | HTTP headers; `{key}` is substituted with the real API key |

**When `models` is null** — models section shows "Not publicly listed."

### Ratings Object

| Field | Type | Range | Description |
|---|---|---|---|
| `stability` | int | 1-5 | API uptime, reliability |
| `model_choice` | int | 1-5 | Breadth and quality of model selection |
| `limits` | int | 1-5 | How generous the free limits are |

**Global rating** = `round((stability + model_choice + limits) / 3)`

Rendered as:

```
| Stability | Model choice | Limits |
|-----------|-------------|--------|
| 4/5       | 5/5         | 3/5    |
```

Global: **4 / 5 - 4 stars**

### Valid Capabilities

`text`, `reasoning`, `code`, `image`, `audio`, `video`, `embedding`, `rerank`, `function_calling`, `vision`, `tts`, `stt`

### Valid pricing_model Values

| Value | Meaning |
|---|---|
| `free_all` | No limits, no key required |
| `free_with_limits` | Free but rate-limited |
| `freemium` | Free tier + paid upgrades |
| `free_tier` | Only a free tier exists |
| `unknown` | Not clear |

## api-keys.secret.json

Encrypted with [sops](https://github.com/getsops/sops) + [age](https://age-encryption.dev/).

```json
{
  "groq": "gsk_xxxx",
  "openrouter": "sk-or-v1-xxxx",
  "github-models": "ghp_xxxx"
}
```

**Edit:** `sops config/api-keys.secret.json`
**CI decrypts with:** `${{ secrets.SOPS_AGE_KEY }}`

## PROVIDERS.md — Auto-Generated Format

One section per provider:

```markdown
# Provider Name

**Global rating:** 4 / 5

| Stability | Model choice | Limits |
|-----------|-------------|--------|
| 4/5       | 5/5         | 3/5    |

**URL:** [provider.example](https://provider.example)
**API docs:** [docs.example](https://docs.example)
**Tested:** Yes by Username (2026-07-14)
**Limits:** 30 req/min, 14400 req/day
**Capabilities:** text, reasoning, code
**Pricing:** free with limits
**Community:** [Discord](https://discord.gg/example) [Telegram](https://t.me/example)

> Free-text maintainer note.

## Models
| Model ID | Context |
|---|---|
| model-name-70b | 128k |
| model-name-8b | 32k |
```

If models config is null or fetch fails:

```
## Models
Not publicly listed.
```

## Script: build-providers.py

Sequence:

1. Read `config/PROVIDERS.json`
2. If any provider has `needs_api_key: true`, read `api-keys.json` (decrypted by sops)
3. For each provider:
   a. If `models` is not null: HTTP request to `endpoint`
   b. Parse response by `format` (openai, huggingface, custom_list, etc.)
   c. Build model table rows
   d. Combine with human data
   e. Write section to PROVIDERS.md
4. Update `last_checked` for processed providers
5. Save back to PROVIDERS.json

### Supported Formats (v1, extensible)

```python
PARSERS = {
    "openai": parse_openai,          # $.data[*].id, $.data[*].context_length
    "huggingface": parse_hf,         # list of {id, context_length}
    "custom_list": parse_custom_list # $.models[*].name
}
```

Unknown format => "Models not automatically listed."

### Rate Limiting

- Max 2 concurrent requests
- 500ms delay between requests to same host
- Timeout: 15s per request

## CI Workflow

```yaml
name: Build provider directory

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install sops
        run: |
          curl -LO https://github.com/getsops/sops/releases/latest/download/sops-linux-amd64
          chmod +x sops-linux-amd64 && sudo mv sops-linux-amd64 /usr/local/bin/sops

      - name: Decrypt API keys
        run: |
          echo "${{ secrets.SOPS_AGE_KEY }}" > /tmp/sops-age-key
          sops --decrypt --age $(cat /tmp/sops-age-key) config/api-keys.secret.json > /tmp/api-keys.json

      - name: Build provider directory
        run: python3 scripts/build-providers.py

      - name: Commit if changed
        run: |
          git diff --quiet && exit 0
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add -A
          git commit -m "chore: update provider directory [skip ci]"
          git push
```

The separate `sort-table.yml` workflow handles the README table independently.

## Maintainer Workflow

```bash
# Add/update encrypted API keys
sops config/api-keys.secret.json

# Edit metadata
$EDITOR config/PROVIDERS.json

# Build and verify locally
python3 scripts/build-providers.py
less config/PROVIDERS.md

# Commit everything
git add -A && git commit -m "feat: add Groq"
git push
```

## Open Questions

1. **SOPS key management:** How to distribute the age key among contributors?
2. **Context unit:** Convert everything to tokens or keep raw values?
3. **Paginated model lists:** How to handle providers that paginate?
4. **PROVIDERS.md in CI only:** Commit generated file or generate on-the-fly?
5. **PR validation:** CI check that PROVIDERS.md matches PROVIDERS.json?
6. **README table future:** Replace with short summary linking to PROVIDERS.md, or keep both?

## Next Steps

1. Discuss spec with contributors
2. Implement build script and PROVIDERS.json
3. Set up CI pipeline
4. Migrate existing 56 providers
5. Write contributor docs
