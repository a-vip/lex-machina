# Article 4 — Core Function 4 — MANAGE (nist_ai_600_1_genai)

- **Instrument**: US Federal AI & NIST RMF
- **Stage**: NIST AI 600-1 Generative AI Profile (`2024-07-26`)
- **Document Symbol**: `NIST AI 600-1`
- **Akoma Ntoso eId**: `nist_manage`
- **Provenance Mode**: `full_primary_pdf`
- **Institutional Author**: National Institute of Standards and Technology (NIST) `<ai-rmf@nist.gov>`

MANAGE 1.3: Responses to the AI risks deemed high priority, as identiﬁed by the MAP function, are developed, planned, and
documented. Risk response options can include mitigating, transferring, avoiding, or accepting.
Action ID Suggested Action GAI Risks
MG-1.3-001
Document trade-oﬀs, decision processes, and relevant measurement and
feedback results for risks that do not surpass organizational risk tolerance, for
example, in the context of model release: Consider diﬀerent approaches for
model release, for example, leveraging a staged release approach. Consider
release approaches in the context of the model and its projected use cases.
Mitigate, transfer, or avoid risks that surpass organizational risk tolerances.
Information Security
MG-1.3-002
Monitor the robustness and eﬀectiveness of risk controls and mitigation plans
(e.g., via red-teaming, ﬁeld testing, participatory engagements, performance
assessments, user feedback mechanisms).
Human-AI Conﬁguration
AI Actor Tasks: AI Development, AI Deployment, AI Impact Assessment, Operation and Monitoring
MANAGE 2.2: Mechanisms are in place and applied to sustain the value of deployed AI systems.
Action ID Suggested Action GAI Risks
MG-2.2-001
Compare GAI system outputs against pre-deﬁned organization risk tolerance,
guidelines, and principles, and review and test AI-generated content against
these guidelines.
CBRN Information or Capabilities;
Obscene, Degrading, and/or
Abusive Content; Harmful Bias and
Homogenization; Dangerous,
Violent, or Hateful Content
MG-2.2-002 Document training data sources to trace the origin and provenance of AI- generated content. Information Integrity
MG-2.2-003
Evaluate feedback loops between GAI system content provenance and human
reviewers, and update where needed. Implement real-time monitoring systems
to aﬃrm that content provenance protocols remain eﬀective.
Information Integrity
MG-2.2-004
Evaluate GAI content and data for representational biases and employ
techniques such as re-sampling, re-ranking, or adversarial training to mitigate
biases in the generated content.
Information Security; Harmful Bias
and Homogenization
MG-2.2-005 Engage in due diligence to analyze GAI output for harmful content, potential misinformation, and CBRN-related or NCII content.
CBRN Information or Capabilities;
Obscene, Degrading, and/or
Abusive Content; Harmful Bias and
Homogenization; Dangerous,
Violent, or Hateful Content
41
MG-2.2-006 Use feedback from internal and external AI Actors, users, individuals, and communities, to assess impact of AI-generated content. Human-AI Conﬁguration
MG-2.2-007 Use real-time auditing tools where they can be demonstrated to aid in the tracking and validation of the lineage and authenticity of AI-generated data. Information Integrity
MG-2.2-008
Use structured feedback mechanisms to solicit and capture user input about AI-
generated content to detect subtle shifts in quality or alignment with
community and societal values.
Human-AI Conﬁguration; Harmful
Bias and Homogenization
MG-2.2-009
Consider opportunities to responsibly use synthetic data and other privacy
enhancing techniques in GAI development, where appropriate and applicable,
match the statistical properties of real-world data without disclosing personally
identiﬁable information or contributing to homogenization.
Data Privacy; Intellectual Property;
Information Integrity;
Confabulation; Harmful Bias and
Homogenization
AI Actor Tasks: AI Deployment, AI Impact Assessment, Governance and Oversight, Operation and Monitoring
MANAGE 2.3: Procedures are followed to respond to and recover from a previously unknown risk when it is identiﬁed.
Action ID Suggested Action GAI Risks
MG-2.3-001
Develop and update GAI system incident response and recovery plans and
procedures to address the following: Review and maintenance of policies and
procedures to account for newly encountered uses; Review and maintenance of
policies and procedures for detection of unanticipated uses; Verify response
and recovery plans account for the GAI system value chain; Verify response and
recovery plans are updated for and include necessary details to communicate
with downstream GAI system Actors: Points-of-Contact (POC), Contact
information, notiﬁcation format.
Value Chain and Component
Integration
AI Actor Tasks: AI Deployment, Operation and Monitoring
MANAGE 2.4: Mechanisms are in place and applied, and responsibilities are assigned and understood, to supersede, disengage, or
deactivate AI systems that demonstrate performance or outcomes inconsistent with intended use.
Action ID Suggested Action GAI Risks
MG-2.4-001
Establish and maintain communication plans to inform AI stakeholders as part of
the deactivation or disengagement process of a speciﬁc GAI system (including for
open-source models) or context of use, including reasons, workarounds, user
access removal, alternative processes, contact information, etc.
Human-AI Conﬁguration
42
MG-2.4-002
Establish and maintain procedures for escalating GAI system incidents to the
organizational risk management authority when speciﬁc criteria for deactivation
or disengagement is met for a particular context of use or for the GAI system as a
whole.
Information Security
MG-2.4-003
Establish and maintain procedures for the remediation of issues which trigger
incident response processes for the use of a GAI system, and provide stakeholders
timelines associated with the remediation plan.
Information Security
MG-2.4-004 Establish and regularly review speciﬁc criteria that warrants the deactivation of GAI systems in accordance with set risk tolerances and appetites. Information Security
AI Actor Tasks: AI Deployment, Governance and Oversight, Operation and Monitoring
MANAGE 3.1: AI risks and beneﬁts from third-party resources are regularly monitored, and risk controls are applied and
documented.
Action ID Suggested Action GAI Risks
MG-3.1-001
Apply organizational risk tolerances and controls (e.g., acquisition and
procurement processes; assessing personnel credentials and qualiﬁcations,
performing background checks; ﬁltering GAI input and outputs, grounding, ﬁne
tuning, retrieval-augmented generation) to third-party GAI resources: Apply
organizational risk tolerance to the utilization of third-party datasets and other
GAI resources; Apply organizational risk tolerances to ﬁne-tuned third-party
models; Apply organizational risk tolerance to existing third-party models
adapted to a new domain; Reassess risk measurements after ﬁne-tuning third-
party GAI models.
Value Chain and Component
Integration; Intellectual Property
MG-3.1-002
Test GAI system value chain risks (e.g., data poisoning, malware, other software
and hardware vulnerabilities; labor practices; data privacy and localization
compliance; geopolitical alignment).
Data Privacy; Information Security;
Value Chain and Component
Integration; Harmful Bias and
Homogenization
MG-3.1-003
Re-assess model risks after ﬁne-tuning or retrieval-augmented generation
implementation and for any third-party GAI models deployed for applications
and/or use cases that were not evaluated in initial testing.
Value Chain and Component
Integration
MG-3.1-004
Take reasonable measures to review training data for CBRN information, and
intellectual property, and where appropriate, remove it. Implement reasonable
measures to prevent, ﬂag, or take other action in response to outputs that
reproduce particular training data (e.g., plagiarized, trademarked, patented,
licensed content or trade secret material).
Intellectual Property; CBRN
Information or Capabilities
43
MG-3.1-005 Review various transparency artifacts (e.g., system cards and model cards) for third-party models. Information Integrity; Information Security; Value Chain and Component Integration
AI Actor Tasks: AI Deployment, Operation and Monitoring, Third-party entities
MANAGE 3.2: Pre-trained models which are used for development are monitored as part of AI system regular monitoring and
maintenance.
Action ID Suggested Action GAI Risks
MG-3.2-001
Apply explainable AI (XAI) techniques (e.g., analysis of embeddings, model
compression/distillation, gradient-based attributions, occlusion/term reduction,
counterfactual prompts, word clouds) as part of ongoing continuous
improvement processes to mitigate risks related to unexplainable GAI systems.
Harmful Bias and Homogenization
MG-3.2-002
Document how pre-trained models have been adapted (e.g., ﬁne-tuned, or
retrieval-augmented generation) for the speciﬁc generative task, including any
data augmentations, parameter adjustments, or other modiﬁcations. Access to
un-tuned (baseline) models supports debugging the relative inﬂuence of the pre-
trained weights compared to the ﬁne-tuned model weights or other system
updates.
Information Integrity; Data Privacy
MG-3.2-003
Document sources and types of training data and their origins, potential biases
present in the data related to the GAI application and its content provenance,
architecture, training process of the pre-trained model including information on
hyperparameters, training duration, and any ﬁne-tuning or retrieval-augmented
generation processes applied.
Information Integrity; Harmful Bias
and Homogenization; Intellectual
Property
MG-3.2-004 Evaluate user reported problematic content and integrate feedback into system updates. Human-AI Conﬁguration, Dangerous, Violent, or Hateful Content
MG-3.2-005
Implement content ﬁlters to prevent the generation of inappropriate, harmful,
false, illegal, or violent content related to the GAI application, including for CSAM
and NCII. These ﬁlters can be rule-based or leverage additional machine learning
models to ﬂag problematic inputs and outputs.
Information Integrity; Harmful Bias
and Homogenization; Dangerous,
Violent, or Hateful Content;
Obscene, Degrading, and/or
Abusive Content
MG-3.2-006
Implement real-time monitoring processes for analyzing generated content
performance and trustworthiness characteristics related to content provenance
to identify deviations from the desired standards and trigger alerts for human
intervention.
Information Integrity
44
MG-3.2-007
Leverage feedback and recommendations from organizational boards or
committees related to the deployment of GAI applications and content
provenance when using third-party pre-trained models.
Information Integrity; Value Chain
and Component Integration
MG-3.2-008
Use human moderation systems where appropriate to review generated content
in accordance with human-AI conﬁguration policies established in the Govern
function, aligned with socio-cultural norms in the context of use, and for settings
where AI models are demonstrated to perform poorly.
Human-AI Conﬁguration
MG-3.2-009
Use organizational risk tolerance to evaluate acceptable risks and performance
metrics and decommission or retrain pre-trained models that perform outside of
deﬁned limits.
CBRN Information or Capabilities;
Confabulation
AI Actor Tasks: AI Deployment, Operation and Monitoring, Third-party entities
MANAGE 4.1: Post-deployment AI system monitoring plans are implemented, including mechanisms for capturing and evaluating
input from users and other relevant AI Actors, appeal and override, decommissioning, incident response, recovery, and change
management.
Action ID Suggested Action GAI Risks
MG-4.1-001
Collaborate with external researchers, industry experts, and community
representatives to maintain awareness of emerging best practices and
technologies in measuring and managing identiﬁed risks.
Information Integrity; Harmful Bias
and Homogenization
MG-4.1-002
Establish, maintain, and evaluate eﬀectiveness of organizational processes and
procedures for post-deployment monitoring of GAI systems, particularly for
potential confabulation, CBRN, or cyber risks.
CBRN Information or Capabilities;
Confabulation; Information
Security
MG-4.1-003
Evaluate the use of sentiment analysis to gauge user sentiment regarding GAI
content performance and impact, and work in collaboration with AI Actors
experienced in user research and experience.
Human-AI Conﬁguration
MG-4.1-004 Implement active learning techniques to identify instances where the model fails or produces unexpected outputs. Confabulation
MG-4.1-005
Share transparency reports with internal and external stakeholders that detail
steps taken to update the GAI system to enhance transparency and
accountability.
Human-AI Conﬁguration; Harmful
Bias and Homogenization
MG-4.1-006
Track dataset modiﬁcations for provenance by monitoring data deletions,
rectiﬁcation requests, and other changes that may impact the veriﬁability of
content origins.
Information Integrity
45
MG-4.1-007
Verify that AI Actors responsible for monitoring reported issues can eﬀectively
evaluate GAI system performance including the application of content
provenance data tracking techniques, and promptly escalate issues for response.
Human-AI Conﬁguration;
Information Integrity
AI Actor Tasks: AI Deployment, Aﬀected Individuals and Communities, Domain Experts, End-Users, Human Factors, Operation and
Monitoring
MANAGE 4.2: Measurable activities for continual improvements are integrated into AI system updates and include regular
engagement with interested parties, including relevant AI Actors.
Action ID Suggested Action GAI Risks
MG-4.2-001 Conduct regular monitoring of GAI systems and publish reports detailing the performance, feedback received, and improvements made. Harmful Bias and Homogenization
MG-4.2-002
Practice and follow incident response plans for addressing the generation of
inappropriate or harmful content and adapt processes based on ﬁndings to
prevent future occurrences. Conduct post-mortem analyses of incidents with
relevant AI Actors, to understand the root causes and implement preventive
measures.
Human-AI Conﬁguration;
Dangerous, Violent, or Hateful
Content
MG-4.2-003 Use visualizations or other methods to represent GAI model behavior to ease non-technical stakeholders understanding of GAI system functionality. Human-AI Conﬁguration
AI Actor Tasks: AI Deployment, AI Design, AI Development, Aﬀected Individuals and Communities, End-Users, Operation and
Monitoring, TEVV
MANAGE 4.3: Incidents and errors are communicated to relevant AI Actors, including aﬀected communities. Processes for tracking,
responding to, and recovering from incidents and errors are followed and documented.
Action ID Suggested Action GAI Risks
MG-4.3-001
Conduct after-action assessments for GAI system incidents to verify incident
response and recovery processes are followed and eﬀective, including to follow
procedures for communicating incidents to relevant AI Actors and where
applicable, relevant legal and regulatory bodies.
Information Security
MG-4.3-002 Establish and maintain policies and procedures to record and track GAI system reported errors, near-misses, and negative impacts. Confabulation; Information Integrity
46
MG-4.3-003
Report GAI incidents in compliance with legal and regulatory requirements (e.g.,
HIPAA breach reporting, e.g., OCR (2023) or NHTSA (2022) autonomous vehicle
crash reporting requirements.
Information Security; Data Privacy
AI Actor Tasks: AI Deployment, Aﬀected Individuals and Communities, Domain Experts, End-Users, Human Factors, Operation and
Monitoring
47
Appendix A. Primary GAI Considerations
The following primary considerations were derived as overarching themes from the GAI PWG
consultation process. These considerations (Governance, Pre-Deployment Testing, Content Provenance,
and Incident Disclosure) are relevant for voluntary use by any organization designing, developing, and
using GAI and also inform the Actions to Manage GAI risks. Information included about the primary
considerations is not exhaustive, but highlights the most relevant topics derived from the GAI PWG.
Acknowledgments: These considerations could not have been surfaced without the helpful analysis and
contributions from the community and NIST staﬀ GAI PWG leads: George Awad, Luca Belli, Harold Booth,
Mat Heyman, Yooyoung Lee, Mark Pryzbocki, Reva Schwartz, Martin Stanley, and Kyra Yee.
A.1. Governance
A.1.1. Overview
Like any other technology system, governance principles and techniques can be used to manage risks
related to generative AI models, capabilities, and applications. Organizations may choose to apply their
existing risk tiering to GAI systems, or they may opt to revise or update AI system risk levels to address
these unique GAI risks. This section describes how organizational governance regimes may be re-
evaluated and adjusted for GAI contexts. It also addresses third-party considerations for governing across
the AI value chain.
A.1.2. Organizational Governance
GAI opportunities, risks and long-term performance characteristics are typically less well-understood
than non-generative AI tools and may be perceived and acted upon by humans in ways that vary greatly.
Accordingly, GAI may call for diﬀerent levels of oversight from AI Actors or diﬀerent human-AI
conﬁgurations in order to manage their risks eﬀectively. Organizations’ use of GAI systems may also
warrant additional human review, tracking and documentation, and greater management oversight.
AI technology can produce varied outputs in multiple modalities and present many classes of user
interfaces. This leads to a broader set of AI Actors interacting with GAI systems for widely diﬀering
applications and contexts of use. These can include data labeling and preparation, development of GAI
models, content moderation, code generation and review, text generation and editing, image and video
generation, summarization, search, and chat. These activities can take place within organizational
settings or in the public domain.
Organizations can restrict AI applications that cause harm, exceed stated risk tolerances, or that conﬂict
with their tolerances or values. Governance tools and protocols that are applied to other types of AI
systems can be applied to GAI systems. These plans and actions inc
