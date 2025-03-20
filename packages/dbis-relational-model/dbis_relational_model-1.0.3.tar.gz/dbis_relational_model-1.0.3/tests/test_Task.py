import json
from tests.basetest import Basetest
from dbis_relational_model import (
    RM,
    Relation,
    Intersection,
    ProjectedRelation,
    compare_deduction_settings,
)


def get_simple_should():
    should = RM()
    should.addRelation(Relation("Katze", ["name"], ["alter", "farbe"]))
    return should


def get_simple_should_intersection_empty():
    should = RM()
    should.addRelation(Relation("Katze", ["name"], ["alter", "farbe"]))
    should.addRelation(Relation("Hund", ["name"], ["alter", "geruch"]))
    should.addDependency(
        Intersection(
            ProjectedRelation("Katze", ["name"]),
            ProjectedRelation("Hund", ["name"]),
            None,
        )
    )
    return should


def get_simple_should_intersection_Full():
    should = RM()
    should.addRelation(Relation("Katze", ["name"], ["alter", "farbe"]))
    should.addRelation(Relation("Hund", ["name"], ["alter", "geruch"]))
    should.addDependency(
        Intersection(
            ProjectedRelation("Katze", ["name"]),
            ProjectedRelation("Hund", ["name"]),
            ProjectedRelation("Hund", ["name"]),
        )
    )
    return should


def get_simple_should():
    should = RM()
    should.addRelation(Relation("Katze", ["name"], ["alter", "farbe"]))
    return should


class TestRelational(Basetest):
    def setUp(self, debug=False, profile=True):
        return super().setUp(debug, profile)

    def test_compare_against_deduction_primary_missing(self):
        r = RM()
        r.addRelation(Relation("Katze", [], ["alter", "farbe"]))
        assert (
            get_simple_should().compare_against(
                r, compare_deduction_settings(), debug=True
            )
            == 1
        )

    def test_compare_against_deduction_attribute_missing(self):
        r = RM()
        r.addRelation(Relation("Katze", ["name"], ["farbe"]))
        assert (
            get_simple_should().compare_against(
                r, compare_deduction_settings(), debug=True
            )
            == 1
        )

    def test_compare_against_deduction_wrong_relation(self):
        r = RM()
        r.addRelation(Relation("Hund", ["name"], ["alter", "farbe"]))
        assert (
            get_simple_should().compare_against(
                r, compare_deduction_settings(), debug=True
            )
            == 4
        )

    def test_get_scaled_score(self):
        s = get_simple_should()
        s.addRelation(Relation("Hund", ["name"], ["alter", "kann_tricks", "spitzname"]))
        r = RM()
        r.addRelation(Relation("Katze", ["name"], ["alter"]))
        r.addRelation(Relation("Hund", ["name"], ["alter", "spitzname"]))
        # 2 attributes missing, 9 possible points to deduct, with scale of max points 10, that should account to
        # 2/9=0.2222222
        # 0.222222 * 10 = 2,2 ~= 2
        assert (
            s.get_scaled_score(
                r, compare_deduction_settings(), debug=True, max_points=10
            )
            == 8
        )


class TestIntersection(Basetest):
    def setUp(self, debug=False, profile=True):
        return super().setUp(debug, profile)

    def test_compare_against_EmptySet(self):
        r = RM()
        r.addRelation(Relation("Katze", ["name"], ["alter", "farbe"]))
        r.addRelation(Relation("Hund", ["name"], ["alter", "geruch"]))
        r.addDependency(
            Intersection(
                ProjectedRelation("Katze", ["name"]),
                ProjectedRelation("Hund", ["name"]),
                None,
            )
        )
        assert (
            get_simple_should_intersection_empty().compare_against(
                r, compare_deduction_settings(), debug=True
            )
            == 0
        )

    def test_compare_against_intersection_attribute_missing(self):
        r = RM()
        r.addRelation(Relation("Katze", ["name"], ["alter", "farbe"]))
        r.addRelation(Relation("Hund", ["name"], ["alter", "geruch"]))
        r.addDependency(
            Intersection(
                ProjectedRelation("Katze", ["name"]),
                ProjectedRelation("Hund", ["toast"]),
                None,
            )
        )
        assert (
            get_simple_should_intersection_empty().compare_against(
                r, compare_deduction_settings(), debug=True
            )
            == 2
        )
