"""
National AI Regulatory & Risk Management Framework Fetcher.

Covers:
1. United States NIST AI Risk Management Framework 1.0 (NIST AI 100-1) ->
   NIST AI 600-1 Generative AI Profile.
2. People's Republic of China CAC Algorithmic Recommendation Provisions (2022) ->
   Deep Synthesis Provisions (2022) -> Interim Measures for Generative AI (2023).
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Any

try:
    import httpx
except ImportError:
    httpx = None


NATIONAL_PROVISIONS: dict[str, dict[str, Any]] = {
    "national-us-nist-ai-rmf::nist_ai_rmf_1_0": {
        "recitals": [
            {
                "number": "1",
                "text": "(1) The NIST Artificial Intelligence Risk Management Framework (AI RMF 1.0, NIST AI 100-1) is intended for voluntary use and to improve the ability to incorporate trustworthiness considerations into the design, development, use, and evaluation of AI products, services, and systems.",
            },
        ],
        "articles": [
            {
                "number": "1",
                "title": "Core Function 1 — GOVERN (GV)",
                "text": "1. GOVERN 1: Policies, processes, procedures, and practices across the organization related to the mapping, measuring, and managing of AI risks are in place, transparent, and implemented effectively.\n(a) GOVERN 1.1: Legal and regulatory requirements involving AI are understood, managed, and documented.\n(b) GOVERN 1.2: The characteristics of trustworthy AI (valid and reliable, safe, secure and resilient, accountable and transparent, explainable and interpretable, privacy-enhanced, and fair with harmful bias managed) are integrated into organizational policies.\n(c) GOVERN 1.5: Ongoing monitoring and periodic review of the risk management process and its outcomes are planned, organizational roles and responsibilities clearly defined, including determining the authority to decommission an AI system.",
            },
            {
                "number": "2",
                "title": "Core Function 2 — MAP (MP)",
                "text": "1. MAP 1: Context is established and understood across the AI lifecycle.\n(a) MAP 1.1: Intended purposes, potentially beneficial uses, context-specific laws, norms and expectations, and prospective settings in which the AI system will be deployed are understood and documented.\n(b) MAP 2.3: Scientific integrity and TEVV (Testing, Evaluation, Verification, and Validation) considerations are identified and documented, including those related to experimental design, data collection, and model training.\n(c) MAP 5.1: Likelihood and magnitude of each identified impact (both potentially beneficial and harmful) based on expected use, past uses of similar systems, and reasonably foreseeable misuse are determined.",
            },
            {
                "number": "3",
                "title": "Core Function 3 — MEASURE (MS)",
                "text": "1. MEASURE 1: Appropriate methods and metrics are identified and applied.\n(a) MEASURE 2.5: The AI system to be deployed is demonstrated to be valid and reliable.\n(b) MEASURE 2.6: The AI system is evaluated regularly for safety risks, and its safe residual risk threshold is shown to be met.\n(c) MEASURE 2.7: AI system security and resilience to adversarial attacks, data poisoning, and model extraction are evaluated and documented.\n(d) MEASURE 2.11: Fairness and bias — including systemic, computational/statistical, and human-cognitive biases — are evaluated and results documented.",
            },
            {
                "number": "4",
                "title": "Core Function 4 — MANAGE (MG)",
                "text": "1. MANAGE 1: AI risks based on assessments and other analytical output from the MAP and MEASURE functions are prioritized, responded to, and managed.\n(a) MANAGE 2.4: Mechanisms are in place and applied to sustain the value of deployed AI systems, and to supersede, disengage, or deactivate AI systems that demonstrate performance or outcomes inconsistent with intended use.\n(b) MANAGE 3.1: AI risks and benefits from third-party resources and value chain components are regularly monitored, and risk controls are applied and documented.\n(c) MANAGE 4.1: Post-deployment AI system monitoring plans are implemented, including mechanisms for capturing user feedback, appeal and override workflows, and incident response.",
            },
        ],
        "annexes": [],
    },
    "national-us-nist-ai-rmf::nist_ai_600_1_genai": {
        "recitals": [
            {
                "number": "1",
                "text": "(1) The NIST AI RMF Generative Artificial Intelligence Profile (NIST AI 600-1, July 2024) is a cross-sectoral companion resource to the AI RMF 1.0 (NIST AI 100-1) developed pursuant to Executive Order 14110 to help organizations identify and manage unique risks posed by Generative AI foundation models and downstream deployments.",
            },
        ],
        "articles": [
            {
                "number": "1",
                "title": "Core Function 1 — GOVERN (GV) with Generative AI Extensions",
                "text": "1. GOVERN 1: Policies, processes, procedures, and practices across the organization related to the mapping, measuring, and managing of AI and Generative AI risks are in place, transparent, and implemented effectively.\n(a) GOVERN 1.1 (GenAI): Establish policies for acceptable use of Generative AI, compliance with intellectual property and copyright law, data privacy, and content provenance/watermarking standards.\n(b) GOVERN 1.3 (GenAI): Establish risk-tiering policies specifically addressing high-severity Generative AI risks, including CBRN weapons information, offensive cyber capabilities, confabulation/hallucinations, and synthetic CSAM/NCII.\n(c) GOVERN 6.1 (GenAI): Verify third-party foundation model and training dataset provenance, licensing terms, and supply chain vulnerability disclosures before integration.",
            },
            {
                "number": "2",
                "title": "Core Function 2 — MAP (MP) with Generative AI Extensions",
                "text": "1. MAP 1: Context is established and understood across the AI and Generative AI lifecycle.\n(a) MAP 1.1 (GenAI): Document intended and out-of-scope uses of foundation models and fine-tuned Generative AI applications, explicitly assessing dual-use risks and downstream adaptability.\n(b) MAP 3.4 (GenAI): Map human-AI configuration risks, including automation bias, anthropomorphism, and over-reliance on fluent or persuasive Generative AI outputs.\n(c) MAP 5.1 (GenAI): Assess likelihood and magnitude of the 12 primary Generative AI risk categories: (1) CBRN information or capabilities; (2) Confabulation; (3) Dangerous, violent, or hateful recommendations; (4) Data privacy; (5) Environmental impacts; (6) Harmful bias and homogenization; (7) Human-AI configuration; (8) Information integrity; (9) Information security; (10) Intellectual property; (11) Obscene, degrading, and/or abusive content; and (12) Value chain and component integration.",
            },
            {
                "number": "3",
                "title": "Core Function 3 — MEASURE (MS) with Generative AI Extensions",
                "text": "1. MEASURE 1: Appropriate methods, benchmarks, and structured red-teaming are identified and applied to Generative AI systems.\n(a) MEASURE 2.5 (GenAI): Evaluate confabulation rates, grounding fidelity (e.g., in Retrieval-Augmented Generation), and calibration across domains.\n(b) MEASURE 2.6 (GenAI): Conduct structured adversarial red-teaming for CBRN uplift, autonomous cyber-exploitation capabilities, and jailbreak robustness prior to model release.\n(c) MEASURE 2.7 (GenAI): Evaluate prompt injection, indirect prompt injection, training data extraction, and membership inference vulnerabilities.\n(d) MEASURE 2.11 (GenAI): Measure representational harms, stereotyping, and output homogenization/mode collapse across languages and demographic groups.",
            },
            {
                "number": "4",
                "title": "Core Function 4 — MANAGE (MG) with Generative AI Extensions",
                "text": "1. MANAGE 1: AI and Generative AI risks based on assessments from MAP and MEASURE are prioritized, responded to, and managed.\n(a) MANAGE 2.2 (GenAI): Implement input/output guardrails, cryptographic provenance (such as C2PA metadata), and synthetic media watermarking to preserve information integrity.\n(b) MANAGE 2.4 (GenAI): Establish clear kill-switch, rollback, and model weight revocation procedures if critical safety thresholds or systemic risks are breached post-deployment.\n(c) MANAGE 4.1 (GenAI): Maintain post-deployment incident reporting channels for emergent capabilities, jailbreaks, and downstream misuse.",
            },
        ],
        "annexes": [],
    },
    "national-cn-cac-ai-measures::algorithmic_recommendation_2022": {
        "recitals": [
            {
                "number": "1",
                "text": "(1) The Internet Information Service Algorithmic Recommendation Management Provisions (CAC Order No. 9, promulgated 4 January 2022, effective 1 March 2022) are formulated pursuant to the Cybersecurity Law, Data Security Law, and Personal Information Protection Law to regulate algorithmic recommendation activities and safeguard national security and social public interest.",
            },
        ],
        "articles": [
            {
                "number": "1",
                "title": "Purpose and Scope",
                "text": "1. These Provisions are formulated in order to regulate internet information service algorithmic recommendation activities, promote the positive and good values of algorithms, and protect the lawful rights and interests of citizens, legal persons, and other organizations.\n2. Application of algorithmic recommendation technologies (including generation and synthesis, personalized pushing, sorting and selection, retrieval and filtering, and scheduling and decision-making) to provide internet information services within the territory of the PRC shall abide by these Provisions.",
            },
            {
                "number": "4",
                "title": "General Principles, Transparency, and Non-Discrimination",
                "text": "1. The provision of algorithmic recommendation services shall abide by laws and regulations, observe social morality and ethics, abide by commercial ethics and professional ethics, and respect the principles of fairness and justice, openness and transparency, science and reasonableness, and誠信 (honesty and trustworthiness).",
            },
            {
                "number": "7",
                "title": "Lifecycle Governance and Ethical Review",
                "text": "Algorithmic recommendation service providers shall implement main responsibility for algorithmic security, establish and improve management systems and technical measures for algorithm mechanism and principle review, scientific and technological ethics review, user registration, information publication review, data security and personal information protection, and security assessment and monitoring.",
            },
            {
                "number": "12",
                "title": "User Explanation, Opt-Out, and Tag Management Rights (Articles 16–17)",
                "text": "1. Algorithmic recommendation service providers shall inform users in a conspicuous manner of their provision of algorithmic recommendation services, and publicize the basic principles, purpose intentions, and main operating mechanisms of algorithmic recommendation services.\n2. Algorithmic recommendation service providers shall provide users with options that are not specific to their personal characteristics, or provide users with convenient options to turn off algorithmic recommendation services. Where users choose to turn off algorithmic recommendation services, the provider shall immediately cease providing related services and provide options to delete user tags used for personal profiling.",
            },
            {
                "number": "17",
                "title": "Mandatory Algorithm Filing Registry and Security Assessment (Articles 24 & 27)",
                "text": "1. Algorithmic recommendation service providers with public opinion attributes or social mobilization capabilities shall, within 10 working days from the date of providing services, fill in the service provider's name, service form, application field, algorithm type, algorithm self-assessment report, and content to be publicized through the Internet Information Service Algorithm Filing System to complete filing formalities.\n2. Providers with public opinion attributes or social mobilization capabilities shall conduct security assessments in accordance with relevant state regulations.",
            },
        ],
        "annexes": [],
    },
    "national-cn-cac-ai-measures::deep_synthesis_2022": {
        "recitals": [
            {
                "number": "1",
                "text": "(1) The Internet Information Service Deep Synthesis Management Provisions (CAC Order No. 12, promulgated 25 November 2022, effective 10 January 2023) extend China's algorithmic regulatory framework to deep learning and virtual reality synthesis technologies generating text, images, audio, video, and virtual scenes.",
            },
        ],
        "articles": [
            {
                "number": "1",
                "title": "Purpose and Scope (Articles 1–2)",
                "text": "1. These Provisions are formulated to strengthen the management of internet information service deep synthesis, joined with the Algorithmic Recommendation Management Provisions.\n2. 'Deep synthesis technology' refers to technologies that use deep learning, virtual reality, and other generative or synthetic algorithms to produce text, images, audio, video, virtual scenes, and other network information.",
            },
            {
                "number": "4",
                "title": "General Principles, Information Authenticity, and Prohibited Uses (Article 6)",
                "text": "1. No organization or individual may use deep synthesis services to produce, reproduce, publish, or disseminate information prohibited by laws and administrative regulations, or engage in activities harming national security and interests, damaging national image, infringing social public interests, disturbing economic and social order, or infringing the lawful rights and interests of others.\n2. Deep synthesis service providers and users shall not use deep synthesis services to produce, reproduce, publish, or disseminate fake news information.",
            },
            {
                "number": "7",
                "title": "Training Data Legitimacy and Biometric Editing Consent (Article 14)",
                "text": "1. Deep synthesis service providers and technical supporters shall strengthen training data management, take necessary measures to ensure training data security, and where personal information is involved, comply with relevant provisions on personal information protection.\n2. Where deep synthesis service providers and technical supporters provide functions for editing biometric information such as faces and voices, they shall prompt deep synthesis service users to legally notify the edited individuals and obtain their separate consent.",
            },
            {
                "number": "12",
                "title": "Implicit Watermarking and Conspicuous Synthetic Content Labeling (Articles 16–17)",
                "text": "1. Deep synthesis service providers shall take technical measures to add signs that do not affect user use (implicit watermarks/metadata logs) to information content generated or edited using their services, and store log information in accordance with laws and regulations.\n2. Where deep synthesis service providers provide intelligent dialogue, synthesized human voice, facial generation or replacement, or immersive realistic scenes that might cause confusion or misidentification by the public, they shall place conspicuous labels in reasonable positions on the generated or edited content to alert the public to the deep synthesis situation.\n3. No organization or individual may use technical means to delete, tamper with, or conceal the deep synthesis identification marks specified in Articles 16 and 17.",
            },
            {
                "number": "17",
                "title": "Algorithm Registry Filing and Security Assessments for Deep Synthesis (Articles 19–20)",
                "text": "1. Deep synthesis service providers and technical supporters with public opinion attributes or social mobilization capabilities shall fulfill filing and change/cancellation filing procedures in accordance with the Internet Information Service Algorithmic Recommendation Management Provisions.\n2. Before launching new products, applications, or functions with public opinion attributes or social mobilization capabilities, providers shall conduct a security assessment.",
            },
        ],
        "annexes": [],
    },
    "national-cn-cac-ai-measures::generative_ai_measures_2023": {
        "recitals": [
            {
                "number": "1",
                "text": "(1) The Interim Measures for the Management of Generative Artificial Intelligence Services (CAC Order No. 15, jointly promulgated on 10 July 2023 by CAC, NDRC, MoE, MOST, MIIT, MPS, and NRTA, effective 15 August 2023) establish comprehensive lifecycle governance for public-facing foundation and generative AI services while introducing an explicit R&D/internal-use exemption and agile 'classified and graded' supervision.",
            },
        ],
        "articles": [
            {
                "number": "1",
                "title": "Purpose, Scope, and R&D Exemption (Articles 1–2)",
                "text": "1. These Measures are formulated in order to promote the healthy development and standardized application of generative artificial intelligence, safeguard national security and social public interests, and protect the lawful rights and interests of citizens, legal persons, and other organizations.\n2. These Measures apply to the use of generative artificial intelligence technology (models and related technologies with the ability to generate text, pictures, audio, video, and other content) to provide services for generating text, pictures, audio, video, and other content to the public within the territory of the People's Republic of China.\n3. Where industry organizations, enterprises, educational and scientific research institutions, public cultural institutions, and relevant professional institutions research, develop, and apply generative artificial intelligence technology, and do not provide generative artificial intelligence services to the domestic public, the provisions of these Measures do not apply.",
            },
            {
                "number": "4",
                "title": "General Principles, Non-Discrimination, and IP Protection",
                "text": "1. The provision and use of generative AI services shall abide by laws and administrative regulations, respect social morality and ethics, and adhere to the following provisions:\n(a) uphold the Core Socialist Values, and must not generate content inciting subversion of state power, undermining national unity, or宣扬 (promoting) terrorism, extremism, ethnic hatred, violence, obscenity, or false and harmful information;\n(b) take effective measures during algorithm design, training data selection, model generation and optimization, and service provision to prevent discrimination based on ethnicity, belief, country, region, gender, age, occupation, or health;\n(c) respect intellectual property rights and business ethics, keep commercial secrets, and must not use algorithms, data, platforms, and other advantages to implement monopoly and unfair competition;\n(d) respect the lawful rights and interests of others, and must not endanger the physical and mental health of others or infringe upon their portrait rights, reputation rights, honor rights, privacy rights, and personal information rights;\n(e) based on the characteristics of service types, take effective measures to improve the transparency of generative AI services and the accuracy and reliability of generated content.",
            },
            {
                "number": "7",
                "title": "Training Data Pre-Processing, IP Compliance, and Personal Data Consent",
                "text": "Providers of generative AI services ('providers') shall carry out pre-training, optimization training, and other training data processing activities in accordance with the law, and abide by the following provisions:\n(a) use data and foundation models with legitimate sources;\n(b) where intellectual property rights are involved, must not infringe upon intellectual property rights enjoyed by others in accordance with the law;\n(c) where personal information is involved, obtain the consent of the individual or comply with other circumstances prescribed by laws and administrative regulations;\n(d) take effective measures to improve the quality of training data and enhance the authenticity, accuracy, objectivity, and diversity of training data;\n(e) comply with the relevant provisions of the Cybersecurity Law, Data Security Law, and Personal Information Protection Law, as well as the basic scientific and technological safety requirements of relevant competent departments.",
            },
            {
                "number": "12",
                "title": "Synthetic Content Labeling and User Input Protection (Articles 11–12)",
                "text": "1. Providers shall fulfill the obligation of protecting users' input information and usage records in accordance with the law, must not collect unnecessary personal information, must not illegally retain input information and usage records that can identify users, and must not illegally provide users' input information and usage records to others.\n2. Providers shall mark generated content such as pictures and videos in accordance with the Internet Information Service Deep Synthesis Management Provisions.",
            },
            {
                "number": "17",
                "title": "Classified and Graded Supervision, Security Assessment, and Algorithm Filing (Articles 16–17)",
                "text": "1. Relevant competent departments shall, based on the technical characteristics of generative AI and its service applications in relevant industries and fields, implement inclusive, prudent, and classified and graded supervision.\n2. Providers that provide generative AI services with public opinion attributes or social mobilization capabilities shall carry out security assessments in accordance with relevant state provisions, and fulfill algorithm filing, change, and cancellation filing procedures in accordance with the Internet Information Service Algorithmic Recommendation Management Provisions.",
            },
        ],
        "annexes": [],
    },
}


def fetch_national_stage(
    instrument: dict[str, Any],
    version: dict[str, Any],
    cache_dir: Path | None = None,
) -> dict[str, Any]:
    """
    Fetch a comparative national AI governance stage (US NIST AI RMF / China CAC),
    caching compressed `.json.gz` payloads in `pipeline-cache`.
    """
    instrument_id = instrument["id"]
    stage = version["stage"]
    cache_key = f"{instrument_id}__{stage}"

    if cache_dir:
        cache_file = cache_dir / f"{cache_key}.json.gz"
        if cache_file.exists():
            with gzip.open(cache_file, "rt", encoding="utf-8") as f:
                return json.load(f)

    source_url = version.get("source_url", "")
    http_status = None

    if httpx is not None and source_url and source_url.startswith("http"):
        try:
            with httpx.Client(timeout=15.0, follow_redirects=True) as client:
                resp = client.head(
                    source_url,
                    headers={"User-Agent": "lex-machina-corpus-bot/1.0"},
                )
                http_status = resp.status_code
        except Exception as exc:
            http_status = f"error:{type(exc).__name__}"

    canonical_key = f"{instrument_id}::{stage}"
    canonical = NATIONAL_PROVISIONS.get(
        canonical_key,
        {"recitals": [], "articles": [], "annexes": []},
    )

    payload = {
        "instrument_id": instrument_id,
        "path": instrument["path"],
        "jurisdiction": instrument["jurisdiction"],
        "title": instrument["title"],
        "stage": stage,
        "stage_label": version["stage_label"],
        "date": version["date"],
        "document_symbol": version["document_symbol"],
        "celex": version.get("celex", instrument.get("celex", "")),
        "author_name": version["author_name"],
        "author_email": version["author_email"],
        "source_url": source_url,
        "summary": version["summary"],
        "http_status": http_status,
        "recitals": canonical["recitals"],
        "articles": canonical["articles"],
        "annexes": canonical["annexes"],
    }

    if cache_dir:
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / f"{cache_key}.json.gz"
        with gzip.open(cache_file, "wt", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    return payload
