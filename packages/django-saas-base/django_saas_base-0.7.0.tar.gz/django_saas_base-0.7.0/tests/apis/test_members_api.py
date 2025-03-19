from tests.client import FixturesTestCase
from saas_base.models import Member, Group


class TestMembersAPI(FixturesTestCase):
    user_id = FixturesTestCase.GUEST_USER_ID

    def create_demo_members(self, count: int = 10):
        users = []
        for i in range(count):
            user = Member.objects.create(
                name=f'member-{i}',
                tenant=self.tenant,
            )
            users.append(user)
        return users

    def test_list_users_via_owner(self):
        self.force_login(self.OWNER_USER_ID)
        resp = self.client.get('/m/members/')
        self.assertEqual(resp.status_code, 200)

    def test_list_users_via_guest_user(self):
        self.force_login()
        resp = self.client.get('/m/members/')
        self.assertEqual(resp.status_code, 403)

        self.add_user_perms('tenant.read')
        resp = self.client.get('/m/members/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        member = data['results'][0]
        self.assertNotIn('user', member)

    def test_list_include_user(self):
        self.add_user_perms('tenant.read')
        self.force_login()
        resp = self.client.get('/m/members/?include=user')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        member = data['results'][0]
        self.assertIn('user', member)

    def test_list_include_permissions(self):
        self.add_user_perms('tenant.read')
        self.force_login()
        resp = self.client.get('/m/members/?include=permissions')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        member = data['results'][0]
        self.assertIn('permissions', member)

    def test_invite_member_signup(self):
        self.add_user_perms('tenant.admin')
        self.force_login()
        data = {'email': 'signup@example.com'}
        resp = self.client.post('/m/members/', data=data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {'invite_email': ['This field is required.']})

        # invite non-exist user
        data = {'invite_email': 'signup@example.com'}
        resp = self.client.post('/m/members/', data=data)
        self.assertEqual(resp.status_code, 200)
        member = resp.json()
        self.assertEqual(member['status'], 'request')

        # invite existing user
        user = self.get_user(self.STAFF_USER_ID)
        data = {'invite_email': user.email}
        resp = self.client.post('/m/members/', data=data)
        self.assertEqual(resp.status_code, 200)
        member = resp.json()
        self.assertEqual(member['status'], 'waiting')

    def test_view_member_item(self):
        self.add_user_perms('tenant.read')
        self.force_login()
        member = Member.objects.filter(tenant=self.tenant, user_id=self.user_id).first()
        resp = self.client.get(f'/m/members/{member.id}/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('groups', data)
        self.assertIn('permissions', data)

    def test_remove_member_item(self):
        self.add_user_perms('tenant.admin')
        self.force_login()
        member = Member.objects.filter(tenant=self.tenant, user_id=self.user_id).first()
        resp = self.client.delete(f'/m/members/{member.id}/')
        self.assertEqual(resp.status_code, 204)

    def test_list_member_permissions(self):
        self.add_user_perms('tenant.read')
        self.force_login()
        member = Member.objects.filter(tenant=self.tenant, user_id=self.user_id).first()
        resp = self.client.get(f'/m/members/{member.id}/permissions/')
        self.assertEqual(resp.status_code, 200)

    def test_list_member_groups(self):
        self.add_user_perms('tenant.read')
        self.force_login()
        member = Member.objects.filter(tenant=self.tenant, user_id=self.user_id).first()
        resp = self.client.get(f'/m/members/{member.id}/groups/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), [])

        groups = Group.objects.filter(tenant=self.tenant).all()
        member.groups.set(groups)
        resp = self.client.get(f'/m/members/{member.id}/groups/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)
        permissions = resp.json()[0]['permissions']
        self.assertEqual(len(permissions), 3)
