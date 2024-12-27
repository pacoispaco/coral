# Data structures for taxonomies

## The modern use of taxonomies and name lists

The orginal purpose of classification was simply to describe, name and classify all living organisms, partly as a celebration of gods creation and partly in order for biologists to be able to communicate about animals and plants in a unambigous way. With the breakthrough of the discovery of evolution and the desire to understand evolutionary processes and mechanisms, there was a big shift from the idea of taxonomies simply beeing a classification to bring order, to an idea of using taxonomies to also describe the evolutionary history of organisms. The purpose of names is still to be able to communicate and uniquely identify organisms, but names should also convey the evolutionary position of taxa in the great and continously ongoing process of evolution.

Amateur naturalists, like birders, want to know which names to use when reporting and keeping track of what they've seen and observed.

These two purpuses, that of the scientific community and that of amateur naturalists, have started to overlapse with the advent of software and online systems for amateurs to reporting sightings, which then can be used by scientists and in environmental research in order to identify possible changes in population trends for different species. These software systems are important tools in enabling what is today called **[crowd science or citizen science](https://en.wikipedia.org/wiki/Citizen_science)**. It is today more important than ever, to be able to know what species and subspecies we are talking about!

## Taxonomies as information structures

A taxonomy can be represented as a *tree*. Relationships between taxa in different taxonomies can be represented by *directed graphs* between related taxa.

### Trees and graphs

A *tree* **T** is a finite set of one or more *nodes* such that (recursively):

 1. there is one special node called the *root* of the tree.
 1. the remaining nodes are partitioned into m disjoint sets **T1**, **T2**, **...**, **Tm**, and each of these sets in turn is also a tree. These trees are called *subtrees*.

A *directed graph* is a set of *vertices* connected by *edges* where edges have a *direction* associated with them.

### Representing taxonomies as trees and taxonomic relationships as graphs

When representing a taxonomy as a tree we will refer to nodes as taxa, and we would like to assign a few attributes to each taxon as follows.

 1. every taxon is assigned a *taxonomic rank*.
 1. every taxon is assigned a *taxonomic name*, *author* and publication date in accordance with the ICZN or ICN rules and which is unique within the taxonomy.
 1. every taxon is assigned a *taxonomic concept*.
 1. every taxon that has the rank of *Species* or *Subspecies* is assigned a set of *type specimens*.

When representing relationships between taxa in different taxonomies we would like to tag the edges with a name describing the relationship, as follows.

 1. A taxon **t1** in the taxonomy **T1** which has the same taxonomic concept **c1** as the taxon **t2** in the taxonomy **T2**, will have a bidirectional edge with the tag *synonym*, even when the names of **t1** and **t2** may differ.
 1. A taxon **t1** in the taxonomy **T1** and a taxon **t2** in the taxonomy **T2** that have different taxonomic concepts but share the same name will have a bidirectional edge with the tag *homonym*.

In particular, when having more that two taxonomies we would like to assign yet two other attributes to each taxon, as follows.

 1. every taxon is assigned a set of edges labled *synonyms* containing edges to taxa in other taxonomies that it is synonymous to.
 1. every taxon is assigned a set of edges labled *homonyms* containing edges to taxa in other taxonomies that it is homonymous to.

### A data representation for taxonomies

There are many ways to represent trees and graphs in different programming languages and data formats. There are even many different ways to represent trees and graphs in any given programming language or data format. Which representation we choose should be guided by two basic considerations; ease of comprehension and suitability for the most important operations we may wish to perform on the taxonomies.

The most important operations we are considering here are:

 * Fast lookup on scientific name and support for auto-complete search.
 * Fast lookup on common names and support for auto-complete search.
 * Fast listing of taxa in taxonomical order.
 * Fast access to supertaxa and subtaxa of a given taxon.
 * Fast access to synonyms and homonyms of a given taxon.

Here I will use [JSON](http://json.org) which is a simple and widely used data format that supports representing hierarchical structures as well as lists. I will first present the data structure by example instead of by specification. In the examples I will use the taxonomic group of subalpine warblers as classified by the Swedish Taxonomic Committee previously discussed.

This is a possible JSON representation of *Sylvia cantillans* based on its classification in the **[Bird List of the Taxonomic Committee of Birdlife Sweden](http://birdlife.se/tk/svenska-namn-pa-varldens-faglar/)** and complemented with some additional information:

```JSON
{
 "binomial_name": "Sylvia cantillans",
 "name": "cantillans",
 "authority": "(Pallas, 1764)",
 "rank": "Species",
 "taxonomy": "TC BS v6",
 "extra": {},
 "distribution": {},
 "concept_references": [{
                         "title": "A taxonomic revision of the Subalpine Warbler by Lars Svensson, 2013",
                         "url": "http://boc-online.org/bulletins/downloads/BBOC1333-Svensson.pdf"
                        }],
 "type_specimens": [{
                     "sort": "neotype",
                     "description": "First-summer male collected on 23 May 1906 at Ficuzza, north-west Sicily",
                     "location": "Natural History Museum, Tring, BMNH 1909.11.18.50",
                     "url": null
                    }],
 "supertaxon": "Sylvia",
 "subtaxa": ["Sylvia cantillans cantillans", "Sylvia cantillans albistriata"],
 "homonyms": [{
               "taxonomy": "IOC 7.3",
               "name": "Sylvia cantillans"
              }],
 "synonyms": [],
 "common_names": {
                  "en": "Subalpine warbler",
                  "sv": "Rödstrupig sångare"
                 }
}
```

It could be argued that the information on common names should be moved to a separate data structure where common names would be indexed by scientific name for fast lookup.

The above JSON data representation could be stored as a separate file with the same name as the taxon; "sylvia\_cantillans.json". Doing the same with the other taxa in this taxonomy we would have the following JSON files:

```bash
sylvia_cantillans.json
sylvia_cantillans_cantillans.json
sylvia_cantillans_albistriata.json
sylvia_inornata.json
sylvia_inornata_inornata.json
sylvia_inornata_iberiae.json
sylvia_subalpina.json
```

This is a possible JSON representation of *Sylvia cantillans* based on its classification in the **[IOC World Bird List (v 7.3) by Gill, F & D Donsker (Eds)](http://www.worldbirdnames.org/ioc-lists/master-list-2/)** and complemented with some additional information:


```JSON
{
 "binomial_name": "Sylvia cantillans",
 "name": "cantillans",
 "authority": "(Pallas, 1764)",
 "rank": "Species",
 "taxonomy": "IOC 7.3",
 "extra": {
           "comment": null,
           "code": null
          },
 "distribution": {
                  "breeding": "EU",
                  "breeding_subrange": "sw",
                  "non_breeding": "n AF",
                  "spring_migration": null,
                  "autumn_migration": null,
                  "extinct": false
                 },
 "concept_references": [],
 "type_specimens": [],
 "supertaxon": "Sylvia",
 "subtaxa": ["Sylvia cantillans cantillans", "Sylvia cantillans albistriata"],
 "homonyms": [{
               "taxonomy": "TC BS v6",
               "name": "Sylvia cantillans"
              }],
 "synonyms": [{
               "taxonomy": "HM 4th ed",
               "name": "Curruca cantillans"
              }],
 "common_names": {
                  "en": "Subalpine warbler",
                  "sv": "Rödstrupig sångare"
                 }
}
```

These JSON files could then be indexed by scientific name as well as by common names, for fast retrieval and it would also be fast to browse the hirarchical structure under or below a given taxon since we have a direct mapping of subtaxa and supertaxon names to file names. Of course, we could also store the JSON-data in a key-value store or document database and preferably have all the data in RAM for fast access.

### Reading and parsing source data files with taxonomic data

For taxonomies and taxa lists for birds the most common data formats are Excel, CSV and XML. Reading and parsing these formats in order to construct a data representation of them as described above presents a number of challenges due to implicit assumptions made in many of the available data sources.
