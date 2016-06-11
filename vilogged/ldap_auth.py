from vilogged.config_manager import ConfigManager
from vilogged.department.models import Department
from vilogged.users.models import UserProfile
from utility.utility import Utility
import ldap


class LDAPManager(object):

    def ldap_login(self, username, password):
        ldap_settings = ConfigManager().get_config('ldap')
        error = None
        user_data = None
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
        try:
            l.simple_bind_s(bind_dn, password)
        except (ldap.AUTH_UNKNOWN, ldap.CONNECT_ERROR) as e:
            error = e
        except ldap.INVALID_CREDENTIALS as e:
            error = 'Invalid Credentials Provided'
        except ldap.SERVER_DOWN:
            error = 'LDAP Server Down'
        except ldap.LDAPError as e:
            error = e
        else:

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
                    "physicalDeliveryOfficeName",
                    "department"
                ]
            )

            user = self.format_user(user, username, password)

            if user is not None:
                user = self.get_or_create_user(user)

            user_data = user
        if error:
            return dict(authenticated=False, reason=error, user=None)
        else:
            return dict(authenticated=True, user=user_data, reason=None)

    def format_user(self, user, username, password):
        import time
        ts = '{}'.format(time.time()).split('.')
        data = None
        if len(user) > 0:
            data = dict()
            cn, user = user[0]
            data['username'] = username
            data['password'] = password
            fullname = user.get('displayName', ['NoneProvided NoName'])[0].split(' ')
            data['first_name'] = fullname[0]
            try:
                data['last_name'] = fullname[1]
            except IndexError:
                data['last_name'] = 'None'
            if len(fullname) > 2:
                data['last_name'] = fullname[2]

            user_email = user.get('mail', None)
            phone = user.get('telephoneNumber', None)
            department_info = user.get('distinguishedName', None)
            department_name = user.get('department')
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
            if department_name:
                data['department'] = department_name[0]

            if work_phone is not None:
                data['work_phone'] = work_phone[0]

            if home_phone is not None:
                data['home_phone'] = home_phone[0]

            if department_floor is not None:
                data['floor'] = department_floor[0]

        return data

    def get_or_create_user(self, data):
        users = UserProfile.objects.filter(username=data.get('username'))
        if users:
            user_instance = users[0]
            user_instance.first_name = data.get('first_name')
            user_instance.last_name = data.get('last_name')
            user_instance.email = data.get('email')
            user_instance.work_phone = data.get('work_phone')
            user_instance.home_phone = data.get('home_phone')
            user_instance.department = self.get_or_create_department(data.get('department'), data.get('floor'))
            user_instance.save()
        else:
            user_instance = UserProfile.objects.create_user(
                username=data.get('username'),
                password=data.get('password'),
                email=data.get('email'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                phone=data.get('phone'),
                home_phone=data.get('home_phone'),
                work_phone=data.get('work_phone'),
                department=self.get_or_create_department(data.get('department'), data.get('floor')),
                is_active=True
            )
            user_instance.save()

        return user_instance

    def get_or_create_department(self, name, floor):
        if name:
            try:
                Department.objects.get(name=name, floor=floor)
            except Department.DoesNotExist:
                Department(
                    name = name,
                    floor=floor,
                ).save()

            return Department.objects.get(name=name, floor=floor)
        return None
