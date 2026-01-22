# Article 18 — Dayos: Tiering and bounding agentic actions by risk level in IT management

- **Instrument**: Singapore Agentic AI Framework
- **Stage**: IMDA Model AI Governance Framework for Agentic AI (2026 PDF) (`2026-01-22`)
- **Document Symbol**: `SG IMDA MGF-Agentic-2026`
- **Akoma Ntoso eId**: `sec_18`
- **Provenance Mode**: `full_primary_pdf`
- **Institutional Author**: Infocomm Media Development Authority of Singapore (IMDA) `<ai-governance@imda.gov.sg>`

Dayos is an enterprise AI automation company headquartered in Singapore with operations in the US.
The company builds Hero, an agentic platform that sits on top of Oracle, SAP, Workday, NetSuite and
Microsoft Dynamics and automates workflows across IT management, accounting, HR and
procurement.
Dayos replaced its own ServiceNow instance with an AI-powered ticketing agent built on Hero. The full
retirement took 45 days and reduced legacy licensing costs by $121,000 annually. The agent now
handles every internal IT request that comes in: it reads the ticket, determines how urgent and complex
it is, and either resolves it automatically or routes it to a human.
Before any of this went live, Dayos ran a structured risk assessment. Every type of IT ticket was scored
against three questions:
• Severity of impact: If the agent gets this wrong, how bad is it?
• Reversibility: Can the action be undone?
• Feasibility of human oversight: Is it realistic for a human to review this at each step?
The scores determined which tier each ticket type falls into, and that tier dictated what reasoning
strategy the agent uses and how much autonomy the agent gets.
Tier
What falls here
What the agent does (and does not do)
Tier 1 (60%
of tickets)
Low severity,
fully
reversible
Password resets,
access requests,
status inquiries
• Fully automated by agent using Simple Feedback (a
propose-confirm loop). The agent proposes, the user
confirms or pushes back, and agent adjusts until the ticket
is closed. No human engineer is in the loop.
• But with biweekly audits: Every action produces a
reasoning chain that captures classification logic and a
confidence score. A designated reviewer audits a cross-
section of these biweekly. As every Tier 1 action is
reversible, errors can be corrected without any lasting
damage.
Tier 2 (30%
of tickets)
Moderate
severity,
partially
reversible
Chart of accounts
updates,
integration
mapping
corrections,
diagnosing failed
API connections
• Agent diagnoses but can only act with a human
engineer’s approval. Uses the ReACT strategy (a multi-
step diagnostic loop for harder problems): the agent
checks logs, queries connected systems, identifies the
probable root cause, and writes up a diagnostic summary
with a proposed fix. But a qualified engineer has to review
and sign off before anything executes.
Tier 3 (10%
of tickets)
High severity,
limited
reversibility
Production
deployments,
security changes,
permission
modifications
• Agent does not touch these. Production deployments and
security changes carry too much risk for autonomous
execution at the current maturity of agentic AI. As
safeguards improve and are validated in real environments
– e.g. multi-agent verification and real-time anomaly
detection – Dayos will reassess whether bounded
automation makes sense for specific Tier 3 actions.
Model AI Governance Framework for Agentic AI
|
Assess and bound the risks upfront
19
2.1.2 Bound risks through design by defining agents limits and permissions
Having selected an appropriate agent use case, organisations can further bound the risks by defining
appropriate limits and permission policies for each agent.
Agent limits
Organisations should consider defining limits on:
• Agent’s access to tools and systems: Define least-privilege policies that give agents only the
minimum tools and data access needed for it to complete its task.18 For example, a coding assistant
may not require access to a broad web search tool, especially if it already has curated access to
the latest software documentation. Structuring agents around functional boundaries (e.g.
separating IT helpdesk from HR self-service) can act as a natural constraint.
• Agent’s autonomy: For process-driven tasks, SOPs and protocols are frequently used to improve
consistency and reduce unpredictability.19 Define similar SOPs for agentic workflows that an agent
is constrained to follow, rather than giving the agent the freedom to define every step of the
workflow.
• Agent’s area of impact: Design mechanisms and procedures to take agents offline and limit their
potential scope of impact when they malfunction. This can include running agents in self-contained
environments with limited network and data access, particularly when they are carrying out high-
risk tasks such as code execution.20
In general, prefer deterministic rather than non-deterministic limits, and bound by design. For example,
rather than relying on prompts to instruct the agent against accessing certain tools, impose access controls
that prevent the tool from being called by the agent at all. This is elaborated in 2.3.1 Implement technical
controls and processes. Where limits are non-deterministic or less reliable, layer on more monitoring
measures or incorporate human-in-the-loop review to catch any failures.
