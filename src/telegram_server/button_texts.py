class ButtonText:
    HELP = "❓ Help"
    PORTFOLIO = "💼 Portfolio"
    ANALYZE = "📊 Analyze market"
    RECOMMEND = "💡 Get recommendations"

    # Command descriptions for menu
    DESC_HELP = "❓ Show help message"
    DESC_PORTFOLIO = "💼 View your portfolio"
    DESC_ANALYZE = "📊 Analyze market conditions"
    DESC_RECOMMEND = "💡 Get investment recommendations"

    @classmethod
    def get_keyboard_layout(cls) -> list:
        return [[cls.PORTFOLIO, cls.HELP], [cls.ANALYZE, cls.RECOMMEND]]
