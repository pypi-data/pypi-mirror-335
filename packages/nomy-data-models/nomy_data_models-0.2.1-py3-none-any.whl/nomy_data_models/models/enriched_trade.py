"""Enriched trade model extending TradeBase with PnL information."""

from datetime import timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy import JSON, Interval, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .trade_base import TradeBase


class EnrichedTrade(TradeBase):
    """Model for storing enriched trade data with PnL calculations."""

    __table_args__ = (
        UniqueConstraint(
            "txn_id",
            "chain_id",
            "wallet_address",
            "event_at",
            name="uix_enriched_trade_txn_chain_id_wallet_event_at",
        ),
    )

    # PnL (Profit and Loss) information
    pnl_usd: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=36, scale=18),
        nullable=True,
        comment="Profit/Loss in USD for this trade (if part of a matched pair)",
    )

    pnl: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=36, scale=18),
        nullable=True,
        comment="Profit/Loss in quote token amount for this trade (if part of a matched pair)",
    )

    roi: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=36, scale=18),
        nullable=True,
        comment="Return on Investment as a decimal (e.g., 0.05 for 5% ROI)",
    )

    holding_duration: Mapped[Optional[timedelta]] = mapped_column(
        Interval, nullable=True, comment="Holding duration as a time interval"
    )

    fee_json: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="Fee information as a JSON object"
    )

    def __repr__(self) -> str:
        """String representation of the EnrichedTrade."""
        return (
            f"<EnrichedTrade(id={self.id}, "
            f"wallet={self.wallet_address[:8]}..., "
            f"pair={self.token_symbol_pair}, "
            f"is_buy={self.is_buy}, "
            f"pnl_usd={self.pnl_usd if self.pnl_usd is not None else 'None'})>"
        )
