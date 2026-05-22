# Journey and Information Architecture

Four decomposition frameworks for understanding how users move through a product and how content is organized for navigation. Each takes a different cut: Norman's seven stages decomposes a single interaction; service blueprints map a journey across surfaces; JTBD frames the user's intent; customer journey maps surface emotional state across touchpoints. Two empirical methods: card sorts (for category discovery) and tree tests (for navigation validation). One inventory discipline: content inventory.

## Contents

- [x] Norman's seven stages of action
- [x] Service blueprint
- [x] Jobs-To-Be-Done (JTBD)
- [x] Customer journey map
- [x] Card sort
- [x] Tree test
- [x] Content inventory
- [x] When to reach for which
- [x] Cross-references

## Norman's seven stages of action

Donald Norman's seven-stage model (from *The Design of Everyday Things*, 1988) decomposes a single goal-directed interaction. Useful for analyzing failure points in a flow.

1. **Goal** — what the user wants to accomplish ("send a payment").
2. **Intention to act** — translation of goal into an intended action ("I'll use the payment button").
3. **Action specification** — planning the action sequence ("click button, enter amount, confirm").
4. **Execution** — performing the actions on the interface.
5. **Perception** — perceiving the system's response.
6. **Interpretation** — interpreting the perception ("did that work? what does this number mean?").
7. **Evaluation** — comparing the result to the original goal ("did I send the payment?").

The model surfaces two gulfs:

- **Gulf of execution** — between intention and execution. The user knows what they want but can't figure out how to do it. Caused by hidden affordances, unclear mapping, ambiguous labels.
- **Gulf of evaluation** — between perception and evaluation. The user did something but can't tell what happened. Caused by silent results, ambiguous feedback, status invisibility.

Most usability failures live in one of the gulfs. Pair Norman with Nielsen's heuristic 1 (visibility of system status) and heuristic 2 (match to real world) for diagnosing.

A worked example — a "save draft" flow:

| Stage | Possible failure |
|---|---|
| Goal | User wants to save partial work for later |
| Intention | "I'll save a draft" |
| Action spec | "I'll click... where?" — gulf of execution if no visible save affordance |
| Execution | Click Save button |
| Perception | Button shows "Saving..." then returns to "Save" — visible |
| Interpretation | "Was that saved? Where did it go?" — gulf of evaluation if there's no confirmation or list of drafts |
| Evaluation | User compares to goal: "I think it saved but I'm not sure where to find it later" |

The interface fix: confirmation message ("Draft saved") + a "Your drafts" list reachable from main navigation. Both gulfs closed.

## Service blueprint

Service blueprints (from service design discipline) map a user-facing journey to the backstage processes that enable it. Useful when a flow crosses multiple surfaces (web UI, email, support, fulfillment) and you need to coordinate.

Five layers, stacked vertically, organized horizontally by journey step:

| Layer | Contents |
|---|---|
| User actions | What the user does at each step |
| Frontstage interactions | UI elements / employee interactions the user sees |
| Backstage interactions | Employee actions / systems the user doesn't see |
| Support processes | Systems and infrastructure |
| Evidence | Physical or digital artifacts produced |

Example — placing an order:

| Step | 1. Browse | 2. Add to cart | 3. Checkout | 4. Pay | 5. Receive |
|---|---|---|---|---|---|
| User action | Searches | Clicks Add | Enters address | Pays | Opens package |
| Frontstage | Search UI | Cart UI | Form UI | Payment UI | Email confirmation |
| Backstage | Search indexer | Inventory check | Address validation | Payment gateway | Fulfillment system |
| Support | Database | ERP | Address API | Stripe / payment | Warehouse + shipping |
| Evidence | Search results | Cart contents | Order summary | Receipt | Package + invoice |

The blueprint surfaces dependencies. A change to the user-facing checkout form ripples to backstage validation, payment integration, and evidence (receipt) generation. Service-level coordination shifts from "do we have a checkout page" to "do all five layers cohere at step 3."

## Jobs-To-Be-Done (JTBD)

JTBD frames the user's task as a "job" the product is "hired" to do. Originated with Christensen and refined by Klement and Spiek. The framing surfaces motivation in a way that "user persona" framings miss.

A JTBD statement has three parts:

1. **Situation** — when the user has this need.
2. **Motivation** — what they're trying to achieve (the "job").
3. **Expected outcome** — what success looks like.

Format: "When I [situation], I want to [motivation], so I can [outcome]."

Examples:

- "When I'm in a meeting and need to take notes, I want to capture them in a tool that's faster than typing, so I can stay engaged with the conversation."
- "When I'm planning a team's quarterly priorities, I want to see what we committed to last quarter, so I can avoid promising the same things twice."

The discipline JTBD enforces: stop describing what users ARE (demographic; persona) and start describing what they're TRYING TO DO. A 23-year-old grad student and a 55-year-old executive may share the same JTBD ("when I want to find research on a topic, I want filtered, ranked results, so I can identify what's worth reading"). Design for the job, not the demographic.

JTBD pairs with Norman's seven stages: the JTBD names the goal (stage 1) and outcome (stage 7); Norman's stages name the path between.

## Customer journey map

Customer journey maps trace a multi-touchpoint journey, surfacing emotional state, friction points, and opportunities. Broader than a service blueprint — typically spans pre-purchase through post-purchase, across marketing / sales / product / support surfaces.

Layers typically include:

- **Phases** — major journey segments (Awareness → Consideration → Purchase → Onboarding → Use → Renewal/Churn).
- **Actions** — what the user does in each phase.
- **Touchpoints** — surfaces the user encounters (ads, website, email, app, support).
- **Thoughts / feelings** — what the user is thinking; emotional state (excitement, frustration, confidence).
- **Pain points** — where the journey fails the user.
- **Opportunities** — design and product interventions.

The "emotional curve" — plotting affect across the journey — is the journey map's distinctive contribution. It surfaces moments where users are most receptive (high points: capitalize) and most fragile (low points: invest in friction reduction).

Compared to JTBD, journey maps are broader in scope (the whole customer relationship) and lighter on motivation framing (focus is on the surface contact points). Use both: JTBD for "why is this happening at all"; journey map for "where in the relationship is this happening."

## Card sort

Empirical method for discovering how users mentally group items. Participants are given a set of cards (each card = one item, page, or category) and asked to organize them.

Two variants:

- **Open card sort** — participants create their own groups and label them. Surfaces the user's mental model.
- **Closed card sort** — participants assign cards to predefined groups. Validates a proposed structure.

A typical card sort uses 30-60 cards and 8-15 participants. Results aggregate: which items consistently cluster, which split contentiously, which labels emerge for groups.

Use case: a design system needs to organize 80 components in its documentation sidebar. Open card sort with 12 frontend engineers surfaces that they group by "form / feedback / navigation / layout / data display" — not by alphabet or by atomic-design tier.

The output is qualitative + quantitative — clustering frequencies plus the participant rationales. Both inform the decision.

## Tree test

Empirical method for validating a navigation structure. Participants are given a text-only representation of the navigation tree and asked to locate specific items.

Setup: a hierarchical menu (e.g., Products → Cameras → DSLR → Canon → 5D) presented as expandable text. The participant is given a task ("Find the Canon 5D camera specifications") and clicks through the tree to where they think the answer lives.

Metrics:

- **Directness** — did the user reach the answer without backtracking?
- **Success rate** — what percentage found the right location?
- **First-click correctness** — did the first click go to the right top-level category?

A tree test is faster and cheaper than a full prototype usability test. It isolates the navigation question from the visual design question. Use after card sort produces a hypothesized structure; use tree test to validate before building.

Tools that automate tree tests: Treejack (Optimal Workshop), UserZoom Tree Testing, and others. Manual administration also works for smaller projects.

## Content inventory

A content inventory catalogs what content exists across the product, where it lives, and its current status. Useful for redesigns, content audits, and IA restructuring.

Columns typically include:

- **ID** — unique identifier (numeric or path-based).
- **URL / location** — where the content currently lives.
- **Title** — the content's current title.
- **Type** — article, page, marketing copy, in-app help, etc.
- **Owner** — who maintains the content.
- **Last updated** — staleness check.
- **Status** — active, deprecated, redirect, archive.
- **Migration disposition** — keep, revise, retire, merge (for redesign contexts).

A modest product may have 50-200 inventory entries. A large enterprise product may have thousands. Spreadsheet tooling (Google Sheets, Airtable) handles either end.

The inventory enables decisions that "we'll figure it out in design" defers indefinitely: which pages get redirected, which are written from scratch, which migrate as-is. Without an inventory, redesigns produce orphaned content.

## When to reach for which

| Question | Framework |
|---|---|
| Why is this single interaction failing? | Norman's seven stages |
| How do multiple surfaces / teams need to coordinate? | Service blueprint |
| What is the user actually trying to accomplish? | JTBD |
| Where in the broad customer relationship is this happening? | Customer journey map |
| How should categories be organized? | Card sort (open or closed) |
| Does this proposed navigation work? | Tree test |
| What content do we have? | Content inventory |

A new feature design may touch several: a JTBD frames the motivation; a customer journey map situates the feature in the broader relationship; Norman's stages diagnose the single interaction; a tree test validates the navigation entry point. Most features don't need all of these — match the framework to the question that's actually load-bearing.

## Cross-references

- **Heuristics for evaluating an interaction's quality:** see `principles.md`.
- **Accessibility considerations in journey design:** see `accessibility-as-flow.md`.
- **Design-system patterns that codify journey-tested patterns:** see `KB-design-system-design`.
- **Norman's foundational text:** Norman, Donald. *The Design of Everyday Things*. Revised Edition, 2013.
- **Service design / blueprints:** Stickdorn et al. *This is Service Design Doing*. 2018.
- **JTBD foundational text:** Klement, Alan. *When Coffee and Kale Compete*. 2016.
