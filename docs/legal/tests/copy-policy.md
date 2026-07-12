# Copy policy check

- All legal UI strings must resolve via `copy-keys.yaml` keys.
- Deck must not contain forbidden lexicon (certain-future, medical, legal/financial, fear/dependency).
- Automated check: `python -m pytest` over a simple lexicon scan (see package tests if added).
