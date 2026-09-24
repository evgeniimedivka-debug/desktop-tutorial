# Instagram — настройка публикации (упрощённая схема, без Facebook Page)

Обновлено под официальную схему **«Instagram API с входом через
Instagram»** (Instagram Login for Business, актуальна с 2025 года) — она
проще предыдущей: **не требует Facebook Page и Business Manager**,
только сам профессиональный (business) аккаунт Instagram и Meta App.

Все шаги ниже делаются вами лично, в вашем браузере, под вашим
Instagram/Meta-логином — это единственная часть задачи, которую
физически не может выполнить автоматизация или я: вход и подтверждение
доступа происходят на официальной странице Instagram, пароль там вводите
только вы.

## 1. Перевести аккаунт Milis Decor в профессиональный (Business)

- В приложении Instagram: аккаунт → Settings → Account type and tools →
  Switch to professional account → **Business**.
- Facebook Page на этом шаге привязывать не обязательно — просто
  пропустите предложение, если оно появится.

## 2. Создать Meta App

- developers.facebook.com → My Apps → Create App → тип **Business**.
- Добавить продукт **Instagram** → выбрать конфигурацию **«Instagram
  API with Instagram Login»** (не Facebook Login for Business — это
  старая схема с обязательной Page).
- App Settings → Basic: заполнить Privacy Policy URL (обязательное
  поле).

## 3. Настроить OAuth redirect URI

- В настройках продукта Instagram → Instagram API setup → добавить
  **Valid OAuth Redirect URI**. Подойдёт `https://n8n.31-130-131-58.sslip.io/webhook/cf/ig-oauth-callback`
  (я разверну под него приёмный webhook, когда дойдём до обмена кода на
  токен).

## 4. Авторизация — ссылку соберу я, откроете и подтвердите вы

Когда у вас будет App ID (Instagram App ID, не путать с Facebook App
ID — в этой схеме они разные), пришлите его мне, и я соберу ссылку вида:

```
https://api.instagram.com/oauth/authorize
  ?client_id=<INSTAGRAM_APP_ID>
  &redirect_uri=<тот же URI, что в шаге 3>
  &scope=instagram_business_basic,instagram_business_content_publish
  &response_type=code
```

Вы откроете её, войдёте под своим Instagram-логином Milis Decor,
подтвердите доступ приложению. Instagram перенаправит на redirect_uri с
`?code=...` в адресной строке — этот код (действует пару минут) нужно
будет прислать мне, дальше обмен на токен я сделаю сам через API.

## 5. Обмен кода на токен (делаю я, через API, без вашего участия)

```
POST https://api.instagram.com/oauth/access_token
  client_id=<INSTAGRAM_APP_ID>
  client_secret=<INSTAGRAM_APP_SECRET>   (из Meta App, шаг 2)
  grant_type=authorization_code
  redirect_uri=<тот же URI>
  code=<код из шага 4>
```
→ короткоживущий токен, дальше обменивается на долгоживущий (~60 дней):
```
GET https://graph.instagram.com/access_token
  ?grant_type=ig_exchange_token
  &client_secret=<INSTAGRAM_APP_SECRET>
  &access_token=<короткий токен>
```

## 6. Получить IG User ID

```
GET https://graph.instagram.com/v21.0/me?fields=user_id&access_token=<токен>
```

## 7. Что передать в n8n (сделаю сам, как получу значения)

- `IG_USER_ID` и `IG_ACCESS_TOKEN` — как переменные окружения n8n на
  VPS. У меня нет shell-доступа к контейнеру n8n, чтобы прописать их
  напрямую в `.env` — этот шаг тоже придётся сделать вам (или дать мне
  доступ к серверу), либо я подставлю значения прямо в узлы workflow
  CF-09 как константы (менее удобно при продлении токена раз в 60 дней,
  но работает без доступа к серверу).

## Ограничения

- Токен живёт ~60 дней, нужно продлевать (`ig_refresh_token` — тот же
  принцип, что и exchange, но без пароля).
- Reels: публикация возможна только после того, как контейнер получит
  `status_code=FINISHED` — CF-09 это уже учитывает (поллинг каждые 15с).
- Публикация — только по прямому публичному URL на файл; `video_url` в
  таблице «Ролики» уже отдаёт публичный URL, дополнительно ничего
  готовить не нужно.
- Лимит 25 публикаций/сутки на аккаунт через API — для вашего объёма
  контента запаса более чем достаточно.
