# NAS (Network Attached Storage) with Global Access

This project sets up a Network Attached Storage (NAS) solution using a Raspberry Pi 5 (8GB RAM) running Kali Linux. The NAS allows you to mount and share a selected partition from an external storage device, making it accessible over the local network—or globally via Ngrok tunneling.

---

## 🧰 Features

- 📁 Mount and share any partition from an external USB storage device
- 🌐 Access NAS over local network or globally with Ngrok
- 🧠 User selects the partition to mount at runtime
- 🔐 Secure and simple configuration

---

## 📦 Requirements

- Raspberry Pi 5 with Kali Linux installed
- External USB storage device
- Internet connection (for Ngrok)
- Ngrok account & authtoken

---

## 🚀 Setup Instructions

### 1. **Connect Your Storage**
Plug in your external storage device (HDD/SSD) to the Raspberry Pi via USB.

### 2. **Clone the Repository**
```bash
sudo apt update
sudo apt upgrade -y
git clone https://github.com/RajatKundu853/Network-Attached-Storage.git
cd Network-Attached-Storage
chmod +x *
./nas.sh
```
It will create a directory named "NAS"

You'll be prompted to select which partition to mount (e.g., /dev/sda1, sdb2, etc.)

Select the partition of external storage device

The selected partition will be mounted to a shared NAS directory

### Now you can access your NAS on your local host's port no 8000 ( http://127.0.0.1:8000 )

### Now,if you only access it in local network then go http://<raspbery_pi's private ip>:8000  (e.g., http://192.168.1.112:8000)

Default User ID: admin  ,  Password: password123


## Access NA$hield globally -- using ngrok tunneling
Open a new terminal.
```bash
./nas.sh
```
#### Follow the instruction on terminal---
1. Visit the Ngrok website: https://dashboard.ngrok.com/get-started/your-authtoken
   
3. Sign up or log in to your Ngrok account.
   
5. Copy your personal Auth Token from the dashboard.
   
7. Paste the token below when prompted.

### Now it will give you a url which work on globally.



## 🛡️ Security Note
### For safe global sharing:
Set strong passwords for your NAS access

Use Ngrok authentication or access control features

Avoid sharing sensitive or personal data without encryption

## 🙌 Author
### Rajat Kundu.


