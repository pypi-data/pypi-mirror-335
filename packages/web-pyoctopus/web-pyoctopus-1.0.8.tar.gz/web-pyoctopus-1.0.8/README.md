# Web-PyOctopus: A Lightweight Python Web Framework

![Purpose](https://img.shields.io/badge/purpose-learning-green.svg)
![PyPI](https://img.shields.io/pypi/v/web-pyoctopus.svg)

**Web-PyOctopus** is a lightweight and easy-to-use Python web framework built for learning purposes. It is a **WSGI framework**, meaning it can be used with any WSGI application server such as **Gunicorn**.

### 🔗 [View on PyPI](https://pypi.org/project/web-pyoctopus/)

---

## 🚀 Installation

### Step 1: Set Up a Virtual Environment

1. **Install `virtualenv`** (if not already installed):

   ```sh
   pip install virtualenv
   ```

2. **Create a Virtual Environment**:

   ```sh
   python -m venv venv
   ```

3. **Activate the Virtual Environment**:
   - On **Windows**:
     ```sh
     venv\Scripts\activate
     ```
   - On **macOS/Linux**:
     ```sh
     source venv/bin/activate
     ```

### Step 2: Install Web-PyOctopus

Install **Web-PyOctopus** using **pip**:

```sh
pip install web-pyoctopus
```

### Step 3: Install Gunicorn

Install **Gunicorn** to run the application:

```sh
pip install gunicorn
```

---

## 📌 Basic Usage

### Step 1: Create `app.py`

Create a file named `app.py` in your project directory and add the following code:

```python
from web_pyoctopus.api import OctopusAPI

# Create an instance of OctopusAPI
app = OctopusAPI()

# Define a route for the home page
@app.route("/home")
def home(request, response):
    response.text = "Hello from the HOME page"

# Define a route with a dynamic parameter
@app.route("/hello/{name}")
def greeting(request, response, name):
    response.text = f"Hello, {name}!"

# Define a class-based view
@app.route("/book")
class BooksResource:
    def get(self, req, resp):
        resp.text = "Books Page"

    def post(self, req, resp):
        resp.text = "Endpoint to create a book"

# Define a route for template rendering
@app.route("/template")
def template_handler(req, resp):
    resp.body = app.template(
        "index.html", context={"name": "Web-PyOctopus", "title": "Simple & Awesome Framework"}
    ).encode()
```

### Step 2: Create a Template (Optional)

If you want to use templates, create a directory named `templates` in the same folder as `app.py`. Inside the `templates` directory, create a file named `index.html`:

```html
<!DOCTYPE html>
<html>
  <head>
    <title>{{ title }}</title>
  </head>
  <body>
    <h1>Welcome to {{ name }}</h1>
  </body>
</html>
```

### Step 3: Run the Application

Run the application using **Gunicorn**:

```sh
gunicorn app:app
```

Visit the following URLs in your browser:

- `http://127.0.0.1:8000/home`
- `http://127.0.0.1:8000/hello/Octopus`
- `http://127.0.0.1:8000/book`
- `http://127.0.0.1:8000/template`

---

## 📚 Routing & Class-Based Views

Define class-based views for better organization:

```python
@app.route("/book")
class BooksResource:
    def get(self, req, resp):
        resp.text = "Books Page"

    def post(self, req, resp):
        resp.text = "Endpoint to create a book"
```

---

## 🎨 Template Rendering

Use templates for dynamic content:

```python
@app.route("/template")
def template_handler(req, resp):
    resp.body = app.template(
        "index.html", context={"name": "Web-PyOctopus", "title": "Simple & Awesome Framework"}
    ).encode()
```

Change the default template directory:

```python
app = OctopusAPI(templates_dir="custom_templates")
```

---

## 📂 Static Files

By default, static files are served from the `static` directory. You can change it:

```python
app = OctopusAPI(static_dir="assets")
```

Use them in HTML:

```html
<link href="/static/styles.css" rel="stylesheet" />
```

---

## 🛠 Middleware Support

Create custom middleware by inheriting from `Middleware`:

```python
from web_pyoctopus.middleware import Middleware

class SimpleLoggerMiddleware(Middleware):
    def process_request(self, req):
        print("Request received:", req.url)

    def process_response(self, req, res):
        print("Response sent:", req.url)

app.add_middleware(SimpleLoggerMiddleware)
```

---

## 🧪 Unit Testing

Use **pytest** for testing. Fixtures `app` and `client` help in writing tests:

```python
def test_home_route(client):
    response = client.get("/home")
    assert response.text == "Hello from the HOME page"
```

Parameterized route testing:

```python
def test_dynamic_route(client):
    response = client.get("/hello/Octopus")
    assert response.text == "Hello, Octopus!"
```

---

## 📜 License

Web-PyOctopus is an open-source project for educational purposes.

---

### 🚀 Happy Coding with Web-PyOctopus! 🎉

---
