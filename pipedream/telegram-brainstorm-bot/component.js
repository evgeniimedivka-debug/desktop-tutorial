import Anthropic from "@anthropic-ai/sdk";

// Pipedream Node.js code step: Telegram-бот для мозгового штурма
// (см. ТЗ, раздел 4). Триггер — HTTP-вебхук Telegram (setWebhook, раздел 5).
export default defineComponent({
  async run({ steps, $ }) {
    const update = steps.trigger.event.body;
    const msg = update.message;
    if (!msg || !msg.text) return;

    // Работаем только в целевой группе мозгового штурма, не в личке с Анной
    // (там та же бот-учётка обслуживает отдельную логику Ozon-эскалаций).
    if (String(msg.chat.id) !== String(process.env.GROUP_CHAT_ID)) return;

    const botUsername = "OzonAnnabot";
    const isMention = msg.text.includes(`@${botUsername}`);
    const isReplyToBot = msg.reply_to_message?.from?.is_bot === true;
    if (!isMention && !isReplyToBot) return;

    const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

    const systemPrompt = `Ты — участник мозгового штурма в рабочем чате Евгения (владелец) и Анны (менеджер Ozon/ВК).
Бизнес: Milis Cosmo (косметика собственного производства, WB/Ozon), Milis Decor (ПУ-панели, Avito), art.Angel (блютус-адаптеры, Ozon).
Текущий фокус: маржинальность карточек, новые каналы сбыта, соцсети/узнаваемость бренда. Избегай советов, требующих крупных вложений на старте.
Роль — предлагать идеи и решения, задавать уточняющие вопросы, по-деловому и кратко (буллиты, без длинных вступлений).
Никогда не публикуй, не отправляй сообщения от их имени и не называй точные суммы без пометки «уточнить» — только советуй в этом чате.`;

    let replyText;
    try {
      const response = await anthropic.messages.create({
        model: "claude-sonnet-4-5", // проверить актуальный ID модели в docs.claude.com перед деплоем
        max_tokens: 1024,
        system: systemPrompt,
        messages: [{ role: "user", content: `${msg.from.first_name}: ${msg.text}` }],
      });
      replyText = response.content[0].text;
    } catch (e) {
      console.log(`[warn] Anthropic API error: ${e.message}`);
      return; // не отвечаем молчанием при ошибке, не роняем workflow
    }

    await fetch(`https://api.telegram.org/bot${process.env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: msg.chat.id,
        text: replyText,
        reply_to_message_id: msg.message_id,
      }),
    });
  },
});
