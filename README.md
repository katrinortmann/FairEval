# FairEval

The traditional evaluation of labeled spans with precision, recall, and F1-score leads to double penalties for close-to-correct annotations. As Manning (2006) argues in an article about named entity recognition, this can lead to undesirable effects when systems are optimized for these traditional metrics. Building on his ideas, in Ortmann (forthcoming), I developed a new evaluation method that more accurately reflects true annotation quality by ensuring that every error is counted only once. In addition to the traditional categories of true positives (`TP`), false positives (`FP`), and false negatives (`FN`), the new method takes into account the more fine-grained error types suggested by Manning: labeling errors (`LE`), boundary errors (`BE`), and labeling-boundary errors (`LBE`). 

In addition, I also distinguish between different types of boundary errors, which enable an even more detailed error analysis:

- `BES`: the system's annotation is smaller than the target span
- `BEL`: the system's annotation is larger than the target span
- `BEO`: the system span overlaps with the target span

This repository contains a Python implementation of the suggested algorithm to identify the new error types in flat and hierarchical spans. The program `FairEval.py` is located in the `/src` folder and can be used as a stand-alone tool (see [here](#stand-alone-version)) or be imported as a python module (see [here](#import-as-module)). 

In the `/data` folder, I also provide the example [data sets](#example-data) from my paper with system and target annotations of named entities, chunks, and topological fields in a custom [input format](#input). The [config files](#configuration) that I used for the exemplary evaluation are located in the `/config` folder. The [result files](#output) can be found in the `/eval` folder.   

For more details on the additional error types, the new algorithm and the example evaluation, please refer to my [paper]().

## Usage

### Stand-alone version

### Import as module

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
