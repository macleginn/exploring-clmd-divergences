## General principles

<ol>
<li>Align only content words (cf. the definition below).</li>
<li>When encountering duplicated technical nodes (with dots in the ID: check the UD parse in 
the respective cell above), do not align them or marked them as unaligned. E.g., in sentence 
25 there is a duplicate of the verb “started”, used to analyse ellipsis in the second part of the sentence. 
Align only the first copy.</li>
<li>Align ‘translation equivalents’ (words denoting the same stuff); differences in POS tags do not matter.</li>
<li>When needed, align content words with phrases (possibly discontiguous as with phrasal verbs) and phrases 
with phrases (when at least one of them is unanalyseable or a fixed expression). Examples:
<ol type="a">
<li>Part of a word in one language corresponds to a separate word in another language: <em><b>un</b>precedented</em> vs.
<em><b>sans</b> précédent</em>.</li>
<li>Phrasal verbs: <em>give <b>up</b></em> vs. <em>abandonner</em>.</li>
<li>Pseudoreflexives: <em>complain</em> vs. <em>se plaindre</em>.</li>
<li>Fixed expressions: <em>substandard</em> vs. <em>de qualité inférieure</em>.</li>
<li>Differently grammaticalised linkers: <em>in addition</em> vs. <em>en outre</em>.</li>
</ol>
NB: when aligning UD-unanalyseable expressions (such as <em>en outre</em>) or fixed expressions, align the head
and do not align the dependants (e.g., in <em>en outre</em> vs. <em>in addition</em>, align <em>en</em> with 
<em>addition</em> and leave it at that; the same with <em>either way</em> vs. Russian <em>так или иначе</em> 
‘thus or otherwise’: <em>way</em>→<em>так</em>). 
Otherwise use one-to-many alignment.
</li>
<li>Align semantic equivalents even if their environments do not match. E.g., given a pair of phrases 
<em>helped himself to some cheese</em> and <em>put some cheese on his plate</em>, align <em>some cheese</em>
and <em>his</em> with <em>himself</em>. Mark <em>helped</em>, <em>put</em>, and <em>plate</em> 
as unaligned content words.</li>
<li>Align pronouns and pronominal/adverbial units with spatiotemporal semantics with their explicit counterparts. 
E.g., in <em>he bought this car last year in Detroit</em> vs. <em>he bought it there last year</em>,
align <em>this car</em> with <em>it</em> and <em>Detroit</em> with <em>there</em>.</li>
</ol>

## Content words vs. function words

Function words are of the following types:

* Grammatical-relation markers (prepositions marking direct/indirect objects, construct-state markers, 
prepositions marking possession and other types of relations inside NPs).
* Tense-aspect-mood markers including inflected auxiliaries.
* Markers of definiteness/indefiniteness.
* Complementisers (aka subordinate conjunctions/dependent clause markers: _I know **that** he’s lying_);
comparative particles (_A is better **than** B_).
* Markers of grammaticalised evidentiality.
* Classifiers.
* Topic/focus particles.
* Copulas and existential predicates.
* Dummy subjects (_**It** rains_, _**It** annoys me that you ask too many questions_).
* Expletives (_**There** are rats in the barn_).
* Coordinate conjunctions (_and_, _or_).

Content words:

* All other types of predicates, participants, obliques, adverbial and adjectival modifiers.
* Negation marking.
* Discourse markers.
* Quantifiers.
* Spatial/temporal-relations markers (_**on** the table_, _two blocks **away** from the flat_, _**on** that day_). 
Take care to distinguish them from case, either inside NPs (_two blocks away **from** the flat_) 
or assigned by verbs (_he works **at** the university_). Spatiotemporal markers can be replaced with other
markers, changing the meaning of the phrase (_**under** the table_, _**after** that day_).
