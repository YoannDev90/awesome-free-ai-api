# Cerebras AI

Cerebras AI delivers ultra-fast AI inference using Wafer-Scale Engine chips and CS-3 systems, powering real-time applications with sub-second reasoning. The platform focuses on high-speed serving of large models like Llama, Qwen, and GPT-OSS via a simple API. It emphasizes up to 100x faster performance than GPU clouds for agentic AI, search, and coding.

## Resources

**Documentation**: <https://inference-docs.cerebras.ai/introduction>.

**Dashboard**: <https://cerebras.ai/> signup for API keys.

**Discord**: <https://discord.com/invite/q6bZcMWJVu> (for support and community).

**Models**: Full list in API docs.

OpenAI compatibility ✅

Official SDK ✅

- Python : <https://github.com/Cerebras/cerebras-cloud-sdk-python>

- JS : <https://github.com/Cerebras/cerebras-cloud-sdk-node>

## Supported Models

| Model                          | Max Context | RPM | RPH | RPD    | T/m    | T/h       | T/d       |
| ------------------------------ | ----------- | --- | --- | ------ | ------ | --------- | --------- |
| gpt-oss-120b                   | 65,536      | 30  | 900 | 14,400 | 64,000 | 1,000,000 | 1,000,000 |
| llama-3.3-70b                  | 65,536      | 30  | 900 | 14,400 | 64,000 | 1,000,000 | 1,000,000 |
| llama3.1-8b                    | 8,192       | 30  | 900 | 14,400 | 60,000 | 1,000,000 | 1,000,000 |
| qwen-3-235b-a22b-instruct-2507 | 65,536      | 30  | 900 | 1,440  | 64,000 | 1,000,000 | 1,000,000 |
| qwen-3-32b                     | 65,536      | 30  | 900 | 14,400 | 64,000 | 1,000,000 | 1,000,000 |
| zai-glm-4.6                    | 64,000      | 10  | 100 | 100    | 60,000 | 100,000   | 1,000,000 |
| zai-glm-4.7                    | 64,000      | 10  | 100 | 100    | 60,000 | 1,000,000 | 1,000,000 |

## Authentication Methods

Email + Github + Google

## Code Examples

Python with OpenAI SDK:

```python
from openai import OpenAI

client = OpenAI(
    api_key="YOUR_CEREBRAS_API_KEY",
    base_url="https://api.cerebras.ai/v1"
)

response = client.chat.completions.create(
    model="cerebras/llama-3.3-70b",
    messages=[{"role": "user", "content": "Hello, how are you?"}],
)
print(response.choices[0].message.content)
```

JS with AI SDK:

```javascript
import { createCerebras } from '@ai-sdk/cerebras';

const cerebras = createCerebras({ apiKey: 'YOUR_CEREBRAS_API_KEY' });

const { text } = await generateText({
    model: cerebras('qwen/qwen3-32b'),
    prompt: 'Hello, how are you?'
});
console.log(text);
```

## Pros and Cons

### Pros

- Blazing inference (2,000+ tokens/sec, sub-second reasoning).
- OpenAI-compatible API, easy integration.
- Cost-efficient vs. GPUs for real-time AI.

### Cons

- Limited free tier (1M tokens/day).
- Context limits (e.g., 131k on some coders).
- Occasional stability issues reported.
