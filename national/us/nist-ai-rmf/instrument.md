# United States NIST Artificial Intelligence Risk Management Framework (AI RMF 1.0 & GenAI Profile)

- **Stage**: NIST AI 600-1 Generative AI Profile (`nist_ai_600_1_genai`)
- **Document Symbol**: `NIST AI 600-1`
- **Date**: `2024-07-26`
- **Institutional Author**: `National Institute of Standards and Technology (NIST) <ai-rmf@nist.gov>`
- **Source**: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf

> Release of the NIST AI RMF Generative Artificial Intelligence Profile (NIST AI 600-1) pursuant to Executive Order 14110, adding 12 specific GenAI risk categories (CBRN capabilities, confabulation, dangerous/violent recommendations, data privacy, environmental impacts, information integrity, intellectual property, value chain security) and over 200 suggested actions across GOVERN, MAP, MEASURE, and MANAGE.

## Preamble & Recitals

(1) The NIST AI RMF Generative Artificial Intelligence Profile (NIST AI 600-1, July 2024) is a cross-sectoral companion resource to the AI RMF 1.0 (NIST AI 100-1) developed pursuant to Executive Order 14110 to help organizations identify and manage unique risks posed by Generative AI foundation models and downstream deployments.

## Enacting Terms (Articles)

### Article 1 — Core Function 1 — GOVERN (GV) with Generative AI Extensions

1. GOVERN 1: Policies, processes, procedures, and practices across the organization related to the mapping, measuring, and managing of AI and Generative AI risks are in place, transparent, and implemented effectively.
(a) GOVERN 1.1 (GenAI): Establish policies for acceptable use of Generative AI, compliance with intellectual property and copyright law, data privacy, and content provenance/watermarking standards.
(b) GOVERN 1.3 (GenAI): Establish risk-tiering policies specifically addressing high-severity Generative AI risks, including CBRN weapons information, offensive cyber capabilities, confabulation/hallucinations, and synthetic CSAM/NCII.
(c) GOVERN 6.1 (GenAI): Verify third-party foundation model and training dataset provenance, licensing terms, and supply chain vulnerability disclosures before integration.

### Article 2 — Core Function 2 — MAP (MP) with Generative AI Extensions

1. MAP 1: Context is established and understood across the AI and Generative AI lifecycle.
(a) MAP 1.1 (GenAI): Document intended and out-of-scope uses of foundation models and fine-tuned Generative AI applications, explicitly assessing dual-use risks and downstream adaptability.
(b) MAP 3.4 (GenAI): Map human-AI configuration risks, including automation bias, anthropomorphism, and over-reliance on fluent or persuasive Generative AI outputs.
(c) MAP 5.1 (GenAI): Assess likelihood and magnitude of the 12 primary Generative AI risk categories:
(1) CBRN information or capabilities;
(2) Confabulation;
(3) Dangerous, violent, or hateful recommendations;
(4) Data privacy;
(5) Environmental impacts;
(6) Harmful bias and homogenization;
(7) Human-AI configuration;
(8) Information integrity;
(9) Information security;
(10) Intellectual property;
(11) Obscene, degrading, and/or abusive content; and (12) Value chain and component integration.

### Article 3 — Core Function 3 — MEASURE (MS) with Generative AI Extensions

1. MEASURE 1: Appropriate methods, benchmarks, and structured red-teaming are identified and applied to Generative AI systems.
(a) MEASURE 2.5 (GenAI): Evaluate confabulation rates, grounding fidelity (e.g., in Retrieval-Augmented Generation), and calibration across domains.
(b) MEASURE 2.6 (GenAI): Conduct structured adversarial red-teaming for CBRN uplift, autonomous cyber-exploitation capabilities, and jailbreak robustness prior to model release.
(c) MEASURE 2.7 (GenAI): Evaluate prompt injection, indirect prompt injection, training data extraction, and membership inference vulnerabilities.
(d) MEASURE 2.11 (GenAI): Measure representational harms, stereotyping, and output homogenization/mode collapse across languages and demographic groups.

### Article 4 — Core Function 4 — MANAGE (MG) with Generative AI Extensions

1. MANAGE 1: AI and Generative AI risks based on assessments from MAP and MEASURE are prioritized, responded to, and managed.
(a) MANAGE 2.2 (GenAI): Implement input/output guardrails, cryptographic provenance (such as C2PA metadata), and synthetic media watermarking to preserve information integrity.
(b) MANAGE 2.4 (GenAI): Establish clear kill-switch, rollback, and model weight revocation procedures if critical safety thresholds or systemic risks are breached post-deployment.
(c) MANAGE 4.1 (GenAI): Maintain post-deployment incident reporting channels for emergent capabilities, jailbreaks, and downstream misuse.
