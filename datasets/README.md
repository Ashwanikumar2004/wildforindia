# Model and evaluation data

## Pretrained model

WildFIndia uses Google's SpeciesNet package and its pretrained camera-trap
model. The package downloads the model files when inference is initialized;
they are cached outside this repository. The current default is
`kaggle:google/speciesnet/pyTorch/v4.0.3a/1`.

SpeciesNet was trained on a geographically diverse collection of more than 65
million camera-trap images and predicts wildlife, broader animal groups, and
non-animal labels. The Python package is Apache 2.0 licensed. Model-weight
terms are described in the model card/source linked by the official project;
review them separately before redistribution. See the [official SpeciesNet
repository](https://github.com/google/cameratrapai) for current install
instructions, model source, terms, and the recommended scientific citation.
Cite the paper listed there in any university report that uses this model.

## Why the training dataset is not copied here

The model is already trained, so inference does not require downloading its
training photos. The training collection is far too large for this Django
repository. Its source images also have different owners and reuse licenses;
being publicly viewable does not automatically allow republishing them in a
GitHub repository.

## Evaluation dataset guidance

Before making accuracy claims, collect a small, separate evaluation set of
images with verified species labels. Keep training images and evaluation images
separate. Record at least the source URL, species label, verification source,
license, and attribution for every image. Only commit an image if its license
allows redistribution in this project; otherwise keep it locally and share the
source link and evaluation result only. Include negative examples (no animal,
people, vehicles, and non-Indian wildlife) so the model is checked against
common mistakes. Never treat an AI prediction as ground truth.

The iNaturalist observation-image download guidance explains how to select
licensed images and why licenses need to be checked per image:
[download licensed observation images](https://help.inaturalist.org/en/support/solutions/articles/151000223300-how-i-download-inaturalist-photos-to-use-for-research-).
This is a source for building a carefully licensed test set, not a ready-made
SpeciesNet dataset to bundle here.
