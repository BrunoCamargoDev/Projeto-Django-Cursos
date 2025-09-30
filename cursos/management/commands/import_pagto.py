import json, shutil
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
from django.utils.timezone import now
from cursos.models import Curso, Inscricao, TransacaoImportada

User = get_user_model()

class Command(BaseCommand):
    help = "Importa um arquivo JSON de pagamentos e libera/estende inscrições (no app cursos)."

    def add_arguments(self, parser):
        parser.add_argument('--file', required=True, help='Caminho do arquivo .json a processar')

    def handle(self, *args, **opts):
        file_path = Path(opts['file'])
        if not file_path.exists():
            raise CommandError(f"Arquivo não encontrado: {file_path}")

        try:
            data = json.loads(file_path.read_text(encoding='utf-8'))
            payments = data.get('payments', [])
        except Exception as e:
            self._move(file_path, settings.PAGTO_ERROS)
            raise CommandError(f'JSON inválido: {e}')

        ok, fail, dup = 0, 0, 0

        for p in payments:
            tx_id = p.get('tx_id')
            email = p.get('user_email')
            titulo = p.get('curso_titulo')
            dias = int(p.get('days') or 30)

            if not tx_id or not email or not titulo:
                self.stderr.write(self.style.ERROR(f'Linha incompleta: {p}'))
                fail += 1
                continue

            try:
                with transaction.atomic():
                    TransacaoImportada.objects.create(tx_id=tx_id, raw=p)

                    user = User.objects.filter(email=email).first()
                    if not user:
                        raise ValueError(f'Usuário não encontrado: {email}')

                    curso = Curso.objects.filter(titulo=titulo).first()
                    if not curso:
                        raise ValueError(f'Curso não encontrado: {titulo}')

                    insc, _ = Inscricao.objects.get_or_create(usuario=user, curso=curso)
                    quando = now()
                    insc.ativar_por_30_dias(quando=quando)  

                    self.stdout.write(self.style.SUCCESS(
                        f'OK tx={tx_id} user={email} curso={titulo} expira_em={insc.expira_em}+{dias}d'
                    ))
                    ok += 1

            except IntegrityError:
                self.stdout.write(self.style.WARNING(f'DUPLICADO tx={tx_id} (ignorado)'))
                dup += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'FALHA tx={tx_id}: {e}'))
                fail += 1

        self._move(file_path, settings.PAGTO_ARQUIVADO if fail == 0 else settings.PAGTO_ERROS)
        self.stdout.write(self.style.NOTICE(f'Concluído: OK={ok} DUP={dup} FAIL={fail}'))

    def _move(self, src: Path, dst_dir: str):
        Path(dst_dir).mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(Path(dst_dir) / src.name))
