import time
from pathlib import Path

from django.core import management
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from watchdog.events import FileSystemEventHandler

from watchdog.observers.polling import PollingObserver as Observer

JSON_EXTS = {'.json', '.JSON'}

def looks_like_json(p: Path) -> bool:
    if not isinstance(p, Path):
        return False
    name = p.name
    if name.startswith('~$') or name.endswith('.crdownload') or name.endswith('.tmp'):
        return False
    return p.suffix in JSON_EXTS

def settle_file(path: Path, tries: int = 12, wait: float = 0.25) -> bool:
    last = -1
    for _ in range(tries):
        try:
            size = path.stat().st_size
        except FileNotFoundError:
            time.sleep(wait)
            continue
        if size == last and size > 0:
            return True
        last = size
        time.sleep(wait)
    return False

def process_file(path: Path):
    if not path.exists():
        time.sleep(0.2)
        if not path.exists():
            print(f'[watch] ignorado (arquivo desapareceu): {path}')
            return
    ok = settle_file(path)
    if not ok:
        print(f'[watch] aviso: arquivo não estabilizou a tempo, tentando assim mesmo: {path}')
    try:
        management.call_command('import_pagto', file=str(path))
    except SystemExit:
        print(f'[watch] erro (SystemExit) ao importar: {path}')
    except Exception as e:
        print(f'[watch] erro ao importar {path}: {e}')

class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory: return
        p = Path(event.src_path)
        if looks_like_json(p):
            print(f'[watch] created:  {p}')
            process_file(p)

    def on_moved(self, event):
        if event.is_directory: return
        p = Path(event.dest_path)
        if looks_like_json(p):
            print(f'[watch] moved:    {p}')
            process_file(p)

    def on_modified(self, event):
        if event.is_directory: return
        p = Path(event.src_path)
        if looks_like_json(p) and p.exists():
            print(f'[watch] modified: {p}')
            process_file(p)

class Command(BaseCommand):
    help = 'Observa a pasta de pagamentos (JSON) ' \
           'definida em settings/.env e importa automaticamente' \
           'novos arquivos.'

    def handle(self, *args, **opts):
        inbox_str = getattr(settings, 'PAGTO_INBOX', None)
        if not inbox_str:
            raise CommandError('PAGTO_INBOX não definido em settings/.env.')
        inbox = Path(inbox_str).resolve() 
        inbox.mkdir(parents=True, exist_ok=True)

        self.stdout.write(self.style.SUCCESS(f'Observando: {inbox} (CTRL+C para sair)'))

        for p in inbox.glob('*.json'):
            print(f'[watch] pre-scan: {p}')
            process_file(p)

        handler = Handler()
        observer = Observer(timeout=1.0)
        observer.schedule(handler, str(inbox), recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(1.0)
        except KeyboardInterrupt:
            observer.stop()
        finally:
            observer.join()
