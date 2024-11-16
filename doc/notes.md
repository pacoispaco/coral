# Some notes on software for biological taxonomy

*We have many names for the things we love* - Swedish proverb

All my interest in experimenting with software for biological names and
taxonomies began with my birding passion. That may be reflected in these
notes!

## The basics of taxonomy

*Taxonomy (from Ancient Greek τάξις (taxis), meaning 'arrangement', and -νομία
(-nomia), meaning 'method') is the science of defining and naming groups of
biological organisms on the basis of shared characteristics. Organisms are
grouped together into **taxa** (singular: **taxon**) and these groups are given
a **taxonomic rank**; groups of a given rank can be aggregated to form a super
group of higher rank, thus creating a taxonomic hierarchy. The principal ranks
in modern use are kingdom, phylum, class, order, family, genus and species. The
Swedish botanist Carl Linnaeus is regarded as the father of taxonomy, as he
developed a system known as Linnaean taxonomy for categorization of organisms
and binomial nomenclature for naming organisms.*

*With the advent of such fields of study as phylogenetics, cladistics, and
systematics, the Linnaean system has progressed to a system of modern biological
classification based on the evolutionary relationships between organisms, both
living and extinct.* - [Introduction to the Wikipedia article on Taxonomy](https://en.wikipedia.org/wiki/Taxonomy_(biology))

There are two well established sets of rules and recommendations for how taxa
should be named, one for animals; [**ICZN** (International Code of Zoological Nomenclature)](http://www.iczn.org)
and one for plants; [**ICN** (International Code of Nomenclature for algae, fungi, and plants)](http://www.iapt-taxon.org/nomen/main.php).
These codes only describe nomenclatural och formal rules for how names should
be constructed and arranged in taxonomies, not the scientific and biological
pinciples for deciding how taxa should be arranged in taxonomies.

## The purpose of the Twitchspot taxonomy system

The main purpose of the system is to provide a number of read-only API services
for searching for and looking up scientific and vernacular names in different
languages of animals and plants, based on source data from authoratative
sources.

To begin with the system will handle bird names and taxonomies. Eventually I'll
try other living animals, as well as plants.

Today there is an estimated 11.000 different species of birds. If taxa for
subspecies and higher taxa are inlcuded the total number of taxa is around
35.000.

Birds are a group of organisms that is fairly well researched and also for
which there is a lot of active research going on. There has been a lot of
renaming and reclassification the last 40 years and it is still going on. There
are also differing opinions in the scientific community on a number of species
and groups of species regarding both their species status as well as their
classification. That means that there today exists a number of different
taxonomies for birds, even though they mostly differ in details.

Today, most scientific classifications and taxonomies for birds are based on
Sibley and Monroes classification presented in *Phylogeny and Classification
of Birds* (1990).

The system for bird names should be able to:

 * Handle current scientific names
 * Handle current but multiple taxonomies
 * Handle different popular names in different languages
 * Possibly relationships between taxa in different taxonomies
 * Possibly handle older scientific names and taxonomies

## Some challenges

 * There is very little structured on data historical scientific names and
   classifications and changes made to taxonomies.

 * Different authorities have different opinions on what the correct taxonomy is
   based on existing evidence.

 * It can be difficult to present differences beteween different taxonomies or
   how taxa in different taxonomies are related to each other.

 * Some languages have multiple synonym names for well known species as well as
   popular names for groups of species that do not match current scientifice
   taxonomies.

### Sources of information on bird names and taxonomies

Many countries' national ornithological associations have maintained name lists
which have listed the official names of all birds that can be seen in given
country. These lists are based on some scientifically accepted classification of
bird species. But the classification used in one country can differ from that
in another country. Even if two countries base their official list on the same
classification, there may exist differences in how the two list handles some
species. A species with two subspecies in one list may be considered two
different species in another list.

For amateur ornothologists who want to keep track of which birds they've seen,
the current situation with names and name lists can be confusing!

The main sources I have used over the years are:

 * [IOC World Bird List](http://www.worldbirdnames.org/ioc-lists/master-list-2/)
 * [Birdlife Sweden](http://birdlife.se/tk/svenska-namn-pa-varldens-faglar/)
 * [Zoonomen](http://www.zoonomen.net/avtax/frame.html)

## References

Here are some references to books I've read when studying the subject of
taxonomy. Of course, the number of articles, both published and blog articles
I've read, are to many to list (or remember) here!

 * [*Biological Systematics - Principles and Applications*, Randall T. Schuch, 2000](https://www.amazon.com/Biological-Systematics-Principles-Applications-2nd/dp/0801447992)
 * [*Describing Species*, Judith E. Winston, 1999](https://www.amazon.com/Describing-Species-Judith-Winston/dp/0231068255)
 * [*Species - A History of the Idea*, John S. Wilkins, 2009](https://www.amazon.com/Species-History-Idea-Systematics/dp/0520271394)
