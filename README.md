# 🏪 BOT Store - بوت المتجر الاحترافي على تيليجرام

> بوت متجر متكامل بـ Python + Supabase + Oracle Cloud

---

## 📁 هيكل المشروع

```
BOT Store/
├── bot.py                  ← نقطة البداية (شغّل هذا)
├── config.py               ← الإعدادات (يقرأ من .env)
├── requirements.txt        ← المكتبات المطلوبة
├── .env.example            ← نموذج متغيرات البيئة
├── .env                    ← ملفك الخاص (لا ترفعه!)
├── .gitignore
│
├── database/
│   ├── db.py               ← الاتصال بـ Supabase
│   └── queries.py          ← كل استعلامات البيانات
│
├── handlers/
│   ├── user_handlers.py    ← معالجات المستخدم العادي
│   ├── product_handlers.py ← عرض المنتجات والشراء
│   └── admin_handlers.py   ← لوحة تحكم الأدمن
│
└── utils/
    └── keyboards.py        ← كل لوحات المفاتيح
```

---

## 🚀 خطوات التثبيت والتشغيل

### الخطوة 1: إنشاء البوت
1. افتح تيليجرام وابحث عن **@BotFather**
2. أرسل `/newbot` واتبع التعليمات
3. احتفظ بالـ **Token** الذي يعطيك إياه

### الخطوة 2: معرفة الـ Admin ID
1. افتح **@userinfobot** في تيليجرام
2. ستجد معرفك الرقمي (مثل: `123456789`)

### الخطوة 3: إنشاء قاعدة البيانات في Supabase
1. اذهب إلى [supabase.com](https://supabase.com) وأنشئ حساباً مجانياً
2. أنشئ **Project** جديد
3. من القائمة الجانبية اختر **SQL Editor**
4. انسخ الـ SQL الموجود في `database/db.py` (متغير `SETUP_SQL`) وشغّله
5. من **Settings > API** احتفظ بـ:
   - `Project URL`
   - `anon public key`

### الخطوة 4: إعداد ملف `.env`
```bash
# انسخ الملف النموذجي
cp .env.example .env

# عدّل القيم بمحرر النصوص
nano .env
```

عبّئ هذه القيم:
```env
BOT_TOKEN=توكن_البوت_من_BotFather
ADMIN_ID=معرفك_الرقمي
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=مفتاح_anon_من_Supabase
STORE_NAME=🏪 اسم متجرك
STORE_CURRENCY=ريال
POINTS_PER_PURCHASE=10
```

### الخطوة 5: تثبيت المكتبات
```bash
pip install -r requirements.txt
```

### الخطوة 6: تشغيل البوت
```bash
python bot.py
```

---

## ☁️ التشغيل على Oracle Cloud (Ubuntu)

```bash
# 1. تحديث النظام
sudo apt update && sudo apt upgrade -y

# 2. تثبيت Python
sudo apt install python3 python3-pip -y

# 3. رفع ملفات المشروع (عبر SCP أو Git)
git clone رابط_مشروعك
cd "BOT Store"

# 4. تثبيت المكتبات
pip3 install -r requirements.txt

# 5. إنشاء ملف .env
nano .env

# 6. تشغيل البوت في الخلفية (يستمر بعد إغلاق SSH)
nohup python3 bot.py > bot.log 2>&1 &

# لمشاهدة اللوج
tail -f bot.log

# لإيقاف البوت
pkill -f bot.py
```

### تشغيل تلقائي عند إعادة التشغيل (systemd)
```bash
# إنشاء ملف الخدمة
sudo nano /etc/systemd/system/storebot.service
```

```ini
[Unit]
Description=Telegram Store Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/BOT Store
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable storebot
sudo systemctl start storebot
sudo systemctl status storebot
```

---

## 📱 الميزات

### للمستخدم
| الميزة | الوصف |
|--------|-------|
| 🛒 تصفح المنتجات | عرض المنتجات مع صورة وأزرار التنقل |
| 🔍 تفاصيل المنتج | عرض وصف كامل وسعر ومخزون |
| 🛍️ الشراء | تأكيد الشراء بضغطة واحدة |
| 💰 نقاط | رصيد نقاط يزيد مع كل شراء |

### للأدمن (لوحة التحكم)
| الأمر | الوصف |
|-------|-------|
| `/admin` | فتح لوحة التحكم |
| 📢 إذاعة | إرسال رسالة/صورة لكل المستخدمين |
| ➕ إضافة منتج | إضافة منتج جديد خطوة بخطوة |
| 🗑️ حذف منتج | حذف منتج بالـ ID |
| ✏️ تعديل الترحيب | تغيير رسالة الترحيب |
| 🎯 إضافة نقاط | منح/خصم نقاط لمستخدم |
| 📊 إحصائيات | عدد المستخدمين والمنتجات والطلبات |

---

## 🔒 الأمان
- ✅ التوكن وبيانات DB في متغيرات بيئية فقط
- ✅ لوحة الأدمن تُفتح فقط للـ Admin ID المحدد
- ✅ معالجة الأخطاء تمنع توقف البوت
- ✅ أضف `.env` إلى `.gitignore` دائماً

---

## 🔮 تطويرات مستقبلية
- [ ] بوابة دفع إلكتروني (Stripe / PayPal)
- [ ] نظام كوبون وخصومات
- [ ] تصنيفات للمنتجات
- [ ] لوحة إحصائيات متقدمة
- [ ] نظام تقييم المنتجات
- [ ] دعم متعدد اللغات
- [ ] نظام الإشعارات التلقائية
