class ButtonText:
    PORTFOLIO = "💼 Portfolio"
    ANALYZE = "📊 Analyze market"
    RECOMMEND = "💡 Get recommendations"
    MENU = "🔙 Menu"
    UPDATE_PORTFOLIO = "🔄 Update portfolio"

    @classmethod
    def get_keyboard_layout(cls) -> list:
        return [[cls.PORTFOLIO], [cls.ANALYZE], [cls.RECOMMEND]]
