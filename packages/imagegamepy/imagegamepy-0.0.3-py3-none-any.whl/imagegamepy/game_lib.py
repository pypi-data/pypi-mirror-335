import tkinter as tk
from PIL import Image, ImageTk, ImageFilter, ImageDraw, ImageSequence, ImageOps
import random, json, os, keyboard
from pygame import mixer
from ffpyplayer.player import MediaPlayer
import numpy as np

class StoryWindow:
    def __init__(self, background_image_address=None, background_color="#FFFFFF", warm=0, noise_params=None):
        self.root = tk.Tk()
        self.root.title("Story Telling Game")
        self.canvas = tk.Canvas(self.root, width=800, height=600)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self.resize_image)
        
        self.background_color = background_color
        self.noise_params = noise_params
        self.warm = warm

        if background_image_address:
            try:
                self.original_image = Image.open(background_image_address).convert("RGB")
            except Exception as e:
                raise ValueError("Invalid background image address: " + str(e))
        else:
            self.original_image = Image.new("RGB", (800, 600), background_color)

        self.background_image = self.apply_warm(self.original_image.copy(), self.warm)
        self.photo = ImageTk.PhotoImage(self.background_image)
        self.image_id = self.canvas.create_image(0, 0, anchor="nw", image=self.photo)

        if self.noise_params:
            self.root.after(200, self.apply_noise_loop)
        
        self.dialog_rect = None
        self.dialog_text = None
        self.option_box = None
        self.option_box_items = []
        self.option_highlight = None
        self.current_option_index = 0
        self.option_chosen = tk.BooleanVar(value=False)
        self.option_result = None
        
        # Resource settings placeholders
        self.audio_volume = 50
        self.audio_file = None
        self.png_settings = {}
        self.gif_settings = {}
        self.video_settings = {}
        self.video_player = None
        self.video_frame = None  # holds current video frame PhotoImage
        
        # Initialize pygame mixer for audio if available
        if mixer:
            mixer.init()
        self.gameData()

    def gameData(self):
        GAME_FILE = 'gamedata.json'
        if not os.path.exists(GAME_FILE):
            with open(GAME_FILE, 'w') as f:
                json.dump([{'state': ''}, {'story': []}], f)
        try:
            with open(GAME_FILE, "r") as file:
                data = json.load(file)
                if not isinstance(data, list):
                    data = []
                return data
        except json.JSONDecodeError:
            return []


    def is_key_pressed(self, key):
        """
    Checks if a specific key is currently pressed.
    
    :param key: The key to check (e.g., 'enter', 'a', 'space', etc.).
    :return: True if the key is pressed, False otherwise.
    """
        return keyboard.is_pressed(key)

    def resize_image(self, event):
        new_width, new_height = event.width, event.height
        resized_image = self.original_image.resize((new_width, new_height), Image.LANCZOS)
        self.background_image = self.apply_warm(resized_image, self.warm)
        self.photo = ImageTk.PhotoImage(self.background_image)
        self.canvas.itemconfig(self.image_id, image=self.photo)
        self.close_text_box()
        self.close_option_box()

    def apply_warm(self, image, warm):
        if warm == 0:
            return image
        factor = abs(warm) / 100.0
        overlay_color = (0, 0, 255) if warm < 0 else (255, 0, 0)
        overlay = Image.new("RGB", image.size, overlay_color)
        return Image.blend(image, overlay, factor)

    def apply_noise(self, image):
        randomness, pattern, blur_val = self.noise_params
        if pattern not in ["HL", "VL", "CL"]:
            raise ValueError("unrecognized noise patterns")
        noise_overlay = Image.new("RGB", image.size, (0, 0, 0))
        draw = ImageDraw.Draw(noise_overlay)
        width, height = image.size
        num_elements = max(int(randomness * 10 / 100), 1)
        if pattern == "HL":
            for _ in range(num_elements):
                y = random.randint(0, height - 1)
                thickness = random.randint(1, 7)
                color = (random.randint(100,200), random.randint(100,200), random.randint(100,200))
                draw.rectangle([0, y, width, y+thickness], fill=color)
        elif pattern == "VL":
            for _ in range(num_elements):
                x = random.randint(0, width - 1)
                thickness = random.randint(1, 7)
                color = (random.randint(100,200), random.randint(100,200), random.randint(100,200))
                draw.rectangle([x, 0, x+thickness, height], fill=color)
        elif pattern == "CL":
            for _ in range(num_elements):
                radius = random.randint(5,20)
                x = random.randint(0, width)
                y = random.randint(0, height)
                color = (random.randint(100,200), random.randint(100,200), random.randint(100,200))
                draw.ellipse([x-radius, y-radius, x+radius, y+radius], outline=color, width=1)
        if blur_val > 0:
            noise_overlay = noise_overlay.filter(ImageFilter.GaussianBlur(radius=blur_val/10.0))
        return Image.blend(image, noise_overlay, 0.3)

    def apply_noise_loop(self):
        noisy_image = self.apply_noise(self.background_image)
        self.photo = ImageTk.PhotoImage(noisy_image)
        self.canvas.itemconfig(self.image_id, image=self.photo)
        self.root.after(200, self.apply_noise_loop)

    def update_background(self):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        resized_image = self.original_image.resize((width, height), Image.LANCZOS)
        self.background_image = self.apply_warm(resized_image, self.warm)
        self.photo = ImageTk.PhotoImage(self.background_image)
        self.canvas.itemconfig(self.image_id, image=self.photo)

    def set_warm(self, new_warm, step=1, delay=50):
        if self.warm == new_warm:
            return
        diff = new_warm - self.warm
        if abs(diff) < step:
            self.warm = new_warm
        else:
            self.warm += step if diff > 0 else -step
        self.update_background()
        self.root.after(delay, self.set_warm, new_warm, step, delay)

    def set_background_image(self, background_image_address):
        try:
            self.original_image = Image.open(background_image_address).convert("RGB")
        except Exception as e:
            raise ValueError("Invalid background image address: " + str(e))
        self.update_background()

    def set_background_color(self, background_color):
        self.background_color = background_color
        self.original_image = Image.new("RGB", (self.canvas.winfo_width(), self.canvas.winfo_height()), background_color)
        self.update_background()

    def set_noise_params(self, noise_params):
        self.noise_params = noise_params

    def dialog(self, text, text_color="white", speed=50, position="bottom left", dialog_box_color="black"):
    # Remove any existing dialog widget
        if hasattr(self, 'dialog_widget'):
            self.dialog_widget.destroy()
            del self.dialog_widget

        # Calculate dialog box coordinates based on position
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if position.lower() == "bottom left":
            x1, y1 = 10, canvas_height - 160
            x2, y2 = canvas_width // 2, canvas_height - 10
        elif position.lower() == "bottom right":
            x1, y1 = canvas_width // 2, canvas_height - 160
            x2, y2 = canvas_width - 10, canvas_height - 10
        elif position.lower() == "top left":
            x1, y1 = 10, 10
            x2, y2 = canvas_width // 2, 150
        elif position.lower() == "top right":
            x1, y1 = canvas_width // 2, 10
            x2, y2 = canvas_width - 10, 150
        elif position.lower() == "center":
            box_width = int(canvas_width * 0.6)
            box_height = 150
            x1 = (canvas_width - box_width) // 2
            y1 = (canvas_height - box_height) // 2
            x2 = x1 + box_width
            y2 = y1 + box_height
        else:
            x1, y1 = 10, canvas_height - 160
            x2, y2 = canvas_width // 2, canvas_height - 10

    # Draw or update the dialog rectangle background
        if self.dialog_rect is not None:
            self.canvas.delete(self.dialog_rect)
        self.dialog_rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=dialog_box_color, outline="", stipple="gray50")

    # Compute inner dimensions with some padding
        width_px = x2 - x1 - 20
        height_px = y2 - y1 - 20

    # Create an embedded Text widget in the canvas for wrapped and scrollable text
        self.dialog_widget = tk.Text(self.canvas, wrap="word", bg=dialog_box_color, fg=text_color, font=("Helvetica", 14), bd=10, highlightthickness=0)
        self.dialog_widget.config(state="disabled")  # make it read-only
    # Embed the Text widget in the canvas
        self.canvas.create_window(x1+10, y1+10, anchor="nw", window=self.dialog_widget ,width=width_px, height=height_px)

    # Optionally bind mousewheel scrolling to the text widget (works on Windows)
        def _on_mousewheel(event):
            self.dialog_widget.yview_scroll(-1 * (event.delta // 120), "units")
        self.dialog_widget.bind("<MouseWheel>", _on_mousewheel)

    # Animate text insertion letter-by-letter, auto-scrolling as needed
        def animate(i=0):
            if i <= len(text):
                self.dialog_widget.config(state="normal")
                self.dialog_widget.delete("1.0", "end")
                self.dialog_widget.insert("end", text[:i])
                self.dialog_widget.see("end")  # auto-scroll to the bottom if text exceeds view
                self.dialog_widget.config(state="disabled")
                self.root.after(speed, animate, i+1)
        animate()


    def close_text_box(self):
        if self.dialog_rect is not None:
            self.canvas.delete(self.dialog_rect)
            self.dialog_rect = None
            if hasattr(self, 'dialog_widget'):
                self.dialog_widget.destroy()
                del self.dialog_widget
        if self.dialog_text is not None:
            self.canvas.delete(self.dialog_text)
            self.dialog_text = None

    def option(self, option_list, option_background_color='', option_list_color='', save_type='default', id='interface'):
        self.canvas.update()  # Ensure canvas dimensions are updated
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        box_width = int(canvas_width * 0.6)
        box_height = len(option_list) * 35 + 20
        x1 = (canvas_width - box_width) // 2
        y1 = (canvas_height - box_height) // 2
        x2 = x1 + box_width
        y2 = y1 + box_height
        self.option_box = self.canvas.create_rectangle(x1, y1, x2, y2, fill=option_background_color, outline="", stipple="gray50")
        self.option_box_items = []
        self.current_option_index = 0
        for i, opt in enumerate(option_list):
            option_y = y1 + 20 + i * 35
            text_id = self.canvas.create_text((x1+x2)//2, option_y, text=opt, fill=option_list_color, font=("Helvetica", 14))
            self.option_box_items.append(text_id)
        self.option_highlight = self.canvas.create_rectangle(x1, y1 + 10 + self.current_option_index * 35 - 2,
                                                               x2, y1 + 10 + self.current_option_index * 35 + 33,
                                                               outline="yellow", width=2)
        self.option_result = None
        self.option_chosen = tk.BooleanVar(value=False)
        self.root.bind("<Up>", lambda event: self._option_up(x1, y1, x2, y2))
        self.root.bind("<Down>", lambda event: self._option_down(x1, y1, x2, y2, len(option_list)))
        self.root.bind("<Return>", lambda event: self._option_enter(option_list, save_type, id))
        self.root.wait_variable(self.option_chosen)
        self.root.unbind("<Up>")
        self.root.unbind("<Down>")
        self.root.unbind("<Return>")
        self.canvas.delete(self.option_box)
        for item in self.option_box_items:
            self.canvas.delete(item)
        self.canvas.delete(self.option_highlight)
        return self.option_result

    def _option_up(self, x1, y1, x2, y2):
        if self.current_option_index > 0:
            self.current_option_index -= 1
            self._update_option_highlight(x1, y1, x2, y2)

    def _option_down(self, x1, y1, x2, y2, total):
        if self.current_option_index < total - 1:
            self.current_option_index += 1
            self._update_option_highlight(x1, y1, x2, y2)

    def _update_option_highlight(self, x1, y1, x2, y2):
        self.canvas.coords(self.option_highlight, x1, y1 + 10 + self.current_option_index * 35 - 2,
                           x2, y1 + 10 + self.current_option_index * 35 + 33)

    def _option_enter(self, option_list, save_type, id):
        chosen = option_list[self.current_option_index]
        result = {"options": option_list, "choice": chosen}
        if save_type == 'json':
            data = self.gameData()
            if id == "interface":
                data[0] = result
            else:
                result = {"id": id, "choice": chosen}
                data[1]['story'].append(result)
            with open("gamedata.json", "w") as f:
                json.dump(data, f)
        self.option_result = result 
        self.option_chosen.set(True)
        self.close_option_box()
    def return_options(self, id=None):
        with open('gamedata.json', 'r') as g:
            data = json.load(g)
        if id is None or id == '':
            return data[0].get("choice")
        elif id == 'checkmem':
            story_list = data[1].get("story", [])
            if story_list:
                return story_list[-1].get("id")  # Return the last executed option ID
            else:
                return None
        else:
            story_list = data[1].get("story", [])
            for item in story_list:
                if item.get("id") == str(id):
                    return item.get("choice")
        return None

    def close_option_box(self):
        if self.option_box is not None:
            self.canvas.delete(self.option_box)
            self.option_box = None
        if self.option_box_items:
            for item in self.option_box_items:
                self.canvas.delete(item)
            self.option_box_items = []
        if self.option_highlight is not None:
            self.canvas.delete(self.option_highlight)
            self.option_highlight = None

    def load(self, resource_type, settings, address, l=''):
        if resource_type not in ['png', 'gif', 'audio', 'video']:
            raise ValueError("Unsupported resource type: " + resource_type)
        # For audio: settings is an int volume (0-100)
        if resource_type == 'audio':
            if not (isinstance(settings, int) and 0 <= settings <= 100):
                raise ValueError("For audio, settings must be an integer between 0 and 100 representing volume.")
            if not mixer:
                raise ImportError("pygame is required for audio playback.")
            self.audio_volume = settings
            self.audio_file = address
            sound = mixer.Sound(address)
            if l == 'l':
                sound = mixer.Sound(address)
                sound.set_volume(settings / 100.0)
                sound.play(loops=-1)
            else:
                sound.set_volume(settings / 100.0)
                sound.play()
            return f"Audio file '{address}' loaded and playing with volume {settings}"
        # For images (png/gif): settings is [scale, position]
        elif resource_type in ['png', 'gif']:
            if not (isinstance(settings, list) and len(settings) == 2):
                raise ValueError(f"For {resource_type}, settings must be a list with [scale, position].")
            try:
                img = Image.open(address)
            except Exception as e:
                raise ValueError("Cannot open image file: " + str(e))
            if resource_type == 'png' and img.format.lower() not in ['png','jpg','jpeg']:
                raise ValueError("File format not supported for png. Supported: png, jpg, jpeg.")
            scaled_img = img.resize(settings[0], Image.LANCZOS)
            photo_img = ImageTk.PhotoImage(scaled_img)
            pos = settings[1]
            self.canvas.create_image(pos[0], pos[1], image=photo_img, anchor="nw")
            if resource_type == 'png':
                self.png_settings = {"scale": settings[0], "position": pos, "file": address, "photo": photo_img}
                return f"PNG file '{address}' loaded with scale {settings[0]} and position {pos}"
            else:
                frames = []
                try:
                    for frame in ImageSequence.Iterator(img):
                        frame = frame.resize(settings[0], Image.LANCZOS)
                        frames.append(ImageTk.PhotoImage(frame))
                except Exception:
                    frames = [photo_img]
                self.gif_settings = {"scale": settings[0], "position": pos, "file": address, "frames": frames}
                def animate_gif(frame_index=0):
                    self.canvas.create_image(pos[0], pos[1], image=frames[frame_index], anchor="nw")
                    self.root.after(100, animate_gif, (frame_index + 1) % len(frames))
                animate_gif()
                return f"GIF file '{address}' loaded with scale {settings[0]} and position {pos}"
        # For video: settings is [volume, scale, position]
        elif resource_type == 'video':
            if not (isinstance(settings, list) and len(settings) == 3):
                raise ValueError("For video, settings must be a list with [volume, scale, position].")
            if not (isinstance(settings[0], int) and 0 <= settings[0] <= 100):
                raise ValueError("Video volume must be an integer between 0 and 100.")
            self.video_settings = {"volume": settings[0], "scale": settings[1], "position": settings[2], "file": address}
            self.video_player = MediaPlayer(address, ff_opts={'paused': False, 'out_fmt': 'rgb24', 'volume': settings[0]/100.0})
            self.update_video()
            return f"Video file '{address}' loaded with volume {settings[0]}, scale {settings[1]}, and position {settings[2]}"

    def update_video(self):
        if self.video_player is None:
            return
        frame, val = self.video_player.get_frame()
        if frame is None:
            self.root.after(30, self.update_video)
            return
        img, pts = frame

        w, h = img.get_size()
        img_bytes = img.to_bytearray()[0]
        np_img = np.frombuffer(img_bytes, dtype=np.uint8).reshape((h, w, 3))  # 3 channels = RGB

        pil_img = Image.fromarray(np_img)

        scale = self.video_settings.get("scale", (self.canvas.winfo_width(), self.canvas.winfo_height()))
        pil_img = pil_img.resize(scale, Image.LANCZOS)

        self.video_frame = ImageTk.PhotoImage(pil_img)
        pos = self.video_settings.get("position", (0, 0))
        self.canvas.create_image(pos[0], pos[1], image=self.video_frame, anchor="nw")
        self.root.after(30, self.update_video)


    def start(self):
        self.root.mainloop()

def body(background_image_address=None, background_color="#FFFFFF", warm=0, noise=None):
    window = StoryWindow(background_image_address, background_color, warm, noise)
    return window

def noise(randomness, pattern, blur_val):
    if pattern not in ["HL", "VL", "CL"]:
        raise ValueError("unrecognized noise patterns")
    if not (0 <= randomness <= 100) or not (0 <= blur_val <= 100):
        raise ValueError("randomness and blur_val must be between 0 and 100")
    return (randomness, pattern, blur_val)