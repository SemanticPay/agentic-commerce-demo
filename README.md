# Agentic commerce MCP demo

To run:

1. Install dependencies:

- Python:

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

- Node.js:

```bash
cd frontend
npm install
```

2. Ensure .env variables are set:

```bash
cp .env.example .env
```
- Update the .env file with your configurations as needed.

3. Run agent backend:

```bash
make agent-backend
```

4. In another terminal, run the frontend:

```bash
make agent-frontend
```
