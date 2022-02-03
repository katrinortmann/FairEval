# FairEval

The traditional evaluation of labeled spans with precision, recall, and F1-score leads to double penalties for close-to-correct annotations. As Manning (2006) argues in an article about named entity recognition, this can lead to undesirable effects when systems are optimized for these traditional metrics.

Building on his ideas, in Ortmann (forthcoming), I developed a new evaluation method that more accurately reflects true annotation quality by ensuring that every error is counted only once. In addition to the traditional categories of true positives (`TP`), false positives (`FP`), and false negatives (`FN`), the new method takes into account the more fine-grained error types suggested by Manning: labeling errors (`LE`), boundary errors (`BE`), and labeling-boundary errors (`LBE`). 

In addition, I also distinguish between different types of boundary errors, which enable an even more detailed error analysis:

- `BES`: the system's annotation is smaller than the target span
- `BEL`: the system's annotation is larger than the target span
- `BEO`: the system span overlaps with the target span

This repository contains a Python implementation of the suggested algorithm to identify the new error types in flat and hierarchical spans. The program `FairEval.py` is located in the `/src` folder and can be used as a stand-alone tool (see [here](#stand-alone-version)) or be imported as a python module (see [here](#import-as-module)). 

In the `/data` folder, I also provide the example [data sets](#example-data) from my paper with system and target annotations of named entities, chunks, and topological fields in a custom [input format](#input). The [config files](#configuration) that I used for the exemplary evaluation are located in the `/config` folder. The [result files](#output) can be found in the `/eval` folder.   

For more details on the additional error types, the new algorithm and the example evaluation, please refer to my [paper]().

## Usage

The application of this FairEval implementation requires [Python 3](https://www.python.org/downloads/).

### Stand-alone version

To use FairEval as a stand-alone version to evaluate your annotations, call it via the command line:

> py FairEval.py --config file.config

The config argument specifies a configuration file with the required parameters. For more information on the config file, see the [section on configuration](#configuration).

When called as described above, the tool will import your [target and system data](#input) and carry out the evaluation according to the [specified options](#configuration). The results will be written to an [output file](#output) or the command line.

### Import as module

If you want to integrate and use FairEval in your own code, you can import it as a python module with

> import FairEval

Suggested applications include:

1. Counting the different fine-grained error types in your data for a detailed error analysis
2. Determine the type of overlap for a (labeling-)boundary error
3. Calculate fair or customized precision, recall, and F1 scores on your error counts
4. Get simple statistics about your data: how often do certain labels occur in the data set

#### Determine fine-grained error types

To count the different fine-grained error types in your data set, according to the algorithm described in Ortmann (forthcoming), you can use the function `compare_spans(target_spans, system_spans, focus)`. The `focus` argument is optional and can be set to "system" or "target" (default), depending on which label should be counted in the case of labeling and labeling-boundary errors.

The function expects a list of target spans and system spans. Each span is a 4-tuple of 
- label: the span type as string
- begin: the index of first token; equals end for spans of length 1
- end: the index of the last token; equals begin for spans of length 1
- tokens: a set of token indices included in the span (this allows the correct evaluation of partially and multiply overlapping spans; you can also use it to exclude punctutation inside of spans from the evaluation)

To allow for changes of the token set, the span tuple is actually implemented as a list, e.g.,

```
[["NP", 1, 3, {1, 2, 3}], ["PP", 5, 10, {5, 6, 7, 8, 9, 10}], ...]
```

The function first performs traditional evaluation on these spans to identify true positives, false positives, and false negatives.
Then, the additional error types for fair evaluation are determined, following steps 1 to 4:
1. Count 1:1 mappings (TP, LE)
2. Count boundary errors (BE = BES + BEL + BEO)
3. Count labeling-boundary errors (LBE)
4. Count 1:0 and 0:1 mappings (FN, FP)    

The function outputs a dictionary containing
- the counts of TP, FP, and FN according to traditional evaluation (per label and overall)
- the counts of TP, FP, LE, BE, BES, BEL, BEO, and FN (per label and overall; BE = BES + BEL + BEO)
- a confusion matrix 

The dictionary has the following structure:

```
{"overall" : {"traditional" : {"TP" : count, "FP" : count, "FN" : count},
              "fair" :        {"TP" : count, "FP" : count, "FN" : count,
                               "additionalErrorType1" : count, "additionalErrorType2" : count, ...}
             },
 "per_label" : {"traditional" : {"label1" : {"TP" : count, "FP" : count, "FN" : count},
                                 "label2" : ... },
                "fair" :        {"label1" : {"TP" : count, "FP" : count, "FN" : count,
                                             "additionalErrorType1" : count, "additionalErrorType2" : count, ...},
                                 "label2" : ... } 
               },
 "conf" : { see below }
}
```

The confusion matrix is implemented as a dictionary with the following structure:

```
{target_label1 : {system_label1 : count,
                  system_label2 : count,
                  ...},
 target_label2 : ... }
 
with an underscore '_' representing an empty label (FN/FP)
```

#### Determine span overlap type

If you want to know, if and how two spans overlap, you can use the function `overlap_type(span1, span2)`. As input, it expects two tuples of integers `(beginSpan1, endSpan1)` and `(beginSpan2, endSpan2)`, where begin and end are the indices of the corresponding tokens. For spans of length one, begin equals end.

The function checks, if and how span1 and span2 overlap. The first span serves as the basis against which the second span is evaluated.

```
span1 ---XXXX---
span2 ---XXXX--- TP (identical)
span2 ----XXXX-- BEO (overlap)
span2 --XXXX---- BEO (overlap)
span2 ----XX---- BES (smaller)
span2 ---XX----- BES (smaller)
span2 --XXXXXX-- BEL (larger)
span2 --XXXXX--- BEL (larger)
span2 -X-------- False (no overlap)
```

Possible output values are either one of the following strings
- "TP" = span1 and span2 are identical, i.e., actually no error here
- "BES" = span2 is shorter and contained within span1 (with at most one identical boundary)
- "BEL" = span2 is longer and contains span1 (with at most one identical boundary)
- "BEO" = span1 and span2 overlap with no identical boundary
- or False if span1 and span2 do not overlap.   

#### Calculate fair or customized scores

precision(eval_dict, version, weights)
recall(eval_dict, version, weights)
fscore(eval_dict)

#### Get simple data statistics

By calling the function `annotation_stats(span_list, result_dict)` with your list of (target) spans, you can get an overview of the distribution of labels in your data. The function expects a list of target spans with each span being a 4-tuple `(label, begin, end, tokens)`. It counts the frequency of labels in the list and stores the result in the dictionary under the key `data_stats`.

For the NER target data, the result would look like this:

```
{ 'data_stats' : { 'OTH' : 778,
                   'PER' : 1694,
                   'ORG' : 1330,
                   'LOC' : 2376 } }
```

## Configuration

## Input 

## Output

## Example data

In my study, I run an example evaluation on three different types of spans: named entities, chunks, and topological fields. The `/data` folder contains the target (i.e., gold standard) annotation and the system annotation. For license and copyright reasons, the data is provided in a custom format that only contains the span annotations and does not allow for the reconstruction of the original corpus data.

  Annotation       | Evaluation data set
:-----------------:|:---------------------------------------
   NER   | The NER data set corresponds to the test section of the GermEval 2014 data set (Benikova et al. 2014). Only top-level entities from the four main classes are included.
  Chunks   | The chunk annotations are taken from 10% of the chunked TüBa-D/Z corpus (Telljohann et al. 2017)
Topological fields | The topological field annotations are taken from 10% of the TüBa-D/Z treebank (Telljohann et al. 2017)

More details about training and evaluation data sets and the NLP tools used for the annotation can be found in my paper.

## Acknowledgement

If you use FairEval in your work, please cite the corresponding paper:

- Ortmann, Katrin. Forthcoming. *Fine-Grained Error Analysis and Fair Evaluation of Labeled Spans*.

## References

Benikova, D., Biemann, C., Kisselew, M., and Padó, S. 2014. *Germeval 2014 named entity recognition shared task: Companion paper*.

Manning, C. 2006. *Doing Named Entity Recognition? Don’t optimize for F1*. Retreived from https://nlpers.blogspot.com/2006/08/doing-named-entity-recognition-dont.html.

Ortmann, K. Forthcoming. *Fine-Grained Error Analysis and Fair Evaluation of Labeled Spans*.

Telljohann, H., Hinrichs, E. W., Kübler, S., Zinsmeister, H., and Beck, K. 2017. *Stylebook for the Tübingen Treebank of Written German (TüBa-D/Z)*. Seminar für Sprachwissenschaft, Universität Tübingen, Germany.
