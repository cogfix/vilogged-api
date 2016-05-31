from django.core.mail.backends.smtp import EmailBackend
from vilogged.config_manager import ConfigManager



class ViloggedEmailBackend(EmailBackend):

    def __init__(self, host=None, port=None, username=None, password=None,
                 use_tls=None, fail_silently=False, use_ssl=None, timeout=None,
                 ssl_keyfile=None, ssl_certfile=None,
                 **kwargs):

        config = ConfigManager().get_config('email')
        backend = EmailBackend(
            host=config.get('host', 'vms@vilogged.com'),
            port=config.get('port', ''),
            username=config.get('username', 'vms@vilogged.com'),
            password=config.get('password', 'password'),
            use_tls=config.get('use_tls'),
            fail_silently=False,
            use_ssl=config.get('use_ssl'),
            timeout=config.get('timeout'),
            ssl_keyfile=config.get('ssl_keyfile'),
            ssl_certfile=config.get('ssl_certfile')
        )

        super(EmailBackend, self).__init__(fail_silently=fail_silently)
        self.host = host or settings.EMAIL_HOST
        self.port = port or settings.EMAIL_PORT
        self.username = settings.EMAIL_HOST_USER if username is None else username
        self.password = settings.EMAIL_HOST_PASSWORD if password is None else password
        self.use_tls = settings.EMAIL_USE_TLS if use_tls is None else use_tls
        self.use_ssl = settings.EMAIL_USE_SSL if use_ssl is None else use_ssl
        self.timeout = settings.EMAIL_TIMEOUT if timeout is None else timeout
        self.ssl_keyfile = settings.EMAIL_SSL_KEYFILE if ssl_keyfile is None else ssl_keyfile
        self.ssl_certfile = settings.EMAIL_SSL_CERTFILE if ssl_certfile is None else ssl_certfile
        if self.use_ssl and self.use_tls:
            raise ValueError(
                "EMAIL_USE_TLS/EMAIL_USE_SSL are mutually exclusive, so only set "
                "one of those settings to True.")
        self.connection = None
        self._lock = threading.RLock()