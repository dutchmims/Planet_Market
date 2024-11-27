from django.core.mail.backends.smtp import EmailBackend as BaseEmailBackend

class EmailBackend(BaseEmailBackend):
    def open(self):
        """
        Ensures we can open a connection to the SMTP server without SSL/TLS-specific arguments
        that might cause compatibility issues.
        """
        if self.connection:
            return False

        connection_kwargs = {}
        if self.timeout is not None:
            connection_kwargs['timeout'] = self.timeout
        
        try:
            self.connection = self.connection_class(self.host, self.port, **connection_kwargs)
            
            if self.use_tls:
                self.connection.starttls()
            
            if self.username:
                self.connection.login(self.username, self.password)
            
            return True
        except:
            if not self.fail_silently:
                raise
