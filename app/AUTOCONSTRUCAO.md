Visão: Autoconstrução do frontend

Objetivo
- Documentar como o frontend pode ser parte do organismo vivo que se auto-constrói, testando mudanças de UI e integrando deploys automáticos.

Diretrizes
- Componentes atômicos: utilizar componentes reutilizáveis que agentes podem combinar para montar páginas.
- Testes visuais automatizados: cada alteração proposta por um agente passa por teste visual (snapshot) em sandbox.
- Pipeline de preview: cada PR gerado automaticamente deve publicar um preview (netlify/render/gh-pages).

Integração com agentes
- Definir contratos (APIs/GraphQL) para que agentes possam atualizar dados e automaticamente validar a renderização.
- Hotswapping controlado: permitir que agentes atualizem componentes no preview antes de merge.

Próximos passos
- Criar um exemplo de componente que agentes possam modificar e gerar testes visuais.
- Integrar previews automáticos com o fluxo de autoconstrução.
