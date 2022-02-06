from sanic.response import raw
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
from config import DEFAULT_VERIFY_BACKGROUND
from IMAGES import IMAGE_CONFIG
import aiohttp


class Route:
    PATH = "/verify/front"
    METHODS = ("GET", )

    def __init__(self):
        self.header1 = ImageFont.truetype("fonts/TovariSans.ttf", 100)
        self.header2 = ImageFont.truetype("fonts/TovariSans.ttf", 50)
       # self.header3 = ImageFont.truetype("fonts/cartoonist/TovariSans.ttf", 90)
        self.header4 = ImageFont.truetype("fonts/TovariSans.ttf", 40)
        self.header5 = ImageFont.truetype("fonts/TovariSans.ttf", 30)

        self.session = None

    async def handler(self, request):
        background   = request.args.get("background")
        background   = background if background != "null" and IMAGE_CONFIG.get(background, {}).get("paths", {}).get("verify", {}).get("front") else DEFAULT_VERIFY_BACKGROUND

        username     = request.args.get("username")
        display_name = request.args.get("display_name")
        headshot     = request.args.get("headshot")

        background_path = IMAGE_CONFIG.get(background, {}).get("verify", {}).get("front")

        # image storage for closing
        headshot_image = None

        # buffer storage
        headshot_buffer = None

        if not self.session:
            self.session = aiohttp.ClientSession()

        first_font_size = self.header1
        second_font_size = self.header2

        adjusted_name_pos_1 = 290
        adjusted_name_pos_2 = 370

        if len(username) >= 20:
            username = f"{username[:20]}..."

        if len(display_name) >= 20:
            display_name = f"{display_name[:20]}..."

        if len(username) >= 10 or len(display_name) >= 10:
            first_font_size = self.header2
            second_font_size = self.header2
            adjusted_name_pos_1 = 320
            adjusted_name_pos_2 = 370

        # TODO: if bg is deleted, then revert to default

        with Image.open(background_path) as background_image:
            image = Image.new("RGBA", (background_image.width, background_image.height))

            if headshot:
                async with self.session.get(headshot) as resp:
                    with Image.open("./assets/props/moon.png") as moon_image:
                        with Image.open("./assets/props/moon_outline.png") as moon_outline_image:
                            headshot_buffer = BytesIO(await resp.read())
                            headshot_image  = Image.open(headshot_buffer)
                            headshot_image  = headshot_image.resize((220, 220))

                            image.paste(moon_image, (0, 0), moon_image)
                            image.paste(headshot_image, (160, 70), headshot_image)

                            image.paste(background_image, (0, 0), background_image)
                            image.paste(moon_outline_image, (0, 0), moon_outline_image)


            # if overlay:
            #     with Image.open(f"./assets/props/overlays/{overlay}.png") as overlay_image:
            #         image.paste(overlay_image, (0, 0), overlay_image)

            draw = ImageDraw.Draw(image)

            if username:
                username = f"@{username}"

                if display_name:
                    if username[1:] == display_name:
                        # header is username. don't display display_name
                        width_username = draw.textsize(username, font=first_font_size)[0]

                        draw.text(
                            ((image.size[0]-width_username) / 2, adjusted_name_pos_1),
                            username,
                            (255, 255, 255),
                            font=first_font_size
                        )
                    else:
                        # show both username and display name
                        width_display_name  = draw.textsize(display_name, font=first_font_size)[0]
                        draw.text(
                            ((image.size[0]-width_display_name) / 2, adjusted_name_pos_1),
                            display_name,
                            (240, 191, 60),
                            font=first_font_size)

                        width_username = draw.textsize(username, font=second_font_size)[0]
                        draw.text(
                            ((image.size[0]-width_username) / 2, adjusted_name_pos_2),
                            username,
                            (255, 255, 255),
                            font=second_font_size)

                else:
                    width_username = draw.textsize(username, font=first_font_size)[0]

                    draw.text(
                        ((image.size[0]-width_username) / 2, adjusted_name_pos_1),
                        username,
                        (255, 255, 255),
                        font=first_font_size
                    )


            # if roblox_age:
            #     draw.text(
            #         (10, roblox_id_age_offset),
            #         f"Minted {roblox_age}",
            #         (240, 191, 60),
            #         font=self.header5
            #     )

        try:
            with BytesIO() as bf:
                image.save(bf, "PNG", quality=70)
                image.seek(0)

                return raw(bf.getvalue())

        finally:
            if headshot_buffer:
                headshot_buffer.close()

            if image:
                image.close()

            if headshot_image:
                headshot_image.close()
