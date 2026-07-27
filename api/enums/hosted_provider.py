from enum import StrEnum


class HostedTrialProvider(StrEnum):
    """
    Enum representing hosted model provider names for trial access.
    """

    OPENAI = "orqivium/openai/openai"
    ANTHROPIC = "orqivium/anthropic/anthropic"
    GEMINI = "orqivium/gemini/google"
    X = "orqivium/x/x"
    DEEPSEEK = "orqivium/deepseek/deepseek"
    TONGYI = "orqivium/tongyi/tongyi"

    @property
    def config_key(self) -> str:
        """Return the config key used in orqivium_config (e.g., HOSTED_{config_key}_PAID_ENABLED)."""
        if self == HostedTrialProvider.X:
            return "XAI"
        return self.name
