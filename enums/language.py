from enum import Enum


class Language(str, Enum):
    EN = "en"
    AR = "ar"
    FR = "fr"
    DE = "de"
    IT = "it"
    ZH = "zh"

    @staticmethod
    def from_locale(locale: str) -> "Language":
        try:
            normalized_locale = (locale or "").replace("_", "-").split("-", 1)[0].lower()
            return Language(normalized_locale)
        except ValueError:
            return Language.EN

    def get_country_code(self):
        match self:
            case Language.AR:
                return "SA"
            case Language.EN:
                return "US"
            case Language.ZH:
                return "CN"
            case _:
                return self.name

    def get_display_name(self) -> str:
        match self:
            case Language.EN:
                return "English"
            case Language.AR:
                return "العربية"
            case Language.FR:
                return "Français"
            case Language.DE:
                return "Deutsch"
            case Language.IT:
                return "Italiano"
            case Language.ZH:
                return "中文"

    def get_flag_emoji(self):
        if len(self) != 2:
            return "?"
        regional_a = 0x1F1E6
        flag_chars = []
        for char in self.get_country_code():
            if "A" <= char <= "Z":
                flag_char = chr(regional_a + ord(char) - ord("A"))
                flag_chars.append(flag_char)
            else:
                return "?"
        return "".join(flag_chars)
