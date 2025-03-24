![PyPI Version](https://img.shields.io/pypi/v/cotlette)
![Python Versions](https://img.shields.io/pypi/pyversions/cotlette)
![License](https://img.shields.io/pypi/l/cotlette)
![Downloads](https://img.shields.io/pypi/dm/cotlette)

# **Cotlette 🚀**

**Cotlette** is a modern web framework built on top of **FastAPI** , offering convenient tools for rapid web application development. Inspired by Django, it includes its own ORM, template rendering support, and built-in commands for project management, as well as an admin panel.

## **Key Features**

*   **FastAPI Under the Hood** : Leverage the full power of FastAPI to create high-performance APIs.
*   **Custom ORM** : A user-friendly interface for working with databases, similar to Django's ORM.
*   **Template Rendering** : Built-in support for rendering HTML pages.
*   **Development Commands**
*   **Minimalist Design** : A simple and intuitive project structure that is easy to extend.
*   **Asynchronous Support** : Full support for asynchronous operations to maximize performance.

## **Installation**

### **Prerequisites**

*   Python 3.6 or higher
*   pip (for installing dependencies)

### **Install via pip**

```
pip install cotlette
```

---

## **Quick Start**

Create a new project and launch the development server in just a few steps:

Create a new project:

```
cotlette startproject myproject
cd myproject
```

Start the development server:

```
cotlette runserver
```

Open your browser and navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000/) .

## **Usage Examples**

### **Creating a Model**

```
from cotlette.db import Model, fields

class Article(Model):
    title = fields.CharField(max_length=200)
    content = fields.TextField()
    published_at = fields.DateTimeField(auto_now_add=True)
```

### **Creating a View**

```
from fastapi import APIRouter
from cotlette.shortcuts import render_template

from .models import Article


router = APIRouter()

@router.get("/")
async def home():
    articles = await Article.objects.all()
    return render_template("index.html", {"articles": articles})
```

### **Working with the ORM**

```
# Creating a record
article = await Article.objects.create(title="Hello World", content="This is a test article.")

# Fetching all records
articles = await Article.objects.all()

# Filtering records
published_articles = await Article.objects.filter(published_at__isnull=False)
```

---

## **Commands**

Cotlette provides a set of commands for convenient project management:

*   **cotlette startproject \<project\_name>** : Creates a new project structure.
*   **cotlette startapp \<app\_name>** : Creates a new application within the project.
*   **cotlette runserver** : Starts the development server.
*   **cotlette shell** : Launches an interactive console for working with the project.