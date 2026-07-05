# Culinary Expert System

Rule-based culinary expert system built in Python for reasoning about recipes, ingredients, allergens, dietary restrictions, nutrition, and food pairings.

## Overview

This is a collaborative academic project for a Knowledge-Based Systems course. The goal was to model culinary knowledge in a way that can be queried and explained, using symbolic rules instead of a black-box model.

The system focuses on practical questions such as:

- Which recipes are compatible with a dietary restriction?
- Which ingredients introduce allergens or nutritional constraints?
- Which ingredient or dish combinations make sense together?
- How can culinary knowledge be represented in a structured knowledge base?

## Tech Stack

- Python 3.13
- Custom knowledge-base parser and query engine
- PyParsing
- Pytest
- uv for dependency management

## Repository Highlights

- `kb/` contains the main culinary knowledge base.
- `sbc/` contains the parser, loader, unification logic, query handling, and CLI.
- `test/` contains automated tests for the reasoning components.
- `doc/` and delivery notes document the project context and iterations.

## How to Run

```bash
uv sync
uv run python -m sbc.cli
uv run pytest
```

## What This Shows

- Modeling a domain with explicit rules and structured facts.
- Building a small inference-oriented Python codebase.
- Testing core reasoning utilities.
- Translating open-ended domain knowledge into executable logic.

## Context

Collaborative academic project by Alvaro Alonso, Jiahao Cheng, Francisco Pastor, and Jiayi Wang.
