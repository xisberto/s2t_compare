# S2T Compare

Este é um aplicativo que visa comparar os serviços de *Speech to Text* dos
provedores de nuvem AWS, Azure e Google.

## Executando

O projeto foi desenvolvido usando o Pycharm, com python 3.11 e *venv* como 
opção de *virtual environment*.

Deve ser criado um arquivo `.env` contendo as variáveis de ambiente abaixo:

```env
TOKEN=TOKEN_BOT_TELEGRAM
AWS_ACCESS_KEY_ID=XXXXXXXX
AWS_SECRET_ACCESS_KEY=XXXXXXXXX
AWS_DEFAULT_REGION=XXXXXXXX
AWS_BUCKET=XXXXXXXXX
```

Os parâmetros de conexão com a AWS também devem ser adicionados à configuração
de execução do projeto como variáveis de ambiente.
