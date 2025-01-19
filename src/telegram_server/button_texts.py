class ButtonText:
    PORTFOLIO = "💼 Portfolio"
    ANALYZE = "📊 Analyze market"
    RECOMMEND = "💡 Get recommendations"
    MENU = "🔙 Menu"

    @classmethod
    def get_keyboard_layout(cls) -> list:
        return [[cls.MENU, cls.PORTFOLIO], [cls.ANALYZE, cls.RECOMMEND]]
