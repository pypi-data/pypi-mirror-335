"""Abstract base model for trade data with common fields."""

import re
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID as PythonUUID
from uuid import uuid4

from sqlalchemy import Boolean, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel
from .enums import MarketType


def is_valid_eth_address(address: str) -> bool:
    """Validate Ethereum address format."""
    return bool(re.match(r"^0x[a-fA-F0-9]{40}$", address))


def is_valid_sol_address(address: str) -> bool:
    """Validate Solana address format."""
    return bool(re.match(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$", address))


class TradeBase(BaseModel):
    """Abstract base model for trade data with common fields."""

    __abstract__ = True

    # Primary key fields
    id: Mapped[PythonUUID] = mapped_column(
        UUID, primary_key=True, default=uuid4, nullable=False
    )
    event_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), primary_key=True, nullable=False, index=True
    )

    # Transaction ID
    txn_id: Mapped[str] = mapped_column(String(length=66), nullable=False, index=True)

    # Blockchain identifiers
    wallet_address: Mapped[str] = mapped_column(
        String(length=42), nullable=False, index=True
    )
    chain_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    exchange: Mapped[str] = mapped_column(
        String(length=100), nullable=False, index=True
    )

    is_buy: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    token_price: Mapped[Decimal] = mapped_column(
        Numeric(precision=36, scale=18), nullable=False
    )
    # Token information
    token_symbol_pair: Mapped[str] = mapped_column(
        String(length=20), nullable=False, index=True
    )
    token_address_pair: Mapped[Optional[str]] = mapped_column(
        String(length=129), nullable=True, index=True
    )

    base_token_symbol: Mapped[str] = mapped_column(
        String(length=10), nullable=False, index=True
    )
    quote_token_symbol: Mapped[str] = mapped_column(
        String(length=10), nullable=False, index=True
    )

    base_token_address: Mapped[Optional[str]] = mapped_column(
        String(length=64), nullable=True, index=True
    )
    quote_token_address: Mapped[Optional[str]] = mapped_column(
        String(length=64), nullable=True, index=True
    )

    # Trade amounts
    base_amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=36, scale=18), nullable=False
    )
    quote_amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=36, scale=18), nullable=False
    )
    usd_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=36, scale=18), nullable=True
    )

    # Market type
    market_type: Mapped[MarketType] = mapped_column(
        SQLEnum(MarketType), nullable=False, index=True
    )
