Rawnaque et al. Brain Inf. (2020) 7:10 Brain Informatics
https://doi.org/10.1186/s40708-020-00109-x
REVIEW Open Access
Technological advancements
and opportunities in Neuromarketing:
a systematic review
Ferdousi Sabera Rawnaque1*, Khandoker Mahmudur Rahman2, Syed Ferhat Anwar3, Ravi Vaidyanathan4,
Tom Chau5, Farhana Sarker6 and Khondaker Abdullah Al Mamun1,7
Abstract
Neuromarketing has become an academic and commercial area of interest, as the advancements in neural record-
ing techniques and interpreting algorithms have made it an effective tool for recognizing the unspoken response
of consumers to the marketing stimuli. This article presents the very first systematic review of the technological
advancements in Neuromarketing field over the last 5 years. For this purpose, authors have selected and reviewed a
total of 57 relevant literatures from valid databases which directly contribute to the Neuromarketing field with basic
or empirical research findings. This review finds consumer goods as the prevalent marketing stimuli used in both
product and promotion forms in these selected literatures. A trend of analyzing frontal and prefrontal alpha band sig-
nals is observed among the consumer emotion recognition-based experiments, which corresponds to frontal alpha
asymmetry theory. The use of electroencephalogram (EEG) is found favorable by many researchers over functional
magnetic resonance imaging (fMRI) in video advertisement-based Neuromarketing experiments, apparently due to
its low cost and high time resolution advantages. Physiological response measuring techniques such as eye tracking,
skin conductance recording, heart rate monitoring, and facial mapping have also been found in these empirical stud-
ies exclusively or in parallel with brain recordings. Alongside traditional filtering methods, independent component
analysis (ICA) was found most commonly in artifact removal from neural signal. In consumer response prediction and
classification, Artificial Neural Network (ANN), Support Vector Machine (SVM) and Linear Discriminant Analysis (LDA)
have performed with the highest average accuracy among other machine learning algorithms used in these litera-
tures. The authors hope, this review will assist the future researchers with vital information in the field of Neuromarket-
ing for making novel contributions.
Keywords: Neuromarketing, Neural recording, Machine learning algorithm, Brain computer interface, Marketing
1 Introduction Without effective marketing, a good product fails to
Neuromarketing, an application of the non-invasive inform, engage and sustain its targeted audiences [1].
brain–computer interface (BCI) technology, has emerged The expanding economy with new businesses is continu-
as an interdisciplinary bridge between neuroscience and ously evolving with changing consumer preferences. It
marketing that has changed the perception of market- is hard for the businesses to grow and sustain without
ing research. Marketing is the channel between prod- having quantitative or qualitative assessment from their
uct and consumers which determines the ultimate sale. consumers. Newly launched products need even more
effective marketing to successfully enter into a com-
*Correspondence: frawnaque@umassd.edu petitive market. However, traditional marketing renders
1 Advanced Intelligent Multidisciplinary Systems Lab, Institute only by posteriori analysis of consumer response. Con-
of Advanced Research, United International University, Dhaka, Bangladesh
ventional market research depends on surveys, focus
Full list of author information is available at the end of the article
© The Author(s) 2020. This article is licensed under a Creative Commons Attribution 4.0 International License, which permits use, sharing,
adaptation, distribution and reproduction in any medium or format, as long as you give appropriate credit to the original author(s) and
the source, provide a link to the Creative Commons licence, and indicate if changes were made. The images or other third party material
in this article are included in the article’s Creative Commons licence, unless indicated otherwise in a credit line to the material. If material
is not included in the article’s Creative Commons licence and your intended use is not permitted by statutory regulation or exceeds the
permitted use, you will need to obtain permission directly from the copyright holder. To view a copy of this licence, visit http://creat iveco
mmons .org/licen ses/by/4.0/.

Rawnaque et al. Brain Inf. (2020) 7:10 Page 2 of 19
group discussion, personal interviews, field trials and in 2012 to bridge the gap between academicians and
observations for collecting consumer feedback [2]. These Neuromarketers, and it is promoting Neuromarket-
approaches have the limitations of time requirement, ing research across the world with its annual event of
high cost and unreliable information, which can often Neuromarketing World Forum [11, 12]. It may be pro-
produce inaccurate results. In contrast to the traditional posed that further dialogue may continue under such a
marketing research techniques, Neuromarketing allows platform for further industry–academia collaboration.
capturing consumers’ unspoken cognitive and emotional Evidently, more than 150 consumer neuroscience com-
response to various marketing stimuli and can forecast panies are commercially operating across the globe and
consumers’ purchase decisions. big brands (Google, Microsoft, Unilever, etc.) are using
Neuromarketing uses non-invasive brain signal record- their insights to impact their consumers in a tailored and
ing techniques to directly measure the response of a efficient way. Academic research, especially the high ana-
customer’s brain to the marketing stimuli, supersed- lytical accuracy from the engineering part of Neuromar-
ing the traditional survey methods [3]. Functional mag- keting has garnered this breakthrough and acceptance
netic resonance (fMRI), electroencephalography (EEG), over the world. Hence, reviewing the building blocks of
magnetoencephalography (MEG), transcranial mag- Neuromarketing is essential to evaluate its scopes and
netic stimulator (TMS), positron emission tomography capacities, and to contribute new perspective in this
(PET), functional near-infrared spectroscopy (fNIRS) etc. field. Numerous literature reviews have been published
are some examples of neural recording devices used in focusing the theoretical aspect of consumer neurosci-
Neuromarketing research. By obtaining neuronal activ- ence, such as marketing, business ethics, management,
ity from the brain using these devices, one can explore psychology, consumer behavior, etc. [13–15]. However,
the cognitive and emotional responses (i.e., like/dislike, systematic literature review from the engineering per-
approach/withdrawal) of a customer. Different stimuli spective with a focus on neural recording tools and inter-
trigger associated response in a human brain and the pretational methodologies used in this field is absent. In
response can be tracked by monitoring the change in this regard, our article sets its premises to answer the fol-
neuronal signals or brainwaves [4]. Further, the signal lowing questions:
and image processing techniques and machine learning
algorithms have enabled the researchers to measure, ana- – What are the types of marketing stimuli currently
lyze and interpret the possible meanings of brainwaves. being used in Neuromarketing?
This opens a new door to detect, analyze and predict – What are the brain regions activated by these mar-
the buying behavior of customers in marketing research. keting stimuli?
Now with the help of brain–computer interface, the men- – What is the best brain signal recording tool currently
tal states of a customer, i.e., excitement, engagement, being used in Neuromarketing research?
withdrawal, stress, etc., while experiencing a market- – How are these brain signals preprocessed for further
ing stimuli can be captured [5]. Besides these brain sig- analysis?
nal recording techniques, Neuromarketing also utilizes – And what are the current methods or techniques
physiological signals, i.e., eye tracking, heart rate and used to interpret these brain signals?
skin conductance measurements to gather the insight of
audience’s physiological responses due to encountering These questions will allow us to gain a comprehensive
stimuli. These neurophysiological signals with advanced knowledge on the up-to-date research scopes and tech-
spectral analysis and machine learning algorithms can niques in consumer neuroscience. After this brief intro-
now provide nearly accurate depiction of consumers’ duction, our methodology of conducting this systematic
preferences and likes/dislikes [6–8]. review will be presented, followed by the state-of-the-art
Early years of Neuromarketing generated a contro- findings corresponding to the aforementioned questions
versy between the academician and the marketers due and synthesis of the important results. We concluded this
to its high promises and lack of groundwork. From review with relevant inference from synthesized result
the claim of peeping into the consumer mind to find- and a recommendation for future researchers.
ing the buy buttons of human brain, Neuromarketing
has long been under the scrutiny of the academicians 2 Methodology
and researchers [9, 10]. However, academic research in
The systematic literature review is a process in which
this field has started to pile up and the scope of Neuro-
a body of literature is collected, screened, selected,
marketing to reveal and predict consumer behavior is
reviewed and assessed with a pre-specified objective for
gradually becoming evident. Neuromarketing Science
the purpose of unbiased evidence collection and to reach
and Business Association (NMSBA) was established
an impartial conclusion [16]. Systematic review has the

R awnaque et al. Brain Inf.            (2020) 7:10  Page 3 of 19
obligation to explicitly define its research question and to  internet  by  using  the  search  item  “Neuromarketing”
address inclusion–exclusion criteria for setting the scope  and “Neuro-marketing” in valid databases. Among the
of the investigation. After exhaustive search of existing  screened  publications,  Table  1  presents  the  database
literatures, articles should be selected based on their rel- source of selected 57 research articles including book
evance, and the results of the selected studies must be  chapters, which directly contribute to the Neuromarket-
synthesized and assessed critically to achieve clear con- ing field with basic or empirical research findings.
clusions [16]. As for the aggregation of relevant existing literatures,
In this systematic review, we would like to explore  the researchers defined that the search for articles would
the marketing stimuli used in Neuromarketing research  be performed in six databases—Science Direct, Emer-
articles over the last 5 years with their triggered brain  ald Insight, Sage, IEEE Xplore, Wiley Online Library,
regions. We would also like to focus on the technologi- and Taylor Francis Online. After the initial article accu-
cal tools used to capture brain signals from these regions,  mulation,  the  articles  were  exhaustively  screened  by
and finally deliberate on signal processing and analytical  the authors by reviewing their title, abstract, keywords
methodologies used in these experiments. and scope to match the objective of this research. Once
Therefore, the inclusion criteria defined here are as  the studies met our aforementioned inclusion criteria,
follows: they were selected for further review and critical analy-
sis. Table 2 classifies the selected articles in terms of the
–  Literatures must be published in the field of Neuro- aforementioned dimensions.
By exploring the articles selected to develop this sys-
marketing from 2015 to 2019.
–  Studies must use brain–computer interface and/or  tematic review, it was possible to successfully categorize
other physiological signal recording device in their  the trends and advancements in Neuromarketing field in
| Neuromarketing experiments. |     | following dimensions: |     |     |     |
| --------------------------- | --- | --------------------- | --- | --- | --- |
–  Studies must have experimental findings from neu-
ral and/or biometric data used in Neuromarketing    i.  Marketing  stimuli  used  in  Neuromarketing
| research. |     | research |     |     |     |
| --------- | --- | -------- | --- | --- | --- |
 ii.  Activation of the brain regions due to marketing
| The exclusion criteria for this review are set as: |     | stimuli |     |     |     |
| -------------------------------------------------- | --- | ------- | --- | --- | --- |
 iii.  Neural response recording techniques
 iv.  Brain signal processing in Neuromarketing
–  Any other literature review on Neuromarketing are
excluded from this review.  v.  Machine learning applications in Neuromarketing.
–  Book chapters are excluded from this review. Since
Neuromarketing  is  comparatively  a  new  research  Some  of  these  Neuromarketing  studies  have  used
field, alongside relevant academic journal articles,  eye tracking, heart rate, galvanic skin response, facial
book  chapters  conducting  empirical  experiments  action  coding,  etc.,  with  or  without  brain  signal
using BCI can only be included. recording techniques to gauge the consumer’s hidden
–  Literatures written/published in any language other  response. As they are the response from autonomous
than English are excluded from this article. nervous system (ANS), they have proven themselves
|     |     | as  successful  | means  of  exploring  | consumer’s  | focus,  |
| --- | --- | --------------- | --------------------- | ----------- | ------- |
To  serve  the  purpose  of  this  systematic  literature  arousal, attention and withdrawal actions. Hence, this
review, a total of 931 articles were found across the  study  includes  articles  those  empirically  used  these
Table 1 Number of articles found and selected
Name of the database Results: search “Neuromarketing” Results: search “Neuro-marketing” Articles selected
| Science direct        | 281              | 55               |     | 12                 |     |
| --------------------- | ---------------- | ---------------- | --- | ------------------ | --- |
| Wiley online          | 111              | 11               |     | 7                  |     |
| Emerald insight       | 115              | 8                |     | 14                 |     |
| IEEE                  | 34               | 0                |     | 14                 |     |
| Sage                  | 12               | 15               |     | 6                  |     |
| Taylor Francis online | 106              | 36               |     | 4                  |     |
|                       | Total found: 806 | Total found: 125 |     | Total selected: 57 |     |

Rawnaque et al. Brain Inf. (2020) 7:10 Page 4 of 19
Table 2 Studies selected on the dimensions of this review
Dimensions Published articles
i. Marketing stimuli used in Neuromarketing Product Chew et al. [17], Yadava et al. [18], Rojas et al. [19], Pozharliev [20], Touchette
and Lee [21], Marques et al. [22], Shen et al. [23], Çakir et al. [24], Hubert
et al. [25], Hsu and Chen et al. [26], Hoefer et al. [27], Gurbuj and Toga [28],
Wriessnegger et al. [29], Wang et al. [30], Wolfe et al. [31], Bosshard et al. [32],
Fehse et al. [33].
Price Çakar et al. [34], Marques et al. [22], Çakir et al. [24], Gong et al. [35], Pilelienė
and Grigaliūnaitė [36], Hsu and Chen [26], Boccia et al. [37], Venkatraman
et al. [38], Baldo et al. [39].
Promotion Soria Morillo et al. [40], Yang et al. [41], Cherubino et al. [42], Soria Morillo
et al. [43], Vasiljević et al. [44], Yang et al. [45], Pilelienė and Grigaliūnaitė
[36], Daugherty et al. [46], Royo et al. [47], Etzold et al. [48], Chen et al.
[49], Casado-Aranda et al. [50], Randolph and Pierquet [51], Nomura and
Mitsukura [52], Ungureanu et al. [53], Goyal and Singh [54], Oon et al. [55],
Singh et al. [56].
ii. Activation of brain region due to marketing stimuli Soria Morillo et al. [40], Chew et al. [17], Cherubino et al. [42], Soria Morillo
et al. [43], Çakar et al. [34], Boksem and Smitds [57], Bhardwaj et al. [58], Ven-
katraman et al. [38], Touchette and Lee [21], Yang et al. [45], Marques et al.
[22], Gong et al. [35], Gordon et al. [59], Krampe et al. [60], Hubert et al. [25],
Çakir et al. [24], Holst and Henseler [61], Hsu and Cheng [62], Hoefer et al.
[27], Chen et al. [49], Casado-Aranda et al. [50], Wang et al. [30], Jain et al.
[63], Wolfe et al. [31], Bosshard et al. [32], Fehse et al. [33].
iii. Neural response recording techniques EEG Soria Morillo et al. [40], Yang et al. [41], Chew et al. [17], Cherubino et al. [42],
Soria Morillo et al. [43], Yadava et al. [18], Doborjeh et al. [64], Çakar et al.
[34], Kaur et al. [65], Baldo et al. [19], Boksem and Smitds [57], Pozharliev
et al. [20], Venkatraman [38], Touchette and Lee [21], Yang et al. [45], Pilelienė
and Grigaliūnaitė [36], Shen et al. [23], Daugherty et al. [46], Royo et al. [47],
Gong et al. [35], Gordon et al. [59], Hsu and Chen et al. [26], Hoefer et al. [27],
Randolph and Pierquet [51], Nomura and Mitsukura [52], Bhardwaj et al.
[58], Fan and Touyama [66], Rakshit and Lahiri [67], Jain et al. [63],Ogino and
Mitsukura [68], Oon et al. [55], Bosshard et al. [32].
fMRI Venkatraman et al. [38], Marques et al. [22], Hubert et al. [25], Hsu and Cheng
[62], Chen et al. [49], Casado-Aranda et al. [50], Wang et al. [30], Wolfe et al.
[31], Fehse et al. [33].
fNIRS Çakir et al. [24], Krampe et al. [60].
EMG Missagila et al. [69]
Eye tracking Venkatraman [38], Rojas et al. [19], Pilelienė and Grigaliūnaitė [36], Çakar et al.
[34], Ceravolo et al. [70], Ungureanu et al. [53]
Galvanic skin Cherubino et al. [42], Çakar et al. [34], Magdin et al. [71], Goyal and Singh [54],
response, Singh et al. [56].
heart rate
iv. Brain signal processing in Neuromarketing Cherubino et al. [42], Bhardwaj et al. [53], Venkatraman [38], Pozharliev et al.
[20], Boksem and Smitds [57], Wriessnegger et al. [29], Fan and Touyama
[66], Pilelienė and Grigaliūnaitė [36], Yadava et al. [18], Baldo et al. [19],
Clerico et al. [72], Chen et al. [49], Casado-Aranda et al. [50], Hsu and Cheng
[62], Taqwa et al. [73], Bhardwaj et al. [58],Wang et al. [30], Rakshit and Lahiri
[67], Goyal and Singh [54], Jain et al. [63], Oon et al. [55], Fehse et al. [33],
v. Machine learning applications in Neuromarketing Soria Morillo et al. [40], Yang et al. [41], Chew et al. [17], Soria Morillo et al. [43],
Yadava et al. [18], Doborjeh et al. [64], Gordon [59], Gurbuj and Toga [28],
Wriessnegger et al. [29], Wang et al. [30], Taqwa et al. [73], Bhardwaj et al.
[58], Randolph and Pierquet [51], Fan and Touyama [66], Rakshit and Lahiri
[67], Goyal and Singh [54], Jain et al. [63], Ogino and Mitsukura [68], Oon
et al. [55], Singh et al. [56].
tools to answer Neuromarketing questions, since this 3 Systematic review on the advancements
study mainly focuses on the engineering perspective. of Neuromarketing
Interpreting the neural data with only statistical analy- Neuromarketing research utilizes marketing strategies in
sis has been out of scope of this paper. the form of stimuli, and aims to invoke, capture and ana-
lyze activities occurring in different brain regions while

R awnaque et al. Brain Inf. (2020) 7:10 Page 5 of 19
subjects experience these stimuli. To conduct a system- of research, the authors used mathematical model (Gie-
atic review on this matter, it is important to recall the lis superformula) to create 3D bracelet-like objects.
interconnection between brain functions with human Their study displayed 3D shapes appear like bracelets as
behavior and actions triggered by the external stimuli. the product to subjects. Using the 3D shapes gave the
The knowledge of brain anatomy and the physiologi- authors an advantage to produce as many of 60 bracelet
cal functions of brain areas as well as the physiological shapes to conduct the research on. Another new prod-
response due to external stimuli along with it, makes uct was the E-commerce products presented to the test
it possible to model brain activity and predict hidden subjects by Yadava et al. and Çakar et al. [18, 34]. Yadava
response. For this purpose, current neural imaging sys- et al. proposed a predictive modeling framework to
tems and neural recording systems have contributed understand consumer choice towards E-commerce prod-
much to capture the true essence of consumer prefer- ucts in terms of “likes” and “dislikes” by analyzing EEG
ences. This section will discuss the marketing stimuli, signals. In showing E-commerce product, they showed a
their targeted brain regions, neural and physiological total of 42 product images to the test participants. These
signal capturing technologies used over the last 5 years product images were mainly of apparels and accessory
in Neuromarketing research. Comparing these signals items such as shirts, sweaters, shoes, school bags, wrist
with their associated anatomical functionality some stud- watches, etc. The test participants were asked to disclose
ies have already reached high accuracy. A number of the their preference in terms of likes and dislikes after view-
selected studies have used machine learning techniques ing the items [18]. Çakar et al. used both product and
to predict like/dislike and possible preference from the price to explore the experience during product search of
test subjects. first-time buyers in E-commerce. To motivate the partici-
For the purpose of Neuromarketing experiments, the pants, this research provided each participants around
following literatures selected right-handed participants, 73 USD as a gift card to use during the experiment. The
with normal or corrected-to-normal vision, free of cen- test participants were asked to search and select three
tral nervous system influencing medications and with no products of their interest from an e-commerce website
history of neuropathology. and reach the maximum of their gift card limit to acti-
vate. Test subjects often experienced negative emotion
3.1 Marketing stimuli used in Neuromarketing while being unable to find necessary buttons such as “add
As Neuromarketing is a focus of marketers and consumer to cart” or “sorting options” [34]. These Neuromarketing
behavior researchers, different strategies from market- experiments on E-commerce products may help develop-
ing have been applied in Neuromarketing and they are ers to build better user experience. Retail businesses lose
being investigated for quantitative assessment from neu- large amount of money when they invest in the wrong
rological data. Nemorin et al. asserts that Neuromarket- product. Among retail products, shoes have thousands
ing differentiates from any other marketing models as of blueprints for manufacturing. Producing thousands
it bypasses the thinking procedures of consumers and of shoes of different designs to satisfy consumers can be
directly enters their brain [74]. Over the last 5 years, laborious and unprofitable since a large number of the
Neuromarketing stimuli has been mainly in two forms— designs turn out to be failures. Baldo et al. directly used
products with/without price, and promotions. Product 30 existing image of shoe designs to show the test sub-
can be defined as physical object or service that meets jects to and to choose from a mock shop showing on the
the consumer demand. In Neuromarketing, product can screen [39]. EEG signals were recorded during the whole
be physical such as tasting a beverage to conceptual like shoe selection time and then subjects were asked to rate
a 3D (three dimensional) image of the product. Price in the shoes in a rank of 1 to 5 of Likert scale. This experi-
Neuromarketing experiments is mostly seen as a stimuli ment helped realize brain response-based prediction can
is most of the time intermingled with product or pro- supersede self-report-based methods, as the simulation
motion. However, it plays an important role that deter- on sales data showed 12.1% profit growth for survey-
mines the decision of test subjects to buy or not to buy based prediction, and 36.4% profit growth for the brain
the product [75]. response-based prediction.
Consumer response to a product has been recognized Similar to the shoe experiment, Touchette and Lee [21]
by either physically experiencing the product or by visu- experimented on the choice of apparel products among
alizing the image of it. To understand the user esthetics young adults, based on Davidson’s frontal asymmetry
of 3D shapes, Chew et al. [17], used virtual 3D bracelet theory. EEG signals were recorded while 34 college stu-
shapes in motion and recorded the brain response of dents viewed three attractive and three unattractive
test subjects with EEG with motion. As 3D visualiza- apparel products on a high-resolution computer screen
tion of objects for preference recognition is a new area in a random order. Pozharliev et al. [20] experimented

Rawnaque et al. Brain Inf. (2020) 7:10 Page 6 of 19
on the emotion associated with visualizing luxury brand decision-making [35]. Hsu and Chen used price as a con-
products vs. regular brand products. The experiment dis- trol variable in their wine tasting experiment. As price
played 60 luxury items and 60 basic brand items to 40 plays a pivotal role in purchase decision, two wines were
female undergraduate students to recognize the brain selected of approximately equal price $15. Then the EEG
response of seeing high emotional value (luxury) prod- signals of test subjects were recorded during the wine
ucts in social vs. alone atmosphere. The study found tasting session [26].
that, luxury brand products invoked a higher emotional Promotion is the communication from the marketers’
value in social atmosphere which could be utilized by the end to influence the purchase decision of consumers [75].
marketers. Bosshard et al. and Fehse et al. experimented In Neuromarketing research, promotion is usually found
on brand images and the comparison between the brain as the TV commercials and short movies for advertise-
responses associated with preferred and not preferred ment. One of the key focus of Neuromarketers is to
brands [32, 33]. In the study performed by Bosshard et al., evaluate the consumer engagement of advertisements.
consumer attitude towards established brand names were Predicting the engagement of advertisements before
measured via electroencephalography. Subjects were broadcasting them on air, ensures higher rate of success-
shown 120 brand names in capital white letter in Tahoma ful promotions.
font on black background and without any logo while In 2015, Yang et al. used six smartphone commercials
their brain responses were recorded. On the other hand, of different brands to compare among them in terms
Fehse et al. compared the brain response of test subjects of extract cognitive neurophysiological indices such as
while they visualized blocks of popular vs. organic food happiness, surprise, and attention as well as behavio-
brand logos. These experiments on brand image may help ral indices (memory rate, preference, etc.) [41]. A com-
marketers to recognize the implicit response of consum- mon experimental design procedure is found among the
ers on different types of branding. promotion-based Neuromarketing experiments, that is
As price is mentioned as an important factor that subjects are first made comfortable in the experimental
determines the user’s interest on purchasing a product, setting, consecutive advertisements were placed at a time
a number of Neuromarketing studies have used price distance no shorter than 10 s and consecutive advertise-
alongside the products. In the aforementioned study ments used neutral stimuli such as white screen, green
by Çakar et al. [34] price was displayed while recording scenario, blank in between them to stabilize the test
brain response during first-time e-commerce user expe- participants.
rience. Marques et al. [22], Çakir et al. [24], Gong et al. The Neuromarketing experiments of Soria Morillo
[35], Pilelienė and Grigaliūnaitė [36], Hsu and Chen [26], et al. [40, 43] tried to find out the electrical activity of
Boccia et al. [37], Venkatraman et al. [38], and Baldo et al. audience brain while viewing advertisement relevant to
[39] have included price as a marketing stimuli with the audiences’ taste. They display used 14 TV commercials
product or promotional. displayed to their 10 test subjects for their experiment
An interesting concept was tried by Boccia et al. to and predicted like or dislike response from audience
recognize the relation between corporate social respon- with the help of advanced algorithms. Cherubino et al.
sibilities and consumer behavior. The author attempted [42] investigated cognitive and emotional changes of
to identify if consumers were willing to pay more for the cerebral activity during the observation of TV commer-
products from socially or environmentally responsible cials among different aged population. Among seven TV
company. Consumers were found to prefer the conven- commercials displayed during the experiment, one com-
tional companies over the socially responsible companies mercial with strong images was analyzed for the adults’
due to lesser price. Marques et al. [22] investigated the and older adults’ reaction. Other than them, Vasiljević
influence of price to compare national brand vs. own- et al. [44] used Nestle advertisement to measure con-
labeled branded products. In the experiment of Çakir sumer attention though pulse analysis; Daugherty et al.
et al, product then product and price were shown to [46] replicated an experiment of Krugman (1971) using
the subjects before decision-making time and the brain both TV advertisements and print media advertise-
responses were recorded through fNIRS [24]. Sometimes ments to recognize how consumers look and think; Royo
price can play a passive role in the form of discounts or et al. [47] focused on consumer response while viewing
gifts in a promotional. Gong et al. innovatively designed advertisements of sustainable product designs. For their
an experiment to compare consumer brain response experiment, an animated commercial was made contain-
associated with promotional using discount (25% off) vs. ing verbal narrative of sustainable product and an exist-
gift-giving (gift value equivalent to the discount) mar- ing commercial was used to convey the visual narrative
keting strategies. Their study found that lower degree of of conventional product. Venkatraman et al. focused
ambiguity (e.g., discounts) better motivates consumer on measuring the success of TV advertisements using

R awnaque et al. Brain Inf. (2020) 7:10 Page 7 of 19
neuroimaging and biometric data [38]. Randolph and vertebrate brain is formed through three phases. First
Pierquet [51] showed super bowl commercials to under- the reptilian complex, which indicates the association
graduate students to compare the class rank of the com- of instincts with the anatomical structure basal gan-
mercials and the neural response from the test subjects. glia. The paleomammalian complex consists of sep-
Nomura and Mitsukura [52] identified emotional states tum, amygdalae, hypothalamus, hippocampal complex,
of audiences while watching favorable vs. unfavorable TV and cingulate cortex as the limbic system. These orga-
commercials. They selected 100 TV commercials among nelles were associated with motivation and emotional
which 50 commercials were award winning which were response of mammalian brain. Finally, neomammalian
labeled as favorable advertisements. Singh et al. [56] used complex consists of cerebral neocortex or the outer
promotion in the form of static vs. video advertisements layer of advanced mammalian brain, which is particu-
to predict the success of omnichannel marketing strate- larly a unique feature of human brain. In the cerebral
gies. Ungureanu et al. [53] measured user attention and neocortex, we find four lobes which control our sen-
arousal by eye tracking while surfing through web page sory, motor, emotional and cognitive processes [76].
containing static advertisements, while Goyal and Singh The triune brain model has been rejected by new neu-
[54] utilized facial biometric sensors to model an auto- roscientists due to the interconnectivity of human brain
mated review systems for video advertisements. Oon structures and their function. However, the anatomical
et al. [55] used merchandise product advertisement clips structure of human brain explained by this theory plays
to recognize user preference. Singh et al. [56] used video a vital role in recognizing cognitive, emotional and
advertisements to measure visual attentions of audiences. behavioral process.
Most of the TVC (television commercials) in these lit- Understanding the anatomy of human brain has
eratures had a standard time of 30 s. In Neuromarketing, showed itself indispensable in Neuromarketing
these TVCs were displayed in between other videos such research, as its functionality is deeply associated with
as documentary film, gaming video, drama, etc., to cap- the interpretation of neural response. The outer layer of
ture the true response of consumers. the human brain is a complex system organized in four
Sometimes Neuromarketing is observed dealing with lobes, namely (frontal, parietal, temporal and occipital
advertisement of different purposes, such as social adver- lobes), each having distinct functionalities for cogni-
tisements or gender-related advertisements. The appli- tive, emotional, and motor responses. The frontal lobe
cation of Neuromarketing in social advertisement is to is the region where most of our thoughts and conscious
predict the success of these ads to reach its messages to decisions are made [77]. Cognitive decision-making
the targeted social groups [45, 49, 69]. Chen et al. [49] mainly takes part in the prefrontal region of this lobe,
experimented on the neural response of adolescent audi- and movement-related decisions are made in the end
ences while they are exposed to e-cigarette commercials. part of frontal lobe. Information about taste, touch and
Another social advertisement stimuli of smoking cessa- movement is processed by the parietal lobe. The occipi-
tion frames was used by Yang [45], to understand what tal lobe is the primary center for visual processing,
types of frames (positive/negative) achieve better atten- and the temporal lobe is responsible for visual memo-
tion from smokers and non-smokers. Gender plays a ries, auditory recognition and integrating new sensory
substantial role in advertisement industry from celebrity information with memories [78]. Besides the primary
endorsement to gender-targeted marketing. Missaglia lobes, cerebral cortex brain anatomy has gyri and sulci
et al. [69] conducted a research on fast marketed con- which create the folded appearance of the brain. The
sumer goods (FMCG) advertisements with celebrity vs. gyri functions on increasing surface area for informa-
non-celebrity female spokesperson. Casado-Aranda et al. tion processing. Alongside the primary lobes, gyri of
[50] worked on gender-targeted advertisements using these lobes can be considered as the region of interest
congruent vs. incongruent product–voice combination. (ROI) in neural imaging techniques [79].
These studies show us the diversity of marketing stimuli Deeper structures of the human brain consist-
for future Neuromarketing applications. ing thalamus, amygdalae, etc., produces sensory and
instinctual responses which are later transported to
3.2 Activation of brain regions due to marketing stimuli the cerebral cortex. Hypothalamus works as the master
control of our autonomic system. Sleep, hunger, thirst,
Human brain is a matter of profound astonishment.
blood pressure, body temperature, sexual arousal are
The anatomical development of our brain resulted in
controlled and regulated by hypothalamus. Thalamus
the complex web of cognitive and emotional process we
on the other hand regulates sensory information, atten-
experience every day. The evolution of vertebrate brain
tion and memory. Amygdalae originate our emotional
was initially proposed by Paul D. MacLean in his Tri-
une Brain model [76]. In his hypothesis, evolution of

Rawnaque et al. Brain Inf. (2020) 7:10 Page 8 of 19
response and hippocampus is the mainframe of our Frontal alpha asymmetry is a key concept of hem-
memory [77]. isphere-based like–dislike classification approach.
Retrieving information from brain requires diverse When the brain is considered as two hemispheres, left
types of methodology. In Neuromarketing experiments, and right frontal cortices show hemispheric asymme-
different parts of brain are selected for retrieving dis- try in their activation during processing positive and
tinct information. An experiment which solely focuses negative emotion. Another term for emotional engage-
on attention might only look at the signals from frontal ment, Approach–Withdrawal Index refers to the emo-
lobe, whereas experiments focusing on buyer’s motiva- tional response from Frontal Alpha Asymmetry theory
tion might want to look at deeper structures [38]. [34]. Frontal Asymmetry Index is a marker of approach
According to Soria Morillo et al., brain signal acquisi- and avoidance. “Emotional Engagement” in Neuromar-
tion may capture neural signals either from cerebral cor- keting is expressed as the power of specific frequency
tex or from the deeper layer of the brain [40, 43]. Their bands from left and right frontal regions. The F3/F4 and
experiment on TV advertisement liking recognition ini- F7/F8 electrodes are the best candidates for these EEG
tially uses information only from prefrontal cortex using power reception as they are positioned at the most sen-
a single electrode EEG device. Their experiment showed, sitive places (International 10–20 System). The alpha
it is possible to classify like/dislike with information col- frequency band (8–12 Hz) is commonly used in the
lected solely from frontal lobe. frontal alpha asymmetry theory. However, as the alpha
Similarly, Cherubino et al. emphasized on the signifi- activity corresponds with relaxation and meditation, it
cance of frontal cortex (FC) and prefrontal cortex (PFC) is negatively correlated with cognitive engagement.
in Neuromarketing studies. PFC processes the conscious Frontal Asymmetry Index is measured from the
and unconscious cognitive and emotional information. equation:
Hence, devices using only a single sensor select PFC as
FrontalAsymmetryIndex
their signal acquisition region [42]. Also, ventromedial
AlphaPowerofRightF4orF8
prefrontal cortex corresponds to motivational behaviors, =ln .
AlphaPowerofLeftF3orF7
imaging of which by fMRI or MEG can reveal purchase
motivations [22].
Higher the Frontal Asymmetry Index value, the more
Neural communication in the brain is conducted
approach response is obtained from the test subjects
through the action potentials, or the firing of neu-
and vice versa. This high or positive asymmetry score
rons [80]. A neuronal signal is the electrochemical
can determine pleasant feeling of a test subject and vice
information that neurons send to each other. These
versa, which was explored in the study conducted by
information are acquired as signals of non-linear pat-
Touchette and Lee [21].
tern called the brainwaves [80]. These brainwaves are
Neuroimaging and neural signal recording devices
further associated with the neural signature of brain
use these locations and brain states to map the mind of
states. The neural signature is divided into frequency
a consumer. A standard 10–20 system has been estab-
bands known as rhythms, such as the delta (0.1–4 Hz),
lished, which is an internationally recognized method
theta (4–8 Hz), alpha (8–12 Hz), beta (12–30 Hz), and
to apply the EEG sensors or electrodes on a human
gamma (30–90 Hz). These frequency bands are related
scalp. EEG electrodes under 10–20 system have let-
to different brain states, regions, functions or patholo-
ters to express their location on skull such as prefron-
gies. Delta (δ) waves are characteristic of deep sleep and
tal (Fp), frontal (F), temporal (T), parietal (P), occipital
have not been explored for BCI applications [81]. Theta
(O), and central (C). Even number of electrodes are
(θ) waves are enhanced during sleep in adults and often
placed on the right side of the head.
related to various brain disorders. During wakefulness
On the other hand, a test subject is placed inside an
under relaxed conditions alpha (α) waves with moder-
fMRI machine where the activities of the cortices can
ate amplitude appear spontaneously. Beta (β) waves have
be recorded from the hemodynamic response or blood
less amplitude and are strongly related to motor control
oxygen level-dependent (BOLD) imaging process.
and engagement or decision-making procedure. Gamma
fMRI can look deeper within the spatial range from
(γ) waves are associated with movement-related activ-
millimeters to centimeters. This enables Neuromar-
ity of the brain and intensely observed in invasive neural
keting researchers using fMRI imaging to examine the
recording [81].
response at putamen, thalamus, amygdalae and even in
In Neuromarketing, beta wave amplitudes are associ-
the hippocampus.
ated with reward processing which can further predict
Functional near-infrared spectroscopy (fNIRS)
success of a product or TVC (Boksem and Smitds) [57].
is another new brain imaging tool which uses the

R awnaque et al. Brain Inf. (2020) 7:10 Page 9 of 19
hemodynamic responses associated with neuronal certain location, making possible to investigate deeper
activities [24, 60]. However, fNIRS has a lower spatial brain structures [57]. The primary disadvantages of
resolution than fMRI and cannot look deeper than 4 cm. this method are that it is very expensive and till now
Alongside brain regions associated with neural has a poor temporal resolution. The computer screen
response, the human has a peripheral system which used in fMRI refreshes the image every 2 to 5 s. This
corresponds to cognitive and emotional processes. Eye low temporal resolution to the order of seconds due to
movement, skin conductance, heart rate, facial expres- the time requirement of the cerebral blood flow’s incre-
sion all are result of neural processes. Eye tracking is ment after being exposed to the stimuli, makes fMRI
primarily considered as the physiological response in unsuitable for tracking brain activities to the order of
consumer neuroscience, however studies have suggested milliseconds, which is required in video advertisement
eye tracking as a result of activation of the visual cortex analysis. Other disadvantage is the head of the subject
or a secondary neural response [34, 36, 38, 53, 70]. must remain static during the whole image recording
Neuromarketing experiments focused on the affect– process [62]. This restriction causes complex preproc-
circumflex coordinate or valance–arousal coordinate use essing and movement-related artifact removal from the
autonomic nervous system (ANS) response from sweat fMRI signals. A number of studies, i.e., Venkatraman
glands of hands or galvanic skin response (GSR), and car- et al. [38], Marques et al. [22], Hubert et al. [25], Hsu
diovascular measure or heart rate (HR). GSR is viewed as and Cheng [26], Chen et al. [49], Casado-Aranda et al.
a sensitive and convenient measure for indexing changes [50], Wang et al. [30], Wolfe et al. [31], Fehse et al. [33],
in sympathetic arousal associated with emotion, cogni- etc., have used fMRI as the neuroimaging technique
tion and attention. On the other hand, HR correlates with in their Neuromarketing studies. fMRI in all studies
the emotional valence of a stimulus, e.g., the positive or required the test subjects to remain static and displayed
negative component of the emotion [34]. the subjects the images and commercials of products
Considering the available regions to capture signals for 3–5 s. Later the subjects had to make purchase deci-
from, it is highly likely that Neuromarketing will expo- sion within 5 s after their exposure to the stimuli [50].
nentially improve its recognition and predictions in user Researchers over the last 5 years are found using 3-T
response and preferences. fMRI scanner 3.0-T Siemens Magnetom Trio system
MRI Scanner equipped with a 32-channel bridge head
3.3 Neural response recording techniques coil (Hubert and Hsu and Cheng) [25, 62] and 3 Tesla
Siemens Verio scanner (Wang et al. [30]). Cost of an
The groundwork in Neuromarketing field is evidently
fMRI machine can be from $500,000 to $3 million vary-
indebted to the advancement of neuroimaging and neu-
ing on its spatiotemporal resolution.
ral recording tools. Neurophysiological tools, such as
Alongside fMRI, electroencephalography (EEG) is
electroencephalography (EEG), functional magnetic
another popular tool used in Neuromarketing research.
resonance imaging (fMRI), eye tracking, skin conduct-
Number of research in Neuromarketing using EEG
ance, heart rate, etc., made it feasible to conduct the aca-
devices is increasing due to EEG’s cost efficiency high
demic and commercial Neuromarketing research. Many
temporal resolution and mobility advantages. The EEG
research-grade neurophysiological and biometric signal
measures electrical activity in the cerebral cortex, the
capturing devices are now available in the market. How-
outer layer of the brain. EEG devices are placed follow-
ever, some devices have cost and mobility advantages
ing the 10–20 system. According to the 10–20 system,
over the others and therefore replacing the expensive and
the 10 and 20 refer to the actual percentage of distances
immobile devices for Neuromarketing purpose.
between adjacent electrodes which are either 10% or 20%
Among all neuroimaging devices, functional mag-
of the total front–back or right–left distance of the skull
netic resonance imaging (fMRI) has been the most
[82]. As EEG is portable and allows capturing signal from
widely used neuroimaging technique in Neuromar-
cerebral cortex with high temporal resolution, it is mainly
keting research during the initial time of consumer
used in TV commercial engagement or success analy-
neuroscience. The reason behind the wide acceptance
sis. EEG signal of interest in Neuromarketing are mainly
of fMRI is that it offers the identification of cerebral
event-related potential (ERP), and late positive potential
regions associated with cognitive and emotional pro-
(LPP). ERP and LPP are used by Pozharliev et al. [20] to
cess. Combining magnetic field and radio waves, fMRI
measure the emotional value of luxury products. Çakar
produces a sequence of images of the cerebral activ-
et al. [34] used ERP to explore the experience of first-time
ity by measuring the blood flow of the cerebral cor-
user of E-commerce product. Pilelienė and Grigaliūnaitė
tex [38]. The signal imaged in fMRI is called BOLD
[36]) used ERP along with eye tracking signal to measure
(blood oxygen level dependent) signal. This technol-
the impact of celebrity spokesman in TVC. Shen et al.
ogy also allows 3D views of the coordinates that denote

Rawnaque et al. Brain Inf. (2020) 7:10 Page 10 of 19
[23] used ERP and LPP to explore the influence of rating electrical field-based EEG, and can indicate the depth of
reviews on online products. the location in the brain with high spatial and temporal
Research-grade EEG devices are vastly used in Neuro- resolution [3]. Similar to MEG, transcranial magnetic
marketing. Emotiv Epoc and Emotive Epoc were found stimulation (TMS) uses varying magnetic field [83] gen-
+
as the mostly commonly used EEG devices in the review. erated by electromagnetic induction using an iron core.
These devices were used in the studies of Yang et al. [45], TMS can stimulate targeted part of the brain, which
Chew et al. [17], Soria Morillo et al. [40], Yadava et al. enables it to conduct social or behavioral experiments.
[18], Royo et al. [47], Jain et al. [63], and Singh et al. [56]. TMS and MEG are also used frequently in Neuromar-
Emotive Epoc is a moveable, cost-effective EEG head- keting experiments. However, the selected databases for
+
set having 14 electrodes those cover the frontal, tempo- this review did not contain any Neuromarketing research
ral, parietal and occipital lobes with channels AF3, F7, articles using these technologies over the last 5 years.
F3, FC5, T7, P7, O1, O2, P8, T8, FC6, F4, F8, AF4. The The electromyography (EMG) measures electrical
acquired brain signals from Emotiv Epoc are highly activity produced by skeletal muscles when the mus-
+
dependable and have already been used in these scientific cles contracts and expands in order to move the body
researches. Another popular EEG device in Neuromar- [70]. Also EMG is generated from the autonomic nerv-
keting, NeuroSky Mindwave, has only one sensor placed ous activity related to emotional or mental activity. In
on the prefrontal cortex of the head or the forehead. Neuromarketing research, facial EMG is the best meas-
Unlike EEG devices with wet electrodes, Neurosky Mind- ure of the valence of the emotional reaction as it records
wave employs a biosensor which does not require any facial muscle movement from two different muscles, i.e.,
conductive medium to be applied on the test subject’s zygomaticus muscle and corrugator muscle. Zygomatic
scalp [40]. With the help of NeroSkyLab, the provided muscle is found to react more while exposed to positive
scientific research tool, data viewing and analysis can be stimuli [70].
conducted easily by non-engineer population. In 2015, Besides these brain signal recordings, eye tracking
Soria Morillo et al. and Ogino and Mitsukura in 2018 is the most popular method for analyzing consumer
conducted Neuromarketing experiment with NeuroSky response. Eye tracking offers to measure visualization
device and with the help of machine learning algorithm, time and gaze path across a screen in Neuromarket-
their choice prediction accuracy was over 70% [40, 68]. A ing experiments. Besides tracking eye movement, pupil
10-channel EEG device BrainAmp, from BrainProducts dilation measurement allows one to associate audi-
GmBh was used in the Neuromarketing experiment con- ence’s focus and arousal to the marketing stimuli. In the
ducted by Cherubino et al. [42]. Another device EEGO reviewed literatures, Tobii Pro X2-30 system from Tobii
Sports from ANT Neuro (32 channels) was used to ana- Technology was found as the most popular eye track-
lyze non-linear features of EEG signals by Oon et al. [55]. ing device. In 2019, Etzold et al. used this eye tracking
B-alert X10 headset from ABM consisting 9 electrode device to explore attention research on online book-
channels is found in use by the experiment of Chew et al. ing [48]. Tobii Pro can also cooperate with fMRI-based
[17]. 8-channel E-Prime from Neuroscan is another EEG Neuromarketing experiment (Venkatraman [38]). Other
device is used in the sales strategy experiment by Gong than Tobii, Eye Tribe is found in use by Çakar et al. [34].
et al. and Touchette et al. conducted their apparel liking Ungureanu et al. used eye tracking to measure the atten-
experiment with NeXus-10 biofeedback system. EEG tion level of consumers while displaying static advertise-
devices have different sampling rates starting from 128 ments of cars and clothing products [53]. Figure 1 depicts
to 512 Hz. This sampling rate determines the highest the most popular methods of neural response recording
frequency recordable by the EEG device. In general EEG i.e. EEG, fMRI and eye tracking used in the Neuromar-
has a lower frequency spectrum, having Gamma band up keting experiments.
to 90 Hz. This gives researchers advantage to choose the Some of the Neuromarketing studies used heart rate, as
right EEG device from numerous manufacturers. Price one of the metrics to measure arousal and focus of the
of EEG devices depends mainly on the number of elec- consumer while they encounter TV commercial stimuli.
trode channels and performance. Cost of EEG device Heart rate is the speed of the heartbeat and it is typically
starts from $99 and can go beyond $25,000, which gives measured by electrocardiogram (EKG). An EKG meas-
researchers buying flexibility. ures the electrical activity of the heart using external skin
Magnetoencephalography (MEG) uses magnetic electrodes. Heart rate is controlled by two antagonistic
potentials to record brain activity at the scalp level, using nervous systems, i.e., the sympathetic nervous system
magnetic field sensitive detectors in the helmet placed (SNS) and the parasympathetic nervous system (PNS).
on the subject’s head. Magnetic field is not influenced Automatic response to external stimuli is determined by
by the type of tissue (blood, brain matter, bones), unlike the sympathetic system of the body. Activation of this

R awnaque et al. Brain Inf. (2020) 7:10 Page 11 of 19
Fig. 1 Neural recording in Neuromarketing experiments: a multichannel EEG [43], b fMRI imaging [50], and c eye tracking for online booking
appointment [48]
system increases heart rate, causing fight or flight mode, amplitude and response latency provide direct measures
which is an independent measure of arousal [38]. In con- of arousal when watching TV commercials, unlike self-
trast, the calm and relaxed state characterized by slower reported measures that are often based on later memory
heart rate is controlled by the parasympathetic system. recall. Although GSR cannot independently relate to
Slower heart rate in response to an advertisement implies emotional valence, some of the Neuromarketing studies,
the increased focus on the ad, hence provides an inde- i.e., Cherubino et al. [42], Çakar et al. [34], Ungureanu
pendent measure of attention [38]. Another physiologi- et al. [53], Magdin et al. [71], Goyal and Singh [54], and
cal parameter, skin conductance (SC), or galvanic skin Singh et al. [56] have used skin conductance along with
response (GSR), develops when the skin acts as an elec- heart rate to measure the consumer attention and focus
trical conductor due to the increased activity of the sweat on the TVC.
glands from exposure to stimulus [38]. Skin conductance

Rawnaque et al. Brain Inf. (2020) 7:10 Page 12 of 19
3.4 Brain signal processing in Neuromarketing Boksem and Smitds[57], Wriessnegger et al. [29], Fan and
Since neural signals and images are highly vulnerable Touyama [66], Pilelienė and Grigaliūnaitė [36] all used
to noise and artifacts, before performing any analysis independent component analysis mostly for eye blink
or interpretation it is imperative to preprocess the neu- and eye movement artifact, and muscular movement
ral signals to increase the signal-to-noise ratio (SNR). noise removal.
Noises that commonly accompany the EEG signals Neuromarketing with fMRI studies have a different
are cardiac signals (ECG), power line interference, eye method for image preprocessing. Since the fMRI provides
movement artifact (EOG) and muscle movement arti- a 3D image of the brain region with time information, it
facts (EMG). Preprocessing in Neuromarketing consists is basically a 4D signal. A 4D dataset is motion corrected
of filtering the signals to the frequency bands of inter- for any head movement, slice time corrected, spatially
est, re-referencing the filtered signal to a common aver- normalized and finally smoothed to recover a denoised
age, detecting and interpolating bad channels, noise fMRI image. Wang et al. [30] used statistical parametric
and artifact removal, and framing or segmentation for mapping (SPM) software to preprocess their fMRI data.
further machine learning process. Their raw fMRI signal was subjected to standard preproc-
EEG signals usually spread across its energy from essing involving correction for head motion, slice timing
0.5 Hz to around 90 Hz. For classification purpose, it correction, temporal and spatial denoising and normali-
is required to have energies only from the relevant fre- zation into standardized Montreal Neurological Institute
quency bands, hence EEG preprocessing commonly (MNI) space. The mean fMRI signal from each region of
uses band pass filtering techniques. Band pass filter interest was extracted from voxels in a sphere of 6-mm
requires two cutoff frequencies, one upper and one radius centered at the activation point in the regional
lower to pass the energy between them and blocks activation map.
energies from all other frequencies. Band pass filter fMRI scan was also used by Hubert et al. [25] in their
used in these Neuromarketing experiments are basi- experiment on hedonic vs. prudent shopper based on
cally the digital version of the filter mostly applied by consumer impulsiveness. Decision-making process with
MATLAB and EEGLAB (a toolbox designated for EEG cognitive deliberation and the consideration of long-
signal processing in MATLAB). Re-referencing to a term consequences are associated with processing in
common average reference is also found common after brain areas such as the ventromedial prefrontal cortex
band pass filtering in the studies of Yang et al. [41], Fan (vmPFC) and the dorsolateral prefrontal cortex (dlPFC).
and Touyama [66] to reduce possible shifts from exter- Hence, these vmPFC and dlPFC were the region of inter-
nal artifacts. Power line interference is usually found ests to capture the BOLD activation imaging [62]. Brain
removed by using a notch filter at 60 Hz or 50 Hz. activation through BOLD signals was used by Hsu and
The reviewed literatures had some common Cheng [26] to investigate negative emotion after prod-
approaches in noise removal techniques. Since the noise uct harm crisis. fMRI region of interest in this study
accompanied with EEG signals are random in nature, included amygdala, left calcarine, striatum, ventral teg-
signal averaging is a common approach to reduce these mental area (VTA) and right insula. The amygdala is
noises. Fan and Touyama [66] averaged the ERP signals associated with memory and subjective evaluation, left
for noise removal. Chew et al. [17] used ABM software calcarine relates to human visual processing, the striatum
development kit (SDK) in MATLAB to remove 5 types is associated with goal-oriented evaluation, and reward
of artifacts, namely EMG, eye blinking artifact, excur- evaluation, VTA relates to decision-making process and
sions, saturations and spike. Excursion, saturation and motive functions, and the insula regions are involved in
spike artifacts in the EEG signals are replaced by zero val- consumer decision-making related to negative reinforce-
ues. Then they applied nearest neighbor interpolation to ment. Acquiring activation within these regions affirms
replace those zero values. Another type of filter Savitzky– the relation between stimuli and cognitive response.
Golay is found in use by Yadava et al. [18] for signal Signal detection and segmentation is the process by
smoothing. For noise and artifact removal, the 4th-order which the signal of interest is detected from the origi-
Butterworth filter was used in the studies of Ogino and nal signal and then separated for further procedures.
Mitsukura [68] and Oon et al. [55]. The energy of the signal may be used as a threshold
Independent component analysis (ICA) is an approach for detection of the signal. Often the Neuromarketing
to separate the statistical subcomponents of EEG sig- experiments contain multiple types of stimuli shown
nals. ICA is found as the most sought after technique to the test subjects. In such cases segmentation sepa-
for removing artifacts and noise from EEG signals in rates the event-based time signals for further pro-
these articles. Studies of Cherubino et al. [42], Bhardwaj cessing, example Bhardwaj et al. [58]. Segmentation
et al. [53], Venkatraman et al. [38], Pozharliev et al. [20], or framing the EEG signals to a shorter time window

R awnaque et al. Brain Inf. (2020) 7:10 Page 13 of 19
is mostly required to process the signal in time–fre- of variance (ANOVA) then cross-validation were also
quency domain [58]. Cherubino et al. [42] segmented found in use to identify the optimal feature set for cog-
their acquired and filtered EEG traces to extract the nitive or affective state classification by Yang et al. [41].
cerebral activity during the exposure to the market-
ing stimuli. Oon et al. [55] used 1-s segmentation time 3.5 Machine learning application in Neuromarketing
to extract non-linear detrended fluctuation analysis Using advanced neural recording method and signal pro-
features. cessing tools, one can analyze EEG signals and interpret
The goal of feature extraction is to find the set of their correspondence with marketing stimuli. Frontal
feature that minimizes intra-class variability and maxi- alpha asymmetry theory helped the researcher classify
mizes inter-class variability. So we need to extract use- emotional approach/withdrawal response of the test sub-
ful information from the preprocessed signal, which jects using sub-band power of left and right hemispheric
can be spatial, spectral or temporal [45]. As the EEG frontal electrode [21]. However, classifying approach/
signal is non-stationary, the feature extraction pro- withdrawal or like/dislike without the FAA is possible,
cedure is quite often complicated. Discrete wavelet even possible from single electrode EEG signals. This
transformation (DWT) is a viable way to extract fea- requires advanced Machine Learning algorithm appli-
tures from EEG signals. cation in Neuromarketing. Both supervised and unsu-
Yadava et al. [18] performed DWT-based four-level pervised learning methods were used in the following
wavelet analysis to extract features from their EEG sig- Neuromarketing experiments. Supervised learning in
nals and decomposed the EEG signal into delta, theta, Neuromarketing uses a priori ground truth, usually the
alpha, beta and gamma frequency bands. Another interviewed response (like/dislike) from the test subjects
feature extraction approach, principal component as the labels. The labels help the classifier know the sig-
analysis (PCA) was used by Venkatraman et al. [38] nal pattern of like and dislike EEGs in the training data-
for extracting fMRI features in their Neuromarketing sets. During the testing phase, like/dislike is predicted
experiment. In 2016, Fan and Touyama applied spatial from a dataset without the labels. Researcher can hide
and temporal principal component analysis (STPCA) the training dataset labels from the classifier, and later
for feature extraction from ERP P300 signal. Rakshit use it for accuracy calculation. On the other hand, unsu-
and Lahiri [67] used a different approach to extract pervised learning approach used in Neuromarketing does
features from EEG signals. They used Welch method not require prior knowledge of the like/dislike labels.
for one-sided power spectral density estimate and then It analyzes the signals with an aim to infer the existing
applied a 256-point DFT algorithm on hamming win- structures for different classes. Supervised learning usu-
dow of length 50 to extract features. Chew et al. [17] ally solves either classification problem or a regression
adopted Hadjidimitriou and Hadjileontiadis methods problem. Support Vector Machines (SVM), Naive Bayes,
in feature extraction where the feature estimation is Artificial Neural Networks (ANN), and Random Forests
based on the event-related synchronization and desyn- (RF) are the most common supervised learning classifi-
chronization theory. ers in Neuromarketing. In parallel, unsupervised learning
Feature selection is also popularly known as dimen- in Neuromarketing has prominently the clustering type
sionality reduction or subset selection. This is a well- classifiers, such as K-NN (k-nearest neighbors), principal
known concept in machine learning which is about component analysis, singular value decomposition, and
selecting an optimal set of features that decreases independent component analysis (ICA).
dimensionality, but has the most contribution to the Neuromarketing researches over the last 5 years mainly
classification accuracy. In the past few years, feature dealt with like/dislike classification problem and pre-
selection has caught the attention of most research- dicting consumer choice problem. Besides the learning
ers because of the nature of high dimensionality of method, both linear and non-linear classifiers have been
bio-signals and the low number of sample data. Selec- used in these Neuromarketing experiments. The most
tion of the optimal feature subset is always relative to used classification algorithms used in Neuromarketing
an evaluation function. In most cases it is the evalua- over the last 5 years are Support Vector Machine (SVM),
tion function that measures the classification accu- Linear Discriminant Analysis (LDA), Artificial Neu-
racy. Feature selection techniques can be divided into ral Network (ANN), Naïve Bayes, k-Nearest Neighbor
three categories, namely: filter, wrapper and embed- (KNN) and Hidden Markov Model (HMM).
ded approach. Wang et al. [30] used Recursive Cluster SVM is a supervised learning method, which requires
Elimination (RCE) algorithm in spatiotemporal fMRI training data for inferring a relation and recognizing pat-
feature selection. Soria Morillo et al. [40] used PCA for terns. SVM works as a discriminative classifier while a
feature reduction from their dataset. One-way analyses hyperplane separates the different classes. Based on the

Rawnaque et al. Brain Inf. (2020) 7:10 Page 14 of 19
training data SVM creates a hyperplane which further the test sample’s category based on to the K training sam-
classifies the new data. The advantage of using SVM in ples which are the nearest neighbors to the test sample.
Neuromarketing is its computational simplicity and In contrast to the hyperplane of SVM, KNN creates a
accuracy level. LDA classifiers are used in several litera- decision boundary among different distinct classes. In
tures in comparison with SVM classifiers. LDA gathers the experiment of Chew et al. [17], SVM and KNN are
data points with similar frequencies as distinct groups used to explore the esthetic preference for 3D shapes.
and 1D Eigen transformation creates the separate classes. The mean accuracy for SVM classifier obtained was 68%,
Bhardwaj et al. [53] extracted energy and power spectral whereas the mean accuracy for KNN classifier was 64%.
density as the feature from the acquired EEG signal and Artificial Neural Network (ANN) is a form of neural
applied SVM and LDA classifiers to classify human emo- network classifiers. ANN is a collection of artificial neu-
tions from EEG signals. Their model achieved 74.13% rons which produces non-linear decision boundaries
average accuracy for SVM-based emotion (happy, sad, among large number of classes. ANN and its different
anger, disgust, neutral, fear and surprised) classification. subtypes are now becoming more common for the Neu-
In contrast, the model achieved 66.50% average accu- romarketing data interpretation. However, ANN requires
racy for LDA-based emotion classification. In the P300 large number of sample data and large number of fea-
signal-based experiment of Fan and Toyuyama, they used tures. Soria Morillo et al. used ANN algorithm in 2015
LD classifier to retrieve emotional faces from different and 2016 in comparison with Random Forest algorithm
subjects. C4.5 and Ameva, respectively. In 2015, their advertise-
In 2016, Ogino and Mitsukura experimented on a ment liking recognition model achieved 80% average
single-channel EEG device for emotion estimation for accuracy with ANN and 69.4% for C4.5 classifier [43]. In
mobile application. Their study used SVM, LR, KNN and 2016, ANN, C4.5 and Ameva achieved average accuracy
SVR together to create a model of valence estimation of 80%, 69%, and 75%, respectively.
from EEG signals. They used two regression methods lin- Oon et al. focused on recognizing preference among
ear regression (LR) and support vector regression (SVR) different categories of products (food, automobile, etc.)
to define valence as sequential value from 1 to 9. SVM using KNN and ANN to analyze non-linear features of
and KNN classified nine emotional classes, and SVR min- the EEG signals [55]. ANN and KNN inputs were used
imized the number of sample errors. Rakshit and Lahiri as the features for Detrended Fluctuation Analysis (DFA)
used SVM and interval-type 2 fuzzy classifiers to classify which achieved the highest classification accuracy 80%
red blue and green colors from EEG signals. Their model for alpha waves, and 76.18% for beta waves. Doborjeh
achieved the classification with 78.81% average accuracy et al. [64] used another type of Neural Network, Spiking
for SVM-based color classification [67]. However, IT2FS Neural Network (SNN) to recognize attention bias pat-
achieved the highest 80.04% mean accuracy compared to tern from spatio-temporal EEG signal. In their study, a
other classifiers in the experiment. brain-like SNN methodology (NeuCube) was used to cre-
The hidden Markov model (HMM) is non-linear clas- ate models from EEG signals to evaluate how attention
sifier under another supervised learning method. It is bias can affect the consumer preferences. Their SNN-
derived from statistical modeling and is widely used based classification model achieved 89.95% average accu-
in temporal and biomedical signals. In Neuromarket- racy, while traditional machine learning SVM classifier
ing experiments, HMM is used to classify multiclass achieved 48.5% accuracy.
sequential data where transition from one mental state to
4 Result synthesis
another mental state can occur. Researchers can find pos-
sible observation of the states using the state transition This section synthesizes the results from already dis-
probabilities. Yadava et al. proposed an HMM-based con- cussed research articles and book chapters with empiri-
sumer choice prediction (like/dislike) model using EEG cal findings on Neuromarketing, published from 2015 to
signals from frontal, parietal, temporal and occipital lobe. 2019. To ensure the reliability of the experimental find-
They compared their classification model with standard ings, the reviewed literatures had largely set their statisti-
classifiers such as SVM, RF and ANN. Their HMM-based cal significance at p < 0.05 [20, 38, 42, 43, 46, 59, 60, 70].
model achieved classification accuracy of 70.33% for male With the advancements in technologies, marketing
test subjects and 63.56% for female test subjects [18]. In stimuli have become more TV commercial or image
comparison, accuracy of 62.85% was achieved with SVM of the product oriented rather than the original prod-
classifier with C 6, whereas ANN with two hidden lay- uct [18–26, 34–43]. 3D image of the products have also
=
ers achieved 60% average accuracy. added to these virtual product purchase decision-making
K-Nearest Neighbor algorithm serves both as a classifi- [17]. E-commerce products have gained interest among
cation and regression algorithm. KNN algorithm predicts the Neuromarketing researchers, since these products

R awnaque et al. Brain Inf. (2020) 7:10 Page 15 of 19
are now more available to the consumers through online respectively [24, 60]. This shows fNIRS can be a promis-
shopping [34]. First-time user experience in online shop- ing mean of neural recording for future Neuromarketing
ping and user experience in online appointment have experiments.
also diversified the stimuli group of Neuromarketing While comparing the EEG devices, Emotiv Epoc
research. Other than these marketing focused stimuli, and Emotive Epoc had the largest number of aca-
+
some of the Neuromarketing studies focused on social demic research conducted through them. Other than
advertisements, particularly the campaign against smok- the 14-channel device, BrainAmp is a 10-channel EEG
ing and alcohol consumption among young adults. These device and eego Sports is a 32-channel device used by
social advertisements used neuroimaging and neural sig- Neuromarketing researchers. NeuroSky MindWave
nal decoding techniques to assess and predict the success despite having only one sensor, provided denoised EEG
of their message reaching the targeted social groups. data and performed well with accuracy over 70%.
Analyzing consumer’s emotional response is found All of the fMRI-based Neuromarketing studies over
as a focus of current Neuromarketing research articles. the last 5 years have used 3-Tesla fMRI scanner Mag-
These experiments widely used Frontal Alpha Asymme- netom Trio, SIEMENS, and Siemens Verio scanner for
try theory for left and right frontal channel. Besides the their experiments [25, 30, 62]. The advantage of 3.0-T
alpha band, beta and theta bands are also found in use functional MRI is the high spatial resolution. However,
in these literatures to recognize cognitive and emotional BOLD signal-based fMRI has the possible confusion
response of the consumers. Table 3 summarizes the find- with blood flow due to head or muscle movement.
ings related to brainwaves and their functionalities in the Signal preprocessing in the selected articles was
reviewed Neuromarketing literatures. mainly performed by using MATLAB and EEGLAB.
Over the last 5 years in consumer neuroscience Besides band pass filtering, increased used of inde-
research, the use of research-grade commercially avail- pendent component analysis (ICA) in spatiotemporal
able EEG devices has become more popular than fMRI domain is also observed over the course of last 5 years
scanners. EEG has been particularly used in TV adver- [20, 36, 38, 42, 53]. Other than noise and artifact
tisement evaluation, where a high temporal resolution is removal, preprocessing dealt with framing or segmen-
required to explore the dynamic effects of TV commer- tation of the temporal EEG signal. The fMRI data were
cials. Even though fMRI has been used less in the Neu- preprocessed using the statistical parametric mapping
romarketing experiments, the use of fMRI is particularly (SPM) software.
found when a consumer is displayed product images and In this systematic review, a number of Neuromar-
asked to make purchase decision [30]. The reason behind keting research experiments used artificial intelligent
using product images as marketing stimuli in fMRI-based algorithms for prediction and classification purposes.
Neuromarketing research is that, fMRI can point out the Table 4 compares the average classification accuracy
activated brain region when a subject encounters a mar- achieved by these algorithms in the selected Neuromar-
keting stimuli. The activated brain region can estimate keting studies.
the positive or negative experience of the consumer in While comparing the classification performance
their brain. However, TVC changes stimuli in millisecond of machine learning algorithms in Neuromarketing
time frame, response of which cannot be obtained by an research, we found the Artificial Neural Network had
fMRI scanner with 2–5 s image refresh rate. Other than the highest classification accuracy around 80% among
EEG and fMRI, fNIRS has started to enter the Neuromar- all other algorithms [40, 43]. However, ANN requires
keting research field. Having the advantage of mobility, more training data than other classifiers such as 70%
fNIRS has been used in purchase behavior correlation data in training and 30% in testing, which calls into
and consumer reaction examination by Çakir et al. and question its viability in Neuromarketing. After ANN,
Krampe et al. In these cases, fNIRS has shown accu- SVM was the algorithm most widely used in Neuromar-
racy over 70% and scored in reliability scale 0.7 out of 1, keting with the second highest classification accuracy
Table 3 Functionalities of brain states used in Neuromarketing research
Brain states Functionalities in Neuromarketing
Theta (4–8 Hz) Frontal theta associated with cognitive process [59]. Theta amplitude increase for preferred color [18].
Alpha (8–12 Hz) Frontal alpha associated with cognitive process [59]. Alpha amplitude is inversely correlated with neural activity used in frontal
asymmetry score [21]. Emotional valance corresponds alpha asymmetry, high alpha activity in central–parietal–occipital lobe
vigilance [27].
Beta (12–30 Hz) Medial–frontal beta band activity is associated with reward processing [57]. Right parietal beta corresponds to imagination [59].

Rawnaque et al. Brain Inf. (2020) 7:10 Page 16 of 19
Table 4 Comparative accuracy analysis for machine learning classifiers in Neuromarketing
Classifiers Neuromarketing studies Average accuracy
Support Vector Machine (SVM) Like/dislike classification for esthetic preference recognition among 3D objects (Chew et al.) 68%
[17]
Attention bias identification between targeted and non-targeted stimuli using NeoCube- 48.5%
based SNN architecture (Doborjeh et al.) [64]
Like/dislike classification among e-commerce product (Yadava et al.) [18] 62.85%
Emotional valence recognition between excitement and boredom using EEG device and 72.4%
combining SVM, KNN, SVR, LR (Ogino and Mitsukura) [68]
Purchase decision prediction from fMRI data using recursive cluster elimination-based support 55.70%
vector machine (RCE-SVM) (Wang et al.) [30]
Facial emotion recognition using GSR sensor biometric data (Goyal and Singh) [54] 81.65%
Seven-emotion recognition using EEG signal (Bhardwaj et al.). Happiness and sadness clas- 87.5%, 92.5%
sification accuracy reported here, respectively
Color classification using EEG signal (Rakshit et al.) 78.81%
K-Nearest Neighbor (KNN) Like/dislike classification for esthetic preference recognition among 3D objects (Chew et al.) 64%
[17]
Hidden Markov model (HMM) Like/dislike classification among e-commerce product (Yadava et al.) [18]. Classification accu- 70.33%, 63.56%
racy reported for male and female subject, respectively
Linear discriminant analysis (LDA) Seven-emotion recognition using EEG signal (Bhardwaj et al.) [58]. Happiness and sadness clas- 82.5, 87.5%
sification accuracy reported here, respectively
Like-/dislike classification using car stimuli and ERP signal (Wreissenger et al.) 61%
Naïve Bayes Purchase decision prediction using Neural Impulse Actuator (NIA) device (Taqwa et al.) [73] 48.5%
Artificial Neural Network Consumer gender prediction using facial action coding (Gurbuj and Toga) [28] 83.8%
TV advertisement liking recognition using EEG signal (Soria Morillo et al.) [43] 80%
TV advertisement liking recognition using EEG (Soria Morillo et al.) [40] 80%
Like/dislike classification among e-commerce products (Yadava et al.) [18] 60%
above 70%. HMM performed better than KNN in cross-validate the experimental findings. While choosing
overall application of machine learning algorithms in among classifiers, although ANN has shown better per-
Neuromarketing. formance consistently. However, authors would recom-
mend preferring linear classifier over neural networks, as
5 Recommendation
most of the Neuromarketing sampling EEG dataset does
From this systematic review, authors would like to sug- not contain plethora of samples to train a complex classi-
gest future Neuromarketing researchers to first define fier as ANN.
the scope of their inquisition, which defines the rest
of the process. Neuromarketing on product purchase 6 Conclusion
assessment and purchase decision-making have been
Neuromarketing is an emerging field with opportuni-
using functional MRI to locate the activated region in
ties in commercial, social and political advertisement
consumer brain to predict the success or failure of the
domain. The advancements of this field hence requires
product. However, to recognize consumer engagement
proper documentation to capture its state-of-art. This
with product commercial, it is worthwhile to use EEG
study was conducted with a focus to shed light on the
devices with high temporal resolution. Neuromarket-
technological scope and possible opportunities in this
ing experiments with EEG devices of 14 channels and 32
field. Authors found over the course of last 5 years, Neu-
channels have established their research-grade perfor-
romarketing experiments have been conducted mainly
mance. However, the raw data availability should be kept
with the stimuli of consumer goods, in both product
in mind by the researchers while selecting an EEG device.
and promotion forms. However, Neuromarketing is
Also, researcher should consider availability of bilateral
showing its possibilities in the domain of social adver-
EEG electrodes if they would like to utilize frontal alpha
tisement. Neuromarketing researchers tend to focus on
asymmetry theory. Accompanying EEG, eye tracking has
the frontal and prefrontal cortex of consumer brain for
also shown high performance in attention and arousal
cognitive and emotional inquiries. Among all brain sig-
locating. Eye tracker, heart rate monitor, galvanic skin
nal recording devices, we found EEG is becoming more
response device can be used alongside brain signal to
popular in Neuromarketing experiments, especially with

R awnaque et al. Brain Inf. (2020) 7:10 Page 17 of 19
TVC analysis due to its high temporal resolution and 3. Vecchiato G, Astolfi L, Fallani FV (2011), On the Use of EEG or MEG brain
imaging tools in neuromarketing research, computational intelligence
cost effectiveness. However, EEG devices have different
and neuroscience 2011, Article ID 643489
sampling rates causing a limitation for highest analyz- 4. Izhikevich EM (2003) Simple model of spiking neurons. IEEE Transac
able frequency, which should be under the scrutiny of Neural Netw. 14(6):1569–1572
5. Custdio PF (2010) Use of EEG as a neuroscientific approach to advertising
the researchers. Signal processing in these studies largely
research, Master thesis, Instituto Superior Tcnico, Universidade Tecnica De
adopted ICA for noise and artifact removal. Finally, the Lisboa
highest number of studies have used SVM for classifica- 6. Dimpfel W (2015) Neuromarketing: neurocode-tracking in combina-
tion with eye-tracking for quantitative objective assessment of TV
tion purpose among all other algorithms, perhaps due
commercials. J Behav Brain Sci. 05:137–147. https ://doi.org/10.4236/
to its simplicity. We hope, our findings will guide future jbbs.2015.54014
researchers to explore the opportunities in this field in a 7. Kroupi E, Hanhart P, Lee JS, Rerabek M, Ebrahimi T (2014) Predicting
subjective sensation of reality during multimedia consumption based on
more efficient manner.
EEG and peripheral physiological signals. In: International conference on
multimedia and expo, pp 1–6
8. Rami NK, Chelsea W, Sarath K, Jordan L, Barbara EK (2013) Consumer
Abbreviations neuroscience: assessing the brain response to marketing stimuli
ANN: Artificial Neural Network; DWT: Discrete wavelet transformation; DFA: using electroencephalogram (EEG) and eye tracking. Expert Syst Appl
Detrended fluctuation analysis; EEG: Electroencephalography; fMRI: Functional 40:3803–3812
magnetic resonance imaging; fNIRS: Functional near infra-red spectroscopy; 9. Ariely D, Berns GS (2010) Neuromarketing: the hope and hype of neuro-
GSR: Galvanic skin response; HMM: Hidden Markov model; HR: Heart rate; imaging in business. Nat Rev Neurosci 11:284–292
ICA: Independent component analysis; KNN: K-Nearest Neighbor; LDA: Linear 10. Sing D, Sharma JK (2010), Neuromarketing: a peep into customer S minds
discriminant analysis; MEG: Magneto encephalography; PCA: Principal com- 11. Neuromarketing Science and Business Association (NMSBA), The Global
ponent analysis; PFC: Prefrontal cortex; SVM: Support Vector Machine; TVC: TV Neuromarketing Network, https ://www.nmsba .com/. Accessed 28 July
commercial. 2019
12. Neuromarketing World Forum, http://neuro marke tingw orldf orum.com/.
Acknowledgements Accessed 19 Oct 2019
Not applicable. 13. Cruz ML, Marcon A, Medeiros JF (2016) Neuromarketing and the
advances in the consumer behaviour studies: a systematic review of the
Authors’ contributions literature. Int J Bus Glob 17(3):330–351
FSR prepared the manuscript and conveyed systematic literature review. KAM 14. Hsu M (2017) Neuromarketing: inside the mind of the consumer. Calif
designed and developed the research framework and co-conducted the Manag Rev 59(4):5–22
systematic literature review. Other authors: KMR, SFA, RV, TC and FS provided 15. Shaw SD, Bagozzi RP (2018) The neuropsychology of consumer behavior
the conceptual guidelines, reviewed and sorted the selected literatures and and marketing. Consum Psychol Rev. 1:22–40. https ://doi.org/10.1002/
contributed in the preparation of the final reviews and draft. All authors read arcp.1006
and approved the final manuscript. 16. Khan KS, Kunz R, Kleijnen J, Antes G (2003) Five steps to conduct-
ing a systematic review. J R Soc Med 96(3):118–121. https ://doi.
Funding org/10.1177/01410 76803 09600 304
This review was conducted under the research grant from Institute of 17. Chew LH, Teo J, Mountstephens J (2015) Aesthetic preference recogni-
Advanced Research, United International University, Project Code No. tion of 3D shapes using EEG. Cognit Neurodynamics. 10(2):165–173
IAR/01/19/SE/10. Grant Recipient: Prof. Khondaker Abdullah Al Mamun. 18. Yadava M, Kumar P, Saini R, Roy PP, Dogra DP (2017) Analysis of EEG
signals and its application to neuromarketing. Multimedia Tools Appl.
Availability of data and materials 76(18):19087–19111. https ://doi.org/10.1007/s1104 2-017-4580-6
This review used available literature relevant to the problem statement from 19. Rojas JC, Contero M, Bartomeu N, Guixeres J (2015) Using combined
valid databases across the internet. Databases are: Science Direct, Emerald bipolar semantic scales and eye-tracking metrics to compare consumer
Insight, Sage, IEEE Xplore, Wiley Online Library, and Taylor Francis Online. perception of real and virtual bottles. Packag Technol Sci. 28:1047–1056.
https ://doi.org/10.1002/pts.2178
Competing interests 20. Pozharliev R, Verbeke WJMI, Van Strien JW, Bagozzi RP (2015) Merely
The authors declare that they have no competing interests. being with you increases my attention to luxury products: using EEG
to understand consumers’ emotional experience with luxury branded
Author details products. J Mark Res 52(4):546–558. https ://doi.org/10.1509/jmr.13.0560
1 Advanced Intelligent Multidisciplinary Systems Lab, Institute of Advanced 21. Touchette B, Lee SE (2016) Measuring neural responses to apparel prod-
Research, United International University, Dhaka, Bangladesh. 2 School of Busi- uct attractiveness: an application of frontal asymmetry theory. Cloth Text
ness and Economics, United International University, Dhaka, Bangladesh. Res J 35(1):3–15
3 Institute of Business Administration, University of Dhaka, Dhaka, Bangla- 22. Marques JP, Martins M, Ferreira HA, Ramalh J, Seixas D (2016), Neural
desh. 4 Department of Mechanical Engineering, Imperial College London, imprints of national brands versus own-label brands, J Prod Brand Man-
London, United Kingdom. 5 Institute of Biomaterials & Biomedical Engineering, age, 25(2)
University of Toronto, Toronto, Canada. 6 Department of Computer Science 23. Shen Y, Shan W, Luan J (2018) Influence of aggregated ratings on pur-
and Engineering, University of Liberal Arts Bangladesh, Dhaka, Bangladesh. chase decisions: an event-related potential study. Eur J Mark. https ://doi.
7 Department of Computer Science and Engineering, United International org/10.1108/EJM-12-2016-0871
University, Dhaka, Bangladesh. 24. Çakir MP, Çakar T, Girisken Y, Yurdakul D (2018) An investigation of
the neural correlates of purchase behavior through fNIRS. Eur J Mark
Received: 31 December 2019 Accepted: 14 August 2020 52(1/2):224–243. https ://doi.org/10.1108/EJM-12-2016-0864
25. Hubert M, Linzmajer M, Riedl R, Kenning P (2018) Trust me if you can—
neurophysiological insights on the influence of consumer impulsiveness
on trustworthiness evaluations in online settings. Eur J Mark. https ://doi.
org/10.1108/EJM-12-2016-0870
References 26. Hsu L, Chen Y (2019) Music and wine tasting: an experimental neuromar-
1. Assael H (1981) Consumer behavior and marketing action keting study. Br Food J. https ://doi.org/10.1108/BFJ-06-2019-0434
2. Malhotra NK (1993) Marketing research: an applied orientation

Rawnaque et al. Brain Inf. (2020) 7:10 Page 18 of 19
27. Hoefer D, Handel M, Mueller K, Hammer TR (2016) Electroencepha- advertising: revisiting Krugman. Eur J Mark 52(1/2):182–198. https ://doi.
lographic study showing that tactile stimulation by fabrics of differ- org/10.1108/EJM-10-2017-0657
ent qualities elicit graded event-related potentials. Skin Res Technol 47. Royo M, Chulvi V, Mulet E, Galán J (2018) Users’ reactions captured by
22(4):470–478 means of an EEG headset on viewing the presentation of sustainable
28. Gurbuz F and Toğa G, Usage Of The Facial Action Coding System To Pre- designs using verbal narrative. Eur J Mark. https ://doi.org/10.1108/
dict Customer Gender Profile: A Neuro Marketing Application In TURKEY. EJM-12-2016-0837
2018 2nd International Symposium on Multidisciplinary Studies and 48. Etzold VM, Braun A, Wanner T (2019) Eye tracking as a method of neuro-
Innovative Technologies (ISMSIT) (2018): 1–4 marketing for attention research—an empirical analysis using the online
29. Wriessnegger S.C., Hackhofer D., Müller-Putz G.R. (2015), Classifica- appointment booking platform from Mercedes-Benz
tion of unconscious like/dislike decisions: First results towards a novel 49. Chen Y, Fowler CH, Papa VB, Lepping RJ, Brucks MG, Fox AT, Martin LE
application for BCI technology Conference Proc IEEE Eng Med Biol Soc. (2018) Adolescents’ behavioral and neural responses to e-cigarette adver-
2015;2015:2331–4. doi: 10.1109/EMBC.2015.7318860. tising. Addict Biol 23(2):761–771
30. Wang Y, Chattaraman V, Kim H, Deshpande G (2015) Predicting purchase 50. Casado-Aranda L, Laan LN, Sánchez-Fernández J (2018) Neural correlates
decisions based on spatiotemporal functional MRI features using of gender congruence in audiovisual commercials for gender-targeted
machine learning. IEEE Trans Auton Ment Dev. https ://doi.org/10.1109/ products: an fMRI study. Hum Brain Mapp 39(11):4360–4372
TAMD.2015.24347 33 51. Randolph, A.B., & Pierquet, S. (2015). Bringing advertising closer to mind:
31. Wolfe K, Jo W, Olds D, Asperin A, DeSanto J, Liu WC (2016) An fMRI study using neurophysiological tools to understand student responses to super
of the effects of food familiarity and labeling on brain activation. J Culi Sci bowl commercials. 2015 48th Hawaii International Conference on System
Technol 14(4):332–346. https ://doi.org/10.1080/15428 052.2016.11389 17 Sciences, 517–522
32. Bosshard SS, Bourke JD, Kunaharan S, Koller M, Walla P (2016) Established 52. Nomura T and Mitsukura Y (2015), Extraction of unconscious emotions
liked versus disliked brands: brain activity, implicit associations and while watching TV commercials IECON 2015—41st Annual Conference of
explicit responses. Cogent Psychol 3(1):1176691 the IEEE Industrial Electronics Society, art. no. 7392127, pp. 368–373
33. Fehse K, Simmank F, Gutyrchik E, Sztrókay-Gaul A (2017) Organic or 53. Ungureanu F, Lupu RG, Cadar A, Prodan A (2017) Neuromarketing and
popular brands—food perception engages distinct functional pathways. visual attention study using eye tracking techniques, 21st International
An fMRI study. Cogent Psychol 4:1. https ://doi.org/10.1080/23311 Conference on System Theory, Control and Computing (ICSTCC)
908.2017.12843 92 54. Goyal G and Singh J (2018), Minimum Annotation identification of facial
34. Çakar T, Rızvanoğlu K, Öztürk O, Çelik DZ, and Gürvardar I (2017) The use affects for Video Advertisement, International Conference on Intelligent
of neurometric and biometric research methods in understanding the Circuits and Systems
user experience during product search of first-time buyers in e-com- 55. Oon HN, Saidatul A, Ibrahim Z. et al. (2018), Analysis on Non-linear fea-
merce, international conference of design, user experience, and usability tures of electroencephalogram (EEG) signal for neuromarketing applica-
35. Gong Y, Hou Z, Zhang Q, Tian S (2018) Discounts or gifts? Not just to tion, 2015 48th Hawaii International Conference on System Sciences
save money: a study on neural mechanism from the perspective of 56. Singh J, Goyal G, Gill R (2019) Use of neurometrics to choose optimal
fuzzy decision. J Contemp Market Sci. https ://doi.org/10.1108/JCMAR advertisement method for omnichannel business. Enterprise Inform Syst.
S-08-2018-0009 https ://doi.org/10.1080/17517 575.2019.16403 92
36. Pilelienė L and Grigaliūnaitė V, (2017), The effect of female celebrity 57. Boksem M, Smitds A (2015) Brain responses to movie trailers predict
spokesperson in FMCG advertising: neuromarketing approach, J Consum individual preferences for movies and their population-wide commercial
Market, 34(3) success. J Market Res 52(4):482–492. https ://doi.org/10.1509/jmr.13.0572
37. Boccia F, Malgeri Manzo R, Covino D (2019) Consumer behavior and cor- 58. Bhardwaj A, Gupta A, Jain P, Rani A, Yadav J (2015). Classification of
porate social responsibility: an evaluation by a choice experiment. Corp human emotions from EEG signals using SVM and LDA Classifiers. 2015
Soc Resp Env Ma. 26:97–105. https ://doi.org/10.1002/csr.1661 2nd International Conference on Signal Processing and Integrated Net-
38. Venkatraman V, Dimoka A, Pavlou PA, Vo K, Hampton W, Bollinger B, works (SPIN), 180–185
Hershfield HE, Ishihara M, Winer RS (2015) Predicting advertising success 59. Gordon R, Ciorciari J, Laer TV (2018) Using EEG to examine the role of
beyond traditional measures: new insights from neurophysiological attention, working memory, emotion, and imagination in narrative
methods and market response modeling. J Market Res 52(4):436–452. transportation. Eur J Mark 52(1/2):92–117. https ://doi.org/10.1108/
https ://doi.org/10.1509/jmr.13.0593 EJM-12-2016-0881
39. Baldo D, Parikh H, Piu Y, Müller KM (2015) Brain waves predict success of 60. Krampe C, Strelow E, Haas A, Kenning P (2018) The application of mobile
new fashion products: a practical application for the footwear retailing fNIRS to shopper neuroscience–first insights from a merchandising com-
industry. J Creat Val 1(1):61–71 munication study. Eur J Mark. https ://doi.org/10.1108/EJM-12-2016-0727
40. Soria Morillo LM, Álvarez-García JA, Gonzalez-Abril L, Ramirez JA (2015) 61. Holst EMZ, Henseler J (2017) Thinking outside the box: a neuroscientific
Advertising liking recognition technique applied to neuromarketing by perspective on trust in B2B relationships. IMP J 12(1):75–110. https ://doi.
using low-cost EEG Headset. IWBBIO org/10.1108/imp-03-2017-0011
41. Yang T, Lee DY, Kwak Y, Choi J, Kim C, Kim SP (2015) Evaluation of TV com- 62. Hsu YT, Cheng MS (2018) fMRI neuromarketing and consumer learning
mercials using neurophysiological responses. J Physiol Anthropol. https :// theory: word-of-mouth effectiveness after product harm crisis. Eur J Mark
doi.org/10.1186/s4010 1-015-0056-4 52(1/2):199–223. https ://doi.org/10.1108/EJM-12-2016-0866
42. Cherubino P, Trettel A, Cartocci G, Rossi D, Modica E, Maglione AG, Man- 63. Anysha Jain, Tanupriya Choudhury, Ruby Singh, Praveen Kumar, (2018),
cini M, Flumeri GD, Babiloni F (2016) Neuroelectrical indexes for the study Signal classification for real-time neuro marketing applications, Inter-
of the efficacy of TV advertising stimuli national Conference on advances in computing and communication
43. Soria Morillo LM, Álvarez-García JA, Gonzalez-Abril L (2016) Ramirez JA engineering (ICACCE-2018)
(2016) Discrete classification technique applied to TV advertisements 64. Gholami Doborjeh Z, Doborjeh MG, Kasabov N (2018) Attentional bias
liking recognition system based on low-cost EEG headsets. Biomed Eng pattern recognition in spiking neural networks from spatio-temporal EEG.
Online. 15:75 Cogn Comput 10:35. https ://doi.org/10.1007/s1255 9-017-9517-x(2017)
44. Vasiljević T, Bogdanović Z, Rodić B, Naumović T, Labus A (2019) Designing 65. Kaur B., Singh D., Roy P.P. (2018) Eyes Open and Eyes Close Activity Rec-
IoT infrastructure for neuromarketing research. In: Rocha Á, Adeli H, Reis L, ognition Using EEG Signals. In: Nagabhushan T., Aradhya V., Jagadeesh P.,
Costanzo S (eds) New knowledge in information systems and technolo- Shukla S., M.L. C. (eds) Cognitive Computing and Information Processing.
gies. WorldCIST’19 2019. Advances in Intelligent Systems and Computing. CCIP 2017. Communications in Computer and Information Science, vol
Springer, Cham, p 930 801. Springer, Singapore
45. Yang D (2018) Exploratory neural reactions to framed advertisement 66. Fan J and Touyama H (2016), Emotional Face Retrieval with P300 signals
messages of smoking cessation. Soc Market Quart 24(3):216–232 of multiple subjects, joint 8th International Conference on Soft Comput-
46. Daugherty T, Hoffman E, Kennedy K, Nolan M (2018) Measuring ing and Intelligent Systems and 17th International Symposium. on
consumer neural activation to differentiate cognitive processing of Advanced Intelligent Systems

R awnaque et al. Brain Inf. (2020) 7:10 Page 19 of 19
67. Rakshit A and Lahiri R(2016), Discriminating different color from EEG 77. Nolte J, and Sundsten J (2009) The Human Brain: an Introduction to Its
signals using interval-type 2 fuzzy space classifier (a neuro-marketing Functional Anatomy. Mosby/Elsevier
study on the effect of color to Cognitive State), 1st IEEE International 78. Frackowiak S, Richard J (2007) Human brain function. Elsevier, Acad, press,
Conference on Power Electronics; Intelligent Control and Energy Systems Amsterdam
(ICPEICES-2016) 79. Beeson P, Rapcsak S, Plante E, Chargualaf J, Chung A, Johnson S,
68. Ogino M, Mitsukura Y (2018), A mobile application for estimating emo- Trouard T (2003) The neural substrates of writing: a functional magnetic
tional valence using a single-channel EEG device resonance imaging study. Aphasiology 17(6–7):647–665. https ://doi.
69. Missaglia A, Oppo A, Mauri M, Ghiringhelli B, Ciceri A, Russo V (2017). The org/10.1080/02687 03034 40000 67
impact of emotions on recall: An empirical study on social ads 80. Vecchiato G, Toppi J, Astolfi L, Fallani FDV (2011), Spectral EEG frontal
70. Ceravolo MG, Farina V, Fattobene L, Leonelli L, Raggetti GM (2019) Pres- asymmetries correlate with the experienced pleasantness of TV com-
entational format and financial consumers’ behaviour: an eye-tracking mercial advertisements, Medical & Biological Engineering & Comput-
study. Int J Bank Market. https ://doi.org/10.1108/IJBM-02-2018-0041 ing > Issue 5
71. Magdin M, Kohutek M, Koprda S, Balogh Z, (2019), EmoSens–the proposal 81. Abdullah-Al-Mamun, Khondaker (2013) Pattern identification of move-
of system for recognition of emotion with SDK affectiva and various sen- ment related states in biosignals. University of Southampton, Faculty of
sors, in: intelligent computing theories and application Engineering and the Environment, Doctoral Thesis, 225 pp
72. Clerico A, Gupta R and Falk TH (2015), Mutual Information Between 82. Klem GH, Lüders H, Jasper HH, Elger C (1958) The ten-twenty electrode
Inter-Hemispheric EEG Spectro-Temporal Patterns: A New Feature for system of the International Federation. The International Federation of
Automated Affect Recognition, 7th Annual International IEEE EMBS Clinical Neurophysiology. Electroencephalogr Clin Neurophysiol Suppl
Conference on Neural Engineering 52:3–6
73. Taqwa T, Suhendra A, Hermita M, and Darmayantie A (2015), Implemen- 83. Jolij J, Lamme VAF (2005) Repression of unconscious information by con-
tation of Naïve Bayes method for product purchasing decision using scious processing: evidence from affective blindsight induced by tran-
neural impulse actuator in neuromarketing, International Conference on scranial magnetic stimulation. Proc Natl Acad Sci 102(30):10747–10751.
Information & Communication Technology and Systems (ICTS) https ://doi.org/10.1073/pnas.05008 34102
74. Nemorin S (2016) Neuromarketing and the “poor in world” consumer:
how the animalization of thinking underpins contemporary market
Publisher’s Note
research discourses. Consum Market Cult. https ://doi.org/10.1080/10253
866.2016.11608 97 Springer Nature remains neutral with regard to jurisdictional claims in pub-
75. Grönroos C (1990), “Marketing Redefined”, Management Decision, 28(8). lished maps and institutional affiliations.
https ://doi.org/10.1108/00251 74901 01391 16
76. MacLean PD (1988) Triune Brain. In: Comparative Neuroscience and
Neurobiology. 126–128