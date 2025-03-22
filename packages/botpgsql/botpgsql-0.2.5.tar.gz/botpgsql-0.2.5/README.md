# BOTPGSQL

BOTPGSQL é uma ferramenta Python projetada para simplificar a interação com bancos de dados PostgreSQL. Este projeto fornece uma interface amigável e funcionalidades robustas para gerenciar consultas e operações em bancos de dados.

## Funcionalidades

- **Conexão Simplificada**: Crie conexões com bancos de dados PostgreSQL de forma rápida e segura.
- **Execução de Consultas**: Execute comandos SQL diretamente a partir da interface.
- **Gerenciamento de Resultados**: Manipule e visualize os resultados das consultas com facilidade.
- **Logs de Atividades**: Registre as operações realizadas para auditoria e depuração.

## Requisitos

- Python 3.10 ou superior.

## Instalação

1. Instale o pacote:
   ```bash
   pip install botpgsql
   ```

## Exemplo de Uso

```python
from botpgsql.database import Postgresql

if __name__ == "__main__":
  db = Postgresql('Bots')
  data = db.execute_script(
      """
      SELECT * FROM bots
      LIMIT 10
      """
  )
  print(data)
```

## Licença

Este projeto está licenciado sob a licença MIT. Consulte o arquivo [Licença MIT](LICENSE) para mais detalhes.

## Contribuições

Contribuições são bem-vindas! Caso tenha sugestões, melhorias ou correções, sinta-se à vontade para abrir uma issue ou enviar um pull request.

## Contato

Para dúvidas ou suporte, entre em contato com o mantenedor através do [repositório no GitHub](https://github.com/botlorien/botpgsql).
