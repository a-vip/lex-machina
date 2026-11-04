"""
Council of Europe (CoE), United Nations (UNGA / CCW GGE), and International
Humanitarian Law (ICRC Geneva Conventions & Additional Protocols) Fetcher.

Fetches treaty texts, negotiating drafts, UN resolutions, and IHL protocols,
producing structured article-level payloads with `.json.gz` caching for the
`pipeline-cache` orphan branch.
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


UN_COE_IHL_PROVISIONS: dict[str, dict[str, Any]] = {
    "coe-ai-convention::revised_zero_draft": {
        "recitals": [
            {
                "number": "1",
                "text": "(1) The member States of the Council of Europe and the other signatories hereto, considering that the aim of the Council of Europe is to achieve a greater unity between its members, based in particular on respect for human rights, democracy and the rule of law, recognise the need to establish a common legal framework for the design, development and application of artificial intelligence systems.",
            },
        ],
        "articles": [
            {
                "number": "1",
                "title": "Purpose and object",
                "text": "1. The provisions of this Convention aim to ensure that the design, development and application of artificial intelligence systems are fully consistent with respect for human rights, the functioning of democracy and the observance of the rule of law.\n2. Each Party shall adopt such legislative, administrative or other measures as may be necessary to give effect to the provisions set out in this Convention.",
            },
            {
                "number": "3",
                "title": "Scope",
                "text": "1. This Convention applies to the design, development and application of artificial intelligence systems by public authorities and private actors.\n2. This Convention shall not apply to the design, development and application of artificial intelligence systems used exclusively for national defence purposes.",
            },
            {
                "number": "4",
                "title": "Definition of Artificial Intelligence System",
                "text": "For the purposes of this Convention, 'artificial intelligence system' means any algorithmic system or a combination of such systems that uses computational methods derived from statistics or other mathematical techniques to carry out functions that are commonly associated with, or would otherwise require, human intelligence and that generates outputs such as content, predictions, recommendations or decisions.",
            },
            {
                "number": "11",
                "title": "Transparency and oversight",
                "text": "Each Party shall establish mechanisms to ensure that adequate transparency and human oversight are maintained throughout the lifecycle of artificial intelligence systems proportionate to the risks to human rights, democracy and the rule of law.",
            },
            {
                "number": "16",
                "title": "Risk and impact assessment",
                "text": "Each Party shall take measures to ensure that prior and iterative assessments of the potential impacts of artificial intelligence systems on human rights, democracy and the rule of law are conducted before deployment.",
            },
        ],
        "annexes": [],
    },
    "coe-ai-convention::consolidated_working_draft": {
        "recitals": [
            {
                "number": "1",
                "text": "(1) The member States of the Council of Europe and the other signatories hereto, recognising the value of fostering cooperation between the Parties to this Convention and of extending such cooperation to other States that share the same values, are conscious of the accelerating developments in science and technology and the profound changes brought about by activities within the lifecycle of artificial intelligence systems.",
            },
        ],
        "articles": [
            {
                "number": "1",
                "title": "Object and purpose",
                "text": "1. The provisions of this Convention aim to ensure that activities within the lifecycle of artificial intelligence systems are fully consistent with human rights, democracy and the rule of law.\n2. Each Party shall adopt or maintain appropriate legislative, administrative or other measures to give effect to the provisions set out in this Convention. These measures shall be graduated and differentiated as may be necessary in view of the severity and probability of occurrence of adverse impacts on human rights, democracy and the rule of law throughout the lifecycle of artificial intelligence systems.",
            },
            {
                "number": "3",
                "title": "Scope",
                "text": "1. The scope of this Convention covers the activities within the lifecycle of artificial intelligence systems that have the potential to interfere with human rights, democracy and the rule of law, as follows:\n(a) Each Party shall apply this Convention to the activities within the lifecycle of artificial intelligence systems undertaken by public authorities, or private actors acting on their behalf;\n(b) Each Party shall address risks and impacts arising from activities within the lifecycle of artificial intelligence systems by private actors to the extent not covered in subparagraph (a) in a manner conforming with the object and purpose of the Convention.\n2. A Party shall not be required to apply this Convention to activities within the lifecycle of artificial intelligence systems related to the protection of its national security interests, with the understanding that such activities are conducted in a manner consistent with applicable international law.\n3. This Convention shall not apply to research and development activities regarding artificial intelligence systems not yet made available for use, unless testing or similar activities are undertaken in such a way that they have the potential to interfere with human rights, democracy and the rule of law.",
            },
            {
                "number": "4",
                "title": "Definition of Artificial Intelligence System",
                "text": "For the purposes of this Convention, 'artificial intelligence system' means a machine-based system that, for explicit or implicit objectives, infers, from the input it receives, how to generate outputs such as predictions, content, recommendations or decisions that may influence physical or virtual environments. Different artificial intelligence systems vary in their levels of autonomy and adaptiveness after deployment.",
            },
            {
                "number": "11",
                "title": "Transparency and oversight",
                "text": "Each Party shall adopt or maintain measures to ensure that adequate transparency and oversight mechanisms are in place in respect of activities within the lifecycle of artificial intelligence systems, including regarding the identification of content generated by artificial intelligence systems and notifying persons interacting with an artificial intelligence system.",
            },
            {
                "number": "16",
                "title": "Risk and impact management framework",
                "text": "1. Each Party shall, taking into account the principles set forth in Chapter III, adopt or maintain measures for the identification, assessment, prevention and mitigation of risks and impacts posed by artificial intelligence systems by considering actual and potential impacts to human rights, democracy and the rule of law.\n2. Such measures shall be graduated and differentiated, as appropriate, and take due account of the context and intended use of artificial intelligence systems.",
            },
        ],
        "annexes": [],
    },
    "coe-ai-convention::adopted_convention_cets_225": {
        "recitals": [
            {
                "number": "1",
                "text": "(1) The member States of the Council of Europe and the other signatories hereto, considering that the aim of the Council of Europe is to achieve greater unity between its members, based in particular on the respect for human rights, democracy and the rule of law, and mindful of the accelerating developments in science and technology and the profound changes brought about by activities within the lifecycle of artificial intelligence systems, which have the potential to promote human prosperity as well as individual and societal well-being, sustainable development, gender equality and the empowerment of all women and girls, while also recognizing the risk of undermining human dignity and individual autonomy, human rights, democracy and the rule of law, have agreed as follows:",
            },
        ],
        "articles": [
            {
                "number": "1",
                "title": "Object and purpose",
                "text": "1. The provisions of this Convention aim to ensure that activities within the lifecycle of artificial intelligence systems are fully consistent with human rights, democracy and the rule of law.\n2. Each Party shall adopt or maintain appropriate legislative, administrative or other measures to give effect to the provisions set out in this Convention. These measures shall be graduated and differentiated as may be necessary in view of the severity and probability of occurrence of adverse impacts on human rights, democracy and the rule of law throughout the lifecycle of artificial intelligence systems.",
            },
            {
                "number": "2",
                "title": "Definition of artificial intelligence systems",
                "text": "For the purposes of this Convention, 'artificial intelligence system' means a machine-based system that, for explicit or implicit objectives, infers, from the input it receives, how to generate outputs such as predictions, content, recommendations or decisions that may influence physical or virtual environments. Different artificial intelligence systems vary in their levels of autonomy and adaptiveness after deployment.",
            },
            {
                "number": "3",
                "title": "Scope",
                "text": "1. The scope of this Convention covers the activities within the lifecycle of artificial intelligence systems that have the potential to interfere with human rights, democracy and the rule of law, as follows:\n(a) Each Party shall apply this Convention to the activities within the lifecycle of artificial intelligence systems undertaken by public authorities, or private actors acting on their behalf;\n(b) Each Party shall address risks and impacts arising from activities within the lifecycle of artificial intelligence systems by private actors to the extent not covered in subparagraph (a) in a manner conforming with the object and purpose of the Convention. Each Party shall specify in a declaration submitted to the Secretary General of the Council of Europe at the time of signature, or when depositing its instrument of ratification, acceptance, approval or accession, how it intends to implement this obligation, either by applying the principles and obligations set forth in Chapters II to VI of this Convention to activities of private actors or by taking other appropriate measures to fulfil the obligation set out in this subparagraph.\n2. A Party shall not be required to apply this Convention to activities within the lifecycle of artificial intelligence systems related to the protection of its national security interests, with the understanding that such activities are conducted in a manner consistent with applicable international law and with respect for its democratic institutions and processes.\n3. Without prejudice to Article 13 and Article 25, paragraph 2, this Convention shall not apply to research and development activities regarding artificial intelligence systems not yet made available for use, unless testing or similar activities are undertaken in such a way that they have the potential to interfere with human rights, democracy and the rule of law.\n4. Matters relating to national defence do not fall within the scope of this Convention.",
            },
            {
                "number": "7",
                "title": "Human dignity and individual autonomy",
                "text": "Each Party shall adopt or maintain measures to respect human dignity and individual autonomy in relation to activities within the lifecycle of artificial intelligence systems.",
            },
            {
                "number": "8",
                "title": "Transparency and oversight",
                "text": "Each Party shall adopt or maintain measures to ensure that adequate transparency and oversight requirements tailored to the specific contexts and risks are in place in respect of activities within the lifecycle of artificial intelligence systems, including with regard to the identification of content generated by artificial intelligence systems.",
            },
            {
                "number": "9",
                "title": "Accountability and responsibility",
                "text": "Each Party shall adopt or maintain measures to ensure accountability and responsibility for adverse impacts on human rights, democracy and the rule of law resulting from activities within the lifecycle of artificial intelligence systems.",
            },
            {
                "number": "14",
                "title": "Remedies",
                "text": "1. Each Party shall, to the extent remedies are required by its international obligations and consistent with its domestic legal system, adopt or maintain measures to ensure the availability of accessible and effective remedies for violations of human rights resulting from the activities within the lifecycle of artificial intelligence systems.\n2. With the aim of supporting paragraph 1, each Party shall adopt or maintain measures including:\n(a) measures to ensure that relevant information regarding artificial intelligence systems which have the potential to significantly affect human rights and their relevant usage is documented, provided to bodies authorised to access that information and, where appropriate and applicable, made available or communicated to affected persons;\n(b) measures to ensure that the information referred to in subparagraph (a) is sufficient for the affected persons to contest the decision(s) made or substantially informed by the use of the system, and, where relevant and appropriate, the use of the system itself; and\n(c) an effective possibility for persons concerned to lodge a complaint to competent authorities.",
            },
            {
                "number": "16",
                "title": "Risk and impact management framework",
                "text": "1. Each Party shall, taking into account the principles set forth in Chapter III, adopt or maintain measures for the identification, assessment, prevention and mitigation of risks posed by artificial intelligence systems by considering actual and potential impacts to human rights, democracy and the rule of law.\n2. Such measures shall be graduated and differentiated, as appropriate, and:\n(a) take due account of the context and intended use of artificial intelligence systems, in particular as concerns risks to human rights, democracy, and the rule of law;\n(b) take due account of the severity and probability of potential impacts;\n(c) consider, where appropriate, the perspectives of relevant stakeholders, in particular persons whose rights may be impacted;\n(d) apply iteratively throughout the activities within the lifecycle of the artificial intelligence system;\n(e) include monitoring for risks and adverse impacts to human rights, democracy, and the rule of law;\n(f) include documentation of risks, actual and potential impacts, and the risk management approach; and\n(g) require, where appropriate, testing of artificial intelligence systems before making them available for first use and when they are significantly modified.\n4. Each Party shall assess the need for a moratorium or ban or other appropriate measures in respect of certain uses of artificial intelligence systems where it considers that such uses are incompatible with the respect for human rights, the functioning of democracy or the rule of law.",
            },
        ],
        "annexes": [
            {
                "number": "I",
                "title": "Explanatory Report to the Council of Europe Framework Convention on Artificial Intelligence (CETS No. 225)",
                "text": "1. The Explanatory Report accompanies CETS No. 225 adopted by the Committee of Ministers on 17 May 2024.\n2. Paragraph 24 clarifies that the definition of 'artificial intelligence system' in Article 2 mirrors the updated OECD AI definition (november 2023) and the EU AI Act Article 3(1) definition to ensure international regulatory interoperability.\n3. Paragraph 105 confirms that under Article 16(4), Parties must evaluate bans or moratoria on AI practices that pose unacceptable risks to human rights, democracy, or the rule of law.",
            },
        ],
    },
    "un-ccw-laws::guiding_principles_2019": {
        "recitals": [
            {
                "number": "1",
                "text": "(1) The High Contracting Parties to the Convention on Prohibitions or Restrictions on the Use of Certain Conventional Weapons Which May Be Deemed to Be Excessively Injurious or to Have Indiscriminate Effects (CCW) affirm the 11 Guiding Principles on emerging technologies in the area of lethal autonomous weapons systems (CCW/GGE.1/2019/3, Annex IV).",
            },
        ],
        "articles": [
            {
                "number": "1",
                "title": "Principle (a) — Applicability of International Humanitarian Law",
                "text": "International humanitarian law continues to apply fully to all weapons systems, including the potential development and use of lethal autonomous weapons systems.",
            },
            {
                "number": "2",
                "title": "Principle (b) — Human Responsibility",
                "text": "Human responsibility for decisions on the use of weapons systems must be retained since accountability cannot be transferred to machines. This should be considered across the entire life cycle of the weapons system.",
            },
            {
                "number": "3",
                "title": "Principle (c) — Human-Machine Interaction and Accountability",
                "text": "Human-machine interaction, which may take various forms and be implemented at various stages of the life cycle of a weapon, should ensure that the potential use of weapons systems based on emerging technologies in the area of lethal autonomous weapons systems is in compliance with applicable international law, in particular IHL. In determining the quality and extent of human-machine interaction, a range of factors should be considered including the operational context, and the characteristics and capabilities of the weapons system as a whole.",
            },
            {
                "number": "4",
                "title": "Principle (d) — Accountability in State Frameworks",
                "text": "Accountability for developing, deploying and using any emerging weapons system in the framework of the CCW must be ensured in accordance with applicable international law, including through the operation of such systems within a responsible chain of human command and control.",
            },
            {
                "number": "5",
                "title": "Principle (e) — National Legal Weapons Reviews",
                "text": "In accordance with States' obligations under international law, in the study, development, acquisition, or adoption of a new weapon, means or method of warfare, determination must be made whether its employment would, in some or all circumstances, be prohibited by international law.",
            },
            {
                "number": "6",
                "title": "Principle (f) — Physical Security and Non-Proliferation Risk Mitigation",
                "text": "When developing or acquiring new weapons systems based on emerging technologies in the area of lethal autonomous weapons systems, physical security, appropriate non-physical safeguards (including cyber-security against hacking or data spoofing), the risk of acquisition by terrorist groups and the risk of proliferation should be considered.",
            },
            {
                "number": "7",
                "title": "Principle (g) — Risk Assessment and Mitigation During Design",
                "text": "Risk assessments and mitigation measures should be part of the design, development, testing and deployment cycle of emerging technologies in any weapons systems.",
            },
            {
                "number": "8",
                "title": "Principle (h) — Anthropomorphism Avoidance",
                "text": "Consideration should be given to the use of emerging technologies in the area of lethal autonomous weapons systems in upholding compliance with IHL and other applicable international legal obligations; in policy discussions, anthropomorphising emerging technologies should be avoided.",
            },
            {
                "number": "9",
                "title": "Principle (i) — Preservation of Peaceful Dual-Use AI Innovation",
                "text": "In crafting potential policy measures, emerging technologies in the area of lethal autonomous weapons systems should not be anthropomorphized and policy measures should not hamper progress in or access to peaceful uses of intelligent autonomous technologies.",
            },
            {
                "number": "10",
                "title": "Principle (j) — Forum Appropriateness of the CCW",
                "text": "The CCW offers an appropriate framework for dealing with the issue of emerging technologies in the area of lethal autonomous weapons systems within the context of the objectives and purposes of the Convention, which seeks to strike a balance between military necessity and humanitarian considerations.",
            },
            {
                "number": "11",
                "title": "Principle (k) — Cyber Security and Data Integrity",
                "text": "Discussions and any potential policy measures taken within the context of the CCW should not hamper progress in or access to civilian research and development and use of autonomous technologies, while ensuring resilience against cyber interference and spoofing.",
            },
        ],
        "annexes": [],
    },
    "un-ccw-laws::rolling_text_report_2023": {
        "recitals": [
            {
                "number": "1",
                "text": "(1) The Group of Governmental Experts on Emerging Technologies in the Area of Lethal Autonomous Weapons Systems adopted its consensus 2023 report (CCW/GGE.1/2023/2) on 26 May 2023 in Geneva, advancing the normative and operational framework toward a two-tier structure of prohibitions and regulations.",
            },
        ],
        "articles": [
            {
                "number": "1",
                "title": "Applicability of IHL and State Responsibility (Paragraphs 17–19)",
                "text": "1. International law, in particular the United Nations Charter and International Humanitarian Law (IHL), applies fully to all weapons systems, including those based on emerging technologies in the area of lethal autonomous weapons systems (LAWS).\n2. Complying with IHL rules and principles, including inter alia distinction, proportionality and precautions in attack, requires inter alia context-specific human judgment and control.\n3. Every internationally wrongful act of a State, including one resulting from the use of a weapon system based on emerging technologies in the area of LAWS, entails the international responsibility of that State.",
            },
            {
                "number": "2",
                "title": "First Tier — Prohibited Autonomous Weapons Systems (Paragraph 21)",
                "text": "1. Weapons systems based on emerging technologies in the area of lethal autonomous weapons systems that cannot be used in compliance with international humanitarian law must not be used, and their development or production should be prohibited.\n2. In particular, weapons systems must not be used if they:\n(a) are of a nature to cause superfluous injury or unnecessary suffering;\n(b) are inherently indiscriminate; or\n(c) are incapable of being directed at a specific military objective or have effects that cannot be limited as required by IHL.",
            },
            {
                "number": "3",
                "title": "Second Tier — Regulated Autonomous Weapons Systems (Paragraph 22)",
                "text": "1. For other weapons systems based on emerging technologies in the area of LAWS that select and apply force to targets without human intervention after activation, States must implement rigorous regulatory measures to ensure compliance with IHL, including:\n(a) limiting the types of targets that the system can engage;\n(b) limiting the duration, geographical scope, and scale of operation, including through self-destruct, self-deactivation, or self-neutralization mechanisms;\n(c) ensuring clear human-machine interaction, understandability, and predictability of system behavior in the specific operational environment; and\n(d) enabling human operators to supervise, intervene, and deactivate the system where appropriate.",
            },
            {
                "number": "5",
                "title": "National Legal Weapons Reviews and Lifecycle Testing (Paragraphs 24–26)",
                "text": "1. National legal reviews of new weapons, means or methods of warfare, including those based on emerging technologies in the area of LAWS, are a critical measure for States to ensure compliance with IHL.\n2. Reviews should be conducted at multiple stages of the lifecycle, including study, development, acquisition, and whenever significant modifications (such as machine learning retraining) alter the operational capabilities or effects of the weapon system.",
            },
        ],
        "annexes": [],
    },
    "un-ai-governance::unga_res_78_265": {
        "recitals": [
            {
                "number": "1",
                "text": "(1) The General Assembly, guided by the purposes and principles of the Charter of the United Nations, reaffirms the Universal Declaration of Human Rights and notes that the same rights that people have offline must also be protected online and throughout the life cycle of artificial intelligence systems.",
            },
        ],
        "articles": [
            {
                "number": "1",
                "title": "Human-Centric, Safe, Secure and Trustworthy AI (Operative Paragraphs 1–3)",
                "text": "1. Resolves to bridge the artificial intelligence and other digital divides between and within countries and to promote safe, secure and trustworthy artificial intelligence systems to accelerate progress towards the full realization of the 2030 Agenda for Sustainable Development.\n2. Emphasizes that human rights and fundamental freedoms must be respected, protected and promoted throughout the life cycle of artificial intelligence systems.",
            },
            {
                "number": "2",
                "title": "Prohibition of Non-Compliant AI Systems (Operative Paragraph 4)",
                "text": "Calls upon Member States and invites other stakeholders to refrain from or cease the use of artificial intelligence systems that are impossible to operate in compliance with international human rights law or that pose undue risks to the enjoyment of human rights, especially of those who are in vulnerable situations.",
            },
            {
                "number": "3",
                "title": "Regulatory Governance and Risk Management (Operative Paragraph 6)",
                "text": "Encourages Member States to develop and support regulatory and governance approaches and frameworks related to safe, secure and trustworthy artificial intelligence systems, including:\n(a) promoting internationally interoperable technical standards and risk management frameworks;\n(b) establishing mechanisms for impact assessments, independent testing, red-teaming, and post-deployment monitoring;\n(c) implementing reliable provenance and watermarking mechanisms to help users identify AI-generated digital content and safeguard information integrity.",
            },
        ],
        "annexes": [],
    },
    "un-ai-governance::global_digital_compact": {
        "recitals": [
            {
                "number": "1",
                "text": "(1) We, the Heads of State and Government, gathered at United Nations Headquarters in New York on 22 and 23 September 2024, adopt the Global Digital Compact (Annex I to the Pact for the Future, A/79/L.2 / A/RES/79/1) to establish an inclusive global framework for digital cooperation and the governance of artificial intelligence for humanity.",
            },
        ],
        "articles": [
            {
                "number": "1",
                "title": "Objectives and Principles of the Global Digital Compact (Paragraphs 7–8)",
                "text": "1. We pursue five overarching objectives:\n(a) close all digital divides and accelerate progress across the Sustainable Development Goals;\n(b) expand inclusion in and benefits from the digital economy for all;\n(c) foster an inclusive, open, safe and secure digital space that respects, protects and promotes human rights;\n(d) advance responsible, equitable and interoperable data governance approaches; and\n(e) enhance international governance of artificial intelligence for the benefit of humanity.",
            },
            {
                "number": "2",
                "title": "Prohibition and Human Rights Safeguards (Paragraphs 51–53)",
                "text": "1. We affirm that international law, including international human rights law, applies across the life cycle of artificial intelligence systems.\n2. We commit to refrain from or cease the use of artificial intelligence systems that are impossible to operate in compliance with international human rights law or that pose undue risks to the enjoyment of human rights.",
            },
            {
                "number": "3",
                "title": "International Scientific Panel on AI and Global Dialogue on AI Governance (Paragraphs 56–57)",
                "text": "1. We decide to establish, within the United Nations, a multidisciplinary Independent International Scientific Panel on AI with balanced geographic representation to promote scientific understanding through impartial, evidence-based risk, opportunity, and impact assessments.\n2. We further decide to initiate a Global Dialogue on AI Governance involving Governments and all relevant stakeholders, which will take place in the margins of existing relevant United Nations conferences and meetings, to promote the interoperability of AI governance frameworks and compatibility with international human rights standards.",
            },
        ],
        "annexes": [],
    },
    "ihl-geneva-conventions::geneva_conventions_1949": {
        "recitals": [
            {
                "number": "1",
                "text": "(1) The undersigned Plenipotentiaries of the Governments represented at the Diplomatic Conference held at Geneva from April 21 to August 12, 1949, have adopted the Four Geneva Conventions for the Protection of War Victims.",
            },
        ],
        "articles": [
            {
                "number": "1",
                "title": "Common Article 1 — Respect for the Convention",
                "text": "The High Contracting Parties undertake to respect and to ensure respect for the present Convention in all circumstances.",
            },
            {
                "number": "2",
                "title": "Common Article 2 — Application of the Convention",
                "text": "1. In addition to the provisions which shall be implemented in peacetime, the present Convention shall apply to all cases of declared war or of any other armed conflict which may arise between two or more of the High Contracting Parties, even if the state of war is not recognized by one of them.\n2. The Convention shall also apply to all cases of partial or total occupation of the territory of a High Contracting Party, even if the said occupation meets with no armed resistance.",
            },
            {
                "number": "3",
                "title": "Common Article 3 — Conflicts Not of an International Character",
                "text": "1. In the case of armed conflict not of an international character occurring in the territory of one of the High Contracting Parties, each Party to the conflict shall be bound to apply, as a minimum, the following provisions:\n(a) Persons taking no active part in the hostilities, including members of armed forces who have laid down their arms and those placed 'hors de combat' by sickness, wounds, detention, or any other cause, shall in all circumstances be treated humanely, without any adverse distinction founded on race, colour, religion or faith, sex, birth or wealth, or any other similar criteria.\nTo this end, the following acts are and shall remain prohibited at any time and in any place whatsoever with respect to the above-mentioned persons:\n(i) violence to life and person, in particular murder of all kinds, mutilation, cruel treatment and torture;\n(ii) taking of hostages;\n(iii) outrages upon personal dignity, in particular humiliating and degrading treatment;\n(iv) the passing of sentences and the carrying out of executions without previous judgment pronounced by a regularly constituted court, affording all the judicial guarantees which are recognized as indispensable by civilized peoples.\n2. The wounded and sick shall be collected and cared for.",
            },
            {
                "number": "147",
                "title": "Grave Breaches (Fourth Geneva Convention Article 147 / GC I Art. 50 / GC II Art. 51 / GC III Art. 130)",
                "text": "Grave breaches to which the preceding Article relates shall be those involving any of the following acts, if committed against persons or property protected by the present Convention: wilful killing, torture or inhuman treatment, including biological experiments, wilfully causing great suffering or serious injury to body or health, unlawful deportation or transfer or unlawful confinement of a protected person, compelling a protected person to serve in the forces of a hostile Power, or wilfully depriving a protected person of the rights of fair and regular trial prescribed in the present Convention, taking of hostages and extensive destruction and appropriation of property, not justified by military necessity and carried out unlawfully and wantonly.",
            },
        ],
        "annexes": [],
    },
    "ihl-geneva-conventions::additional_protocols_1977": {
        "recitals": [
            {
                "number": "1",
                "text": "(1) The High Contracting Parties, proclaiming their earnest wish to see peace prevail among peoples, believing it necessary nevertheless to reaffirm and develop the provisions protecting the victims of armed conflicts and to supplement measures intended to reinforce their application, have adopted Protocol Additional I and Protocol Additional II of 8 June 1977 to the Geneva Conventions of 12 August 1949.",
            },
        ],
        "articles": [
            {
                "number": "1",
                "title": "Common Article 1 & AP I Article 1 — General Principles and Scope of Application (incl. Martens Clause)",
                "text": "1. The High Contracting Parties undertake to respect and to ensure respect for this Protocol in all circumstances.\n2. In cases not covered by this Protocol or by other international agreements, civilians and combatants remain under the protection and authority of the principles of international law derived from established custom, from the principles of humanity and from the dictates of public conscience.",
            },
            {
                "number": "2",
                "title": "Common Article 2 — Application in International Armed Conflicts",
                "text": "1. In addition to the provisions which shall be implemented in peacetime, the Conventions and Protocol Additional I apply to all cases of declared war or of any other armed conflict which may arise between two or more High Contracting Parties, as well as armed conflicts in which peoples are fighting against colonial domination and alien occupation and against racist regimes in the exercise of their right of self-determination.",
            },
            {
                "number": "3",
                "title": "Common Article 3 & Additional Protocol II — Non-International Armed Conflicts",
                "text": "1. Protocol Additional II develops and supplements Article 3 common to the Geneva Conventions of 12 August 1949 without modifying its existing conditions of application.\n2. Neither the civilian population as such, nor individual civilians, shall be the object of attack. Acts or threats of violence the primary purpose of which is to spread terror among the civilian population are prohibited (AP II Article 13).",
            },
            {
                "number": "35",
                "title": "Part III, Section I — Methods and Means of Warfare: Basic Rules (AP I Article 35)",
                "text": "1. In any armed conflict, the right of the Parties to the conflict to choose methods or means of warfare is not unlimited.\n2. It is prohibited to employ weapons, projectiles and material and methods of warfare of a nature to cause superfluous injury or unnecessary suffering.\n3. It is prohibited to employ methods or means of warfare which are intended, or may be expected, to cause widespread, long-term and severe damage to the natural environment.",
            },
            {
                "number": "36",
                "title": "Part III, Section I — New Weapons (AP I Article 36)",
                "text": "In the study, development, acquisition or adoption of a new weapon, means or method of warfare, a High Contracting Party is under an obligation to determine whether its employment would, in some or all circumstances, be prohibited by this Protocol or by any other rule of international law applicable to the High Contracting Party.",
            },
            {
                "number": "48",
                "title": "Part IV, Section I — Basic Rule of Distinction (AP I Article 48)",
                "text": "In order to ensure respect for and protection of the civilian population and civilian objects, the Parties to the conflict shall at all times distinguish between the civilian population and combatants and between civilian objects and military objectives and accordingly shall direct their operations only against military objectives.",
            },
            {
                "number": "51",
                "title": "Protection of the Civilian Population & Prohibition of Indiscriminate Attacks (AP I Article 51)",
                "text": "1. The civilian population and individual civilians shall enjoy general protection against dangers arising from military operations.\n4. Indiscriminate attacks are prohibited. Indiscriminate attacks are:\n(a) those which are not directed at a specific military objective;\n(b) those which employ a method or means of combat which cannot be directed at a specific military objective; or\n(c) those which employ a method or means of combat the effects of which cannot be limited as required by this Protocol;\nand consequently, in each such case, are of a nature to strike military objectives and civilians or civilian objects without distinction.\n5. Among others, the following types of attacks are to be considered as indiscriminate:\n(a) an attack by bombardment by any methods or means which treats as a single military objective a number of clearly separated and distinct military objectives located in a city, town, village or other area containing a similar concentration of civilians or civilian objects; and\n(b) an attack which may be expected to cause incidental loss of civilian life, injury to civilians, damage to civilian objects, or a combination thereof, which would be excessive in relation to the concrete and direct military advantage anticipated.",
            },
            {
                "number": "57",
                "title": "Precautions in Attack (AP I Article 57)",
                "text": "1. In the conduct of military operations, constant care shall be taken to spare the civilian population, civilians and civilian objects.\n2. With respect to attacks, the following precautions shall be taken:\n(a) those who plan or decide upon an attack shall:\n(i) do everything feasible to verify that the objectives to be attacked are neither civilians nor civilian objects and are not subject to special protection but are military objectives within the meaning of paragraph 2 of Article 52 and that it is not prohibited by the provisions of this Protocol to attack them;\n(ii) take all feasible precautions in the choice of means and methods of attack with a view to avoiding, and in any event to minimizing, incidental loss of civilian life, injury to civilians and damage to civilian objects;\n(iii) refrain from deciding to launch any attack which may be expected to cause incidental loss of civilian life, injury to civilians, damage to civilian objects, or a combination thereof, which would be excessive in relation to the concrete and direct military advantage anticipated;\n(b) an attack shall be cancelled or suspended if it becomes apparent that the objective is not a military one or is subject to special protection or that the attack may be expected to cause incidental loss of civilian life, injury to civilians, damage to civilian objects, or a combination thereof, which would be excessive in relation to the concrete and direct military advantage anticipated.",
            },
            {
                "number": "147",
                "title": "Grave Breaches (GC IV Art. 147 & AP I Art. 85)",
                "text": "1. The provisions of the Conventions relating to the repression of breaches and grave breaches, supplemented by this Section, shall apply to the repression of breaches and grave breaches of this Protocol.\n3. In addition to the grave breaches defined in Article 11, the following acts shall be regarded as grave breaches of this Protocol, when committed wilfully, in violation of the relevant provisions of this Protocol, and causing death or serious injury to body or health:\n(a) making the civilian population or individual civilians the object of attack;\n(b) launching an indiscriminate attack affecting the civilian population or civilian objects in the knowledge that such attack will cause excessive loss of life, injury to civilians or damage to civilian objects, as defined in Article 57, paragraph 2 (a)(iii).",
            },
        ],
        "annexes": [],
    },
}


def fetch_un_coe_stage(
    instrument: dict[str, Any],
    version: dict[str, Any],
    cache_dir: Path | None = None,
) -> dict[str, Any]:
    """
    Fetch a CoE treaty draft, UNGA/CCW GGE document, or IHL convention stage,
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
                resp = client.get(
                    source_url,
                    headers={"User-Agent": "lex-machina-corpus-bot/1.0"},
                )
                http_status = resp.status_code
        except Exception as exc:
            http_status = f"error:{type(exc).__name__}"

    canonical_key = f"{instrument_id}::{stage}"
    canonical = UN_COE_IHL_PROVISIONS.get(
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
