import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    joint = 1

    for person in people:
        # Détermine le nombre de copies du gène pour la personne
        if person in two_genes:
            gene_count = 2
        elif person in one_gene:
            gene_count = 1
        else:
            gene_count = 0

        # Détermine si la personne a le trait
        has_trait = person in have_trait

        # Calcul de la probabilité d'avoir gene_count copies du gène
        # Cas sans information parentale : utiliser la probabilité inconditionnelle
        if people[person]["mother"] is None and people[person]["father"] is None:
            gene_prob = PROBS["gene"][gene_count]
        else:
            # La personne a des parents connus
            mother = people[person]["mother"]
            father = people[person]["father"]

            # On détermine le nombre de copies du gène chez la mère et le père
            if mother in two_genes:
                mother_gene = 2
            elif mother in one_gene:
                mother_gene = 1
            else:
                mother_gene = 0

            if father in two_genes:
                father_gene = 2
            elif father in one_gene:
                father_gene = 1
            else:
                father_gene = 0

            # Probabilité qu'un parent transmette le gène
            if mother_gene == 2:
                p_mother = 1 - PROBS["mutation"]
            elif mother_gene == 1:
                p_mother = 0.5
            else:
                p_mother = PROBS["mutation"]

            if father_gene == 2:
                p_father = 1 - PROBS["mutation"]
            elif father_gene == 1:
                p_father = 0.5
            else:
                p_father = PROBS["mutation"]

            # Calcul de la probabilité que l'enfant ait gene_count copies :
            if gene_count == 2:
                gene_prob = p_mother * p_father
            elif gene_count == 1:
                gene_prob = p_mother * (1 - p_father) + (1 - p_mother) * p_father
            else:  # gene_count == 0
                gene_prob = (1 - p_mother) * (1 - p_father)

        # Probabilité de manifester (ou non) le trait, conditionnée au nombre de copies du gène
        trait_prob = PROBS["trait"][gene_count][has_trait]

        # Multiplie la probabilité de cette personne par la probabilité conjointe
        joint *= gene_prob * trait_prob

    return joint


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        if person in two_genes:
            gene_count = 2
        elif person in one_gene:
            gene_count = 1
        else:
            gene_count = 0

        has_trait = person in have_trait

        probabilities[person]["gene"][gene_count] += p
        probabilities[person]["trait"][has_trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        # Normalise la distribution "gene"
        gene_total = sum(probabilities[person]["gene"].values())
        for count in probabilities[person]["gene"]:
            probabilities[person]["gene"][count] /= gene_total

        # Normalise la distribution "trait"
        trait_total = sum(probabilities[person]["trait"].values())
        for outcome in probabilities[person]["trait"]:
            probabilities[person]["trait"][outcome] /= trait_total


if __name__ == "__main__":
    main()
