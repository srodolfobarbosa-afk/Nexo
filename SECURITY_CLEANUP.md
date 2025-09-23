## Segurança: limpeza de segredos e rotação

Passos recomendados se você expôs chaves secretas (por exemplo, no chat ou em commits):

1. Revogar/rotacionar imediatamente todas as chaves expostas (Supabase, OpenAI, Google, etc.).
2. Substituir variáveis sensíveis por novos valores e apenas guardar em **GitHub Secrets** (Settings → Secrets → Actions).
3. Remover arquivos que contenham segredos e reescrever o histórico do git usando `git filter-repo` ou `BFG`.
   - Exemplo (git filter-repo):
     ```bash
     pip install git-filter-repo
     git clone --mirror git@github.com:YOUR/REPO.git repo.git
     cd repo.git
     git filter-repo --invert-paths --paths path/to/secret_file.env
     git push --force
     ```
   - Se preferir o BFG (mais simples), veja a documentação do BFG.
4. Após reescrever histórico, notifique colaboradores e force-pull onde necessário.
5. Atualize o CI para usar GitHub Secrets em vez de variáveis em arquivos.

Script seguro de detecção rápida:
  - `scripts/clean_secrets.sh` (exemplo) irá procurar por padrões comumente usados e listar arquivos que contenham ocorrências.

Se quiser, eu posso executar a reescrita de histórico e ajudar a revogar as chaves (preciso da sua confirmação para operar no repositório remoto). Caso prefira, eu gero um pull request com as mudanças (remove arquivos e adiciona .env.example) e os comandos para você executar localmente.
