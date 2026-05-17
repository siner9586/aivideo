# roadmap

This document belongs to AI Video Studio MVP.

## Summary

AI Video Studio uses a modular FastAPI backend, a React workbench, and replaceable VideoBackend implementations. The current version prioritizes CPU-runnable mock generation and stable engineering contracts over downloading large closed or open video foundation models.

## Notes

- Use mock backend first for end-to-end testing.
- Configure real models through .env and MODEL_PATH.
- Keep API keys outside source code.
- Apply safety checks before generation.
