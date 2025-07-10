# Article 6 — Review and update of the Commission guidelines

- **Instrument**: EU AI Act
- **Stage**: Commission Guidelines on General-Purpose AI Model Obligations & Code of Practice (`2025-07-10`)
- **Document Symbol**: `AI Office GPAI Guidelines & CoP (2025)`
- **Akoma Ntoso eId**: `sec_6`
- **Provenance Mode**: `full_primary_pdf`
- **Institutional Author**: European Commission AI Office `<ai-office@ec.europa.eu>`

(113) The Commission will review these guidelines as soon as it becomes necessary in
the light of practical experience gained by providers of general-purpose AI models
in implementing their obligations, and technological, societal, and market
developments in this area. This also includes any relevant experience from
enforcement actions and interpretations given by the CJEU on the obligations for
providers of general-purpose AI models and other provisions of the AI Act
examined in these guidelines. During its review, the Commission may decide to
withdraw or amend these guidelines. The Commission encourages providers of
general-purpose AI models, national market surveillance authorities (through the
Board), the advisory forum, the scientific panel, the research community, and civil
society organisations to contribute to this process by responding to future calls for
public consultation, workshops, or other opportunities for input.
29
Annex: Training compute of general-purpose AI models
(114) Article 51(2) AI Act lays down a threshold for the compute used to train a general-
purpose AI model that can lead to the model being classified as a general-purpose
AI model with systemic risk. Sections 2.1 and 3.2 also set thresholds involving
training compute. To know whether a model meets any of these thresholds, potential
providers must estimate the relevant amount of compute used for training. This
Annex to the guidelines provides guidance on how they may do so. Annex A.1
specifies what potential providers of general-purpose AI models and of general-
purpose AI models with systemic risk should include when estimating training
compute, while Annex A.2 describes two widely used approaches that potential
providers may use. Annex A.3 estimates the training compute for a number of
models trained with approximately one billion parameters to illustrate the formulae
in Annex A.2 and to justify the threshold that forms part of the indicative criterion
for when a model is a general-purpose AI model (Section 2.1).
A.1. What should be estimated?
(115) In these guidelines, ‘training compute’ of a general-purpose AI model refers to
either:
• the total amount of compute directly contributing to parameter updates in
the model if the model is not a general-purpose AI model with systemic risk;
• the cumulative amount of compute used to train the model if, and for the
purpose of assessing whether, the model is a general-purpose AI model with
systemic risk.
(116) Under the AI Act, regarding how ‘cumulative training compute’ should be
understood, recital 111 AI Act specifies that ‘the cumulative amount of computation
used for training includes the computation used across the activities and methods
that are intended to enhance the capabilities of the model prior to deployment, such
as pre-training, synthetic data generation and fine-tuning’. Given the wide variety
of such ‘activities and methods’, and their rapid evolution, it is not feasible to
provide a precise and exhaustive list of what should and should not be included.
Instead, the Commission considers that providers should, as a general rule, account
for all compute that contributed or will contribute to the model’s capabilities. In
particular, any compute directly contributing to parameter updates in the model
should be included.
(117) If the model is trained on synthetic data that is not publicly accessible, the forward
passes used to generate the data, including discarded data, should be included in the
estimation of the cumulative training compute. For example, if 100 samples were
generated and only the top 10 samples were selected for training, the compute used
to generate all 100 samples should be counted, since the compute used to generate
all 100 samples was necessary to create the selected 10.
(118) Where a model has been created by combining model weights, for example via
model weight merging or model weight averaging, or through integrating pre-
30
existing model weights, for example through weight initialisation, the training
compute used to train the combined model weights should be included in the
estimation of the cumulative training compute of the model.
(119) By contrast, the following are examples of compute which need not be included in
the estimation of the cumulative training compute. This list may change as
technology evolves:
• compute used to generate synthetic data which is publicly accessible, since
it may be indistinguishable from other publicly accessible data;
• compute spent on purely diagnostic processes that do not contribute to
enhancing model capabilities, such as model evaluations or red-teaming;
• compute whose expenditure contributes to enhancing model capabilities
only through lessons learnt by humans, such as compute spent on
exploratory research projects that result in more efficient training
techniques, or on experiments in synthetic data generation that fail and
whose results are discarded;
• compute used to train parent model(s) used in distillation (whether or not the
parent model coincides with the concerned model);
▪ compute used to train auxiliary model(s) such as value functions
or reward models (whether or not the auxiliary model coincides
with the concerned model);
• recomputation of activations to save memory.
A.2. How should training compute be estimated?
(120) Providers may choose any method to estimate the relevant amount of training
compute, so long as the estimated amount is, in the providers’ best judgement,
accurate within an overall error margin of 30% of the reported estimate. This is to
account for the difficulties providers may face in obtaining precise estimates of their
model’s cumulative training compute, for example, when estimates are made before
training of the model is completed. Providers are nevertheless expected to document
the assumptions made in making their estimations, including the method of
estimation, and the associated uncertainties.
(121) Providers may choose to estimate the relevant amount of training compute by
tracking graphics processing unit (‘GPU’) usage (hardware-based approach) or by
estimating operations directly based on the relevant model’s architecture
(architecture-based approach), as appropriate to what is being estimated.
(122) Regardless of the method of estimation, all operations should be counted equally,
independently of floating-point precision.
31
A.2.1. Hardware-based approach
(123) To estimate training compute using the hardware-based approach, the potential
provider of a general-purpose AI model or general-purpose AI model with systemic
risk should first estimate:
• the number 𝑁 of GPUs or other hardware units used or expected to be used;
• the total duration of use 𝐿, achieved or expected (measured in seconds);
• the peak theoretical performance 𝐻 of the GPUs or other hardware units
used or expected to be used (measured in FLOP/second), calculated via
weighted average if different types of GPUs or hardware units are used with
different peak theoretical performances (where the weights are determined
by the number of hardware units of each type);
• the average percentage of GPU utilisation 𝑈 achieved or expected to be
achieved for the duration of use.
(124) If all hardware units 𝑁 are used for the entirety of the duration 𝐿, the corresponding
amount of training compute 𝐶 (measured in FLOP) can then be calculated according
to the following formula:
𝐶 = 𝑁 ⋅ 𝐿 ⋅ 𝐻 ⋅ 𝑈.
(125) If different numbers of hardware units are used for different periods of time, the
formula above can be applied to each period of time for which a constant number
of hardware units is used (provided that the total time matches the total duration of
training). The resulting estimates can then be summed up to yield the total amount
of training compute.
(126) Annex A.3 includes example calculations using this approach.
A.2.2. Architecture-based approach
(127) This approach consists in directly estimating the number of operations performed
based on the relevant model’s architecture.
(128) For example, essentially all general-purpose AI models or potentially general-
purpose AI models today are based on neural networks that are trained through a
succession of forward and backward passes. For such models, the corresponding
amount of training compute 𝐶 (measured in FLOP) is the product of the number of
full passes (one full pass is the combination of a forward and backward pass) made
during training with the total number of operations performed in a full pass, i.e.:
𝐶 = Number of forward passes made during training ⋅ number of operations/full pass.
32
(129) For some dense large14 language models based on the transformer architecture, the
amount of training compute 𝐶 may be approximated by the following formula:
𝐶 ≈ 6 ⋅ 𝑃 ⋅ 𝐷,
where 𝑃 refers to the total number of model parameters and 𝐷 refers to the total
number of training tokens used for training.15
(130) Annex A.3 includes example calculations using this approach.
A.3. Training compute of models with approximately one billion parameters
(131) The threshold that forms part of the indicative criterion for when a model is a
general-purpose AI model (Section 2.1) has been informed by the estimated amount
of compute used in practice to train widely used models with approximately one
billion parameters. Although the models and their providers are not referred to by
name, information relevant to this estimate is shared below.
(132) The estimated compute used to train the investigated models is as follows:
• Model A (a language model with 3.8 billion parameters): 7.5 ⋅ 1022 FLOP;
• Model B (an image diffusion model with 1 billion parameters): 1023 FLOP;
• Model C (a language model with 600 million parameters): 1.3 ⋅ 1023 FLOP;
• Model D (a language model with 1.5 billion parameters): 1.7 ⋅ 1023 FLOP;
• Model E (a language model with 1.7 billion parameters): 3.7 ⋅ 1023 FLOP;
• Model F (a language model with 2.5 billion parameters): 1.8 ⋅ 1023 FLOP;
• Model G (a language model with 2.6 billion parameters): 1.6 ⋅ 1023 FLOP;
• Model H (a language model with 1 billion parameters): 6.6 ⋅ 1023 FLOP.
(133) The values above have been obtained via the following calculations, which also
serve to illustrate the two estimation methods described in Annex A.2.
(134) Model A. Architecture-based approach: Model A is a language model with a
transformer decoder architecture and 3.8 billion parameters, trained on 3.3 trillion
tokens. The approximation from Annex A.2.2 yields:
𝐶 ≈ 6 ⋅ 𝑃 ⋅ 𝐷 = 6 ⋅ 3.8 ⋅ 109 ⋅ 3.3 ⋅ 1012 ≈ 7.5 ⋅ 1022 FLOP.
(135) Model B. Hardware-based approach: Model B is a diffusion model for image
generation. According to its model card it was trained for a total of 200,000 GPU
hours on 40GB A100 GPUs. This implies a product 𝑁𝐿 of number of GPUs 𝑁 and
total training duration of 𝐿 equal to 𝑁𝐿 = 200,000 ⋅ 3,600 seconds. Assuming a
peak performance of 300 TFLOP/second and GPU utilisation of 50%, the
approximation from Annex A.2.1 yields:
14 A model based on a dense transformer architecture should be considered large if its number of parameters is
significantly larger than one twelfth of the number of tokens in the input context. This ensures that the contribution
to the training compute coming from the context-dependent compute is negligible in comparison to the
contribution coming from the non-embedding compute and which equals 6𝑃𝐷 (see for example the reference in
footnote 16).
15 See for example Kaplan, J., et al, Scaling laws for neural language models, arXiv preprint 2001.08361, 2020.
33
𝐶 = 𝑁 ⋅ 𝐿 ⋅ 𝐻 ⋅ 𝑈 = 2 ∙ 105 ∙ 3600 ∙ 3 ∙ 1014 ∙ 0.5 ≈ 1023 FLOP.
(136) Model C. Architecture-based approach: Model C is a language model with a
transformer decoder architecture and 600 million parameters, trained on 36 trillion
tokens. The approximation from Annex A.2.2 yields:
𝐶 ≈ 6 ⋅ 𝑃 ⋅ 𝐷 = 6 ⋅ 0.6 ⋅ 109 ⋅ 36 ⋅ 1012 ≈ 1.3 ⋅ 1023 FLOP.
(137) Model D. Architecture-based approach: Model D is a language model with a
transformer decoder architecture and 1.54 billion parameters, trained on 18 trillion
tokens. The approximation from Annex A.2.2 yields:
𝐶 ≈ 6 ⋅ 𝑃 ⋅ 𝐷 = 6 ⋅ 1.54 ⋅ 109 ⋅ 18 ⋅ 1012 ≈ 1.7 ⋅ 1023 FLOP.
(138) Model E. Architecture-based approach: Model E is a language model with a
transformer decoder architecture and 1.7 billion parameters, trained on 36 trillion
tokens. The approximation from Annex A.2.2 yields:
𝐶 ≈ 6 ⋅ 𝑃 ⋅ 𝐷 = 6 ⋅ 1.7 ⋅ 109 ⋅ 36 ⋅ 1012 ≈ 3.7 ⋅ 1023 FLOP.
(139) Model F. Architecture-based approach: Model F is a language model with a
transformer decoder architecture and 2.5 billion parameters, trained on 12 trillion
tokens. The approximation from Annex A.2.2 yields:
𝐶 ≈ 6 ⋅ 𝑃 ⋅ 𝐷 = 6 ⋅ 2.5 ⋅ 109 ⋅ 12 ⋅ 1012 ≈ 1.8 ⋅ 1023 FLOP.
(140) Model G. Architecture-based approach: Model G is a language model with a
transformer decoder architecture and 2.6 billion parameters, trained on 61 billion
tokens for 164 epochs, i.e. a total of about 10 trillion training tokens. The
approximation from Annex A.2.2 yields:
𝐶 ≈ 6 ⋅ 𝑃 ⋅ 𝐷 = 6 ⋅ 2.6 ⋅ 109 ⋅ 10 ⋅ 1012 ≈ 1.6 ⋅ 1023 FLOP.
(141) Model H. Hardware-based approach: Model H is a language model. According to
its model card, Model H was trained for a total of 370,000 GPU hours on 80GB
H100 GPUs. Assuming a peak performance of 989 TFLOP/second and GPU
utilisation as previously, the approximation from Annex A.2.1 yields:
𝐶 = 𝑁 ⋅ 𝐿 ⋅ 𝐻 ⋅ 𝑈 = 3.7 ∙ 105 ∙ 3600 ∙ 9.89 ∙ 10^14 ∙ 0.5 = 6.6 ⋅ 1023 FLOP.
