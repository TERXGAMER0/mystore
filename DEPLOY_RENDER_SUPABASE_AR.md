# تشغيل القالب على Render وSupabase

هذا القالب صار جاهزًا للعمل على:

- `Render` كخدمة ويب للبوت
- `Supabase` كقاعدة بيانات PostgreSQL
- بدون Redis إجباري

## قبل البدء

جهّز هذه الأشياء:

- توكن البوت من `@BotFather`
- رقمك في تيليجرام `Telegram ID`
- رابط حساب الدعم في تيليجرام مثل `https://t.me/username`
- كلمة مرور قوية لقاعدة البيانات في Supabase
- كلمة مرور قوية لدخول `SQLAdmin`
- مفتاح سري عشوائي لـ `WEBHOOK_SECRET_TOKEN`
- مفتاح سري عشوائي لـ `JWT_SECRET_KEY`

## 1. إنشاء مشروع Supabase

1. ادخل إلى لوحة Supabase.
2. اضغط `New project`.
3. اختر `Organization`.
4. اكتب `Project name`:
   `aiogram-shop-bot`
5. اكتب `Database Password`:
   اختر كلمة مرور قوية واحفظها.
6. اختر `Region`:
   اختر الأقرب لك.
7. اضغط `Create new project`.

بعد إنشاء المشروع:

1. افتح المشروع.
2. من الأعلى اضغط `Connect`.
3. ابحث عن `Session pooler`.
4. انسخ `connection string`.

مهم:

- استخدم `Session pooler` وليس `Direct connection`.
- السبب: `Session pooler` أنسب عندما تكون بيئة التشغيل تعتمد IPv4.

## 2. إنشاء خدمة Render

1. ارفع المشروع إلى GitHub.
2. ادخل إلى Render.
3. اضغط `New +`.
4. اختر `Web Service`.
5. اربط مستودع GitHub.
6. اختر المستودع الخاص بالقالب.

املأ الخانات كالتالي:

- `Name`: أي اسم تريده مثل `aiogram-shop-bot`
- `Region`: اختر الأقرب لك
- `Branch`: الفرع الذي عليه الكود
- `Root Directory`: اتركها فارغة
- `Runtime`: `Python 3`
- `Build Command`: `pip install -r requirements.txt`
- `Start Command`: `python run.py`
- `Instance Type`: اختر `Free`

خانة `Health Check Path`:

- ضع `/healthz`

## 3. متغيرات البيئة في Render

أضف هذه المتغيرات داخل `Environment Variables`:

- `TOKEN`
  ضع توكن البوت من BotFather

- `ADMIN_ID_LIST`
  ضع رقمك في تيليجرام
  إذا عندك أكثر من أدمن:
  `123456789,987654321`

- `SUPPORT_LINK`
  مثال:
  `https://t.me/your_username`

- `DATABASE_URL`
  ضع رابط `Session pooler` الذي نسخته من Supabase

- `WEBHOOK_SECRET_TOKEN`
  ضع أي نص سري طويل

- `SQLADMIN_RAW_PASSWORD`
  ضع كلمة مرور دخول لوحة الإدارة

- `JWT_SECRET_KEY`
  ضع نصًا سريًا طويلًا مختلفًا عن كلمة المرور

- `RUNTIME_ENVIRONMENT`
  `PROD`

- `WEBHOOK_PATH`
  `/webhook`

- `WEBAPP_HOST`
  `0.0.0.0`

- `SQL_ECHO`
  `false`

- `MULTIBOT`
  `false`

- `CURRENCY`
  `USD`

- `PAGE_ENTRIES`
  `8`

- `KRYPTO_EXPRESS_API_URL`
  `https://kryptoexpress.pro/api`

المتغيرات الاختيارية:

- `WEBHOOK_HOST`
  اتركه فارغًا
  التطبيق سيقرأ رابط Render تلقائيًا من `RENDER_EXTERNAL_URL`

- `REDIS_URL`
  اتركه فارغًا

- `REDIS_HOST`
  اتركه فارغًا

- `TELEGRAM_PROXY_URL`
  اتركه فارغًا إلا إذا كنت تحتاج بروكسي

## 4. أين تجد رابط البوت بعد النشر

بعد أول نشر ناجح في Render:

1. افتح الخدمة.
2. انسخ الرابط الأساسي للخدمة.
3. غالبًا سيكون مثل:
   `https://your-service-name.onrender.com`

لا تحتاج وضعه يدويًا في `WEBHOOK_HOST` إذا كنت على Render، لأن التطبيق يقرأه تلقائيًا.

## 5. تفعيل البوت

بعد حفظ المتغيرات:

1. اضغط `Create Web Service` أو `Manual Deploy`.
2. انتظر حتى ينتهي البناء.
3. إذا نجح التشغيل سترى في السجل:
   أن الخدمة اشتغلت وأن Telegram webhook تم ضبطه.

## 6. فحص الخدمة

افتح هذا الرابط:

- `https://your-service-name.onrender.com/healthz`

إذا ظهر:

```json
{"status":"ok"}
```

فهذا يعني أن خدمة الويب شغالة.

## 7. لوحة الإدارة SQLAdmin

بعد نجاح النشر افتح:

- `https://your-service-name.onrender.com/admin`

بيانات الدخول:

- اسم المستخدم: `admin`
- كلمة المرور: القيمة التي وضعتها في `SQLADMIN_RAW_PASSWORD`

## 8. ملاحظات مهمة

- إذا تركت `REDIS_URL` فارغًا فالبوت سيعمل بدون Redis.
- اللغة العربية صارت مدعومة داخل القالب.
- أول مستخدم موجود في `ADMIN_ID_LIST` سيظهر له زر الإدارة.
- إذا كنت تريد ميزات الدفع المشفر الكاملة، ستحتاج إعداد مفاتيح `KryptoExpress`.

## 9. إذا لم يعمل الاتصال مع Supabase

تأكد من التالي:

- أنك استخدمت `Session pooler`
- أنك وضعت الرابط كاملًا داخل `DATABASE_URL`
- أن كلمة مرور قاعدة البيانات صحيحة
- أن مشروع Supabase ليس `Paused`

## 10. أقل إعداد مطلوب للتشغيل

إذا كنت تريد أقل إعداد ممكن، فهذه أهم القيم:

```env
TOKEN=ضع_توكن_البوت
ADMIN_ID_LIST=ضع_رقم_تيليجرام_الخاص_بك
SUPPORT_LINK=https://t.me/your_username
DATABASE_URL=ضع_رابط_Supabase_Session_Pooler
WEBHOOK_SECRET_TOKEN=ضع_قيمة_سرية
SQLADMIN_RAW_PASSWORD=ضع_كلمة_مرور
JWT_SECRET_KEY=ضع_قيمة_سرية
RUNTIME_ENVIRONMENT=PROD
WEBHOOK_PATH=/webhook
WEBAPP_HOST=0.0.0.0
```
