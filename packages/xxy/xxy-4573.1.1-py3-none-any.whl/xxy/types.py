from dataclasses import dataclass


@dataclass
class Query:
    company: str
    date: str
    entity_name: str


@dataclass
class Entity:
    value: str
    reference: str
