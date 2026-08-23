# 💸 Dongi Bot

**Dongi** یک ربات تلگرام برای مدیریت هزینه‌های گروهی و محاسبه بدهی بین اعضای گروه است.

با استفاده از Dongi می‌توانید هزینه‌های مشترک را ثبت کنید، سهم هر شخص را مشخص کنید، بدهی‌ها را محاسبه و ساده‌سازی کنید و تسویه‌های انجام‌شده را ثبت کنید.

---

## ✨ قابلیت‌ها

* 👥 مدیریت اعضای گروه
* 💰 ثبت هزینه جدید
* ⚖️ تقسیم مساوی هزینه بین اعضا
* 🎯 تقسیم سفارشی هزینه
* 👤 مشخص کردن پرداخت‌کننده
* 📊 محاسبه خودکار بدهی و طلب اعضا
* 🔄 ساده‌سازی بدهی‌ها
* 💸 ثبت تسویه حساب
* 💳 پشتیبانی از تسویه کامل و جزئی
* 📋 مشاهده لیست هزینه‌ها
* 🔎 مشاهده جزئیات هر هزینه
* 🗑️ حذف هزینه
* 📈 گزارش کلی گروه
* 📊 مشاهده وضعیت شخصی
* 📚 راهنمای دستورات
* ⌨️ نمایش دستورات در منوی Telegram

---

## 🧠 نحوه محاسبه بدهی

Dongi برای هر شخص یک Balance محاسبه می‌کند.

اگر شخصی بیشتر از سهم خودش پرداخت کرده باشد، Balance او مثبت می‌شود:

```text
+500,000
```

یعنی این شخص **500,000 تومان طلبکار است**.

اگر شخصی کمتر از سهم خودش پرداخت کرده باشد، Balance او منفی می‌شود:

```text
-500,000
```

یعنی این شخص **500,000 تومان بدهکار است**.

سپس بدهکارها و طلبکارها با یک الگوریتم ساده به یکدیگر متصل می‌شوند تا تعداد تراکنش‌های لازم به حداقل برسد.

### مثال

فرض کنیم:

```text
پویا → علی : 500,000
علی → محمد : 250,000
```

به جای اینکه این دو بدهی جداگانه باقی بمانند، سیستم آن‌ها را ساده می‌کند:

```text
پویا → محمد : 250,000
```

---

## 🗂️ ساختار پروژه

ساختار پروژه به صورت کلی:

```text
Dongi/
│
├── handlers/
│   ├── expense.py
│   ├── expenses.py
│   ├── balance.py
│   ├── settle.py
│   ├── report.py
│   └── help.py
│
├── migrations/
│   ├── versions/
│   └── env.py
│
├── models.py
├── database.py
├── telegram_commands.py
├── main.py
├── requirements.txt
├── alembic.ini
├── .env
├── .gitignore
└── README.md
```

> نام بعضی فایل‌ها ممکن است با توجه به ساختار نهایی پروژه متفاوت باشد.

---

## 🛠️ تکنولوژی‌ها

این پروژه با استفاده از تکنولوژی‌های زیر ساخته شده است:

* Python
* Python Telegram Bot
* SQLAlchemy
* Alembic
* SQLite
* Telegram Bot API

---

# 🚀 نصب و اجرا

## 1. Clone کردن پروژه

```bash
git clone https://github.com/YOUR_USERNAME/dongi-bot.git
```

وارد پوشه پروژه شوید:

```bash
cd dongi-bot
```

---

## 2. ساخت Virtual Environment

در Windows:

```bash
python -m venv .venv
```

فعال کردن:

```bash
.venv\Scripts\activate
```

در Linux / macOS:

```bash
source .venv/bin/activate
```

---

## 3. نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

---

# 🔐 تنظیم Environment Variables

اطلاعات حساس پروژه نباید داخل GitHub قرار بگیرند.

یک فایل `.env` در ریشه پروژه ایجاد کنید:

```env
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
PROXY=YOUR_PROXY
```

اگر از Proxy استفاده نمی‌کنید، می‌توانید مقدار آن را خالی قرار دهید:

```env
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
PROXY=
```

### دریافت Bot Token

برای ساخت Bot و دریافت Token از **BotFather** در Telegram استفاده کنید.

> هرگز Bot Token را داخل GitHub Commit نکنید.

---

# 🗄️ Database

در نسخه فعلی پروژه از SQLite استفاده می‌شود.

نمونه:

```text
dongi.db
```

ساختار اصلی دیتابیس شامل جدول‌های زیر است:

```text
users
groups
group_members
expenses
expense_shares
settlements
```

### Users

اطلاعات کاربران Telegram را نگهداری می‌کند.

### Groups

اطلاعات گروه‌های Telegram را نگهداری می‌کند.

### Group Members

ارتباط کاربران با گروه‌ها را نگهداری می‌کند.

### Expenses

هزینه‌های ثبت‌شده را نگهداری می‌کند.

### Expense Shares

سهم هر کاربر از یک هزینه را نگهداری می‌کند.

### Settlements

تسویه‌های انجام‌شده بین کاربران را نگهداری می‌کند.

---

# 🔄 Database Migration

برای مدیریت تغییرات ساختار دیتابیس از Alembic استفاده شده است.

ساخت Migration جدید:

```bash
alembic revision --autogenerate -m "description"
```

اعمال Migration:

```bash
alembic upgrade head
```

مشاهده وضعیت Migration:

```bash
alembic current
```

مشاهده تاریخچه:

```bash
alembic history
```

---

# ▶️ اجرای Bot

بعد از تنظیم `.env`:

```bash
python main.py
```

اگر همه چیز درست باشد، Bot شروع به دریافت پیام‌های Telegram می‌کند.

---

# 🤖 دستورات Bot

## `/start`

ثبت کاربر و آماده‌سازی او برای استفاده از Bot.

---

## `/expense`

ثبت یک هزینه جدید.

فرآیند ثبت هزینه:

```text
عنوان هزینه
↓
مبلغ
↓
انتخاب پرداخت‌کننده
↓
انتخاب نوع تقسیم
↓
انتخاب اعضا
↓
ثبت سهم‌ها
```

---

## تقسیم مساوی

در حالت Equal، مبلغ هزینه به صورت مساوی بین افراد انتخاب‌شده تقسیم می‌شود.

مثلاً:

```text
مبلغ: 900,000

3 نفر:

پویا     300,000
علی      300,000
رضا      300,000
```

---

## تقسیم سفارشی

در حالت Custom، مقدار سهم هر شخص به صورت جداگانه مشخص می‌شود.

مثلاً:

```text
پویا     500,000
علی      250,000
رضا      150,000
```

مجموع سهم‌ها باید برابر با مبلغ کل هزینه باشد.

---

## `/balance`

نمایش بدهی‌های فعلی گروه.

مثلاً:

```text
📊 وضعیت بدهی‌ها

رضا → پویا : 250,000
علی → محمد : 400,000
```

سیستم بدهی‌ها را تا حد امکان ساده می‌کند.

---

## `/settle`

ثبت یک تسویه بین دو نفر.

مثلاً:

```text
/settle

رضا 250000
```

یعنی رضا مبلغ 250,000 تومان به فرد مشخص‌شده پرداخت کرده است.

تسویه‌ها در جدول `settlements` ذخیره می‌شوند و در محاسبه وضعیت مالی لحاظ می‌شوند.

---

## `/expenses`

نمایش هزینه‌های ثبت‌شده گروه.

مثلاً:

```text
📋 آخرین هزینه‌ها

🍔 شام - 850,000
⛽ بنزین - 300,000
🛒 خرید - 1,200,000
```

با انتخاب هر هزینه می‌توان جزئیات آن را مشاهده کرد.

---

## مشاهده جزئیات هزینه

جزئیات شامل:

```text
📝 عنوان
💰 مبلغ
👤 پرداخت‌کننده
📊 نوع تقسیم
👥 سهم هر شخص
```

است.

---

## حذف هزینه

ثبت‌کننده هزینه می‌تواند آن را حذف کند.

قبل از حذف بهتر است تأیید کاربر دریافت شود تا از حذف اشتباهی جلوگیری شود.

---

## `/report`

نمایش گزارش کلی گروه.

اطلاعات گزارش شامل مواردی مانند:

```text
💰 کل هزینه‌ها
🧾 تعداد هزینه‌ها
🏆 بیشترین پرداخت
📉 کمترین پرداخت
💸 بیشترین بدهکار
💵 بیشترین طلبکار
```

---

## `/me`

نمایش وضعیت مالی شخص فعلی.

این بخش برای نمایش بدهی‌ها و طلب‌های مربوط به خود کاربر استفاده می‌شود.

---

## `/help`

نمایش راهنمای کامل دستورات Bot.

---

# ⌨️ Telegram Command Menu

دستورات Bot در Telegram نیز ثبت می‌شوند.

بنابراین کاربر با وارد کردن:

```text
/
```

می‌تواند لیست دستورات موجود را مشاهده کند.

این Commandها توسط `set_my_commands` تنظیم می‌شوند.

---

# 🌐 Deploy روی Render

برای اجرای دائمی Bot می‌توان از Render استفاده کرد.

از آنجایی که این پروژه یک Telegram Bot است، نوع سرویس مناسب:

```text
Background Worker
```

است.

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
python main.py
```

---

## Environment Variables در Render

توکن را داخل GitHub قرار ندهید.

در Render قسمت:

```text
Environment Variables
```

مقادیر زیر را اضافه کنید:

```text
BOT_TOKEN = YOUR_TELEGRAM_BOT_TOKEN
PROXY = YOUR_PROXY
```

Render این متغیرها را هنگام اجرای برنامه در اختیار Python قرار می‌دهد.

بنابراین کد می‌تواند از:

```python
import os

TOKEN = os.getenv("BOT_TOKEN")
```

استفاده کند.

---

# ⚠️ نکته مهم درباره SQLite روی Render

نسخه فعلی پروژه از SQLite استفاده می‌کند.

SQLite برای تست و توسعه مناسب است، اما برای استفاده Production روی سرویس‌های Cloud انتخاب ایده‌آلی نیست.

دلیل اصلی این است که فایل دیتابیس:

```text
dongi.db
```

روی فایل‌سیستم سرویس قرار می‌گیرد و نباید روی آن به عنوان یک دیتابیس دائمی و Production حساب کرد.

برای نسخه Production پیشنهاد می‌شود دیتابیس به:

```text
PostgreSQL
```

مهاجرت داده شود.

ساختار پروژه با SQLAlchemy این مهاجرت را ساده‌تر می‌کند.

---

# 🔒 امنیت

اطلاعات زیر نباید داخل GitHub قرار بگیرند:

```text
BOT_TOKEN
API Keys
Passwords
Database Credentials
.env
```

بنابراین در `.gitignore` قرار دهید:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

اگر دیتابیس SQLite را هم نمی‌خواهید روی GitHub قرار دهید:

```gitignore
*.db
*.sqlite3
```

---

# 🧪 وضعیت پروژه

نسخه فعلی در مرحله MVP قرار دارد.

قابلیت‌های اصلی مدیریت هزینه و بدهی پیاده‌سازی شده‌اند.

### Completed

* [x] Telegram Bot
* [x] User management
* [x] Group management
* [x] Expense creation
* [x] Equal split
* [x] Custom split
* [x] Expense shares
* [x] Balance calculation
* [x] Balance simplification
* [x] Settlement
* [x] Partial settlement
* [x] Expense history
* [x] Expense details
* [x] Expense deletion
* [x] Group report
* [x] Help command
* [x] Telegram command menu
* [x] Alembic migrations

### Planned

* [ ] Personal report
* [ ] Delete confirmation
* [ ] Export report
* [ ] PostgreSQL support
* [ ] Better error handling
* [ ] Admin management
* [ ] Expense editing
* [ ] Improved UI/UX
* [ ] Production deployment
* [ ] Automated tests

---

# 📌 مثال ساده

فرض کنید سه نفر در یک گروه هستند:

```text
پویا
علی
رضا
```

پویا یک هزینه 900,000 تومانی ثبت می‌کند و هزینه بین هر سه نفر مساوی تقسیم می‌شود:

```text
پویا پرداخت کرده: 900,000

سهم پویا: 300,000
سهم علی: 300,000
سهم رضا: 300,000
```

در نتیجه:

```text
علی → پویا : 300,000
رضا → پویا : 300,000
```

اگر بعداً پویا 300,000 تومان برای هزینه دیگری به جای علی پرداخت کند، سیستم می‌تواند بدهی‌ها را ساده کند و تعداد پرداخت‌های لازم را کاهش دهد.

---

# 👨‍💻 Development

برای ایجاد تغییر در دیتابیس:

```bash
alembic revision --autogenerate -m "your change"
```

سپس:

```bash
alembic upgrade head
```

قبل از Push کردن تغییرات:

```bash
git status
git add .
git commit -m "your commit message"
git push
```

---

# 📄 License

این پروژه در حال توسعه است.

در صورت نیاز می‌توان در نسخه نهایی یک License مناسب مانند MIT اضافه کرد.

---

## 🚀 Roadmap

هدف پروژه تبدیل شدن به یک سیستم کامل مدیریت هزینه‌های گروهی است:

```text
Telegram
   │
   ▼
Dongi Bot
   │
   ├── Users
   ├── Groups
   ├── Expenses
   ├── Custom Shares
   ├── Balances
   ├── Settlements
   └── Reports
           │
           ▼
      PostgreSQL
           │
           ▼
        Render
```

---
