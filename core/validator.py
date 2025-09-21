import subprocess
import logging

logger = logging.getLogger("validator")

def run_tests():
    try:
        result = subprocess.run(
            ["pytest", "--maxfail=1", "--disable-warnings", "-q"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            logger.info("✅ Testes passaram. Código aprovado.")
            return True, result.stdout
        else:
            logger.error("❌ Testes falharam")
            logger.error(result.stdout)
            logger.error(result.stderr)
            return False, result.stdout + result.stderr
    except Exception as e:
        logger.error(f"Erro ao rodar testes: {e}")
        return False, str(e)

