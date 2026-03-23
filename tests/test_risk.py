from trading_bot.risk import RiskManager


def test_position_size_positive():
    rm = RiskManager(max_risk_per_trade=0.01)
    qty = rm.position_size(equity=100_000, entry=4.2, stop=4.0, contract_size=25_000)
    assert qty > 0


def test_leverage_check():
    rm = RiskManager(max_leverage=2.0)
    assert rm.validate_leverage(150_000, 100_000)
    assert not rm.validate_leverage(300_000, 100_000)
