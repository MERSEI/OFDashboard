# OFDashboard

Streamlit management dashboard for creator agencies: fan messaging, content
planning, analytics and tiered access control.

**Live demo:** https://ofdashboard-production.up.railway.app

> Demo build. All data is seeded and generated locally — the app is not wired to any
> real platform account, and the credentials below are deliberately public.

| User | Password | Plan |
|---|---|---|
| `admin` | `admin123` | Premium |
| `operator1` | `password123` | Basic |
| `demo` | `demo` | Trial |

## Features

**Chats** — fan list with segment filters (VIP / Buyer / Free), message history,
AI-generated opener suggestions, quick send and clear.

**Content** — image-model selector, LoRA configuration by id or upload, pricing
calculator with markup and profit breakdown, generation preview.

**Analytics** — revenue, subscriber and session-time metrics, interactive Plotly
charts, goal tracking, top-fan ranking.

**Access control** — three plan tiers gating features per role.

## Stack

Python · Streamlit · Plotly · Pandas · Railway

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## License

MIT — see [LICENSE](LICENSE).
