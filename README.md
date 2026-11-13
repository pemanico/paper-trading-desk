# Paper Trading Desk - Professional Risk Simulation

Skeleton for paper trading simulation of Solana-style altcoins using professional risk management criteria.

## Structure
- `skeleton_paper.py` — Core simulation (filters, sizing, logging)
- `app.py` — Streamlit visualizer
- `requirements.txt` — Dependencies

## Setup

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Run simulation
```bash
python skeleton_paper.py
```

## Run visualizer
```bash
streamlit run app.py
```

## Notes
- High rejection rates are expected with strict professional filters.
- Expectancy is typically negative or near zero in high-friction low-liquidity markets.
- This is for learning the process, not for live trading.
