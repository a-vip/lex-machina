# Article 23 — Agent identity

- **Instrument**: Singapore Agentic AI Framework
- **Stage**: IMDA Model AI Governance Framework for Agentic AI (2026 PDF) (`2026-01-22`)
- **Document Symbol**: `SG IMDA MGF-Agentic-2026`
- **Akoma Ntoso eId**: `sec_23`
- **Provenance Mode**: `full_primary_pdf`
- **Institutional Author**: Infocomm Media Development Authority of Singapore (IMDA) `<ai-governance@imda.gov.sg>`

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
