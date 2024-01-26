# TODO app

Todo application with FastAPI

## Description

Temporary description placeholder.

## Roadmap

- [ ] CRUD operations for the `Task` model
- [ ] CRUD operations for the `TaskList` model
- [ ] Add base token authentication (with login and password)
- [ ] Relate the `TaskList` model with the `User` model
- [ ] Signup functionality via email (with all related methods such as password reset and etc.)
- [ ] Signup via Google, Telegram, Discord, VK
- [ ] Create "repeated" task lists functionality
- [ ] Add JWT usage
- [ ] Authentication via TOTP (e.g. Google Authenticator app)

## Development

### Install requirements

Install requirements

```bash
pip install -r requirements.txt
```

### How to check code and commit style

Check code style:

```bash
bash code-style.sh
```

Check commit style:

```bash
gitlint
```

Fix imports:

```bash
isort .
```

### Install linter for your commits messages

```bash
gitlint install-hook
```
