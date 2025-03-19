# SoMeSci

**CIKM 2021**: [SoMeSci – A 5 Star Open Data Gold Standard Knowledge Graph of Software Mentions in Scientific Articles](https://dl.acm.org/doi/10.1145/3459637.3482017)

[**Website**](https://data.gesis.org/somesci/)

**GitHub**: [`dave-s477/SoMeSci_Code`](https://github.com/dave-s477/SoMeSci_ISWC)

**License**: [CC BY 4.0](https://data.gesis.org/somesci/#License)


## Versioning

The SoMeSci dataset has 3 versions: `0.1`, `0.2`, and `1.1`.
We load SoMeSci 1.1 by default; the `version` kwarg can be passed to override this.


## Schema

### Entity Types

**Application** is a standalone program, designed for end-users.
Using applications usually results in data or project files associated with it, e.g. Excel sheets.
This definition includes web-based applications such as web-services

**Plugin** is an extension to a software that cannot be used individually.
Often, the original application can be concluded from the plugin, e.g. ggplot2 is a well known R package.

**Operating System (OS)** is a special type of software that is used to manage the hardware of a computer and all other software processes running on it.

**Programming Environment (PE)** is an integrated environment that is built around programming languages and is used to design programs or scripts.
This implicitly includes compilers or interpreters.


## Splits

The main dataset does not come with splits.
However, Section 6.1 of the paper describes experiments where the authors split their data into train, development, and test sets in a 60:20:20 ratio.
We take these to be the standard splits of the dataset.
We re-run the authors' [splitting code](https://github.com/dave-s477/SoMeNLP/blob/master/bin/split_data) with the same random seed to reproduce their splits.


## Errata

1. The `Abbreviation_of` relation type lists `abbreviation` instead of `Abbreviation` (note the case) as an argument type.
