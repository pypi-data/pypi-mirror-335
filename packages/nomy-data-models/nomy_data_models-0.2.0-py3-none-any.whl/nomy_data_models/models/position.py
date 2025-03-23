"""Position model for tracking trading positions."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID as PythonUUID

from sqlalchemy import (
    JSON,
    DateTime,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import (
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel
from .enums import MarketType, PositionDirection, PositionStatus


class Position(BaseModel):
    """Model for tracking trading positions."""

    # Position identifiers
    position_id: Mapped[PythonUUID] = mapped_column(
        UUID, nullable=False, index=True, comment="Unique identifier for the position"
    )

    # Position classification
    chain_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    exchange: Mapped[str] = mapped_column(
        String(length=100), nullable=False, index=True
    )
    market_type: Mapped[MarketType] = mapped_column(
        SQLEnum(MarketType), nullable=False, index=True
    )
    position_direction: Mapped[PositionDirection] = mapped_column(
        SQLEnum(PositionDirection), nullable=False
    )

    # Wallet information
    wallet_address: Mapped[str] = mapped_column(
        String(length=42), nullable=False, index=True
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
    base_token_address: Mapped[Optional[str]] = mapped_column(
        String(length=64), nullable=True, index=True
    )

    quote_token_symbol: Mapped[str] = mapped_column(
        String(length=10), nullable=False, index=True
    )
    quote_token_address: Mapped[Optional[str]] = mapped_column(
        String(length=64), nullable=True, index=True
    )

    # Position status
    status: Mapped[PositionStatus] = mapped_column(
        SQLEnum(PositionStatus), nullable=False, index=True
    )

    notional_amount_usd: Mapped[Decimal] = mapped_column(
        Numeric(precision=36, scale=18), nullable=False, default=0
    )

    # Position size and cost
    current_base_amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=36, scale=18), nullable=False
    )
    original_base_amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=36, scale=18), nullable=False
    )
    avg_entry_price: Mapped[Decimal] = mapped_column(
        Numeric(precision=36, scale=18), nullable=False
    )
    avg_exit_price: Mapped[Decimal] = mapped_column(
        Numeric(precision=36, scale=18), nullable=False
    )
    cost_basis: Mapped[Decimal] = mapped_column(
        Numeric(precision=36, scale=18), nullable=False
    )

    # PnL tracking
    realized_pnl: Mapped[Decimal] = mapped_column(
        Numeric(precision=36, scale=18), nullable=False, default=0
    )
    realized_pnl_usd: Mapped[Decimal] = mapped_column(
        Numeric(precision=36, scale=18), nullable=False, default=0
    )

    # Trade references
    opening_trades: Mapped[dict] = mapped_column(JSON, nullable=False)
    closing_trades: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # Performance metrics
    realized_roi: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=10, scale=6), nullable=True
    )
    leverage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=10, scale=6), nullable=True
    )
    # Time tracking
    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    closed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    fee_json: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="Fee information as a JSON object"
    )

    __table_args__ = (
        UniqueConstraint(
            "wallet_address",
            "token_symbol_pair",
            "position_id",
            name="uix_position_wallet_token_pair_position_id",
        ),
    )

    def __repr__(self) -> str:
        """String representation of the Position."""
        return (
            f"<Position(id={self.id}, "
            f"wallet={self.wallet_address[:8]}..., "
            f"pair={self.token_symbol_pair}, "
            f"direction={self.position_direction.value}, "
            f"status={self.status.value}, "
            f"realized_pnl_usd={self.realized_pnl_usd})>"
        )
