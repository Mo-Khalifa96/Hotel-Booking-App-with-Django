import logging

#Custom filter to exclude web-crawler 404 requests
class RequestsFilter(logging.Filter):
    def filter(self, record):
        request_paths = [
            #WordPress / CMS
            'wp-includes/', 'wp-admin/', 'wp-content/', 'wp-login.php',
            'xmlrpc.php', 'wp-config.php', 'wordpress/', 'feed/',
            'robots.txt', 'sitemap.xml', 'llms.txt', '/sellers.json',
            
            #PHPUnit exploit attempts
            '/vendor/phpunit/', '/phpunit/', '/lib/phpunit/',
            '/laravel/vendor/phpunit/', '/tests/vendor/phpunit/',
            '/test/vendor/phpunit/', '/testing/vendor/phpunit/',
            '/cms/vendor/phpunit/', '/crm/vendor/phpunit/',
            '/panel/vendor/phpunit/', '/public/vendor/phpunit/',
            '/apps/vendor/phpunit/', '/app/vendor/phpunit/',
            '/workspace/drupal/vendor/phpunit/', 'ads.txt', 'app-ads.txt'
            
            #Sensitive files / configs
            '.env', '/env', '/version', '/stats', '/index.php', '/index.html' '/public/index.php', '/security.txt', 
            '/.well-known/security.txt', '/config.json', '/server', '/about', '/debug/default/view', '/_all_dbs',
            
            #DNS over HTTPS
            '/dns-query', '/query', '/resolve',
            
            #VPN / RDP / Exchange probes
            '/dana-', '/dana-na/', '/dana-cached/', '/owa/', '/ecp/',
            '/RDWeb', '/Remote', '/wsman', 'sslvpnLogin', 
            'auth.html', 'auth1.html', '/api/sonicos/',
            
            #Misc scanning
            '/containers/json', '/login', '/hello.world',
            '/alive.php', '/developmentserver/metadatauploader',
            '/teorema505', '/aaa9', '/aab9', '/ab2g', '/ab2h',
            '/favicon.ico', '/wiki', 
        ]

        if hasattr(record, 'getMessage'):
            message = record.getMessage().lower()

            if 'not found' in message or '404' in message:
                return not any(path.lower() in message for path in request_paths)
            
            if 'disallowedhost' in message or 'disallowed host' in message:
                return False 

        return True

