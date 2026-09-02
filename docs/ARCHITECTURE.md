# Architecture

React + Vite calls a versioned FastAPI REST API. FastAPI owns market-data retrieval, indicator calculation, signal evaluation, risk rules, and SQLite persistence. Broker adapters remain read-only until manual-confirmation order flow is explicitly enabled.

