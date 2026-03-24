<div align="center">

# Mercatto

</div>

<div align="center">

![Project Status](https://img.shields.io/badge/Status-Archived-red?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11%20tested-green?style=for-the-badge)
![Framework](https://img.shields.io/badge/Framework-Kivy%20%2F%20KivyMD-orange?style=for-the-badge)

</div>

---

## Context
**Mercatto** is a legacy sales management application originally developed as an early-stage project. This repository serves as a professional archive to preserve early explorations into Python-based Graphical User Interfaces (GUI) and relational database integration.

### Operational Disclaimer
**This software is NOT intended for production use.** The codebase contains legacy architectural patterns, specifically static credentials used during development for testing purposes. It is preserved here for educational reference, code review, and to showcase the author's technical evolution.

---

## Core Functionalities
The application was designed to handle essential retail workflows, connecting a local GUI to a remote MySQL database.

* **Authentication:** Access control logic validated against a remote MySQL database.
* **Inventory Management:** Hierarchical organization of product categories and individual stock units.
* **Sales Logging:** Real-time transaction confirmation and historical record persistence.
* **Database Integration:** Direct communication with a database for centralized data management.

---

## Technical Specifications

| Component | Technology | Version |
| :--- | :--- | :--- |
| **Language** | Python | 3.11 (tested) |
| **UI Framework** | Kivy | 2.3.1 |
| **Design System** | KivyMD | 1.2.0 |
| **Database Driver** | mysql-connector-python | 8.0.28 |

---

## Mobile Build
The application can be compiled for mobile platforms using **Buildozer**.

The repository includes all required assets and configuration files at the project root:

- `buildozer.spec`
- `main.py`
- `interface_main.kv`
- `requirements.txt`
- `logo.png`
- `splash.png`

> The provided Buildozer configuration reflects the original development setup and may require adjustments for modern environments.

---

## Architectural Analysis & Limitations
To provide full transparency for reviewers and recruiters, the following technical debts are acknowledged:

* **Synchronous Database Access:** Database queries are executed on the main thread. Due to the remote nature of the MySQL server, this causes blocking I/O, resulting in UI latency during data-heavy operations.
* **Security Architecture:** The authentication system utilizes static credentials during development. Modern security protocols (hashing, salting, or token-based auth) were not the focus of this specific functional prototype.
* **Hardware Dependency:** Performance is tied to network latency between client and remote database server.

---

## Setup and Execution

### Environment Setup
Clone the repository and initialize a virtual environment:

```bash
git clone https://github.com/elyon932/mercatto-app.git
cd mercatto-app
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### Dependency Resolution
Install the required dependencies via the provided requirements file:

```bash
pip install -r requirements.txt
```

### Execution

```bash
python main.py
```

### Testing Credentials

To facilitate testing and demonstration, the following static credentials are available:

| Parameter | Value |
| :--- | :--- |
| **Username** | `elyon` |
| **Password** | `123` |

---

## Author

**Elyon Oliveira dos Santos**  
Software Developer

---

## License

This project is licensed under the MIT License.