# Meu local de votação

Site que mostra as seções eleitorais que mudaram de local entre o 1º e o 2º turno de 2026, com dados do TSE.

## Atualizar a lista

1. Copie a lista do painel do TSE: sig.tse.jus.br > Eleitorado da eleição > Capilaridade > Seções alteradas.
2. Salve em `ferramentas/dados/tse_AAAA-MM-DD_HHMM.csv` com as colunas `UF;MUNICIPIO;ZONA;SECAO;ELEITORES;LOCAL_1T;LOCAL_2T`.
3. Rode:

```
python3 ferramentas/gerar.py ferramentas/dados/tse_AAAA-MM-DD_HHMM.csv "20/10/2026 às 6h27"
```

O script refaz os dados do `index.html` e troca a data mostrada no site. A posição das cidades no mapa vem da tabela de municípios do IBGE em `ferramentas/dados`.

A pasta `ferramentas/` não é publicada na Vercel.
