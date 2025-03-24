import datetime
import os
import pathlib
import shutil
import jmcomic.jm_config
import telegram
import telegram.ext
import jmcomic

jmoption = jmcomic.create_option_by_file(
    str((pathlib.Path(__file__).parent.resolve() / "option.yml").absolute())
)


async def jmdownload(
    update: telegram.Update, ctx: telegram.ext.ContextTypes.DEFAULT_TYPE
):
    if ctx.bot_data.get("cleanup", False):
        return
    if update.effective_message is None:
        return
    if not ctx.args:
        await update.effective_message.reply_text("Usage: /jmd <漫画ID>")
        return
    jmid = ctx.args[0]
    try:
        msg = await update.effective_message.reply_text(f"正在下载 JM {jmid}")
        album, _ = jmcomic.download_album(jmid, jmoption)
        if isinstance(album, jmcomic.JmAlbumDetail):
            print(f"下载完成: \n标题: {album.title}\n")
            await msg.delete()
            await update.effective_message.reply_document(
                f"./pdfs/{album.id}.pdf",
                caption=album.title,
            )
    except Exception as e:
        print(e)
        await update.effective_message.reply_text(f"Error: {e.__class__.__name__}")


async def cleanup(update: telegram.Update, ctx: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if update.effective_message is None:
        return
    if update.effective_user is None:
        return
    if not os.environ.get("ADMIN"):
        return
    if str(update.effective_user.id) != os.environ.get("ADMIN"):
        print(update.effective_user.id)
        return
    ctx.bot_data["cleanup"] = True
    try:
        shutil.rmtree("./pdfs")
        shutil.rmtree("./downloads")
        os.mkdir("./pdfs")
        os.mkdir("./downloads")
    except FileNotFoundError:
        pass
    except Exception as e:
        print(e)
        await update.effective_message.reply_text(f"Error: {e.__class__.__name__}")
    finally:
        ctx.bot_data["cleanup"] = False

    await update.effective_message.reply_text("Cleanup done.")


async def init_commands(app: telegram.ext.Application):
    await app.bot.set_my_commands(
        [
            telegram.BotCommand("jmd", "Download JM comic"),
            telegram.BotCommand("cleanup", "Cleanup downloaded files (Admin only)"),
        ]
    )


handlers = [
    telegram.ext.CommandHandler("jmd", jmdownload),
    telegram.ext.CommandHandler("cleanup", cleanup),
]


def main():
    default_config = telegram.ext.Defaults(
        tzinfo=datetime.timezone(datetime.timedelta(hours=8)),
        do_quote=True,
        allow_sending_without_reply=True,
    )
    rate_limiter = telegram.ext.AIORateLimiter()
    app = (
        telegram.ext.ApplicationBuilder()
        .token(os.environ["TOKEN"])
        .defaults(default_config)
        .rate_limiter(rate_limiter)
        .base_url(os.environ.get("API_URL", "https://api.telegram.org/bot"))
        .base_file_url(os.environ.get("FILE_URL", "https://api.telegram.org/file/bot"))
        .post_init(init_commands)
        .build()
    )
    app.add_handlers(handlers)
    print("Running...")
    app.run_polling()


if __name__ == "__main__":
    main()
