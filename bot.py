import os
import discord
from dotenv import load_dotenv
import google.generativeai as genai
from discord.ext import commands
import logging
import importlib
import asyncio
import sys
import io
from contextlib import redirect_stdout, redirect_stderr
import Forecast

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
    logger.exception(f"Lỗi nghiêm trọng khi cấu hình Google Generative AI: {e}") 
    exit()

# --- Cài đặt Intents cho Discord ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# --- Khởi tạo Discord Client ---
client = discord.Client(intents=intents)

# --- Sự kiện Bot Sẵn sàng ---
@client.event
async def on_ready():
    logger.info(f'{client.user.name} đã kết nối tới Discord!')
    await client.change_presence(activity=discord.Game(name="Hỏi đáp cùng Gemini"))
    logger.info(f"Bot đang hoạt động trên {len(client.guilds)} máy chủ.")

# --- Sự kiện Thành viên mới tham gia ---
@client.event
async def on_member_join(member: discord.Member):
    logger.info(f"Thành viên mới tham gia: {member.name} trong server {member.guild.name}")
    try:
        await member.dm_channel.send(f'Chào {member.mention}, chào mừng bạn đến với server **{member.guild.name}**!\nTôi là bot AI ở đây, bạn có thể tag tôi (@{client.user.name}) trong các kênh chat và đặt câu hỏi nhé.')
        logger.info(f"Đã gửi tin nhắn chào mừng tới {member.name}")
    except discord.errors.Forbidden:
        logger.warning(f"Không thể gửi tin nhắn DM tới {member.name}. Có thể do họ đã tắt DM từ thành viên server.")
    except Exception as e:
        logger.error(f"Lỗi khi gửi tin nhắn chào mừng tới {member.name}: {e}")

# --- Hàm chạy main.py và thu thập đầu ra ---
async def run_main_with_output_capture(alpaca_api_key, alpaca_api_secret, symbol):
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            importlib.reload(importlib.import_module("main"))
            from main import main
            
            result = main(alpaca_api_key, alpaca_api_secret, symbol)
            
        # Xử lý stdout/stderr 
        stdout_output = stdout_capture.getvalue()
        stderr_output = stderr_capture.getvalue()
        
        # Tạo nội dung tin nhắn
        combined_output = f"Kết quả phân tích cổ phiếu {symbol}:\n\n"
        combined_output += f"**Lời khuyên:**\n{result['advice']}\n\n"
        
        # Thêm metrics nếu có
        if result['metrics']['mae']:
            combined_output += f"\n**Độ chính xác:**\n"
            combined_output += f"- MAE: {result['metrics']['mae']:.2f}\n"
            combined_output += f"- RMSE: {result['metrics']['rmse']:.2f}\n"
            combined_output += f"- MAPE: {result['metrics']['mape']:.2f}%\n"
            
        # Trả về cả nội dung và đường dẫn ảnh
        return {
            "message": combined_output,
            "image_path": result['image_path']
        }
    
    except Exception as e:
        return {
            "message": f"Lỗi khi chạy phân tích cổ phiếu: {str(e)}\n\nLỗi chi tiết:\n```\n{stderr_capture.getvalue()}\n```",
            "image_path": None
        }


# --- Hàm gửi tin nhắn dài ---
async def send_long_message(channel, text, mention=None): 
    """
    Gửi một tin nhắn dài đến kênh Discord, chia thành nhiều phần nếu cần.
    Cố gắng chia tại các điểm ngắt tự nhiên (xuống dòng, chấm câu, khoảng trắng).
    """
    max_length = 2000
    if mention:  
        text = f"{mention}\n{text}"

    while len(text) > max_length:
        split_point = text[:max_length].rfind('\n')
        if split_point == -1:
            split_point = text[:max_length].rfind('.')
        if split_point == -1:
            split_point = text[:max_length].rfind(' ')
        if split_point == -1:
            split_point = max_length
        
        await channel.send(text[:split_point])
        text = text[split_point:]

    await channel.send(text)

# --- Hàm xử lý khi nhận tin nhắn lệnh ---
@client.event
async def on_message(message: discord.Message):
    if message.author == client.user or message.author.bot:
        return

    if client.user.mentioned_in(message):
        logger.info(f"Bot được tag bởi {message.author.name} trong kênh #{message.channel.name} (Server: {message.guild.name})")
        logger.debug(f"Nội dung gốc: '{message.content}'")

        prompt_text = message.content
        bot_mention_string = client.user.mention
        bot_nick_mention_string = f'<@!{client.user.id}>'

        if bot_nick_mention_string in prompt_text:
            prompt_text = prompt_text.replace(bot_nick_mention_string, '', 1)
        elif bot_mention_string in prompt_text:
            prompt_text = prompt_text.replace(bot_mention_string, '', 1)

        prompt_text = prompt_text.strip()

        if not prompt_text:
            logger.debug(f"Bot được tag nhưng không có câu hỏi từ {message.author.name}")
            await message.reply(f"Chào {message.author.mention}, bạn gọi tôi có việc gì không? Hãy đặt câu hỏi nhé!", mention_author=False)
            return

        investment_keywords = ["cổ phiếu", "dự đoán", "đầu tư", "chứng khoán", "mã", "tài chính", "price", "stock", "invest"]
        if any(keyword in prompt_text.lower() for keyword in investment_keywords):
            # async with message.channel.typing():
            def check(m):
                return m.author == message.author and m.channel == message.channel
            try:
                await message.reply(f"{message.author.mention} SkyBot đã nhận được yêu cầu của bạn. Vui lòng cung cấp thông tin cần thiết.", mention_author=False)
                await message.channel.send(f"{message.author.mention} Bạn muốn lấy tin tức từ trang Alpaca hay là một trang mới?", mention_author=False)
                try:
                    new_message = await client.wait_for('message', timeout=30.0, check=check)
                    new_response = new_message.content
                except asyncio.TimeoutError:
                    await message.channel.send(f"{message.author.mention} Đã hết thời gian chờ. Vui lòng thử lại.", mention_author=False)
                    return
                
                if "alpaca" in new_response.lower():
                    alpaca_api_key=os.getenv('ALPACA_API_KEY')
                    alpaca_api_secret=os.getenv('ALPACA_API_SECRET')

                else:
                    # Hỏi về API KEY
                    await message.channel.send(f"{message.author.mention} Vui lòng cho biết API Key của nơi bạn sẽ lấy tin tức của bạn:", mention_author=False)
                    try:
                        alpaca_api_key_message = await client.wait_for('message', timeout=30.0, check=check)
                        alpaca_api_key = alpaca_api_key_message.content
                        # Xóa tin nhắn chứa API key để bảo mật
                        try:
                            await alpaca_api_key_message.delete()
                        except:
                            await message.channel.send("Không thể xóa tin nhắn chứa API key. Cân nhắc xóa thủ công để bảo mật.")
                    except asyncio.TimeoutError:
                        await message.channel.send(f"{message.author.mention} Đã hết thời gian chờ. Vui lòng thử lại.", mention_author=False)
                        return

                    # Hỏi về API SECRET
                    await message.channel.send(f"{message.author.mention} Vui lòng cho biết API Secret của trang đó của bạn:", mention_author=False)
                    try:
                        alpaca_api_secret_message = await client.wait_for('message', timeout=30.0, check=check)
                        alpaca_api_secret = alpaca_api_secret_message.content
                        # Xóa tin nhắn chứa API secret để bảo mật
                        try:
                            await alpaca_api_secret_message.delete()
                        except:
                            await message.channel.send("Không thể xóa tin nhắn chứa API secret. Cân nhắc xóa thủ công để bảo mật.")
                    except asyncio.TimeoutError:
                        await message.channel.send(f"{message.author.mention} Đã hết thời gian chờ. Vui lòng thử lại.", mention_author=False)
                        return

                # Hỏi về mã cổ phiếu
                await message.channel.send(f"{message.author.mention} Vui lòng cho biết mã cổ phiếu bạn muốn hỏi (ví dụ: AAPL):", mention_author=False)
                try:
                    symbol_message = await client.wait_for('message', timeout=30.0, check=check)
                    symbol = symbol_message.content.upper()  # Chuyển thành chữ hoa để thống nhất
                except asyncio.TimeoutError:
                    await message.channel.send(f"{message.author.mention} Đã hết thời gian chờ. Vui lòng thử lại.", mention_author=False)
                    return

                processing_msg = await message.reply(f"{message.author.mention} Tôi đã nhận đủ thông tin cần thiết và đang phân tích dữ liệu cổ phiếu {symbol}. Vui lòng đợi trong giây lát...", mention_author=False)
                
                async with message.channel.typing():
                    result = await run_main_with_output_capture(alpaca_api_key, alpaca_api_secret, symbol)
                    await send_long_message(message.channel, result["message"], mention=message.author.mention)

                    if result["image_path"]:
                        with open(result["image_path"], 'rb') as img_file:
                            await message.channel.send(file=discord.File(img_file))
                    
                    # Cập nhật thông báo đang xử lý
                    await processing_msg.delete()

                    # Forecast data
                    try:
                        csv_path = f"Data/{symbol}_du_lieu.csv"
                        forecast_df = Forecast.forecasting(csv_path, column_name="close", periods=7, future_only=True)

                        forecast_output = f"\t\t\t\t\t📊 **Dự báo giá cổ phiếu {symbol} cho 7 ngày tới:** 📊\n"
                        for index, row in forecast_df.iterrows():
                            date = row['ds'].strftime('%Y-%m-%d')
                            yhat = row['yhat']
                            yhat_lower = row['yhat_lower']
                            yhat_upper = row['yhat_upper']
                            forecast_output += f"Ngày: {date}, Dự đoán: {yhat:.2f}, Khoảng tin cậy: ({yhat_lower:.2f} - {yhat_upper:.2f})\n"
                        await send_long_message(message.channel, forecast_output, mention=None)
                        await message.channel.send(f"{message.author.mention} **Lưu ý:** Đây chỉ là những khuyến nghị dựa trên dữ liệu hạn chế là những tin tức lấy được trên web về loại cổ phiếu của bạn. Bạn nên tự mình nghiên cứu thêm về công ty, ngành và các yếu tố vĩ mô có thể ảnh hưởng đến giá cổ phiếu")

                    except Exception as e:
                        error_message = f"Lỗi khi thực hiện dự báo: {str(e)}"
                        logger.exception(error_message)
                        await message.reply(f"{message.author.mention} {error_message}", mention_author=False)

            except Exception as e:
                logger.exception(f"Lỗi khi chạy main.py: {e}")
                await message.reply(f"{message.author.mention} Xin lỗi, tôi gặp sự cố khi xử lý yêu cầu của bạn: {str(e)}", mention_author=False)
        else:
            # Nếu không hỏi về cổ phiếu, sử dụng Gemini AI
            async with message.channel.typing():
                try:
                    logger.info(f"Gửi câu hỏi tới Google AI: '{prompt_text}'")
                    response = model.generate_content(prompt_text)

                    if not response.parts:
                        logger.warning(f"Google AI không trả về nội dung cho prompt: '{prompt_text}'. Phản hồi an toàn: {response.prompt_feedback}")
                        await message.reply(f"{message.author.mention} Xin lỗi, tôi không thể tạo phản hồi cho yêu cầu này. Có thể nội dung không phù hợp hoặc có lỗi xảy ra.", mention_author=False)
                        return

                    ai_response = response.text
                    logger.info(f"Nhận phản hồi từ Google AI (độ dài: {len(ai_response)} ký tự).")
                    await send_long_message(message.channel, ai_response, mention=message.author.mention)

                except Exception as e:
                    logger.exception(f"Lỗi khi xử lý tin nhắn hoặc gọi Google AI: {e}")
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