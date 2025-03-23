# **UbLite – Lightweight Telegram Userbot**  

**UbLite** is a **fast, lightweight, and efficient** Telegram userbot built using **Telethon**. Originally developed as a private userbot in **2020**, UbLite is now being made public with carefully refined features for automation and convenience.  

---

## 🚀 Features  
UbLite currently includes essential automation tools, with more features being added soon:  

- ✅ **Auto-translate** (Google API)  
- ✅ **Sticker pack cloning**  
- ✅ **Manage GIFs** (add/remove from recent GIFs Cloud)  
- ✅ **Message JSON viewer**  
- ✅ **Fun commands**  
- ✅ **Purge messages**  
- ✅ **High-speed message forwarding** (x chat to y)  
- ✅ **Google web search**  
- ✅ **SDM (Self Destruct Message Saver)**  
- ✅ …and many more coming soon!  

---

## ⚙️ Installation  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/ankit-chaubey/UbLite.git  
cd UbLite
```

2️⃣ Install Dependencies

```
pip install -r requirements.txt
```

3️⃣ Set Up Environment Variables

Create a .env file or set the following environment variables:

```
API_ID=your_api_id  
API_HASH=your_api_hash
ONWER_ID=your_user_id
```

> 📌 Note: You don't need to generate a telethon session before running UbLite it'll be automatically handled.



4️⃣ Run the Userbot

```
python3 UbLite.py
```


---

🔧 Configuration

UbLite allows customization through a config.py file. Modify settings to adjust features as per your needs.


---

## **🔹 Command Guide for UbLite Userbot**  

### **🗑 Purge Commands**  

| Command | Description | Example | Output |
|---------|------------|---------|--------|
| `.purge <number>` | Deletes the specified number of messages or all messages after a replied message | `.purge 10` | Deletes 10 messages |
| `.purgeme <number>` | Deletes your own messages (by count or after a replied message) | `.purgeme 5` | Deletes 5 of your own messages |
| `.purgeall` | Deletes all messages from the replied user's chat history | `.purgeall` (reply to a message) | Deletes all messages from the user |

---

### **🎥 GIF Commands**  

| Command | Description | Example | Output |
|---------|------------|---------|--------|
| `.gif sendall <@username or chat_id>` | Sends all saved GIFs to a user or chat | `.gif sendall @username` | Sends all saved GIFs |
| `.gif deleteall` | Deletes all GIFs in your saved GIFs | `.gif deleteall` | Removes all GIFs |
| `.gif addall <@username or chat_id>` | Saves all GIFs from a specific chat to your GIF collection | `.gif addall @username` | Adds all GIFs from the chat |
| `.gif help` | Displays help for GIF commands | `.gif help` | Shows GIF commands |

---

### **🎨 Sticker Commands**  

| Command | Description | Example | Output |
|---------|------------|---------|--------|
| `.clone <sticker_url> <shortname_for_pack> <pack_name>` | Clones a sticker pack | `/clone https://t.me/addstickers/SamplePack mypack My Pack` | Clone the sticker pack and make your own pack |

---

### **📤 Forwarding Messages**  

| Command | Description | Example | Output |
|---------|------------|---------|--------|
| `.fwd <start_msg_id> <end_msg_id> <msgs_per_sec> <source_chat_id> <dest_chat_id>` | Forwards messages in bulk from one chat to another | `.fwd 100 200 5/sec 123456789 987654321` | Forwards messages from chat 123456789 to 987654321 |

---

### **📢 Spam Commands**  

| Command | Description | Example | Output |
|---------|------------|---------|--------|
| `.spam <number> <message>` | Sends a message multiple times | `.spam 5 Hello` | Sends "Hello" five times |
| `.delayspam <number> <message> <delay>` | Sends a message multiple times with a delay | `.delayspam 5 Hello 2` | Sends "Hello" five times with a 2-second delay |

---

### **📜 JSON Command**  

| Command | Description | Example | Output |
|---------|------------|---------|--------|
| `.json` | Replies with the raw JSON of a message | `.json` (reply to a message) | Displays message JSON |

---

### **🌍 Auto-Translation Commands**  

| Command | Description | Example | Output |
|---------|------------|---------|--------|
| `.t-lang text` | Auto-detect source language & translate to `lang` | `.t-en नमस्ते` | `Hello` |
| `.t-from:to text` | Translate from `from` language to `to` language | `.t-hi:en मेरा नाम अंकित है` | `My name is Ankit` |
| `.t-fr How are you?` | Translate to French | `.t-fr How are you?` | `Comment ça va ?` |
| `.t-es I love programming` | Translate to Spanish | `.t-es I love programming` | `Me encanta programar` |

📌 **Language Codes:**  
- `en` → English  
- `hi` → Hindi  
- `fr` → French  
- `es` → Spanish  
- **[Full list of supported languages](https://cloud.google.com/translate/docs/languages)**  

🚀 **Now you can translate messages instantly on Telegram!**  

---

### **💡 Explanation of Features**  

- **Purge Messages** – Quickly delete multiple messages from chats.  
- **GIF Management** – Save, delete, and send GIFs automatically.  
- **Sticker Cloning** – Copy any sticker pack to your account.  
- **Bulk Forwarding** – Forward messages from one chat to another in bulk.  
- **Spam Automation** – Auto-send messages multiple times.  
- **JSON Message Debugging** – Extract raw message data in JSON format.  
- **Auto-Translation** – Translate messages in any Telegram chat.  

💡 **UbLite is constantly improving!** Stay tuned for more features and updates. 🚀

---

🤝 Contributing

Want to help improve UbLite? Fork the repo, make changes, and submit a PR!

For any issues or suggestions, feel free to open an issue.

---

## **👨‍💻 Creator**  
This project is built by **[Ankit Chaubey](https://github.com/ankit-chaubey)**
- 📬 **Telegram:** [@ankify](https://t.me/ankify)
- 📧 **Email:** [📨📨📨📨](mailto:m.ankitchaubey@gmail.com)

---

🚀 UbLite – Light, Fast, and Smart Userbot!
