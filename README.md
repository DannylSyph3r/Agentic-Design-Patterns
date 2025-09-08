# Agentic Design Patterns

Practical design patterns for building AI agents and workflows.

## What Are Agentic Design Patterns?

Reusable solutions for common problems in AI agent development. Each pattern includes working code and real-world examples you can implement immediately.

## Patterns

### 1. Prompt Chaining with LangChain ✅

**Problem:** Break down complex AI tasks into sequential steps where each step builds on the previous one.

**Solution:** Use LangChain's chaining operators (`|`) to create pipelines that automatically pass data between prompt templates.

**Example:** Blog content → Extract key points → Create Twitter thread → Format as JSON

**Key Concepts:**
- Chain composition with `|` operator
- Data transformation with `RunnableLambda`
- Single invoke executes entire pipeline

**When to use:** Multi-step content transformation, document processing, complex reasoning tasks.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Add your GOOGLE_API_KEY to .env
```