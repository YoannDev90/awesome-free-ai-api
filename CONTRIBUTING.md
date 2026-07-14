# Contributing to Awesome Free AI Inference APIs

Thank you for your interest in contributing! Here's how to add or update providers.

## Adding a New Provider

1. Fork the repository
2. Edit `config/PROVIDERS.json` and add your provider entry
3. If your provider requires an API key, include it in your PR description (we'll add it securely)
4. Submit a pull request

## Provider Entry Format

```json
{
  "name": "Provider Name",
  "url": "https://provider.example",
  "docs_url": "https://docs.provider.example",
  "discord_url": null,
  "telegram_url": null,
  "needs_api_key": false,
  "api_key_env": null,
  "models": {
    "endpoint": "https://api.provider.example/v1/models",
    "format": "openai",
    "response_path": "$.data[*]",
    "model_id_path": "$.id",
    "model_context_path": "$.context_length",
    "headers": {
      "Authorization": "Bearer {key}"
    }
  },
  "ratings": {
    "stability": 4,
    "model_choice": 5,
    "limits": 3
  },
  "limits": "30 requests per minute",
  "capabilities": ["text", "reasoning", "code"],
  "pricing_model": "free_with_limits",
  "tested": false,
  "tested_by": null,
  "last_checked": "2026-07-14",
  "note": "Optional note about the provider"
}
```

## Rating Guidelines

- **Stability**: How reliable is the API? (1-5)
- **Model choice**: How many models are available? (1-5)
- **Limits**: How generous are the free limits? (1-5)

## Testing

- Set `tested: true` if you've personally verified the provider works
- Add `tested_by: "YourUsername"` if you want credit
- Update `last_checked` with today's date

## API Keys

If your provider requires an API key:
1. Set `needs_api_key: true`
2. Set `api_key_env: "provider_name"` (this will be the key in `api-keys.secret.json`)
3. Include the actual API key in your PR description (we'll add it securely using SOPS)

**Never commit API keys directly to the repository.**

## Building Locally

To preview your changes:

```bash
# Install dependencies (if needed)
pip install -r requirements.txt  # if we had one

# Build the provider directory and site
python3 scripts/build-providers.py
python3 scripts/build-providers.py --site

# View the site
open docs/index.html
```

## Code Style

- Follow existing patterns in `PROVIDERS.json`
- Keep entries alphabetically sorted by provider name
- Use lowercase for capability values: `text`, `reasoning`, `code`, `image`, etc.

## Questions?

Open an issue or reach out on Discord if you have questions about contributing.