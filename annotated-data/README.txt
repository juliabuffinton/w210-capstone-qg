## Annotation data of Sugawara et al. (2017) ``Evaluation Metrics for Machine Reading Comprehension: Prerequisite Skills and Readability''

* paper
  - http://aclweb.org/anthology/P/P17/P17-1075.pdf

## json format

* Skill number
  - 0-12: skills (See the annotation guideline)
  - 13: no skill
* sents_indices
  - Indices of sentences that are required for answering a question.
  - Each value represents an index of list of string(context).split() in python.
* skill_count
  - Number of required skills
* id
  - Numbering in annotation
* original_id
  - Identifier in datasets
