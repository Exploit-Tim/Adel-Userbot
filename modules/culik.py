# Ayra - UserBot
# Copyright (C) 2021-2022 senpai80
#
# This file is a part of < https://github.com/senpai80/Ayra/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/senpai80/Ayra/blob/main/LICENSE/>.
"""
✘ **Bantuan Untuk Culik**

๏ **Perintah:** `invite` <id pengguna>
◉ **Keterangan:** Culik 1 member.

๏ **Perintah:** `inviteall` <username grup>
◉ **Keterangan:** Culik banyak member dari grup tersebut.

◉ **Notes:** Fitur Ini Dilarang Keras Untuk IDC 5 & 6 Karena Akun Anda Akan Ter-Deak.
"""


from telethon import functions
from telethon.errors import (
    ChannelInvalidError,
    ChannelPrivateError,
    ChannelPublicGroupNaError,
    ChatAdminRequiredError, # Import error spesifik ini
    UserAlreadyParticipantError, # Tambahkan ini
    UserNotMutualContactError, # Tambahkan ini
    UserPrivacyRestrictedError, # Tambahkan ini
    FloodWaitError # Tambahkan ini untuk handle rate limit
)
from telethon.tl.functions.channels import (
    GetFullChannelRequest,
    InviteToChannelRequest
)
from telethon.tl.functions.messages import GetFullChatRequest
import asyncio # Import asyncio untuk delay

from . import * # Asumsi ini mengimpor eor, eod, ayra_cmd


async def get_chatinfo(event):
    chat = event.pattern_match.group(1)
    chat_info = None
    if chat:
        try:
            chat = int(chat)
        except ValueError:
            pass
    if not chat:
        if event.reply_to_msg_id:
            replied_msg = await event.get_reply_message()
            if replied_msg.fwd_from and replied_msg.fwd_from.channel_id is not None:
                chat = replied_msg.fwd_from.channel_id
        else:
            chat = event.chat_id
    try:
        chat_info = await event.client(GetFullChatRequest(chat))
    except BaseException:
        try:
            chat_info = await event.client(GetFullChannelRequest(chat))
        except ChannelInvalidError:
            await eor(event, "`Grup tidak ditemukan...`")
            return None
        except ChannelPrivateError:
            await eod(event, "`Sepertinya Grup Private atau Userbot tidak punya akses.`")
            return None
        except ChannelPublicGroupNaError:
            await eod(event, "`Grup tidak ditemukan atau tidak tersedia.`")
            return None
        except (TypeError, ValueError):
            await eod(event, "`Grup tidak ditemukan...`")
            return None
    return chat_info


@ayra_cmd(pattern="invite(?: |$)(.*)")
async def _(event):
    if event.fwd_from:
        return
    to_add_users = event.pattern_match.group(1)
    if event.is_private:
        await eor(
            event,
            "Gunakan format `invite` pengguna ke grup chat, bukan ke Pesan Pribadi.",
        )
        return
    else:
        for user_id_str in to_add_users.split():
            try:
                user_id = int(user_id_str) if user_id_str.isdigit() else user_id_str
                
                await event.client(
                    InviteToChannelRequest(
                        channel=event.chat_id, users=[user_id]
                    )
                )
            except Exception as e:
                error_message = f"**Gagal mengundang {user_id_str}**: `{e}`."
                if isinstance(e, ChatAdminRequiredError):
                    error_message = "**Error**: `Bot perlu menjadi admin dengan izin 'Tambah Anggota' di grup ini.`"
                elif isinstance(e, UserAlreadyParticipantError):
                    error_message = f"**Gagal**: `Pengguna {user_id_str} sudah ada di grup.`"
                elif isinstance(e, UserPrivacyRestrictedError):
                    error_message = f"**Gagal**: `Pengguna {user_id_str} membatasi siapa yang bisa menambahkannya ke grup.`"
                elif isinstance(e, UserNotMutualContactError):
                    error_message = f"**Gagal**: `Pengguna {user_id_str} bukan kontak bersama atau membatasi penambahan.`"
                elif isinstance(e, FloodWaitError):
                    error_message = f"**Warning**: `Terkena batasan Telegram. Tunggu {e.seconds} detik.`"
                    await asyncio.sleep(e.seconds + 2)
                return await eor(event, error_message)
        
        await eor(event, "`Sukses Nyulik Untung Ga Deak...`")


# inviteall Ported By @VckyouuBitch
# From Geez - Projects <https://github.com/vckyou/Geez-UserBot>
# Copyright © Team Geez - Project


@ayra_cmd(pattern="inviteall ?(.*)")
async def get_users(event):
    target_group_username_or_id = event.pattern_match.group(1)
    
    if target_group_username_or_id and not target_group_username_or_id.startswith('@') and not target_group_username_or_id.isdigit():
        target_group_username_or_id = '@' + target_group_username_or_id

    restricted = ["@AstaSupportt", "@astaboynich"]
    
    if target_group_username_or_id.lower() in [r.lower() for r in restricted]:
        await eor(event, "**Dilarang nyulik member dari sana om.**")
        try:
            await event.client.send_message(-1002109872719, "**Mo nyulik kaga bisa.**")
        except Exception as e:
            print(f"Gagal mengirim pesan ke chat restricted: {e}")
        return
        
    if not target_group_username_or_id:
        return await eor(event, "`Berikan username atau ID grup target (tempat member culikan akan dikirim) dan grup sumber (tempat member akan diambil). Contoh: .inviteall <username_grup_target> <username_grup_sumber>`")

    args = target_group_username_or_id.split()
    if len(args) != 2:
        return await eor(event, "`Format salah. Gunakan: .inviteall <username_grup_target> <username_grup_sumber>`")

    target_chat_str = args[0]
    source_chat_str = args[1]

    ayraa = await eor(event, "`Processing....`")
    
    try:
        if target_chat_str.isdigit():
            target_chat_entity = await event.client.get_entity(int(target_chat_str))
        else:
            target_chat_entity = await event.client.get_entity(target_chat_str)
        target_chat_id = target_chat_entity.id
    except Exception:
        return await ayraa.edit("`Grup target tidak ditemukan atau tidak valid.`")

    try:
        if source_chat_str.isdigit():
            source_chat_entity = await event.client.get_entity(int(source_chat_str))
        else:
            source_chat_entity = await event.client.get_entity(source_chat_str)
        source_chat_id = source_chat_entity.id
    except Exception:
        return await ayraa.edit("`Grup sumber tidak ditemukan atau tidak valid.`")

    # Perbaikan: tambahkan 'await' di kedua panggilan event.client.get_me()
    try:
        me_as_participant = await event.client.get_permissions(target_chat_entity, await event.client.get_me())
        if not me_as_participant.is_admin or not me_as_participant.invite_users:
            return await ayraa.edit("**Error**: `Bot harus menjadi admin dengan izin 'Tambah Anggota' di grup target.`")
    except Exception as e:
        return await ayraa.edit(f"**Error memeriksa izin di grup target**: `{e}`. Pastikan bot ada di grup.")
    
    try:
        me_as_participant_source = await event.client.get_permissions(source_chat_entity, await event.client.get_me())
        if not me_as_participant_source.is_admin:
            await ayraa.edit("`Peringatan: Bot bukan admin di grup sumber. Mungkin tidak bisa mendapatkan semua peserta.`")
    except Exception as e:
        # Ini bisa terjadi jika bot tidak ada di grup sumber sama sekali atau grupnya private
        return await ayraa.edit(f"**Error memeriksa izin di grup sumber**: `{e}`. Pastikan bot ada di grup sumber.")

    s = 0
    f = 0
    error = "None"
    await ayraa.edit("`Processing...`")
    async for user in event.client.iter_participants(source_chat_id): # Menggunakan source_chat_id
        # Lewati diri sendiri atau bot lain (opsional)
        if user.is_self or user.bot:
            continue
            
        try:
            await event.client(InviteToChannelRequest(channel=target_chat_id, users=[user.id])) # Menggunakan target_chat_id
            s += 1
            await ayraa.edit(
                f"`Processing...`\n\n• **Berhasil Menambahkan** `{s}` **orang** \n• **Gagal Menambahkan** `{f}` **orang**\n\n** Error:** `{error}`"
            )
            await asyncio.sleep(0.5) # Jeda kecil untuk menghindari FloodWait
        except UserAlreadyParticipantError:
            f += 1
            error = "UserAlreadyParticipantError"
            pass # Lanjutkan tanpa mengubah pesan error terakhir secara global
        except UserPrivacyRestrictedError:
            f += 1
            error = "UserPrivacyRestrictedError"
            pass
        except UserNotMutualContactError:
            f += 1
            error = "UserNotMutualContactError"
            pass
        except FloodWaitError as e:
            await ayraa.edit(f"**Peringatan FloodWait**: `Terkena batasan Telegram. Menunggu {e.seconds} detik...`")
            await asyncio.sleep(e.seconds + 5)
        except ChatAdminRequiredError:
            # Jika tiba-tiba kehilangan admin atau error permission saat invite
            return await ayraa.edit("**Error**: `Bot tidak lagi menjadi admin atau tidak punya izin 'Tambah Anggota' di grup target.`")
        except Exception as e:
            error = str(e)
            f += 1
            pass # Lanjutkan

    return await ayraa.edit(
        f"**Terminal Selesai** \n\n• **Berhasil Menambahkan** `{s}` **orang** \n• **Gagal Menambahkan** `{f}` **orang**"
    )
