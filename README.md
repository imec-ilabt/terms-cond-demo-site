# terms-cond-demo-site
Terms &amp; Conditions Demo Site

Files:
- nginx-conf: A demo nginx config file, which serves the frontend and proxies to the backend webapi.
- www: The frontend of the web site. This is intentionally kept very simple.
- python_tc_api: A demo web API that stores the user consent in a sqlite DB. This uses python flask.
 
Assumptions made in `nginx-conf`:
- Your domain is example.com (obviously, you need to change this)
- You are using certbot (to request Let's encrypt SSL certificates)
- Your tc_api is using port 8042
- Your TC website is stored at `/var/www/termscond` and the main file is `terms_conditions.html`
- The wall2 PEM file is stored at `/etc/wall2.pem` (this is used to only allow authenticated users of the fed4fire authority)
- You are using at least nginx version 1.13.5. (This is required for `$ssl_client_escaped_cert`) (on debian stretch, this means you need to use `stretch-backports`)
- nginx server the website and API on port 443 (and redirects port 80 to 443)
- The API is served at https://example.com/api/terms_and_cond/v1.0/  (replace example.com by your domain name)
