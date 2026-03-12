from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from django.contrib.auth import get_user_model


class BackupModuloTests(TestCase):
	def setUp(self):
		self.user_model = get_user_model()
		self.superadmin = self.user_model.objects.create_superuser(
			username='superadmin',
			password='Admin12345!',
			documento='12345678',
			email='superadmin@test.com',
		)
		self.admin = self.user_model.objects.create_user(
			username='admin',
			password='Admin12345!',
			documento='87654321',
			email='admin@test.com',
			is_staff=True,
			is_superuser=False,
		)

	def test_superadmin_puede_generar_backup(self):
		self.client.force_login(self.superadmin)
		response = self.client.post(reverse('usuarios:generar_backup_db'))

		self.assertIn(response.status_code, [200, 302])
		if response.status_code == 200:
			self.assertIn('attachment;', response.get('Content-Disposition', ''))
		else:
			self.assertRedirects(response, reverse('usuarios:perfil'))

	def test_admin_no_superuser_no_puede_generar_backup(self):
		self.client.force_login(self.admin)
		response = self.client.post(reverse('usuarios:generar_backup_db'))

		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, reverse('core:dashboard'))

	def test_restaurar_backup_rechaza_extension_invalida(self):
		self.client.force_login(self.superadmin)
		invalid_file = SimpleUploadedFile('respaldo.txt', b'no-es-sqlite', content_type='text/plain')
		response = self.client.post(reverse('usuarios:restaurar_backup_db'), {'backup_file': invalid_file})

		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, reverse('usuarios:perfil'))
