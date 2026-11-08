# Quando usar
Depois que o validador aprovar a matéria: `python skills/wp_rascunho/skill.py materias/<arquivo>.md`.
Gera `<arquivo>.payload.json`. O envio ao site é feito pelo navegador logado no painel (fetch na API REST com o nonce da sessão):
1. sobe a foto em /wp-json/wp/v2/media e grava legenda e alt;
2. resolve as tags por nome (cria as que faltam);
3. cria o post com status draft e a foto de destaque.
# O que não faz
Não publica. Não edita posts existentes.
