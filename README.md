# An aligned subset of the Parallel Universal Dependencies

This repository contains word-alignment annotations for several language pairs with PUD corpora.
At the moment, English–French, English–Russian, English–Chinese, English–Japanese, and
English–Korean are available. The analysis of the morphosyntactic divergences in these 
language pairs was reported in

...

We also provide the copies of the original PUD .conllu files used for the annotation. At the moment,
they are identical to the ones provided in [the parent repo](https://github.com/UniversalDependencies),
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

Keys are id’s of the nodes in the original UD tree corresponding to content words (see AlignmentManual.md for the 
discussion of the distinction between content and function words) or to function words that are in a many-to-one
relationship with a target-side content word. Many-to-one relationships are reflected as cases where several source-side
keys map to the same one-element list (`"7": ["3"], "12": ["3"]`). One to many relationships are represented by a key,
value pair with several id’s in the value list (`"9": ["9", "10"]`). `"X"` represents unaligned content words
on the source side (`"33": ["X"], "3": ["X"]`) or the target side (`"X": ["34", "5", "6"]`).
