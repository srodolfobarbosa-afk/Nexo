# Instruções para Purge do Histórico Git

Este documento explica passo-a-passo como remover arquivos sensíveis do histórico do repositório usando `git-filter-repo` (recomendado) ou BFG. **Atenção**: estas operações reescrevem o histórico e requerem coordenação com a equipe (force-push).

1. Pré-requisitos

- Tenha credenciais administrativas do repositório GitHub.
- Instale `git-filter-repo` (Python) ou `bfg-repo-cleaner`.

2. Exemplo usando git-filter-repo

```bash
pip install --user git-filter-repo
git clone --mirror https://github.com/SEU-USER/Nexo.git
cd Nexo.git
git filter-repo --invert-paths --path .secrets.baseline --path .secrets.current --path nexo_data.db --path memoria_curto_prazo.json
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force
```

3. Pós-purge

- Rotacione todas as chaves que podem ter sido comprometidas.
- Atualize os mantenedores e crie um comunicado interno com lista de ações (rotacionar, revogar tokens, revisar logs de acesso).
- Habilite Secret Scanning e branch protection.

4. Considerações legais e operacionais

- Force-push altera commits hashes; outros colaboradores deverão reclonar ou rebasear seus branches.
- Planeje janela de manutenção e comunique claramente para evitar perda de trabalho.
