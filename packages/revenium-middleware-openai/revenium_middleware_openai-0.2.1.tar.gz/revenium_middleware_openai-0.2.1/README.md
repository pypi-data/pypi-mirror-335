# 🤖 Revenium Middleware for OpenAI

[![PyPI version](https://img.shields.io/pypi/v/revenium-middleware-openai.svg)](https://pypi.org/project/revenium-middleware-openai/)
[![Python Versions](https://img.shields.io/pypi/pyversions/revenium-middleware-openai.svg)](https://pypi.org/project/revenium-middleware-openai/)
[![Documentation Status](https://readthedocs.org/projects/revenium-middleware-openai/badge/?version=latest)](https://revenium-middleware-openai.readthedocs.io/en/latest/?badge=latest)
[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

[//]: # ([![Build Status]&#40;https://github.com/revenium/revenium-middleware-openai/actions/workflows/ci.yml/badge.svg&#41;]&#40;https://github.com/revenium/revenium-middleware-openai/actions&#41;)

A production-grade middleware library for metering and monitoring OpenAI API usage in Python applications. 🐍✨

## ✨ Features

- **📊 Precise Usage Tracking**: Monitor tokens, costs, and request counts across all OpenAI API endpoints
- **🔌 Seamless Integration**: Drop-in middleware that works with minimal code changes
- **⚙️ Flexible Configuration**: Customize metering behavior to suit your application needs


## 📥 Installation

```bash
pip install revenium-middleware-openai
```

## 🔧 Usage

### 🔄 Zero-Config Integration

Simply export your REVENIUM_METERING_API_KEY and import the middleware. 
Your OpenAI calls will be metered automatically:

```python
import openai
import revenium_middleware_openai

# Ensure REVENIUM_METERING_API_KEY environment variable is set

response = openai.chat.completions.create(
    model="gpt-4",  
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "What is the answer to life, the universe and everything?",
        },
    ],
    max_tokens=500,
)

print(response.choices[0].message.content)
```

The middleware automatically intercepts OpenAI API calls and sends metering data to Revenium without requiring any changes to your existing code. Make sure to set the `REVENIUM_METERING_API_KEY` environment variable for authentication with the Revenium service.

### 📈 Enhanced Tracking with Metadata

For more granular usage tracking and detailed reporting, add the `usage_metadata` parameter:

```python
import openai
import revenium_middleware_openai

response = openai.chat.completions.create(
    model="gpt-4",  # You can change this to other models like "gpt-3.5-turbo"
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "What is the meaning of life, the universe and everything?",
        },
    ],
    max_tokens=500,
    usage_metadata={
        "trace_id": "conv-28a7e9d4-1c3b-4e5f-8a9b-7d1e3f2c1b4a",
        "task_id": "chat-summary-af23c910",
        "task_type": "text-classification",
        "subscriber_identity": "customer-email@example.com",
        "organization_id": "acme-corporation-12345",
        "subscription_id": "startup-plan-quarterly-2025-Q1",
        "product_id": "intelligent-document-processor-v3",
        "source_id": "mobile-app-ios-v4.2",
        "ai_provider_key_name": "openai-production-key1",
        "agent": "customer-support-assistant-v2",
    },
)
print(response.choices[0].message.content)
```

#### 🏷️ Metadata Fields

The `usage_metadata` parameter supports the following fields:

| Field | Description | Use Case |
|-------|-------------|----------|
| `trace_id` | Unique identifier for a conversation or session | Track multi-turn conversations |
| `task_id` | Identifier for a specific AI task | Group related API calls for a single task |
| `task_type` | Classification of the AI operation | Categorize usage by purpose (e.g., classification, summarization) |
| `subscriber_identity` | End-user identifier | Track usage by individual users |
| `organization_id` | Customer or department identifier | Allocate costs to business units |
| `subscription_id` | Reference to a billing plan | Associate usage with specific subscriptions |
| `product_id` | The product or feature using AI | Track usage across different products |
| `source_id` | Origin of the request | Monitor usage by platform or app version |
| `ai_provider_key_name` | Identifier for the API key used | Track usage by different API keys |
| `agent` | Identifier for the specific AI agent | Compare performance across different AI agents |

All metadata fields are optional. Adding them enables more detailed reporting and analytics in Revenium.

## 🔄 Compatibility

- 🐍 Python 3.8+
- 🤖 OpenAI Python SDK 1.0.0+
- 🌐 Works with all OpenAI models and endpoints

## 📚 Documentation

Full documentation is available at [https://revenium-middleware-openai.readthedocs.io/](https://revenium-middleware-openai.readthedocs.io/)

## 👥 Contributing

Contributions are welcome! Please check out our [contributing guidelines](CONTRIBUTING.md) for details.

1. 🍴 Fork the repository
2. 🌿 Create your feature branch (`git checkout -b feature/amazing-feature`)
3. 💾 Commit your changes (`git commit -m 'Add some amazing feature'`)
4. 🚀 Push to the branch (`git push origin feature/amazing-feature`)
5. 🔍 Open a Pull Request

## 📄 License

This project is licensed under the GNU Lesser General Public License v3.0 (LGPL-3.0) - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- 🔥 Thanks to the OpenAI team for creating an excellent API
- 💖 Built with ❤️ by the Revenium team
