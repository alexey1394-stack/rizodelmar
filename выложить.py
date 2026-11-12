import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = "alexey1394-stack/rizodelmar"
ORIGIN = f"https://github.com/{REPO}.git"
DOMAIN = "rizodelmar.ru"


def run(*args, check=True):
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    if check and result.returncode:
        raise RuntimeError((result.stderr or result.stdout).strip())
    return result


def check_source():
    remote = run("git", "remote", "get-url", "origin").stdout.strip()
    assert remote == ORIGIN, f"Неожиданный origin: {remote}"
    branch = run("git", "branch", "--show-current").stdout.strip()
    assert branch == "main", f"Неожиданная ветка: {branch}"
    status = run("git", "status", "--short").stdout.strip()
    assert not status, f"Есть незакоммиченные файлы:\n{status}"
    leaks = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.name == Path(__file__).name:
            continue
        if path.suffix.lower() not in {".html", ".css", ".js", ".txt", ".xml", ".svg", ""}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "/Users/" in text or "PRIVATE KEY-----" in text:
            leaks.append(str(path.relative_to(ROOT)))
    assert not leaks, f"Служебные данные в публикации: {leaks}"
    print("Источник, ветка main и файлы публикации проверены")


def pages():
    current = run("gh", "api", f"repos/{REPO}/pages", check=False)
    method = "PUT" if current.returncode == 0 else "POST"
    result = run(
        "gh", "api", "--method", method, f"repos/{REPO}/pages",
        "-f", f"cname={DOMAIN}", "-f", "source[branch]=main", "-f", "source[path]=/",
        check=False,
    )
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout).strip())
    print(f"GitHub Pages настроен для {DOMAIN}")


def live():
    errors = []
    for scheme in ("https", "http"):
        url = f"{scheme}://{DOMAIN}/"
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(request, timeout=30) as response:
                html = response.read().decode("utf-8")
                assert "RIZO DEL MAR — питомник испанской водяной собаки" in html
                assert "https://vk.ru/club238840740" in html
                print(f"Живой сайт проверен: {response.url} · HTTP {response.status}")
                return
        except Exception as error:
            errors.append(f"{url}: {error}")
    raise RuntimeError("\n".join(errors))


def main():
    if "--проверить-live" in sys.argv:
        live()
        return
    check_source()
    if "--проверить" in sys.argv:
        return
    run("git", "push", "-u", "origin", "main")
    print("Файлы отправлены в GitHub")
    pages()
    print(f"Сайт: https://{DOMAIN}/")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, RuntimeError) as error:
        sys.exit(f"Публикация остановлена: {error}")
