import os
import discord
from dotenv import load_dotenv
import google.generativeai as genai
import logging

# --- Cấu hình Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)

# --- Tải biến môi trường ---
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD') 
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# --- Kiểm tra biến môi trường ---
if not TOKEN:
    logger.error("Lỗi: DISCORD_TOKEN không được tìm thấy trong tệp .env")
    exit()
if not GOOGLE_API_KEY:
    logger.error("Lỗi: GOOGLE_API_KEY không được tìm thấy trong tệp .env")
    exit()

# --- Cấu hình Google Generative AI ---
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
    logger.info("Đã kết nối thành công với Google Generative AI (Model: gemini-pro).")
except Exception as e:
    logger.exception(f"Lỗi nghiêm trọng khi cấu hình Google Generative AI: {e}") # logger.exception bao gồm cả traceback
    exit()

# --- Cài đặt Intents cho Discord ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True # Cần cho on_member_join

# --- Khởi tạo Discord Client ---
client = discord.Client(intents=intents)

# --- Sự kiện Bot Sẵn sàng ---
@client.event
async def on_ready():
    """Sự kiện được kích hoạt khi bot kết nối thành công với Discord."""
    logger.info(f'{client.user.name} (ID: {client.user.id}) đã kết nối tới Discord!')
    # Đặt trạng thái hoạt động cho bot
    await client.change_presence(activity=discord.Game(name="Hỏi đáp cùng Gemini"))
    logger.info(f"Bot đang hoạt động trên {len(client.guilds)} máy chủ.")
    # Bạn có thể log tên các máy chủ nếu cần (chỉ khi bot ở ít server)
    # for guild in client.guilds:
    #     logger.info(f"- {guild.name} (ID: {guild.id})")

# --- Sự kiện Thành viên mới tham gia ---
@client.event
async def on_member_join(member: discord.Member):
    """Gửi tin nhắn chào mừng khi có thành viên mới tham gia server."""
    logger.info(f"Thành viên mới tham gia: {member.name} (ID: {member.id}) trong server {member.guild.name}")
    try:
        # Tạo kênh DM với thành viên
        await member.create_dm()
        # Gửi tin nhắn chào mừng cá nhân
        await member.dm_channel.send(
            f'Chào {member.mention}, chào mừng bạn đến với server **{member.guild.name}**!'
            f'\nTôi là bot AI ở đây, bạn có thể tag tôi (@{client.user.name}) trong các kênh chat và đặt câu hỏi nhé.'
        )
        logger.info(f"Đã gửi tin nhắn chào mừng tới {member.name}")
    except discord.errors.Forbidden:
        logger.warning(f"Không thể gửi tin nhắn DM tới {member.name}. Có thể do họ đã tắt DM từ thành viên server.")
    except Exception as e:
        logger.error(f"Lỗi khi gửi tin nhắn chào mừng tới {member.name}: {e}")

# --- Sự kiện Nhận Tin nhắn ---
@client.event
async def on_message(message: discord.Message):
    """Xử lý tin nhắn đến."""
    # Bỏ qua tin nhắn từ chính bot hoặc các bot khác
    if message.author == client.user or message.author.bot:
        return

    # Kiểm tra xem bot có được tag (mention) trong tin nhắn không
    if client.user.mentioned_in(message):
        logger.info(f"Bot được tag bởi {message.author.name} (ID: {message.author.id}) trong kênh #{message.channel.name} (Server: {message.guild.name})")
        logger.debug(f"Nội dung gốc: '{message.content}'")

        # Xóa phần tag bot khỏi nội dung tin nhắn để lấy câu hỏi
        # Cách này đảm bảo xóa đúng mention của bot, kể cả khi có nickname
        prompt_text = message.content
        bot_mention_string = client.user.mention # Dạng <@USER_ID>
        bot_nick_mention_string = f'<@!{client.user.id}>' # Dạng <@!USER_ID> khi có nickname server

        # Ưu tiên xóa nick mention trước nếu có, sau đó xóa mention thường
        if bot_nick_mention_string in prompt_text:
             prompt_text = prompt_text.replace(bot_nick_mention_string, '', 1)
        elif bot_mention_string in prompt_text:
             prompt_text = prompt_text.replace(bot_mention_string, '', 1)

        prompt_text = prompt_text.strip() # Xóa khoảng trắng thừa ở đầu/cuối

        # Nếu không còn nội dung sau khi xóa mention -> yêu cầu đặt câu hỏi
        if not prompt_text:
            logger.info(f"Bot được tag nhưng không có câu hỏi từ {message.author.name}")
            await message.reply(f"Chào {message.author.mention}, bạn gọi tôi có việc gì không? Hãy đặt câu hỏi nhé!", mention_author=False) # reply tiện hơn send ở đây
            return

        # Gửi thông báo "đang xử lý" (typing indicator) cho người dùng biết bot đang làm việc
        async with message.channel.typing():
            try:
                logger.info(f"Gửi câu hỏi tới Google AI: '{prompt_text}'")
                # Bắt đầu phiên chat (tùy chọn, nếu muốn có ngữ cảnh đơn giản)
                # chat = model.start_chat()
                # response = await chat.send_message_async(prompt_text) # Sử dụng async nếu có thể

                # Hoặc gọi trực tiếp như cũ (stateless)
                response = model.generate_content(prompt_text)

                # Xử lý response (Gemini có thể có các cơ chế an toàn, kiểm tra trước khi lấy text)
                # Tham khảo thêm tài liệu Gemini về `response.prompt_feedback` và `response.candidates[0].finish_reason`
                if not response.parts:
                     # Có thể do bộ lọc an toàn hoặc không có nội dung trả về
                     logger.warning(f"Google AI không trả về nội dung cho prompt: '{prompt_text}'. Phản hồi an toàn: {response.prompt_feedback}")
                     await message.reply(f"{message.author.mention} Xin lỗi, tôi không thể tạo phản hồi cho yêu cầu này. Có thể nội dung không phù hợp hoặc có lỗi xảy ra.", mention_author=False)
                     return

                ai_response = response.text
                logger.info(f"Nhận phản hồi từ Google AI (độ dài: {len(ai_response)} ký tự).")
                # logger.debug(f"Nội dung phản hồi AI: '{ai_response[:200]}...'") # Log một phần để kiểm tra

                # Giới hạn độ dài tin nhắn Discord (2000 ký tự)
                discord_max_length = 2000
                mention_prefix = f"{message.author.mention} "
                # Tính toán độ dài tối đa cho mỗi phần, trừ đi độ dài mention và khoảng trắng
                max_chunk_length = discord_max_length - len(mention_prefix) - 10 # Thêm buffer nhỏ

                if len(ai_response) <= max_chunk_length:
                    # Gửi toàn bộ nếu đủ ngắn
                    await message.reply(f"{mention_prefix}{ai_response}", mention_author=False)
                else:
                    # Gửi từng phần nếu quá dài
                    logger.info(f"Phản hồi quá dài ({len(ai_response)}), sẽ gửi thành nhiều phần.")
                    await message.reply(f"{mention_prefix}Câu trả lời hơi dài, tôi sẽ gửi thành nhiều phần:", mention_author=False)
                    
                    # Chia nhỏ văn bản thông minh hơn (cố gắng không cắt giữa câu/từ) - cách đơn giản:
                    start = 0
                    while start < len(ai_response):
                        end = start + max_chunk_length
                        # Nếu end chưa phải cuối chuỗi, cố gắng lùi lại tìm dấu xuống dòng hoặc khoảng trắng gần nhất
                        if end < len(ai_response):
                            # Tìm vị trí cắt hợp lý (ví dụ: xuống dòng, chấm câu, khoảng trắng)
                            # Đoạn này có thể làm phức tạp hơn để cắt đẹp hơn
                            best_cut = ai_response.rfind('\n', start, end)
                            if best_cut == -1: # Không tìm thấy xuống dòng
                                best_cut = ai_response.rfind('.', start, end)
                            if best_cut == -1: # Không tìm thấy dấu chấm
                                best_cut = ai_response.rfind(' ', start, end)

                            # Nếu tìm được vị trí cắt tốt và không quá ngắn, dùng nó
                            if best_cut != -1 and best_cut > start + max_chunk_length // 2: # Tránh cắt quá sớm
                                end = best_cut + 1 # Cắt sau ký tự tìm được
                            # else: giữ nguyên end (cắt cứng)

                        chunk = ai_response[start:end]
                        await message.channel.send(chunk) # Gửi phần tiếp theo không cần mention lại
                        start = end
                        # Thêm delay nhỏ nếu cần để tránh rate limit của Discord
                        # await asyncio.sleep(0.5) 

            except Exception as e:
                logger.exception(f"Lỗi khi xử lý tin nhắn hoặc gọi Google AI: {e}") # logger.exception để log cả traceback
                try:
                    await message.reply(f"{message.author.mention} Xin lỗi, tôi gặp sự cố khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.", mention_author=False)
                except discord.errors.HTTPException as http_err:
                    logger.error(f"Lỗi HTTP khi gửi thông báo lỗi Discord: {http_err}")


# --- Chạy bot ---
if __name__ == "__main__":
    logger.info("Đang khởi chạy bot...")
    try:
        client.run(TOKEN)
    except discord.errors.LoginFailure:
        logger.error("Lỗi đăng nhập Discord: Token không hợp lệ.")
    except Exception as e:
        logger.exception(f"Lỗi không xác định khi chạy bot: {e}")