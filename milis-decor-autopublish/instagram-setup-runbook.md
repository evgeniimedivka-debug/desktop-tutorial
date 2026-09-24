# Instagram Graph API — настройка с нуля для Milis Decor

Ваш ответ: сейчас нет ни Facebook Business Manager, ни привязанного
Instagram Business-аккаунта. Ниже — минимальный набор шагов через
официальные бесплатные инструменты Meta, без платных сервисов.

Эти шаги делаются в личном кабинете Meta вашими руками (логин, номер
телефона для верификации, подтверждение владения) — автоматизация тут
подключиться не может.

## 1. Facebook Page для Milis Decor
- facebook.com → Pages → Create Page.
- Название: «Milis Decor», категория — что-то в духе «Home Decor» /
  «Building Materials».
- Без Page нельзя привязать Instagram Business-аккаунт к Graph API.

## 2. Meta Business Manager (business.facebook.com)
- Create Account → название бизнеса «Milis Decor» (или общий бизнес-аккаунт
  Milis, если хотите объединить с Milis Cosmo — можно оставить раздельно,
  проще прав доступа).
- Business Settings → Accounts → Pages → Add → привязать Page из шага 1.

## 3. Instagram-аккаунт Milis Decor → Business
- В приложении Instagram: аккаунт Milis Decor → Settings → Account type
  and tools → Switch to professional account → Business.
- Привязать к Facebook Page из шага 1 (предложится в том же мастере).
- В Business Manager: Business Settings → Accounts → Instagram accounts →
  Add → подключить тот же IG-аккаунт.

## 4. Meta App (developers.facebook.com)
- My Apps → Create App → тип **Business**.
- Добавить продукт **Instagram Graph API** (не Basic Display — он для
  чтения своих медиа, для публикации нужен Graph API через Business
  Login).
- App Settings → Basic: заполнить Privacy Policy URL (обязательное поле;
  подойдёт страница на вашем сайте/маркетплейсе-визитке) — без этого
  App не пройдёт даже базовую проверку для использования с реальным
  IG-аккаунтом.

## 5. Права доступа (permissions) и токен
Нужны разрешения: `instagram_basic`, `instagram_content_publish`,
`pages_show_list`, `pages_read_engagement`.

- Graph API Explorer (developers.facebook.com/tools/explorer) → выбрать
  свой App → User Token → отметить перечисленные permissions → Generate
  Access Token → войти под аккаунтом, у которого есть доступ к Page.
- Это короткоживущий токен (~1 час) — дальше обменять на долгоживущий:

```
GET https://graph.facebook.com/v21.0/oauth/access_token
  ?grant_type=fb_exchange_token
  &client_id=<APP_ID>
  &client_secret=<APP_SECRET>
  &fb_exchange_token=<КОРОТКИЙ_ТОКЕН>
```
Ответ — токен на ~60 дней.

- Для промышленной эксплуатации (без ручного продления раз в 60 дней)
  дальше нужен **System User token** в Business Manager (Business
  Settings → Users → System Users → Add → назначить Page/IG asset →
  Generate Token с теми же permissions) — такой токен не истекает по
  времени, только при ревокации. Рекомендую сразу делать через System
  User, чтобы не продлевать вручную каждые 2 месяца.

## 6. Получить IG User ID (`ig-user-id`) для API-вызовов

```
GET https://graph.facebook.com/v21.0/<PAGE_ID>
  ?fields=instagram_business_account
  &access_token=<ТОКЕН>
```
В ответе — `instagram_business_account.id`, он же `ig-user-id`,
используется в CF-09 (`n8n-workflows/CF-09-publish-instagram.json`).

## 7. App Review (только если публикация не работает у обычных
   пользователей / только у вас как у админа App)
- Пока вы единственный, кто публикует под этим App (владелец = сам
  бизнес), режим **Development** обычно достаточен — Graph API
  разрешает вызовы от ролей App (Admin/Developer/Tester), назначенных
  в App Roles, без прохождения полного Review.
- Полный App Review (Advanced Access) нужен только если публикацию
  будет делать сторонний сервис от имени множества клиентов — это не
  ваш случай.

## Что сохранить и передать в n8n (credential, не в NocoDB и не в git)

- `IG_USER_ID` — из шага 6
- `ACCESS_TOKEN` (System User token) — из шага 5
- Оба — в n8n: Credentials → HTTP Header Auth / Generic, используется
  в `CF-09-publish-instagram.json`.

## Ограничения Instagram Graph API, которые важно знать заранее

- Публикация — только по **прямой публичной URL** на файл (n8n должен
  отдать n8n-инстансу доступный извне `https://` URL картинки/видео,
  не base64 и не локальный путь). Уточнить, откуда рендер CF-02..CF-05
  хранит готовые файлы — если это NocoDB attachment или файл на VPS,
  нужен публично доступный URL (например, отдать через nginx на VPS
  или Attachment URL из NocoDB, если он публичный).
- Reels: контейнер создаётся, но публикация возможна только после того,
  как `status_code` контейнера станет `FINISHED` (обработка видео на
  стороне Meta занимает от нескольких секунд до пары минут) — CF-09
  это учитывает через поллинг.
- Лимит: 25 публикаций на IG Business-аккаунт в сутки через API (для
  вашего объёма — 1 видео + 2 фото в день по плану — с большим запасом).
