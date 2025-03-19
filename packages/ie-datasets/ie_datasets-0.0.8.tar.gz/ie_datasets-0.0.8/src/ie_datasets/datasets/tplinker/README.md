# TPLinker

For better or worse (definitely worse), the preprocessed variations of NYT and WebNLG found in the [TPLinker project](https://github.com/131250208/TPlinker-joint-extraction#data) have become the de facto versions of those datasets used in relation extraction research.
They are typically used for supervised learning despite NYT originally being a distant supervision dataset.
Moreover, WebNLG lacks offical text span annotations, but they are added in TPLinker's data preprocessing steps.


## TPLinker-WebNLG

The dataset we call TPLinker-WebNLG, simply referred to as "WebNLG" in modern relation extraction literature, ultimately derives from the English half of [WebNLG 3.0](https://gitlab.com/shimorina/webnlg-dataset/-/tree/master/release_v3.0), created for the [WebNLG Challenge 2020](https://synalp.gitlabpages.inria.fr/webnlg-challenge/challenge_2020/).

For their work, the authors of [CopyRE](https://aclanthology.org/P18-1047/) take the train set of WebNLG 3.0 and split it into the train and development sets of "WebNLG", while the labelled development set became the test set.

The authors of TPLinker convert this data into a readable JSON format.
