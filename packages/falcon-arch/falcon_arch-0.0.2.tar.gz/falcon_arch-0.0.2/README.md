# FalconArch Framework

**Do you speak English? Read the README in English _[here](https://github.com/celiovmjr/falcon-arch/blob/main/README_en.md)_**

**FalconArch** é uma biblioteca leve e modular que fornece uma estrutura base para o desenvolvimento de aplicações com **Flask**. Ela simplifica a criação de rotas, o gerenciamento de blueprints e o carregamento dinâmico de controladores, além de suportar múltiplos métodos HTTP e fornecer logs detalhados para facilitar o debugging.

## 🚀 Recursos

- **Estrutura baseada no padrão MVC**: Organize sua aplicação de forma modular com os padrões **Model-View-Controller**.
- **Registro simplificado de blueprints**: Registre controladores e rotas facilmente com uma interface simples.
- **Carregamento dinâmico de controladores**: Carregue controladores automaticamente, sem a necessidade de configurações complicadas.
- **Suporte para múltiplos métodos HTTP**: Defina rotas para diferentes métodos HTTP (`GET`, `POST`, `PUT`, `DELETE`, etc.).
- **Logs detalhados com emojis**: O framework oferece logs com emojis para tornar o processo de debugging mais fácil e intuitivo.

## 📂 Estrutura do Projeto

```
.
├── app
│   ├── models
│   │   └── ...
│   ├── views
│   │   └── ...
│   ├── http
│   │   ├── middlewares
│   │   │   └── ...
│   │   ├── requests
│   │   │   └── ...
│   │   └── controllers
│   │       └── ...
│   └── services
│       └── ...
├── public
│   └── ...
└── routes
    └── ...
```

## 🛠 Instalação

```bash
pip install falcon-arch
```

## 🎨 Como Declarar Rotas

### **Definindo Rotas em Arquivos**:

- **Exemplo de rota para página web**:

   ```python
   from falcon_arch import Router

   web = Router()

   web.get("/home", "HomeController@index")
   web.post("/submit", "FormController@submit")
   ```

- **Exemplo de rota para API**:

   ```python
   from falcon_arch import Router

   users = Router(prefix="/api/users")

   users.get("/", "UserController@index")
   users.get("/<int:id>", "UserController@show")
   users.post("/", "UserController@store")
   ```

### **Registrando Rotas no Servidor**:

```python
from falcon_arch import FalconArch

app = FalconArch(__name__, template_folder="app/views", static_folder="public")

if __name__ == "__main__":
    app.run(app, host="0.0.0.0", port=80, threads=10, _quiet=True)
```

## 📜 Renderizando Views

Para renderizar uma view usando **Jinja**, utilize o método `Response.render`:

```python
from falcon_arch import Response

def index(request, response: Response):
    return response.render("home.html", {"title": "Página Inicial"})
```

O diretório padrão para views é `/app/views`, e os arquivos estáticos estão localizados em `/public`.

---

## 📜 Licença

Este projeto é licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

### 🔧 Logs e Debugging

**FalconArch** oferece logs detalhados e interativos com emojis, facilitando o acompanhamento do que está acontecendo na aplicação. Isso ajuda a depurar erros de forma mais eficiente e amigável.