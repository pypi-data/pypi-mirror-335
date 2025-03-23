# FastAPI AutoDoc

FastAPI AutoDoc is a library designed to help developers generate and manage project documentation dynamically for Python projects. It integrates seamlessly with FastAPI and provides a web-based dashboard for managing and viewing documentation.

## Features

- **Dynamic Documentation**: Automatically generate documentation for Python FastApi projects.
- **Web-Based Dashboard**: View and manage documentation through a user-friendly interface.
- **File Watching**: Monitor project files for changes and update documentation in real-time.
- **REST API**: Expose endpoints for interacting with the documentation service programmatically.
- **Health Check**: Built-in health check endpoint to monitor the service.

---

## Installation

You can install the library using pip:

```bash
pip install fastapi-autodoc==1.0.0.7
```
---

## Usage

After installing the library, you can run the FastAPI AutoDoc server using the following command:

```bash
fastapi-autodoc generate
```

```bash
fastapi-autodoc runserver
```

This will start the server on `http://127.0.0.1:8000` by default.

---

## Accessing the Dashboard

Once the server is running, you can access the web-based dashboard at:

```plaintext
http://127.0.0.1:8000/api/v1/documentation/dashboard
```

From the dashboard, you can:
- View the list of documented projects.
- Generate new documentation.
- Monitor file changes in real-time.
- When you view the documentation, it will be displayed in a web-based interface. And you can always view detailed documentation

---

## Health Check

To verify that the server is running, you can access the health check endpoint:

```plaintext
http://127.0.0.1:8000/health
```

This will return a JSON response indicating the status of the service:
```json
{
  "status": "ok"
}
```

---

## Configuration

You can customize the behavior of FastAPI AutoDoc by setting environment variables in a `.env` file. For example:

```plaintext
PROJECT_PATH=the path to the project you want to document
DEBUG=True
```

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests on the [GitHub repository](https://github.com/BisiOlaYemi/fastapi-auto-doc).

---