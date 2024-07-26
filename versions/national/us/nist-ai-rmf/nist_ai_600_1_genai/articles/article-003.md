# Article 3 — Core Function 3 — MEASURE (nist_ai_600_1_genai)

- **Instrument**: US Federal AI & NIST RMF
- **Stage**: NIST AI 600-1 Generative AI Profile (`2024-07-26`)
- **Document Symbol**: `NIST AI 600-1`
- **Akoma Ntoso eId**: `nist_measure`
- **Provenance Mode**: `full_primary_pdf`
- **Institutional Author**: National Institute of Standards and Technology (NIST) `<ai-rmf@nist.gov>`

MEASURE 1.1: Approaches and metrics for measurement of AI risks enumerated during the MAP function are selected for
implementation starting with the most signiﬁcant AI risks. The risks or trustworthiness characteristics that will not – or cannot – be
measured are properly documented.
Action ID Suggested Action GAI Risks
MS-1.1-001 Employ methods to trace the origin and modiﬁcations of digital content. Information Integrity
MS-1.1-002
Integrate tools designed to analyze content provenance and detect data
anomalies, verify the authenticity of digital signatures, and identify patterns
associated with misinformation or manipulation.
Information Integrity
MS-1.1-003
Disaggregate evaluation metrics by demographic factors to identify any
discrepancies in how content provenance mechanisms work across diverse
populations.
Information Integrity; Harmful
Bias and Homogenization
MS-1.1-004 Develop a suite of metrics to evaluate structured public feedback exercises informed by representative AI Actors. Human-AI Conﬁguration; Harmful Bias and Homogenization; CBRN Information or Capabilities
MS-1.1-005
Evaluate novel methods and technologies for the measurement of GAI-related
risks including in content provenance, oﬀensive cy ber, and CBRN, while
maintaining the models’ ability to produce valid, reliable, and factually accurate
outputs.
Information Integrity; CBRN
Information or Capabilities;
Obscene, Degrading, and/or
Abusive Content
29
MS-1.1-006
Implement continuous monitoring of GAI system impacts to identify whether GAI
outputs are equitable across various sub-populations. Seek active and direct
feedback from aﬀected communities via structured feedback mechanisms or red-
teaming to monitor and improve outputs.
Harmful Bias and Homogenization
MS-1.1-007
Evaluate the quality and integrity of data used in training and the provenance of
AI-generated content, for example by employing techniques like chaos
engineering and seeking stakeholder feedback.
Information Integrity
MS-1.1-008
Deﬁne use cases, contexts of use, capabilities, and negative impacts where
structured human feedback exercises, e.g., GAI red-teaming, would be most
beneﬁcial for GAI risk measurement and management based on the context of
use.
Harmful Bias and
Homogenization; CBRN
Information or Capabilities
MS-1.1-009
Track and document risks or opportunities related to all GAI risks that cannot be
measured quantitatively, including explanations as to why some risks cannot be
measured (e.g., due to technological limitations, resource constraints, or
trustworthy considerations). Include unmeasured risks in marginal risks.
Information Integrity
AI Actor Tasks: AI Development, Domain Experts, TEVV
MEASURE 1.3: Internal experts who did not serve as front-line developers for the system and/or independent assessors are
involved in regular assessments and updates. Domain experts, users, AI Actors external to the team that developed or deployed the
AI system, and aﬀected communities are consulted in support of assessments as necessary per organizational risk tolerance.
Action ID Suggested Action GAI Risks
MS-1.3-001
Deﬁne relevant groups of interest (e.g., demographic groups, subject matter
experts, experience with GAI technology) within the context of use as part of
plans for gathering structured public feedback.
Human-AI Conﬁguration; Harmful
Bias and Homogenization; CBRN
Information or Capabilities
MS-1.3-002
Engage in internal and external evaluations, GAI red-teaming, impact
assessments, or other structured human feedback exercises in consultation
with representative AI Actors with expertise and familiarity in the context of
use, and/or who are representative of the populations associated with the
context of use.
Human-AI Conﬁguration; Harmful
Bias and Homogenization; CBRN
Information or Capabilities
MS-1.3-003 Verify those conducting structured human feedback exercises are not directly involved in system development tasks for the same GAI model. Human-AI Conﬁguration; Data Privacy
AI Actor Tasks: AI Deployment, AI Development, AI Impact Assessment, Aﬀected Individuals and Communities, Domain Experts,
End-Users, Operation and Monitoring, TEVV
30
MEASURE 2.2: Evaluations involving human subjects meet applicable requirements (including human subject protection) and are
representative of the relevant population.
Action ID Suggested Action GAI Risks
MS-2.2-001 Assess and manage statistical biases related to GAI content provenance through techniques such as re-sampling, re-weighting, or adversarial training. Information Integrity; Information Security; Harmful Bias and Homogenization
MS-2.2-002
Document how content provenance data is tracked and how that data interacts
with privacy and security. Consider: Anonymizing data to protect the privacy of
human subjects; Leveraging privacy output ﬁlters; Removing any personally
identiﬁable information (PII) to prevent potential harm or misuse.
Data Privacy; Human AI
Conﬁguration; Information
Integrity; Information Security;
Dangerous, Violent, or Hateful
Content
MS-2.2-003 Provide human subjects with options to withdraw participation or revoke their consent for present or future use of their data in GAI applications. Data Privacy; Human-AI Conﬁguration; Information Integrity
MS-2.2-004
Use techniques such as anonymization, diﬀerential privacy or other privacy-
enhancing technologies to minimize the risks associated with linking AI-generated
content back to individual human subjects.
Data Privacy; Human-AI
Conﬁguration
AI Actor Tasks: AI Development, Human Factors, TEVV
MEASURE 2.3: AI system performance or assurance criteria are measured qualitatively or quantitatively and demonstrated for
conditions similar to deployment setting(s). Measures are documented.
Action ID Suggested Action GAI Risks
MS-2.3-001 Consider baseline model performance on suites of benchmarks when selecting a model for ﬁne tuning or enhancement with retrieval-augmented generation. Information Security; Confabulation
MS-2.3-002 Evaluate claims of model capabilities using empirically validated methods. Confabulation; Information Security
MS-2.3-003 Share results of pre-deployment testing with relevant GAI Actors, such as those with system release approval authority. Human-AI Conﬁguration
31
MS-2.3-004
Utilize a purpose-built testing environment such as NIST Dioptra to empirically
evaluate GAI trustworthy characteristics.
CBRN Information or Capabilities;
Data Privacy; Confabulation;
Information Integrity; Information
Security; Dangerous, Violent, or
Hateful Content; Harmful Bias and
Homogenization
AI Actor Tasks: AI Deployment, TEVV
MEASURE 2.5: The AI system to be deployed is demonstrated to be valid and reliable. Limitations of the generalizability beyond the
conditions under which the technology was developed are documented.
Action ID Suggested Action Risks
MS-2.5-001 Avoid extrapolating GAI system performance or capabilities from narrow, non- systematic, and anecdotal assessments. Human-AI Conﬁguration; Confabulation
MS-2.5-002
Document the extent to which human domain knowledge is employed to
improve GAI system performance, via, e.g., RLHF, ﬁne-tuning, retrieval-
augmented generation, content moderation, business rules.
Human-AI Conﬁguration
MS-2.5-003 Review and verify sources and citations in GAI system outputs during pre- deployment risk measurement and ongoing monitoring activities. Confabulation
MS-2.5-004 Track and document instances of anthropomorphization (e.g., human images, mentions of human feelings, cyborg imagery or motifs) in GAI system interfaces. Human-AI Conﬁguration
MS-2.5-005 Verify GAI system training data and TEVV data provenance, and that ﬁne-tuning or retrieval-augmented generation data is grounded. Information Integrity
MS-2.5-006
Regularly review security and safety guardrails, especially if the GAI system is
being operated in novel circumstances. This includes reviewing reasons why the
GAI system was initially assessed as being safe to deploy.
Information Security; Dangerous,
Violent, or Hateful Content
AI Actor Tasks: Domain Experts, TEVV
32
MEASURE 2.6: The AI system is evaluated regularly for safety risks – as identiﬁed in the MAP function. The AI system to be
deployed is demonstrated to be safe, its residual negative risk does not exceed the risk tolerance, and it can fail safely, particularly if
made to operate beyond its knowledge limits. Safety metrics reﬂect system reliability and robustness, real-time monitoring, and
response times for AI system failures.
Action ID Suggested Action GAI Risks
MS-2.6-001
Assess adverse impacts, including health and wellbeing impacts for value chain
or other AI Actors that are exposed to sexually explicit, oﬀensive, or violent
information during GAI training and maintenance.
Human-AI Conﬁguration; Obscene,
Degrading, and/or Abusive
Content; Value Chain and
Component Integration;
Dangerous, Violent, or Hateful
Content
MS-2.6-002
Assess existence or levels of harmful bias, intellectual property infringement,
data privacy violations, obscenity, extremism, violence, or CBRN information in
system training data.
Data Privacy; Intellectual Property;
Obscene, Degrading, and/or
Abusive Content; Harmful Bias and
Homogenization; Dangerous,
Violent, or Hateful Content; CBRN
Information or Capabilities
MS-2.6-003 Re-evaluate safety features of ﬁne-tuned models when the negative risk exceeds organizational risk tolerance. Dangerous, Violent, or Hateful Content
MS-2.6-004 Review GAI system outputs for validity and safety: Review generated code to assess risks that may arise from unreliable downstream decision-making. Value Chain and Component Integration; Dangerous, Violent, or Hateful Content
MS-2.6-005
Verify that GAI system architecture can monitor outputs and performance, and
handle, recover from, and repair errors when security anomalies, threats and
impacts are detected.
Confabulation; Information
Integrity; Information Security
MS-2.6-006
Verify that systems properly handle queries that may give rise to inappropriate,
malicious, or illegal usage, including facilitating manipulation, extortion, targeted
impersonation, cyber-attacks, and weapons creation.
CBRN Information or Capabilities;
Information Security
MS-2.6-007 Regularly evaluate GAI system vulnerabilities to possible circumvention of safety measures. CBRN Information or Capabilities; Information Security
AI Actor Tasks: AI Deployment, AI Impact Assessment, Domain Experts, Operation and Monitoring, TEVV
33
MEASURE 2.7: AI system security and resilience – as identiﬁed in the MAP function – are evaluated and documented.
Action ID Suggested Action GAI Risks
MS-2.7-001
Apply established security measures to: Assess likelihood and magnitude of
vulnerabilities and threats such as backdoors, compromised dependencies, data
breaches, eavesdropping, man-in-the-middle attacks, reverse engineering,
autonomous agents, model theft or exposure of model weights, AI inference,
bypass, extraction, and other baseline security concerns.
Data Privacy; Information Integrity;
Information Security; Value Chain
and Component Integration
MS-2.7-002
Benchmark GAI system security and resilience related to content provenance
against industry standards and best practices. Compare GAI system security
features and content provenance methods against industry state-of-the-art.
Information Integrity; Information
Security
MS-2.7-003
Conduct user surveys to gather user satisfaction with the AI-generated content
and user perceptions of content authenticity. Analyze user feedback to identify
concerns and/or current literacy levels related to content provenance and
understanding of labels on content.
Human-AI Conﬁguration;
Information Integrity
MS-2.7-004
Identify metrics that reﬂect the eﬀectiveness of security measures, such as data
provenance, the number of unauthorized access attempts, inference, bypass,
extraction, penetrations, or provenance veriﬁcation.
Information Integrity; Information
Security
MS-2.7-005
Measure reliability of content authentication methods, such as watermarking,
cryptographic signatures, digital ﬁngerprints, as well as access controls,
conformity assessment, and model integrity veriﬁcation, which can help support
the eﬀective implementation of content provenance techniques. Evaluate the
rate of false positives and false negatives in content provenance, as well as true
positives and true negatives for veriﬁcation.
Information Integrity
MS-2.7-006
Measure the rate at which recommendations from security checks and incidents
are implemented. Assess how quickly the AI system can adapt and improve
based on lessons learned from security incidents and feedback.
Information Integrity; Information
Security
MS-2.7-007
Perform AI red-teaming to assess resilience against: Abuse to facilitate attacks on
other systems (e.g., malicious code generation, enhanced phishing content), GAI
attacks (e.g., prompt injection), ML attacks (e.g., adversarial examples/prompts,
data poisoning, membership inference, model extraction, sponge examples).
Information Security; Harmful Bias
and Homogenization; Dangerous,
Violent, or Hateful Content
MS-2.7-008 Verify ﬁne-tuning does not compromise safety and security controls.
Information Integrity; Information
Security; Dangerous, Violent, or
Hateful Content
34
MS-2.7-009 Regularly assess and verify that security measures remain eﬀective and have not been compromised. Information Security
AI Actor Tasks: AI Deployment, AI Impact Assessment, Domain Experts, Operation and Monitoring, TEVV
MEASURE 2.8: Risks associated with transparency and accountability – as identiﬁed in the MAP function – are examined and
documented.
Action ID Suggested Action GAI Risks
MS-2.8-001
Compile statistics on actual policy violations, take-down requests, and intellectual
property infringement for organizational GAI systems: Analyze transparency
reports across demographic groups, languages groups.
Intellectual Property; Harmful Bias
and Homogenization
MS-2.8-002 Document the instructions given to data annotators or AI red-teamers. Human-AI Conﬁguration
MS-2.8-003
Use digital content transparency solutions to enable the documentation of each
instance where content is generated, modiﬁed, or shared to provide a tamper-
proof history of the content, promote transparency, and enable traceability.
Robust version control systems can also be applied to track changes across the AI
lifecycle over time.
Information Integrity
MS-2.8-004 Verify adequacy of GAI system user instructions through user testing. Human-AI Conﬁguration
AI Actor Tasks: AI Deployment, AI Impact Assessment, Domain Experts, Operation and Monitoring, TEVV
35
MEASURE 2.9: The AI model is explained, validated, and documented, and AI system output is interpreted within its context – as
identiﬁed in the MAP function – to inform responsible use and governance.
Action ID Suggested Action GAI Risks
MS-2.9-001
Apply and document ML explanation results such as: Analysis of embeddings,
Counterfactual prompts, Gradient-based attributions, Model
compression/surrogate models, Occlusion/term reduction.
Confabulation
MS-2.9-002
Document GAI model details including: Proposed use and organizational value;
Assumptions and limitations, Data collection methodologies; Data provenance;
Data quality; Model architecture (e.g., convolutional neural network,
transformers, etc.); Optimization objectives; Training algorithms; RLHF
approaches; Fine-tuning or retrieval-augmented generation approaches;
Evaluation data; Ethical considerations; Legal and regulatory requirements.
Information Integrity; Harmful Bias
and Homogenization
AI Actor Tasks: AI Deployment, AI Impact Assessment, Domain Experts, End-Users, Operation and Monitoring, TEVV
MEASURE 2.10: Privacy risk of the AI system – as identiﬁed in the MAP function – is examined and documented.
Action ID Suggested Action GAI Risks
MS-2.10-001
Conduct AI red-teaming to assess issues such as: Outputting of training data
samples, and subsequent reverse engineering, model extraction, and
membership inference risks; Revealing biometric, conﬁdential, copyrighted,
licensed, patented, personal, proprietary, sensitive, or trade-marked information;
Tracking or revealing location information of users or members of training
datasets.
Human-AI Conﬁguration;
Information Integrity; Intellectual
Property
MS-2.10-002
Engage directly with end-users and other stakeholders to understand their
expectations and concerns regarding content provenance. Use this feedback to
guide the design of provenance data-tracking techniques.
Human-AI Conﬁguration;
Information Integrity
MS-2.10-003 Verify deduplication of GAI training data samples, particularly regarding synthetic data. Harmful Bias and Homogenization
AI Actor Tasks: AI Deployment, AI Impact Assessment, Domain Experts, End-Users, Operation and Monitoring, TEVV
36
MEASURE 2.11: Fairness and bias – as identiﬁed in the MAP function – are evaluated and results are documented.
Action ID Suggested Action GAI Risks
MS-2.11-001
Apply use-case appropriate benchmarks (e.g., Bias Benchmark Questions, Real
Hateful or Harmful Prompts, Winogender Schemas15) to quantify systemic bias,
stereotyping, denigration, and hateful content in GAI system outputs;
Document assumptions and limitations of benchmarks, including any actual or
possible training/test data cross contamination, relative to in-context
deployment environment.
Harmful Bias and Homogenization
MS-2.11-002
Conduct fairness assessments to measure systemic bias. Measure GAI system
performance across demographic groups and subgroups, addressing both
quality of service and any allocation of services and resources. Quantify harms
using: ﬁeld testing with sub-group populations to determine likelihood of
exposure to generated content exhibiting harmful bias, AI red-teaming with
counterfactual and low-context (e.g., “leader,” “bad guys”) prompts. For ML
pipelines or business processes with categorical or numeric outcomes that rely
on GAI, apply general fairn
