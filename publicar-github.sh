#!/usr/bin/env bash
# Publica en el repositorio YA EXISTENTE Elias-km/km-hyperframes.
# No crea repositorios ni fuerza el push; ante divergencias detiene la operación.
set -euo pipefail
cd "$(dirname "$0")"
repo='Elias-km/km-hyperframes'
remote="https://github.com/${repo}.git"

for tool in git gh; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "Falta $tool. En macOS: brew install git gh" >&2
    exit 1
  fi
done
if ! gh auth status >/dev/null 2>&1; then
  echo 'Primero autentícate en GitHub CLI: gh auth login' >&2
  exit 1
fi
if ! gh repo view "$repo" >/dev/null 2>&1; then
  echo "El repositorio $repo no es accesible desde esta sesión." >&2
  exit 1
fi
permission="$(gh api "repos/$repo" --jq '.permissions.push' 2>/dev/null || true)"
if [[ "$permission" != 'true' ]]; then
  echo "Tu sesión GitHub CLI no tiene permiso de escritura en $repo. Autentícate con la cuenta Elias-km." >&2
  exit 1
fi

if [[ ! -d .git ]]; then git init -b main; fi
if [[ -n "$(git remote 2>/dev/null | grep '^origin$' || true)" ]]; then
  actual="$(git remote get-url origin)"
  if [[ "$actual" != "$remote" && "$actual" != "git@github.com:${repo}.git" ]]; then
    echo "Se ha detectado otro remoto origin: $actual. No se modifica." >&2
    exit 1
  fi
else
  git remote add origin "$remote"
fi

if [[ -z "$(git config user.name || true)" ]]; then git config user.name "$(gh api user --jq '.login')"; fi
if [[ -z "$(git config user.email || true)" ]]; then
  uid="$(gh api user --jq '.id')"; login="$(gh api user --jq '.login')"
  git config user.email "${uid}+${login}@users.noreply.github.com"
fi

git add .
if ! git diff --cached --quiet; then
  git commit -m 'feat: incorpora parodia audiovisual de Pepe y Manuel'
fi
# Push normal: nunca se reescribe historial remoto.
if ! git push --set-upstream origin HEAD:main; then
  echo 'No se ha podido publicar. Si main contiene commits, clona primero el repositorio y copia allí los archivos del proyecto.' >&2
  exit 1
fi
echo "Publicado correctamente: https://github.com/$repo"
