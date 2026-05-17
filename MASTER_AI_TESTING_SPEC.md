# 🧠 MASTER AI-TESTING SPECIFICATION
### Omni-Architect Protocol — Playwright AI-Augmented Testing Lifecycle

> **Document Class:** Source of Truth  
> **Version:** 1.0.0  
> **Governing Standard:** Omni-Architect Protocol v1  
> **Agents Governed:** PLANNER · GENERATOR · HEALER  
> **Status:** `[ ] Draft` `[ ] Approved` `[ ] Active`

---

> ## 🔒 IMMUTABLE HUMAN CONTRACT
>
> **The human does not edit this document. Ever.**
>
> This specification is written for, and maintained exclusively by, the AI agents it governs. The human's only permitted interactions with this document are:
>
> 1. **Answer questions** when an agent asks for information in chat.
> 2. **Say "approved"** or **"rejected"** at designated Human Gate checkpoints.
> 3. **Read** the document to understand what the agents are doing.
>
> All context gathering, all field population, all scenario writing, all code examples, and all document updates are performed by the agents. If the human finds themselves typing into this file, they must stop and instead tell the agent what they want in chat.
>
> Agents: treat any section of this document that contains unfilled placeholders as a signal that **you have not yet done your job**. Fill them by asking the human in chat, then update this document yourself.

---

## TABLE OF CONTENTS

1. [How to Start — First-Run Bootstrap Protocol](#0-how-to-start--first-run-bootstrap-protocol)
2. [Project Context & Environment](#1-project-context--environment)
3. [The 3-Stage Operational Lifecycle](#2-the-3-stage-operational-lifecycle)
   - [Stage 1: The Planner — Architectural Blueprint](#stage-1-the-planner--architectural-blueprint)
   - [Stage 2: The Generator — Tiered Implementation](#stage-2-the-generator--tiered-implementation)
   - [Stage 3: The Healer — Maintenance & Stability](#stage-3-the-healer--maintenance--stability)
4. [Core Technical Constraints](#3-core-technical-constraints)
   - [Strict POM Enforcement](#31-strict-pom-enforcement)
   - [Selector Hierarchy of Quality](#32-selector-hierarchy-of-quality)
   - [Anti-Hallucination Safeguards](#33-anti-hallucination-safeguards)
5. [Scenario Blueprinting Template](#4-scenario-blueprinting-template)
6. [Logic & Coverage Matrix](#5-logic--coverage-matrix)
7. [Code Quality Reference](#6-code-quality-reference)
8. [Healer Rules of Engagement](#7-healer-rules-of-engagement)
9. [Agent Prompt Templates](#8-agent-prompt-templates)
10. [Document Control](#appendix--document-control)

---

## 0. HOW TO START — FIRST-RUN BOOTSTRAP PROTOCOL

> **This section is addressed to the AI agent reading this document for the first time.**
> The human has done nothing except paste this spec into the conversation. Your job starts here.

When a human shares this document and says something like *"let's get started"*, *"set this up"*, or *"begin"*, execute the following bootstrap sequence in order, without skipping steps.

### Bootstrap Step 1 — Detect Document State

Read Section 1 of this document. If any fields read `AWAITING_PLANNER_INTAKE`, the project has not been onboarded yet. Proceed to Bootstrap Step 2.

If Section 1 is already populated, skip to Bootstrap Step 3.

### Bootstrap Step 2 — Conduct the Intake Interview

Tell the human:

> *"I'm the PLANNER. Before I can build your testing strategy, I need to understand your application. I'll ask you a short series of questions — just answer in plain language and I'll handle the rest."*

Then ask the following questions, **one group at a time** (wait for the answer before continuing):

**Group A — Application Identity**
1. What is the name of the application you want to test?
2. What type is it? (e.g., single-page app, server-rendered, mobile web)
3. What is the tech stack? (e.g., React, Next.js, Vue, plain HTML)
4. What is the repository URL, if any?
5. What version of Playwright, or should I assume the latest stable?

**Group B — Environments**
1. What URL should tests run against locally?
2. Do you have staging or CI environments? If so, their URLs?
3. What environment variable names will the tests need? (names only — no values in this document)

**Group C — Users & Roles**
1. What types of users exist? (e.g., Admin, Editor, Guest, Unauthenticated)
2. For each type: what can they do that others cannot?

**Group D — Application States**
1. What does a "clean" state look like before a test run?
2. Are there other important pre-conditions a test might start from?

**Group E — Coverage Scope**
1. What are the main features or user flows to test?
2. Are any flows explicitly out of scope right now?
3. Are there any known fragile areas of the UI?

### Bootstrap Step 3 — Populate Section 1

Once you have the answers, populate every field in Section 1 yourself. Do not ask the human to fill it in. After updating, summarize what you wrote and confirm accuracy with the human.

### Bootstrap Step 4 — Proceed to Stage 1

Once Section 1 is confirmed, say:

> *"Section 1 is complete. Moving into Stage 1 to produce the architectural blueprint. I'll present it for your approval before any code is generated."*

---

## 1. PROJECT CONTEXT & ENVIRONMENT

> **AGENT INSTRUCTION:** All fields in this section are populated by the PLANNER during Bootstrap. The human never types into this section. Any field reading `AWAITING_PLANNER_INTAKE` means Bootstrap has not been completed — stop and execute Section 0.

### 1.1 Application Under Test

| Field | Value |
|---|---|
| **Application Name** | `AWAITING_PLANNER_INTAKE` |
| **Application Type** | `AWAITING_PLANNER_INTAKE` |
| **Framework / Stack** | `AWAITING_PLANNER_INTAKE` |
| **Repository URL** | `AWAITING_PLANNER_INTAKE` |
| **Test Runner Version** | `AWAITING_PLANNER_INTAKE` |

### 1.2 Environment Configuration

| Environment | Base URL | Notes |
|---|---|---|
| **Local** | `AWAITING_PLANNER_INTAKE` | Developer machine |
| **Staging** | `AWAITING_PLANNER_INTAKE` | Pre-production parity |
| **CI** | `AWAITING_PLANNER_INTAKE` | Pipeline execution target |

```bash
# .env.test — Required Variable Names
# PLANNER populates this block with variable names gathered during intake.
# Values are never stored in this document — they are set by the team out-of-band.
# ─────────────────────────────────────────────────────────────────
# AWAITING_PLANNER_INTAKE
```

### 1.3 Application State Definitions

> **AGENT INSTRUCTION:** PLANNER defines state labels from Group D intake answers. Every STATE:: label used in Section 4 blueprints must be declared here first.

| State Label | Description | Setup Mechanism |
|---|---|---|
| `AWAITING_PLANNER_INTAKE` | PLANNER populates after Group D answers | PLANNER populates after intake |

### 1.4 User Roles & Permissions

> **AGENT INSTRUCTION:** PLANNER derives these from Group C intake answers. Every ROLE:: label used in Section 4 blueprints must be declared here first.

| Role Label | Permissions | Test Account (label only — no passwords in this document) |
|---|---|---|
| `AWAITING_PLANNER_INTAKE` | PLANNER populates after intake | PLANNER populates after intake |

---

## 2. THE 3-STAGE OPERATIONAL LIFECYCLE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    OMNI-ARCHITECT OPERATIONAL PIPELINE                      │
│                                                                             │
│  ┌──────────────┐    🔐 HUMAN GATE   ┌──────────────┐     🔐 HUMAN GATE    │
│  │  STAGE 1     │ ──────────────────► │  STAGE 2     │ ──────────────────►  │
│  │  PLANNER     │    Approve Plan     │  GENERATOR   │    Approve Tests     │
│  │  (Agent)     │                     │  A → B → C   │                      │
│  └──────────────┘                     │  (Agent)     │                      │
│                                       └──────────────┘                      │
│                                                                             │
│                                            │ Failing tests detected         │
│                                            ▼                                │
│                                       ┌──────────────┐                      │
│                                       │  STAGE 3     │                      │
│                                       │  HEALER      │                      │
│                                       │  (Agent)     │                      │
│                                       └──────────────┘                      │
└─────────────────────────────────────────────────────────────────────────────┘

  Human role: APPROVE or REJECT at gates only. No document editing. No code writing.
```

---

### STAGE 1: THE PLANNER — Architectural Blueprint

**Agent Identity:** PLANNER
**Objective:** Produce a complete architectural blueprint before a single line of code is written.
**Prerequisite:** Section 1 must be fully populated (Bootstrap complete).

#### Activation Conditions

- Section 0 Bootstrap is complete and Section 1 is fully populated.
- A new feature has been confirmed in scope by the human in chat.
- The human says "re-plan" or "update the architecture" in chat.

#### How the PLANNER Gathers Missing Information

The PLANNER never assumes. If information needed to complete a deliverable is absent from Section 1 or the conversation history, the PLANNER asks one targeted question in chat, waits for the answer, then continues. It does not leave `AWAITING_` values — it resolves them.

#### Mandatory Deliverables

The PLANNER produces all four artifacts below, writes them into this document, then requests Human Gate 1 review. No code is generated before approval.

---

##### Deliverable 1.A — Proposed Directory Tree

> **AGENT INSTRUCTION:** Replace the placeholder block below with the actual directory tree for this project. Derive page names from the features confirmed in Group E of intake. This is a proposal — the human approves or amends it via chat (not by editing this file).

```
AWAITING_PLANNER_GENERATION

PLANNER: Replace this entire block with the proposed directory tree.
Follow this canonical structure, adapting names to the application under test.

project-root/
├── playwright.config.ts
├── .env.test
├── pages/
│   ├── BasePage.ts
│   └── [one file per page identified during intake]
├── tests/
│   ├── unit/
│   ├── e2e/
│   │   └── [one subdirectory per feature area]
│   └── fixtures/
├── utils/
│   ├── testData.ts
│   ├── apiHelpers.ts
│   └── assertions.ts
└── reports/
```

---

##### Deliverable 1.B — File Naming Conventions

> These conventions are fixed by the protocol. The PLANNER confirms them; it does not alter them.

| Artifact | Convention | Example |
|---|---|---|
| POM Class File | `PascalCasePage.ts` | `CheckoutPage.ts` |
| E2E Test File | `feature-name.spec.ts` | `checkout-happy.spec.ts` |
| Unit Test File | `feature-name.unit.spec.ts` | `login.unit.spec.ts` |
| Fixture File | `context.fixture.ts` | `auth.fixture.ts` |
| Utility File | `camelCaseHelper.ts` | `apiHelpers.ts` |
| Test Data File | `camelCaseData.ts` | `checkoutData.ts` |

---

##### Deliverable 1.C — Scenario Inventory

> **AGENT INSTRUCTION:** PLANNER builds this from the features confirmed in Group E of intake. Every row becomes a future test. This must be a real, project-specific list — not a template. If scope is unclear, ask the human in chat before writing.

| Scenario ID | Feature Area | Type | Priority | Initial State | Assigned To (Step) |
|---|---|---|---|---|---|
| `AWAITING_PLANNER_GENERATION` | PLANNER fills | PLANNER fills | PLANNER fills | PLANNER fills | PLANNER fills |

---

##### Deliverable 1.D — Dependency & Risk Register

> **AGENT INSTRUCTION:** PLANNER identifies risks from intake answers (third-party integrations, known flaky flows, animation-heavy UIs, auth complexity). Every risk must have a concrete mitigation — not a placeholder.

| Dependency / Risk | Impact | Mitigation |
|---|---|---|
| `AWAITING_PLANNER_GENERATION` | PLANNER fills | PLANNER fills |

---

#### 🔐 HUMAN GATE 1 — PLANNER APPROVAL

> **HARD CONSTRAINT:** The GENERATOR cannot be invoked until the human says "approved" in chat. The PLANNER presents the four deliverables as a chat summary, then stops and waits.

The PLANNER says the following after presenting deliverables:

> *"That completes the Stage 1 architectural blueprint. Please review the four deliverables above. If anything needs to change, tell me in chat and I'll update the document. When you're satisfied, say 'approved' and I'll hand off to the GENERATOR."*

```
PLANNER SELF-VERIFICATION (must all be true before requesting Gate 1):

[ ] Section 1 has no fields reading AWAITING_PLANNER_INTAKE
[ ] Deliverable 1.A reflects the actual application's pages
[ ] Deliverable 1.C contains real scenario rows (not placeholder rows)
[ ] Deliverable 1.D contains real, project-specific risks
[ ] Zero lines of test code or POM code have been generated
[ ] Document Control (Appendix) has been updated with today's date

Gate 1 Status: AWAITING_HUMAN_APPROVAL
```

---

### STAGE 2: THE GENERATOR — Tiered Implementation

**Agent Identity:** GENERATOR
**Prerequisite:** Human Gate 1 must be recorded as approved in Document Control (Appendix) before this stage begins. The GENERATOR reads the Appendix to verify approval before writing any code.

The GENERATOR operates in three strictly sequential steps. Step N cannot begin until Step N-1 is complete and all completion criteria are met.

---

#### Step A — POM Foundation

**Goal:** Build all Page Object Model classes identified in Deliverable 1.A.

**How the GENERATOR uses this document:** Read Deliverable 1.A for the directory structure and Deliverable 1.C for required actions per page. Do not ask the human for information already in Section 1. If information is genuinely missing, ask once in chat, update Section 1, then proceed.

**Mandatory POM Structure:**

```typescript
// pages/ExamplePage.ts — CANONICAL POM TEMPLATE
// GENERATOR: Use this structure for every POM class.
// Replace names and locators with the real elements of the page being implemented.
import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class ExamplePage extends BasePage {

  // ── LOCATORS ──────────────────────────────────────────────────────────────
  // One private property per interactive element.
  // Ordered by the Selector Hierarchy of Quality (Section 3.2).
  // Raw selector strings never leave this class.

  private readonly primaryInput: Locator;
  private readonly submitButton: Locator;
  private readonly errorMessage: Locator;

  constructor(page: Page) {
    super(page);
    // Priority 1 — getByRole (always attempt first)
    this.submitButton  = page.getByRole('button', { name: 'Submit' });
    // Priority 2 — getByLabel (for labelled form fields)
    this.primaryInput  = page.getByLabel('Field label');
    // Priority 4 — getByText (for non-interactive visible text)
    this.errorMessage  = page.getByText('Error message text');
  }

  // ── ATOMIC ACTIONS ────────────────────────────────────────────────────────
  // One action per method. No assertions. Returns `this` for chaining.

  async fillPrimaryInput(value: string): Promise<this> {
    await this.primaryInput.fill(value);
    return this;
  }

  async clickSubmit(): Promise<void> {
    await this.submitButton.click();
  }

  // ── COMPOUND ACTIONS ──────────────────────────────────────────────────────
  // Combine atomics for DRY setup. Still no assertions.

  async submitForm(value: string): Promise<void> {
    await this.fillPrimaryInput(value);
    await this.clickSubmit();
  }

  // ── GETTERS ───────────────────────────────────────────────────────────────
  // Return locators so tests can assert against them.

  getErrorMessage(): Locator {
    return this.errorMessage;
  }
}
```

**Step A Completion Criteria:**

```
[ ] All POM classes from Deliverable 1.C are created
[ ] Every class extends BasePage
[ ] All locators adhere to the Selector Hierarchy of Quality (Section 3.2)
[ ] No assertions (expect()) inside any POM file
[ ] No raw selectors exist outside /pages/ directory
[ ] TypeScript compiles clean: npx tsc --noEmit
```

---

#### Step B — Inner-Unit Validation

**Goal:** Verify every POM method works in isolation before composing flows.

**Mandatory Unit Test Structure:**

```typescript
// tests/unit/example.unit.spec.ts — CANONICAL UNIT TEST TEMPLATE
// GENERATOR: One describe block per POM class. One test per action method.
// Validate that the action executes. No business outcomes. No E2E flows.
import { test, expect } from '@playwright/test';
import { ExamplePage } from '../../pages/ExamplePage';

test.describe('ExamplePage — POM Method Isolation', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/example-route');
  });

  test('fillPrimaryInput() — writes value into the target field', async ({ page }) => {
    const examplePage = new ExamplePage(page);
    await examplePage.fillPrimaryInput('test value');
    await expect(page.getByLabel('Field label')).toHaveValue('test value');
  });

  test('clickSubmit() — button is enabled and interaction is accepted', async ({ page }) => {
    const examplePage = new ExamplePage(page);
    await expect(page.getByRole('button', { name: 'Submit' })).toBeEnabled();
    await examplePage.clickSubmit();
    await expect(page).not.toHaveURL('/example-route');
  });

});
```

**Step B Completion Criteria:**

```
[ ] Every POM action method has a corresponding unit test
[ ] All unit tests pass: npx playwright test tests/unit/
[ ] Zero flakiness across 3 consecutive local runs
[ ] No compound business flows in any unit test file
```

---

#### Step C — Full Flow Integration

**Goal:** Compose POM methods into complete E2E scenarios from Deliverable 1.C.

**Prerequisite:** All Step B completion criteria must be checked before Step C begins.

**Mandatory E2E Test Structure:**

```typescript
// tests/e2e/[feature]/[scenario].spec.ts — CANONICAL E2E TEST TEMPLATE
// GENERATOR: Every test maps to one row in Deliverable 1.C.
// No raw selectors anywhere in this file. All actions via POM methods.
import { test, expect } from '@playwright/test';
import { ExamplePage } from '../../../pages/ExamplePage';
import { TEST_USERS } from '../../../utils/testData';

// Scenario ID: [FROM DELIVERABLE 1.C]
// Initial State: [STATE LABEL FROM SECTION 1.3]

test.describe('[SCN-ID] | [Feature Area] — [Scenario Type]', () => {

  test.beforeEach(async ({ page }) => {
    // Establish initial state. No test relies on a prior test's side effects.
    await page.goto('/route');
  });

  test('[plain-English description of what success looks like]', async ({ page }) => {
    // ARRANGE
    const examplePage = new ExamplePage(page);

    // ACT — POM methods only. Zero raw selectors.
    await examplePage.submitForm(TEST_USERS.admin.email);

    // ASSERT — Auto-waiting assertions only. No hard waits.
    await expect(page).toHaveURL('/expected-route');
    await expect(examplePage.getErrorMessage()).not.toBeVisible();
  });

});
```

**Step C Completion Criteria:**

```
[ ] All Scenario Inventory rows are implemented
[ ] All E2E tests pass: npx playwright test tests/e2e/
[ ] HTML report reviewed and linked in Document Control
[ ] Run is reproducible in CI
[ ] Selector audit: grep -r "css=\|xpath=\|page\.locator(" tests/ returns 0 results
```

---

### STAGE 3: THE HEALER — Maintenance & Stability

**Agent Identity:** HEALER
**Trigger:** One or more tests are failing. The human reports this in chat or pastes error output.

**How the HEALER is invoked:** The human pastes failing test output into chat. The HEALER reads this document, reads the error, and begins the Rules of Engagement checklist (Section 7) before proposing any fix. The human never edits the document.

#### HEALER Operational Constraints

| Constraint | Rule |
|---|---|
| **Selector Strategy** | `FORBIDDEN` — Cannot introduce any selector strategy not already in the codebase. |
| **Folder Structure** | `FORBIDDEN` — Cannot create directories, rename files, or relocate tests. |
| **New POM Methods** | `PERMITTED` — May add methods to existing POM classes if genuinely needed. |
| **POM Locator Updates** | `PERMITTED` — May update locator definitions within existing POM classes. |
| **Test Logic Updates** | `PERMITTED` — May update assertions or action sequences for intentional app changes. |
| **Hard Waits** | `FORBIDDEN` — `waitForTimeout()` is never the fix. |
| **New Utility Files** | `RESTRICTED` — Requires explicit human approval in chat before creating files in `/utils/`. |
| **Document Updates** | `REQUIRED` — Must update affected Scenario Blueprint rows if Success Criteria or Action Steps change. |

---

## 3. CORE TECHNICAL CONSTRAINTS

> Non-negotiable. Applies to all agents at all times. No agent may seek an exception without explicit human approval recorded in Document Control.

### 3.1 Strict POM Enforcement

```
┌─────────────────────────────────────────────┐   ┌─────────────────────────────────────────┐
│           TEST FILES (.spec.ts)              │   │        POM FILES (pages/*.ts)           │
│                                             │   │                                         │
│  ✅ Business flows (Arrange / Act / Assert) │   │  ✅ Locator definitions                 │
│  ✅ POM method calls only                   │   │  ✅ Atomic action methods               │
│  ✅ expect() on POM getters                 │   │  ✅ Compound actions (no assertions)    │
│  ✅ TEST_DATA references from testData.ts   │   │  ✅ Getter methods (return Locator)     │
│                                             │   │                                         │
│  ❌ page.locator() of any kind              │   │  ❌ expect() assertions                 │
│  ❌ CSS selectors / XPath strings           │   │  ❌ Business logic or branching         │
│  ❌ Hard-coded strings (emails, URLs, names)│   │  ❌ Test data                           │
│  ❌ waitForTimeout()                        │   │  ❌ waitForTimeout()                    │
└─────────────────────────────────────────────┘   └─────────────────────────────────────────┘
```

**CI Enforcement (run before every merge — all must return zero results):**

```bash
grep -rn "page\.locator\|css=\|xpath=" tests/
grep -rn "expect(" pages/
grep -rn "waitForTimeout" .
```

---

### 3.2 Selector Hierarchy of Quality

Agents must resolve locators in this exact priority order. A lower-priority strategy may only be used if all higher-priority strategies are genuinely inapplicable. Justification is required in a code comment when skipping a level.

| Priority | Strategy | When to Use |
|:---:|---|---|
| **1** | `page.getByRole(role, { name })` | Element has a semantic ARIA role. Always attempt first. |
| **2** | `page.getByLabel(text)` | Form field with an associated `<label>`. |
| **3** | `page.getByPlaceholder(text)` | Input with `placeholder` and no visible label. |
| **4** | `page.getByText(text)` | Non-interactive element identified by stable visible text. |
| **5** | `page.getByAltText(text)` | `<img>` or element with `alt` attribute. |
| **6** | `page.getByTitle(text)` | Element with `title` attribute. |
| **7** | `page.getByTestId(id)` | Last resort. No semantic identity exists. Agent must flag to human before using. Requires `data-testid` in DOM. |

**Prohibited — agents must never write these:**

```typescript
page.locator('.btn-primary')                          // ❌ CSS class
page.locator('#submit-form > div:nth-child(2)')       // ❌ CSS structural
page.locator('xpath=//button[@type="submit"]')        // ❌ XPath
page.locator('[data-cy="login-button"]')              // ❌ Non-standard attribute
page.locator('[type="submit"]')                       // ❌ Attribute selector
```

---

### 3.3 Anti-Hallucination Safeguards

| Rule | Prohibited Pattern | Required Pattern |
|---|---|---|
| **No Hard Waits** | `await page.waitForTimeout(3000)` | `await expect(locator).toBeVisible()` |
| **No Magic Strings** | `'admin@example.com'` inline in test | `TEST_USERS.admin.email` from `testData.ts` |
| **No Over-Engineering** | Nested loops, complex retry logic in tests | Flat, readable, sequential action steps |
| **No Assertion in POM** | `expect(this.button).toBeVisible()` in POM | Return the locator; assert in the test |
| **No Implicit State** | Tests that depend on a prior test having run | Every test has its own `beforeEach` |
| **No Interdependence** | `test.only` left in committed code | Every test independently runnable |

---

## 4. SCENARIO BLUEPRINTING TEMPLATE

> **AGENT INSTRUCTION:** The PLANNER creates one instance of this blueprint for every row in Deliverable 1.C. The GENERATOR references blueprints when generating Step C tests. The HEALER updates them when a fix changes Success Criteria or Action Steps. The human never fills in this section.

---

### Scenario Blueprint — `[PLANNER ASSIGNS SCN-ID]`

> **PLANNER:** Duplicate this section for each scenario in the Inventory. Replace all values. Delete this instruction block when the blueprint is complete.

#### Header

| Field | Value |
|---|---|
| **Scenario ID** | `AWAITING_PLANNER_GENERATION` |
| **Feature Area** | `AWAITING_PLANNER_GENERATION` |
| **Test Type** | `AWAITING_PLANNER_GENERATION` |
| **Priority** | `AWAITING_PLANNER_GENERATION` |
| **Covered By** | `AWAITING_PLANNER_GENERATION` |
| **Output File** | `AWAITING_PLANNER_GENERATION` |

#### State & Context

| Field | Value |
|---|---|
| **Initial State** | `AWAITING_PLANNER_GENERATION` |
| **User Role** | `AWAITING_PLANNER_GENERATION` |
| **Prerequisites** | `AWAITING_PLANNER_GENERATION` |

#### Action Steps

> PLANNER: One atomic action per row. No compound instructions. The GENERATOR translates each row into a POM method call.

| Step # | Actor | Action | Target (Semantic Description) |
|:---:|---|---|---|
| 1 | `PLANNER fills` | `PLANNER fills` | `PLANNER fills` |

#### Success Criteria

> PLANNER: Each row must map to a specific Playwright assertion. Vague outcomes are not acceptable.

| # | Playwright Method | Target | Expected Value |
|:---:|---|---|---|
| A1 | `PLANNER fills` | `PLANNER fills` | `PLANNER fills` |

#### Negative Outcomes (Negative / Edge Case tests only)

| Trigger | Expected System Response | Playwright Assertion |
|---|---|---|
| `PLANNER fills if applicable` | `PLANNER fills if applicable` | `PLANNER fills if applicable` |

---

## 5. LOGIC & COVERAGE MATRIX

> **AGENT INSTRUCTION:** PLANNER populates this section during Stage 1 from features identified in intake. The human never adds rows to these tables.

### 5.1 Boundary Value Analysis

> PLANNER: For every numeric, string-length, or date input identified, define the boundary test cases.

| Input Field | Min Valid | Min-1 (Invalid) | Max Valid | Max+1 (Invalid) | Notes |
|---|---|---|---|---|---|
| `AWAITING_PLANNER_GENERATION` | PLANNER fills | PLANNER fills | PLANNER fills | PLANNER fills | PLANNER fills |

### 5.2 Logic Predicates

> PLANNER: For features with conditional logic, enumerate all condition combinations requiring coverage.

| Condition 1 | Condition 2 | Condition 3 | Expected Outcome | Scenario ID |
|---|---|---|---|---|
| `AWAITING_PLANNER_GENERATION` | PLANNER fills | PLANNER fills | PLANNER fills | PLANNER fills |

### 5.3 RACC Coverage Checklist

> GENERATOR completes this after Step C by pointing to specific test files for each item.

```
[ ] R — Response Coverage:    At least one test per distinct system response
[ ] A — Action Coverage:      Every user action has a corresponding unit test (Step B)
[ ] C — Condition Coverage:   Every condition branch has a true AND false test
[ ] C — Combination Coverage: Critical condition combinations appear in Section 5.2

GENERATOR: After Step C, record which test files satisfy each coverage item.
The human does not fill this in.
```

---

## 6. CODE QUALITY REFERENCE

> Permanent reference. Set by the protocol. Never modified by agents or humans.

### ❌ Bad Test — What to Avoid

```typescript
// VIOLATION: This pattern is prohibited under the Omni-Architect Protocol.
// All agents must recognize and refuse to reproduce this structure.

import { test, expect } from '@playwright/test';

test('login test', async ({ page }) => {
  await page.goto('http://localhost:3000/login');    // ❌ Hardcoded URL

  await page.locator('#email-input').fill('admin@example.com'); // ❌ CSS + magic string

  await page.locator('xpath=//button[@class="btn btn-primary"]').click(); // ❌ XPath

  await page.waitForTimeout(3000);                  // ❌ Hard wait

  const banner = await page.locator('.welcome-msg').textContent(); // ❌ No auto-wait
  expect(banner).toContain('Welcome');
});

// VIOLATIONS:
// 1. Hardcoded URL — breaks across environments
// 2. CSS/XPath selectors — coupled to DOM implementation
// 3. Magic string email — breaks when test data changes
// 4. waitForTimeout — non-deterministic, masks real bugs
// 5. No POM — test owns both locators AND business logic
// 6. textContent() + expect() — no auto-waiting, will fail on slow renders
```

### ✅ Good Test — The Required Standard

```typescript
// COMPLIANT: This is the exact structure all generated tests must follow.

import { test, expect } from '@playwright/test';
import { LoginPage } from '../../../pages/LoginPage';
import { DashboardPage } from '../../../pages/DashboardPage';
import { TEST_USERS } from '../../../utils/testData';

test.describe('SCN-001 | Authentication — Admin Happy Path', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/login');                          // ✅ Relative URL from config
  });

  test('admin can log in with valid credentials and reach the dashboard', async ({ page }) => {
    const loginPage     = new LoginPage(page);          // ✅ POM instantiation
    const dashboardPage = new DashboardPage(page);

    await loginPage.login(                              // ✅ POM compound action
      TEST_USERS.admin.email,                           // ✅ Centralised test data
      TEST_USERS.admin.password
    );

    await expect(page).toHaveURL('/dashboard');                        // ✅ Auto-wait
    await expect(dashboardPage.getWelcomeBanner()).toBeVisible();      // ✅ Auto-wait
    await expect(dashboardPage.getWelcomeBanner())
      .toContainText(TEST_USERS.admin.displayName);                    // ✅ Auto-wait
  });

});
```

```typescript
// COMPLIANT POM — The class that powers the test above.

import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class LoginPage extends BasePage {
  private readonly emailInput:    Locator;  // Priority 2: getByLabel
  private readonly passwordInput: Locator;  // Priority 2: getByLabel
  private readonly submitButton:  Locator;  // Priority 1: getByRole

  constructor(page: Page) {
    super(page);
    this.emailInput    = page.getByLabel('Email address');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton  = page.getByRole('button', { name: 'Sign in' });
  }

  async fillEmail(email: string): Promise<this> {
    await this.emailInput.fill(email);
    return this;
  }

  async fillPassword(password: string): Promise<this> {
    await this.passwordInput.fill(password);
    return this;
  }

  async clickSubmit(): Promise<void> {
    await this.submitButton.click();
  }

  async login(email: string, password: string): Promise<void> { // ✅ No assertions
    await this.fillEmail(email);
    await this.fillPassword(password);
    await this.clickSubmit();
  }
}
```

---

## 7. HEALER RULES OF ENGAGEMENT

> **AGENT INSTRUCTION:** The HEALER completes this checklist in chat before proposing any fix. The document is only updated after a fix is confirmed and applied.

### Pre-Fix Investigation Checklist

```
PHASE 1 — ROOT CAUSE IDENTIFICATION
────────────────────────────────────────────────────────────────────────────────
[ ] 1. I have read the full failure output including stack trace and screenshot.

[ ] 2. I have classified the failure into exactly one category:
        [ ] Selector failure    (element not found or ambiguous)
        [ ] Timing failure      (element not ready at point of interaction)
        [ ] Assertion failure   (value mismatch — intentional app change?)
        [ ] Navigation failure  (URL or route has changed)
        [ ] Data failure        (test data is stale, missing, or changed format)

[ ] 3. For SELECTOR failures:
        Have I consulted the Selector Hierarchy of Quality (Section 3.2)?
        Have I run the Playwright Inspector to confirm the element's ARIA role?
        Command: npx playwright codegen --target=playwright-test <URL>

[ ] 4. For TIMING failures:
        Is there a waitForTimeout() in the call chain? If so — remove it.
        What is the correct auto-waiting assertion to use instead?

[ ] 5. For ASSERTION failures:
        Did the application change intentionally or is this a regression?
        If intentional: I will update the Scenario Blueprint AND the test.
        If regression: I will fix the code and document the root cause.

PHASE 2 — FIX SCOPE VALIDATION
────────────────────────────────────────────────────────────────────────────────
[ ] 6. My fix does NOT introduce a selector strategy absent from the codebase.

[ ] 7. My fix does NOT modify folder structure or relocate any file.

[ ] 8. My fix does NOT add waitForTimeout() anywhere.

[ ] 9. If I am updating a POM locator, the new locator adheres to the Selector
        Hierarchy (Priority 1 first; justify in a comment if skipping a level).

[ ] 10. If I need getByTestId(), I have flagged to the human in chat that a
         data-testid attribute must be added to the DOM, and I have NOT written
         the selector until the human confirms the attribute is in place.

[ ] 11. My fix touches the minimum number of files. No unrelated refactoring.

[ ] 12. The fix passes: npx playwright test <failing-spec>
         verified across 3 consecutive runs with zero flakiness.

PHASE 3 — DOCUMENTATION
────────────────────────────────────────────────────────────────────────────────
[ ] 13. I have added an inline comment to any changed locator explaining WHY.
         Example: // Updated: button role changed from 'button' to 'link' in v2.3

[ ] 14. If Success Criteria or Action Steps changed, I have updated the
         corresponding Scenario Blueprint in Section 4.

[ ] 15. I have added a row to the Document Control Change Log (Appendix).

HEALER FIX SUMMARY — Present this in chat before submitting any code change:
────────────────────────────────────────────────────────────────────────────────
  Scenario ID(s) affected:   _______________
  Root cause category:       _______________
  Files modified:            _______________
  Selector strategy used:    _______________
  Checklist items escalated: _______________
  Explanation:
  ___________________________________________________________________________
```

---

## 8. AGENT PROMPT TEMPLATES

> **AGENT INSTRUCTION:** These prompts are self-referential. When handing off between agents, the current agent fills all context from the populated fields in this document — no bracketed values should remain unresolved when a prompt is sent. If a value cannot be resolved from this document, ask the human in chat first, update the document, then send the prompt.

---

### Prompt — Invoke PLANNER

```
You are the PLANNER agent operating under the Omni-Architect Protocol.

Your context is the Master AI-Testing Specification in this conversation.
Section 1 has been populated via the Bootstrap Protocol.

Your task is to produce the four Stage 1 deliverables and write them
directly into the specification document:

  1. Proposed Directory Tree      → Deliverable 1.A
  2. File Naming Conventions      → Deliverable 1.B (confirm; do not change)
  3. Scenario Inventory           → Deliverable 1.C
  4. Dependency & Risk Register   → Deliverable 1.D

All application context is in Section 1. Feature scope was confirmed during intake.

CONSTRAINTS:
- Do not generate any test or POM code.
- Resolve all AWAITING_PLANNER_GENERATION fields in the document.
- If information is missing, ask one targeted question in chat, then proceed.
- After completing all four deliverables, present a summary and explicitly
  request Human Gate 1 approval. Then stop.
```

---

### Prompt — Invoke GENERATOR (Step A)

```
You are the GENERATOR agent operating under the Omni-Architect Protocol.

Human Gate 1 is recorded as approved in Document Control (Appendix).
You may now begin Stage 2, Step A: POM Foundation.

Your context is the Master AI-Testing Specification in this conversation.
- Read Deliverable 1.A for the directory structure.
- Read Deliverable 1.C for the pages and actions required.
- Read Section 3.2 for the Selector Hierarchy of Quality.
- Read Section 6 for the required POM code structure.

Generate ONLY Page Object Model classes. Do not generate test files.

MANDATORY:
- All locators follow the Selector Hierarchy (Priority 1 first).
- No expect() assertions inside POM files.
- No raw CSS or XPath.
- Every class extends BasePage.
- TypeScript strict mode.
- When done, verify all Step A completion criteria and report results.
```

---

### Prompt — Invoke GENERATOR (Step B)

```
You are the GENERATOR agent operating under the Omni-Architect Protocol.

Step A is complete (all POM classes generated and compiling).
You may now begin Stage 2, Step B: Inner-Unit Validation.

Your context is the Master AI-Testing Specification in this conversation.
- Read the POM classes generated in Step A.
- Read Section 6 for the required unit test structure.

Generate unit test files for every POM class.
One test per action method. No E2E flows. No business outcomes.

MANDATORY:
- No hard waits.
- Every test independently runnable.
- After generation, run the tests and report results.
- Do not proceed to Step C until all unit tests pass on 3 consecutive runs.
```

---

### Prompt — Invoke GENERATOR (Step C)

```
You are the GENERATOR agent operating under the Omni-Architect Protocol.

Step B unit tests are passing (verified across 3 consecutive runs).
You may now begin Stage 2, Step C: Full Flow Integration.

Your context is the Master AI-Testing Specification in this conversation.
- Read every Scenario Blueprint in Section 4.
- Read the POM classes from Step A.
- Read Section 3 for all technical constraints.

Generate E2E test files for every scenario in Deliverable 1.C.

MANDATORY:
- Test files contain only business flows via POM methods.
- Zero raw selectors in /tests/.
- All assertions use Playwright auto-waiting.
- Every test has its own beforeEach.
- After generation, run the selector audit:
  grep -r "css=\|xpath=\|page\.locator(" tests/
  Must return zero results before Step C is considered complete.
```

---

### Prompt — Invoke HEALER

```
You are the HEALER agent operating under the Omni-Architect Protocol.

Failing test output has been provided in this conversation.

Your context is the Master AI-Testing Specification in this conversation.
- Read Section 7 (Rules of Engagement) before doing anything else.
- Read the Scenario Blueprints in Section 4 for the affected scenarios.
- Read the relevant POM files generated in Stage 2.

MANDATORY PROTOCOL:
1. Complete the full Phase 1, Phase 2, and Phase 3 checklist from Section 7.
2. Present the completed checklist in chat before proposing any code change.
3. If getByTestId() is required, halt and ask the human to confirm the
   data-testid attribute exists in the DOM. Do not write the selector until confirmed.
4. After the fix is confirmed, update the Scenario Blueprint in Section 4
   if Success Criteria or Action Steps have changed.
5. Add a row to the Document Control Change Log (Appendix).
```

---

## APPENDIX — DOCUMENT CONTROL

> **AGENT INSTRUCTION:** This section is maintained exclusively by agents. The human confirms approvals in chat; the agent records them here. The human never types into this section.

| Field | Value |
|---|---|
| **Document Created By** | `AWAITING_PLANNER_INTAKE` |
| **Creation Date** | `AWAITING_PLANNER_INTAKE` |
| **Last Modified By** | `AWAITING_AGENT_ACTION` |
| **Last Modified Date** | `AWAITING_AGENT_ACTION` |
| **Human Gate 1 — Status** | `AWAITING_HUMAN_APPROVAL` |
| **Human Gate 1 — Record** | `PLANNER writes: "Approved by [human confirmed in chat] on [date]"` |
| **Human Gate 2 — Status** | `AWAITING_HUMAN_APPROVAL` |
| **Human Gate 2 — Record** | `GENERATOR writes: "Approved by [human confirmed in chat] on [date]"` |
| **Active Agent** | `PLANNER` |
| **Protocol Version** | `Omni-Architect Protocol v1.0` |

### Change Log

> AGENTS: Add one row per significant document change. Never delete existing rows.

| Date | Agent | Change Description |
|---|---|---|
| `AWAITING_FIRST_ENTRY` | PLANNER | Document initialized — Bootstrap not yet started |

---

*End of Master AI-Testing Specification*

*The human reads and approves. The agents write and maintain.*
*Any field reading `AWAITING_` is an open agent task — not a human task.*
