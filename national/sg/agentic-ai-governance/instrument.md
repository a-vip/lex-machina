# Singapore IMDA Model AI Governance Framework for Agentic AI (2026)

- **Stage**: IMDA Model AI Governance Framework for Agentic AI (2026 PDF) (`imda_mgf_agentic_ai_2026`)
- **Document Symbol**: `SG IMDA MGF-Agentic-2026`
- **Date**: `2026-01-22`
- **Institutional Author**: `Infocomm Media Development Authority of Singapore (IMDA) <ai-governance@imda.gov.sg>`
- **Provenance Mode**: `full_primary_pdf`
- **Primary Source SHA-256**: `2636e19ff1c86e862394d2fc900592e97b83c04cc35e3c8443108114b7f1dfba`
- **Source URL**: https://www.imda.gov.sg/-/media/imda/files/about/emerging-tech-and-research/artificial-intelligence/mgf-for-agentic-ai.pdf

> Verbatim official IMDA PDF establishing four core governance pillars for autonomous AI agents: assessing/bounding risks upfront, making humans meaningfully accountable, implementing technical controls & process gates, and enabling end-user responsibility.

## Enacting Terms (Articles)

### Article 1 — Assess and bound the risks upfront

• Avoid deploying OpenClaw as-is in mission-critical environments, including systems that
handle sensitive data or financial transactions
• Avoid creating a single “all-powerful” agent with unrestricted access, instead use multiple
agents with narrow, clearly defined rules
• Avoid installing OpenClaw on primary work or personal devices containing sensitive data,
and granting it unrestricted access to files and applications

### Article 2 — Make humans meaningfully accountable

• Adopt a risk-based approach to determine the appropriate level of agent autonomy based
on data sensitivity and task criticality
• Enforce human approval through system-level controls where possible, vs prompt-layer
guardrails, which may be bypassed or “forgotten”

### Article 3 — Implement technical controls and processes

• During design and development, review and tighten OpenClaw configurations which are
permissive by default e.g. restrict messaging channel access, using dedicated identities
and credentials for the agent
• Before deployment, test and verify that safety controls and human-in-the-loop is working
as intended e.g. attempt disallowed actions to ensure restrictions work
• After deployment, ensure all agent actions are logged and attributable, and avoid leaving
the agent unsupervised for extended periods

### Article 4 — Enable end-user responsibility

• Provide personnel training to improve employees’ awareness of autonomous agent risks
and reinforce their responsibility to prevent careless misuse
See the full case study here.
Model AI Governance Framework for Agentic AI
|
Assess and bound the risks upfront
15
2.1 Assess and bound the risks upfront
Agents bring new risks, especially in their access to sensitive data and ability to change their environment
through action-taking. Their adaptive, autonomous and multi-step nature also increases the potential for
unexpected actions, emergent risks and cascading impacts. Organisations should consider these new
dimensions through:
• Determining suitable use cases for agent deployment by considering agent-specific factors that
can affect the likelihood and impact of the risk.
• Design choices to bound the risks upfront by applying limits on agent’s access to tools and
systems and defining a robust identity and permissions framework.
2.1.1 Determine suitable use cases for agent deployment
When considering if an agentic use case is suitable for development or deployment, first identify and
assess the risk against the benefits. Risk is a function of likelihood (probability of the risk manifesting) and
impact (severity of impact if the risk manifests). Not all use cases are suitable for agents, and some may be
better served by deterministic workflows.
The following non-exhaustive factors affect the level of risk of an agentic use case:
Factors affecting impact (severity of impact if the risk manifests)
Factor Description Illustration
Domain and use
case in which
agent is being
deployed
Level of tolerance of error in the domain and
use case in which the agent is being deployed.
Also consider the number and criticality of
business processes the agent supports, which
affects the impact of agent failure.
Agent executing financial
transactions which require a
high degree of accuracy would
have a larger negative impact if
an error were made, vs agent
that summarises internal
meetings
Agent’s access
to sensitive data
Whether the agent can access sensitive data,
such as personal information or confidential
data.
If agent has such access, the risk increases if
the agent has persistent memory and can store
sensitive data across sessions.
Agent that requires access to
personal customer data gives
rise to the risk of leaking such
data, vs agent who only has
access to publicly available
information
Agent’s access
to external
systems
Whether the agent can access external
systems.
Agent that sends data to third-
party APIs can leak data to these
third parties, or disrupt these
systems by making too many
requests, vs agent that only has
Model AI Governance Framework for Agentic AI
|
Assess and bound the risks upfront
16
access to sandboxed or internal
tools
Scope of agent’s
actions
Whether an agent can only read from or can
also modify the data and systems it has access
to.
Whether the agent can complete a small or
wide range of actions using tools available to it.
Read vs write: Agent that can
only read from a database
cannot impact the database, vs
agent that can write to it
Many actions vs a few: Agent
that can only choose from a few
pre-defined tools, vs one who
has access to a computer use
tool that can navigate any user
interface
Reversibility of
agent’s actions
If the agent can modify data and systems,
whether such modifications are easily
reversed. Modifications may not be easily
reversed if they trigger downstream obligations
e.g. entering into a contract or sale.
Agent that schedules meetings
can easily reschedule them if an
error is made, vs agent that
sends email communications to
external parties
Factors affecting likelihood (probability of the risk manifesting)
Factor Description Illustration
Agent’s level of
autonomy
Whether the agent can define the entire
workflow or must follow a well-defined
procedure.
A higher level of autonomy can result in higher
unpredictability, increasing likelihood of error.
Agent is provided with a SOP
and instructed to follow it when
carrying out a task, vs agent is
instructed to use its best
judgment to select and execute
every step
Task complexity How complex the task is, in relation to the
number of steps required to complete it and
the level of analysis required at each step.
A higher level of task complexity similarly
increases unpredictability and the likelihood of
error.
Agent is required to extract key
action points from a meeting
transcript, vs agent is tasked to
follow a nuanced data sharing
policy when handling external
requests for information
Agent’s access
to external
systems
Whether the agent is exposed to external
systems, and who maintains these systems.
A higher level of exposure makes the agent
more vulnerable to prompt injections and
cyberattacks.
Agent who can only access an
internal knowledge base which
is maintained by trusted internal
teams, vs an agent who can
access the web containing
untrusted data
Model AI Governance Framework for Agentic AI
|
Assess and bound the risks upfront

### Article 17 — Agent being

provided or
operated by an
external party
Whether the organisation is using agents
provided or operated by external parties.
When using third-party solutions, organisations
should consider to what extent their visibility
and control over the agent is limited.
Agent developed and maintained
internally with full visibility vs
agent provided by third-party
vendor with limited transparency
into its operations and data
processing
System
complexity
How complex the agentic system is, e.g. using
multiple agents with autonomous decision-
making, feedback loops.
A system can also become complex due to a
combination of different factors above (e.g.
complex tasks with greater autonomy). A
higher level of system complexity can result in
more unpredictable and emergent behaviour as
components interact in unexpected ways,
compounding any negative effects.
A single agent carrying out a
sequential workflow vs multiple
agents which can interact with
each other, make decisions
collectively, or autonomously
handoff to other agents
Threat modelling also makes risk assessment
more rigorous by systematically identifying
specific ways in which an attacker may take to
compromise the system. Common security
threats to agentic systems include memory
poisoning, tool misuse, and privilege
compromise. 17 As agentic systems can become
very complex, it is often useful to use a method
called taint tracing to map out all the workflows
and interactions to track how untrusted data can
move through the system. For more information on
how to perform threat modelling and taint tracing
for agentic systems, organisations may refer to
CSA’s Draft Addendum on Securing Agentic AI.

### Article 18 — Dayos: Tiering and bounding agentic actions by risk level in IT management

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

### Article 20 — OCBC: Bounding agent autonomy in source of wealth analysis

OCBC is the longest established Singapore bank and the second largest financial services group in
Southeast Asia by assets, operating in 19 countries and regions. Bank of Singapore is a wholly owned
private banking subsidiary of OCBC.
Bank of Singapore Relationship Manager and compliance team synthesise customer-provided
financial documents into a structured Source of Wealth memo. The bank developed an agentic AI
system to support this work with the objectives of:
• Improving consistency and completeness of the analysis
• Reducing manual effort in document review and drafting
The agentic AI system parses income-related documents (e.g. tax submissions, corporate annual
reports, property documents, dividend statements) and generates a draft Source of Wealth memo
based on internal guidelines and benchmarks. The system provides decision support only and does
not make credit, onboarding or risk decisions autonomously – final validation and approval remain
with designated human reviewers.
The agentic workflow bounds risk through design by defining limits on the agents’ autonomy:
• Task-level autonomy only: Agents perform narrowly scoped tasks (extraction, drafting,
checking), not end-to-end decisions
• No self-initiation of actions: Agents operate only when triggered by predefined workflows
• No decision authority: There is human review at critical decision points, including after the
income and financial documents have been assessed to ensure accuracy. Ultimately, outputs
are advisory and subject to human validation.
Model AI Governance Framework for Agentic AI
|
Assess and bound the risks upfront

### Article 21 — MSD: Bounding the risks of agentic AI through tiered autonomy and third-party

ecosystem boundaries
MSD aims to use the power of leading-edge science to save and improve lives around the world, bringing
forward medicines, vaccines and innovative health solutions for the world’s most challenging diseases.
MSD develops and deploys agents in use cases such as streamlining the production of key trial
protocols and minimizing labor-intensive tasks like clinical documentation and quality review. For its
75,000 employees, MSD implemented an enterprise agentic AI governance strategy that bounds risk
by, among other things, calibrating governance processes to level of agency, and derisking third-party
platforms.
Calibrating governance processes to level of agency
MSD created multiple risk-calibrated governance pathways based on five levels of agency, accounting
for factors such as action and permission scope, human oversight, data and context scope etc.
• Lower levels move quickly through a lightweight governance pathway; middle levels move
through an established AI impact assessment process, and higher levels require escalations to
enterprise architecture review and testing where appropriate.
• The highest levels of agency require technical measures beyond monitoring. A programmatic
runtime policy enforcement layer is being implemented at the AI gateway before higher levels
of autonomy are enabled.
Model AI Governance Framework for Agentic AI
|
Assess and bound the risks upfront

### Article 22 — Derisking third-party agent platforms

Beyond agentic autonomy, enterprise AI invariably includes multiple third-party SaaS agentic platforms.
While each third-party agent platform would have performed validation and testing within its own
ecosystem, risks increase when these systems attempt to perform cross platform actions which may
not have been exhaustively tested. This is particularly the case as interoperability frameworks are still
nascent and maturing.
To promote safety and security, MSD adopted a containment strategy — rather than allowing vendor-
embedded agents to act freely across MSD’s data and systems, agentic features in SaaS tools are by
default restricted to within their own ecosystems. This contains residual risk while preserving the
productivity benefits of approved use cases.
Model AI Governance Framework for Agentic AI
|
Assess and bound the risks upfront

### Article 23 — Agent identity

Identity management and access control is one of the key means in which organisations enable
traceability and accountability today for humans. As organisations deploy more agents, including agents
which interact across organisation boundaries, identity management needs to be extended to agents to
track individual agent behaviour and establish who holds accountability for each agent.
This is an evolving space, and gaps exist today in terms of handling agent identity robustly. For example,
current authorisation systems typically have pre-defined, static scopes. However, to operate safely in more
complex scenarios, agents require fine-grained permissions that may change dynamically depending on the
context, risk levels, and task objectives. Current authentication systems are also typically based on a single,
unique individual. Such systems face difficulty in handling complex agent setups, such as when agents act
for multiple human users with different permissions, or recursive delegation scenarios where agents spin
up multiple sub-agents.21
Solutions are being developed to address these issues, such as intra-organisation identity systems being
extended to agents,22 or integrating well-established standards like OAuth 2.1 into MCP.23 The industry is
also developing new standards and solutions for agents, such as decentralised identity management and
dynamic access control.24
In the interim, organisations should consider these best practices:
• Identification: An agent’s identity should be:
o Unique: An agent should have its own unique, cryptographically verifiable identity, such
that it can identify itself to the organisation, its human user, or other agents.
o Accounted for: This identity should be tied to a supervising agent, a human user, or an
organisational department for accountability and tracking.
o Differentiated according to the capacity in which it acts: The different capacities in
which an agent acts (e.g. independently or on behalf of a specified human user) should be
recorded for auditability.
o Catalogued and centrally managed: To prevent agent sprawl, all agent identities (and their
attendant permissions) should be issued from and tracked by a centralised system. This
enables an organisation to track its deployed agents, identify any anomalies, and remove
identities that are no longer required.

### Article 24 — See proposed framework for agentic identity by Cloud Security Alliance, Agentic AI Identity & Access

Management: A New Approach.
Model AI Governance Framework for Agentic AI
|
Assess and bound the risks upfront
24
• Authorisation: An agent’s authority should be:
o Scoped, least-privilege, non-transferable: Authorisations should generally be scoped,
time- or session-bound, non-transferable, and follow the principle of least privilege by
default, with explicit escalation paths for elevated permissions.
o Bounded by authorising human’s permissions: An agent can have pre-defined
permissions based on its role or the task, or its permissions may be dynamically set by its
authorising human user, or a combination of both. As a rule of thumb, the human user
should not be able to set permissions for the agent greater than what the human user is
himself authorised to do, such as accessing data outside the human’s permissions. Such
delegations of authority should be clearly recorded.
Evaluating the residual risks
Residual risk is the risk that remains after mitigation measures have been applied. It is important to note
that there will always be a level of risk remaining, even after efforts are taken to identify appropriate
agentic use cases and define limits on any agents, especially given how quickly agentic AI is evolving.
Ultimately, organisations should evaluate and determine if the residual risk for their agentic deployment
is of a tolerable level and can be accepted.
Model AI Governance Framework for Agentic AI
|
Make humans meaningfully accountable
25
2.2 Make humans meaningfully accountable
The organisations that deploy agents and the humans who oversee them remain accountable for the agents’
actions. But it can be challenging to fulfil this accountability when agent actions emerge dynamically and
adaptively from interactions instead of fixed logic. Multiple stakeholders may also be involved in different
parts of the agent lifecycle, diffusing accountability. Finally, automation bias, or the tendency to over-trust
an automated system, especially when it has performed reliably in the past, becomes a bigger concern as
humans supervise increasingly capable agents.
To address these challenges to human accountability, organisations should consider:
• Clear allocation of responsibilities within and outside the organisation, by establishing chains
of accountability across the agent value chain and lifecycle, while emphasising adaptive
governance, so that the organisation is set up to quickly understand new developments and update
their approach as the technology evolves.
• Measures to enable meaningful human oversight of agents, such as requiring human approval at
significant checkpoints, auditing the effectiveness of human approvals, and complementing these
measures with automated monitoring.
2.2.1 Clear allocation of responsibilities within and outside the organisation
As deployers, organisations and humans remain accountable for the decisions and actions of agents.
However, as with AI, the value chain for agentic AI involves multiple actors. Organisations should consider
the allocation of responsibility both within their organisation, and vis-à-vis other organisations along the
value chain.
Simplified agentic AI value chain25
Organisations may play multiple overlapping roles across this value chain. For example, an organisation
that develops its own agents and subsequently deploys them would play both the role of the system
provider and the deployer.

### Article 25 — For a more comprehensive list of potential stakeholders involved in the agentic AI ecosystem, see CSA and

FAR.AI, Securing Agentic AI: A Discussion Paper.
Model
developers
Platform
providers
Deployer
End users
Tooling providers
e.g. MCP, APIs
System providers
/ app developers
Model AI Governance Framework for Agentic AI
|
Make humans meaningfully accountable
