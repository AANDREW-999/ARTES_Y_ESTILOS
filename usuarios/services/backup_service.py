import json
import logging
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


class BackupError(Exception):
    """Error funcional del servicio de backups."""


@dataclass(frozen=True)
class BackupMetadata:
    name: str
    path: Path
    modified_at: datetime
    size_bytes: int

    @property
    def extension(self) -> str:
        return self.path.suffix.lower()

    @property
    def size_kb(self) -> float:
        return round(self.size_bytes / 1024, 2)


def get_backup_directory() -> Path:
    configured_dir = getattr(settings, 'BACKUP_DIR', None)
    backup_dir = Path(configured_dir) if configured_dir else (Path(settings.BASE_DIR) / 'backups')
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def get_excluded_models() -> list[str]:
    default_excludes = [
        'auth.user',
        'usuarios.perfil',
        'admin.logentry',
        'sessions.session',
        'contenttypes.contenttype',
    ]
    configured = getattr(settings, 'BACKUP_EXCLUDE_MODELS', default_excludes)
    return [item.strip() for item in configured if item and item.strip()]


def _safe_backup_name(filename: str) -> str:
    name = (filename or '').strip()
    if not name:
        raise BackupError('Nombre de backup invalido.')

    if Path(name).name != name:
        raise BackupError('Nombre de backup invalido.')

    return name


def resolve_backup_path(filename: str) -> Path:
    safe_name = _safe_backup_name(filename)
    backup_path = get_backup_directory() / safe_name

    if backup_path.suffix.lower() not in {'.json', '.zip'}:
        raise BackupError('Formato de backup no soportado. Usa .json o .zip.')

    if not backup_path.exists() or not backup_path.is_file():
        raise BackupError('El backup seleccionado no existe.')

    return backup_path


def list_backups() -> list[BackupMetadata]:
    backups: list[BackupMetadata] = []

    for file in get_backup_directory().iterdir():
        if not file.is_file() or file.suffix.lower() not in {'.json', '.zip'}:
            continue

        stat = file.stat()
        backups.append(
            BackupMetadata(
                name=file.name,
                path=file,
                modified_at=datetime.fromtimestamp(stat.st_mtime, tz=timezone.get_current_timezone()),
                size_bytes=stat.st_size,
            )
        )

    backups.sort(key=lambda item: item.modified_at, reverse=True)
    return backups


def _validate_json_content(raw_content: str) -> int:
    try:
        payload = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        raise BackupError(f'JSON invalido: {exc}') from exc

    if not isinstance(payload, list):
        raise BackupError('El backup JSON no tiene formato valido de fixture (lista de objetos).')

    return len(payload)


def _validate_json_file(file_path: Path) -> int:
    try:
        raw = file_path.read_text(encoding='utf-8')
    except UnicodeDecodeError as exc:
        raise BackupError('El backup no esta en UTF-8 valido.') from exc

    return _validate_json_content(raw)


def _extract_json_from_zip(zip_path: Path) -> tuple[Path, int]:
    try:
        with zipfile.ZipFile(zip_path, 'r') as archive:
            json_members = [
                member for member in archive.namelist()
                if member.lower().endswith('.json') and not member.endswith('/')
            ]

            if not json_members:
                raise BackupError('El ZIP no contiene un archivo .json.')

            source_member = json_members[0]
            with archive.open(source_member, 'r') as source:
                content = source.read().decode('utf-8')

    except zipfile.BadZipFile as exc:
        raise BackupError('El archivo ZIP esta corrupto o no es valido.') from exc
    except UnicodeDecodeError as exc:
        raise BackupError('El JSON dentro del ZIP no esta en UTF-8 valido.') from exc

    objects_count = _validate_json_content(content)
    temp_json = tempfile.NamedTemporaryFile(delete=False, suffix='.json')

    with open(temp_json.name, 'w', encoding='utf-8', newline='\n') as output:
        output.write(content)

    return Path(temp_json.name), objects_count


def _normalize_json_utf8(file_path: Path):
    raw = file_path.read_text(encoding='utf-8')
    payload = json.loads(raw)
    file_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding='utf-8',
        newline='\n',
    )


def create_backup(*, compress: bool = False) -> BackupMetadata:
    backup_dir = get_backup_directory()
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    json_name = f'backup_{timestamp}.json'
    json_path = backup_dir / json_name
    exclude_models = get_excluded_models()

    try:
        with open(json_path, 'w', encoding='utf-8', errors='strict', newline='\n') as output_file:
            call_command(
                'dumpdata',
                indent=2,
                natural_foreign=True,
                natural_primary=True,
                exclude=exclude_models,
                stdout=output_file,
            )

        _normalize_json_utf8(json_path)
        objects_count = _validate_json_file(json_path)

        final_path = json_path

        if compress:
            zip_path = backup_dir / f'backup_{timestamp}.zip'
            with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
                archive.write(json_path, arcname=json_name)

            keep_json = getattr(settings, 'BACKUP_KEEP_JSON_WHEN_ZIPPED', False)
            if not keep_json:
                json_path.unlink(missing_ok=True)

            final_path = zip_path

        logger.info(
            'Backup generado correctamente: file=%s size_bytes=%s objects=%s compress=%s',
            final_path.name,
            final_path.stat().st_size,
            objects_count,
            compress,
        )
        stat = final_path.stat()
        return BackupMetadata(
            name=final_path.name,
            path=final_path,
            modified_at=datetime.fromtimestamp(stat.st_mtime, tz=timezone.get_current_timezone()),
            size_bytes=stat.st_size,
        )
    except CommandError as exc:
        logger.exception('Error de Django al generar backup.')
        raise BackupError(f'Error de Django al generar backup: {exc}') from exc
    except Exception as exc:
        logger.exception('Error inesperado generando backup.')
        raise BackupError(f'Error inesperado generando backup: {exc}') from exc


def validate_backup_file(file_path: Path) -> int:
    if file_path.suffix.lower() == '.json':
        return _validate_json_file(file_path)
    if file_path.suffix.lower() == '.zip':
        temp_json, count = _extract_json_from_zip(file_path)
        temp_json.unlink(missing_ok=True)
        return count
    raise BackupError('Formato de backup no soportado. Usa .json o .zip.')


def restore_backup(file_path: Path):
    backup_path = Path(file_path)
    objects_count = 0
    temp_json = None

    if backup_path.suffix.lower() == '.json':
        objects_count = _validate_json_file(backup_path)
        load_path = backup_path
    elif backup_path.suffix.lower() == '.zip':
        temp_json, objects_count = _extract_json_from_zip(backup_path)
        load_path = temp_json
    else:
        raise BackupError('Formato de backup no soportado. Usa .json o .zip.')

    try:
        with transaction.atomic(using='default'):
            call_command('loaddata', str(load_path), database='default')

        logger.info(
            'Backup restaurado correctamente: source=%s objects=%s',
            backup_path.name,
            objects_count,
        )
    except CommandError as exc:
        logger.exception('Error de Django al restaurar backup.')
        raise BackupError(f'Error de Django al restaurar backup: {exc}') from exc
    except Exception as exc:
        logger.exception('Error inesperado restaurando backup.')
        raise BackupError(f'Error inesperado restaurando backup: {exc}') from exc
    finally:
        if temp_json and temp_json.exists():
            temp_json.unlink(missing_ok=True)


def delete_backup(filename: str):
    backup_path = resolve_backup_path(filename)
    backup_path.unlink(missing_ok=False)
    logger.info('Backup eliminado: %s', backup_path.name)
