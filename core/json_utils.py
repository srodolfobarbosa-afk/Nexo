import json
import re

def extract_json(text: str):
    """
    Extrai apenas o JSON válido de uma resposta do LLM.
    Remove blocos de markdown, texto extra e valida no final.
    """
    if not text or not isinstance(text, str):
        raise ValueError("Texto inválido para extração de JSON")
    
    # Tenta capturar bloco dentro de ```json ... ```
    match = re.search(r"```(?:json)?(.*?)```", text, re.DOTALL)
    if match:
        candidate = match.group(1).strip()
    else:
        # Se não encontrar bloco markdown, tenta encontrar JSON puro
        # Procura pelo primeiro { até o último }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            candidate = text[start:end+1]
        else:
            # Procura por array JSON
            start = text.find('[')
            end = text.rfind(']')
            if start != -1 and end != -1 and end > start:
                candidate = text[start:end+1]
            else:
                candidate = text.strip()

    # Remove possíveis prefixos/sufixos não JSON
    candidate = candidate.strip("` \n\t\r")
    
    # Remove possíveis caracteres de controle
    candidate = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', candidate)

    try:
        return json.loads(candidate)
    except json.JSONDecodeError as e:
        # Tenta fallback com dirtyjson se disponível
        try:
            import dirtyjson
            return dirtyjson.loads(candidate)
        except (ImportError, Exception):
            raise ValueError(f"Falha ao converter para JSON: {e}\nTexto bruto: {candidate[:200]}...")

def safe_json_response(llm_response: str, fallback_response: dict = None):
    """
    Wrapper seguro para extrair JSON de respostas de LLM com fallback
    """
    try:
        return extract_json(llm_response)
    except Exception as e:
        print(f"⚠️ Erro ao extrair JSON: {e}")
        if fallback_response:
            return fallback_response
        else:
            return {
                "action": "error",
                "response": f"Erro ao processar resposta do LLM: {str(e)[:100]}",
                "raw_response": llm_response[:200] if llm_response else "Resposta vazia"
            }

def create_json_prompt(instruction: str, json_schema: dict = None):
    """
    Cria um prompt otimizado para garantir resposta JSON válida
    """
    base_prompt = f"""
{instruction}

IMPORTANTE: Responda APENAS com JSON válido, sem texto extra, sem markdown, sem explicação.
Não use ```json ou qualquer wrapper de código.
Responda diretamente com o objeto JSON.
"""
    
    if json_schema:
        base_prompt += f"\nEstrutura esperada:\n{json.dumps(json_schema, indent=2)}"
    
    return base_prompt

# Schemas comuns para o EcoGuardians
MISSION_INTERPRETATION_SCHEMA = {
    "action": "create_agent|use_existing|clarify|auto_construct",
    "agent_name": "string",
    "description": "string", 
    "requirements": ["list", "of", "strings"],
    "response": "string",
    "use_auto_construction": "boolean"
}

ARCHITECTURE_SCHEMA = {
    "overview": "string",
    "components": ["list", "of", "components"],
    "dependencies": ["list", "of", "dependencies"],
    "files_to_create": ["list", "of", "file", "paths"],
    "files_to_modify": ["list", "of", "file", "paths"],
    "database_changes": ["list", "of", "changes"],
    "api_endpoints": ["list", "of", "endpoints"],
    "testing_strategy": "string",
    "deployment_steps": ["list", "of", "steps"]
}

CODE_IMPLEMENTATION_SCHEMA = {
    "files": {"file_path": "file_content"},
    "installation_commands": ["list", "of", "commands"],
    "setup_instructions": ["list", "of", "instructions"]
}

REVIEW_SCHEMA = {
    "approved": "boolean",
    "score": "number (0-10)",
    "strengths": ["list", "of", "strengths"],
    "issues": ["list", "of", "issues"],
    "suggestions": ["list", "of", "suggestions"],
    "security_check": "string",
    "performance_check": "string",
    "compatibility_check": "string"
}

if __name__ == "__main__":
    # Teste da função
    test_responses = [
        '```json\n{"test": "value"}\n```',
        '{"test": "value"}',
        'Aqui está o JSON: {"test": "value"} espero que ajude!',
        '```\n{"test": "value"}\n```',
        'JSON inválido aqui'
    ]
    
    for i, response in enumerate(test_responses):
        try:
            result = extract_json(response)
            print(f"Teste {i+1}: ✅ {result}")
        except Exception as e:
            print(f"Teste {i+1}: ❌ {e}")
