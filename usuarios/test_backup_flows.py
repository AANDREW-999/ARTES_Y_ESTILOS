from pathlib import Path
from tempfile import NamedTemporaryFile
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from usuarios.services.backup_service import BackupError


User = get_user_model()


class BackupFlowsTestCase(TestCase):
    def setUp(self):
        self.password = 'Admin12345!'
        self.superadmin = User.objects.create_superuser(
            username='superadmin_backup',
            documento='99887766',
            email='superadmin.backup@test.com',
            password=self.password,
        )
        self.staff = User.objects.create_user(
            username='staff_backup',
            documento='11223344',
            email='staff.backup@test.com',
            password=self.password,
            is_staff=True,
            is_active=True,
        )

    def test_superadmin_can_generate_backup_and_store_auto_download(self):
        self.client.force_login(self.superadmin)

        with patch('usuarios.views.create_backup', return_value=SimpleNamespace(name='backup_20260321_205029.json')):
            response = self.client.post(reverse('usuarios:generar_backup_db'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('usuarios:seguridad'))
        self.assertEqual(self.client.session.get('backup_auto_download'), 'backup_20260321_205029.json')

    def test_generate_backup_error_shows_message(self):
        self.client.force_login(self.superadmin)

        with patch('usuarios.views.create_backup', side_effect=BackupError('fallo esperado')):
            response = self.client.post(reverse('usuarios:generar_backup_db'), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No fue posible generar el backup')

    def test_seguridad_view_pops_auto_download_from_session(self):
        self.client.force_login(self.superadmin)
        session = self.client.session
        session['backup_auto_download'] = 'backup_test.json'
        session.save()

        response = self.client.get(reverse('usuarios:seguridad'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['auto_download_backup'], 'backup_test.json')
        self.assertNotIn('backup_auto_download', self.client.session)

    def test_staff_cannot_generate_backup(self):
        self.client.force_login(self.staff)
        response = self.client.post(reverse('usuarios:generar_backup_db'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('core:dashboard'))

    def test_restore_requires_file_or_selection(self):
        self.client.force_login(self.superadmin)
        response = self.client.post(reverse('usuarios:restaurar_backup_db'), {}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Debes seleccionar un backup o subir un archivo.')

    def test_restore_rejects_invalid_extension(self):
        self.client.force_login(self.superadmin)
        invalid_file = SimpleUploadedFile('respaldo.txt', b'invalido', content_type='text/plain')

        response = self.client.post(reverse('usuarios:restaurar_backup_db'), {'backup_file': invalid_file}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Archivo inválido. Solo se permiten backups .json o .zip.')

    @override_settings(BACKUP_MAX_UPLOAD_MB=1)
    def test_restore_rejects_oversized_file(self):
        self.client.force_login(self.superadmin)
        oversized = SimpleUploadedFile('backup.json', b'a' * (1024 * 1024 + 1), content_type='application/json')

        response = self.client.post(reverse('usuarios:restaurar_backup_db'), {'backup_file': oversized}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'El archivo supera el límite de 1 MB.')

    def test_restore_by_selected_backup_calls_service(self):
        self.client.force_login(self.superadmin)
        backup_path = Path('C:/tmp/backup_20260321.json')

        with patch('usuarios.views.resolve_backup_path', return_value=backup_path) as mock_resolve, \
             patch('usuarios.views.validate_backup_file') as mock_validate, \
             patch('usuarios.views.restore_backup') as mock_restore:
            response = self.client.post(
                reverse('usuarios:restaurar_backup_db'),
                {'backup_selected': 'backup_20260321.json'},
                follow=True,
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Backup restaurado correctamente.')
        mock_resolve.assert_called_once_with('backup_20260321.json')
        mock_validate.assert_called_once_with(backup_path)
        mock_restore.assert_called_once_with(backup_path)

    def test_delete_backup_success_message(self):
        self.client.force_login(self.superadmin)

        with patch('usuarios.views.delete_backup') as mock_delete:
            response = self.client.post(
                reverse('usuarios:eliminar_backup_db', args=['backup_20260321.json']),
                follow=True,
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Backup eliminado: backup_20260321.json.')
        mock_delete.assert_called_once_with('backup_20260321.json')

    def test_download_backup_returns_attachment(self):
        self.client.force_login(self.superadmin)
        with NamedTemporaryFile(suffix='.json', delete=False) as temp:
            temp.write(b'[]')
            temp.flush()

        temp_path = Path(temp.name)

        try:
            with patch('usuarios.views.resolve_backup_path', return_value=temp_path):
                response = self.client.get(
                    reverse('usuarios:descargar_backup_db', args=[temp_path.name])
                )
                response.close()
        finally:
            try:
                temp_path.unlink(missing_ok=True)
            except PermissionError:
                pass

        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment;', response.get('Content-Disposition', ''))
        self.assertEqual(response.get('Content-Type'), 'application/json')

    def test_seguridad_template_uses_admin_overlay_confirm_attributes(self):
        self.client.force_login(self.superadmin)
        response = self.client.get(reverse('usuarios:seguridad'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-admin-confirm')
        self.assertContains(response, 'data-admin-progress-message="Restaurando backup..."')
        self.assertContains(response, 'data-admin-progress-message="Eliminando backup..."')
