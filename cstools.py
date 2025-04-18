import tkinter as tk
from tkinter import Scrollbar, ttk  # Import ttk for Progressbar
from PIL import Image, ImageTk  # Import PIL library for working with images
from telethon.sync import TelegramClient
from telethon import functions
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch, ChannelParticipantsAdmins
import phonenumbers
from phonenumbers import carrier, number_type, PhoneNumberType, is_possible_number, is_valid_number
import json
import webbrowser  # Import the webbrowser module to open links
import asyncio
import threading
import requests
import re

# Initialize the Telegram client https://my.telegram.org/auth
api_id = 'Inserisci qui API ID'  # Replace with your API ID
api_hash = 'Inserisci qui API HASH'  # Replace with your API Hash
client = TelegramClient("anon", api_id, api_hash)

# Functions to execute different queries
async def get_user_data(user_id):
    try:
        user = await client.get_entity(user_id)
        full_user = await client(functions.users.GetFullUserRequest(id=user_id))
        bio = full_user.about if hasattr(full_user, 'about') else "N/A"
        name = f"{user.first_name} {user.last_name if user.last_name else ''}".strip()
        username = f"@{user.username}" if user.username else "N/A"
        return f"\nName: {name}\nUsername: {username}\nBio: {bio}"
    except Exception as e:
        return f"Errore: {e}"

async def get_group_members(channel_input):
    try:
        if channel_input.startswith("https://"):
            channel_input = channel_input.split("/")[-1]
        
        channel_entity = await client.get_entity(channel_input)
        full_channel = await client(functions.channels.GetFullChannelRequest(channel=channel_entity))

        # Ottieni la lista completa dei partecipanti del canale/gruppo
        participants = []
        async for participant in client.iter_participants(channel_entity):
            participants.append(participant)
            progress = int((len(participants) / full_channel.full_chat.participants_count) * 100)
            percentage.set(f"{progress}%")
            progress_bar['value'] = progress
            await asyncio.sleep(0.01)  # Simulate work being done

        # Creazione di una lista dei partecipanti
        members_list = ""
        for participant in participants:
            members_list += f"{participant.id} - {participant.first_name} {participant.last_name if participant.last_name else ''}\n"

        group_info = [
            ("Nome del gruppo", channel_entity.title),
            ("Link del gruppo", f"https://t.me/{channel_entity.username}" if channel_entity.username else "N/A"),
            ("ID del gruppo", str(channel_entity.id)),
            ("Bio", full_channel.full_chat.about or "N/A"),
            ("Numero di iscritti", len(participants))
        ]

        info_str = "\n".join([f"{info[0]}: {info[1]}" for info in group_info])
        info_str += f"\n\nLista membri:\n{members_list}"

        return f"{info_str}\n\nCaricamento completato!"

    except Exception as e:
        return f"Errore: {e}"

async def phone_info(phone_number):
    try:
        parsed = phonenumbers.parse(phone_number)
        operator = carrier.name_for_number(parsed, "en")
        line = number_type(parsed)

        line_type = ""
        if line == PhoneNumberType.FIXED_LINE:
            line_type = "Linea fissa"
        elif line == PhoneNumberType.MOBILE:
            line_type = "Telefono cellulare"
        else:
            line_type = "Tipo di linea non trovato"

        possible = is_possible_number(parsed)
        valid = is_valid_number(parsed)

        with open("country.json", "r") as file:
            countries = json.load(file)

        country_list = []

        for country, code in countries.items():
            if phone_number.startswith(code):
                country_list.append(country)

        phone_number_for_links = phone_number.lstrip('+')
        telegram_link = f"https://t.me/+{phone_number_for_links}"
        whatsapp_link = f"https://wa.me/{phone_number}"

        return f"Numero di telefono: {phone_number}\nPossibile: {'✔' if possible else '❌'}\nValido: {'✔' if valid else '❌'}\nOperatore: {operator if operator else 'Non disponibile'}\nPaese possibile: {', '.join(country_list) if country_list else 'Non trovato'}\nTipo di linea: {line_type}\nLink Telegram: {telegram_link}\nLink WhatsApp: {whatsapp_link}\nCaricamento completato!"

    except Exception as e:
        return f"Errore: {e}"

async def username_info(username):
    try:
        results = {}
        social_media = [
            {"url": "https://www.facebook.com/{}", "name": "Facebook"},
            {"url": "https://www.twitter.com/{}", "name": "Twitter"},
            {"url": "https://www.instagram.com/{}", "name": "Instagram"},
            {"url": "https://www.linkedin.com/in/{}", "name": "LinkedIn"},
            {"url": "https://www.github.com/{}", "name": "GitHub"},
            {"url": "https://www.pinterest.com/{}", "name": "Pinterest"},
            {"url": "https://www.tumblr.com/{}", "name": "Tumblr"},
            {"url": "https://www.youtube.com/{}", "name": "YouTube"},
            {"url": "https://soundcloud.com/{}", "name": "SoundCloud"},
            {"url": "https://www.snapchat.com/add/{}", "name": "Snapchat"},
            {"url": "https://www.tiktok.com/@{}", "name": "TikTok"},
            {"url": "https://www.behance.net/{}", "name": "Behance"},
            {"url": "https://www.medium.com/@{}", "name": "Medium"},
            {"url": "https://www.quora.com/profile/{}", "name": "Quora"},
            {"url": "https://www.flickr.com/people/{}", "name": "Flickr"},
            {"url": "https://www.periscope.tv/{}", "name": "Periscope"},
            {"url": "https://www.twitch.tv/{}", "name": "Twitch"},
            {"url": "https://www.dribbble.com/{}", "name": "Dribbble"},
            {"url": "https://www.stumbleupon.com/stumbler/{}", "name": "StumbleUpon"},
            {"url": "https://www.ello.co/{}", "name": "Ello"},
            {"url": "https://www.producthunt.com/@{}", "name": "Product Hunt"},
            {"url": "https://www.telegram.me/{}", "name": "Telegram"},
            {"url": "https://www.weheartit.com/{}", "name": "We Heart It"},
            {"url": "https://truthsocial.com/api/v1/accounts/lookup?acct={username}", "name": "truthsocial"},
            {"url": "https://api.nostr.wine/search?query={username}", "name": "wine"},
            {"url": "https://mastodon.social/api/v2/search?q={username}", "name": "mastodon"},
            {"url": "https://bsky.app/profile/{username}.bsky.social", "name": "BluSky"},
            {"url": "https://www.snapchat.com/add/{username}", "name": "snapchat"},
        ]
        
        total_sites = len(social_media)
        for i, site in enumerate(social_media):
            url = site['url'].format(username)
            response = requests.get(url)
            if response.status_code == 200:
                results[site['name']] = url
            else:
                results[site['name']] = "Nessun RISULTATO"
            progress = int(((i + 1) / total_sites) * 100)
            percentage.set(f"{progress}%")
            progress_bar['value'] = progress
            await asyncio.sleep(0.1)  # Simulate work being done

        # Format results with clickable links and red color for "Nessun RISULTATO"
        formatted_results = []
        for site, url in results.items():
            if url.startswith("http"):
                if url == "Nessun RISULTATO":
                    formatted_results.append(f"{site}: <font color='red'>{url}</font>")
                else:
                    formatted_results.append(f"{site}: {url}")
            else:
                formatted_results.append(f"{site}: {url}")

        info_str = "\n".join(formatted_results)
        return f"{info_str}\n\nCaricamento completato!"

    except Exception as e:
        return f"Errore: {e}"

def make_clickable(widget):
    text = widget.get("1.0", "end")
    urls = re.findall(r'(https?://\S+)', text)
    for url in urls:
        widget.tag_config("link", foreground="blue", underline=1)
        widget.tag_bind("link", "<Button-1>", lambda event, link=url: webbrowser.open_new(link))

# Function to start the Telegram client
async def start_client():
    await client.start()

# Functions for searches
async def search_user():
    user_id = user_id_entry.get()
    result_text.configure(state='normal')
    result_text.delete('1.0', tk.END)
    progress_bar['value'] = 0
    percentage.set("0%")
    result_text.insert(tk.END, await get_user_data(user_id))
    percentage.set("100%")
    progress_bar['value'] = 100
    result_text.configure(state='disabled')
    make_clickable(result_text)

async def search_group():
    group_name_or_link = group_entry.get()
    result_text.configure(state='normal')
    result_text.delete('1.0', tk.END)
    progress_bar['value'] = 0
    percentage.set("0%")
    result_text.insert(tk.END, await get_group_members(group_name_or_link))
    percentage.set("100%")
    progress_bar['value'] = 100
    result_text.configure(state='disabled')
    make_clickable(result_text)

async def search_phone():
    phone_number = phone_entry.get()
    result_text.configure(state='normal')
    result_text.delete('1.0', tk.END)
    progress_bar['value'] = 0
    percentage.set("0%")
    result_text.insert(tk.END, await phone_info(phone_number))
    percentage.set("100%")
    progress_bar['value'] = 100
    result_text.configure(state='disabled')
    make_clickable(result_text)

async def search_username():
    username = username_entry.get()
    result_text.configure(state='normal')
    result_text.delete('1.0', tk.END)
    progress_bar['value'] = 0
    percentage.set("0%")
    result_text.insert(tk.END, await username_info(username))
    percentage.set("100%")
    progress_bar['value'] = 100
    result_text.configure(state='disabled')
    make_clickable(result_text)

def open_link(event):
    try:
        text = result_text.get(tk.CURRENT)
        start_index = result_text.index(tk.CURRENT + " linestart")
        end_index = result_text.index(tk.CURRENT + " lineend")
        line_text = text[start_index:end_index]

        # Check if line contains a link
        if line_text.startswith("Link del gruppo: ") or line_text.startswith("Link Telegram: ") or line_text.startswith("Link WhatsApp: "):
            url = line_text.split(": ")[1]
            webbrowser.open_new(url)
    except Exception as e:
        print(f"Errore nell'apertura del link: {e}")

# Function to copy the result to clipboard
def copy_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append(result_text.get('1.0', tk.END))
    root.update()  # now it stays on the clipboard after the window is closed

# Function to reset the input fields and result
def reset_fields():
    user_id_entry.delete(0, tk.END)
    group_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)
    username_entry.delete(0, tk.END)
    result_text.configure(state='normal')
    result_text.delete('1.0', tk.END)
    result_text.configure(state='disabled')
    logo_button.grid(row=0, column=0, columnspan=4)
    instructions_label.grid(row=1, column=0, columnspan=4)

# Function to save the result to a CSV file
def save_to_csv():
    with open("output.csv", mode='w', newline='') as file:
        file.write(result_text.get('1.0', tk.END))
    result_text.configure(state='normal')
    result_text.delete('1.0', tk.END)
    result_text.insert(tk.END, f"Risultato salvato in output.csv")
    result_text.configure(state='disabled')

# Function to open the webpage
def open_webpage():
    webbrowser.open_new("https://cscorza.github.io/CScorza/")

# Create the GUI
def run_gui(loop):
    global user_id_entry, group_entry, phone_entry, username_entry, result_text, root, logo_button, instructions_label, progress_bar, percentage
    
    root = tk.Tk()
    root.resizable(False, False)
    root.title("CScorza Tools")

    # Load the logo image and resize it by 50%
    logo_image = Image.open("./logo/logo.gif")
    logo_image = logo_image.resize((logo_image.width // 2, logo_image.height // 2))
    logo_photo = ImageTk.PhotoImage(logo_image)

    # Display logo as a button
    logo_button = tk.Button(root, image=logo_photo, command=open_webpage)
    logo_button.grid(row=0, column=0, columnspan=4, pady=5)

    # Instructions label
    instructions_label = tk.Label(root, text="CScorza - Indagini Telematiche")
    instructions_label.grid(row=1, column=0, columnspan=4, pady=5)

    tk.Label(root, text="Ricerca Account Telegram:").grid(row=2, column=0, pady=5)
    user_id_entry = tk.Entry(root)
    user_id_entry.grid(row=2, column=1, pady=5)
    tk.Button(root, text="Cerca", command=lambda: asyncio.run_coroutine_threadsafe(search_user(), loop)).grid(row=2, column=2, pady=5)

    tk.Label(root, text="Ricerca Gruppo Telegram:").grid(row=3, column=0, pady=5)
    group_entry = tk.Entry(root)
    group_entry.grid(row=3, column=1, pady=5)
    tk.Button(root, text="Cerca", command=lambda: asyncio.run_coroutine_threadsafe(search_group(), loop)).grid(row=3, column=2, pady=5)

    tk.Label(root, text="Ricerca Numero di Telefono:").grid(row=4, column=0, pady=5)
    phone_entry = tk.Entry(root)
    phone_entry.grid(row=4, column=1, pady=5)
    tk.Button(root, text="Cerca", command=lambda: asyncio.run_coroutine_threadsafe(search_phone(), loop)).grid(row=4, column=2, pady=5)
    
    tk.Label(root, text="Ricerca per Username:").grid(row=5, column=0, pady=5)
    username_entry = tk.Entry(root)
    username_entry.grid(row=5, column=1, pady=5)
    tk.Button(root, text="Cerca", command=lambda: asyncio.run_coroutine_threadsafe(search_username(), loop)).grid(row=5, column=2, pady=5)

    global result_text
    result_text = tk.Text(root, wrap=tk.WORD, width=10, height=10, state='disabled')
    result_text.grid(row=6, column=0, columnspan=3, padx=3, pady=3, sticky="nsew")
         
    # Progress bar and percentage label
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=180, mode="determinate")
    progress_bar.grid(row=7, column=0, padx=(0, 0), pady=(1, 0), sticky='w')
        
    percentage = tk.StringVar()
    percentage.set("0%")
    percentage_label = tk.Label(root, textvariable=percentage)
    percentage_label.grid(row=7, column=0, padx=(0, 0), pady=(1, 0), sticky='w')
        
    # Buttons
    tk.Label(root, text="Attendere il caricamento").grid(row=7, column=1, pady=5)
    tk.Button(root, text="Resetta risultati", command=reset_fields).grid(row=8, column=0, padx=(2, 0), pady=(2, 0), sticky='w')
    tk.Button(root, text="Copia negli appunti", command=copy_to_clipboard).grid(row=8, column=1, padx=(0, 0), pady=(4, 0),     sticky='w')
    tk.Button(root, text="Salva in .CSV", command=save_to_csv).grid(row=8, column=2, padx=(3, 0), pady=(3, 0), sticky='w')

    root.mainloop()    

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    threading.Thread(target=loop.run_forever).start()

    asyncio.run_coroutine_threadsafe(start_client(), loop)

    run_gui(loop)
