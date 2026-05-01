# BotEscrivao

Estrutura inicial de um bot de Discord com menu de opcoes:
- Botao **Iniciar**
- Selecao entre **Limpeza de Ficha** e **Transferencia de Unidade**

## Requisitos
- Python 3.10+
- FFmpeg (opcional, para reproduzir áudio)

## Setup

### 1. Criar ambiente virtual
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Instalar dependências
```powershell
pip install -r requirements.txt
```

### 3. Configurar token do bot
Copie o arquivo de exemplo:
```powershell
Copy-Item .env.example .env
```

Edite `.env` com seu token:
```
DISCORD_TOKEN=SEU_TOKEN_AQUI
BOT_PREFIX=!
```

## Usar o bot

### Validacao local (sem conectar ao Discord)
```powershell
python main.py --dry-run
```

### Rodar o bot
```powershell
python main.py
```

No Discord, use o comando:
```
!menu
```

Clique em **Iniciar** e escolha entre:
- **Limpeza de Ficha**
- **Transferencia de Unidade**

