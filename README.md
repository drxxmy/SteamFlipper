# Steam Flipper (SF)

A Python service that periodically checks Steam Market prices for a predefined
list of liquid CS2 items, calculates net profit after Steam fees, and sends
Telegram notifications when profitable flip opportunities appear.

## Money loop

### Manual

- Bot scans Steam Market for profitable flips
- Bot sends Telegram alert
- User manually buys & sells

### Automated

- User enables auto-flip mode
- Bot buys & lists items automatically
- Bot notifies on each operation

## MVP constraints

| Area | Limit |
| ------------- | -------------- |
| Items tracked | 20-50 |
| Steam endpoints | priceoverview only |
| Storage | None |
| Auto-buy | No |
| UI | No |

## How to Run?

Sync dependencies using `uv` package manager:

```bash
uv sync
```

Run script:

```bash
python main.py
```
