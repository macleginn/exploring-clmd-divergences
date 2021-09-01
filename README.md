# An aligned subset of the Parallel Universal Dependencies

This repository contains word-alignment annotations for several language pairs
with PUD corpora.  At the moment, English–French, English–Russian,
English–Chinese, English–Japanese, English–Korean, and English-Arabic are available. The
analysis of the morphosyntactic divergences in these language pairs was reported
in

```bibtex
@inproceedings{nikolaevetal2020clmd,
	title="Fine-Grained Analysis of Cross-Linguistic Syntactic Divergences",
	author="Nikolaev, Dmitry and Arviv, Ofir and Karidi, Taelin and Kenneth, Neta and Mitnik, Veronika and Saeboe, Lilja Maria and Abend, Omri",
	booktitle="Proceedings of the 2020 {C}onference of the {A}ssociation for {C}omputational {L}inguistics",
	year="2020",
	pages="1159–1176"
}	
```

Please cite this paper if you use the data in your work. If you use the English-Arabic alignments, please also cite

```bibtex
@misc{rafaeli2021speech,
      title={Part of Speech and Universal Dependency effects on English Arabic Machine Translation}, 
      author={Ofek Rafaeli and Omri Abend and Leshem Choshen and Dmitry Nikolaev},
      year={2021},
      eprint={2106.00745},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```

Alignments are stored in the `alignments` directory in subdirectories
corresponding to PUD corpora. Each subdirectory contains three files:

* `en.conllu`: the original CoNLL-U records from the English PUD corpus.
* `target.conllu`: CoNLL-U records from the target corpus.
* `alignment.json`: the alignments.

.conllu files only contain records for which alignments are available (999
sentences for En–Fr, 995 sentences for En–Ru, 999 sentences for En–Jp, 999
sentences for En–Zh, and 884 sentences for En–Ko). At the moment, the records
are identical to the ones provided in [the parent repo](https://github.com/UniversalDependencies),
but differences may accrue over time.

## Data format

Alignments are stored as JSON files with lists of objects of the following form:

```json
{
  "7": ["3"],
  "6": ["4"],
  "9": ["9", "10"],
  "X": ["34", "5", "6", "19", "29", "17"], 
  "33": ["X"], 
  "3": ["X"]
}
```

Keys are id’s of the nodes in the original UD tree corresponding to content
words (see `AlignmentManual.md` for the discussion of the distinction between
content and function words) or to function words that are in a many-to-one
relationship with a target-side content word. Many-to-one relationships are
reflected as cases where several source-side keys map to the same one-element
list (`"7": ["3"], "12": ["3"]`). One to many relationships are represented by a
key, value pair with several id’s in the value list (`"9": ["9", "10"]`). `"X"`
represents unaligned content words on the source side (`"33": ["X"], "3":
["X"]`) or the target side (`"X": ["34", "5", "6"]`). Many-to-many relationships
are prohibited by the annotation manual. In case of aligned multiword
expressions where no connections can be established between individual words,
the headwords were aligned.
