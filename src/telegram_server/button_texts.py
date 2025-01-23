class ButtonText:
    """Constants for telegram bot button text and keyboard layouts.

    Provides standardized button text strings and keyboard layout configuration
    for the telegram bot interface.
    """

    PORTFOLIO = "💼 Portfolio"
    ANALYZE = "📊 Analyze market"
    RECOMMEND = "💡 Get recommendations"
    MENU = "🔙 Menu"
    UPDATE_PORTFOLIO = "🔄 Update portfolio"

    @classmethod
    def get_keyboard_layout(cls) -> list:
        return [[cls.PORTFOLIO], [cls.ANALYZE], [cls.RECOMMEND]]
