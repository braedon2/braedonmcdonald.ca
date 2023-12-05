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