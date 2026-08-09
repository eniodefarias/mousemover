import ctypes
import platform


ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002


class PowerManager:
    def __init__(self, logger=None):
        self.logger = logger
        self.enabled = False

    def enable(self):
        """
        Mantém sistema e tela ativos no Windows.
        Em outros sistemas operacionais não faz nada.
        """

        if platform.system() != "Windows":
            if self.logger:
                self.logger.debug(
                    "Keep-awake ignorado: sistema operacional não é Windows."
                )
            return

        result = ctypes.windll.kernel32.SetThreadExecutionState(
            ES_CONTINUOUS
            | ES_SYSTEM_REQUIRED
            | ES_DISPLAY_REQUIRED
        )

        if result == 0:
            raise RuntimeError(
                "Falha ao ativar SetThreadExecutionState."
            )

        self.enabled = True

        if self.logger:
            self.logger.info(
                "Keep-awake ativado: sistema e tela serão mantidos ativos."
            )

    def disable(self):
        """
        Restaura o comportamento normal de energia do Windows.
        """

        if platform.system() != "Windows":
            return

        if not self.enabled:
            return

        result = ctypes.windll.kernel32.SetThreadExecutionState(
            ES_CONTINUOUS
        )

        if result == 0:
            if self.logger:
                self.logger.error(
                    "Falha ao restaurar SetThreadExecutionState."
                )
            return

        self.enabled = False

        if self.logger:
            self.logger.info(
                "Keep-awake desativado: comportamento normal restaurado."
            )