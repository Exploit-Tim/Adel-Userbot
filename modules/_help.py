# ... kode sebelumnya ...

from Ayra.dB._core import HELP, LIST
from Ayra.fns.tools import cmd_regex_replace
from telethon import events # Pastikan ini sudah diimpor
from telethon.errors.rpcerrorlist import (BotInlineDisabledError,
                                          BotMethodInvalidError,
                                          BotResponseTimeoutError)
from telethon.tl.custom import Button

from . import HNDLR, LOGS, asst, ayra_cmd, get_string # Pastikan semua import ini ada

_main_help_menu = [
    [
        Button.inline(get_string("help_4"), data="uh_Official_"),
    ],
]


@ayra_cmd(pattern="[hH][eE][lL][pP]( (.*)|$)")
async def _help(ayra):
    plug = ayra.pattern_match.group(1).strip()
    chat = await ayra.get_chat()
    if plug:
        try:
            if plug in HELP["Official"]:
                output = f"**Plugin** - `{plug}`\n"
                for i in HELP["Official"][plug]:
                    output += i
                output += "\n© @Darensupport"
                await ayra.eor(output)
            else:
                try:
                    x = get_string("help_11").format(plug)
                    for d in LIST[plug]:
                        x += HNDLR + d
                        x += "\n"
                    x += "\n© @Darensupport"
                    await ayra.eor(x)
                except BaseException:
                    file = None
                    compare_strings = []
                    for file_name in LIST:
                        compare_strings.append(file_name)
                        value = LIST[file_name]
                        for j in value:
                            j = cmd_regex_replace(j)
                            compare_strings.append(j)
                            if j.strip() == plug:
                                file = file_name
                                break
                    if not file:
                        text = f"`{plug}` is not a valid plugin!"
                        if best_match := next(
                            (
                                _
                                for _ in compare_strings
                                if plug in _ and not _.startswith("_")
                            ),
                            None,
                        ):
                            text += f"\nDid you mean `{best_match}`?"
                        return await ayra.eor(text)
                    output = f"**Perintah** `{plug}` **ditemukan dalam** - `{file}`\n"
                    if file in HELP["Official"]:
                        for i in HELP["Official"][file]:
                            output += i
                    output += "\n© @Darensupport"
                    await ayra.eor(output)
        except BaseException as er:
            LOGS.exception(er)
            await ayra.eor("Error 🤔 occured.")
    else:
        try:
            results = await ayra.client.inline_query(asst.me.username, "ayra")
        except BotMethodInvalidError:
            z = []
            for x in LIST.values():
                z.extend(x)
            cmd = len(z) + 10
            return await ayra.reply(
                get_string("inline_4").format(
                    OWNER_NAME, # Pastikan OWNER_NAME sudah terdefinisi
                    len(HELP["Official"]),
                    cmd,
                ),
                buttons=_main_help_menu,
            )
        except BotResponseTimeoutError:
            return await ayra.eor(
                get_string("help_2").format(HNDLR),
            )
        except BotInlineDisabledError:
            return await ayra.eor(get_string("help_3"))
        await results[0].click(chat.id, reply_to=ayra.reply_to_msg_id, hide_via=True)
        await ayra.delete()


# --- START OF NEW CODE FOR INLINE BUTTON HANDLING ---

# Ini adalah handler untuk tombol inline
@ayra_cmd(pattern="^uh_Official_", incoming=True, func=lambda e: e.is_private, is_callback=True)
async def inline_help_handler(event):
    # event.data akan berisi data dari tombol yang dipencet (uh_Official_")
    query_data = event.data.decode("utf-8")

    if query_data == "uh_Official_":
        # Di sini kamu akan membuat isi pesan yang seharusnya muncul setelah tombol dipencet
        # Misalnya, daftar modul inline atau pesan bantuan khusus.
        
        # Contoh sederhana:
        # Dapatkan daftar modul inline yang ada (misal dari HELP atau LIST)
        inline_modules_text = "**Daftar Modul Inline:**\n\n"
        # Asumsi 'HELP' atau 'LIST' memiliki struktur untuk modul inline
        # Ini perlu kamu sesuaikan dengan struktur data bot kamu yang sebenarnya.
        # Contoh:
        # for module_name, commands in LIST.items():
        #     if "inline" in module_name.lower(): # Contoh: jika nama modul mengandung "inline"
        #         inline_modules_text += f"• `{module_name}`\n"
        
        # Untuk demonstrasi, kita akan gunakan teks placeholder
        inline_modules_text += "• Modul Inline 1\n"
        inline_modules_text += "• Modul Inline 2\n"
        inline_modules_text += "\n© @Darensupport"


        await event.edit(inline_modules_text, buttons=[
            Button.inline("Kembali ke Menu Utama", data="main_menu_help") # Contoh tombol kembali
        ])

    # Contoh handler untuk tombol 'Kembali ke Menu Utama'
    elif query_data == "main_menu_help":
        # Kembali menampilkan menu bantuan utama
        await event.edit(
            get_string("inline_4").format(
                OWNER_NAME,
                len(HELP["Official"]),
                len(LIST.values()) + 10, # Perkiraan cmd total, sesuaikan jika perlu
            ),
            buttons=_main_help_menu, # Menampilkan tombol menu utama lagi
        )

# --- END OF NEW CODE ---
