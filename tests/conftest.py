"""Shared ContractModel fixtures for tests."""

from __future__ import annotations

from contractmodel import ContractModel


class RawCustomer(ContractModel):
    customer_id: int
    first_name: str
    last_name: str


class Customer(ContractModel):
    customer_id: int
    full_name: str


class Rejection(ContractModel):
    customer_id: int
    reason: str


class Metrics(ContractModel):
    accepted: int
    rejected: int


class Order(ContractModel):
    order_id: int
    customer_id: int
