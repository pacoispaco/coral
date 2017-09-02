# Some notes on software for biological taxonomy

*We have many names for the things we love* - Swedish proverb

All my interest in experimenting with software for biological names and
taxonomies began with my birding passion. That may be reflected in these
notes!

## The challenge

There are two well established sets of rules and recommendations for naming
organisms and plants; [**ICZN** (International Code of Zoological Nomenclature)](http://www.iczn.org)
and [**ICN** (International Code of Nomenclature for algae, fungi, and plants)](http://www.iapt-taxon.org/nomen/main.php).
These codes only describe the naming of organisms and plats, not *how* they then
should be classified into taxonomies.

The basics for everything regarding scientific names goes back to Carl Linnaeus
system of naming system and classification, although his morphological
principles for classification have been replaced by more modern principles
based on evolution and genetics.

The questions of what constitues a species and what principles and criteria
are to be applied in establishing the relationships between different species,
and thus how to establish taxonomies, are complex and not entirely answered
today. The question of *what* a species actually is is often refered to as the
*species concept* question, and the answer to that question differs between
biologists working with different organisms, since the *species concept* is
tightly coupled to the mechanisms by which different organisms reproduce
themselves. The principles that should be used for establishing relationships
between species and, thus how taxonomies should be constructed, are today
based on the view that a taxonomy should reflect the evolutionary history of
the species in the taxonomy.

From a purely practical perspective, biologists working with these questions are
also challenged with the practical problems of changing names and continuously
revised taxonomies due to new research and insights. A given species may be
given a new name and a new position in a taxonomy after research shows it to be
related to a different group of species than previously thought. This leads to
difficulties when searching for older publications of this species. Also,
different biologist may have differing opinions on what name and what taxonomy
is the correct one, which means that different taxonomies may be seen as correct
by different groups of biologists.

All animals and plats that have had importance to humans have been given names,
probably since the invention of language. Some animals and plants are of great
importance in agriculture, husbandry and fishing as well as being of great
interest to amateurs and hobbyists, so that there also exist many popular names
and taxonomies in different languages. In many languages the same animal or
plant can also have many names. So these names and and taxonomies suffer from
similar problems and challenges as the scientific names and taxonomiesi do.

All this adds upp to a rather interesting challenge for programmers trying to
manage and represent this information in software systems!

## A few words on taxonomic nomenclature

*Taxonomy* refers both to the science of description, identification, naming and
classification of organisms, and to actual concrete instances of classification.
Sometimes the latter is also called a *classification*.

Organisms are grouped into *taxa* (singular *taxon*) and aranged in hierachical
tree structures. The level of a taxon in a specific taxonomy is called its
*taxonomic rank*.

## Let's start with birds!

I like birds, so let's start there!

Today there is an estimated 11.000 different species of birds. Birds are a group
of organisms that is fairly well researched and also for which there is a lot of
active research going on. There has been a lot of renaming and reclassification
the last 40 years and it is still going on. There are also differing opinions
on a number of species and groups of species regarding both their species status
as well as their classification. That means that there today exists a number of
different taxonomies for birds, even though they mostly differ in details.

Today, most scientific classifications and taxonomies for birds are based on
Sibley and Monroes classification presented in *Phylogeny and Classification
of Birds* (1990). But there exist differing opinions on many species of birds,
whether they should be split into other species or not, or classifed under
other genus.

A decent software system for bird names should be able to:

 * Handle current scientific names
 * Handle current but multiple taxonomies
 * Handle relationships between taxa in different taxonomies
 * Handle different popular names
 * Possibly handle older scientific names and taxonomies

### Sources of information on bird names and taxonomies

Many countries' national ornithological associations have maintained name lists
which have listed the official names of all birds that can be seen in given
country. These lists are based on some scientifically accepted classification of
bird species. But the classification used in one country can differ from that
in another country. Even if two countries base their official list on the same
classification, there may exist differences in how the two list handles some
species. A species with two subspecies in one list may be considered two
different species in another list.

For amateur ornothologists who want to keep track of which birds they've seen and
who travel a lot, the current situation with names and name lists can be confusing!

The main sources used in *Twitchspot taxonomy* are:

 * [IOC World Bird List](http://www.worldbirdnames.org/ioc-lists/master-list-2/)
 * [Birdlife Sweden](http://birdlife.se/tk/svenska-namn-pa-varldens-faglar/)
 * [Zoonomen](http://www.zoonomen.net/avtax/frame.html)

## References

Here are some references to books I've read. Of course, the number of articles,
both published and bloglike articles I've read, are to many to list (or remember)
here!

 * [*Biological Systematics - Principles and Applications*, Randall T. Schuch, 2000]()
 * [*Describing Species*, Judith E. Winston, 1999]()
 * [*Species - A History of the Idea*, John S. Wilkins, 2009]()
