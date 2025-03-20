from unicodedata import name
from IPython.display import display, Markdown
import math
from Levenshtein import ratio
from typing import Tuple, List, Dict

WILDCARD = "*"


def compareLists(should, given, *, label_threshold):
    badCount = 0
    should_cpy = should.copy()
    given_copy = given.copy()

    for a in given_copy:
        if not any([ratio(a, b) >= label_threshold for b in should_cpy]) and not any(
            [
                ratio(a.split("_")[-1], b.split("_")[-1]) >= label_threshold
                for b in should_cpy
            ]
        ):
            if WILDCARD in should_cpy:
                should_cpy.remove(WILDCARD)
            else:
                badCount += 1  # Superfluous item in given

    # In a correct solution, all wildcards should be removed by now

    for a in should_cpy:
        if not any([ratio(a, b) >= label_threshold for b in given_copy]) and not any(
            [
                ratio(a.split("_")[-1], b.split("_")[-1]) >= label_threshold
                for b in given_copy
            ]
        ):
            badCount += 1  # Missing item in given

    return badCount


def compare_deduction_settings(
    wrong_relation=1,
    wrong_attribute=1,
    wrong_primary=1,
    wrong_subset=1,
    wrong_intersection=1,
) -> Dict[str, int]:
    return {
        "wrong_relation": wrong_relation,
        "wrong_attribute": wrong_attribute,
        "wrong_primary": wrong_primary,
        "wrong_subset": wrong_subset,
        "wrong_intersection": wrong_intersection,
    }


class RM:
    relations = []
    subsets = []
    intersections = []

    def __init__(self):
        self.relations = []
        self.subsets = []
        self.intersections = []
        return

    def addRelation(self, relation):
        for r in self.relations:
            if relation.name == r.name:
                print(f"Fehler: Relation mit Name {r.name} wurde bereits hinzugefügt.")
                return
        self.relations.append(relation)

    def addDependency(self, dependency):
        if str(dependency.__class__.__name__) == "Subset":
            self.subsets.append(dependency)
            return
        if str(dependency.__class__.__name__) == "Intersection":
            self.intersections.append(dependency)
            return
        print(
            "Fehler: An addDependency sollte entweder ein Subset oder eine Intersection übergeben werden."
        )
        print("Es wurde ein " + dependency.__class__.__name__ + " übergeben.")

    def getNumRelations(self):
        return len(self.relations)

    def getNumDependencies(self):
        return len(self.subsets) + len(self.intersections)

    def display(self):
        for r in self.relations:
            r.display()
        for s in self.subsets:
            s.display()
        for i in self.intersections:
            i.display()

        if len(self.relations) + len(self.subsets) + len(self.intersections) == 0:
            display(Markdown("(empty Relation)"))

    def get_scaled_score(self, rm, scores, max_points, debug=False):
        """Get the scaled score, that is the fraction of the max score, scaled to the worst archievable score."""
        worst_score = self.compare_against(RM(), scores, False)
        score = self.compare_against(rm, scores, debug)
        penalty = round((score / worst_score) * max_points)
        result = max(0, max_points - penalty)
        print(
            f"Setze abgezogene Punkte in Maßstab zu den möglichen Gesamtpunkten der Aufgabe: {penalty}"
        )
        print(f"Ergebniss: {result} / {max_points} punkte erreicht")
        return result

    def compare_relations(
        self, rm, relation_mappings, scores, debug=False, label_threshold=0.8
    ) -> Dict[str, str]:
        score = 0
        for r1 in self.relations:
            # check for possible matches by comparing the name of the relation w.r.t. the given threshold
            all_possible_matches: List[Tuple[float, Relation]] = []
            for r2 in rm.relations:
                if ratio(r1.name, r2.name) >= label_threshold:
                    all_possible_matches.append((ratio(r1.name, r2.name), r2))

            if len(all_possible_matches) > 0:
                # found a match
                # sort the matches w.r.t. similiarity
                all_possible_matches.sort(key=lambda x: x[0], reverse=True)
                # choose the one with the highest similiarity
                r2 = all_possible_matches[0][1]
                relation_mappings[r1.name] = r2.name

                print(f"Relation gefunden: {r1.name}")
                # count the missing primary keys
                missingPrimaries = compareLists(
                    r1.primaryKeys, r2.primaryKeys, label_threshold=label_threshold
                )
                # count the missing normal attributes
                missingNormal = compareLists(
                    r1.attributeList, r2.attributeList, label_threshold=label_threshold
                )

                penalty = scores["wrong_attribute"] * (missingPrimaries + missingNormal)
                score += penalty

                if debug:
                    if missingPrimaries > 0:
                        print(f"Fehlenden Primärschlüssel: {missingPrimaries}")
                    if missingNormal > 0:
                        print(f"Fehlende normale Attribute: {missingNormal}")
                    if penalty > 0:
                        print(
                            f"Falsche Attribute in Relation: '{r1.name}': ziehe {penalty} Punkte ab"
                        )
            else:
                missingRelationPenalty = scores["wrong_relation"] + scores[
                    "wrong_attribute"
                ] * (len(r1.primaryKeys) + len(r1.attributeList))
                score += missingRelationPenalty
                if debug:
                    print(
                        f"Fehlende Relation '{r1.name}': ziehe {missingRelationPenalty} Punkte ab"
                    )
        return score, relation_mappings

    def compare_subsets(
        self, rm, relation_mappings, scores, debug=False, label_threshold=0.8
    ):
        score = 0
        for s1 in self.subsets:
            curr_best = None
            curr_best_score = 10000

            for s2 in rm.subsets:
                if (
                    s1.lhs.relationName in relation_mappings
                    and s1.rhs.relationName in relation_mappings
                    and relation_mappings[s1.lhs.relationName] == s2.lhs.relationName
                    and relation_mappings[s1.rhs.relationName] == s2.rhs.relationName
                ):
                    # Found correct subset
                    # Check attributes
                    missingLhs = compareLists(
                        s1.lhs.attributes,
                        s2.lhs.attributes,
                        label_threshold=label_threshold,
                    )
                    missingRhs = compareLists(
                        s1.rhs.attributes,
                        s2.rhs.attributes,
                        label_threshold=label_threshold,
                    )
                    curr_score = scores["wrong_attribute"] * (missingLhs + missingRhs)
                    if curr_score < curr_best_score:
                        if curr_best is not None:
                            print("Neues bestes Untermengen match")
                        curr_best_score = curr_score
                        curr_best = s2

            if curr_best is None:
                penalty = scores["wrong_subset"] + scores["wrong_attribute"] * (
                    len(s1.rhs.attributes) + len(s1.lhs.attributes)
                )
                score += penalty
                if debug:
                    left = s1.lhs.relationName if s1.lhs is not None else "EMPTY"
                    right = s1.rhs.relationName if s1.rhs is not None else "EMPTY"
                    print(
                        f"Fehlende Untermengen-Abh. links={left}, rechts={right}: ziehe {penalty} Punkte ab"
                    )
            else:
                if debug:
                    # if missingLhs > 0:
                    #    print(f"Wrong attributes on left side: {missingLhs}")
                    # if missingRhs > 0:
                    #    print(f"Wrong attributes on right side: {missingRhs}")
                    left = s1.lhs.relationName if s1.lhs is not None else "EMPTY"
                    right = s1.rhs.relationName if s1.rhs is not None else "EMPTY"
                    if curr_best_score > 0:
                        print(
                            f"Falsche Attribute in Untermengen-Abh. links={left}, rechts={right}: ziehe {curr_best_score} Punkte ab"
                        )
                score += curr_best_score

        return score, relation_mappings

    def compare_intersections(
        self, rm, relation_mappings, scores, debug=False, label_threshold=0.8
    ):
        score = 0
        for i1 in self.intersections:
            curr_best = None
            curr_best_score = 10000

            for i2 in rm.intersections:
                matching_intersecting_relations = False
                # Check intersecting relations
                if (
                    i1.lhs.relationName in relation_mappings
                    and i1.rhs.relationName in relation_mappings
                    and relation_mappings[i1.lhs.relationName] == i2.lhs.relationName
                    and relation_mappings[i1.rhs.relationName] == i2.rhs.relationName
                ):
                    # Found correct intersection
                    # Check attributes
                    missingLhs = compareLists(
                        i1.lhs.attributes,
                        i2.lhs.attributes,
                        label_threshold=label_threshold,
                    )
                    missingRhs = compareLists(
                        i1.rhs.attributes,
                        i2.rhs.attributes,
                        label_threshold=label_threshold,
                    )

                    matching_intersecting_relations = True
                elif (  # In case the relations are on different sides in the intersections
                    i1.lhs.relationName in relation_mappings
                    and i1.rhs.relationName in relation_mappings
                    and relation_mappings[i1.lhs.relationName] == i2.rhs.relationName
                    and relation_mappings[i1.rhs.relationName] == i2.lhs.relationName
                ):
                    # Found correct (switched) intersection
                    # Check attributes
                    missingLhs = compareLists(
                        i1.lhs.attributes,
                        i2.rhs.attributes,
                        label_threshold=label_threshold,
                    )
                    missingRhs = compareLists(
                        i1.rhs.attributes,
                        i2.lhs.attributes,
                        label_threshold=label_threshold,
                    )

                    matching_intersecting_relations = True

                if matching_intersecting_relations:
                    # Check intersection result
                    missingRes = 0
                    if (
                        i1.equals is not None and i2.equals is not None
                    ):  # Resulting relation name is ignored since its only relevant that it covers the right attributes
                        missingRes = compareLists(
                            i1.equals.attributes,
                            i2.equals.attributes,
                            label_threshold=label_threshold,
                        )
                    elif (i1.equals is None and i2.equals is not None) or (
                        i1.equals is not None and i2.equals is None
                    ):
                        missingRes = (
                            len(i1.equals.attributes)
                            if i2.equals is None
                            else len(i2.equals.attributes)
                        )

                    curr_score = scores["wrong_attribute"] * (
                        missingLhs + missingRhs + missingRes
                    )
                    if curr_score < curr_best_score:
                        if curr_best is not None:
                            print("Neues bestes schnitt match")
                        curr_best_score = curr_score
                        curr_best = i2

            if curr_best is None:
                penalty = scores["wrong_intersection"] + scores["wrong_attribute"] * (
                    len(i1.rhs.attributes) + len(i1.lhs.attributes)
                )
                score += penalty
                if debug:
                    left = i1.lhs.relationName if i1.lhs is not None else "EMPTY"
                    right = i1.rhs.relationName if i1.rhs is not None else "EMPTY"
                    equals = (
                        i1.equals.relationName if i1.equals is not None else "EMPTY"
                    )
                    print(
                        f"Fehlender Schnitt: links={left}, rechts={right}, Schnittmenge={equals}. Ziehe {penalty} Punkte ab"
                    )
            else:
                if debug:
                    # if missingLhs > 0:
                    #    print(f"Wrong attributes on left side: {missingLhs}")
                    # if missingRhs > 0:
                    #    print(f"Wrong attributes on right side: {missingRhs}")
                    left = i1.lhs.relationName if i1.lhs is not None else "EMPTY"
                    right = i1.rhs.relationName if i1.rhs is not None else "EMPTY"
                    if curr_best_score > 0:
                        print(
                            f"Falsche Attribute in Schnitt: linkeRelation={left}, rechteRelation={right}: ziehe {curr_best_score} Punkte ab"
                        )
                score += curr_best_score

        return score, relation_mappings

    def compare_against(self, rm, scores, debug=False, label_threshold=0.8):
        if debug:
            print("Überprüfe Relationen...")

        # store relation mappings (from self to rm)
        relation_mappings: Dict[str, str] = {}

        # 1. Check relations
        score_relations, relation_mappings = self.compare_relations(
            rm, relation_mappings, scores, debug, label_threshold
        )

        if debug:
            print("Überprüfe Untermengen-Abhängigkeiten...")

        # 2. Check subsets
        score_subsets, relation_mappings = self.compare_subsets(
            rm, relation_mappings, scores, debug, label_threshold
        )

        if debug:
            print("Überprüfe Schnittmenge-Abhängigkeiten...")

        # 3. Check intersections
        score_intersections, relation_mappings = self.compare_intersections(
            rm, relation_mappings, scores, debug, label_threshold
        )

        if debug:
            print(
                f"Insgesamt abgezogene Punkte: {score_relations + score_subsets + score_intersections}"
            )

        return score_relations + score_subsets + score_intersections


class ProjectedRelation:
    relationName = ""
    attributes = []

    def __init__(self, relationName, attributes):
        self.relationName = relationName
        self.attributes = attributes

    def getMarkdown(self):
        return self.relationName + "[" + ", ".join(self.attributes) + "]"

    def display(self):
        display(Markdown(self.getMarkdown()))

    def compareTo(self, projectedRelation, *, label_threshold):
        if self.relationName != projectedRelation.relationName:
            return 0
        return max(
            0,
            compareLists(
                self.attributes,
                projectedRelation.attributes,
                label_threshold=label_threshold,
            ),
        )


class Relation:
    name = ""
    attributeList = []  # Excluding primary keys???
    primaryKeys = []

    def __init__(self, name, primaryKeys, attributeList):
        self.name = name
        self.attributeList = attributeList
        self.primaryKeys = primaryKeys

    def getMarkdown(self):
        return (
            self.name
            + "("
            + ", ".join(map(lambda x: "<u>" + x + "</u>", self.primaryKeys))
            + (
                ""
                if len(self.primaryKeys) == 0 or len(self.attributeList) == 0
                else ", "
            )
            + ", ".join(self.attributeList)
            + ")"
        )

    def display(self):
        display(Markdown(self.getMarkdown()))

    def compareTo(self, relation, *, label_threshold):
        if self.name != relation.name:
            return 0
        return max(
            0,
            compareLists(
                self.attributeList,
                relation.attributeList,
                label_threshold=label_threshold,
            )
            + compareLists(
                self.primaryKeys, relation.primaryKeys, label_threshold=label_threshold
            ),
        )


class Subset:
    lhs = None  # Takes a projected relation
    rhs = None  # Takes a projected relation

    def __init__(self, lhs, rhs):
        # if ((not isinstance(lhs, ProjectedRelation)) or (not isinstance(rhs, ProjectedRelation))):
        # print("Fehler: An ein Subset sollten zwei ProjectedRelations übergeben werden")
        self.lhs = lhs
        self.rhs = rhs

    def getMarkdown(self):
        return self.lhs.getMarkdown() + " ⊆ " + self.rhs.getMarkdown()

    def display(self):
        display(Markdown(self.getMarkdown()))

    def compareTo(self, subset, *, label_threshold):
        return self.lhs.compareTo(
            subset.lhs, label_threshold=label_threshold
        ) + self.rhs.compareTo(subset.rhs, label_threshold=label_threshold)


class Intersection:
    lhs = None
    rhs = None
    equals = None

    def __init__(self, lhs, rhs, equals):
        # if ((not isinstance(lhs, ProjectedRelation)) or (not isinstance(rhs, ProjectedRelation))):
        # print("Fehler: An eine Intersection sollten zwei ProjectedRelations übergeben werden")
        self.lhs = lhs
        self.rhs = rhs
        self.equals = equals

    def getMarkdown(self):
        return (
            self.lhs.getMarkdown()
            + " ∩ "
            + self.rhs.getMarkdown()
            + " = "
            + (self.equals.getMarkdown() if self.equals is not None else "EMPTY")
        )

    def display(self):
        display(Markdown(self.getMarkdown()))

    def compareTo(self, intersection, *, label_threshold):
        # self.equals will not be tested
        return self.rhs.compareTo(
            intersection.rhs, label_threshold=label_threshold
        ) + self.lhs.compareTo(intersection.lhs, label_threshold=label_threshold)
