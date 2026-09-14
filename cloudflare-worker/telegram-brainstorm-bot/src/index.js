// Telegram-бот для мозгового штурма (Milis Cosmo / Milis Decor / art.Angel).
// Cloudflare Worker: принимает Telegram-webhook напрямую, без промежуточных
// сервисов (альтернатива pipedream/telegram-brainstorm-bot — тот же ТЗ,
// но без Pipedream).

const BOT_USERNAME = "OzonAnnabot";

const SYSTEM_PROMPT = `Ты — участник мозгового штурма в рабочем чате Евгения (владелец) и Анны (менеджер Ozon/ВК).
Бизнес: Milis Cosmo (косметика собственного производства, WB/Ozon), Milis Decor (ПУ-панели, Avito), art.Angel (блютус-адаптеры, Ozon).
Текущий фокус: маржинальность карточек, новые каналы сбыта, соцсети/узнаваемость бренда. Избегай советов, требующих крупных вложений на старте.
Роль — предлагать идеи и решения, задавать уточняющие вопросы, по-деловому и кратко (буллиты, без длинных вступлений).
Никогда не публикуй, не отправляй сообщения от их имени и не называй точные суммы без пометки «уточнить» — только советуй в этом чате.`;

export default {
  async fetch(request, env, ctx) {
    if (request.method !== "POST") return new Response("OK");

    let update;
    try {
      update = await request.json();
    } catch {
      return new Response("OK");
    }

    // Отвечаем Telegram сразу, обработку делаем в фоне (waitUntil) —
    // так вебхук не ждёт ответа Anthropic API.
    ctx.waitUntil(handleUpdate(update, env));
    return new Response("OK");
  },
};

async function handleUpdate(update, env) {
  const msg = update.message;
  if (!msg || !msg.text) {
    console.log(`[debug] skip: no message/text. keys=${Object.keys(update)}`);
    return;
  }

  // Работаем только в целевой группе мозгового штурма, не в личке с Анной
  // (там та же бот-учётка обслуживает отдельную логику Ozon-эскалаций).
  if (String(msg.chat.id) !== String(env.GROUP_CHAT_ID)) {
    console.log(`[debug] skip: chat.id=${msg.chat.id} != GROUP_CHAT_ID=${env.GROUP_CHAT_ID}`);
    return;
  }

  const isMention = msg.text.includes(`@${BOT_USERNAME}`);
  const isReplyToBot = msg.reply_to_message?.from?.is_bot === true;
  if (!isMention && !isReplyToBot) {
    console.log(`[debug] skip: no mention/reply. text=${msg.text}`);
    return;
  }
  console.log(`[debug] processing message: ${msg.text}`);

  let replyText;
  try {
    const res = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": env.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: "claude-sonnet-4-5", // проверить актуальный ID модели в docs.claude.com перед деплоем
        max_tokens: 1024,
        system: SYSTEM_PROMPT,
        messages: [{ role: "user", content: `${msg.from.first_name}: ${msg.text}` }],
      }),
    });
    if (!res.ok) {
      console.log(`[warn] Anthropic API error: ${res.status} ${await res.text()}`);
      return; // не отвечаем молчанием при ошибке, не роняем worker
    }
    const data = await res.json();
    replyText = data.content[0].text;
  } catch (e) {
    console.log(`[warn] Anthropic API error: ${e.message}`);
    return;
  }

  const tgRes = await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      chat_id: msg.chat.id,
      text: replyText,
      reply_to_message_id: msg.message_id,
    }),
  });
  if (!tgRes.ok) {
    console.log(`[warn] Telegram sendMessage error: ${tgRes.status} ${await tgRes.text()}`);
  }
}
