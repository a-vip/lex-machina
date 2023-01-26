# Article 4 — Core Function 4 — MANAGE (nist_ai_rmf_1_0)

- **Instrument**: US Federal AI & NIST RMF
- **Stage**: NIST AI Risk Management Framework 1.0 (NIST AI 100-1) (`2023-01-26`)
- **Document Symbol**: `NIST AI 100-1`
- **Akoma Ntoso eId**: `nist_manage`
- **Provenance Mode**: `full_primary_pdf`
- **Institutional Author**: National Institute of Standards and Technology (NIST) `<ai-rmf@nist.gov>`

MANAGE 1.4: Negative residual risks (defined as the sum of all
unmitigated risks) to both downstream acquirers of AI systems
and end users are documented.
MANAGE 2:
Strategies to
maximize AI
benefits and
minimize negative
impacts are planned,
prepared,
implemented,
documented, and
informed by input
from relevant AI
actors.
MANAGE 2.1: Resources required to manage AI risks are taken
into account – along with viable non-AI alternative systems, ap-
proaches, or methods – to reduce the magnitude or likelihood of
potential impacts.
MANAGE 2.2: Mechanisms are in place and applied to sustain
the value of deployed AI systems.
MANAGE 2.3: Procedures are followed to respond to and recover
from a previously unknown risk when it is identified.
MANAGE 2.4: Mechanisms are in place and applied, and respon-
sibilities are assigned and understood, to supersede, disengage, or
deactivate AI systems that demonstrate performance or outcomes
inconsistent with intended use.
MANAGE 3: AI
risks and benefits
from third-party
entities are
managed.
MANAGE 3.1: AI risks and benefits from third-party resources
are regularly monitored, and risk controls are applied and
documented.
MANAGE 3.2: Pre-trained models which are used for develop-
ment are monitored as part of AI system regular monitoring and
maintenance.
Categories Subcategories
Continued on next page
Page 32
NIST AI 100-1 AI RMF 1.0
Table 4: Categories and subcategories for the MANAGE function. (Continued)
MANAGE 4: Risk
treatments,
including response
and recovery, and
communication
plans for the
identified and
measured AI risks
are documented and
monitored regularly.
MANAGE 4.1: Post-deployment AI system monitoring plans
are implemented, including mechanisms for capturing and eval-
uating input from users and other relevant AI actors, appeal
and override, decommissioning, incident response, recovery, and
change management.
MANAGE 4.2: Measurable activities for continual improvements
are integrated into AI system updates and include regular engage-
ment with interested parties, including relevant AI actors.
MANAGE 4.3: Incidents and errors are communicated to relevant
AI actors, including affected communities. Processes for track-
ing, responding to, and recovering from incidents and errors are
followed and documented.
Categories Subcategories
6. AI RMF Profiles
AI RMF use-case profiles are implementations of the AI RMF functions, categories, and
subcategories for a specific setting or application based on the requirements, risk tolerance,
and resources of the Framework user: for example, an AI RMF hiring profile or an AI
RMF fair housing profile. Profiles may illustrate and offer insights into how risk can be
managed at various stages of the AI lifecycle or in specific sector, technology, or end-use
applications. AI RMF profiles assist organizations in deciding how they might best manage
AI risk that is well-aligned with their goals, considers legal/regulatory requirements and
best practices, and reflects risk management priorities.
AI RMF temporal profiles are descriptions of either the current state or the desired, target
state of specific AI risk management activities within a given sector, industry, organization,
or application context. An AI RMF Current Profile indicates how AI is currently being
managed and the related risks in terms of current outcomes. A Target Profile indicates the
outcomes needed to achieve the desired or target AI risk management goals.
Comparing Current and Target Profiles likely reveals gaps to be addressed to meet AI risk
management objectives. Action plans can be developed to address these gaps to fulfill
outcomes in a given category or subcategory. Prioritization of gap mitigation is driven by
the user’s needs and risk management processes. This risk-based approach also enables
Framework users to compare their approaches with other approaches and to gauge the
resources needed (e.g., staffing, funding) to achieve AI risk management goals in a cost-
effective, prioritized manner.
Page 33
NIST AI 100-1 AI RMF 1.0
AI RMF cross-sectoral profiles cover risks of models or applications that can be used across
use cases or sectors. Cross-sectoral profiles can also cover how to govern, map, measure,
and manage risks for activities or business processes common across sectors such as the
use of large language models, cloud-based services or acquisition.
This Framework does not prescribe profile templates, allowing for flexibility in implemen-
tation.
Page 34
NIST AI 100-1 AI RMF 1.0
Appendix A:
Descriptions of AI Actor Tasks from Figures 2 and 3
AI Design tasks are performed during the Application Context and Data and Input phases
of the AI lifecycle in Figure 2. AI Design actors create the concept and objectives of AI
systems and are responsible for the planning, design, and data collection and processing
tasks of the AI system so that the AI system is lawful and fit-for-purpose. Tasks include ar-
ticulating and documenting the system’s concept and objectives, underlying assumptions,
context, and requirements; gathering and cleaning data; and documenting the metadata
and characteristics of the dataset. AI actors in this category include data scientists, do-
main experts, socio-cultural analysts, experts in the field of diversity, equity, inclusion,
and accessibility, members of impacted communities, human factors experts (e.g., UX/UI
design), governance experts, data engineers, data providers, system funders, product man-
agers, third-party entities, evaluators, and legal and privacy governance.
AI Development tasks are performed during the AI Model phase of the lifecycle in Figure
2. AI Development actors provide the initial infrastructure of AI systems and are responsi-
ble for model building and interpretation tasks, which involve the creation, selection, cali-
bration, training, and/or testing of models or algorithms. AI actors in this category include
machine learning experts, data scientists, developers, third-party entities, legal and privacy
governance experts, and experts in the socio-cultural and contextual factors associated with
the deployment setting.
AI Deployment tasks are performed during the Task and Output phase of the lifecycle in
Figure 2. AI Deployment actors are responsible for contextual decisions relating to how
the AI system is used to assure deployment of the system into production. Related tasks
include piloting the system, checking compatibility with legacy systems, ensuring regu-
latory compliance, managing organizational change, and evaluating user experience. AI
actors in this category include system integrators, software developers, end users, oper-
ators and practitioners, evaluators, and domain experts with expertise in human factors,
socio-cultural analysis, and governance.
Operation and Monitoring tasks are performed in the Application Context/Operate and
Monitor phase of the lifecycle in Figure 2. These tasks are carried out by AI actors who are
responsible for operating the AI system and working with others to regularly assess system
output and impacts. AI actors in this category include system operators, domain experts, AI
designers, users who interpret or incorporate the output of AI systems, product developers,
evaluators and auditors, compliance experts, organizational management, and members of
the research community.
Test, Evaluation, Verification, and Validation (TEVV) tasks are performed throughout
the AI lifecycle. They are carried out by AI actors who examine the AI system or its
components, or detect and remediate problems. Ideally, AI actors carrying out verification
Page 35
NIST AI 100-1 AI RMF 1.0
and validation tasks are distinct from those who perform test and evaluation actions. Tasks
can be incorporated into a phase as early as design, where tests are planned in accordance
with the design requirement.
• TEVV tasks for design, planning, and data may center on internal and external vali-
dation of assumptions for system design, data collection, and measurements relative
to the intended context of deployment or application.
• TEVV tasks for development (i.e., model building) include model validation and
assessment.
• TEVV tasks for deployment include system validation and integration in production,
with testing, and recalibration for systems and process integration, user experience,
and compliance with existing legal, regulatory, and ethical specifications.
• TEVV tasks for operations involve ongoing monitoring for periodic updates, testing,
and subject matter expert (SME) recalibration of models, the tracking of incidents
or errors reported and their management, the detection of emergent properties and
related impacts, and processes for redress and response.
Human Factors tasks and activities are found throughout the dimensions of the AI life-
cycle. They include human-centered design practices and methodologies, promoting the
active involvement of end users and other interested parties and relevant AI actors, incor-
porating context-specific norms and values in system design, evaluating and adapting end
user experiences, and broad integration of humans and human dynamics in all phases of the
AI lifecycle. Human factors professionals provide multidisciplinary skills and perspectives
to understand context of use, inform interdisciplinary and demographic diversity, engage
in consultative processes, design and evaluate user experience, perform human-centered
evaluation and testing, and inform impact assessments.
Domain Expert tasks involve input from multidisciplinary practitioners or scholars who
provide knowledge or expertise in – and about – an industry sector, economic sector, con-
text, or application area where an AI system is being used. AI actors who are domain
experts can provide essential guidance for AI system design and development, and inter-
pret outputs in support of work performed by TEVV and AI impact assessment teams.
AI Impact Assessment tasks include assessing and evaluating requirements for AI system
accountability, combating harmful bias, examining impacts of AI systems, product safety,
liability, and security, among others. AI actors such as impact assessors and evaluators
provide technical, human factor, socio-cultural, and legal expertise.
Procurement tasks are conducted by AI actors with financial, legal, or policy management
authority for acquisition of AI models, products, or services from a third-party developer,
vendor, or contractor.
Governance and Oversight tasks are assumed by AI actors with management, fiduciary,
and legal authority and responsibility for the organization in which an AI system is de-
Page 36
NIST AI 100-1 AI RMF 1.0
signed, developed, and/or deployed. Key AI actors responsible for AI governance include
organizational management, senior leadership, and the Board of Directors. These actors
are parties that are concerned with the impact and sustainability of the organization as a
whole.
Additional AI Actors
Third-party entities include providers, developers, vendors, and evaluators of data, al-
gorithms, models, and/or systems and related services for another organization or the or-
ganization’s customers or clients. Third-party entities are responsible for AI design and
development tasks, in whole or in part. By definition, they are external to the design, devel-
opment, or deployment team of the organization that acquires its technologies or services.
The technologies acquired from third-party entities may be complex or opaque, and risk
tolerances may not align with the deploying or operating organization.
End users of an AI system are the individuals or groups that use the system for specific
purposes. These individuals or groups interact with an AI system in a specific context. End
users can range in competency from AI experts to first-time technology end users.
Affected individuals/communities encompass all individuals, groups, communities, or
organizations directly or indirectly affected by AI systems or decisions based on the output
of AI systems. These individuals do not necessarily interact with the deployed system or
application.
Other AI actors may provide formal or quasi-formal norms or guidance for specifying
and managing AI risks. They can include trade associations, standards developing or-
ganizations, advocacy groups, researchers, environmental groups, and civil society
organizations.
The general public is most likely to directly experience positive and negative impacts of
AI technologies. They may provide the motivation for actions taken by the AI actors. This
group can include individuals, communities, and consumers associated with the context in
which an AI system is developed or deployed.
Page 37
NIST AI 100-1 AI RMF 1.0
Appendix B:
How AI Risks Differ from Traditional Software Risks
As with traditional software, risks from AI-based technology can be bigger than an en-
terprise, span organizations, and lead to societal impacts. AI systems also bring a set of
risks that are not comprehensively addressed by current risk frameworks and approaches.
Some AI system features that present risks also can be beneficial. For example, pre-trained
models and transfer learning can advance research and increase accuracy and resilience
when compared to other models and approaches. Identifying contextual factors in the MAP
function will assist AI actors in determining the level of risk and potential management
efforts.
Compared to traditional software, AI-specific risks that are new or increased include the
following:
• The data used for building an AI system may not be a true or appropriate representa-
tion of the context or intended use of the AI system, and the ground truth may either
not exist or not be available. Additionally, harmful bias and other data quality issues
can affect AI system trustworthiness, which could lead to negative impacts.
• AI system dependency and reliance on data for training tasks, combined with in-
creased volume and complexity typically associated with such data.
• Intentional or unintentional changes during training may fundamentally alter AI sys-
tem performance.
• Datasets used to train AI systems may become detached from their original and in-
tended context or may become stale or outdated relative to deployment context.
• AI system scale and complexity (many systems contain billions or even trillions of
decision points) housed within more traditional software applications.
• Use of pre-trained models that can advance research and improve performance can
also increase levels of statistical uncertainty and cause issues with bias management,
scientific validity, and reproducibility.
• Higher degree of difficulty in predicting failure modes for emergent properties of
large-scale pre-trained models.
• Privacy risk due to enhanced data aggregation capability for AI systems.
• AI systems may require more frequent maintenance and triggers for conducting cor-
rective maintenance due to data, model, or concept drift.
• Increased opacity and concerns about reproducibility.
• Underdeveloped software testing standards and inability to document AI-based prac-
tices to the standard expected of traditionally engineered software for all but the
simplest of cases.
• Difficulty in performing regular AI-based software testing, or determining what to
test, since AI systems are not subject to the same controls as traditional code devel-
opment.
Page 38
NIST AI 100-1 AI RMF 1.0
• Computational costs for developing AI systems and their impact on the environment
and planet.
• Inability to predict or detect the side effects of AI-based systems beyond statistical
measures.
Privacy and cybersecurity risk management considerations and approaches are applicable
in the design, development, deployment, evaluation, and use of AI systems. Privacy and
cybersecurity risks are also considered as part of broader enterprise risk management con-
siderations, which may incorporate AI risks. As part of the effort to address AI trustworthi-
ness characteristics such as “Secure and Resilient” and “Privacy-Enhanced,” organizations
may consider leveraging available standards and guidance that provide broad guidance to
organizations to reduce security and privacy risks, such as, but not limited to, the NIST Cy-
bersecurity Framework, the NIST Privacy Framework, the NIST Risk Management Frame-
work, and the Secure Software Development Framework. These frameworks have some
features in common with the AI RMF. Like most risk management approaches, they are
outcome-based rather than prescriptive and are often structured around a Core set of func-
tions, categories, and subcategories. While there are significant differences between these
frameworks based on the domain addressed – and because AI risk management calls for
addressing many other types of risks – frameworks like those mentioned above may inform
security and privacy considerations in the MAP, MEASURE, and MANAGE functions of the
AI RMF.
At the same time, guidance available before publication of this AI RMF does not compre-
hensively address many AI system risks. For example, existing frameworks and guidance
are unable to:
• adequately manage the problem of harmful bias in AI systems;
• confront the challenging risks related to generative AI;
• comprehensively address security concerns related to evasion, model extraction, mem-
bership inference, availability, or other machine learning attacks;
• account for the complex attack surface of AI systems or other security abuses enabled
by AI systems; and
• consider risks associated with third-party AI technologies, transfer learning, and off-
label use where AI systems may be trained for decision-making outside an organiza-
tion’s security controls or trained in one domain and then “fine-tuned” for another.
Both AI and traditional software technologies and systems are subject to rapid innovation.
Technology advances should be monitored and deployed to take advantage of those devel-
opments and work towards a
