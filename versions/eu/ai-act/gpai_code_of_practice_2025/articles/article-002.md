# Article 2 — General-purpose AI models

- **Instrument**: EU AI Act
- **Stage**: Commission Guidelines on General-Purpose AI Model Obligations & Code of Practice (`2025-07-10`)
- **Document Symbol**: `AI Office GPAI Guidelines & CoP (2025)`
- **Akoma Ntoso eId**: `sec_2`
- **Provenance Mode**: `full_primary_pdf`
- **Institutional Author**: European Commission AI Office `<ai-office@ec.europa.eu>`

(12) This section of the guidelines focuses on the concept of a ‘general-purpose AI
model’. It clarifies when the Commission considers a model to be a general-purpose
AI model by providing an indicative criterion (Section 2.1). It also clarifies the
notion of the ‘lifecycle’ of a general-purpose AI model and its implications for the
obligations for providers of general-purpose AI models (Section 2.2). Further, it
clarifies when a general-purpose AI model is a general-purpose AI model with
systemic risk under Articles 51 and 52 AI Act (Section 2.3).
2.1. When is a model a general-purpose AI model?
(13) Article 3(63) AI Act defines a ‘general-purpose AI model’ as ‘an AI model,
including where such an AI model is trained with a large amount of data using self-
supervision at scale, that displays significant generality and is capable of
competently performing a wide range of distinct tasks regardless of the way the
model is placed on the market and that can be integrated into a variety of
downstream systems or applications, except AI models that are used for research,
development or prototyping activities before they are placed on the market’. This
definition lists in a general manner factors that determine whether a model is a
general-purpose AI model. Nevertheless, it does not set out specific criteria that
potential providers can use to assess whether their model is a general-purpose AI
model. Yet it is important to provide conditions that are simple to check to limit the
burden on the many actors that must assess whether they are providers of general-
purpose AI models.
(14) Given the wide variety of capabilities and use cases for general-purpose AI models,
it is not feasible to provide a precise list of capabilities that a model must display
and tasks that it must be able to perform in order to determine whether it is a general-
purpose AI model.
1 Explanatory Notice and Template for the Public Summary of Training Content for general-purpose AI models.
4
(15) Instead, the Commission’s approach is to use the amount of computational resources
used to train the model (‘training compute’, see paragraph 115 for how this notion
should be understood in these guidelines) measured in FLOP as well as the
modalities of the model to set an indicative criterion for when it considers a model
to be a general-purpose AI model. This approach builds on recital 98 AI Act which
specifies that ‘models with at least a billion of parameters and trained with a large
amount of data using self-supervision at scale should be considered to display
significant generality and to competently perform a wide range of distinctive tasks’,
as well as on recital 99 AI Act which clarifies that ‘[l]arge generative AI models are
a typical example for a general-purpose AI model, given that they allow for flexible
generation of content, such as in the form of text, audio, images or video, that can
readily accommodate a wide range of distinctive tasks’.
(16) Training compute has the advantage of combining number of parameters and
number of training examples into a single number that is reasonably straightforward
for providers to estimate. This number is typically proportional to the number
obtained by multiplying these two numbers, allowing a single threshold to be set
rather than separate thresholds for model size and training data size. While training
compute is an imperfect proxy for generality and capabilities, the Commission
considers setting an indicative criterion which includes a training compute threshold
to be the most suitable approach at present. Nevertheless, the Commission’s
approach may change in the future as technology and the market evolve.
Furthermore, the Commission will continue to investigate the availability of other
criteria that could be used to assess generality and capabilities with relative ease,
especially for smaller actors.2
(17) Based on the considerations above, an indicative criterion for a model to be
considered a general-purpose AI model is that its training compute is greater than
1023 FLOP and it can generate language (whether in the form of text3 or audio4),
text-to-image, or text-to-video.
(18) This threshold corresponds to the approximate amount of compute typically used to
train a model with one billion parameters on a large amount of data. While such
models may be trained with varying amounts of compute depending on how much
data is used, 1023 FLOP is typical for models trained on large amounts of data as of
the time of writing (see the examples in Annex A.3).5
(19) The modalities are chosen based on the fact that models trained to generate language
– be it via text or speech (as a type of audio) – are able to use language to
2 In the future, if deemed appropriate, the Commission may take into account benchmarks to determine whether a
model is a general-purpose AI model.
3 The Commission understands the modality of ‘text’ to include ‘code’.
4 The Commission understands the modality of ‘audio’ to include ‘speech’.
5 This value for the threshold was updated from the value proposed in the public consultation for these guidelines.
Previously, the reference examples in Annex A.3 contained several examples of models trained with less than 1023
FLOP. However, these models were trained for research purposes only by non-commercial actors (e.g. academic
groups or research non-profits), and so they were deemed unrepresentative of models that should be in scope of
the AI Act.
5
communicate, store knowledge, and reason. No other modality confers such a wide
range of capabilities. Consequently, models that generate language are typically
more capable of competently performing a wider range of tasks than other models.
Although models that generate images or video typically exhibit a narrower range
of capabilities and use cases compared to those that generate language, such models
may nevertheless be considered to be general-purpose AI models. Text-to-image
and text-to-video models are capable of generating a wide range of visual outputs,
which enables flexible content generation that can readily accommodate a wide
range of distinct tasks.
(20) If a general-purpose AI model meets the criterion from paragraph 17 but,
exceptionally, does not display significant generality or is not capable of
competently performing a wide range of distinct tasks, it is not a general-purpose
AI model. Similarly, if a general-purpose AI model does not meet that criterion but,
exceptionally, displays significant generality and is capable of competently
performing a wide range of distinct tasks, it is a general-purpose AI model.
Example of a model in scope
• A model is trained on a broad range of natural language data (i.e. text) curated and
scraped from the internet and other sources (as is currently typical for language
models) using 1024 FLOP.
o The criterion from paragraph 17 indicates that the model should be a general-
purpose AI model because it can generate text and its training compute is
greater than 1023 FLOP. Training on a broad range of natural language further
indicates that the model should display significant generality and should be
capable of competently performing a wide range of distinct tasks. Therefore,
the model likely is a general-purpose AI model.
Examples of models out of scope
• A model is trained on natural language data, using 1022 FLOP, and is not able to
competently perform a wide range of distinct tasks.
o While the model can generate text, its training compute is not greater than
1023 FLOP. Therefore, the criterion from paragraph 17 indicates that the
model should not be a general-purpose AI model. The fact that the model is
not capable of performing a wide range of distinct tasks confirms that it is not
a general-purpose AI model.
• A model is trained specifically for the task of transcribing speech to text, using 1024
FLOP.
o The model can generate text and its training compute is greater than 1023
FLOP. Therefore, the criterion from paragraph 17 indicates that the model
should be a general-purpose AI model. However, if the model can only
competently perform a narrow set of tasks (transcribing speech), it is not
actually a general-purpose AI model.
6
• A model is trained specifically for the task of generating speech from text, using 1024
FLOP.
o The model can generate speech and its training compute is greater than 1023
FLOP. Therefore, the criterion from paragraph 17 indicates that the model
should be a general-purpose AI model. However, if the model can only
competently perform a narrow set of tasks (generating speech from text), it is
not actually a general-purpose AI model.
• A model is trained specifically for the task of increasing the resolution of images,
using 1024 FLOP.
o The model can generate images and its training compute is greater than 1023
FLOP. Therefore, the criterion from paragraph 17 indicates that the model
should be a general-purpose AI model. However, if the model can only
competently perform a narrow set of tasks (upscaling images), it is not
actually a general-purpose AI model.
• A model is trained specifically for the task of filling in damaged or missing parts of
images, using 1024 FLOP.
o The model can generate images and its training compute is greater than 1023
FLOP. Therefore, the criterion from paragraph 17 indicates that the model
should be a general-purpose AI model. However, if the model can only
competently perform a narrow set of tasks (inpainting images), it is not
actually a general-purpose AI model.
• A model is trained specifically for playing chess or video games, using 1024 FLOP.
o While the model’s training compute is greater than 1023 FLOP, if it cannot
generate text, speech, text-to-image, and text-to-video, the criterion from
paragraph 17 indicates that the model should not be a general-purpose AI
model. If the model can only competently perform a narrow set of tasks
(playing chess or video games), this fact confirms that it is not a general-
purpose AI model.
• A model is trained specifically for modelling weather patterns or physical systems,
using 1024 FLOP.
o While the model’s training compute is greater than 1023 FLOP, if it cannot
generate text, speech, text-to-image, and text-to-video, the criterion from
paragraph 17 indicates that the model should not be a general-purpose AI
model. If the model can only competently perform a narrow set of tasks
(modelling weather patterns or physical systems), this fact confirms that it is
not a general-purpose AI model.
• A model is trained specifically for generating music, based on text prompts including
lyrics, using 1024 FLOP.
o The model can generate speech (in the form of song lyrics) and its training
compute is greater than 1023 FLOP. Therefore, the criterion from paragraph
17 indicates that the model should be a general-purpose AI model. However,
if the model can only competently perform a narrow set of tasks (generating
music, based on text prompts including lyrics) it is not actually a general-
purpose AI model.
• A model is trained specifically for generating sound effects, using 1024 FLOP. It can
generate language (speech), but the quality of the content of the speech generated is
low (e.g. the content is not consistent over the course of a brief conversation).
7
o The model can generate language and its training compute is greater than 1023
FLOP. Therefore, the criterion from paragraph 17 indicates that the model
should be a general-purpose AI model. However, if the model can only
competently perform a narrow set of tasks (sound effects) it is not actually a
general-purpose AI model.
2.2. The lifecycle of a general-purpose AI model
(21) Providers of general-purpose AI models with systemic risk are expected to
‘continuously assess and mitigate systemic risks’, including by ‘taking appropriate
measures along the entire model’s lifecycle’ (recital 114 AI Act). They must also
‘ensure an adequate level of cybersecurity protection for the model and its physical
infrastructure, if appropriate, along the entire model lifecycle’ (recital 115 AI Act).
The notion of the ‘lifecycle’ of a model thus plays an important role for the
obligations for providers of general-purpose AI models with systemic risk.
(22) The iterative and interlinked process through which a provider may develop a
‘model’, for example through techniques such as distillation, quantisation, or
merging of model weights, makes it difficult to clearly delineate a model and its
lifecycle. In light of this challenge, the Commission understands the notion of
‘model’, and consequently its ‘lifecycle’, in a broad sense. In practice, the
Commission considers the lifecycle of a general-purpose AI model to begin at the
start of the large pre-training run.6 Any subsequent development of the model
downstream of this large pre-training run performed by the provider or on behalf of
the provider, whether before or after the model has been placed on the market, forms
part of the same model’s lifecycle rather than giving rise to new models. Different
considerations apply if another actor modifies the model (see Section 3.2). A model
is thus considered to be the same model along its entire lifecycle, i.e. throughout its
development, market availability, and use. In particular, different stages of the
development of a model are not considered to constitute different models.
(23) This approach to the lifecycle of a general-purpose AI model has the implications
described below for the obligations for providers of general-purpose AI models.
• The documentation required under Article 53(1), points (a) and (b), AI Act
must be drawn up for each model placed on the market and kept up to date
throughout its entire lifecycle.
• The copyright policy required under Article 53(1), point (c), AI Act must be
applied throughout the entire lifecycle of each of the provider’s relevant
models. Providers may choose to develop one policy and apply it to all their
relevant models.
6 A large pre-training run is understood as the foundational training run conducted on a large amount of data
to build the model’s general capabilities, which may take place after smaller experimental training runs, and
which may be followed by fine-tuning for specialisation or other post-training enhancements.
8
• The summary of the content used for training required under Article 53(1),
point (d), AI Act must be drawn up and made publicly available for all the
provider’s models placed on the market. The template that has been prepared
by the AI Office specifies circumstances under which the summary must be
updated.
• The systemic risk assessment and mitigation required under Article 55(1) AI
Act must be carried out continuously for each model throughout its entire
lifecycle. This may involve a combination of ongoing measures, as well as
more comprehensive and thorough measures at regular intervals and before
key decisions in the lifecycle of the model. These measures should be
effective, adequate, and proportionate to the systemic risks. The governance
mitigations required under Article 55(1) AI Act must be applied throughout
the entire lifecycle of each of the provider’s relevant models. For some
mitigations, providers may be able to develop them once and then apply
them to all their relevant models.
2.3. When is a general-purpose AI model a general-purpose AI model with systemic risk?
(24) ‘General-purpose AI models with systemic risk’ form a special class of general-
purpose AI models. Providers of such models are subject to additional obligations
concerning the assessment and mitigation of the systemic risks presented by these
models, under Articles 52 and 55 AI Act. The AI Act defines a ‘systemic risk’ as ‘a
risk that is specific to the high-impact capabilities of general-purpose AI models,
having a significant impact on the Union market due to their reach, or due to actual
or reasonably foreseeable negative effects on public health, safety, public security,
fundamental rights, or the society as a whole, that can be propagated at scale across
the value chain’ (Article 3(65) AI Act).
2.3.1. Classification
(25) Under Article 51(1) AI Act, a general-purpose AI model is classified as a general-
purpose AI model with systemic risk if it meets either of the following two
conditions:
• it has ‘high-impact capabilities’, defined as ‘capabilities that match or
exceed those recorded in the most advanced models’ (Article 3(64) AI Act);
• ‘based on a decision of the Commission, ex officio or following a qualified
alert from the scientific panel, it has capabilities or an impact equivalent to
those set out in [the preceding point] having regard to the criteria set out in
Annex XIII’.
(26) From the moment when a general-purpose AI model meets either of the two
conditions above, the model is classified as a general-purpose AI model with
systemic risk and its provider must comply with the relevant obligations.
9
(27) Whether a given general-purpose AI model has high-impact capabilities should be
‘evaluated on the basis of appropriate technical tools and methodologies, including
indicators and benchmarks’, under Article 51(1), point (a), AI Act. These tools and
methodologies are to be further specified by the Commission through adoption of
delegated acts (see paragraph 28). Notwithstanding future adoption of such
delegated acts, Article 51(2) AI Act states that a general-purpose AI model is
‘presumed to have high-impact capabilities pursuant to paragraph 1, point (a),
when the cumulative amount of computation used for its training measured in
floating point operations is greater than 1025.’ This is because the cumulative
amount of computation used for the training of a general-purpose AI model
(‘cumulative training compute’, see paragraph 116 for how this notion should be
understood in these guidelines) measured in FLOP is considered to be a relevant
metric for identifying high-impact capabilities (see recital 111 AI Act).
(28) Under Article 51(3) AI Act, the Commission is empowered to adopt delegated acts,
in line with Article 97 AI Act, to amend the thresholds set out in Article 51(1) and
(2) AI Act. The Commission is also empowered to introduce additional benchmarks
and indicators when necessary, to account for technological advancements – such
as improvements in algorithms or greater hardware efficiency – so that these
thresholds continue to reflect the state of the art.
2.3.2. Notification
(29) When a general-purpose AI model has met or it becomes known that it will meet a
requirement leading to the presumption that the model has high-impact capabilities,7
the provider must notify the Commission in line with Article 52(1) AI Act (see also
recital 112 AI Act). The notification must happen ‘without delay and in any event
within two weeks after that requirement is met or it becomes known that it will be
met’ (Article 52(1) AI Act).
(30) In particular, a notification may be required before training is complete, if the
provider can reasonably foresee that the requirement that leads to the presumption
of the model having high-impact capabilities is reasonably likely to be met. In this
regard, recital 112 AI Act specifies that ‘training of general-purpose AI models
takes considerable planning which includes the upfront allocation of compute
resources and, therefore, providers of general-purpose AI models are able to know
if their model would meet the threshold before the training is completed.’ Since the
‘planning’ and ‘upfront allocation of compute resources’ take place before the start
of the large pre-training run, providers should estimate the cumulative amount of
training compute that they will use before starting this run (see Sections A.1 and A.2
7 In the absence of a delegated act amending the thresholds or supplementing the benchmarks and indicators listed
in Article 51(1) and (2) AI Act, the only possible such requirements are the requirement that the model meets or
will meet the threshold laid down in Article 52(2) AI Act, and the requirement that the model is the result of a
modification of a general-purpose AI model with systemic risk that meets or will meet the threshold laid down in
paragraph 60.
10
of the Annex to these guidelines for how to estimate training compute). Following
this estimation, providers should proceed in the following way.
• If the estimated value meets the threshold laid down in Article 51(2) AI Act,
providers should notify the Commission ‘without delay and in any event
within two weeks’, under Article 52(1) AI Act.
• If the estimated value does not meet the threshold laid down in Article 51(2)
AI Act, providers should in any case closely monitor their actual and
expected compute usage over the course of training and throughout the
model’s entire lifecycle. This is to ensure that they are able to know if and
when the cumulative amount of training compute has met or will meet the
threshold, and that they notify the Commission accordingly under Article
52(1) AI Act.
(31) Under Article 52(1) AI Act, the notification should include ‘the information
necessary to demonstrate that the relevant requirement has been met’. In the case
where the notification has been triggered because the model meets or will meet the
threshold laid down in Article 51(2) AI Act, or because the model is the result of a
modification of a general-purpose AI model with high-impact capabilities that
meets or will meet the threshold laid down in paragraph 60,8 this information should
cover in particular:
• the amount of compute estimated by the provider that has triggered the
requirement to notify, reported in FLOP and with two significant figures
(e.g. 2.3x1025 FLOP);
• a description of the approach used to estimate this amount of compute,
including approaches used to make approximations where precise
information is not available.
2.3.3. Procedure for contesting classification
(32) When a provider notifies the Commission under Article 52(1) AI Act, they ‘may
present, with its notification, sufficiently substantiated arguments to demonstrate
that, exceptionally, although it meets that requirement, the general-purpose AI
model does not present, due to its specific characteristics, systemic risks and
therefore should not be classified as a general-purpose AI model with systemic risk’
(Article 52(2) AI Act). This provision acknowledges that while general-purpose AI
models that meet the threshold laid down in Article 51(2) AI Act or that have high-
impact capabilities typically present systemic risks, there may be cases where this
is not so.
(33) Providers may present arguments aimed at demonstrating that their model does not
or will not present systemic risks by demonstrating that their model does not or will
8 In the absence of a delegated act amending the thresholds or supplementing the benchmarks and indicators listed
in Article 51(1) and (2) AI Act, these two requirements are the only requirements that trigger the obligation to
notify the Commission under Article 52(1) AI Act.
11
not have high-impact capabilities, namely capabilities that ‘match or exceed those
recorded in the most advanced models’ (Article 3(64) AI Act). This is because
systemic risks are ‘specific to high-impact capabilities’ (Article 3(65) AI Act). Such
an approach would be appropriate in cases where the notification has been triggered
because of the presumption that the model has high-impact capabilities (for
example, because the model has met or will meet the threshold laid down in Article
51(2) AI Act), but the provider deems that the presumption is not well-founded for
its model. The Commission notes that the burden of adducing evidence that the
presumption deriving from the fulfilment of the quantitative thresholds should not
apply should be borne by that provider.
(34) As part of justifying why their model does not or will not have high-impact
capabilities and therefore does not or will not present systemic risks, providers
should include information available to them at the time of the notification about
the model’s achieved or anticipated capabilities, including in the form of actual or
forecasted benchmark results (for example based on scaling analyses). To
complement this information and allow the Commission to properly assess whether
the model does not or will not have high-impact capabilities and therefore does not
or will not present systemic risks, providers are strongly advised to include any other
information that may have a bearing on the model’s capabilities, such as model
architecture, number of parameters, number of training examples, data curation and
processing techniques, training techniques, input and output modalities, expected
tool use, and expected context length.
(35) Upon receiving a notification with arguments for why the model does not present
systemic risks, the Commission will assess the arguments and decide whether to
accept or reject them, in line with the rules of procedure of the European
Commission9 and established principles of EU law. In particular, in the case of
rejection, in line with Article 41 of the Charter of Fundamental Rights of the
European Union, providers will have the right to be heard before the decision is
taken (through receiving a draft decision letter in advance), and the right to have
access to their file, while respecting the legitimate interests of confidentiality and of
professional and business secrecy. The Commission’s decision will include reasons
for why the arguments submitted by the provider under Article 52(2) AI Act have
been accepted or rejected.
(36) In the case where the provider’s arguments are aimed at rebutting the presumption
that the model has high-impact capabilities and therefore does not present systemic
risks, the Commission will assess whether the provider has presented sufficiently
substantiated arguments manifestly calling into question this presumption.
(37) High-impact capabilities are, by definition, ‘capabilities that match or exceed those
recorded in the most advanced models’ (Article 3(64) AI Act). Moreover, they
determine whether a general-purpose AI model is classified as a general-purpose AI
model with systemic risk. For this reason, the level of capabilities beyond which a
9 Rules of Procedure of the European Commission.
12
model is considered to have ‘high-impact capabilities’, or equivalently to be
amongst the ‘most advanced models’, is expected to change over time, as
capabilities increase and risks evolve. In particular, the Commission does not
consider it to refer to a fixed level of capabilities.
(38) In its assessment of whether the model is amongst the most advanced models at the
time of the notification, the Commission will take into account the extent to which
the cumulative training compute of the model is indicative of the model being
amongst these models. In this regard, the extent to which the cumulative training
compute of the model exceeds the threshold laid down in Article 51(2) AI Act will
also be taken into account. The Commission will also assess any other elements
beyond cumulative training compute which influence the achieved or expected
capabilities of the model, including forecasted or achieved benchmark scores.
(39) In the case where the provider’s arguments are aimed at demonstrating that their
model does not present systemic risks despite having high-impact capabilities, the
Commission considers that arguments that a model does not present systemic risks
because of mitigations already or planned to be implemented are not suitable
grounds for a model being excluded from classification as a general-purpose AI
model with systemic risk. In those cases, the model still poses systemic risks which
must continuously be assessed and mitigated. Nevertheless, the provider could use
these mitigations as part of the systemic risk mitigation that they must carry out
under Article 55(1) AI Act.
(40) The Commission’s decision to accept or reject the provider’s arguments has the
legal effects set out below.
• If the Commission decides to reject the arguments, the model is confirmed
to be a general-purpose AI model with systemic risk. The provider is subject
to the obligations for providers of general-purpose AI models with systemic
risk from the moment when the model meets the condition laid down in
Article 51(1), point (a), AI Act. In particular, this means that presenting
arguments with the notification does not suspend the provider’s obligations
as providers of general-purpose AI models with systemic risk.
• If the Commission decides to accept the arguments, the general-purpose AI
model is no longer classified as a general-purpose AI model with systemic
risk. The provider is no longer subject to the obligations for providers of
general-purpose AI models with systemic risk from the moment when it is
informed of the acceptance decision. This acceptance decision will require
the provider to renotify the Commission if there is or it becomes known that
there will be a substantial change in any of the facts on which the acceptance
decision was based or it becomes known that the acceptance decision was
based on substantially incomplete, incorrect or misleading information. In
either case, the provider must provide the Commission with all relevant
information, and the Commission may turn its acceptance decision into a
rejection decision, in which case the model becomes a general-purpose AI
model with systemic risk. Moreover, an acceptance decision does not
13
preclude the model later being classified as a general-purpose AI model with
systemic risk via a designation decision by the Commission based on the
criteria set out in Annex XIII AI Act (see Section 2.3.4).
2.3.4. Designation
(41) In addition to the above mechanism whereby a general-purpose AI model is
classified as a general-purpose AI model with systemic risk through having high-
impact capabilities, the AI Act also lays down a designation mechanism.
(42) Specifically, under Article 52(1), Article 51(1), poin
