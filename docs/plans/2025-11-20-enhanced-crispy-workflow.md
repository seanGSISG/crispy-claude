# Enhanced CrispyClaude Workflow Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use the executing-plans skill to implement this plan task-by-task.

**Goal:** Add research capabilities, plan validation, state persistence, and PR automation to CrispyClaude workflow

**Architecture:** Create new slash commands (`/cc:research`, `/cc:parse-plan`, `/cc:review-plan`, `/cc:save`, `/cc:resume`, `/cc:pr`, `/cc:crispy`) backed by skills that orchestrate MCP-powered subagents. Research subagents are defined as agent files with frontmatter metadata. State persistence uses Serena MCP memory with stage-specific naming.

**Tech Stack:** Claude Agent SDK, Serena MCP, Context7 MCP, WebSearch, GitHub CLI, Markdown frontmatter

---

## Phase 1: Research Infrastructure

### Task 1: Create using-serena-for-exploration skill

**Files:**
- Create: `cc/skills/using-serena-for-exploration/SKILL.md`

**Step 1: Create skill directory**

```bash
mkdir -p cc/skills/using-serena-for-exploration
```

**Step 2: Write the skill file**

Create `cc/skills/using-serena-for-exploration/SKILL.md`:

```markdown
# Using Serena for Exploration

Use this skill when exploring codebases with Serena MCP tools for architectural understanding and pattern discovery.

## Core Principles

- Start broad, narrow progressively
- Use symbolic tools before reading full files
- Always provide file:line references
- Minimize token usage through targeted reads

## Workflow

### 1. Initial Discovery

**Use `list_dir` and `find_file`** to understand project structure:

```bash
# Get repository overview
list_dir(relative_path=".", recursive=false)

# Find specific file types
find_file(file_mask="*auth*.py", relative_path="src")
```

### 2. Symbol Overview

**Use `get_symbols_overview`** before reading full files:

```python
# Get top-level symbols in a file
get_symbols_overview(relative_path="src/auth/handler.py")
```

Returns classes, functions, imports - understand structure without reading bodies.

### 3. Targeted Symbol Reading

**Use `find_symbol`** for specific code:

```python
# Read a specific class without body
find_symbol(
    name_path_pattern="AuthHandler",
    relative_path="src/auth/handler.py",
    include_body=false,
    depth=1  # Include methods list
)

# Read specific method with body
find_symbol(
    name_path_pattern="AuthHandler/login",
    relative_path="src/auth/handler.py",
    include_body=true
)
```

**Name path patterns:**
- Simple name: `"login"` - matches any symbol named "login"
- Relative path: `"AuthHandler/login"` - matches method in class
- Absolute path: `"/AuthHandler/login"` - exact match within file
- With index: `"AuthHandler/login[0]"` - specific overload

### 4. Pattern Searching

**Use `search_for_pattern`** when you don't know symbol names:

```python
# Find all JWT usage
search_for_pattern(
    substring_pattern="jwt\\.encode",
    relative_path="src",
    restrict_search_to_code_files=true,
    context_lines_before=2,
    context_lines_after=2,
    output_mode="content"
)
```

**Pattern matching:**
- Uses regex with DOTALL flag (. matches newlines)
- Non-greedy quantifiers preferred: `.*?` not `.*`
- Escape special chars: `\\{\\}` for literal braces

### 5. Relationship Discovery

**Use `find_referencing_symbols`** to understand dependencies:

```python
# Who calls this function?
find_referencing_symbols(
    name_path="authenticate_user",
    relative_path="src/auth/handler.py"
)
```

Returns code snippets around references with symbolic info.

## Reporting Format

Always structure findings as:

```markdown
## Codebase Findings

### Current Architecture
- **Authentication:** `src/auth/handler.py:45-120`
  - JWT-based auth with refresh tokens
  - Session storage in Redis

### Similar Implementations
- **User management:** `src/users/controller.py:200-250`
  - Uses similar validation pattern
  - Can reuse `validate_credentials()` helper

### Integration Points
- **Middleware:** `src/middleware/auth.py:30`
  - Hook new auth method here
  - Follows pattern: check → validate → attach user
```

## Anti-Patterns

❌ **Don't:** Read entire files before understanding structure
✅ **Do:** Use `get_symbols_overview` first

❌ **Don't:** Use full file reads for symbol searches
✅ **Do:** Use `find_symbol` with targeted name paths

❌ **Don't:** Search without context limits
✅ **Do:** Use `relative_path` to restrict search scope

❌ **Don't:** Return findings without file:line references
✅ **Do:** Always include exact locations: `file.py:123-145`

## Token Efficiency

- Overview tools use ~500 tokens vs. ~5000 for full file
- Targeted symbol reads use ~200 tokens per symbol
- Pattern search with `head_limit=20` caps results
- Use `depth=0` if you don't need child symbols

## Example Session

```python
# 1. Find auth-related files
files = find_file(file_mask="*auth*.py", relative_path="src")
# → Found: src/auth/handler.py, src/auth/middleware.py

# 2. Get overview of main handler
overview = get_symbols_overview(relative_path="src/auth/handler.py")
# → Classes: AuthHandler
# → Functions: authenticate_user, validate_token

# 3. Read specific method
method = find_symbol(
    name_path_pattern="AuthHandler/authenticate_user",
    relative_path="src/auth/handler.py",
    include_body=true
)
# → Got full implementation of authenticate_user

# 4. Find who calls this
refs = find_referencing_symbols(
    name_path="authenticate_user",
    relative_path="src/auth/handler.py"
)
# → Called from: middleware.py:67, api/routes.py:123
```
```

**Step 3: Verify file created**

```bash
ls -la cc/skills/using-serena-for-exploration/SKILL.md
```

Expected: File exists with content

**Step 4: Commit**

```bash
git add cc/skills/using-serena-for-exploration/
git commit -m "feat: add using-serena-for-exploration skill"
```

### Task 2: Create using-context7-for-docs skill

**Files:**
- Create: `cc/skills/using-context7-for-docs/SKILL.md`

**Step 1: Create skill directory**

```bash
mkdir -p cc/skills/using-context7-for-docs
```

**Step 2: Write the skill file**

Create `cc/skills/using-context7-for-docs/SKILL.md`:

```markdown
# Using Context7 for Documentation

Use this skill when researching library documentation with Context7 MCP tools for official patterns and best practices.

## Core Principles

- Always resolve library ID first (unless user provides exact ID)
- Use topic parameter to focus documentation
- Paginate when initial results insufficient
- Prioritize high benchmark scores and reputation

## Workflow

### 1. Resolve Library ID

**Use `resolve-library-id`** before fetching docs:

```python
# Search for library
result = resolve_library_id(libraryName="react")

# Returns matches with:
# - Context7 ID (e.g., "/facebook/react")
# - Description
# - Code snippet count
# - Source reputation (High/Medium/Low)
# - Benchmark score (0-100, higher is better)
```

**Selection criteria:**
1. Exact name match preferred
2. Higher documentation coverage (more snippets)
3. High/Medium reputation sources
4. Higher benchmark scores (aim for 80+)

**Example output:**

```markdown
Selected: /facebook/react
Reason: Official React repository, High reputation, 850 snippets, Benchmark: 95
```

### 2. Fetch Documentation

**Use `get-library-docs`** with resolved ID:

```python
# Get focused documentation
docs = get_library_docs(
    context7CompatibleLibraryID="/facebook/react",
    topic="hooks",
    page=1
)
```

**Topic parameter:**
- Focuses results on specific area
- Examples: "hooks", "routing", "authentication", "testing"
- More specific = better results

**Pagination:**
- Default `page=1` returns first batch
- If insufficient, try `page=2`, `page=3`, etc.
- Maximum `page=10`

### 3. Version-Specific Docs

**Include version in ID** when needed:

```python
# Specific version
docs = get_library_docs(
    context7CompatibleLibraryID="/vercel/next.js/v14.3.0-canary.87",
    topic="server components"
)
```

Use when:
- Project uses specific version
- Breaking changes between versions
- Need migration guidance

## Reporting Format

Structure findings as:

```markdown
## Library Documentation Findings

### Library: React 18
**Context7 ID:** /facebook/react
**Benchmark Score:** 95

### Relevant APIs

**useEffect Hook** (Official pattern)
```javascript
// Recommended: Cleanup pattern
useEffect(() => {
  const subscription = api.subscribe()
  return () => subscription.unsubscribe()
}, [dependencies])
```
Source: React docs, hooks section

### Best Practices

1. **Dependency Arrays**
   - Always specify dependencies
   - Use exhaustive-deps ESLint rule
   - Avoid functions in dependencies

2. **Performance**
   - Prefer useMemo for expensive calculations
   - useCallback for function props
   - React.memo for component memoization

### Migration Notes
- React 18 introduces concurrent features
- Automatic batching now default
- Upgrade guide: /facebook/react/v18/migration
```

## Common Libraries

**Frontend:**
- React: `/facebook/react`
- Next.js: `/vercel/next.js`
- Vue: `/vuejs/vue`
- Svelte: `/sveltejs/svelte`

**Backend:**
- Express: `/expressjs/express`
- FastAPI: `/tiangolo/fastapi`
- Django: `/django/django`

**Tools:**
- TypeScript: `/microsoft/typescript`
- Vite: `/vitejs/vite`
- Jest: `/jestjs/jest`

## Anti-Patterns

❌ **Don't:** Skip resolve-library-id step
✅ **Do:** Always resolve first (unless user provides exact ID)

❌ **Don't:** Use vague topics like "general"
✅ **Do:** Use specific topics: "authentication", "state management"

❌ **Don't:** Accept low benchmark scores (<50) without checking alternatives
✅ **Do:** Prefer high-quality sources (benchmark 80+)

❌ **Don't:** Cite docs without library version
✅ **Do:** Include version in findings

## Example Session

```python
# 1. Resolve library
result = resolve_library_id(libraryName="fastapi")
# → Selected: /tiangolo/fastapi (Benchmark: 92, High reputation)

# 2. Get auth documentation
docs = get_library_docs(
    context7CompatibleLibraryID="/tiangolo/fastapi",
    topic="authentication",
    page=1
)
# → Got OAuth2, JWT patterns, security best practices

# 3. Need more detail on dependencies
docs2 = get_library_docs(
    context7CompatibleLibraryID="/tiangolo/fastapi",
    topic="dependency injection",
    page=1
)
# → Got Depends() patterns, testing with overrides

# 4. Check pagination if needed
if insufficient:
    docs3 = get_library_docs(
        context7CompatibleLibraryID="/tiangolo/fastapi",
        topic="authentication",
        page=2  # Next page
    )
```

## Quality Indicators

**High-quality results have:**
- ✅ Benchmark score 80+
- ✅ High/Medium source reputation
- ✅ Recent documentation (check dates)
- ✅ Official repositories
- ✅ Code examples with explanation

**Consider alternatives if:**
- ❌ Benchmark score <50
- ❌ Low reputation source
- ❌ Very few code snippets (<10)
- ❌ Unofficial/outdated sources
```

**Step 3: Verify file created**

```bash
ls -la cc/skills/using-context7-for-docs/SKILL.md
```

Expected: File exists with content

**Step 4: Commit**

```bash
git add cc/skills/using-context7-for-docs/
git commit -m "feat: add using-context7-for-docs skill"
```

### Task 3: Create using-web-search skill

**Files:**
- Create: `cc/skills/using-web-search/SKILL.md`

**Step 1: Create skill directory**

```bash
mkdir -p cc/skills/using-web-search
```

**Step 2: Write the skill file**

Create `cc/skills/using-web-search/SKILL.md`:

```markdown
# Using Web Search

Use this skill when researching best practices, tutorials, and expert opinions using WebSearch and WebFetch tools.

## Core Principles

- Search with specific, current queries
- Fetch promising results for detailed analysis
- Assess source authority and recency
- Synthesize findings with citations

## Workflow

### 1. Craft Search Query

**Be specific and current:**

```python
# ❌ Vague
WebSearch(query="authentication best practices")

# ✅ Specific
WebSearch(query="OAuth2 JWT authentication Node.js 2024")
```

**Query patterns:**
- Technology + use case + year: `"React server-side rendering 2024"`
- Problem + solution: `"avoid N+1 queries GraphQL"`
- Comparison: `"REST vs GraphQL microservices 2024"`
- Pattern: `"repository pattern TypeScript best practices"`

**Account for current date:**
- Current date from <env>: Check "Today's date"
- Use current/recent year in queries
- Avoid outdated year filters (e.g., don't search "2024" if it's 2025)

### 2. Domain Filtering

**Include trusted sources:**

```python
# Focus on specific domains
WebSearch(
    query="React performance optimization",
    allowed_domains=["react.dev", "web.dev", "kentcdodds.com"]
)
```

**Block unreliable sources:**

```python
# Exclude low-quality sites
WebSearch(
    query="TypeScript patterns",
    blocked_domains=["w3schools.com", "tutorialspoint.com"]
)
```

**Trusted sources by category:**

**Frontend:**
- react.dev, web.dev, developer.mozilla.org
- kentcdodds.com, joshwcomeau.com, overreacted.io

**Backend:**
- martinfowler.com, 12factor.net
- fastapi.tiangolo.com, docs.python.org

**Architecture:**
- microservices.io, aws.amazon.com/blogs
- martinfowler.com, thoughtworks.com

**Security:**
- owasp.org, auth0.com/blog, securityheaders.com

### 3. Fetch and Analyze

**Use WebFetch** for detailed content:

```python
# Fetch specific article
content = WebFetch(
    url="https://kentcdodds.com/blog/authentication-patterns",
    prompt="Extract key recommendations for authentication patterns, including code examples and security considerations"
)
```

**Fetch prompt patterns:**
- "Extract key recommendations for [topic]"
- "Summarize best practices with code examples"
- "List security considerations and common pitfalls"
- "Compare approaches mentioned with pros/cons"

### 4. Authority Assessment

**Evaluate sources:**

```markdown
Source: Kent C. Dodds - Authentication Patterns (2024)
Authority: ⭐⭐⭐⭐⭐
- Industry expert, React core contributor
- Recent publication (Jan 2024)
- Cited by 50+ articles
- Production examples from real apps
```

**Authority indicators:**
- ✅ Known experts in field
- ✅ Official documentation
- ✅ Recent publication dates
- ✅ Specific, detailed examples
- ✅ Acknowledges trade-offs

**Red flags:**
- ❌ No author/date
- ❌ Generic advice without context
- ❌ No code examples
- ❌ Outdated libraries/patterns
- ❌ Copy-pasted content

## Reporting Format

Structure findings as:

```markdown
## Web Research Findings

### 1. Authentication Best Practices

**Source:** Auth0 Blog - "Modern Authentication Patterns" (2024-10-15)
**Authority:** ⭐⭐⭐⭐⭐ (Official security vendor documentation)
**URL:** https://auth0.com/blog/authentication-patterns

**Key Recommendations:**

1. **Token Storage**
   > "Never store tokens in localStorage due to XSS vulnerabilities. Use httpOnly cookies for refresh tokens."

   - ✅ Refresh tokens → httpOnly cookies
   - ✅ Access tokens → memory only
   - ❌ localStorage for sensitive data

2. **Token Rotation**
   ```javascript
   // Recommended pattern
   const rotateToken = async (refreshToken) => {
     const { access, refresh } = await api.rotate(refreshToken)
     invalidateOldToken(refreshToken)
     return { access, refresh }
   }
   ```

**Trade-offs:**
- Memory-only tokens lost on refresh (need refresh flow)
- HttpOnly cookies require CSRF protection
- Complexity vs. security balance

---

### 2. Performance Optimization

**Source:** web.dev - "React Performance Guide" (2024-08)
**Authority:** ⭐⭐⭐⭐⭐ (Google official web platform docs)
**URL:** https://web.dev/react-performance

**Findings:**

1. **Code Splitting**
   - Lazy load routes: 40% faster initial load
   - Use React.lazy() + Suspense
   - Combine with route-based splitting

2. **Memoization Strategy**
   - useMemo for expensive computations (>16ms)
   - useCallback only when passed to memoized children
   - Don't over-optimize - measure first

**Benchmarks cited:**
- Code splitting: 2.1s → 1.3s load time
- Proper memoization: 15% render reduction
```

## Search Strategies

### Pattern Discovery
```python
WebSearch(query="factory pattern TypeScript best practices 2024")
```

### Problem Solutions
```python
WebSearch(query="prevent race conditions React useEffect")
```

### Technology Comparisons
```python
WebSearch(query="Prisma vs TypeORM PostgreSQL 2024")
```

### Migration Guides
```python
WebSearch(query="migrate Express to Fastify performance")
```

## Anti-Patterns

❌ **Don't:** Search without year context
✅ **Do:** Include current year for recent practices

❌ **Don't:** Accept first result without verification
✅ **Do:** Fetch 2-3 sources, compare findings

❌ **Don't:** Copy recommendations without understanding
✅ **Do:** Synthesize findings, note trade-offs

❌ **Don't:** Skip source credibility check
✅ **Do:** Assess authority, recency, specificity

## Citation Format

Always cite findings:

```markdown
**Recommendation:** Use dependency injection for testability

Source: Martin Fowler - "Inversion of Control Containers" (2023)
URL: https://martinfowler.com/articles/injection.html
Authority: ⭐⭐⭐⭐⭐ (Industry thought leader, 20+ years)

Quote: "Constructor injection makes dependencies explicit and enables testing without mocks."
```

## Example Session

```python
# 1. Search for auth patterns
results = WebSearch(
    query="JWT refresh token rotation Node.js 2024",
    allowed_domains=["auth0.com", "oauth.net"]
)
# → Found 5 articles from Auth0, OAuth.net

# 2. Fetch most promising
article1 = WebFetch(
    url="https://auth0.com/blog/refresh-tokens-rotation",
    prompt="Extract token rotation implementation patterns and security considerations"
)
# → Got detailed rotation strategy with code

# 3. Fetch second source for comparison
article2 = WebFetch(
    url="https://oauth.net/2/refresh-tokens/",
    prompt="Summarize OAuth2 refresh token best practices"
)
# → Got official OAuth2 spec recommendations

# 4. Search for implementation gotchas
gotchas = WebSearch(
    query="JWT refresh token common mistakes pitfalls"
)
# → Found 3 articles on common errors

# 5. Synthesize findings
# Compare sources, note consensus vs. disagreement
# Highlight trade-offs and context-specific advice
```

## Quality Indicators

**High-quality findings have:**
- ✅ Multiple authoritative sources agree
- ✅ Publication dates within last 2 years
- ✅ Specific code examples with explanation
- ✅ Acknowledges trade-offs and context
- ✅ Cites benchmarks or case studies

**Reconsider if:**
- ❌ Only one source found
- ❌ Sources conflict without explanation
- ❌ Generic advice without specifics
- ❌ Outdated patterns (>3 years old for web)
- ❌ No consideration of modern alternatives
```

**Step 3: Verify file created**

```bash
ls -la cc/skills/using-web-search/SKILL.md
```

Expected: File exists with content

**Step 4: Commit**

```bash
git add cc/skills/using-web-search/
git commit -m "feat: add using-web-search skill"
```

### Task 4: Create using-github-search skill

**Files:**
- Create: `cc/skills/using-github-search/SKILL.md`

**Step 1: Create skill directory**

```bash
mkdir -p cc/skills/using-github-search
```

**Step 2: Write the skill file**

Create `cc/skills/using-github-search/SKILL.md`:

```markdown
# Using GitHub Search

Use this skill when researching GitHub issues, PRs, discussions for community solutions and known gotchas.

## Core Principles

- Search GitHub via WebSearch with site: filter
- Focus on closed issues (solved problems)
- Fetch promising threads for detailed analysis
- Extract problem-solution patterns

## Workflow

### 1. Issue Search

**Use WebSearch with site:github.com:**

```python
# Find closed issues with solutions
WebSearch(
    query="site:github.com React useEffect memory leak closed"
)
```

**Search patterns:**

**Closed issues (solved problems):**
```python
query="site:github.com [repo-name] [problem] closed is:issue"
```

**Pull requests (implementation examples):**
```python
query="site:github.com [repo-name] [feature] is:pr merged"
```

**Discussions (community advice):**
```python
query="site:github.com [repo-name] [topic] is:discussion"
```

**Labels for filtering:**
```python
query="site:github.com react label:bug label:performance closed"
```

### 2. Repository-Specific Search

**Known repositories:**

```python
# React issues
WebSearch(query="site:github.com/facebook/react useEffect cleanup closed")

# Next.js issues
WebSearch(query="site:github.com/vercel/next.js SSR hydration closed")

# TypeScript issues
WebSearch(query="site:github.com/microsoft/typescript type inference closed")
```

**Community repositories:**

```python
# Awesome lists
WebSearch(query="site:github.com awesome-react authentication")

# Best practice repos
WebSearch(query="site:github.com typescript best practices")
```

### 3. Fetch Issue Details

**Use WebFetch** to analyze threads:

```python
# Fetch specific issue
thread = WebFetch(
    url="https://github.com/facebook/react/issues/14326",
    prompt="Extract the problem description, root cause, and accepted solution. Include any workarounds or caveats mentioned."
)
```

**Fetch prompt patterns:**
- "Summarize the problem and official solution"
- "Extract workarounds and their trade-offs"
- "List breaking changes and migration steps"
- "Identify root cause and fix explanation"

### 4. Pattern Recognition

Look for **common patterns:**

**Problem-Solution:**
```markdown
Problem: Memory leak with event listeners in useEffect
Solution: Return cleanup function
Frequency: 50+ issues
Pattern: Missing return in useEffect
```

**Gotchas:**
```markdown
Gotcha: Array.sort() mutates in place
Impact: React state updates fail silently
Workaround: [...arr].sort()
Source: 20+ issues across projects
```

## Reporting Format

Structure findings as:

```markdown
## GitHub Research Findings

### 1. React useEffect Memory Leaks

**Source:** facebook/react#14326 (Closed, 150+ comments)
**Status:** Resolved in React 18
**URL:** https://github.com/facebook/react/issues/14326

**Problem:**
Event listeners added in useEffect not cleaned up, causing memory leaks on component unmount.

**Root Cause:**
Missing cleanup function in useEffect hook.

**Solution:**
```javascript
useEffect(() => {
  const handler = () => console.log('event')
  window.addEventListener('resize', handler)

  // Cleanup function
  return () => window.removeEventListener('resize', handler)
}, [])
```

**Caveats:**
- Cleanup runs before next effect AND on unmount
- Don't cleanup external state (e.g., API calls may complete after unmount)
- Use AbortController for fetch requests

**Community Consensus:**
- 95% of comments recommend cleanup pattern
- Official docs updated to emphasize this
- ESLint rule available: `exhaustive-deps`

---

### 2. Next.js Hydration Mismatch

**Source:** vercel/next.js#7417 (Closed, 80+ comments)
**Status:** Workarounds available, improved errors in Next 13+
**URL:** https://github.com/vercel/next.js/issues/7417

**Problem:**
Server-rendered HTML differs from client, causing hydration errors.

**Common Causes:**
1. Date.now() or random values in render
2. window object access during SSR
3. Third-party scripts modifying DOM

**Solutions:**

**Approach 1: Suppress hydration warning (temporary)**
```jsx
<div suppressHydrationWarning>{Date.now()}</div>
```

**Approach 2: Client-only rendering**
```jsx
const [mounted, setMounted] = useState(false)
useEffect(() => setMounted(true), [])
if (!mounted) return null
return <div>{Date.now()}</div>
```

**Approach 3: Use next/dynamic**
```jsx
const ClientOnly = dynamic(() => import('./ClientOnly'), { ssr: false })
```

**Trade-offs:**
- Suppress: Quick but masks real issues
- Client-only: Flash of missing content
- Dynamic: Extra bundle split, best for isolated components

**Community Recommendation:**
Use dynamic imports for truly client-only components. Fix server/client differences when possible.

---

### 3. TypeScript Type Inference Limitations

**Source:** microsoft/typescript#10571 (Open, discussion ongoing)
**Status:** Design limitation, workarounds exist
**URL:** https://github.com/microsoft/typescript/issues/10571

**Problem:**
Generic type inference fails with complex nested structures.

**Workarounds:**

**Explicit type parameters:**
```typescript
// Instead of inference
const result = complexFunction<User, string>(data)
```

**Type assertions:**
```typescript
const result = complexFunction(data) as Result<User>
```

**Community Patterns:**
- 40% use explicit type parameters
- 30% restructure code to simplify inference
- 30% use type assertions with validation

**Gotcha:**
Type assertions bypass type checking. Validate at runtime or use type guards.
```

## Search Strategies

### Find Solved Problems
```python
WebSearch(query="site:github.com react hooks stale closure closed is:issue")
```

### Implementation Examples
```python
WebSearch(query="site:github.com authentication JWT refresh is:pr merged")
```

### Breaking Changes
```python
WebSearch(query="site:github.com next.js migration breaking changes v14")
```

### Community Discussions
```python
WebSearch(query="site:github.com typescript best practices is:discussion")
```

### Security Issues
```python
WebSearch(query="site:github.com express security vulnerability closed CVE")
```

## Anti-Patterns

❌ **Don't:** Only search open issues (may not have solutions)
✅ **Do:** Focus on closed issues with accepted solutions

❌ **Don't:** Trust first comment without reading thread
✅ **Do:** Read accepted solution and top comments

❌ **Don't:** Apply workarounds without understanding trade-offs
✅ **Do:** Document caveats and alternatives

❌ **Don't:** Assume issue applies to current version
✅ **Do:** Check version context and current status

## Quality Indicators

**High-value issues have:**
- ✅ Closed with accepted solution
- ✅ 20+ comments (community vetted)
- ✅ Official maintainer response
- ✅ Code examples in solution
- ✅ Referenced in docs or other issues

**Skip if:**
- ❌ Open with no recent activity
- ❌ No clear solution or consensus
- ❌ Very old (>2 years) without recent confirmation
- ❌ Off-topic discussion
- ❌ No code examples

## Example Session

```python
# 1. Search for known React issues
results = WebSearch(
    query="site:github.com/facebook/react useEffect infinite loop closed"
)
# → Found 10 closed issues

# 2. Fetch most relevant
issue1 = WebFetch(
    url="https://github.com/facebook/react/issues/12345",
    prompt="Extract the root cause of infinite loops in useEffect and the recommended solution"
)
# → Got dependency array explanation and fix

# 3. Search for migration issues
migration = WebSearch(
    query="site:github.com/vercel/next.js migrate v13 to v14 breaking changes"
)
# → Found migration guide and common issues

# 4. Fetch migration PR
pr = WebFetch(
    url="https://github.com/vercel/next.js/pull/56789",
    prompt="List all breaking changes and required code updates"
)
# → Got comprehensive migration checklist

# 5. Search for community patterns
patterns = WebSearch(
    query="site:github.com awesome-typescript patterns is:repo"
)
# → Found curated best practices repo

# 6. Synthesize findings
# Combine issue solutions, migration steps, community patterns
# Note frequency of issues, consensus solutions
```

## Citation Format

```markdown
**Issue:** Memory leak in React hooks
**Source:** facebook/react#14326 (Closed)
**URL:** https://github.com/facebook/react/issues/14326
**Status:** Resolved in React 18
**Comments:** 150+ (High community engagement)

**Official Response:**
> "The cleanup function must be returned from useEffect. This is critical for preventing memory leaks." - Dan Abramov (React team)

**Community Consensus:**
95% of solutions recommend cleanup pattern. ESLint rule added to enforce.
```

## Useful Repositories

**Best Practices:**
- awesome-[tech] lists (curated resources)
- [framework]-best-practices repos
- [company]-engineering-blogs

**Security:**
- OWASP repos for security patterns
- CVE databases for vulnerabilities
- Security advisories in popular frameworks

**Migration Guides:**
- Official framework upgrade guides
- Community migration experience issues
- Breaking change tracking issues
```

**Step 3: Verify file created**

```bash
ls -la cc/skills/using-github-search/SKILL.md
```

Expected: File exists with content

**Step 4: Commit**

```bash
git add cc/skills/using-github-search/
git commit -m "feat: add using-github-search skill"
```

---

## Phase 2: Research Agents & Orchestration

### Task 5: Create serena-explorer agent

**Files:**
- Create: `cc/agents/serena-explorer.md`

**Step 1: Create agents directory**

```bash
mkdir -p cc/agents
```

**Step 2: Write agent file**

Create `cc/agents/serena-explorer.md`:

```markdown
---
name: serena-explorer
description: Codebase exploration specialist using Serena MCP for architectural understanding and pattern discovery
tools: [Serena MCP]
skill: using-serena-for-exploration
model: sonnet
---

# Serena Explorer Agent

You are a codebase exploration specialist. Use Serena MCP tools to understand architecture, find similar implementations, and trace dependencies.

Follow the `using-serena-for-exploration` skill for best practices on:
- Using find_symbol for targeted code discovery
- Using search_for_pattern for broader searches
- Using get_symbols_overview for file structure understanding
- Providing file:line references in all findings

Report findings with:
- File paths and line numbers
- Architectural patterns discovered
- Integration points identified
- Relevant code snippets with context
```

**Step 3: Verify file created**

```bash
cat cc/agents/serena-explorer.md | head -20
```

Expected: Frontmatter and content visible

**Step 4: Commit**

```bash
git add cc/agents/serena-explorer.md
git commit -m "feat: add serena-explorer research agent"
```

### Task 6: Create context7-researcher agent

**Files:**
- Create: `cc/agents/context7-researcher.md`

**Step 1: Write agent file**

Create `cc/agents/context7-researcher.md`:

```markdown
---
name: context7-researcher
description: Library documentation specialist using Context7 MCP for official patterns and API best practices
tools: [Context7 MCP]
skill: using-context7-for-docs
model: sonnet
---

# Context7 Researcher Agent

You are a library documentation specialist. Use Context7 MCP tools to find official patterns, API documentation, and framework best practices.

Follow the `using-context7-for-docs` skill for best practices on:
- Resolving library IDs with resolve-library-id
- Fetching focused documentation with topic parameter
- Paginating when initial results insufficient
- Prioritizing high benchmark scores and reputation

Report findings with:
- Library name and Context7 ID
- Benchmark score and source reputation
- Relevant API patterns with code examples
- Official recommendations and best practices
- Version-specific guidance when applicable
```

**Step 2: Verify file created**

```bash
cat cc/agents/context7-researcher.md | head -20
```

Expected: Frontmatter and content visible

**Step 3: Commit**

```bash
git add cc/agents/context7-researcher.md
git commit -m "feat: add context7-researcher agent"
```

### Task 7: Create web-researcher agent

**Files:**
- Create: `cc/agents/web-researcher.md`

**Step 1: Write agent file**

Create `cc/agents/web-researcher.md`:

```markdown
---
name: web-researcher
description: Web search specialist for best practices, tutorials, and expert opinions
tools: [WebSearch, WebFetch]
skill: using-web-search
model: sonnet
---

# Web Researcher Agent

You are a web research specialist. Use WebSearch and WebFetch to find best practices, recent articles, expert opinions, and industry patterns.

Follow the `using-web-search` skill for best practices on:
- Crafting specific, current search queries
- Using domain filtering for trusted sources
- Fetching promising results for detailed analysis
- Assessing source authority and recency

Report findings with:
- Source citations (author, title, date, URL)
- Authority assessment (5-star rating with justification)
- Key recommendations with supporting quotes
- Code examples and benchmarks where available
- Trade-offs and context-specific advice
```

**Step 2: Verify file created**

```bash
cat cc/agents/web-researcher.md | head -20
```

Expected: Frontmatter and content visible

**Step 3: Commit**

```bash
git add cc/agents/web-researcher.md
git commit -m "feat: add web-researcher agent"
```

### Task 8: Create github-researcher agent

**Files:**
- Create: `cc/agents/github-researcher.md`

**Step 1: Write agent file**

Create `cc/agents/github-researcher.md`:

```markdown
---
name: github-researcher
description: GitHub issues, PRs, and discussions specialist for community solutions and known gotchas
tools: [WebSearch, WebFetch]
skill: using-github-search
model: sonnet
---

# GitHub Researcher Agent

You are a GitHub research specialist. Use WebSearch (with site:github.com) and WebFetch to find community solutions, known issues, and implementation patterns from GitHub repositories.

Follow the `using-github-search` skill for best practices on:
- Searching closed issues for solved problems
- Finding merged PRs for implementation examples
- Analyzing discussions for community consensus
- Extracting problem-solution patterns

Report findings with:
- Issue/PR/Discussion links and status
- Problem descriptions and root causes
- Solutions with code examples
- Community consensus and frequency
- Caveats, gotchas, and trade-offs mentioned
```

**Step 2: Verify file created**

```bash
cat cc/agents/github-researcher.md | head -20
```

Expected: Frontmatter and content visible

**Step 3: Commit**

```bash
git add cc/agents/github-researcher.md
git commit -m "feat: add github-researcher agent"
```

### Task 9: Create research-orchestration skill

**Files:**
- Create: `cc/skills/research-orchestration/SKILL.md`

**Step 1: Create skill directory**

```bash
mkdir -p cc/skills/research-orchestration
```

**Step 2: Write skill file**

Create `cc/skills/research-orchestration/SKILL.md`:

```markdown
# Research Orchestration

Use this skill to manage parallel research subagents and synthesize findings from multiple sources.

## When to Use

After brainstorming completes and user selects "B) research first" option.

## Selection Algorithm

### Default Selection

Based on brainstorm context, intelligently select researchers:

**serena-explorer** [✓ ALWAYS]
- Always need codebase understanding
- No keywords required - default ON

**context7-researcher** [✓ if library mentioned]
- Select if: new library, framework, official docs needed
- Keywords: "using [library]", "integrate [framework]", "best practices for [tool]"
- Example: "using React hooks" → ON

**web-researcher** [✓ if patterns mentioned]
- Select if: best practices, tutorials, modern approaches, expert opinions
- Keywords: "industry standard", "common pattern", "how to", "best approach"
- Example: "authentication best practices" → ON

**github-researcher** [☐ usually OFF]
- Select if: known issues, community solutions, similar features, troubleshooting
- Keywords: "GitHub issue", "others solved", "similar to [project]", "known problems"
- Example: "known issues with SSR" → ON

### User Presentation

Present recommendations with context:

```markdown
Based on the brainstorm, I recommend these researchers:

[✓] Codebase (serena-explorer)
    → Understand current architecture and integration points

[✓] Library docs (context7-researcher)
    → React hooks patterns and official recommendations

[✓] Web (web-researcher)
    → Authentication best practices and security patterns

[ ] GitHub (github-researcher)
    → Not needed unless we hit specific issues

Adjust selection? (Y/n)
```

If **Y**: Interactive toggle
```
Toggle researchers: (C)odebase (L)ibrary (W)eb (G)itHub (D)one
User input: L G D
Result: Toggled OFF context7-researcher, ON github-researcher, Done
```

If **n**: Use defaults and proceed

## Spawning Subagents

**Run up to 4 in parallel** using Task tool:

```typescript
// Spawn all selected researchers in parallel
const results = await Promise.all([
  // Always spawn serena-explorer
  Task({
    subagent_type: "serena-explorer",
    description: "Explore codebase architecture",
    prompt: `
      Analyze the current codebase for ${feature} implementation.

      Find:
      - Current architecture relevant to ${feature}
      - Similar existing implementations we can learn from
      - Integration points where ${feature} should hook in
      - Patterns used in similar features

      Provide all findings with file:line references.
    `
  }),

  // Conditionally spawn context7-researcher
  ...(useContext7 ? [Task({
    subagent_type: "context7-researcher",
    description: "Research library documentation",
    prompt: `
      Research official documentation for ${libraries}.

      Find:
      - Recommended patterns for ${useCase}
      - API best practices and examples
      - Security considerations
      - Performance recommendations

      Include Context7 IDs, benchmark scores, and code examples.
    `
  })] : []),

  // Conditionally spawn web-researcher
  ...(useWeb ? [Task({
    subagent_type: "web-researcher",
    description: "Research best practices",
    prompt: `
      Search for ${topic} best practices and expert opinions.

      Find:
      - Industry standard approaches for ${useCase}
      - Recent articles (2024-2025) on ${topic}
      - Expert recommendations with rationale
      - Common gotchas and solutions

      Cite sources with authority assessment and publication dates.
    `
  })] : []),

  // Conditionally spawn github-researcher
  ...(useGithub ? [Task({
    subagent_type: "github-researcher",
    description: "Research GitHub issues/PRs",
    prompt: `
      Search GitHub for ${topic} issues and solutions.

      Find:
      - Closed issues related to ${problem}
      - Merged PRs implementing ${feature}
      - Community discussions on ${topic}
      - Known gotchas and workarounds

      Focus on ${relevantRepos} repositories.
      Provide issue links, status, and consensus solutions.
    `
  })] : [])
])
```

**Key points:**
- All spawned in single Task call block (parallel execution)
- Each has specific prompt tailored to feature context
- Prompts reference brainstorm decisions
- Results returned when all complete

## Synthesis

After all subagents complete, synthesize findings:

### Structure

```markdown
# Research: ${feature-name}

## Brainstorm Summary

${brief-summary-of-brainstorm-decisions}

## Codebase Findings (serena-explorer)

### Current Architecture
- **${component}:** `${file}:${line}`
  - ${description}

### Similar Implementations
- **${existing-feature}:** `${file}:${line}`
  - ${pattern-used}
  - ${why-relevant}

### Integration Points
- **${location}:** `${file}:${line}`
  - ${how-to-hook-in}

## Library Documentation (context7-researcher)

### ${Library-Name}
**Context7 ID:** ${id}
**Benchmark Score:** ${score}

**Relevant APIs:**
- **${api-name}:** ${description}
  ```${lang}
  ${code-example}
  ```

**Best Practices:**
1. ${practice-1}
2. ${practice-2}

## Web Research (web-researcher)

### ${Topic}

**Source:** ${author} - "${title}" (${date})
**Authority:** ${stars} (${justification})
**URL:** ${url}

**Key Recommendations:**
1. **${recommendation}**
   > "${quote}"

   - ${implementation-detail}

**Trade-offs:**
- ${trade-off-1}
- ${trade-off-2}

## GitHub Research (github-researcher)

### ${Issue-Topic}

**Source:** ${repo}#${number} (${status})
**URL:** ${url}

**Problem:** ${description}

**Solution:**
```${lang}
${code-example}
```

**Caveats:**
- ${caveat-1}
- ${caveat-2}

## Synthesis

### Recommended Approach

Based on all research, recommend ${approach} because:

1. **Codebase fit:** ${how-it-fits-existing-patterns}
2. **Library support:** ${official-patterns-available}
3. **Industry proven:** ${expert-consensus}
4. **Community validated:** ${github-evidence}

### Key Decisions

- **${decision-1}:** ${rationale}
- **${decision-2}:** ${rationale}

### Risks & Mitigations

- **Risk:** ${risk}
  - **Mitigation:** ${mitigation}

## Next Steps

Ready to write implementation plan with this research context.
```

## Auto-Save

After synthesis completes, automatically save to memory:

```typescript
// Use state-persistence skill
await saveResearchMemory({
  feature: extractFeatureName(brainstorm),
  content: synthesizedResearch,
  type: "research"
})
```

**Filename:** `YYYY-MM-DD-${feature-name}-research.md`

**Location:** Serena MCP memory (via write_memory tool)

## Handoff

After save completes, report to user:

```markdown
Research complete and saved to memory: ${filename}

I've synthesized findings from ${count} sources:
- Codebase: ${summary-of-serena-findings}
- Library docs: ${summary-of-context7-findings}
- Web: ${summary-of-web-findings}
- GitHub: ${summary-of-github-findings}

Key recommendation: ${one-sentence-approach}

Ready to write the implementation plan with this research context.
```

Then invoke `writing-plans` skill automatically.

## Error Handling

**If subagent fails:**
1. Continue with other subagents
2. Note missing research in synthesis
3. Offer to re-run failed researcher

**If no results found:**
1. Note in synthesis
2. Don't block workflow
3. Proceed with available research

**If all subagents fail:**
1. Report failure
2. Offer to proceed without research
3. User can retry or continue to planning
```

**Step 3: Verify file created**

```bash
cat cc/skills/research-orchestration/SKILL.md | head -50
```

Expected: Skill content visible

**Step 4: Commit**

```bash
git add cc/skills/research-orchestration/
git commit -m "feat: add research-orchestration skill"
```

---

## Phase 3: Plan Review Infrastructure

### Task 10: Create plan-review agents

**Files:**
- Create: `cc/agents/completeness-checker.md`
- Create: `cc/agents/feasibility-analyzer.md`
- Create: `cc/agents/scope-creep-detector.md`
- Create: `cc/agents/quality-validator.md`

**Step 1: Write completeness-checker agent**

Create `cc/agents/completeness-checker.md`:

```markdown
---
name: completeness-checker
description: Plan completeness validator checking for success criteria, dependencies, rollback strategy, and edge cases
tools: [Read]
skill: null
model: haiku
---

# Completeness Checker Agent

You are a plan completeness specialist. Analyze implementation plans for missing phases, unclear success criteria, and unaddressed edge cases.

Check for:

1. **Success Criteria**
   - Every phase has automated verification steps
   - Manual verification described when automation not possible
   - Clear pass/fail criteria

2. **Dependencies**
   - Prerequisites identified between phases
   - Dependency order makes sense
   - Circular dependencies flagged

3. **Rollback Strategy**
   - How to undo changes if phase fails
   - Database migrations have down scripts
   - Feature flags or gradual rollout mentioned

4. **Edge Cases**
   - Error handling addressed
   - Boundary conditions considered
   - Concurrent access handled

5. **Testing Strategy**
   - Unit tests specified
   - Integration tests defined
   - Manual testing steps clear

Report findings as:

**Completeness: PASS / WARN / FAIL**

**Issues Found:**
- ❌ Phase 2 missing automated success criteria
- ⚠️ No rollback strategy for database migration
- ❌ Edge case: concurrent user updates not addressed

**Recommendations:**
- Add `make test-phase-2` verification command
- Create rollback migration script
- Add mutex or optimistic locking for concurrent updates
```

**Step 2: Write feasibility-analyzer agent**

Create `cc/agents/feasibility-analyzer.md`:

```markdown
---
name: feasibility-analyzer
description: Plan feasibility checker verifying prerequisites exist and assumptions are valid
tools: [Serena MCP, Read]
skill: using-serena-for-exploration
model: sonnet
---

# Feasibility Analyzer Agent

You are a plan feasibility specialist. Verify that plan assumptions are valid and prerequisites exist in the actual codebase.

Use Serena MCP tools to check:

1. **Prerequisites Exist**
   - Files/functions referenced actually exist
   - Libraries mentioned are in dependencies
   - Database tables/models are present

2. **Assumptions Valid**
   - Architecture matches plan's assumptions
   - Integration points are where plan expects
   - No conflicting implementations

3. **Technical Blockers**
   - No obvious impossibilities
   - Technology choices compatible
   - Performance implications reasonable

4. **Scope Reasonable**
   - Estimated effort matches complexity
   - Not too ambitious for timeframe
   - Dependencies available/stable

Process:
1. Extract all file paths, functions, libraries from plan
2. Use find_symbol, find_file to verify they exist
3. Check integration points with get_symbols_overview
4. Flag missing prerequisites or invalid assumptions

Report findings as:

**Feasibility: PASS / WARN / FAIL**

**Issues Found:**
- ❌ Plan assumes `src/auth/handler.py` exists - NOT FOUND
- ⚠️ Plan references `validateToken()` function - exists but signature different
- ❌ Plan requires `jsonwebtoken` library - not in package.json

**Recommendations:**
- Create auth handler or update plan to use existing: `src/security/auth.py:45`
- Update plan to match actual validateToken signature: `(token, options)`
- Add jsonwebtoken to dependencies: `npm install jsonwebtoken`
```

**Step 3: Write scope-creep-detector agent**

Create `cc/agents/scope-creep-detector.md`:

```markdown
---
name: scope-creep-detector
description: Scope validation specialist comparing plan against original brainstorm and research to catch feature creep
tools: [Read, Serena MCP read_memory]
skill: null
model: haiku
---

# Scope Creep Detector Agent

You are a scope validation specialist. Compare the plan against original brainstorm and research to identify scope creep, gold-plating, or over-engineering.

Check for:

1. **Scope Alignment**
   - All plan features were in brainstorm decisions
   - No new features added without justification
   - "What We're NOT Doing" section exists and is respected

2. **Gold-Plating**
   - Unnecessary abstraction layers
   - Premature optimization
   - Features beyond requirements

3. **Over-Engineering**
   - Overly complex solutions to simple problems
   - Framework/library overkill
   - Unnecessary configuration options

4. **Scope Expansion**
   - Features not in original scope
   - "While we're at it" additions
   - Future-proofing beyond needs

Process:
1. Read brainstorm context (from research.md memory or conversation)
2. Extract original decisions and "NOT doing" list
3. Compare plan features against original scope
4. Flag additions, expansions, over-engineering

Report findings as:

**Scope: PASS / WARN / FAIL**

**Issues Found:**
- ❌ Plan includes "admin dashboard" - NOT in original brainstorm (only "user dashboard")
- ⚠️ Plan adds role-based permissions - brainstorm said "simple auth only"
- ❌ Plan implements caching layer - brainstorm had no performance requirements

**Recommendations:**
- Remove admin dashboard or split into separate plan
- Simplify to basic authentication without roles
- Remove caching - add only if performance issues arise

**Original Scope (from brainstorm):**
- User authentication with JWT
- Login/logout functionality
- User dashboard to view profile
- NOT doing: admin features, roles, social auth
```

**Step 4: Write quality-validator agent**

Create `cc/agents/quality-validator.md`:

```markdown
---
name: quality-validator
description: Plan quality checker ensuring clear language, specific references, and measurable criteria
tools: [Read]
skill: null
model: haiku
---

# Quality Validator Agent

You are a plan quality specialist. Check for vague language, missing references, and untestable success criteria.

Check for:

1. **Clear Language**
   - No vague terms: "handle errors properly", "add validation"
   - Specific actions: "validate email format with regex", "return 400 on invalid input"
   - Concrete implementations, not abstractions

2. **Specific References**
   - File paths included: `src/auth/handler.py:123`
   - Line numbers when modifying existing code
   - Exact function/class names
   - Specific libraries with versions

3. **Measurable Criteria**
   - Success criteria are testable
   - Commands specified: `make test-auth`
   - Expected outputs defined
   - No "should work correctly" without verification

4. **Code Examples**
   - Complete, not pseudocode
   - Syntax-correct
   - Imports included
   - Context-appropriate

5. **Command Usage**
   - Prefer `make` targets over raw commands
   - Standard project commands used
   - Build/test commands match project conventions

Process:
1. Scan plan for vague language patterns
2. Check all code references have file:line
3. Verify success criteria are testable
4. Review code examples for completeness

Report findings as:

**Quality: PASS / WARN / FAIL**

**Issues Found:**
- ⚠️ Phase 1 says "add error handling" - not specific
- ❌ Phase 2 references "user controller" without file path
- ⚠️ Success criteria: "authentication works" - not measurable
- ❌ Code example missing imports

**Recommendations:**
- Change "add error handling" to: "Raise ValueError on invalid email format, return 400 HTTP response"
- Specify: `src/controllers/user_controller.py:67`
- Change success to: "Run `make test-auth` - all tests pass, can login with valid credentials and get 401 with invalid"
- Add imports to code example:
  ```python
  from flask import request, jsonify
  from auth import validate_token
  ```
```

**Step 5: Verify files created**

```bash
ls -la cc/agents/completeness-checker.md cc/agents/feasibility-analyzer.md cc/agents/scope-creep-detector.md cc/agents/quality-validator.md
```

Expected: All 4 files exist

**Step 6: Commit**

```bash
git add cc/agents/completeness-checker.md cc/agents/feasibility-analyzer.md cc/agents/scope-creep-detector.md cc/agents/quality-validator.md
git commit -m "feat: add plan review validator agents"
```

### Task 11: Create plan-review skill

**Files:**
- Create: `cc/skills/plan-review/SKILL.md`

**Step 1: Create skill directory**

```bash
mkdir -p cc/skills/plan-review
```

**Step 2: Write skill file**

Create `cc/skills/plan-review/SKILL.md`:

```markdown
# Plan Review

Use this skill to validate implementation plans across completeness, quality, feasibility, and scope dimensions.

## When to Use

After plan is written and user selects "A) review the plan" option.

## Phase 1: Initial Assessment

Run automatic checks across 4 dimensions using simple validation logic (no subagents yet):

### Completeness Check

Scan plan for:
- ✅ All phases have success criteria section
- ✅ Commands for verification present (`make test-`, `pytest`, etc.)
- ✅ Rollback/migration strategy mentioned
- ✅ Edge cases section or error handling
- ✅ Testing strategy defined

**Scoring:**
- PASS: All criteria present
- WARN: 1-2 criteria missing
- FAIL: 3+ criteria missing

### Quality Check

Scan plan for:
- ✅ File paths with line numbers: `file.py:123`
- ✅ Specific function/class names
- ✅ Code examples are complete (not pseudocode)
- ✅ Success criteria are measurable
- ❌ Vague language: "properly", "correctly", "handle", "add validation" without specifics

**Scoring:**
- PASS: File paths present, code complete, criteria measurable, no vague language
- WARN: Some file paths missing or minor vagueness
- FAIL: No file paths, pseudocode only, vague criteria

### Feasibility Check

Basic checks (detailed check needs subagent):
- ✅ References to existing files/functions seem reasonable
- ✅ No obvious impossibilities
- ✅ Technology choices are compatible
- ✅ Libraries mentioned are standard/available

**Scoring:**
- PASS: Seems feasible on surface
- WARN: Some questionable assumptions
- FAIL: Obvious blockers or impossibilities

### Scope Creep Check

Requires research.md memory or brainstorm context:
- ✅ "What We're NOT Doing" section exists
- ✅ Features align with original brainstorm
- ❌ New features added without justification
- ❌ Gold-plating or over-engineering patterns

**Scoring:**
- PASS: Scope aligned with original decisions
- WARN: Minor scope expansion, can justify
- FAIL: Significant scope creep or gold-plating

## Phase 2: Escalation (If Needed)

If **any dimension scores FAIL**, spawn specialized validators:

```typescript
const failedDimensions = {
  completeness: score === 'FAIL',
  quality: score === 'FAIL',
  feasibility: score === 'FAIL',
  scope: score === 'FAIL'
}

// Spawn validators in parallel for failed dimensions
const validations = await Promise.all([
  ...(failedDimensions.completeness ? [Task({
    subagent_type: "completeness-checker",
    description: "Validate plan completeness",
    prompt: `
      Analyze this implementation plan for completeness.

      Plan file: ${planPath}

      Check for:
      - Success criteria (automated + manual)
      - Dependencies between phases
      - Rollback/migration strategy
      - Edge cases and error handling
      - Testing strategy

      Report issues and recommendations.
    `
  })] : []),

  ...(failedDimensions.feasibility ? [Task({
    subagent_type: "feasibility-analyzer",
    description: "Verify plan feasibility",
    prompt: `
      Verify this implementation plan is feasible.

      Plan file: ${planPath}

      Use Serena MCP to check:
      - All referenced files/functions exist
      - Libraries are in dependencies
      - Integration points match reality
      - No technical blockers

      Report what doesn't exist or doesn't match assumptions.
    `
  })] : []),

  ...(failedDimensions.scope ? [Task({
    subagent_type: "scope-creep-detector",
    description: "Check scope alignment",
    prompt: `
      Compare plan against original brainstorm for scope creep.

      Plan file: ${planPath}
      Research/brainstorm: ${researchMemoryPath}

      Check for:
      - Features not in original scope
      - Gold-plating or over-engineering
      - "While we're at it" additions
      - Violations of "What We're NOT Doing"

      Report scope expansions and recommend removals.
    `
  })] : []),

  ...(failedDimensions.quality ? [Task({
    subagent_type: "quality-validator",
    description: "Validate plan quality",
    prompt: `
      Check this implementation plan for quality issues.

      Plan file: ${planPath}

      Check for:
      - Vague language vs. specific actions
      - Missing file:line references
      - Untestable success criteria
      - Incomplete code examples

      Report specific quality issues and improvements.
    `
  })] : [])
])
```

## Phase 3: Interactive Refinement

Present findings conversationally (like brainstorming skill):

```markdown
I've reviewed the plan. Here's what I found:

**Completeness: ${score}**
${if issues:}
- ${issue-1}
- ${issue-2}

**Quality: ${score}**
${if issues:}
- ${issue-1}
- ${issue-2}

**Feasibility: ${score}**
${if issues:}
- ${issue-1}
- ${issue-2}

**Scope: ${score}**
${if issues:}
- ${issue-1}
- ${issue-2}

${if any FAIL:}
Let's address these issues. Starting with ${most-critical-dimension}:

Q1: ${specific-question}
   A) ${option-1}
   B) ${option-2}
   C) ${option-3}
```

### Question Flow

Ask **one question at a time**, wait for answer, then next question.

For each issue:
1. Explain the problem clearly
2. Offer 2-4 concrete options
3. Allow "other" for custom response
4. Apply user's decision immediately
5. Update plan if changes agreed
6. Move to next issue

### Refinement Loop

After addressing all issues:
1. Update plan file with agreed changes
2. Re-run Phase 1 assessment
3. If still FAIL, spawn relevant validators again
4. Continue until all dimensions PASS or user approves WARN

### Approval

When all dimensions PASS or user accepts WARN:

```markdown
Plan review complete! ✅

**Final Scores:**
- Completeness: PASS
- Quality: PASS
- Feasibility: PASS
- Scope: PASS

The plan is ready for execution.
```

If user approved with WARN:

```markdown
Plan review complete with warnings.

**Final Scores:**
- Completeness: PASS
- Quality: WARN (minor file path gaps)
- Feasibility: PASS
- Scope: PASS

Warnings acknowledged. Proceeding with execution.
```

## Plan Updates

When making changes based on review:

1. Read current plan file
2. Apply specific edits using Edit tool
3. Preserve structure and formatting
4. Update only sections with issues
5. Verify changes with re-read

Don't rewrite entire plan - use targeted edits.

## Exit Conditions

**Success:** All PASS or user approves WARN
**Abort:** User requests to skip review and execute anyway
**Restart:** User requests major redesign (back to brainstorm)

## Example Session

```markdown
I've reviewed the plan. Here's what I found:

**Completeness: ⚠️ WARN**
- Phase 2 lacks automated success criteria

**Quality: ✅ PASS**

**Feasibility: ❌ FAIL**
- Plan assumes `src/auth/handler.py` exists - NOT FOUND

**Scope: ❌ FAIL**
- Plan includes "admin dashboard" but brainstorm only mentioned "user dashboard"

Let's address these issues. Starting with scope:

Q1: The plan includes an admin dashboard, but your brainstorm only mentioned a user dashboard. Should we:
   A) Remove admin dashboard (stick to original scope)
   B) Keep it (intentional expansion)
   C) Split admin dashboard into separate plan

User: A

Got it. I'll remove the admin dashboard from the plan.

[Updates plan, removes admin dashboard task]

Next, feasibility:

Q2: The plan references `src/auth/handler.py` but this file doesn't exist. I found `src/security/auth.py:45` with similar functionality. Should we:
   A) Create new `src/auth/handler.py` as planned
   B) Use existing `src/security/auth.py` instead
   C) Rename existing file to match plan

User: B

Makes sense. I'll update the plan to use `src/security/auth.py`.

[Updates plan with correct file paths]

Finally, completeness:

Q3: Phase 2 doesn't have automated success criteria. Should we add:
   A) `make test-auth` command to verify
   B) Specific pytest command
   C) Manual testing steps only

User: A

Perfect. I'll add `make test-auth` verification to Phase 2.

[Updates plan with verification command]

Re-checking plan with fixes...

**Final Scores:**
- Completeness: ✅ PASS
- Quality: ✅ PASS
- Feasibility: ✅ PASS
- Scope: ✅ PASS

Plan review complete! The plan is ready for execution.
```
```

**Step 3: Verify file created**

```bash
cat cc/skills/plan-review/SKILL.md | head -100
```

Expected: Skill content visible

**Step 4: Commit**

```bash
git add cc/skills/plan-review/
git commit -m "feat: add plan-review skill"
```

---

## Phase 4: State Persistence

### Task 12: Create state-persistence skill

**Files:**
- Create: `cc/skills/state-persistence/SKILL.md`

**Step 1: Create skill directory**

```bash
mkdir -p cc/skills/state-persistence
```

**Step 2: Write skill file**

Create `cc/skills/state-persistence/SKILL.md`:

```markdown
# State Persistence

Use this skill to save workflow state to Serena MCP memory at any stage and resume later.

## Memory File Format

**Naming:** `YYYY-MM-DD-<feature-name>-<stage>.md`

**Stages:**
- `research` - After research completes (automatic)
- `planning` - During plan writing (manual)
- `execution` - During/pausing execution (manual)
- `complete` - After workflow completion (automatic)

## Frontmatter Structure

All memory files include:

```yaml
---
date: 2025-11-20T15:30:00-08:00
git_commit: abc123def456
branch: feature/user-authentication
repository: crispy-claude
topic: "User Authentication Checkpoint"
tags: [checkpoint, authentication, jwt]
status: in-progress  # or: complete, blocked
last_updated: 2025-11-20
type: execution  # research, planning, execution, complete
---
```

## Automatic Saves

### After Research (automatic)

**Triggered by:** research-orchestration skill completion

**Filename:** `YYYY-MM-DD-<feature>-research.md`

**Content:**

```markdown
---
date: ${iso-timestamp}
git_commit: ${commit-hash}
branch: ${branch-name}
repository: crispy-claude
topic: "${Feature} Research"
tags: [checkpoint, research, ${feature-tags}]
status: complete
last_updated: ${date}
type: research
---

# Research: ${feature-name}

## Brainstorm Summary

${key-decisions-from-brainstorm}

## Codebase Findings (serena-explorer)

${serena-findings}

## Library Documentation (context7-researcher)

${context7-findings}

## Web Research (web-researcher)

${web-findings}

## GitHub Research (github-researcher)

${github-findings}

## Synthesis

${recommended-approach-and-decisions}

## Next Steps

Ready to write plan with research context.
```

### After Completion (automatic)

**Triggered by:** Workflow completion before PR creation

**Filename:** `YYYY-MM-DD-<feature>-complete.md`

**Content:**

```markdown
---
date: ${iso-timestamp}
git_commit: ${commit-hash}
branch: ${branch-name}
repository: crispy-claude
topic: "${Feature} Implementation Complete"
tags: [checkpoint, complete, ${feature-tags}]
status: complete
last_updated: ${date}
type: complete
---

# Implementation Complete: ${feature-name}

## What Was Built

${summary-of-implementation}

## Key Learnings

### Patterns Discovered
- ${pattern-1}: ${what-worked-well}
- ${pattern-2}: ${what-worked-well}

### Gotchas Encountered
- ${gotcha-1}: ${what-to-watch-for}
- ${gotcha-2}: ${what-to-watch-for}

### Trade-offs Made
- ${trade-off-1}: ${decision-and-reasoning}
- ${trade-off-2}: ${decision-and-reasoning}

## Codebase Updates

### Files Modified
- \`${file-1}:${lines}\`: ${major-change-description}
- \`${file-2}:${lines}\`: ${major-change-description}

### New Patterns Introduced
- ${pattern-1}: ${where-used}
- ${pattern-2}: ${where-used}

### Integration Points
- ${integration-1}: ${how-system-connects}
- ${integration-2}: ${how-system-connects}

## For Next Time

### What Worked
- ${approach-to-reuse}

### What Didn't
- ${avoid-in-future}

### Suggestions
- ${improvements-for-similar-tasks}

## PR Created

Link to PR: ${pr-url}
```

## Manual Saves

### During Planning (manual `/cc:save`)

**Filename:** `YYYY-MM-DD-<feature>-planning.md`

**Content:**

```markdown
---
date: ${iso-timestamp}
git_commit: ${commit-hash}
branch: ${branch-name}
repository: crispy-claude
topic: "${Feature} Planning"
tags: [checkpoint, planning, ${feature-tags}]
status: ${in-progress|blocked}
last_updated: ${date}
type: planning
---

# Planning: ${feature-name}

## Design Decisions

### Approach Chosen
${approach-with-rationale}

### Alternatives Considered
- ${alternative-1}: ${trade-offs}
- ${alternative-2}: ${trade-offs}

## Plan Draft

${current-plan-state-or-link-to-file}

## Open Questions

- ${question-1}
- ${question-2}

## Next Steps

${parse-plan-or-continue-planning}
```

### During Execution (manual `/cc:save`)

**Filename:** `YYYY-MM-DD-<feature>-execution.md`

**Content:**

```markdown
---
date: ${iso-timestamp}
git_commit: ${commit-hash}
branch: ${branch-name}
repository: crispy-claude
topic: "${Feature} Execution Checkpoint"
tags: [checkpoint, execution, ${feature-tags}]
status: ${in-progress|blocked}
last_updated: ${date}
type: execution
---

# Execution: ${feature-name}

## Plan Reference

- Plan file: \`docs/plans/${date}-${feature}.md\`
- Tasks directory: \`docs/plans/tasks/${date}-${feature}/\`
- Manifest: \`docs/plans/tasks/${date}-${feature}/manifest.json\`

## Progress Summary

- Total tasks: ${total}
- Completed: ${completed}
- In progress: ${in-progress}
- Remaining: ${remaining}

## Completed Tasks

- [✓] ${task-1}: ${summary-of-changes}
- [✓] ${task-2}: ${summary-of-changes}

## Current Task

- [ ] ${task-n}: ${current-state}

${if-blocked:}
**Blocker:** ${description-of-blocker}

## Blockers/Issues

${if-any-issues}
- ${issue-1}
- ${issue-2}

## Next Steps

Continue execution from task ${n}
```

## Stage Detection Algorithm

When `/cc:save` runs, detect stage automatically:

### Detection Rules

**Research stage** if:
- ✅ Brainstorm completed (conversation history has brainstorm skill invocation)
- ✅ Research subagents reported back (research-orchestration completed)
- ❌ No plan file in `docs/plans/YYYY-MM-DD-*.md`

**Planning stage** if:
- ✅ Plan file exists: `docs/plans/YYYY-MM-DD-*.md`
- ❌ No manifest.json in tasks directory
- ❌ No active TodoWrite tasks

**Execution stage** if:
- ✅ Plan exists AND (manifest.json exists OR TodoWrite has tasks)
- ✅ Uncommitted changes exist (`git status --short` has output)
- ❌ Not all tasks complete

**Complete stage** if:
- ✅ All tasks complete in TodoWrite (all status: completed)
- ✅ Execution finished

### Feature Name Extraction

```typescript
// Try plan filename first
const planFiles = glob('docs/plans/YYYY-MM-DD-*.md')
if (planFiles.length > 0) {
  // Extract from: docs/plans/2025-11-20-user-auth.md → user-auth
  featureName = planFiles[0].match(/\d{4}-\d{2}-\d{2}-(.+)\.md$/)[1]
}

// Fall back to brainstorm topic
if (!featureName) {
  // Extract from conversation history
  featureName = extractFromBrainstormTopic()
}

// Ask user if ambiguous
if (!featureName) {
  featureName = await askUser("Feature name for save file?")
}
```

### Metadata Collection

```bash
# Git commit hash
git rev-parse HEAD

# Current branch
git branch --show-current

# ISO timestamp
date -Iseconds

# Git status for changes
git status --short
```

### Ambiguity Handling

If detection unclear, ask user:

```markdown
Save checkpoint as:
A) Research (brainstorm + research complete, no plan yet)
B) Planning (plan in progress)
C) Execution (currently implementing tasks)
D) Complete (all tasks finished)

Current stage? (A/B/C/D)
```

## Saving Process

1. **Detect stage** using algorithm above
2. **Collect metadata** via git commands
3. **Generate content** based on stage type
4. **Write to Serena memory** using `write_memory` tool:

```typescript
await mcp__serena__write_memory({
  memory_file_name: `${date}-${feature}-${stage}.md`,
  content: `---\n${frontmatter}\n---\n\n${content}`
})
```

5. **Confirm to user:**

```markdown
Checkpoint saved: ${filename}

Stage: ${stage}
Status: ${status}
Branch: ${branch}

Resume later with: /cc:resume ${filename}
```

## Example Saves

### Research Save (automatic)

```bash
# After research completes
Saved: 2025-11-20-user-auth-research.md

Contains:
- Brainstorm summary
- Codebase findings from Serena
- React auth patterns from Context7
- Best practices from web research

Next: Ready to write plan
```

### Planning Save (manual)

```bash
User: /cc:save

# Detection
✓ Plan file exists: docs/plans/2025-11-20-user-auth.md
✗ No manifest.json
✗ No active tasks

→ Stage: planning

Saved: 2025-11-20-user-auth-planning.md

Contains:
- Design decisions made so far
- Alternatives considered
- Current plan draft
- Open questions

Resume with: /cc:resume 2025-11-20-user-auth-planning.md
```

### Execution Save (manual)

```bash
User: /cc:save

# Detection
✓ Plan exists
✓ Manifest exists
✓ TodoWrite: 3/5 tasks complete
✓ Uncommitted changes

→ Stage: execution

Saved: 2025-11-20-user-auth-execution.md

Contains:
- Progress: 3/5 tasks complete
- Completed: Task 1, 2, 3
- In progress: Task 4
- Remaining: Task 5

Resume with: /cc:resume 2025-11-20-user-auth-execution.md
```

### Complete Save (automatic)

```bash
# After all tasks complete, before PR
Saved: 2025-11-20-user-auth-complete.md

Contains:
- What was built
- Key learnings and gotchas
- Files modified with descriptions
- Patterns introduced
- Recommendations for next time

Next: Create PR
```

## Error Handling

**If write_memory fails:**
1. Log error details
2. Offer to retry
3. Suggest manual save (copy content to file)

**If metadata collection fails:**
1. Use defaults (unknown for git info)
2. Warn user about missing metadata
3. Proceed with save anyway

**If stage detection ambiguous:**
1. Present options to user
2. Let user choose stage explicitly
3. Add note in metadata about manual selection
```

**Step 3: Verify file created**

```bash
cat cc/skills/state-persistence/SKILL.md | head -100
```

Expected: Skill content visible

**Step 4: Commit**

```bash
git add cc/skills/state-persistence/
git commit -m "feat: add state-persistence skill"
```

---

## Phase 5: PR Creation

### Task 13: Create pr-creation skill

**Files:**
- Create: `cc/skills/pr-creation/SKILL.md`

**Step 1: Create skill directory**

```bash
mkdir -p cc/skills/pr-creation
```

**Step 2: Write skill file**

Create `cc/skills/pr-creation/SKILL.md`:

```markdown
# PR Creation

Use this skill to create pull requests with auto-generated descriptions from plan, execution context, and memory.

## Pre-flight Checks

Run these checks BEFORE generating PR description:

### 1. Branch Check

```bash
# Get current branch
branch=$(git branch --show-current)

# Check if on main/master
if [[ "$branch" == "main" || "$branch" == "master" ]]; then
  ERROR: Cannot create PR from main/master branch
  Must be on feature branch
  exit 1
fi
```

**Error message:**

```markdown
❌ Cannot create PR from main/master branch.

You're currently on: ${branch}

Create a feature branch first:
  git checkout -b feature/${feature-name}

Or if work is already done:
  git checkout -b feature/${feature-name}
  (commits stay with you)
```

### 2. Uncommitted Changes Check

```bash
# Check for uncommitted changes
git status --short

# If output exists
if [[ -n $(git status --short) ]]; then
  WARN: Uncommitted changes found
  Offer to commit before PR
fi
```

**Warning message:**

```markdown
⚠️ You have uncommitted changes:

${git status --short output}

Options:
A) Commit changes now
B) Stash and create PR anyway
C) Cancel PR creation

Choose: (A/B/C)
```

If **A**: Run commit process, then continue
If **B**: Stash changes, continue (warn they're not in PR)
If **C**: Exit PR creation

### 3. Remote Tracking Check

```bash
# Check if branch has remote
git rev-parse --abbrev-ref --symbolic-full-name @{u}

# If fails (no remote tracking)
if [[ $? -ne 0 ]]; then
  INFO: No remote tracking branch
  Will push with -u flag
fi
```

### 4. GitHub CLI Check

```bash
# Check gh installed
which gh

# Check gh authenticated
gh auth status
```

**Error if missing:**

```markdown
❌ GitHub CLI (gh) not found or not authenticated.

Install:
  macOS: brew install gh
  Linux: sudo apt install gh

Authenticate:
  gh auth login
```

## PR Description Generation

Auto-generate from multiple sources:

### Source Priority

1. **Plan file:** `docs/plans/YYYY-MM-DD-<feature>.md`
2. **Complete memory:** `YYYY-MM-DD-<feature>-complete.md` (if exists)
3. **Git diff:** For files changed summary
4. **Commit messages:** For timeline context

### Template Structure

```markdown
## Summary

${extract-from-plan-overview}

## Implementation Details

${synthesize-from-plan-phases-and-execution}

### What Changed

${git-diff-stat-summary}

### Key Files

- \`${file-1}\`: ${purpose-from-plan}
- \`${file-2}\`: ${purpose-from-plan}

### Approach

${extract-from-plan-architecture-or-approach}

## Testing

${extract-from-plan-testing-strategy}

### Verification

${if-complete-memory-exists:}
- ✅ All unit tests passing
- ✅ Integration tests passing
- ✅ Manual verification completed

${else:}
- [ ] Unit tests: \`${test-command}\`
- [ ] Integration tests: \`${test-command}\`
- [ ] Manual verification: ${steps}

## Key Learnings

${if-complete-memory-exists:}
${extract-learnings-section}

${if-patterns-discovered:}
### Patterns Discovered
- ${pattern-1}

${if-gotchas:}
### Gotchas Encountered
- ${gotcha-1}

## References

- Implementation plan: \`docs/plans/${plan-file}\`
${if-tasks-exist:}
- Tasks completed: \`docs/plans/tasks/${feature}/\`
${if-research-exists:}
- Research: \`${research-memory-file}\`

---

🔥 Generated with [CrispyClaude](https://github.com/seanGSISG/crispy-claude)
```

### Extraction Logic

**Summary (from plan):**
```typescript
// Read plan file
const plan = readFile(`docs/plans/${planFile}`)

// Extract content under ## Overview or ## Goal
const summary = extractSection(plan, ['Overview', 'Goal'])

// Take first 2-3 sentences
return summary.split('.').slice(0, 3).join('.') + '.'
```

**What Changed (from git):**
```bash
# Get diff stat
git diff --stat main...HEAD

# Get major files (top 5 by lines changed)
git diff --numstat main...HEAD | sort -k1 -rn | head -5
```

**Approach (from plan):**
```typescript
// Extract from plan sections
const approach = extractSection(plan, [
  'Architecture',
  'Approach',
  'Implementation Approach',
  'Technical Approach'
])
```

**Testing (from plan):**
```typescript
// Extract testing sections
const testing = extractSection(plan, [
  'Testing Strategy',
  'Testing',
  'Verification',
  'Test Plan'
])

// Include make commands found in plan
const testCommands = extractCommands(plan, ['make test', 'pytest', 'npm test'])
```

**Key Learnings (from complete.md):**
```typescript
// If complete memory exists
const complete = readMemory(`${feature}-complete.md`)

// Extract learnings section
const learnings = extractSection(complete, [
  'Key Learnings',
  'Patterns Discovered',
  'Gotchas Encountered',
  'Trade-offs Made'
])
```

## Push and Create PR

### Push Branch

```bash
# Check if remote tracking exists
remote_tracking=$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null)

if [[ -z "$remote_tracking" ]]; then
  # No remote tracking, push with -u
  git push -u origin $(git branch --show-current)
else
  # Remote tracking exists, regular push
  git push
fi
```

### Create PR with gh

```bash
# Create PR with generated description
gh pr create \
  --title "${PR_TITLE}" \
  --body "$(cat <<'EOF'
${GENERATED_DESCRIPTION}
EOF
)"
```

**PR Title Generation:**

```typescript
// Extract feature name from plan filename
// docs/plans/2025-11-20-user-authentication.md → "User Authentication"

const featureName = planFile
  .replace(/^\d{4}-\d{2}-\d{2}-/, '')  // Remove date
  .replace(/\.md$/, '')                 // Remove extension
  .replace(/-/g, ' ')                   // Hyphens to spaces
  .replace(/\b\w/g, c => c.toUpperCase()) // Title case

// PR title: "feat: ${featureName}"
const prTitle = `feat: ${featureName}`
```

### Success Output

```markdown
✅ Pull request created successfully!

**PR:** ${pr-url}
**Branch:** ${branch-name}
**Base:** main

**Description preview:**
${first-3-lines-of-description}

View PR: ${pr-url}
```

### Update Complete Memory

If complete.md exists, add PR link:

```typescript
// Read complete memory
const complete = readMemory(`${feature}-complete.md`)

// Add PR link section if not present
if (!complete.includes('## PR Created')) {
  const updated = complete + `\n\n## PR Created\n\nLink: ${prUrl}\nCreated: ${date}\n`

  // Write back to memory
  writeMemory(`${feature}-complete.md`, updated)
}
```

## Error Handling

**Push fails:**
```markdown
❌ Failed to push branch to remote.

Error: ${error-message}

Common fixes:
- Check remote is configured: \`git remote -v\`
- Check authentication: \`git remote set-url origin git@github.com:user/repo.git\`
- Force push if rebased: \`git push --force-with-lease\`
```

**gh pr create fails:**
```markdown
❌ Failed to create pull request.

Error: ${error-message}

Common fixes:
- Re-authenticate: \`gh auth login\`
- Check permissions: Need write access to repository
- Check branch already has PR: \`gh pr list --head ${branch}\`

Manual PR creation:
1. Go to: https://github.com/${owner}/${repo}/compare/${branch}
2. Click "Create pull request"
3. Use this description:

${generated-description}
```

**Missing sources:**
```markdown
⚠️ Could not find implementation plan.

Searched:
- docs/plans/${date}-*.md
- Memory files

Creating PR with basic description from git history.
You may want to edit the PR description manually.
```

## Example Session

```bash
User: /cc:pr

# Pre-flight checks
✓ On feature branch: feature/user-authentication
✓ No uncommitted changes
✓ GitHub CLI authenticated

# Generating PR description...

Found sources:
- Plan: docs/plans/2025-11-20-user-authentication.md
- Memory: 2025-11-20-user-authentication-complete.md
- Git diff: 8 files changed, 450 insertions, 120 deletions

# Creating pull request...

Pushing branch to origin...
✓ Pushed feature/user-authentication

Creating PR...
✓ PR created: https://github.com/user/repo/pull/42

─────────────────────────────────

✅ Pull request created successfully!

**PR:** https://github.com/user/repo/pull/42
**Branch:** feature/user-authentication
**Base:** main

**Title:** feat: User Authentication

**Description preview:**
## Summary
Implement JWT-based user authentication with login/logout functionality...

View full PR: https://github.com/user/repo/pull/42
```
```

**Step 3: Verify file created**

```bash
cat cc/skills/pr-creation/SKILL.md | head -100
```

Expected: Skill content visible

**Step 4: Commit**

```bash
git add cc/skills/pr-creation/
git commit -m "feat: add pr-creation skill"
```

---

## Phase 6: Commands

### Task 14: Create /cc:research command

**Files:**
- Create: `cc/commands/cc/research.md`

**Step 1: Ensure directory exists**

```bash
ls -la cc/commands/cc/
```

Expected: Directory exists (created in earlier tasks)

**Step 2: Write command file**

Create `cc/commands/cc/research.md`:

```markdown
Use the research-orchestration skill to spawn parallel research subagents and synthesize findings.

**Prerequisites:**
- Brainstorm completed
- Feature concept defined

**What this does:**
1. Analyzes brainstorm context
2. Suggests researchers (Codebase, Library docs, Web, GitHub)
3. Allows user to adjust selection
4. Spawns up to 4 subagents in parallel
5. Synthesizes findings
6. Automatically saves to \`YYYY-MM-DD-<feature>-research.md\`

**Next step:** Writing implementation plan with research context
```

**Step 3: Verify file created**

```bash
cat cc/commands/cc/research.md
```

Expected: Command content visible

**Step 4: Commit**

```bash
git add cc/commands/cc/research.md
git commit -m "feat: add /cc:research command"
```

### Task 15: Create /cc:parse-plan command

**Files:**
- Create: `cc/commands/cc/parse-plan.md`

**Step 1: Write command file**

Create `cc/commands/cc/parse-plan.md`:

```markdown
Use the decomposing-plans skill to break down a monolithic plan into parallel task files.

**Prerequisites:**
- Plan file exists: \`docs/plans/YYYY-MM-DD-<feature>.md\`
- Plan has 2+ tasks worth decomposing

**What this does:**
1. Reads the monolithic plan
2. Identifies parallelizable tasks
3. Creates task files in \`docs/plans/tasks/YYYY-MM-DD-<feature>/\`
4. Generates \`manifest.json\` with parallel batches
5. Prompts for next step: review or execute

**Output:**
- Task files: One per task
- Manifest: Defines batch execution order
- Enables parallel execution (up to 2 tasks per batch)

**Recommendation:** Always decompose plans with 4+ tasks for parallel execution.

**Next step:** Review plan or execute immediately
```

**Step 2: Verify file created**

```bash
cat cc/commands/cc/parse-plan.md
```

Expected: Command content visible

**Step 3: Commit**

```bash
git add cc/commands/cc/parse-plan.md
git commit -m "feat: add /cc:parse-plan command"
```

### Task 16: Create /cc:review-plan command

**Files:**
- Create: `cc/commands/cc/review-plan.md`

**Step 1: Write command file**

Create `cc/commands/cc/review-plan.md`:

```markdown
Use the plan-review skill to validate implementation plans for completeness, quality, feasibility, and scope.

**Prerequisites:**
- Plan file exists: \`docs/plans/YYYY-MM-DD-<feature>.md\`
- Optional: Plan decomposed (can review before or after)

**What this does:**

**Phase 1:** Initial assessment across 4 dimensions
- Completeness: Success criteria, rollback, edge cases
- Quality: File paths, specific references, measurable criteria
- Feasibility: Prerequisites exist, assumptions valid
- Scope: Aligned with brainstorm, no gold-plating

**Phase 2:** If any dimension fails, spawns specialized validators
- completeness-checker
- feasibility-analyzer (uses Serena to verify codebase)
- scope-creep-detector (compares to brainstorm/research)
- quality-validator

**Phase 3:** Interactive refinement
- Ask questions one at a time
- Offer concrete options
- Update plan with agreed changes
- Re-check until all pass or user approves warnings

**Exit:** Plan approved and ready for execution

**Next step:** Execute plan
```

**Step 2: Verify file created**

```bash
cat cc/commands/cc/review-plan.md
```

Expected: Command content visible

**Step 3: Commit**

```bash
git add cc/commands/cc/review-plan.md
git commit -m "feat: add /cc:review-plan command"
```

### Task 17: Create /cc:save command

**Files:**
- Create: `cc/commands/cc/save.md`

**Step 1: Write command file**

Create `cc/commands/cc/save.md`:

```markdown
Use the state-persistence skill to save workflow state to Serena MCP memory.

**Prerequisites:** At least one of:
- Brainstorm + research completed
- Plan file exists
- Execution in progress
- Execution complete

**What this does:**

**Stage Detection (automatic):**
- Analyzes current workflow state
- Determines stage: research, planning, execution, or complete
- Extracts feature name from plan or brainstorm
- Collects git metadata (commit, branch)

**Saves to:** \`YYYY-MM-DD-<feature-name>-<stage>.md\`

**Stage-specific content:**

**research.md** - After research completes
- Brainstorm summary
- Codebase findings (Serena)
- Library docs (Context7)
- Web research
- GitHub research

**planning.md** - During plan writing
- Design decisions
- Alternatives considered
- Plan draft
- Open questions

**execution.md** - During implementation
- Progress summary (X/Y tasks complete)
- Completed tasks
- Current task state
- Blockers/issues

**complete.md** - After workflow completion
- What was built
- Key learnings and gotchas
- Files modified
- Patterns introduced
- Recommendations

**Resume later with:** \`/cc:resume <filename>\`
```

**Step 2: Verify file created**

```bash
cat cc/commands/cc/save.md
```

Expected: Command content visible

**Step 3: Commit**

```bash
git add cc/commands/cc/save.md
git commit -m "feat: add /cc:save command"
```

### Task 18: Create /cc:resume command

**Files:**
- Create: `cc/commands/cc/resume.md`

**Step 1: Write command file**

Create `cc/commands/cc/resume.md`:

```markdown
Load saved workflow state from Serena MCP memory and continue from checkpoint.

**Usage:** \`/cc:resume <memory-file>\`

**Example:** \`/cc:resume 2025-11-20-user-auth-execution.md\`

**Prerequisites:**
- Valid memory file exists: \`YYYY-MM-DD-<feature>-<stage>.md\`
- Memory has required frontmatter metadata

**What this does:**

**Load & Parse:**
1. Read memory file from Serena MCP
2. Parse frontmatter (status, type, branch)
3. Load full content into conversation context

**Analyze Progress:**
- Based on type (research, planning, execution, complete)
- Check status (in-progress, complete, blocked)
- Determine what's done vs. remaining

**Present Assessment:**

\`\`\`
Loaded: ${filename}
Status: ${status}
Branch: ${branch}
Last updated: ${date}

${stage-specific-summary}

Next step in crispy workflow: ${recommended-next-step}

Options:
A) ${primary-next-action}
B) ${alternative-action}
C) ${another-alternative}
D) Skip to different workflow step
\`\`\`

**Stage-Specific Options:**

**From research.md:**
- A) Write plan with research context
- B) Re-run specific research subagent
- C) Do additional research

**From planning.md:**
- A) Continue writing plan
- B) Review draft with plan-review
- C) Start over with new brainstorm

**From execution.md:**
- A) Continue execution from current task
- B) Review completed work
- C) Adjust remaining tasks

**From complete.md:**
- A) Create PR
- B) Make additional changes
- C) Review implementation

**Flexible Continuation:**
- User can continue crispy workflow
- Or run any individual command
- Context fully restored
```

**Step 2: Verify file created**

```bash
cat cc/commands/cc/resume.md
```

Expected: Command content visible

**Step 3: Commit**

```bash
git add cc/commands/cc/resume.md
git commit -m "feat: add /cc:resume command"
```

### Task 19: Create /cc:pr command

**Files:**
- Create: `cc/commands/cc/pr.md`

**Step 1: Write command file**

Create `cc/commands/cc/pr.md`:

```markdown
Use the pr-creation skill to create a pull request with auto-generated description.

**Prerequisites:**
- On feature branch (NOT main/master)
- Execution completed
- Changes committed to branch
- \`gh\` CLI installed and authenticated

**What this does:**

**Pre-flight Checks:**
1. Verify on feature branch (error if main/master)
2. Check for uncommitted changes (offer to commit)
3. Verify remote tracking (set up if needed)
4. Check GitHub CLI installed and authenticated

**Generate PR Description from:**
- Plan file: \`docs/plans/YYYY-MM-DD-<feature>.md\`
- Complete memory: \`YYYY-MM-DD-<feature>-complete.md\` (if exists)
- Git diff: Files changed summary
- Commit messages: Timeline context

**Description Structure:**
- Summary (from plan overview)
- What Changed (git diff stat)
- Approach (from plan architecture)
- Testing (from plan + verification results)
- Key Learnings (from complete.md)
- References (plan, tasks, research)

**Execute:**
1. Push branch to remote
2. Create PR using \`gh pr create\`
3. Output PR URL
4. Update complete.md with PR link

**Title Format:** \`feat: ${Feature Name}\`

**Example:**
\`\`\`
✅ Pull request created successfully!

PR: https://github.com/user/repo/pull/42
Branch: feature/user-authentication
Base: main

View PR: https://github.com/user/repo/pull/42
\`\`\`
```

**Step 2: Verify file created**

```bash
cat cc/commands/cc/pr.md
```

Expected: Command content visible

**Step 3: Commit**

```bash
git add cc/commands/cc/pr.md
git commit -m "feat: add /cc:pr command"
```

### Task 20: Create /cc:crispy orchestrator command

**Files:**
- Create: `cc/commands/cc/crispy.md`

**Step 1: Write command file**

Create `cc/commands/cc/crispy.md`:

```markdown
Run the complete CrispyClaude workflow from ideation to PR creation.

**Prerequisites:** None (orchestrates entire workflow from start)

**Complete Workflow:**

## Step 1: Brainstorm

Invoke the \`brainstorming\` skill.

At completion, prompt:
\`\`\`
Ready to:
A) Write the plan
B) Research first

Choose: (A/B)
\`\`\`

## Step 2: Research (Optional)

If user selects **B**:
- Invoke \`research-orchestration\` skill
- Skill analyzes brainstorm and suggests researchers
- User can adjust selection (Codebase, Library docs, Web, GitHub)
- Spawns up to 4 subagents in parallel
- Synthesizes findings
- **Automatically saves:** \`YYYY-MM-DD-<feature>-research.md\`

## Step 3: Write Plan

Invoke \`writing-plans\` skill.
- Incorporates research findings if available
- Outputs plan to \`docs/plans/YYYY-MM-DD-<feature>.md\`

## Step 4: Parse Plan

Invoke \`decomposing-plans\` skill (ALWAYS decompose in crispy workflow).
- Creates task files in \`docs/plans/tasks/YYYY-MM-DD-<feature>/\`
- Generates manifest with parallel batches

At completion, prompt:
\`\`\`
Plan decomposed into X tasks across Y batches.

Ready to:
A) Review the plan
B) Execute immediately

Choose: (A/B)
\`\`\`

## Step 5: Review Plan (Optional)

If user selects **A**:
- Invoke \`plan-review\` skill
- Validates completeness, quality, feasibility, scope
- Interactive refinement until approved
- Updates plan if changes made

## Step 6: Execute Plan

Invoke \`parallel-subagent-driven-development\` skill.
- Executes tasks in parallel batches (up to 2 concurrent)
- Code review gate after each batch
- Handles failures with resilience mechanisms

## Step 7: Save Memory

Invoke \`state-persistence\` skill with \`type=complete\`.
- Captures implementation learnings, patterns, gotchas
- **Automatically saves:** \`YYYY-MM-DD-<feature>-complete.md\`

## Step 8: Create PR

Invoke \`pr-creation\` skill.
- Verifies on feature branch
- Generates PR description from plan, execution, memory
- Pushes branch to remote
- Creates PR with \`gh pr create\`
- Outputs PR URL

**Workflow Complete!** 🎉

---

**Throughout Workflow:**
- User can run \`/cc:save\` at any point to pause
- Creates stage-specific memory file
- Later run \`/cc:resume <file>\` to continue

**Approval Gates:**
- Step 2: Research? (optional)
- Step 5: Review? (optional)

**Automatic Saves:**
- After Step 2: \`-research.md\`
- After Step 7: \`-complete.md\`

**Manual Saves:**
- User can \`/cc:save\` during Steps 3, 6
- Creates \`-planning.md\` or \`-execution.md\`
```

**Step 2: Verify file created**

```bash
cat cc/commands/cc/crispy.md
```

Expected: Command content visible

**Step 3: Commit**

```bash
git add cc/commands/cc/crispy.md
git commit -m "feat: add /cc:crispy orchestrator command"
```

---

## Phase 7: Update Existing Skills

### Task 21: Update brainstorming skill

**Files:**
- Modify: `cc/skills/brainstorming/SKILL.md`

**Step 1: Read current skill**

```bash
cat cc/skills/brainstorming/SKILL.md | tail -50
```

Expected: See end of brainstorming skill

**Step 2: Add research prompt using Edit**

Add this section at the end of the "After the Design" section (before any final notes):

```markdown
### Next Steps

After design is complete, prompt user:

\`\`\`
Design complete! Ready to:
A) Write the plan
B) Research first (gather codebase insights, library docs, best practices)

Choose: (A/B)
\`\`\`

**If user chooses A:**
- Proceed directly to \`writing-plans\` skill

**If user chooses B:**
- Invoke \`research-orchestration\` skill
- Research skill will:
  - Analyze brainstorm context
  - Suggest researchers: \`[✓] Codebase [✓] Library docs [✓] Web [ ] GitHub\`
  - Allow user to adjust selection
  - Spawn selected subagents (max 4 in parallel)
  - Synthesize findings
  - Automatically save to \`YYYY-MM-DD-<feature>-research.md\`
  - Report: "Research complete. Ready to write the plan."
- Then proceed to \`writing-plans\` skill with research context
```

**Step 3: Locate insertion point**

```bash
grep -n "After the Design" cc/skills/brainstorming/SKILL.md
```

Expected: Find line number of "After the Design" section

**Step 4: Read section to find exact insertion point**

```bash
# Read the "After the Design" section
sed -n '/## After the Design/,/^## /p' cc/skills/brainstorming/SKILL.md
```

Expected: See the section content

**Step 5: Use Edit tool to add content**

Find the end of "After the Design" section and add the new "Next Steps" subsection there.

Note: This will require reading the full file first, then using Edit.

**Step 6: Read file to prepare for edit**

```bash
cat cc/skills/brainstorming/SKILL.md
```

**Step 7: Commit**

```bash
git add cc/skills/brainstorming/SKILL.md
git commit -m "feat: update brainstorming skill to prompt for research"
```

### Task 22: Update decomposing-plans skill

**Files:**
- Modify: `cc/skills/decomposing-plans/SKILL.md`

**Step 1: Read current skill**

```bash
cat cc/skills/decomposing-plans/SKILL.md | tail -50
```

Expected: See end of decomposing-plans skill

**Step 2: Add review prompt at the end**

Add this section at the very end of the skill file:

```markdown
## After Decomposition

After decomposition completes successfully, prompt user:

\`\`\`
Plan decomposed into X tasks across Y parallel batches.

Manifest: \`docs/plans/tasks/YYYY-MM-DD-<feature>/manifest.json\`
Tasks: \`docs/plans/tasks/YYYY-MM-DD-<feature>/<task-files>\`

Options:
A) Review the plan with plan-review
B) Execute immediately with parallel-subagent-driven-development
C) Save and exit (resume later with /cc:resume)

Choose: (A/B/C)
\`\`\`

**If user chooses A:**
- Invoke \`plan-review\` skill
- After review completes and plan approved
- Return to this prompt (offer B or C)

**If user chooses B:**
- Proceed directly to \`parallel-subagent-driven-development\` skill
- Begin executing tasks in parallel batches

**If user chooses C:**
- Invoke \`state-persistence\` skill to save execution checkpoint
- Save as \`YYYY-MM-DD-<feature>-execution.md\` with:
  - Plan reference and manifest location
  - Status: ready to execute, 0 tasks complete
  - Next step: Resume with \`/cc:resume\` and execute
- Exit workflow after save completes
```

**Step 3: Read file to prepare for edit**

```bash
cat cc/skills/decomposing-plans/SKILL.md
```

**Step 4: Commit**

```bash
git add cc/skills/decomposing-plans/SKILL.md
git commit -m "feat: update decomposing-plans to prompt for review or execute"
```

### Task 23: Update executing-plans skill

**Files:**
- Modify: `cc/skills/executing-plans/SKILL.md`

**Step 1: Read current skill**

```bash
head -100 cc/skills/executing-plans/SKILL.md
```

Expected: See beginning of executing-plans skill

**Step 2: Update execution strategy section**

Find the execution strategy section and update it to:

```markdown
## Execution Strategy

This skill checks for decomposition and chooses execution method:

### Detection

Check for manifest file before choosing execution:

\`\`\`bash
if [[ -f "docs/plans/tasks/YYYY-MM-DD-<feature>/manifest.json" ]]; then
  # Manifest exists → Use parallel execution
  EXECUTION_MODE="parallel"
else
  # No manifest → Use sequential execution
  EXECUTION_MODE="sequential"
fi
\`\`\`

### Parallel Execution (manifest exists)

**When:** \`manifest.json\` found in tasks directory

**Process:**
1. Load plan manifest from \`docs/plans/tasks/YYYY-MM-DD-<feature>/manifest.json\`
2. Invoke \`parallel-subagent-driven-development\` skill with manifest
3. Execute tasks in parallel batches (up to 2 concurrent subagents)
4. Code review gate after each batch
5. Continue until all tasks complete

**Benefits:**
- Up to 2 tasks run concurrently per batch
- ~40% faster for parallelizable plans
- 90% context reduction per task

### Sequential Execution (no manifest)

**When:** No \`manifest.json\` found

**Process:**
1. Load monolithic plan from \`docs/plans/YYYY-MM-DD-<feature>.md\`
2. Invoke \`subagent-driven-development\` skill
3. Execute tasks sequentially (one at a time)
4. Code review gate after each task
5. Continue until all tasks complete

**Use case:**
- Simple plans (1-3 tasks)
- Sequential work that can't parallelize
- Prefer simplicity over speed

### CRITICAL Constraint

⚠️ **Cannot use parallel-subagent-driven-development without manifest.json**

If manifest does not exist → MUST use sequential mode (subagent-driven-development)

### Recommendation

Always decompose plans with 4+ tasks to enable parallel execution.
Run \`/cc:parse-plan\` to create manifest before execution.
```

**Step 3: Read file to find execution strategy section**

```bash
grep -n "Execution Strategy" cc/skills/executing-plans/SKILL.md
```

**Step 4: Read file to prepare for edit**

```bash
cat cc/skills/executing-plans/SKILL.md
```

**Step 5: Commit**

```bash
git add cc/skills/executing-plans/SKILL.md
git commit -m "feat: update executing-plans to detect and use parallel/sequential"
```

### Task 24: Update writing-plans skill with execution guidance

**Files:**
- Modify: `cc/skills/writing-plans/SKILL.md`

**Step 1: Read end of current skill**

```bash
tail -50 cc/skills/writing-plans/SKILL.md
```

Expected: See "Execution Handoff" section

**Step 2: Update Execution Handoff section**

Replace the "Execution Handoff" section with:

```markdown
## Execution Handoff

After saving the plan, present execution options:

\`\`\`
Plan complete and saved to \`docs/plans/${filename}.md\`.

## Recommended Next Step: /cc:parse-plan

Decompose this plan into parallel task files. This enables:
- Up to 2 tasks executing concurrently per batch
- ~40% faster execution for parallelizable plans
- 90% context reduction per task

**Best for:** Plans with 4+ tasks

## Alternative: Execute Without Decomposition

Use sequential execution via subagent-driven-development.
- Best for simple plans (1-3 tasks)
- Simpler flow, no decomposition overhead
- One task at a time

## Important

Decomposition is **REQUIRED** for parallel execution.
Always decompose plans with 4+ tasks to enable parallel-subagent-driven-development.

---

Which approach?
A) Decompose plan (/cc:parse-plan) - Recommended
B) Execute sequentially without decomposition
C) Exit (run manually later)
\`\`\`

**If user chooses A:**
- Invoke \`decomposing-plans\` skill
- Proceed with decomposition workflow

**If user chooses B:**
- Invoke \`subagent-driven-development\` skill
- Execute tasks sequentially from monolithic plan

**If user chooses C:**
- Exit workflow
- User can run \`/cc:parse-plan\` or execution commands later
```

**Step 3: Read file to find Execution Handoff section**

```bash
grep -n "Execution Handoff" cc/skills/writing-plans/SKILL.md
```

**Step 4: Read file to prepare for edit**

```bash
cat cc/skills/writing-plans/SKILL.md
```

**Step 5: Commit**

```bash
git add cc/skills/writing-plans/SKILL.md
git commit -m "feat: update writing-plans to recommend decomposition"
```

---

## Success Criteria

- ✅ All new commands accessible via `/cc:*` pattern
- ✅ Research subagents can run in parallel (max 4 concurrent)
- ✅ Memory files follow naming convention with frontmatter metadata
- ✅ `/cc:resume` can restore context from any stage
- ✅ `/cc:review-plan` validates across 4 dimensions
- ✅ `/cc:pr` generates comprehensive descriptions
- ✅ `/cc:crispy` orchestrates full workflow with approval gates
- ✅ Existing skills integrate seamlessly with new workflow

## Testing Plan

**Manual verification after implementation:**

1. **Test research flow:**
   - Run `/cc:brainstorm` → Choose research → Verify subagents spawn
   - Check research.md memory created with correct format

2. **Test plan decomposition:**
   - Create plan with 4+ tasks
   - Run `/cc:parse-plan` → Verify manifest.json and task files

3. **Test plan review:**
   - Run `/cc:review-plan` on a plan
   - Verify validation runs and interactive refinement works

4. **Test save/resume:**
   - Run `/cc:save` at different stages
   - Verify correct memory file created
   - Run `/cc:resume <file>` → Verify context restored

5. **Test PR creation:**
   - Complete execution
   - Run `/cc:pr` → Verify PR created with generated description

6. **Test full orchestrator:**
   - Run `/cc:crispy` from start
   - Verify all steps execute in order
   - Verify approval gates work

7. **Test parallel execution:**
   - Decompose plan with parallel batches
   - Execute → Verify 2 tasks run concurrently
   - Verify code review gates between batches

## Notes

- All agent files use frontmatter metadata for configuration
- Research subagents are defined in `cc/agents/*.md`
- Skills provide detailed instructions for MCP tool usage
- State persistence uses Serena MCP `write_memory`/`read_memory`
- PR creation uses GitHub CLI (`gh`)
- Workflow supports both automatic and manual saves
- Decomposition is REQUIRED for parallel execution
