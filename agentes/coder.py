from core.agent_base import AgentBase
import textwrap


class CoderAI(AgentBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'Coder'

    def handle(self, task_spec: str) -> dict:
        """Gera um módulo Python simples a partir de um spec curto.

        Retorna dict contendo 'code' (str) e 'entrypoint' (nome da função).
        """
        fn_name = 'generated_main'
        code = textwrap.dedent(f"""
        # Auto-gerado pelo CoderAI para: {task_spec}
        def {fn_name}():
            '''Função principal gerada.'''
            return 'OK: {task_spec}'

        if __name__ == '__main__':
            print({fn_name}())
        """)
        return {"agent": self.name, "code": code, "entrypoint": fn_name}

