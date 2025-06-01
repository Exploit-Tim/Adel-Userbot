# Ayra - UserBot
# Copyright (C) 2021-2022 senpai80
#
# This file is a part of < https://github.com/senpai80/Ayra/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/senpai80/Ayra/blob/main/LICENSE/>.

from Ayra.dB._core import HELP, LIST # Pastikan path ini benar
from Ayra.fns.tools import cmd_regex_replace
from telethon import events # Pastikan ini sudah diimpor
from telethon.errors.rpcerrorlist import (BotInlineDisabledError,
                                          BotMethodInvalidError,
                                          BotResponseTimeoutError)
from telethon.tl.custom import Button
import asyncio # Diperlukan untuk async sleep, jika ada (misal di inviteall)

from . import HNDLR, LOGS, asst, ayra_cmd, get_string # Pastikan semua import ini ada, termasuk eor, eod, dll.

# Asumsi OWNER_NAME didefinisikan di scope yang bisa diakses di sini
# Contoh: OWNER_NAME = "Nama Pemilik Bot"

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
            # Perhatikan: asst.me.username ini membutuhkan bot inline kamu aktif dan username-nya terdefinisi
            results = await ayra.client.inline_query(asst.me.username, "ayra")
        except BotMethodInvalidError:
            # Fallback jika bot inline tidak aktif atau ada masalah
            total_commands = sum(len(cmds) for cmds in LIST.values()) # Menghitung total commands
            return await ayra.reply(
                get_string("inline_4").format(
                    OWNER_NAME,
                    len(HELP["Official"]), # Jumlah modul "Official"
                    total_commands, # Total Commands
                ),
                buttons=_main_help_menu,
            )
        except BotResponseTimeoutError:
            return await ayra.eor(
                get_string("help_2").format(HNDLR),
            )
        except BotInlineDisabledError:
            return await ayra.eor(get_string("help_3"))
        
        # Ini adalah bagian yang akan memicu hasil inline query (jika berhasil)
        # Jika inline query berhasil, bot akan mengirim pesan inline hasil query.
        # Jika ingin selalu menggunakan inline button di bawah pesan utama (tanpa inline query bot),
        # maka bagian ini perlu diubah untuk langsung ayra.reply/eor dengan _main_help_menu.
        # Untuk saat ini, saya biarkan sesuai logika aslinya yang mencoba inline query dulu.
        await results[0].click(chat.id, reply_to=ayra.reply_to_msg_id, hide_via=True)
        await ayra.delete()


# --- START OF NEW CODE FOR INLINE BUTTON HANDLING ---

# Handler untuk tombol "Module" (data="uh_Official_")
@ayra_cmd(pattern="^uh_Official_", incoming=True, func=lambda e: e.is_private, is_callback=True)
async def inline_help_modules_handler(event):
    # event.data akan berisi data dari tombol yang dipencet ("uh_Official_")
    query_data = event.data.decode("utf-8")

    if query_data == "uh_Official_":
        # Di sini kamu akan membuat isi pesan yang seharusnya muncul setelah tombol dipencet
        # Misalnya, daftar modul inline atau pesan bantuan khusus.
        
        module_list_text = f"**{get_string('help_4')}**\n\n" # Menggunakan get_string untuk judul
        
        # Iterasi melalui LIST untuk mendapatkan nama-nama modul
        # Asumsi 'LIST' adalah dictionary dengan keys sebagai nama modul
        module_names = sorted([name for name in LIST.keys() if not name.startswith("_")]) # Filter modul internal
        
        if module_names:
            for module_name in module_names:
                module_list_text += f"• `{module_name}`\n"
        else:
            module_list_text += "Tidak ada modul yang ditemukan.\n"
        
        module_list_text += "\n\n**Untuk melihat detail perintah:**\n` .help <nama_modul>`"
        module_list_text += "\n© @Darensupport"

        # Kirim respons (mengedit pesan sebelumnya agar terlihat mulus)
        # Tombol untuk kembali ke menu utama
        await event.edit(module_list_text, buttons=[
            Button.inline("Kembali ke Menu Utama", data="main_menu_help")
        ])
    else:
        # Ini seharusnya tidak tercapai jika pattern sudah spesifik
        LOGS.warning(f"Unexpected callback data received: {query_data}")
        await event.answer("Terjadi kesalahan, coba lagi.")

# Handler untuk tombol "Kembali ke Menu Utama" (data="main_menu_help")
@ayra_cmd(pattern="^main_menu_help", incoming=True, func=lambda e: e.is_private, is_callback=True)
async def back_to_main_menu_handler(event):
    # Hitung total perintah lagi untuk menu utama
    total_commands = sum(len(cmds) for cmds in LIST.values())

    await event.edit(
        get_string("inline_4").format(
            OWNOR_NAME, # Gunakan OWNER_NAME
            len(HELP["Official"]),
            total_commands,
        ),
        buttons=_main_help_menu, # Menampilkan tombol menu utama lagi
    )

# --- END OF NEW CODE ---
