---
mode: agent
language: python
framework: fastapi
---

# Compile Specification to Code

**IMPORTANT**: This specification documents an **EXISTING, PRODUCTION APPLICATION** built over 6 months.

- Read and understand [the specification](./SPECIFICATION.md)
- The spec describes what **ALREADY EXISTS** in the codebase
- Use this spec to understand the current system architecture
- When making changes:
  - Follow the specification exactly as written
  - Maintain **strict backward compatibility** with ALL existing endpoints
  - Preserve existing database schemas and relationships
  - Keep existing file structure in `/api` directory
  - Test thoroughly before deploying changes
- Generate/update Python code using FastAPI framework
- Follow existing code patterns and conventions
- Follow Python best practices (PEP 8, type hints)

**The spec is documentation-as-code for the existing system.**






