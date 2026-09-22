# oldfox.uz — shaxsiy sayt (Django)

Qaymoqrang, klassik tipografikaga asoslangan shaxsiy sayt: bosh sahifa
(slayder bilan), rezyume, papkalar ko'rinishidagi portfolio, maqolalar va
aloqa sahifasi. Kirgan (login qilgan) foydalanuvchi sahifalarning o'zida
tahrirlash tugmalarini ko'radi.

## Ishga tushirish

```bash
.venv/bin/python manage.py runserver
```

Sayt: http://127.0.0.1:8000/ · Boshqaruv: `/manage/` · Django admin: `/admin/`

Yangi muhitda noldan:

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py seed_demo   # namunaviy ma'lumot (ixtiyoriy)
```

## Tuzilishi

| Papka | Vazifasi |
|---|---|
| `config/` | Sozlamalar, URL'lar (`manage_urls.py` — tahrirlash sahifalari) |
| `core/` | Profil, tajriba, ta'lim, ko'nikma, til, yutuq, slayder, xabarlar |
| `core/richtext.py` | Boy matn maydoni, Quill widget'i va HTML tozalagich (nh3) |
| `core/widgets.py` | Rasm maydonlari uchun kesish (crop) widget'i |
| `core/ai.py` | Gemini bilan matnni tozalash (tashqi kutubxonasiz REST) |
| `portfolio/` | Papkalar (`Folder`) va loyihalar (`Project`, `ProjectImage`) |
| `blog/` | Maqolalar (`Article`) |
| `templates/` | Barcha shablonlar; `widgets/richtext.html` — muharrir |
| `static/css/site.css` | Butun dizayn tizimi (ranglar, tipografika, papkalar) |

## Sahifalar

- `/` — bosh sahifa: slayder, “Men haqimda”, so'nggi maqolalar, tanlangan ishlar
- `/rezyume/` — to'liq rezyume (chop etish uchun ham moslangan)
- `/portfolio/` — papkalar; `/portfolio/<papka>/` — ichidagi loyihalar
- `/portfolio/loyiha/<slug>/` — loyiha maqolasi (boy matn)
- `/maqolalar/` — maqolalar ro'yxati; `/maqolalar/<slug>/` — maqola
- `/aloqa/` — bog'lanish shakli; xabarlar `/manage/xabarlar/` da
- `/kirish/` — egasi uchun kirish

## Tahrirlash

Kirgandan so'ng yuqorida qora “Tahrir rejimi” paneli chiqadi va har bir bo'lim
yonida kichik *tahrir* tugmalari paydo bo'ladi. Loyiha va maqola matni Quill
muharririda yoziladi: sarlavhalar, ro'yxatlar, iqtiboslar, kod bloklari, jadval, video va
rasmlar. Rasmni muharrir ichiga tortib tashlash yoki nusxadan qo'yish mumkin —
u `media/editor/` ga yuklanadi.

Saqlashda HTML `nh3` orqali tozalanadi (faqat ruxsat etilgan teg, atribut va
CSS xossalari qoladi), shuning uchun muharrirdagi matn XSS keltirib chiqarmaydi.

### Rasmlarni kesish

Har bir rasm maydonida fayl tanlangach kesish oynasi ochiladi: rasmni surish,
sichqoncha g'ildiragi yoki slayder bilan kattalashtirish mumkin. Har bir joy
uchun mos nisbat oldindan tanlangan bo'ladi:

| Joy | Nisbat |
|---|---|
| Profil surati | 1:1 |
| Bosh sahifa slayderi | 21:9 |
| Loyiha va maqola muqovasi | 16:9 |
| Papka muqovasi, loyiha galereyasi | 3:2 |
| Matn ichidagi rasmlar | asl nisbat |

Nisbatni 1:1, 4:3, 16:9 yoki asl holatga almashtirish, “Asl holida qoldirish”
tugmasi bilan kesmasdan yuklash, saytda turgan rasmni esa “Qayta kesish”
tugmasi bilan qaytadan sozlash mumkin. Kesish brauzerda bajariladi —
serverga allaqachon kerakli o'lchamdagi rasm boradi.

### Matnni Gemini bilan tozalash

`.env` ga kalit qo'yilgan bo'lsa, boy matn muharriri tepasida ikkita tab
va **“✦ Imlo va formatni tuzatish”** tugmasi paydo bo'ladi:

| Tab | Nimani ko'rsatadi |
|---|---|
| **Asl matn** | Siz yozgan matn — Quill muharriri |
| **Tuzatilgan** | Gemini qaytargan variant (faqat o'qish uchun) |

Tugma bosilgach matn Gemini'ga yuboriladi: imloviy xatolar tuzatiladi, gaplar
ravon qilinadi, matn bandlarga, sarlavhalarga va ro'yxatlarga ajratiladi.
Natija yoqsa **“Shu matnni qo'yish”** bosiladi — matn muharrirga ko'chadi va
pastda **“Avvalgi matnni qaytarish”** havolasi chiqadi. Saqlanmaguncha hech
narsa o'zgarmaydi.

Sozlamalar `.env` da:

```
GEMINI_API_KEY=...            # https://aistudio.google.com/apikey
GEMINI_MODEL=gemini-2.5-flash
GEMINI_TIMEOUT=90
DJANGO_ASSIST_RATE_LIMIT=40   # bitta foydalanuvchi uchun soatiga
```

Kalit bo'lmasa tugma ham, tablar ham umuman chiqmaydi — sayt oddiy holatda
ishlayveradi. Model javobi ham ishonchsiz manba deb qaraladi: muharrirga
qo'yilishidan oldin `nh3` bilan tozalanadi.

### Bosh sahifa slayderi

`/manage/slayd/yangi/` — rasm, sarlavha, qo'shimcha matn va havola. Havola
ichki yo'l (`/portfolio/`) yoki to'liq manzil bo'lishi mumkin. Tartibni `order`
maydoni belgilaydi, `Ko'rsatilsin` belgisini olib tashlasangiz slayd yashiriladi.
Slaydlar 7 soniyada almashadi; sichqoncha ustiga kelganda to'xtaydi.

Har bir slaydning ko'rinishi alohida sozlanadi va forma ichidagi **jonli
ko'rinishda** darhol aks etadi:

| Sozlama | Nima qiladi |
|---|---|
| Karta tomoni | Sarlavha kartasi chapda yoki o'ngda turadi |
| Karta uslubi | Yorug' shisha, to'q shisha yoki shaffofsiz qog'oz |
| Karta ortidagi xiralik | Karta ostidagi rasm qanchalik xiralashadi (0–40 px) |
| Rasmning shu tomonidagi xiralik | Karta turgan tomonni xiralashtirish (0–40 px) |
| Xira maydon kengligi | Rasmning necha foizi xiralashadi (15–100%) |

Xira maydon niqob (mask) orqali yumshoq tugaydi — chegara chizig'i ko'rinmaydi.
`backdrop-filter` ishlamaydigan brauzerlarda karta avtomatik shaffofsiz bo'ladi.

## Telefonda

Sayt telefon uchun alohida sozlangan: tahrir paneli yon tomonga suriladigan
tasmaga aylanadi, slayd kartasi rasm ostiga tushadi, ma'lumot qutisi bitta
ustunga o'tadi, tugma va belgilar barmoq uchun kattalashadi (`pointer: coarse`),
kod bloklari va jadvallar esa o'z ichida suriladi — sahifaning o'zi hech qachon
yon tomonga surilmaydi. Kesish oynasi ham telefon ekraniga sig'adi.

## Xavfsizlik

| Xavf | Qanday yopilgan |
|---|---|
| SQL injection | Faqat Django ORM ishlatiladi, xom SQL yo'q |
| XSS (boy matn) | Saqlashda ham, chiqarishda ham `nh3` bilan tozalanadi: ruxsat etilgan teg, atribut va CSS xossalari ro'yxati bo'yicha |
| XSS (inline skript) | CSP: `script-src 'self' 'nonce-…'` — sahifadagi yagona inline skript nonce bilan, HTMLdagi `onclick` kabi hodisalar butunlay olib tashlangan |
| Clickjacking | `X-Frame-Options: DENY` + CSP `frame-ancestors 'none'` |
| CSRF | Django CSRF middleware, `CSRF_TRUSTED_ORIGINS`, cookie `Secure`+`SameSite=Lax` |
| Ochiq yo'naltirish | “Qaytish” havolasi faqat shu saytdagi manzilni qabul qiladi (`url_has_allowed_host_and_scheme`) |
| Sarlavha/log injection | Aloqa shaklidagi bir qatorlik maydonlardan yangi qator va ko'rinmas boshqaruv belgilari olib tashlanadi |
| Spam va brute force | Aloqa shakli: bir IP soatiga 5 ta xabar + honeypot maydon. Kirish: 15 daqiqada 8 ta noto'g'ri urinish, keyin vaqtincha to'xtaydi |
| Zararli fayl yuklash | Rasm maydonlari Pillow bilan tekshiriladi, muharrirdagi yuklash faqat rasm MIME turlarini va 8 MB gacha qabul qiladi, fayl nomi UUID bilan almashtiriladi |
| Havola orqali hujum | `javascript:` kabi sxemalar tozalanadi; slayd havolasi faqat ichki yo'l yoki `http(s)` bo'lishi mumkin |
| Ma'lumot sizishi | `DEBUG=0` da xato sahifalari o'z shablonlarimiz, `Referrer-Policy`, `Permissions-Policy` va HSTS yoqilgan |

`python manage.py check --deploy` faqat SECRET_KEY haqida ogohlantiradi — uni
muhit o'zgaruvchisidan bergandan so'ng ro'yxat toza bo'ladi.

## Ishlab chiqarishga chiqarish

`.env` fayli avtomatik o'qiladi (tashqi kutubxona kerak emas); haqiqiy muhit
o'zgaruvchilari undan ustun turadi.

```bash
cp .env.example .env          # va qiymatlarni to'ldiring
python -c "import secrets; print(secrets.token_urlsafe(64))"   # SECRET_KEY

pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --no-input
python manage.py check --deploy
gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3
```

Statik fayllarni WhiteNoise o'zi beradi (nginx shart emas), `media/` esa
veb-server orqali beriladi. Nginx uchun eng kichik namuna:

```nginx
server {
    server_name oldfox.uz www.oldfox.uz;
    client_max_body_size 12M;

    location /media/ { alias /var/www/oldfox/media/; }
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Eslatmalar:

- `DEBUG=0` bo'lganda `SECRET_KEY` bo'lmasa, sayt ataylab ishga tushmaydi
- Xato sahifalari: `templates/404.html`, `403.html`, `400.html`, `500.html`
  (500 sahifasi ma'lumotlar bazasiga murojaat qilmaydi — baza yotganda ham ochiladi)
- Dev uchun yaratilgan `admin` hisobining parolini albatta almashtiring
- `media/slider/placeholder-*.png` — vaqtinchalik rasmlar, o'zingiznikiga almashtiring
- Ko'p foydalanuvchili yuklamada SQLite o'rniga PostgreSQL ga o'tish tavsiya etiladi
