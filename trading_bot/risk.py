from dataclasses import dataclass


@dataclass
class RiskManager:
    max_risk_per_trade: float = 0.01
    max_portfolio_risk: float = 0.05
    max_leverage: float = 2.0

    def position_size(self, equity: float, entry: float, stop: float, contract_size: float = 1.0) -> float:
        risk_amount = equity * self.max_risk_per_trade
        per_unit_risk = max(abs(entry - stop) * contract_size, 1e-9)
        return risk_amount / per_unit_risk

    def validate_leverage(self, gross_exposure: float, equity: float) -> bool:
        leverage = gross_exposure / max(equity, 1e-9)
        return leverage <= self.max_leverage

    def validate_portfolio_risk(self, total_open_risk: float, equity: float) -> bool:
        return (total_open_risk / max(equity, 1e-9)) <= self.max_portfolio_risk
