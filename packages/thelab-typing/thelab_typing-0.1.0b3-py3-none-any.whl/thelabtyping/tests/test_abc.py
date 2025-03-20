from unittest import TestCase

import pydantic

from thelabtyping.abc import ListOf


class Person(pydantic.BaseModel):
    name: str


class PersonList(ListOf[Person]):
    pass


class ListOfTest(TestCase):
    def setUp(self) -> None:
        self.people = PersonList.model_validate(
            [
                {"name": "Jack"},
                {"name": "Diane"},
            ]
        )

    def test_isinstance(self) -> None:
        self.assertIsInstance(self.people, PersonList)
        self.assertIsInstance(self.people[0], Person)

    def test_index_accessors(self) -> None:
        self.assertEqual(self.people[0].name, "Jack")
        self.assertEqual(self.people[1].name, "Diane")

    def test_iteration(self) -> None:
        names = ["Jack", "Diane"]
        for i, person in enumerate(self.people):
            self.assertEqual(person.name, names[i])
