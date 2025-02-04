# Article 6 — ARTICLE 5(1)(E) AI ACT - UNTARGETED SCRAPING OF FACIAL IMAGES

- **Instrument**: EU AI Act
- **Stage**: Commission Guidelines on Prohibited AI Practices (C(2025) 884) (`2025-02-04`)
- **Document Symbol**: `C(2025) 884 final`
- **Akoma Ntoso eId**: `sec_6`
- **Provenance Mode**: `full_primary_pdf`
- **Institutional Author**: European Commission AI Office `<ai-office@ec.europa.eu>`

(222) Article 5(1)(e) AI Act prohibits the placing on the market, putting into service for this
specific purpose, or the use of AI systems that create or expand facial recognition
databases through the untargeted scraping of facial images from the Internet or CCTV
footage.
6.1. Rationale and objectives
(223) The untargeted scraping of facial images from the internet and from CCTV footage
seriously interferes with individuals’ rights to privacy and data protection and deny
those individuals the right to remain anonymous. Recital 43 AI Act therefore justifies
the prohibition established in Article 5(1)(e) AI Act based on the ‘feeling of mass
surveillance’ and the risks of ‘gross violations of fundamental rights, including the right
to privacy’.
6.2. Main concepts and components of the prohibition
Article 5(1)(e) AI Act provides
The following AI practices shall be prohibited:
(e) the placing on the market, the putting into service for this specific purpose, or the
use of AI systems that create or expand facial recognition databases through the
untargeted scraping of facial images from the internet or CCTV footage;
144 The presumption of innocence is a fundamental right enshrined in Article 48 of the EU Charter of Fundamental Rights.
145 As specified by the CJEU, it is not required that this person is made aware of their status as suspect/accused persons by the competent
authorities for the Directive to apply.
74
(224) Several cumulative conditions must be fulfilled for the prohibition in Article 5(1)(e) AI
Act to apply:
(i) The practice must constitute the ‘placing on the market’, ‘the putting into service
for this specific purpose’ or the ‘use’ of an AI system;
(ii) for the purpose of creating or expanding facial recognition databases;
(iii) the means to populate the database are through AI tools for untargeted scraping;
and
(iv) the sources of the images are either from the internet or CCTV footage.
(225) For the prohibition to apply all four conditions must be simultaneously fulfilled. The
first element of placing on the market, putting into service or use of the AI system has
been already analysed in section 2.3. The prohibition, therefore, applies to both
providers and deployers of AI systems, each within their respective responsibilities, not
to place on the market, put into service or use such AI systems. The specific criteria
related to the prohibition of untargeted scraping are further described and analysed
below. The prohibition applies to scraping tools that are placed on the market or being
put into service ‘for this specific purpose’ of untargeted scraping of facial images from
the internet or CCTV footage. This implies that the prohibition does not apply to any
scraping tool with which a database for face recognition may be constructed or
expanded, but only to tools for untargeted scraping.
6.2.1. Facial recognition databases
(226) The prohibition in Article 5(1)(e) AI Act covers AI systems used to create or expand
facial recognition databases. ‘Database’ in this context should be understood to refer to
any collection of data, or information, that is specially organized for rapid search and
retrieval by a computer. A facial recognition database is capable of matching a human
face from a digital image or video frame against a database of faces, comparing it to
images in the database and determining whether there is a likely match between the
two. Such a facial recognition database may be temporary, centralised or decentralised.
Article 5(1)(e) does not require that the sole purpose of the database is to be used for
facial recognition; it is sufficient that the database can be used for facial recognition.
6.2.2. Through untargeted scraping of facial images
(227) ‘Scraping’ typically refers to using web crawlers, bots, or other means to extract data
or content from different sources, including CCTV, websites or social media,
automatically. These tools are software ‘programmed to sift through databases and
extract information and to make use of that information for another purpose.
(228) ‘Untargeted’ relates to a technique that operates like a ‘vacuum cleaner’, absorbing as
much data and information as possible, without targeting specifically and individually
intended subject(s) of the scarping. Scraping indiscriminately harvests data or content.
Thus, the notion of ‘untargeted’ means without a specific focus on a given individual
or group of individuals. The respect of opt-out of internet protocols such as robot.txt
does not affect the untargeted nature of the scraping.
75
(229) If a scraping tool is instructed to collect images or video containing human faces only
of specific individuals or a pre-defined group of persons, then the scraping becomes
targeted, for example to find one specific criminal or to identify a group of victims.
Such scraping is not covered by the prohibition in Article 5(1)(e) AI Act.
(230) For example, the targeted collection of images focusing on a class of victims, by using
crawlers to pick up on images of victims that human traffickers post/advertise on social
media channels, is not covered by the prohibition. Untargeted scraping should be
interpreted in a manner that does not allow circumvention of the prohibition. The
scraping of the Internet or CCTV footage for the creation of a database step-by-step,
thereby selecting specific groups of individuals or other criteria each time, should fall
within the prohibition of Article 5(1)(e) AI Act where the end-result is functionally the
same as pursuing untargeted scraping from the outset.
(231) Where systems combine targeted searches for images or videos with untargeted
searches, the untargeted scraping is prohibited.
6.2.3. From the Internet and CCTV footage
(232) For the prohibition in Article 5(1)(e) AI Act to apply, the source of the facial images
may either be the Internet or CCTV footage. Regarding the internet, the fact that a
person has published facial images of themselves on a social media platform does not
mean that that person has given his or her consent for those images to be included in a
facial recognition database. Examples of scraping facial images from CCTV footage
include images acquired by surveillance cameras operated in places such as airports,
streets, parks, etc.
Example:
A facial recognition software company collects pictures of faces. The photographs held
by the company have been scraped from social media (e.g., Facebook, YouTube,
Twitter, Venmo) with an ‘automated image scraper’ that searches the internet and
detects images containing human faces. It collects those images with any associated
information (such as the source of the image (URL), the geo-localisation, and
sometimes the names of the individuals). The facial features are then extracted from the
images and transformed into mathematical representations, which are hashed for
indexation and future comparison. When a user uploads the image of an individual to
the AI system, that system will determine whether that image matches a face in the
database. The uploaded image will go through the same mathematical transformation
as the scraped images.
(233) Where an AI system receives a picture of a person and searches the face on the internet
for matches, i.e. ‘reverse engineering image search engines’, this will be considered to
be targeted scraping. Moreover, it is questionable whether the matches would appear in
a ‘database’.
6.3. Out of scope
76
(234) The prohibition in Article 5(1)(e) AI Act does not apply to the untargeted scraping of
biometric data other than facial images (such as voice samples). The prohibition does
also not apply where no AI systems are involved in the scraping. Facial image databases
that are not used for the recognition of persons are also out of scope, such as facial
image databases used for AI model training or testing purposes, where the persons are
not identified.
(235) The prohibition in Article 5(1)(e) AI Act does not apply to AI systems which harvest
large amounts of facial images from the internet to build AI models that generate new
images about fictitious persons because such systems would not result in the recognition
of real persons. Such AI systems could fall under the transparency requirements of
Article 50 AI Act.
(236) The prohibition in Article 5(1)(e) AI Act covers AI systems used to create or expand
facial recognition databases. When it comes to existing facial databases built up prior
to the entry into application of the prohibition, which are not further expanded through
AI-enabled untargeted scraping, those databases and their use must comply with the
applicable Union data protection rules.
(237) The prohibition in Article 5(1)(e) AI Act is targeted at the creation or expansion of
facial recognition databases. The concrete act of biometric identification is subject to
specific rules in the AI Act and other relevant Union legislation.
6.4. Interplay with other Union legal acts
(238) In relation to Union data protection law, the untargeted scraping of the internet or CCTV
material to build-up or expand face recognition databases, i.e. the processing of
personal data (collection of data and use of databases) would be unlawful and no legal
basis under the GDPR, EUDPR and the LED could be relied upon.
