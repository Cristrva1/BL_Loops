ORIGINALRESEARCH
published:26May2022
doi:10.3389/fnhum.2022.861270
BCI-Based Consumers’ Choice
Prediction From EEG Signals: An
Intelligent Neuromarketing
Framework
FazlaRabbiMashrur1,KhandokerMahmudurRahman2,MohammadTohidulIslamMiya2,
RaviVaidyanathan3,SyedFerhatAnwar4,FarhanaSarker5andKhondakerA.Mamun1,6*
1AdvancedIntelligentMultidisciplinarySystems(AIMS)Lab,InstituteforAdvancedResearch(IAR),UnitedInternational
University,Dhaka,Bangladesh,2SchoolofBusinessandEconomics,UnitedInternationalUniversity,Dhaka,Bangladesh,
3DepartmentofMechanicalEngineeringandUKDementiaResearchInstituteCare,ResearchandTechnologyCentre
(DRI-CR&T),ImperialCollegeLondon,London,UnitedKingdom,4InstituteofBusinessAdministration,UniversityofDhaka,
Dhaka,Bangladesh,5DepartmentofComputerScienceandEngineering,UniversityofLiberalArtsBangladesh,Dhaka,
Bangladesh,6DepartmentofComputerScience&Engineering,UnitedInternationalUniversity,Dhaka,Bangladesh
Neuromarketing relies on Brain Computer Interface (BCI) technology to gain insight
Editedby:
FaresAl-Shargie, into how customers react to marketing stimuli. Marketers spend about $750 billion
AmericanUniversityofSharjah, annually on traditional marketing camping. They use traditional marketing research
UnitedArabEmirates
procedures such as Personal Depth Interviews, Surveys, Focused Group Discussions,
Reviewedby:
andsoon,whicharefrequentlycriticizedforfailingtoextracttrueconsumerpreferences.
AydinAkan,
ÏzmirUniversityofEconomics,Turkey On the other hand, Neuromarketing promises to overcome such constraints. This
AhmadRaufSubhani,
work proposes a machine learning framework for predicting consumers’ purchase
NationalUniversityofSciencesand
Technology(NUST),Pakistan intention (PI) and affective attitude (AA) from analyzing EEG signals. In this work, EEG
*Correspondence: signals are collected from 20 healthy participants while administering three advertising
KhondakerA.Mamun stimulisettings:product,endorsement,andpromotion.Afterpreprocessing,featuresare
mamun@cse.uiu.ac.bd
extracted in three domains (time, frequency, and time-frequency). Then, after selecting
Specialtysection: features using wrapper-based methods Recursive Feature Elimination, Support Vector
Thisarticlewassubmittedto Machine is used for categorizing positive and negative (AA and PI). The experimental
Brain-ComputerInterfaces,
results show that proposed framework achieves an accuracy of 84 and 87.00% for PI
asectionofthejournal
FrontiersinHumanNeuroscience and AA ensuring the simulation of real-life results. In addition, AA and PI signals show
Received:24January2022 N200 and N400 components when people tend to take decision after visualizing static
Accepted:02May2022
advertisement. Moreover, negative AA signals shows more dispersion than positive AA
Published:26May2022
signals.Furthermore,thisworkpavesthewayforimplementingsuchaneuromarketing
Citation:
MashrurFR,RahmanKM,MiyaMTI, frameworkusingconsumer-gradeEEGdevicesinareal-lifesetting.Therefore,itisevident
VaidyanathanR,AnwarSF,SarkerF thatBCI-basedneuromarketingtechnology canhelpbrands and businesses effectively
andMamunKA(2022)BCI-Based
predict future consumer preferences. Hence, EEG-based neuromarketing technologies
Consumers’ChoicePredictionFrom
EEGSignals:AnIntelligent canassistbrandsandenterprizesinaccuratelyforecastingfutureconsumerpreferences.
NeuromarketingFramework.
Front.Hum.Neurosci.16:861270. Keywords: Brain Computer Interface, neuromarketing, machine learning, electroencephalography, consumer
doi:10.3389/fnhum.2022.861270 behavior,patternrecognition,consumerneuroscience
FrontiersinHumanNeuroscience|www.frontiersin.org 1 May2022|Volume16|Article861270

| Mashruretal. |     |     |     |     |     |     |     |     |     |     | BCI-BasedConsumers’ChoicePrediction |     |     |     |
| ------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ----------------------------------- | --- | --- | --- |
1. INTRODUCTION
|     |     |     |     |     |     |     |     | In the | past, | EEG-based | neuromarketing-related |     |     | studies |
| --- | --- | --- | --- | --- | --- | --- | --- | ------ | ----- | --------- | ---------------------- | --- | --- | ------- |
examinedhowcommercialanditsdesigncouldaffectcustomers’
Neuromarketing is a subfield of marketing research that judgement and buying behavior. Khushaba et al. (2013) used
investigates customers’ cognitive and emotive responses photographs of crackers to study marketing stimulus in three
| to promoted |     | products | or  | services. | It is | an  | emerging |           |         |         |             |           |     |                |
| ----------- | --- | -------- | --- | --------- | ----- | --- | -------- | --------- | ------- | ------- | ----------- | --------- | --- | -------------- |
|             |     |          |     |           |       |     |          | different | shapes, | tastes, | and topping | to create | a   | sequence of 57 |
multidisciplinary area that brings together neuroscience, options. The participants were asked to pick their preferred set
technology, and traditional marketing. Neuromarketing uses and categorize their preferences across all sets. The change in
| Brain-Computer  |     | Interface   | (BCI) | technologies |           | to gain | insight   |              |          |      |             |     |             |           |
| --------------- | --- | ----------- | ----- | ------------ | --------- | ------- | --------- | ------------ | -------- | ---- | ----------- | --- | ----------- | --------- |
|                 |     |             |       |              |           |         |           | EEG spectral | activity | that | accompanied |     | it was then | measured. |
| into consumers’ |     | preferences | and   | purchase     | intention |         | triggered |              |          |      |             |     |             |           |
Yılmazetal.(2014)investigatedshoeimagesinordertoobtain
by marketing stimuli. Furthermore, one of the main objectives userfeedbackfromEEGsignalsintermsofdislikeorlikeofthe
of marketing professional is to present their advertisement in corresponding image. A similar strategy was utilized by Yadava
| such a | way that | the intended |     | consumer | response | is  | elicited. |     |     |     |     |     |     |     |
| ------ | -------- | ------------ | --- | -------- | -------- | --- | --------- | --- | --- | --- | --- | --- | --- | --- |
etal.(2017).Theyused42photographsofitemsinvarioushues
They spend $750 billion or more every year on marketing, and textures. Researchers then used the Hidden Markov model
promotion, and advertising to achieve this (Guttmann, classifier to extract four features from EEG and classify them.
| 2021). Hence, | there | is  | a significant | motivation |     | to investigate |     |             |     |            |      |             |     |                |
| ------------- | ----- | --- | ------------- | ---------- | --- | -------------- | --- | ----------- | --- | ---------- | ---- | ----------- | --- | -------------- |
|               |       |     |               |            |     |                |     | Bastiaansen | et  | al. (2018) | used | photographs | of  | Bruges tourist |
opportunities for targeting the appropriate market segments attractionstosplittheparticipantsintotwogroups.Onegroup
andcustomers. viewed11minand42softhefilm“InBruges”beforeseeingthe
Traditional research methods rely on consumers filling images,whereastheother(controlgroup)sawanunrelated9min
| out questionnaires, |     | focus | group | discussion, |     | or one-on-one |     |     |     |     |     |     |     |     |
| ------------------- | --- | ----- | ----- | ----------- | --- | ------------- | --- | --- | --- | --- | --- | --- | --- | --- |
and23smoviesample.Subsequently,EEGwasusedtorecordthe
interviewstodeterminetheirattitudestowardproducts,mostly differencesinemotionalresponseswithinthesegroups.
on post-facto basis (Hulland et al., 2018). Although these One of the most concern in marketing research is how
| approaches | are | simple, | they oftentimes |     | fail to | reflect | the true |     |     |     |     |     |     |     |
| ---------- | --- | ------- | --------------- | --- | ------- | ------- | -------- | --- | --- | --- | --- | --- | --- | --- |
consumersdealwithdiverseproductoptionsdependingontheir
state of mind of the customers, primarily because of the ownuniqueperceptionsofadvantagesandcosts.Theprefrontal
limitations associated with self-reported questionnaire surveys cortex (PFC), which is located in the frontal cortex (FC) of the
| (Rawnaque    | et al., | 2020). | Neuromarketing, |              | on  | the other | hand,     |              |       |      |                   |     |           |          |
| ------------ | ------- | ------ | --------------- | ------------ | --- | --------- | --------- | ------------ | ----- | ---- | ----------------- | --- | --------- | -------- |
|              |         |        |                 |              |     |           |           | brain, plays | a key | role | in the underlying |     | processes | of human |
| solves these | issues  | by     | focusing        | on capturing |     | the       | in-person |              |       |      |                   |     |           |          |
decision-making.SeveralstudiesshowthatthepartsofPFCare
response by taking into account brain response. As a result, involvedindecision-makingprocessesbyweighingtheprosand
thereisaneedfortechnology-enabledautonomouspredictionof cons of various options and outcomes (Tremblay and Schultz,
consumerpreferences.
|     |     |     |     |     |     |     |     | 1999; Daw | et al., | 2006). | People | can either | be  | attracted to or |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | ------- | ------ | ------ | ---------- | --- | --------------- |
In the last 20 years, researchers proposed several automatic repellent to a stimulus when they interact with it. Currently,
approaches with some of these considering the neurological researchersarelookingintobrainactivitysignalsthatarelinked
| mechanisms | that   | drive   | marketing |     | decision-making |                | and |                |     |           |             |     |      |                 |
| ---------- | ------ | ------- | --------- | --- | --------------- | -------------- | --- | -------------- | --- | --------- | ----------- | --- | ---- | --------------- |
|            |        |         |           |     |                 |                |     | to an increase | in  | emotional | involvement |     | when | people interact |
| contribute | to the | rapidly | expanding |     | field of        | neuromarketing |     |                |     |           |             |     |      |                 |
withmarketingstimuli(Langlebenetal.,2009;Vecchiatoetal.,
research. In neuromarketing studies, researchers use biometric 2010). When people experience a consumer product the blood
responses such as facial expression (Filipovic´ et al., 2020), eye flow of a particular part increases which is usually captured by
tracking(Khushabaetal.,2013),functionalmagneticresonance
fMRI(Telpazetal.,2015;Rawnaqueetal.,2020).Simultaneously,
imaging(fMRI)(HsuandCheng,2018),galvanicskinresponse the electrical activity of certain part of the human brain shows
(Ohira and Hirao, 2015), and electroencephalography (EEG) distinctpatternlikeoscillationinfrequencywhichiscapturedby
| (Golnar-Nik | et  | al., 2019), | magnetoencephalograpy |     |     |     | (MEG) |     |     |     |     |     |     |     |
| ----------- | --- | ----------- | --------------------- | --- | --- | --- | ----- | --- | --- | --- | --- | --- | --- | --- |
EEG(Telpazetal.,2015;Rawnaqueetal.,2020).Whileworking
(Hege et al., 2014) to extract customers’ insights. Previously, with EEG, researchers discovered strong links between people’s
the neuromarketing community was primarily interested in behavioralsystems(both positiveand bad) andtheirconsumer
fMRI, which assesses cerebral blood flow imaging and aids in actions. The activity of specific anatomical areas connected to
theidentificationofareastriggeredbystimuli(Rawnaqueetal.,
|     |     |     |     |     |     |     |     | emotional | processing | activity | in  | humans, | such as | the PFC and |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | ---------- | -------- | --- | ------- | ------- | ----------- |
2020). Despitethe fact thatthis technology hasa higher spatial FC, could be tracked to gather indirect variables of emotional
resolutionthananyothercurrentlyavailabletechnology,itslack processing (Davidson and Irwin, 1999). The anatomically and
| of portability, | high | cost, | and | low temporal | resolution |     | compel |              |         |      |        |                |     |                 |
| --------------- | ---- | ----- | --- | ------------ | ---------- | --- | ------ | ------------ | ------- | ---- | ------ | -------------- | --- | --------------- |
|                 |      |       |     |              |            |     |        | functionally | various | area | of PFC | are well-known |     | for its role in |
researchers to seek out other options. EEG and MEG, on the emotionformation(Davidson,2000).AccordingtoEEGspectral
other hand, are technologies with a better temporal resolution poweranalyses,leftPFCappearstobeasignificantcomponent
thanfMRIbutwithalowerspatialresolution(Rawnaqueetal.,
ofabraincircuitmediatingappetitiveapproachbehavior,while
| 2020). Due | to the | fact | that MEG | devices | require | a   | shielded |     |     |     |     |     |     |     |
| ---------- | ------ | ---- | -------- | ------- | ------- | --- | -------- | --- | --- | --- | --- | --- | --- | --- |
therightPFCappearstobeakeycomponentofaneuralcircuit
environment to detect the brain’s very low magnetic fields, mediatingdefensivewithdrawalbehavior(Davidson,2000,2004).
they are usually expensive. EEG technology has appealed to Measuring the activity of these regions can thus provide useful
| the neuromarketing |     | sector | as  | a reasonably | inexpensive, |     | well- |     |     |     |     |     |     |     |
| ------------------ | --- | ------ | --- | ------------ | ------------ | --- | ----- | --- | --- | --- | --- | --- | --- | --- |
informationaboutmarketingconceptslikeperceivedvalueand
established, and portable instrument from Krugman’s original thebrainunderpinningsofcustomerdecision-making.
usage in 1971 (Krugman, 1971). Taken together, EEG analysis In other studies, researchers used Support Vector Machine
asarealisticandefficienttoolcanaidourunderstandingofthe
|     |     |     |     |     |     |     |     | (SVM) and | K-Nearest |     | Neighbor | (KNN) | to  | quantify user |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | --------- | --- | -------- | ----- | --- | ------------- |
brain’sdecision-makingprocesses.
preferencesforaestheticsdisplayedasvirtualthree-dimensional
FrontiersinHumanNeuroscience|www.frontiersin.org 2 May2022|Volume16|Article861270

| Mashruretal. |     |     |     |     |     |     |     |     |     |     |     | BCI-BasedConsumers’ChoicePrediction |     |     |     |
| ------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ----------------------------------- | --- | --- | --- |
objects, with frequency bands acting as attributes for EEG andnegativePI(NPI).Themajorcontributionsofthisworkare
| segmentation | into | binary | classes | (Agarwal |     | and Dutta, | 2015; | listedbelow. |     |     |     |     |     |     |     |
| ------------ | ---- | ------ | ------- | -------- | --- | ---------- | ----- | ------------ | --- | --- | --- | --- | --- | --- | --- |
Ramadanetal.,2015).Hakimetal.(2018)usedSVMtocombine Aspreviousworldonlyusedproductimageasstimuli,
| EEG measurements |     | with | questionnaire |     | responses |     | to identify |     |     |     |     |     |     |     |     |
| ---------------- | --- | ---- | ------------- | --- | --------- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
•
Tothebestofauthors’knowledge,thisismostlikelythefirst
| the more | and the | less favored |     | parts. | The type | of  | classification |     |     |     |     |     |     |     |     |
| -------- | ------- | ------------ | --- | ------ | -------- | --- | -------------- | --- | --- | --- | --- | --- | --- | --- | --- |
studythatproposeMLframeworkforpredictingconsumers’
| system | used in | a BCI | system | is mostly | determined |     | by the |          |           |     |               |          |         |             |     |
| ------ | ------- | ----- | ------ | --------- | ---------- | --- | ------ | -------- | --------- | --- | ------------- | -------- | ------- | ----------- | --- |
|        |         |       |        |           |            |     |        | purchase | intention |     | and affective | attitude | (toward | advertising |     |
application’snatureandlocation.Withtherecentapplicationof
stimuli)fromEEGsignals.
| deep learning | (DL)    | in different |        | domain     | (Mashrur |     | et al., 2019, | •        |          |     |         |             |           |          |        |
| ------------- | ------- | ------------ | ------ | ---------- | -------- | --- | ------------- | -------- | -------- | --- | ------- | ----------- | --------- | -------- | ------ |
|               |         |              |        |            |          |     |               | We show  | the      | EEG | signals | differences | between   | positive | and    |
| 2021a; Nazi   | et al., | 2021),       | Teo et | al. (2017) | showed   |     | the subjects  |          |          |     |         |             |           |          |        |
|               |         |              |        |            |          |     |               | negative | response | (AA | and     | PI). In     | addition, | we also  | report |
3Dvirtualjewelryobjects,askedtoratethemonaLikertscale,
EEGsignalsdifferencesamongtheadvertisingstimuli.
| and then | categorized | EEG | signals | using | deep | learning. | Again, |     |     |     |     |     |     |     |     |
| -------- | ----------- | --- | ------- | ----- | ---- | --------- | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
•
Athoroughexperimentalevaluation(hyperparametertuning)
| Aldayel  | et al. (2020) | emphasized |     | the      | need | of spectral | valence    |            |     |              |     |                 |     |        |          |
| -------- | ------------- | ---------- | --- | -------- | ---- | ----------- | ---------- | ---------- | --- | ------------ | --- | --------------- | --- | ------ | -------- |
|          |               |            |     |          |      |             |            | is carried | out | to establish |     | the feasibility |     | of the | proposed |
| features | to improve    | prediction |     | accuracy | and  | the         | merging of |            |     |              |     |                 |     |        |          |
method.
| classifiers | using | deep learning |     | to extract | features. |     | In another |     |     |     |     |     |     |     |     |
| ----------- | ----- | ------------- | --- | ---------- | --------- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
•
|     |     |     |     |     |     |     |     | We also | suggest | consumer |     | grade device | to  | implement | such |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | ------- | -------- | --- | ------------ | --- | --------- | ---- |
work,Aldayeletal.(2021)measuredpreferenceindicestoclassify
Neuromarketingframeworkinreallifesetting.
| like and     | dislike | signals. | Authors | used       | data | from Yadava | et al. |     |     |     |     |     |     |     |     |
| ------------ | ------- | -------- | ------- | ---------- | ---- | ----------- | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
| (2017) which | used    | only     | product | as stimuli | and  | extracted   | time-  |     |     |     |     |     |     |     |     |
2. MATERIALS
frequencydomainfeatures.Usingthesefeatures,theycalculated
preferenceindiceswhichwaslaterusedtotrainmultiplemachine
Thissectiondiscussestheresearchparticipants,stimuli,anddata
learninganddeeplearning(DL)modelsfortheclassificationof
collectiondescription.
EEGsignals.Golnar-Niketal.(2019)employedLDAandSVM
classifierstoassesshoweffectivelyEEGsignalscoulddistinguish 2.1. Participants
| various | customer | preferences |     | and predict |     | the occurrence | of  |     |     |     |     |     |     |     |     |
| ------- | -------- | ----------- | --- | ----------- | --- | -------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Twentyhealthyyoungvolunteers(age:24±7.2)participatedin
decision-makinginanotherstudy.Telpazetal.(2015)published
|     |     |     |     |     |     |     |     | this study | with | no history | of  | neurological | or  | mental | disorders. |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | ---- | ---------- | --- | ------------ | --- | ------ | ---------- |
one of the most influential research articles in the field of Before the study, According to the Helsinki Declaration and
neuromarketingin2015.Theresearchersinthisstudyproposed
|     |     |     |     |     |     |     |     | Neuromarketing |     | Science | and | Business | Association |     | Code of |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------- | --- | ------- | --- | -------- | ----------- | --- | ------- |
thatEEGmaybeusedtoforecastfuturecustomerchoicesbased
|                |               |     |           |     |               |            |           | Ethics (NMSBA), |               | all | participants | provided | their         | consent.    | The |
| -------------- | ------------- | --- | --------- | --- | ------------- | ---------- | --------- | --------------- | ------------- | --- | ------------ | -------- | ------------- | ----------- | --- |
| on statistical | significance. |     | However,  |     | extant        | literature | indicates |                 |               |     |              |          |               |             |     |
|                |               |     |           |     |               |            |           | study is        | also approved |     | by the       | United   | International | University, |     |
| that, there    | is hardly     | any | validated | and | significantly |            | accurate  |                 |               |     |              |          |               |             |     |
InstitutionalResearchEthicsBoardcommittee.
| ML framework |     | predicting | consumer |     | purchase | intention | from |     |     |     |     |     |     |     |     |
| ------------ | --- | ---------- | -------- | --- | -------- | --------- | ---- | --- | --- | --- | --- | --- | --- | --- | --- |
EEG signals. Moreover, EEG-based research on consumers’ 2.2. Stimuli Description
affective attitude toward advertising stimuli is almost non- We use five different items in this research, each with its
existentincurrentliterature.Therefore,inthisstudy,wepropose endorsement and promotion-based (offers) advertisement. A
| a ML framework |     | for predicting |     | consumer |     | future | choices by |         |             |     |           |              |     |               |     |
| -------------- | --- | -------------- | --- | -------- | --- | ------ | ---------- | ------- | ----------- | --- | --------- | ------------ | --- | ------------- | --- |
|                |     |                |     |          |     |        |            | product | endorsement |     | is a tool | in marketing |     | communication |     |
linkingaffectiveattitude(AA)andpurchaseintention(PI)from
|     |     |     |     |     |     |     |     | that has | a positive | effect | on  | customers. | In  | the vast | majority |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | ---------- | ------ | --- | ---------- | --- | -------- | -------- |
EEGsignals. of cases, celebrities promote a product in a real-world setting.
Firstly, we collect EEG signals from the participants while Nevertheless, in order to avoid biasing the participants, we use
| they view | three | types of | advertisements |     | with | three | different |                     |     |     |               |     |        |             |       |
| --------- | ----- | -------- | -------------- | --- | ---- | ----- | --------- | ------------------- | --- | --- | ------------- | --- | ------ | ----------- | ----- |
|           |       |          |                |     |      |       |           | neutral endorsement |     | in  | our research. |     | On the | other hand, | sales |
dominantfeatures:onefocusedonproductfeatures;onecentered
|     |     |     |     |     |     |     |     | promotion | is a | technique | used | by marketers |     | where | they give |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | ---- | --------- | ---- | ------------ | --- | ----- | --------- |
on endorsement and one centered on promotion or offers. discounts, cashback or any other monetary offers so that the
| After preprocessing, |     | we  | extract | features |     | from | the signals. |     |     |     |     |     |     |     |     |
| -------------------- | --- | --- | ------- | -------- | --- | ---- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- |
customersareattractedtobuytheproduct.Inourcase,weoffer
| Afterward,  | using | feature  | selection | techniques, |     | we   | classify the |           |     |          |      |              |      |      |          |
| ----------- | ----- | -------- | --------- | ----------- | --- | ---- | ------------ | --------- | --- | -------- | ---- | ------------ | ---- | ---- | -------- |
|             |       |          |           |             |     |      |              | a buy one | get | one free | or a | 50% discount | with | that | product. |
| EEG signals | into  | positive | and       | negative    | for | both | AA and PI    |           |     |          |      |              |      |      |          |
ThestimuliareshowninFigure2,whereeachrowrepresentsa
| using SVM-RBF |     | classifier. | It should |     | be noted | that | as previous |     |     |     |     |     |     |     |     |
| ------------- | --- | ----------- | --------- | --- | -------- | ---- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
differentproduct:burgers,sunglasses,cake,hats,andcoats.The
| works only | focused | on  | only | product | stimuli | (Telpaz | et al., |     |     |     |     |     |     |     |     |
| ---------- | ------- | --- | ---- | ------- | ------- | ------- | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
baselineproductsareinthefirstcolumn,endorsementsareinthe
| 2015; Yadava | et  | al., 2017; | Aldayel |     | et al., | 2021), | we want |     |     |     |     |     |     |     |     |
| ------------ | --- | ---------- | ------- | --- | ------- | ------ | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
secondcolumn,andpromotionstimuliareinthethirdcolumn
| to propose | a more | robust        | and | generalize |      | machine  | learning  | foreachproduct. |     |     |     |     |     |     |     |
| ---------- | ------ | ------------- | --- | ---------- | ---- | -------- | --------- | --------------- | --- | --- | --- | --- | --- | --- | --- |
| framework  | that   | can recognize |     | beyond     | only | product. | Here, our |                 |     |     |     |     |     |     |     |
main focus was to find EEG pattern of the participants for 2.3. Data Collection
| these combined |     | heterogeneous |     | stimuli | setting. | Therefore, | we  |     |     |     |     |     |     |     |     |
| -------------- | --- | ------------- | --- | ------- | -------- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Thedatacollectionprocessisseparatedintothreestageswhich
addedendorsementandpromotionwhichweareimplementing are inspired by Levy et al. (2011) and Telpaz et al. (2015). In
for very first time. Taken together, we are using product, stage1,theexperimenterbriefstheparticipantsaboutthestimuli
| product | + endorsement, |     | and product |     | + promotion |     | to increase |         |           |     |         |               |     |         |         |
| ------- | -------------- | --- | ----------- | --- | ----------- | --- | ----------- | ------- | --------- | --- | ------- | ------------- | --- | ------- | ------- |
|         |                |     |             |     |             |     |             | so that | they will | be  | at ease | when watching |     | them on | screen. |
the generalizability of the proposed machine learning (ML) We do not show actual stimuli to the participants before the
framework. Consequently, we combine these stimuli and treat experiments, rather experimenters describe the promotion and
| as same | while classifying |     | of positive |     | and negative |     | AA and PI. |     |     |     |     |     |     |     |     |
| ------- | ----------------- | --- | ----------- | --- | ------------ | --- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
endorsementbeforehandusingadifferentimagethatisnotused
| as positive | AA (PAA), | negative |     | AA  | (NAA), | positive | PI (PPI), |     |     |     |     |     |     |     |     |
| ----------- | --------- | -------- | --- | --- | ------ | -------- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
asstimuli.Thismakessuretheparticipantswatchthestimulifor
FrontiersinHumanNeuroscience|www.frontiersin.org 3 May2022|Volume16|Article861270

Mashruretal. BCI-BasedConsumers’ChoicePrediction
enough to collect EEG data. After that, we use PsychoPy v3.0
(Peirce,2007)toshowthestimulustotheparticipantsandcollect
EEGdatasimultaneously.ThesamplingrateofEEGsignalsis128
Hz.Weusesixfrontalchannelsforthisworkbecauseprevious
studies suggest better performance with FC (Rawnaque et al.,
2020;Mashruretal.,2021b).IllustratedinFigure3.Throughout
the trial, each product was presented for 5 s, followed by an
endorsement or promotion. Moreover, before showing each
stimulus a black screen is shown with a white plus sign in the
middletokeepthefocusoftheparticipantsonthescreen.Instage
3,wegavetheparticipantsaquestionnaireinwhicheachstimulus
isaccompaniedbythefollowingstatements:1.Iwouldbehappy
to have x and 2. If given the opportunity, I am willing to buy
x. The first question is demonstrating the affective attitude and
thesecondoneispurchaseintention.Participantsrespondona
numericscaleof1–10(stronglydisagreetostronglyagree),which
waslaterconvertedinto:negative(1–5)andpositive(6–10).
3. METHODS
The workflow of our proposed algorithm is illustrated in
Figure4.Atfirst,wepreprocesstherawEEGsignalstoeliminate
the noise and then segment the data. Next, we extract features
FIGURE1|ElectrodepositioningofEMotivepoch+device. fromsignals.Afterthat,thebestfeaturesareselectedtoclassify
positive and negative AA and PI using SVM. The following
notation is used throughout this paper: The dataset Y =
[y ,y ,...,y ], where N is the number of participants. For any
1 2 N
participantY ,thesegmentedtimeseriesvectorforoneelectrode
N
isX(t)∈RT,whereTrepresentsthenumberofsamplesintime.
Again,thefeaturematrixisdenotedbyF=[f ,f ,...,f],wheref
1 2 t t
isthevector(allsamples)forafeatureandtisthetotalnumber
offeatures.
3.1. Pre-processing
Both customized scripts in MATLAB 2020a (MathWorks,
Natick, MA) and EEGLAB (Delorme and Makeig, 2004) are
used to preprocess EEG signals. Y is first normalized by
N
subtracting the mean from all sample points and dividing
each point by the standard deviation. The power line noise
is then removed using a notch filter (50 Hz). The signals
are then filtered using a third-order Butterworth bandpass
filter with a frequency range of 0.5–48 Hz to remove
high and low-frequency noise. Furthermore, Independent
component analysis (ICA) (Hyvärinen and Oja, 2000) is
used to distinguish the source of the signals and eliminate
noise such as eye blink, electrocardiogram, muscle movement,
and line noise. Finally, Y are segmented and averaged
N
FIGURE2|Stimuliusedinourexperimentalsetup,withthefirstcolumn
(participants wise), resulting in our structured X(t) time
representingthebaselineproduct,thesecondcolumndepictingendorsement
stimuli,andthelastcolumnrepresentingpromotionstimuli. seriesvector.
3.2. Feature Extraction
This subsection describes the extracted features for this study,
the first time while collecting EEG signals. In the second stage, categorized by: time domain, frequency domain, and time-
participants sit comfortably in front of a monitor that displays frequency domain features similar as Mamun et al. (2015).
the stimuli at a 75–100 cm distance. Then, We set the Emotiv Table1 shows the feature list used in this work. According to
Epoch+headset(electrodepositionillustratedinFigure1)inthe theliterature(Section1)PFCandFCaremostlyresponsiblefor
participant’s head and ensure the electrode conduction is good AA and PI (Davidson and Irwin, 1999; Davidson, 2000, 2004;
FrontiersinHumanNeuroscience|www.frontiersin.org 4 May2022|Volume16|Article861270

Mashruretal. BCI-BasedConsumers’ChoicePrediction
FIGURE3|ThestimulisequencewhilewecollecttheEEGdatafromparticipants.Tobegin,theparticipantsareshownablankscreentoaidinvisualstability.Then,it
showsasetofstimuliforaspecificproductatrandomintervals(firstaproduct,thenitsendorsement,orpromotion).Notethatbeforeshowingeachstimulusablack
screenisshownwithawhiteplussigninthemiddletokeepthefocusoftheparticipantsonthescreen.
FIGURE4|Illustrationoftheworkflowofourproposedpipeline.Atfirst,wepreprocesstherawEEGsignalstoeliminatethenoiseandpreparethesignals.Thenthree
typesoffeatures,namely,time,frequency,andtime-frequencydomainfeaturesareextracted.Then,wrapper-basedSupportVectorMachine-RecursiveFeature
Elimination(SVM-RFE)alongwithcorrelationbiasreductionisusedforfeatureselection.Lastly,weuseSVMwithradialbasisfunction(RBF)kernelforcategorizing
positiveaffectiveattitudeandnegativeaffectiveattitude.
Ramsøy et al., 2018). Therefore, we extract feature from FC promotion as stimuli. Therefore, we use a diverse feature set
in this work. When people watch a stimulus neurons within a to capture any changes in the electrical signal of the brain.
certain brain become active and pass a small electric current So, this work represents those features that captures distinct
which can be detected placing a sensor on the human scalp firingpatternfromEEGsignals.Previously,thepowerandsome
(Luck, 2014). Again, according to Davidson (2000) active area statistical features were widely used in Neuromarketing works
of the FC varies with corresponding neuromarketing stimuli. (Golnar-Niketal.,2019;Yadavaetal.,2017).Alongwiththese,
According to the extent literature, for the first time, we use we increased the feature set to capture more subtle changes
ML based neuromarketing work that uses endorsement and in the EEG for the mixed stimuli setting. From f to f , we
1 11
FrontiersinHumanNeuroscience|www.frontiersin.org 5 May2022|Volume16|Article861270

| Mashruretal. |     |     |     |     |     | BCI-BasedConsumers’ChoicePrediction |     |
| ------------ | --- | --- | --- | --- | --- | ----------------------------------- | --- |
TABLE1|Listofbasefeaturesusedinthiswork.
| Index | Featurename |     | Description |     |     |     |     |
| ----- | ----------- | --- | ----------- | --- | --- | --- | --- |
f1 Averagepower(Golnar-Niketal.,2019) MeanpowerofEEGcalculatedbypowerspectradensity(PSD)usingWelch’smethod
f2 Relativepower(Golnar-Niketal.,2019) BandpowerovertotalpoweroftheEEGsignals
| f3  | Hjorthmobility(Jenkeetal.,2014)   |     | Hjorthfeature                |     |     |     |     |
| --- | --------------------------------- | --- | ---------------------------- | --- | --- | --- | --- |
| f4  | Hjorthcomplexity(Jenkeetal.,2014) |     | Hjorthfeature                |     |     |     |     |
| f5  | Skewness(Islametal.,2013)         |     | DegreeofsymmetryofEEGsignals |     |     |     |     |
| f6  | Arithmeticmean(Jenkeetal.,2014)   |     | MeanvalueofEEGsignals        |     |     |     |     |
| f7  | Medianvalue(Islametal.,2013)      |     | MedianvalueofEEGsignals      |     |     |     |     |
| f8  | Minimumvalue(Islametal.,2013)     |     | LowestValueofEEGsignals      |     |     |     |     |
f9 Meanabsolutevalue(Phinyomarketal.,2012) MeanabsolutevalueofEEGsignals
f10 Interquartilerange(Ahammadetal.,2014) Differencebetween75thpercentilesand25thpercentiles
| f11 | Renyientropy(Inusoetal.,2007) |     | Non-linearentropyofEEGsignals |     |     |     |     |
| --- | ----------------------------- | --- | ----------------------------- | --- | --- | --- | --- |
f12 Absolutethresholdcrossing(Tkachetal.,2010) NumberoftimesEEGsignalscrossthresholdvalue:T1 =0.5
f13 Thresholdcrossing(Toledo-Pérezetal.,2020) NumberoftimesEEGsignalscrossthresholdvalue:T2 =4× 1 1 0 X(i)
|     |     |     |     |     |     | 1 0P | i= 1 |
| --- | --- | --- | --- | --- | --- | ---- | ---- |
f14 Zerocrossing(Jenkeetal.,2014) NumberoftimesEEGsignalschangessign
f15 Slopesignchange(SharmilaandGeethanjali,2018) NumberoftimesEEGsignalschangeslopesign
| f16 | Squareintegral(Phinyomarketal.,2012) |     | SummationofsquareEEGsignals |     |     |     |     |
| --- | ------------------------------------ | --- | --------------------------- | --- | --- | --- | --- |
f17 Logdetector(Phinyomarketal.,2012) Non-linearnaturalexponentialmeasurement
| f18 | Cardinality(WarisandKamavuako,2018) |     | Numberofdistinctvalue |     |     |     |     |
| --- | ----------------------------------- | --- | --------------------- | --- | --- | --- | --- |
f19 Autoregressivemodel(Zhangetal.,2017) LinearregressionofthepresentEEGsignalsobservationagainstoneormoreprecedingseries
data
f20 Detrendfluctuationanalysis(Oonetal.,2018) Non-linearmeasureofauto-correlationproperties
| f21 | Spectralcentroid(Peeters,2004) |     | Barycenterofthespectrum |     |     |     |     |
| --- | ------------------------------ | --- | ----------------------- | --- | --- | --- | --- |
f22 Spectralspread(Peeters,2004) Spreadofthespectrumarounditsmeanvalue
f23 Spectralkurtosis(Peeters,2004) Flatnessdistributionofspectrumarounditsmeanvalue
f24 Spectralentropy(Misraetal.,2004) Peakinessdistributionofthespectrum
f25
|     | Spectralflatness(Johnston,1988) |     | Noiselikenatureofthespectrum |     |     |     |     |
| --- | ------------------------------- | --- | ---------------------------- | --- | --- | --- | --- |
| f26 | Spectralcrest(Peeters,2004)     |     | Sinusoidalityofthespectrum   |     |     |     |     |
f27 Spectralslope(Peeters,2004) Lineardecreasingofthespectralamplitude
f28 Spectraldecrease(Peeters,2004) Decreasingofthespectralamplitude
f29 Spectralrolloffpoint(ScheirerandSlaney,1997) 95thpercentileofthespectralpowerdistribution
use statistical and power features that were before for EEG value of the SFs obtained with MATLAB 2020a. Despite their
signalspatternrecognition(Inusoetal.,2007;Islametal.,2013; ubiquitous usage in speech and audio signal classification, SFs
Ahammadetal.,2014;Jenkeetal.,2014;Golnar-Niketal.,2019). have recently been used for EEG signal categorization (Hassan
Moreover, this study finds dispersion to be prominent feature andSubasi,2016;Rashidetal.,2018).SFsrecordtheamplitude
for Neuromarketing, therefore we use features from f 2 to f . spectrum of EEG data, which gives discriminating information
|                                                            |     |     | 1 20 |                 |     |     |     |
| ---------------------------------------------------------- | --- | --- | ---- | --------------- | --- | --- | --- |
| Inaddition,literatureshowsthat,frequencybandoscillationand |     |     |      | betweenclasses. |     |     |     |
spectralchangesaresignificantwhilemeasuringEEGfordecision
making, attention, and consumer choice, consequently, we also 3.2.3.Time-FrequencyDomainFeatures(TFDFs)
|              |                  |                |                   | EEG signals | are complicated | in that they have | qualities in both |
| ------------ | ---------------- | -------------- | ----------------- | ----------- | --------------- | ----------------- | ----------------- |
| used diverse | spectral feature | for this study | (Foxe and Snyder, |             |                 |                   |                   |
2011; Nácher et al., 2013; Telpaz et al., 2015; Mashrur et al., thetemporalandfrequencydomains.EEGsignalsaresplitinto
2021b). six bands in this work utilizing wavelet packet transformation
|     |     |     |     | (WPT), which | may recover | frequency | information without |
| --- | --- | --- | --- | ------------ | ----------- | --------- | ------------------- |
3.2.1.TimeDomainFeatures(TDFs) leaving the temporal domain. In the literature, WPT has been
TDFs are calculated from X(t) decomposed in time domain. routinely utilized to distinguish frequency bands from EEG
Here, as mentioned in Table1, feature index f to f are used data (Wali et al., 2013; Vidyaratne and Iftekharuddin, 2017;
1 20
| asTDFs. |     |     |     | PhanikrishnaandChinara,2021). |     |     |     |
| ------- | --- | --- | --- | ----------------------------- | --- | --- | --- |
3.2.3.1.WPT
3.2.2.FrequencyDomainFeatures(FDFs)
FDFs are extracted to find changes in the frequency domain of The signal is decomposed by WPT into both detailed and
X(t).Inthiswork,weestimatespectralfeatures(SFs)described approximate coefficients. The extracted coefficients up to a
in Table1 as feature index f 21 to f 29 . In this study, the average definedlevelcouldbeconsideredasfeaturesbecausetheirvalues
FrontiersinHumanNeuroscience|www.frontiersin.org 6 May2022|Volume16|Article861270

| Mashruretal. |     |     |     |     |     |     |     |     |     | BCI-BasedConsumers’ChoicePrediction |     |     |     |
| ------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | ----------------------------------- | --- | --- | --- |
aredependentonthetimeandfrequencydomaincharacteristics themodelistrainedusingthestructuralriskreductioncriterion
of the EEG signals. WPT creates a subspace tree of a signal bycombiningamaximalmarginapproachwithakernelmethod
with distinct frequency characteristics by recursively applying (Gunn et al., 1998; Hart et al., 2000). SVM utilizes a kernel
high-passandlow-passfilters(PercivalandWalden,2000).Let, functiontotranslatetheinputsintoahigh-dimensionalfeature
= 0,..,2a−1,denotetheWPTcoefficientsatlevela.
Q (k),n space,whereaslearningderivesthedecisionboundariesdirectly
a,b
Thewaveletpacketcoefficientsarethencomputedusingthetwo from the training data set. Then, it constructs an optimal
waveletpacketorthogonalbasesequations: separation hyperplane in the feature space. The choice of an
|     |     |     |     |     |     |     | appropriate | kernel      | function | is       | crucial     | for optimizing | SVM        |
| --- | --- | --- | --- | --- | --- | --- | ----------- | ----------- | -------- | -------- | ----------- | -------------- | ---------- |
|     |     |     |     |     |     |     | classifier  | performance |          | (Gunn et | al., 1998). | We use         | RBF kernel |
L − 1H(s)Q
Q (i)= P (cid:0)2k+1−lmodN b−1(cid:1) (1) forit’sbetterperformanceearlierresearchbasedonEEGsignals
| a,2b | l= 0 | a−1,b |     |     |     |     |             |       |           |     |            |         |              |
| ---- | ---- | ----- | --- | --- | --- | --- | ----------- | ----- | --------- | --- | ---------- | ------- | ------------ |
|      |      |       |     |     |     |     | (Li et al., | 2014; | Zainuddin | et  | al., 2018; | Anuragi | and Sisodia, |
− 2 0 1 9 ) . T o in c r e a s e c la s s i fi c at i o n p e r fo r m a n c e ,a n S V M c l as sifi e r ’s
| Q   | (i)= P L 1G(s)Q |     | (cid:0)2k+1−lmodN |     | b−1(cid:1) | (2) |     |     |     |     |     |     |     |
| --- | --------------- | --- | ----------------- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
a,2b+1 l= 0 a−1,b h y p e r -p a ra m e t e r s , n o t a b l y t h e r e g u la r iz a ti o n p a ra m et e r C a n d
|            |          |         |         |           |       |     | the gamma, | are | tuned | during | training as | demonstrated | most |
| ---------- | -------- | ------- | ------- | --------- | ----- | --- | ---------- | --- | ----- | ------ | ----------- | ------------ | ---- |
| Where H(s) | and G(s) | are the | impulse | responses | which | are |            |     |       |        |             |              |      |
highpass and lowpass filters of the wavelet packets respectively efficientandaccurateinHsuetal.(2003).WeutilizetheLIBSVM
and i = 1...N and N = N/2 (Percival and Walden, 2000). (ChangandLin,2011)functiontoclassifyourwork.Inaddition,
|          |                   | b   | b         |     |           |       |              |             |     |             |       |                 |       |
| -------- | ----------------- | --- | --------- | --- | --------- | ----- | ------------ | ----------- | --- | ----------- | ----- | --------------- | ----- |
|          |                   |     |           |     |           |       | we use other | classifiers |     | too namely, | Naive | Bayes, Decision | tree, |
| Here, we | use Meyer wavelet | for | computing | the | sub-bands | as it |              |             |     |             |       |                 |       |
K-NearestNeighbor(Bonaccorso,2017).
| showed better | performance | in  | previous | work (Mamun, |     | 2011) |     |     |     |     |     |     |     |
| ------------- | ----------- | --- | -------- | ------------ | --- | ----- | --- | --- | --- | --- | --- | --- | --- |
usingEEGsignals.
|     |     |     |     |     |     |     | 3.4. Metrics |     | for | Assessing | Performance |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------------ | --- | --- | --------- | ----------- | --- | --- |
ToextractTFDFs,X(t)isdecomposedinfivelevelsextracting
|                   |          |     |          |           |     |     | In order | to access | the | performance | of our | proposed | pipeline, |
| ----------------- | -------- | --- | -------- | --------- | --- | --- | -------- | --------- | --- | ----------- | ------ | -------- | --------- |
| sixbands,namely,δ | =0−4Hz,θ |     | =4−8Hz,α | =8−12Hz,β |     | 1 = |          |           |     |             |        |          |           |
severalmetrics,namely,accuracy(Acc.),sensitivity(Sens.),and
| 12−20Hz,β    | =20−32Hz,γ | =32−64Hz.Thenallthefeatures, |           |           |       |      |                     |     |     |     |     |     |     |
| ------------ | ---------- | ---------------------------- | --------- | --------- | ----- | ---- | ------------------- | --- | --- | --- | --- | --- | --- |
|              | 2          |                              |           |           |       |      | specificity(Spec.). |     |     |     |     |     |     |
| as mentioned | in Table1, | were                         | extracted | from each | band, | with |                     |     |     |     |     |     |     |
atotalof246features.Again,aspowerfeaturesperformedwell
in the literature (Golnar-Nik et al., 2019), ratio of average and Sens= TP
|     |     |     |     |     |     |     |     |     |     |     | TP+FN |     | (3) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ----- | --- | --- |
relativepoweralsocalculatedasseparatefeatures.Theratiosare:
| θ,α, β1,     | β2, γ ,α, β1, β2, | γ β | β2, γ β2, | γ γ            |     |     |     |     |     |       |     |     |     |
| ------------ | ----------------- | --- | --------- | -------------- | --- | --- | --- | --- | --- | ----- | --- | --- | --- |
|              |                   | , , | ,         | , .            |     |     |     |     |     |       |     |     |     |
| δ δ δ        | δ δ θ θ θ         | θ α | α α β1    | β1 β2          |     |     |     |     |     |       |     |     |     |
| 3.3. Feature | Selection         |     | and       | Classification |     |     |     |     |     | Spec= | TN  |     | (4) |
TN+FP
| To select | the best feature | set, | we use | wrapper-based |     | Support |     |     |     |     |     |     |     |
| --------- | ---------------- | ---- | ------ | ------------- | --- | ------- | --- | --- | --- | --- | --- | --- | --- |
VectorMachine-RecursiveFeatureElimination(SVM-RFE)with
correlation bias reduction (CBR) (Yan and Zhang, 2015). ACC= TP+TN (5)
TP+TN+FN+FP
Initially,Guyonetal.(2002)proposeSVM-RFEwhichevaluates
features using criteria derived from SVM model coefficients, where FP,FN,TP, and TN are the number of false positives,
then recursively eliminates features with small criteria. This false negatives, true positives, and true negatives, respectively.
method can be used in both linear and nonlinear situations Wereportthemeanvalueofthemetrices.TheShapiro-Wilktest
(Guyonetal.,2002;Rakotomamonjy,2003).Whentheoptimal is used to determine the normality of the data. Moreover, we
decisionfunctionisnonlinear,thenonlinearSVM-RFEapproach useWilcoxonSigned-RankedTestfornonparametrichypothesis
is preferred since it incorporates a novel kernel method. We testing.Again,Friedmantestisusedformatched,nonparametric
also employed a non-linear variant with a radial basis function datatofinddifferencesamongadvertisements.
(RBF)asthekernelinourresearch.Foritsbackwardelimination
method, SVM-RFE may represent feature dependencies. SVM- 4. RESULTS
RFEdoesnotusecross-validation(cv)accuracyonthetraining
data as a selection criterion, which means it is less prone This section represents the results obtained by the proposed
to overfitting, can fully utilize the training data, and has a model. We report the performance of channel pairs for both
substantiallyshorterexecutiontime,especiallywhentherearea PI and AA. In addition, We present the report the dispersion
highnumberofcandidatefeatures.Asaresult,it’sbeenapplied differences between PAA and NAA. Furthermore, we report
to a range of problems, such as gene selection (Guyon et al., the most contributing feature domain and EEG bands while
2002; Rakotomamonjy, 2003; Duan et al., 2005; Mundra and classifyingthesignals.
Rajapakse,2009).However,whensomeofthefeaturesarehighly Inthiswork,weuseleave-one-subject-out(LOSO)evaluation
associated,theassessingcriteriaofthesefeatureswouldbealtered techniques where the features are separated in 20 as the total
by underestimating their value. To address this, inspired by numberofsubjectsis20.Everysubjectisusedforthetestsetonly
Tolo¸siandLengauer(2011)andYanandZhang(2015)suggested once,whiletherestisusedasthetrainingset.
arobusttechnique,SVM-RFE+CBR,forestimatinggassensor Figure5A illustrates the grand average of positive AA and
characteristics. negative AA in the time domain for AF3 channel. Similarly,
In this work, SVM is used for classification. The SVM Figure5B also illustrates the same for PI. It is evident that
identifies the appropriate boundary in the feature space where negative and positive signals have N200 to N400 components
FrontiersinHumanNeuroscience|www.frontiersin.org 7 May2022|Volume16|Article861270

Mashruretal. BCI-BasedConsumers’ChoicePrediction
FIGURE5|Exampleofgrandaverage5sEEGsignalsintimedomainforAF3channel.Itisevidentthatnegative(red)signalshavehigherdispersionthanpositive
(green).(A)AA.(B)PI.
FIGURE6|IllustrationoftheaverageofEEGsignalsofproduct,endorsement,andpromotion.(A)PAA,(B)NAA,(C)PPI,(D)NPI.
respectively.Moreover,totestdispersionofnegativeandpositive there is a negative peak and for promotion, there is a positive
signals, a Wilcoxon Signed-Ranked Test (WSRT) indicates that peak.However,theproductshowsneutralityinthesignals.
the standard deviation of NAA is significantly higher than the Again,inTable2,wereporttheperformanceofourproposed
standard deviation of PAA Z = 133,p = 0.0006. However, modelforfourcombinations.Wetakethefirstthreesymmetrical
WSRTdoesnotfinddispersionbetweenNPIandPPI. channels as pairs from EEG montage, namely AF3+AF4,
Figure6 illustrates the average of EEG signals of product, F3+F4, and F7+F8. The fourth combination is all FC channels
endorsement, and promotion: Figure6A (PAA), Figure6B (combination of three pairs). The combination of all channels
(NAA),Figure6C(PPI),andFigure6D(NPI).Itisalsoevident gives the best results of accuracy 84.00 and 87.00% for PI and
fromthePAAandPPI(Figures6A,C)havelessdispersionthan AA,respectively.Inaddition,amongthreepairsF3+F4performs
NAAandNPI(Figures6B,D)similartoFigure5.Moreover,for the best with an accuracy of 81.50 and 85.50% for PI and AA,
NAAandNPI(Figures6B,D),threeadvertisingstimulishowed respectively.Forallthecombinations,sensitivityishigherthan
different EEG signatures (around 1.5–4.0 s). For endorsement, specificitymeaningthatthetruepositiveishighinourproposed
FrontiersinHumanNeuroscience|www.frontiersin.org 8 May2022|Volume16|Article861270

| Mashruretal. |     |     |     |     |     |     |     | BCI-BasedConsumers’ChoicePrediction |     |     |
| ------------ | --- | --- | --- | --- | --- | --- | --- | ----------------------------------- | --- | --- |
TABLE2|Performanceofourproposedframework.
| Channel             |     |     |         |     |          | PI  |          |         | AA       |          |
| ------------------- | --- | --- | ------- | --- | -------- | --- | -------- | ------- | -------- | -------- |
|                     |     |     | Acc.(%) |     | Spec.(%) |     | Sens.(%) | Acc.(%) | Spec.(%) | Sens.(%) |
| AF3+AF4             |     |     | 80.00   |     | 71.52    |     | 85.53    | 84.75   | 71.31    | 91.14    |
| F3+F4               |     |     | 81.50   |     | 77.21    |     | 84.30    | 85.50   | 72.09    | 91.53    |
| F7+F8               |     |     | 79.00   |     | 72.78    |     | 83.05    | 82.50   | 65.12    | 90.77    |
| AF3+AF4+F3+F4+F7+F8 |     |     | 84.00   |     | 75.32    |     | 89.66    | 87.00   | 74.41    | 92.98    |
FIGURE7|Performanceoftheproposedmodelwithnumberoffeatures.Here,forchannelcombinationbestresultsarestarted(*)markedwithrespectivecolor
verticaltonumberoffeatures.(A)AA.(B)PI.
framework. We also use other classification methods for all six bands. Here, it can be seen that theta (θ) band mostly
|     |     |     |     |     |     |     | dominatesfollowedbydelta(δ),beta2(β |     | ),andbeta1(β |     |
| --- | --- | --- | --- | --- | --- | --- | ----------------------------------- | --- | ------------ | --- |
FC channels. Naive Bayes, Decision Tree, K-Nearest Neighbors 1 2 )bands.
| yields 67.14,    | 70.24,  | 72.14%  | for PI and   | 70.78, | 72.62,  | 73.33% for |               |     |     |     |
| ---------------- | ------- | ------- | ------------ | ------ | ------- | ---------- | ------------- | --- | --- | --- |
| AA,respectively. |         |         |              |        |         |            | 5. DISCUSSION |     |     |     |
| Again,           | Figure7 | depicts | the accuracy | with   | respect | to the     |               |     |     |     |
number of features. Here, we present the same combination of Inthisstudy,wedemonstrateaframeworktoclassifyconsumer
channelsreportedinTable2.Itisevidentthattheperformance choice from EEG signals. This is the initial work that predicts
of the model improves with the number of features. However, thepurchaseintention(PI)usingtheMLframework.Inaddition,
for AA the experimented total number of features is 45 as the thisismostlikelythefirstresearchadoptingadvertisingstimuli
increasing features more than that leads to poor performance. asaffectiveattitude(AA)prediction.
Again,forPIwereportthehighest40featuresastheperformance For the first time, we proposed that NAA has higher
stabilizedaround35features. EEG signals dispersion than PAA which is illustrated in
We also evaluate the difference of AA and PI among three Figure5. In addition, Figure6 depicts that positive AA and PI
advertisements, namely, product, endorsement, and promotion (Figures6A,C) have less dispersion than negative AA and PI
for both reported (reported outcome from the participant) and (Figures6B,D).Moreover,fromFigure5,itisevidentthatEEG
predicted(theoutcome wegetfrom ourproposed framework). signalsshowanegativepeakafterwatchingadvertisingstimuli.
Friedmantestofdifferencesamongrepeatedmeasures(reported ItshouldbementionedthatbothNAAandNPIhavethepeakin
outcome of three advertisements for AA) is conducted which N200 where the PAA and PPI show the peak in N400 which is
yield a Chi-square value of 20.86 which was significant (P < alignedwithpreviousworks(Telpazetal.,2015).Takentogether,
0.0001). The exact same test for predicted outcome result a this indicates that subjects tend to decide NAA and NPI faster
Chi-square value of 12.50 which was significant (P = 0.0019). thanPAAandPPI.Then,aftertakingthedecisionssubjectsstill
Again,forPI,Friedmantestforreportedoutcomegivearesultof thinkorrevisittheirdecisionaboutthenegativeattitudetoward
=
Chi-square value of 15.92 which was significant (P 0.0003). particularproductswhichmakestheEEGsignalsmoredispersed
Moreover, for predicted outcome the Chi-square value of 6.75 thanapositiveattitude.
whichwassignificant(P=0.0343). Moreover,tothebestofauthorsknowledge,forthefirsttime,
weusetime,frequency,andtime-frequencydomainfeaturesfor
| Again, | Figure8 | depicts | the percentage | of  | features( | domain |     |     |     |     |
| ------ | ------- | ------- | -------------- | --- | --------- | ------ | --- | --- | --- | --- |
wise) for best results reported in Table2 for both AA and the ML framework for the Neuromarketing application. It is
PI. Here, time-frequency domain features dominate the most evident from Figures8A,B that subjects’ EEG signals are most
significant features in the classification task. Again, we also susceptible to the time-frequency domain which indicates that
illustrate the percentage of time-frequency domain features for whilechoosingaproductEEGsignalsshiftamongbands.Again,
FrontiersinHumanNeuroscience|www.frontiersin.org 9 May2022|Volume16|Article861270

Mashruretal. BCI-BasedConsumers’ChoicePrediction
FIGURE8|(A,C)Illustratethepercentageoffeatures(domainwise)forworkingresultsreportedinTable2.(B,D)Illustratethepercentageoftime-frequencydomain
features(bandwise)forbestresultsreportedinTable2.
Figures8B,Dreferthatθ bandisthemostsignificantTFDFsfor different results. Afterward, we perform the same with the
bothAAandPIassupportedbypreviousstudies(Telpazetal., predictedresultsanditisalsoyieldingsignificantresults.
2015;Rawnaqueetal.,2020;Mashruretal.,2021b).Interestingly, Again, according to Figures6B,D, NAA and NPI show that
δ band is the second most used feature and for the first which promotion stimuli trigger a positive peak around 1.5 and 4 s
is an unique finding in context of Neuromarketing research. whileendorsementstimulitriggeranegativepeak.However,for
Accordingtoapreviousstudy,δbandisresponsiblefordecision- product stimuli the EEG signals do not show any peak. This
making(Nácheretal.,2013)whichmayexplainthesignificance can be explained by promotion having a 50% off which creates
of δ band in our study. Further study is needed to explore this the positive peak and endorsers bring the negative peak. Note
band’simportance. that,PAAandPPIdonotshowanykindofpeakforadvertising
Ourmethodsimprovethelevelofgeneralizationbyincreasing differentiation.Foradditionalinvestigation,afuturestudywith
the number of subjects along with rigorous hyperparameter simultaneouseyetrackingisrequired.
tuningwiththeSVMRBFkernel.Wechosewrapper-basedSVM- Lastly, this work paves the way for implementing such
RFEwithCBRwhichusesanSVMclassifierwhileselectingthe a neuromarketing framework using consumer-grade EEG
best set of features. This method removes the highly correlated devices (CEEGDs) in a real-life setting. The most commonly
featuresfirstandthenranksthefeaturesbasedontheSVM-RBF used CEEGDs (provided channel/s) are Emotiv Insight
kernel. We tune the α and C parameters in the kernel to find (AF ,AF ,P ,T ,T ), Neurosky Mindwave 2 (Fp ), Muse 2
3 4 z 7 8 1
thebestworkingmodelsusingtheLOSOevaluationtechnique. (AF ,AF ), FocusCalm (F Z). According to our result, Emotiv
7 8 p
As the feature selection is wrapper-based, this uses a classifier Insight can be a good choice for practical application as this
whileselectingthefeatureset.Wealsouseotherclassifierssuchas gives comparatively better performance. Though due to our
NaiveBayes,DecisionTree,K-NearestNeighborswhichyieldthe device limitation (Emotive epoch + does not has F Z channel),
p
accuracyofbothAAandPIaround67–73%whichiscompared wearenotabletomeasuretheperformanceofthechannelF Z,
p
low compared to current results. Taken together, our model Focus Calm can be an interesting choice for future researchers
ensuresarobustclassificationthatworksbestwiththeSVM-RBF toexploreit’spotential.Basedonthesearchforavailabledevices
kernelclassifier. inthemarket,noCEEGDsofferF3,F4channels.Anintegration
Our proposed framework also simulates the real-life results of these channels in CEEGDs will improve their performances
which are proved by significant results in the ANOVA test as supported by the findings of our research. Nevertheless, the
(Friedman test). At first, we test the reported results for three performance will be largely dependent on the sensors of each
advertisements for both AA and PI which give significantly deviceandthequalityoftherawEEGsignals.
FrontiersinHumanNeuroscience|www.frontiersin.org 10 May2022|Volume16|Article861270

| Mashruretal.  |     |     |     |     |     |     |     |        |           |     | BCI-BasedConsumers’ChoicePrediction |     |     |     |
| ------------- | --- | --- | --- | --- | --- | --- | --- | ------ | --------- | --- | ----------------------------------- | --- | --- | --- |
| 6. CONCLUSION |     |     |     |     |     |     |     | ETHICS | STATEMENT |     |                                     |     |     |     |
This research presents a comprehensive machine learning The studies involving human participants were reviewed
framework to classify EEG signals based on consumers’ future and approved by Institutional Research Ethics Board, United
choices: affective attitude and purchase intention. We also International University. The patients/participants provided
propose that a negative attitude has higher dispersion and theirwritteninformedconsenttoparticipateinthisstudy.
| faster response. | In           | addition, | TFDFs     | have     | mostly   | used         | features |        |               |     |     |     |     |     |
| ---------------- | ------------ | --------- | --------- | -------- | -------- | ------------ | -------- | ------ | ------------- | --- | --- | --- | --- | --- |
| in our proposed  | framework.   |           | Moreover, |          | the      | proposed     | model is |        |               |     |     |     |     |     |
|                  |              |           |           |          |          |              |          | AUTHOR | CONTRIBUTIONS |     |     |     |     |     |
| also able        | to replicate | real-life |           | reported | results. | In the       | future,  |        |               |     |     |     |     |     |
| researchers      | can work     | on        | different | types    | of       | endorsements | such     |        |               |     |     |     |     |     |
KM,FM,KR,MM,FS,RV,andSAcontributedtoconceptionand
asneutralendorsementandcelebrityendorsement.Participants
|               |     |         |          |       |          |             |     | design of   | the study.   | KR, MM, | and KM     | revised  | the draft        | of the |
| ------------- | --- | ------- | -------- | ----- | -------- | ----------- | --- | ----------- | ------------ | ------- | ---------- | -------- | ---------------- | ------ |
| in this study | are | limited | to young | adult | subjects | considering |     |             |              |         |            |          |                  |        |
|               |     |         |          |       |          |             |     | manuscript. | FM performed |         | the formal | analysis | and illustration |        |
themastargetconsumersofthemarketingstimuli.Infuture,a
andwrotethefirstdraftofthemanuscript.KMsupervisedand
morediversesubjectgroupmaybeincludedalongsidedifferent
administeredtheproject.Allauthorscontributedtomanuscript
| intervals | of purchase | like | daily | required | products, | weekly | or  |     |     |     |     |     |     |     |
| --------- | ----------- | ---- | ----- | -------- | --------- | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
revision,read,andapprovedthesubmittedversion.
| monthly, | and product-groups |     |     | like fresh, | stationery, |     | home or |     |     |     |     |     |     |     |
| -------- | ------------------ | --- | --- | ----------- | ----------- | --- | ------- | --- | --- | --- | --- | --- | --- | --- |
officeappliances,etc.Thefutureresearchersmayalsoaddmore
| featuresandfine-tunetheclassifiertoimprovethesingle-channel |     |     |     |     |     |     |     | FUNDING |     |     |     |     |     |     |
| ----------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | ------- | --- | --- | --- | --- | --- | --- |
performance.Lastly,itisevidentthatneuromarketingisefficient
inforecastingconsumerpreferencesandbehaviors. This study was funded by Market-Brain: A Neuromarketing
|      |              |     |           |     |     |     |     | System for                    | Advanced  | Market    | Research | Project   | Under        | ICT  |
| ---- | ------------ | --- | --------- | --- | --- | --- | --- | ----------------------------- | --------- | --------- | -------- | --------- | ------------ | ---- |
|      |              |     |           |     |     |     |     | innovation                    | Fund, ICT | Division, | MoPTIT,  | GOB,      | Project      | Code |
| DATA | AVAILABILITY |     | STATEMENT |     |     |     |     |                               |           |           |          |           |              |      |
|      |              |     |           |     |     |     |     | No. 1280101-120008431-3631108 |           |           | and      | Institute | for Advanced |      |
The raw data supporting the conclusions of this article will be Research, United International University, Bangladesh (Code:
madeavailablebytheauthors,withoutunduereservation. IAR/01/19/SE/10).
REFERENCES Daw,N.D.,O’doherty,J.P.,Dayan,P.,Seymour,B.,andDolan,R.J.(2006).
Corticalsubstratesforexploratorydecisionsinhumans.Nature441,876–879.
Agarwal,S.,andDutta,T.(2015).Neuromarketingandconsumerneuroscience: doi:10.1038/nature04766
current understanding and the way forward. Decision 42, 457–462. Delorme, A., and Makeig, S. (2004). EEGlab: an open source toolbox for
doi:10.1007/s40622-015-0113-1 analysis of single-trial EEG dynamics including independent component
Ahammad, N., Fathima, T., and Joseph, P. (2014). Detection of epileptic analysis. J. Neurosci. Methods 134, 9–21. doi: 10.1016/j.jneumeth.2003.
| seizure | event and | onset | using EEG. | BioMed | Res. | Int. 2014, | 450573. | 10.009 |     |     |     |     |     |     |
| ------- | --------- | ----- | ---------- | ------ | ---- | ---------- | ------- | ------ | --- | --- | --- | --- | --- | --- |
doi:10.1155/2014/450573 Duan,K.-B.,Rajapakse,J.C.,Wang,H.,andAzuaje,F.(2005).MultipleSVM-
Aldayel, M., Ykhlef, M., and Al-Nafjan, A. (2020). Deep learning for eeg- RFEforgeneselectionincancerclassificationwithexpressiondata.IEEETrans.
based preference classification in neuromarketing. Appl. Sci. 10, 1525. Nanobiosci.4,228–234.doi:10.1109/TNB.2005.853657
doi:10.3390/app10041525 Filipovic´, F., Baljak, L., Naumovic´, T., Labus, A., and Bogdanovic´, Z. (2020).
Aldayel, M., Ykhlef, M., and Al-Nafjan, A. (2021). Recognition of consumer “Developingawebapplicationforrecognizingemotionsinneuromarketing,”
preferencebyanalysisandclassificationEEGsignals.Front.Hum.Neurosci. inMarketingandSmartTechnologies,edsÁ.Rocha,J.L.Reis,M.K.Peterand
2020,604639.doi:10.3389/fnhum.2020.604639 Z.Bogdanovic´(Maia:Springer),297–308.doi:10.1007/978-981-15-1564-4_28
Anuragi, A., and Sisodia, D. S. (2019). Alcohol use disorder detection Foxe,J.J.,andSnyder,A.C.(2011).Theroleofalpha-bandbrainoscillationsas
using EEG signal features and flexible analytical wavelet transform. asensorysuppressionmechanismduringselectiveattention.Front.Psychol.2,
Biomed. Signal Process. Control 52, 384–393. doi: 10.1016/j.bspc.2018. 154.doi:10.3389/fpsyg.2011.00154
10.017 Golnar-Nik, P., Farashi, S., and Safari, M.-S. (2019). The application
Bastiaansen,M.,Straatman,S.,Driessen,E.,Mitas,O.,Stekelenburg,J.,andWang, of EEG power for the prediction and interpretation of consumer
L.(2018).Mydestinationinyourbrain:anovelneuromarketingapproachfor decision-making: a neuromarketing study. Physiol. Behav. 207, 90–98.
evaluatingtheeffectivenessofdestinationmarketing.J.Destin.Mark.Manage. doi:10.1016/j.physbeh.2019.04.025
7,76–88.doi:10.1016/j.jdmm.2016.09.003 Gunn,S.R.,etal.(1998).Supportvectormachinesforclassificationandregression.
Bonaccorso, G. (2017). Machine Learning Algorithms. Birmingham: Packt ISISTechn.Rep.14,5–16.
PublishingLtd. Guttmann,A.(2021).GlobalAdvertisingRevenue.Availableonlineat:https://www.
Chang,C.-C.,andLin,C.-J.(2011).LIBSVM:alibraryforsupportvectormachines. statista.com/statistics/236943/global-advertising-spending/(accessedMarch1,
| ACMTrans.Intell.Syst.Technol.2,1–27.doi:10.1145/1961189.1961199 |     |     |     |     |     |     |     | 2022). |     |     |     |     |     |     |
| --------------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | ------ | --- | --- | --- | --- | --- | --- |
Davidson, R. J. (2000). Affective style, psychopathology, and Guyon, I., Weston, J., Barnhill, S., and Vapnik, V. (2002). Gene selection for
resilience: brain mechanisms and plasticity. Am. Psychol. 55, 1196. cancerclassificationusingsupportvectormachines.Mach.Learn.46,389–422.
| doi:10.1037/0003-066X.55.11.1196 |     |     |     |     |     |     |     | doi:10.1023/A:1012487302797 |     |     |     |     |     |     |
| -------------------------------- | --- | --- | --- | --- | --- | --- | --- | --------------------------- | --- | --- | --- | --- | --- | --- |
Davidson, R. J. (2004). What does the prefrontal cortex “do” in affect: Hakim,A.,Klorfeld,S.,Sela,T.,Friedman,D.,Shabat-Simon,M.,andLevy,D.
perspectivesonfrontalEEGasymmetryresearch.Biol.Psychol.67,219–234. J.(2018).Pathwaystoconsumersminds:usingmachinelearningandmultiple
doi:10.1016/j.biopsycho.2004.03.008 EEGmetricstoincreasepreferencepredictionaboveandbeyondtraditional
Davidson, R. J., and Irwin, W. (1999). The functional neuroanatomy measurements.bioRxiv2018,317073.doi:10.1101/317073
of emotion and affective style. Trends Cogn. Sci. 3, 11–21. Hart,P.E.,Stork,D.G.,andDuda,R.O.(2000).PatternClassification.NewYork,
| doi:10.1016/S1364-6613(98)01265-0 |     |     |     |     |     |     |     | NY:WileyHoboken. |     |     |     |     |     |     |
| --------------------------------- | --- | --- | --- | --- | --- | --- | --- | ---------------- | --- | --- | --- | --- | --- | --- |
FrontiersinHumanNeuroscience|www.frontiersin.org 11 May2022|Volume16|Article861270

Mashruretal. BCI-BasedConsumers’ChoicePrediction
Hassan,A.R.,andSubasi,A.(2016).Automaticidentificationofepilepticseizures 4th International Conference on Electrical Information and Communication
fromEEGsignalsusinglinearprogrammingboosting.Comput.MethodsProg. Technology(EICT)(Khulna),1–5.doi:10.1109/EICT48899.2019.9068806
Biomed.136,65–77.doi:10.1016/j.cmpb.2016.08.013 Misra,H.,Ikbal,S.,Bourlard,H.,andHermansky,H.(2004).“Spectralentropy
Hege, M. A., Preissl, H., and Stingl, K. T. (2014). Magnetoencephalographic based feature for robust ASR,” in 2004 IEEE International Conference on
signaturesofrightprefrontalcortexinvolvementinresponseinhibition.Hum. Acoustics, Speech, and Signal Processing, Vol. 1 (Montreal, QC), I–193.
BrainMapp.35,5236–5248.doi:10.1002/hbm.22546 doi:10.1109/ICASSP.2004.1325955
Hsu, C. W., Chang, C. C., and Lin, C. J. (2003). A practical guide to support Mundra,P.A.,andRajapakse,J.C.(2009).SVM-RFEwithMRMRfilterforgene
vectorclassification.Taipei:DepartmentofComputerScience,NationalTaiwan selection.IEEETrans.Nanobiosci.9,31–37.doi:10.1109/TNB.2009.2035284
University,1–16. Nácher, V., Ledberg, A., Deco, G., and Romo, R. (2013). Coherent delta-band
Hsu,M.Y.-T.,andCheng,J.M.-S.(2018).fMRIneuromarketingandconsumer oscillationsbetweencorticalareascorrelatewithdecisionmaking.Proc.Natl.
learningtheory:Word-of-moutheffectivenessafterproductharmcrisis.Eur.J. Acad.Sci.U.S.A.110,15085–15090.doi:10.1073/pnas.1314681110
Mark.52,199–223.doi:10.1108/EJM-12-2016-0866 Nazi,Z.A.,Mashrur,F.R.,Islam,M.A.,andSaha,S.(2021).Fibro-CoSANet:
Hulland,J.,Baumgartner,H.,andSmith,K.M.(2018).Marketingsurveyresearch pulmonaryfibrosisprognosispredictionusingaconvolutionalselfattention
bestpractices:evidenceandrecommendationsfromareviewofJAMSarticles. network.Phys.Med.Biol.66,225013.doi:10.1088/1361-6560/ac36a2
J.Acad.Mark.Sci.46,92–108.doi:10.1007/s11747-017-0532-y Ohira,H.,andHirao,N.(2015).Analysisofskinconductanceresponseduring
Hyvärinen, A., and Oja, E. (2000). Independent component evaluation of preferences for cosmetic products. Front. Psychol. 6, 103.
analysis: algorithms and applications. Neural Netw. 13, 411–430. doi:10.3389/fpsyg.2015.00103
doi:10.1016/S0893-6080(00)00026-5 Oon, H. N., Saidatul, A., and Ibrahim, Z. (2018). “Analysis on non-
Inuso, G., La Foresta, F., Mammone, N., and Morabito, F. C. (2007). “Brain linear features of electroencephalogram (EEG) signal for neuromarketing
activityinvestigationbyEEGprocessing:waveletanalysis,kurtosisandRenyi’s application,” in 2018 International Conference on Computational Approach
entropyforartifactdetection,”in2007InternationalConferenceonInformation in Smart Systems Design and Applications (ICASSDA) (Kuching), 1–8.
Acquisition(Seogwipo),195–200.doi:10.1109/ICIA.2007.4295725 doi:10.1109/ICASSDA.2018.8477618
Islam,M.,Ahmed,T.,Mostafa,S.S.,Yusuf,M.S.U.,andAhmad,M.(2013). Peeters,G.(2004).Alargesetofaudiofeaturesforsounddescription(similarity
“Humanemotionrecognitionusingfrequency&statisticalmeasuresofEEG and classification) in the cuidado project. CUIDADO Ist Project Rep. 54,
signal,”in2013InternationalConferenceonInformatics,ElectronicsandVision 1–25.Availableonlineat:http://recherche.ircam.fr/equipes/analyse-synthese/
(ICIEV)(Dhaka),1–6.doi:10.1109/ICIEV.2013.6572658 peeters/ARTICLES/Peeters_2003_cuidadoaudiofeatures.pdf
Jenke, R., Peer, A., and Buss, M. (2014). Feature extraction and selection for Peirce, J. W. (2007). Psychopy-psychophysics software in python. J. Neurosci.
emotion recognition from EEG. IEEE Trans. Affect. Comput. 5, 327–339. Methods162,8–13.doi:10.1016/j.jneumeth.2006.11.017
doi:10.1109/TAFFC.2014.2339834 Percival,D.B.,andWalden,A.T.(2000).WaveletMethodsforTimeSeriesAnalysis,
Johnston,J.D.(1988).Transformcodingofaudiosignalsusingperceptualnoise Vol.4.Cambridge:CambridgeUniversityPress.doi:10.1017/CBO97805118
criteria.IEEEJ.Select.AreasCommun.6,314–323.doi:10.1109/49.608 41040
Khushaba,R.N.,Wise,C.,Kodagoda,S.,Louviere,J.,Kahn,B.E.,andTownsend, Phanikrishna,V.,andChinara,S.(2021).Automaticclassificationmethodsfor
C.(2013).Consumerneuroscience:assessingthebrainresponsetomarketing detectingdrowsinessusingwaveletpackettransformextractedtime-domain
stimuliusingelectroencephalogram(EEG)andeyetracking.ExpertSyst.Appl. features from single-channel EEG signal. J. Neurosci. Methods 347, 108927.
40,3803–3812.doi:10.1016/j.eswa.2012.12.095 doi:10.1016/j.jneumeth.2020.108927
Krugman,H.E.(1971).Brainwavemeasuresofmediainvolvement.J.Advert.Res. Phinyomark,A.,Phukpattaranont,P.,andLimsakul,C.(2012).Featurereduction
11,3–9. andselectionforEMGsignalclassification.ExpertSyst.Appl.39,7420–7431.
Langleben,D.D.,Loughead,J.W.,Ruparel,K.,Hakun,J.G.,Busch-Winokur, doi:10.1016/j.eswa.2012.01.102
S., Holloway, M. B., et al. (2009). Reduced prefrontal and temporal Rakotomamonjy,A.(2003).VariableselectionusingSVM-basedcriteria.J.Mach.
processingandrecallofhigh”sensationvalue”ads.Neuroimage46,219–225. Learn.Res.3,1357–1370.
doi:10.1016/j.neuroimage.2008.12.062 Ramadan,R.A.,Refat,S.,Elshahed,M.A.,andAli,R.A.(2015).“Basicsofbrain
Levy,I.,Lazzaro,S.C.,Rutledge,R.B.,andGlimcher,P.W.(2011).Choicefrom computerinterface,”inBrain-ComputerInterfaces,edsA.E.HassanienandA.
non-choice:predictingconsumerpreferencesfrombloodoxygenationlevel- T.Aza(Springer),31–50.doi:10.1007/978-3-319-10978-7_2
dependentsignalsobtainedduringpassiveviewing.J.Neurosci.31,118–125. Ramsøy, T. Z., Skov, M., Christensen, M. K., and Stahlhut, C. (2018).
doi:10.1523/JNEUROSCI.3214-10.2011 Frontal brain asymmetry and willingness to pay. Front. Neurosci. 12, 138.
Li,X.,Chen,X.,Yan,Y.,Wei,W.,andWang,Z.J.(2014).ClassificationofEEG doi:10.3389/fnins.2018.00138
signalsusingamultiplekernellearningsupportvectormachine.Sensors14, Rashid, M., Sulaiman, N., Mustafa, M., Khatun, S., and Bari, B. S. (2018).
12784–12802.doi:10.3390/s140712784 “The classification of EEG signal using different machine learning
Luck, S. J. (2014). An Introduction to the Event-Related Potential Technique. techniques for BCI application,” in International Conference on Robot
Cambridge,MA:MITPress. IntelligenceTechnologyandApplications(KualaLumpur:Springer),207–221.
Mamun, K. A., Steele, C. M., and Chau, T. (2015). Swallowing accelerometry doi:10.1007/978-981-13-7780-8_17
signalfeaturevariationswithsensordisplacement.Med.Eng.Phys.37,665–673. Rawnaque, F. S., Rahman, K. M., Anwar, S. F., Vaidyanathan, R., Chau, T.,
doi:10.1016/j.medengphy.2015.04.007 Sarker, F., et al. (2020). Technological advancements and opportunities
Mamun, K. A. E. A. (2011). “Decoding movement and laterality from local in neuromarketing: a systematic review. Brain Inform. 7, 1–19.
field potentials in the subthalamic nucleus,” in 2011 5th International doi:10.1186/s40708-020-00109-x
IEEE/EMBS Conference on Neural Engineering (Cancun), 128–131. Scheirer, E., and Slaney, M. (1997). “Construction and evaluation of a
doi:10.1109/NER.2011.5910505 robustmultifeaturespeech/musicdiscriminator,”in1997IEEEInternational
Mashrur,F.R.,Islam,M.S.,Saha,D.K.,Islam,S.R.,andMoni,M.A.(2021a). Conference on Acoustics, Speech, and Signal Processing, Vol. 2 (Munich),
SCNN:scalogram-basedconvolutionalneuralnetworktodetectobstructive 1331–1334.doi:10.1109/ICASSP.1997.596192
sleepapneausingsingle-leadelectrocardiogramsignals.Comput.Biol.Med. Sharmila, A., and Geethanjali, P. (2018). Effect of filtering with time domain
2021,104532.doi:10.1016/j.compbiomed.2021.104532 featuresforthedetectionofepilepticseizurefromEEGsignals.J.Med.Eng.
Mashrur,F.R.,Miya,M.T.I.,Rawnaque,F.S.,Rahman,K.M.,Vaidyanathan,R., Technol.42,217–227.doi:10.1080/03091902.2018.1464075
Anwar,S.F.,etal.(2021b).“Marketbrain:anEEGbasedintelligentconsumer Telpaz, A., Webb, R., and Levy, D. J. (2015). Using EEG to predict
preferencepredictionsystem,”in202143rdAnnualInternationalConferenceof consumers? future choices. J. Mark. Res. 52, 511–529. doi: 10.1509/jmr.13.
theIEEEEngineeringinMedicine&BiologySociety(EMBC)(Mexico),808–811. 0564
doi:10.1109/EMBC46164.2021.9629841 Teo,J.,Hou,C.L.,andMountstephens,J.(2017).“DeeplearningforEEG-based
Mashrur,F.R.,Roy,A.D.,andSaha,D.K.(2019).“Automaticidentificationof preferenceclassification,”inAIPConferenceProceedings,Vol.1891(Kedah:AIP
arrhythmiafromECGusingalexnetconvolutionalneuralnetwork,”in2019 PublishingLLC.),020141.doi:10.1063/1.5005474
FrontiersinHumanNeuroscience|www.frontiersin.org 12 May2022|Volume16|Article861270

Mashruretal. BCI-BasedConsumers’ChoicePrediction
Tkach,D.,Huang,H.,andKuiken,T.A.(2010).Studyofstabilityoftime-domain Yılmaz, B., Korkmaz, S., Arslan, D. B., Güngör, E., and Asyalı, M. H.
features for electromyographic pattern recognition. J. Neuroeng. Rehabil. 7, (2014).Like/dislikeanalysisusingEEG:determinationofmostdiscriminative
1–13.doi:10.1186/1743-0003-7-21 channels and frequencies. Comput. Methods Prog. Biomed. 113, 705–713.
Toledo-Pérez, D., Rodríguez-Reséndiz, J., and Gómez-Loenzo, R. A. (2020). A doi:10.1016/j.cmpb.2013.11.010
studyofcomputingzerocrossingmethodsandanimprovedproposalforEMG Zainuddin,A.,Mansor,W.,Lee,K.Y.,andMahmoodin,Z.(2018).Performance
signals.IEEEAccess8,8783–8790.doi:10.1109/ACCESS.2020.2964678 of support vector machine in classifying EEG signal of dyslexic children
Tolo¸si, L., and Lengauer, T. (2011). Classification with correlated features: using RBF kernel. Indones. J. Electr. Eng. Comput. Sci. 9, 403–409.
unreliabilityoffeaturerankingandsolutions.Bioinformatics27,1986–1994. doi:10.11591/ijeecs.v9.i2.pp403-409
doi:10.1093/bioinformatics/btr300 Zhang,Y.,Liu,B.,Ji,X.,andHuang,D.(2017).ClassificationofEEGsignalsbased
Tremblay, L., and Schultz, W. (1999). Relative reward preference in primate onautoregressivemodelandwaveletpacketdecomposition.NeuralProcess.
orbitofrontalcortex.Nature398,704–708.doi:10.1038/19525 Lett.45,365–378.doi:10.1007/s11063-016-9530-1
Vecchiato,G.,Astolfi,L.,DeVicoFallani,F.,Cincotti,F.,Mattia,D.,Salinari,
S., et al. (2010). Changes in brain activity during the observation of TV ConflictofInterest:Theauthorsdeclarethattheresearchwasconductedinthe
commercialsbyusingEEG,GSRandHRmeasurements.BrainTopogr.23, absenceofanycommercialorfinancialrelationshipsthatcouldbeconstruedasa
165–179.doi:10.1007/s10548-009-0127-0 potentialconflictofinterest.
Vidyaratne, L. S., and Iftekharuddin, K. M. (2017). Real-time epileptic seizure
detectionusingEEG.IEEETrans.NeuralSyst.Rehabil.Eng.25,2146–2156.
Publisher’sNote:Allclaimsexpressedinthisarticlearesolelythoseoftheauthors
doi:10.1109/TNSRE.2017.2697920
anddonotnecessarilyrepresentthoseoftheiraffiliatedorganizations,orthoseof
Wali,M.K.,Murugappan,M.,andAhmmad,B.(2013).Waveletpackettransform
thepublisher,theeditorsandthereviewers.Anyproductthatmaybeevaluatedin
baseddriverdistractionlevelclassificationusingEEG.Math.Probl.Eng.2013,
297587.doi:10.1155/2013/297587 thisarticle,orclaimthatmaybemadebyitsmanufacturer,isnotguaranteedor
Waris, A., and Kamavuako, E. N. (2018). Effect of threshold values on the endorsedbythepublisher.
combinationofEMGtimedomainfeatures:surfaceversusintramuscularEMG.
Biomed.SignalProcess.Control45,267–273.doi:10.1016/j.bspc.2018.05.036 Copyright © 2022 Mashrur, Rahman, Miya, Vaidyanathan, Anwar, Sarker and
Yadava,M.,Kumar,P.,Saini,R.,Roy,P.P.,andDogra,D.P.(2017).Analysisof Mamun.Thisisanopen-accessarticledistributedunderthetermsoftheCreative
EEGsignalsanditsapplicationtoneuromarketing.Multim.ToolsAppl.76, CommonsAttributionLicense(CCBY).Theuse,distributionorreproductionin
19087–19111.doi:10.1007/s11042-017-4580-6 otherforumsispermitted,providedtheoriginalauthor(s)andthecopyrightowner(s)
Yan,K.,andZhang,D.(2015).Featureselectionandanalysisoncorrelatedgas arecreditedandthattheoriginalpublicationinthisjournaliscited,inaccordance
sensordatawithrecursivefeatureelimination.SensorsActuat.B212,353–363. withacceptedacademicpractice.Nouse,distributionorreproductionispermitted
doi:10.1016/j.snb.2015.02.025 whichdoesnotcomplywiththeseterms.
FrontiersinHumanNeuroscience|www.frontiersin.org 13 May2022|Volume16|Article861270