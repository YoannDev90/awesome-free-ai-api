# Cloudflare Workers AI

Cloudflare Workers AI enables running AI models directly on Cloudflare's global edge network, providing low-latency inference for applications. It supports a wide range of open-source models for text generation, embeddings, image generation, speech recognition, and more, with serverless execution and a free tier of 10,000 Neurons per day.

## Resources

**Documentation**: <https://developers.cloudflare.com/workers-ai/>

**Dashboard**: <https://dash.cloudflare.com/?to=/:account/ai/workers-ai>

**Playground**: <https://playground.ai.cloudflare.com/>

**Models**: <https://developers.cloudflare.com/workers-ai/models/>

OpenAI compatibility ✅

Official SDK ✅

- JS : <https://www.npmjs.com/package/@cloudflare/ai>

## Supported Models

| Model                                        | Max Context | RPM | RPH    | RPD       | T/m | T/h | T/d |
| -------------------------------------------- | ----------- | --- | ------ | --------- | --- | --- | --- |
| @cf/meta/llama-3.3-70b-instruct-fp8-fast     | 128,000     | 300 | 18,000 | 432,000   | N/A | N/A | N/A |
| @cf/mistralai/mistral-small-3.1-24b-instruct | 128,000     | 300 | 18,000 | 432,000   | N/A | N/A | N/A |
| @cf/openai/gpt-oss-120b                      | 65,536      | 300 | 18,000 | 432,000   | N/A | N/A | N/A |
| @cf/qwen/qwq-32b                             | 128,000     | 300 | 18,000 | 432,000   | N/A | N/A | N/A |
| @cf/google/gemma-3-12b-it                    | 128,000     | 300 | 18,000 | 432,000   | N/A | N/A | N/A |
| @cf/black-forest-labs/flux-1-schnell         | N/A         | 720 | 43,200 | 1,036,800 | N/A | N/A | N/A |
| @cf/openai/whisper                           | N/A         | 720 | 43,200 | 1,036,800 | N/A | N/A | N/A |

## Authentication Methods

Cloudflare account

## Code Examples

Python with requests:

```python
import requests

response = requests.post(
    "https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/meta/llama-3.1-8b-instruct",
    headers={"Authorization": "Bearer {API_TOKEN}"},
    json={"messages": [{"role": "user", "content": "Hello, how are you?"}]}
)
print(response.json())
```

JS with fetch:

```javascript
fetch('https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/meta/llama-3.1-8b-instruct', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({messages: [{role: 'user', content: 'Hello, how are you?'}]})
}).then(r => r.json()).then(console.log);
```

## Pros and Cons

### Pros

- Fast deployment on global edge network.
- Wide variety of models from top providers.
- Serverless scaling with no infrastructure management.
- Generous free tier for experimentation.

### Cons

- Not user-friendly for beginners (requires Cloudflare account setup).
- Some models may have higher latency for complex tasks.
- Limited customization compared to self-hosted models.
