# Replit Agent Guidelines

## Overview

This is a new Python project in its initial state. The repository currently contains a minimal "Hello World" application with no established architecture or framework. The project is a blank slate ready for development.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Current State
- **Language**: Python
- **Entry Point**: `main.py` with a simple main function
- **Structure**: Single-file application with no established patterns

### Architectural Decisions

Since this is a fresh project, no significant architectural decisions have been made yet. When building out this project:

1. **Project Structure**: Organize code into logical modules and packages as complexity grows
2. **Dependencies**: Add a `requirements.txt` or `pyproject.toml` for dependency management when external packages are needed
3. **Configuration**: Consider environment variables or config files for any settings that may change between environments

## External Dependencies

### Current Dependencies
None - the project uses only Python standard library.

### Future Considerations
When adding external services or dependencies:
- Document API keys and credentials needed in environment variables
- Add database connections if data persistence is required
- Include any third-party service integrations as they are introduced