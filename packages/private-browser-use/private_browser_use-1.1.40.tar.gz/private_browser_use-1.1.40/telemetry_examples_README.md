# Browser-Use Telemetry Examples

This directory contains examples of how to work with the browser-use telemetry system.

## Prerequisites

1. Install browser-use:
```bash
pip install browser-use
```

2. Install Playwright:
```bash
playwright install
```

3. Configure your API keys for models (create a `.env` file):
```
OPENAI_API_KEY=your_openai_api_key
```

## Examples

### 1. Send Example Telemetry Events

This script manually sends various telemetry events with example data:

```bash
python send_telemetry_example.py
```

This is useful for testing or understanding the telemetry system.

### 2. Agent With Telemetry Debugging

This example runs a browser-use agent with telemetry debugging enabled:

```bash
python agent_with_telemetry.py
```

This will:
1. Set logging level to debug to show telemetry events
2. Create and run a browser-use agent (which automatically sends telemetry)
3. Print telemetry information like user ID

## Disabling Telemetry

Telemetry can be disabled in two ways:

1. In your `.env` file:
```
ANONYMIZED_TELEMETRY=false
```

2. In your Python code:
```python
import os
os.environ["ANONYMIZED_TELEMETRY"] = "false"
```

## Telemetry Implementation Notes

- Browser-use uses PostHog for telemetry collection
- Data is anonymized with a random user ID stored at `~/.cache/browser_use/telemetry_user_id`
- No personally identifiable information is collected
- Telemetry captures information about:
  - Agent runs (model used, task description)
  - Agent steps (actions taken, success/failure)
  - Performance metrics (token usage, execution time)

For more information, see the [official telemetry documentation](https://docs.browser-use.com/development/telemetry). 