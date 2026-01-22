# Article 4 — Enable end-user responsibility

- **Instrument**: Singapore Agentic AI Framework
- **Stage**: IMDA Model AI Governance Framework for Agentic AI (2026 PDF) (`2026-01-22`)
- **Document Symbol**: `SG IMDA MGF-Agentic-2026`
- **Akoma Ntoso eId**: `sec_4`
- **Provenance Mode**: `full_primary_pdf`
- **Institutional Author**: Infocomm Media Development Authority of Singapore (IMDA) `<ai-governance@imda.gov.sg>`

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
