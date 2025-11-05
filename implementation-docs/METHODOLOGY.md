# Spec-Driven Development for Parrot (iPersona)

This document explains how to use spec-driven development with AI coding agents for the Parrot project, following the [GitHub blog post approach](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-using-markdown-as-a-programming-language-when-building-with-ai/).

## What is Spec-Driven Development?

Spec-driven development is a methodology where you:
1. Write specifications in Markdown (in `SPECIFICATION.md`)
2. Use AI coding agents to compile specifications into working code
3. Iteratively refine specifications and regenerate code

## Files in This Project

### `SPECIFICATION.md`
The master specification document that describes:
- Database architecture and schemas
- API endpoints and their behavior
- Real-time Socket.IO events
- Background task processing
- Authentication flows
- Core features and workflows

### `COMPILE_GUIDE.md`
Instructions for the AI coding agent to compile `SPECIFICATION.md` into Python code.

### `LINT_GUIDE.md`
Instructions for cleaning up and optimizing the Markdown specification.

## How to Use This Approach

### 1. Update the Specification

Edit `SPECIFICATION.md` to describe desired changes. For example:

```markdown
### New Feature: Video Interview Support

Add video analysis capabilities:

1. Accept video file uploads in addition to audio
2. Extract frames at 1-second intervals
3. Analyze facial expressions and body language
4. Integrate video analysis into overall evaluation
```

### 2. Compile to Code

Use GitHub Copilot Chat or any AI coding agent with the compile prompt:

**Option A: GitHub Copilot Chat**
```
/load implementation-docs/COMPILE_GUIDE.md
```

**Option B: Manual instruction**
```
Read the specification in implementation-docs/SPECIFICATION.md and update the codebase accordingly. 
Focus on [specific feature mentioned in the spec].
```

### 3. Test and Iterate

1. Run the application
2. Test new features
3. If something doesn't work, update `SPECIFICATION.md` to clarify the requirements
4. Recompile using step 2

### 4. Lint the Specification (Optional)

As the spec grows, it may become messy. Clean it up:

```
/load implementation-docs/LINT_GUIDE.md
```

This will:
- Remove duplicate content
- Standardize terminology (e.g., always use "fetch" instead of "get/pull/fetch")
- Improve clarity and conciseness
- Preserve all important details

## Example Workflow

### Adding a New Endpoint

**Step 1: Update `SPECIFICATION.md`**

Add to the "API Endpoints Summary" section:

```markdown
### User Analytics
- `GET /api/ipersona/user/{user_id}/stats` - Get interview statistics
  - Returns: Total interviews, average score, improvement trends
  - Requires authentication
```

**Step 2: Compile**

```
Update the application to add the user stats endpoint as described in implementation-docs/SPECIFICATION.md
```

**Step 3: Test**

```bash
curl -X GET http://localhost:9900/api/ipersona/user/123/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Modifying Existing Feature

**Step 1: Update `SPECIFICATION.md`**

Find the relevant section and modify:

```markdown
### Real-Time Evaluation

Modify to include sentiment analysis:
1. Perform existing evaluation
2. Add sentiment analysis using OpenAI
3. Include sentiment score in response
```

**Step 2: Compile**

```
Update the real-time evaluation feature as specified in implementation-docs/SPECIFICATION.md, 
focusing on adding sentiment analysis.
```

## Benefits of This Approach

1. **Documentation and code stay in sync**: The spec IS the documentation
2. **Clear thinking**: Writing specs forces you to think clearly about requirements
3. **Reproducible**: Can regenerate the app from scratch in any language
4. **Version control**: Spec changes show the evolution of requirements
5. **Collaboration**: Team members can discuss specifications before coding

## Tips for Success

### Writing Good Specs

1. **Be specific**: Use concrete examples, not vague descriptions
2. **Include edge cases**: What happens when things go wrong?
3. **Show data structures**: Include JSON examples of inputs/outputs
4. **Specify error handling**: How should errors be handled?
5. **Include testing info**: How to verify it works?

### Using AI Coding Agents

1. **Be incremental**: Update small parts of the spec at a time
2. **Test frequently**: Don't let the spec grow too large before compiling
3. **Use focus directives**: Guide the AI with "focus on [feature]"
4. **Review generated code**: AI may not always get it right on first try

### Maintaining the Spec

1. **Keep it up to date**: Update spec when code changes
2. **Regular linting**: Run LINT_GUIDE.md periodically
3. **Remove outdated sections**: Don't let dead code live in the spec
4. **Add context**: Include why decisions were made

## Tools Integration

### GitHub Copilot (VS Code)

Use these commands in GitHub Copilot Chat:
- `/load implementation-docs/COMPILE_GUIDE.md` - Compile the spec
- `/load implementation-docs/LINT_GUIDE.md` - Clean up the spec
- `/focus on [feature]` - Focus compilation on specific feature

### Other AI Coding Agents

You can adapt this approach to other tools:
- ChatGPT with Code Interpreter
- Claude with Code
- Cursor AI
- Any agent that can read Markdown and modify code

## Current Status

The `SPECIFICATION.md` file currently describes:
- ✅ Database architecture
- ✅ API endpoints
- ✅ Real-time Socket.IO communication
- ✅ Background task processing with Celery
- ✅ Authentication and authorization
- ✅ Speech-to-text services
- ✅ Question generation and evaluation
- ✅ Structured matching system

## Next Steps

1. **Add comprehensive testing**: Document how to test each feature
2. **Add deployment docs**: Document Docker and production deployment
3. **Add monitoring setup**: Document logging and monitoring
4. **Refine specifications**: As you work, refine the spec for clarity

## References

- [Original Blog Post](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-using-markdown-as-a-programming-language-when-building-with-ai/)
- [Example from Blog Post](https://github.com/wham/github-sync)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Socket.IO Documentation](https://socket.io/docs/)

## Contributing

When contributing to this project:

1. Read and understand `SPECIFICATION.md` first
2. Make spec changes in `SPECIFICATION.md`
3. Compile using `COMPILE_GUIDE.md`
4. Test thoroughly
5. Update `SPECIFICATION.md` if code changes during implementation
6. Consider linting with `LINT_GUIDE.md` before committing







