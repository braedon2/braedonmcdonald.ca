# Server setup

install nginx and vim 
```
sudo apt-get install nginx
sudo apt-get install vim
```

start nginx
```
sudo systemctl start nginx
```

start nginx on boot
```
sudo systemctl enable nginx
```

copy the configuration into `/etx/nginx/sites-available/braedoncmdonald.conf`
```
server {
	listen 80;
	listen [::]:80;

	root /home/braedonmcdonald/braedonmcdonald.ca;
	index index.html;

	location / {
		try_files $uri $uri/ =404;
	}
}
```

link the configuration to `sites-enabled`
```
sudo ln -s /etc/nginx/sites-available/braedonmcdonald.conf /etc/nginx/sites-enabled/
```

remove the default configuration from `sites-enabled`

reload nginx
```
sudo systemctl reload nginx
```

download the dynamic dhcp script
```
git clone https://github.com/timothymiller/cloudflare-ddns.git
```

copy the example config
```
cp config-example.json config.json
```

go to your cloudflare profile and copy the api key and set the fields. Delete the `api_token` field. Unset `api_token`
```
"authentication":
  "api_token": "",
  "api_key":
    "api_key": "Your cloudflare API Key",
    "account_email": "The email address you use to sign in to cloudflare",
```

add this
```
"zone_id": "5d7737fbbe6156472649f4fe94be5163",
"subdomains": [
{
	"name": "",
	"proxied": true
},
{
	"name": "www",
	"proxied": true
}
]
```

disable aaaa records
```
"aaaa": false
```

change permission of script
```
chmod +x cloudflare-ddns.py
```

make sure script doesn't give errors
```
./cloudflare-ddns.py
```

run `crontab -e` and add the job
```
*/10 * * * * /home/braedonmcdonald/cloudflare-ddns/cloudflare-ddns.py
```