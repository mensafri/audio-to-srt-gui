import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext
import threading
import whisper
import srt
from datetime import timedelta
import time
import os


# Fungsi untuk memilih file audio
def pilih_file_audio():
    file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")])
    if file_path:
        label_file.config(text=file_path)
        btn_convert.config(state="normal")


# Fungsi untuk konversi audio ke subtitle menggunakan Whisper
def convert_audio_to_srt():
    file_path = label_file.cget("text")
    if not file_path:
        label_status.config(text="Tidak ada file audio yang dipilih.")
        return

    btn_convert.config(state="disabled")
    label_status.config(text="Proses konversi dimulai...")
    progress_bar['value'] = 0
    output_log.delete(1.0, tk.END)

    # Mulai pencatatan waktu
    start_time = time.time()

    # Load Whisper model
    model = whisper.load_model("base")

    # Mulai transkripsi
    result = model.transcribe(file_path)
    segments = result["segments"]  # Ambil daftar segmen hasil transkripsi

    # Membuat subtitle dari hasil transkripsi
    subtitle = []
    num_segments = len(segments)  # Total segmen untuk progress tracking

    for i, segment in enumerate(segments):
        start = timedelta(seconds=segment["start"])
        end = timedelta(seconds=segment["end"])
        content = segment["text"]

        # Tambahkan setiap segmen ke output_log
        output_log.insert(tk.END, f"Teks potongan {i + 1}: {content}\n")

        # Buat objek subtitle SRT
        subtitle.append(srt.Subtitle(index=i + 1, start=start, end=end, content=content))

        # Update progress bar
        progress = ((i + 1) / num_segments) * 100
        progress_bar['value'] = progress
        window.update_idletasks()  # Update GUI untuk tampilan progress real-time

    # Menyimpan file .srt ke folder Downloads
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    srt_filename = f"C:\\Users\\Safri\\Downloads\\{base_name}.srt"
    with open(srt_filename, "w") as srt_file:
        srt_file.write(srt.compose(subtitle))

    # Hitung lama waktu proses
    end_time = time.time()
    elapsed_time = end_time - start_time
    elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))

    label_status.config(text=f"Subtitle berhasil dibuat: '{srt_filename}'\nLama Waktu Proses: {elapsed_str}")
    btn_convert.config(state="normal")


# Fungsi untuk menjalankan konversi di thread terpisah
def start_conversion_thread():
    conversion_thread = threading.Thread(target=convert_audio_to_srt)
    conversion_thread.start()


# Membuat GUI dengan tkinter
window = tk.Tk()
window.title("Audio to SRT Converter")
window.geometry("500x500")

frame = tk.Frame(window)
frame.pack(padx=10, pady=10)

label_intro = tk.Label(frame, text="Pilih file audio untuk dikonversi ke SRT:")
label_intro.pack()

btn_pilih_file = tk.Button(frame, text="Pilih File Audio", command=pilih_file_audio)
btn_pilih_file.pack(pady=5)

label_file = tk.Label(frame, text="Tidak ada file audio yang dipilih.")
label_file.pack()

# Progress bar untuk menampilkan kemajuan proses konversi
progress_bar = ttk.Progressbar(frame, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=5)

btn_convert = tk.Button(frame, text="Mulai Konversi", command=start_conversion_thread, state="disabled")
btn_convert.pack(pady=5)

# Scrolled text untuk menampilkan log proses
output_log = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=50, height=10)
output_log.pack(pady=5)

# Label status untuk menampilkan status akhir proses dan waktu proses
label_status = tk.Label(frame, text="")
label_status.pack()

window.mainloop()
