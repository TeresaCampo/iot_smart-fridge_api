# SMART FRIDGE API

### 1. creare ambiente virtuale con conda

```bash
conda create -n iot_server python=3.12.4
```

### 2. da /iot_projects installare i requirements

```bash
 pip install -r requirements.txt
```

### 3. Rendere il proprio ip statico sulla rete locale(hotspot) per far funzionare MITApp Inventor

![Come assegnare ipv4 fisso al proprio pc dalle impostazioni (Ubuntu)](readme_resources/static_ipv4.png)
Impostare come ipv4 address: 172.20.10.4
Controllare la netmask con ifconfig
Gateway: 172.20.10

### 4. eseguire il server

```bash
python manage.py runserver 0.0.0.0:8080
```

### 5. controllare la documentazione alla pagina /api

http://172.20.10.4:8080/api/
