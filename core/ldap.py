from core.config_manager import ConfigManager
from user_profile.models import UserProfile, Department
import ldap


class LDAPManager(object):

    def ldap_login(self, username, password):
        ldap_settings = ConfigManager().get_config('ldap')

        server_name = ldap_settings.get('host', '172.16.0.21')
        port = ldap_settings.get('port', 389)
        base_dn = ldap_settings.get('baseDN', 'ncc.local')
        dn = base_dn.split('.')
        dc = []
        for ns in dn:
            dc.append('dc={}'.format(ns))

        dn = ','.join(dc)

        l = ldap.initialize("ldap://{0}:{1}".format(server_name, port))
        # Bind/authenticate with a user with apropriate rights to add objects
        l.protocol_version = ldap.VERSION3
        l.set_option(ldap.OPT_REFERRALS, 0)
        bind_dn  = '{0}\{1}'.format(base_dn.split('.')[0], username)
        dn_password = password
        l.simple_bind_s(bind_dn, password)

        # The dn of our new entry/object
        user = l.search_ext_s(
            dn,
            ldap.SCOPE_SUBTREE,
            "(sAMAccountName={})".format(username),
            attrlist=[
                "sAMAccountName",
                "displayName",
                "mail",
                "distinguishedName",
                "telephoneNumber",
                "ipPhone",
                "home",
                "physicalDeliveryOfficeName"
            ]
        )

        user = self.format_user(user, username, password)

        if user is not None:
            user = self.get_or_create_user(user)

        return user

    def format_user(self, user, username, password):
        import time
        ts = '{}'.format(time.time()).split('.')
        data = None

        if len(user) > 0:
            data = {}
            cn, user = user[0]
            if username is None:
                username = user.get('sAMAccountName', None)
            if username is None:
               data['username']  = user.get('uid', None)[0]
            if password is None:
                data['password'] = 'password@1'

            fullname = user.get('displayName', ['NoneProvided NoName'])[0].split(' ')
            data['first_name'] = fullname[0]
            try:
                data['last_name'] = fullname[1]
            except IndexError:
                data['last_name'] = 'None'

            user_email = user.get('mail', None)
            phone = user.get('telephoneNumber', None)
            department_info = user.get('distinguishedName', None)
            work_phone = user.get('ipPhone', None)
            home_phone = user.get('home', None)
            department_floor = user.get('physicalDeliveryOfficeName', None)

            if phone is not None:
                data['phone'] = phone[0]
            else:
                data['phone'] = ts[0]

            if user_email is not None:
                data['email'] = user_email[0]
            else:
                data['email'] = 'mail{0}@vilogged.com'.format(ts[0])

            if department_info is not None:
                department_info = department_info[0].split(',')
                department_info = department_info[1].split('=')
                data['department'] = department_info[1]
            else:
                data['department'] = 'None'

            if work_phone is not None:
                data['work_phone'] = work_phone[0]

            if home_phone is not None:
                data['home_phone'] = home_phone[0]

            if department_floor is not None:
                data['floor'] = department_floor[0]

        return self.get_or_create_user(data)

    def get_or_create_user(self, data):

        try:
            user_instance = UserProfile.objects.get(username=data['username'])
            user_instance.first_name = data['first_name']
            user_instance.last_name = data['last_name']
            user_instance.email = data['email']
            user_instance.phone = data['phone']
            user_instance.work_phone = data['work_phone']
            user_instance.home_phone = data['home_phone']
            user_instance.department = self.get_or_create_department(data['department'], data['floor'])
            user_instance.save()
        except UserProfile.DoesNotExist:
            user_instance = UserProfile.objects.create_user(
                username=data['username'],
                password=data['password'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone=data['phone'],
                home_phone=data['home_phone'],
                work_phone=data['work_phone'],
                department=self.get_or_create_department(data['department'], data['floor']),
                is_active=True
            )
            user_instance.save()

        return UserProfile.objects.get(username=data['username'])

    def get_or_create_department(self, name, floor):
        try:
            department_instance = Department.objects.get(name=name, floor=floor)
        except Department.DoesNotExist:
            Department(
                name = name,
                floor=floor,
            ).save()

        return Department.objects.get(name=name, floor=floor)
