import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_entry_image():
    width, height = 1024, 1024
    img = Image.new("RGBA", (width, height), (13, 2, 33, 255))
    draw = ImageDraw.Draw(img)

    # 1. Background vertical / diagonal gradient (deep violet to dark indigo)
    for y in range(height):
        factor = y / height
        # lerp from #0b001a to #240046 to #3c096c
        r = int(11 + factor * 40)
        g = int(0 + factor * 5)
        b = int(26 + factor * 80)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # Add subtle nebula clouds
    nebula_overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    n_draw = ImageDraw.Draw(nebula_overlay)
    
    random.seed(42)
    for _ in range(30):
        nx = random.randint(-100, width + 100)
        ny = random.randint(-100, height + 100)
        nr = random.randint(150, 400)
        # magenta / cyan / purple clouds
        color = random.choice([
            (120, 20, 140, 25),
            (20, 100, 160, 25),
            (180, 50, 120, 20),
            (60, 20, 180, 25)
        ])
        n_draw.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=color)
    
    nebula_overlay = nebula_overlay.filter(ImageFilter.GaussianBlur(80))
    img = Image.alpha_composite(img, nebula_overlay)
    draw = ImageDraw.Draw(img)

    # 2. Stars
    for _ in range(400):
        sx = random.randint(0, width - 1)
        sy = random.randint(0, height - 1)
        brightness = random.randint(100, 255)
        size = random.choice([1, 1, 1, 2, 2, 3])
        color = random.choice([
            (255, 255, 255, brightness),
            (200, 230, 255, brightness),
            (255, 220, 240, brightness),
            (255, 255, 180, brightness)
        ])
        if size == 3:
            # 4-point star flare
            draw.ellipse([sx-1, sy-1, sx+1, sy+1], fill=color)
            draw.line([sx-4, sy, sx+4, sy], fill=(*color[:3], brightness // 2), width=1)
            draw.line([sx, sy-4, sx, sy+4], fill=(*color[:3], brightness // 2), width=1)
        else:
            draw.ellipse([sx, sy, sx+size-1, sy+size-1], fill=color)

    # 3. Huge ringed gas giant planet rising in the background (top-left) with high-contrast glowing rings
    planet_cx, planet_cy, planet_r = 220, 280, 140
    # Planet base shading
    planet_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    p_draw = ImageDraw.Draw(planet_layer)
    
    # Draw sphere with radial gradient effect & bands
    for dy in range(-planet_r, planet_r + 1):
        for dx in range(-planet_r, planet_r + 1):
            dist = dx*dx + dy*dy
            if dist <= planet_r*planet_r:
                px = planet_cx + dx
                py = planet_cy + dy
                if 0 <= px < width and 0 <= py < height:
                    angle_y = dy / planet_r
                    base_r = int(200 + 55 * math.sin(angle_y * 4))
                    base_g = int(90 + 60 * math.cos(angle_y * 3))
                    base_b = int(160 + 80 * math.sin(angle_y * 5))
                    light = 0.5 + 0.5 * (dx * 0.7 - dy * 0.7) / planet_r
                    light = max(0.25, min(1.0, light))
                    col = (int(base_r * light), int(base_g * light), int(base_b * light), 255)
                    planet_layer.putpixel((px, py), col)

    # Draw rings behind planet part (high contrast & vivid)
    ring_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    r_draw = ImageDraw.Draw(ring_layer)
    
    rx_radius, ry_radius = 300, 75
    for r_offset in range(-20, 21):
        curr_rx = rx_radius + r_offset
        curr_ry = ry_radius + int(r_offset * 0.3)
        alpha = int(240 - abs(r_offset) * 6)
        # High contrast electric cyan and magenta ring tracks with white bright core
        if r_offset == 0:
            ring_color = (255, 255, 255, 255)
        elif r_offset % 2 == 0:
            ring_color = (120, 255, 255, alpha)
        else:
            ring_color = (255, 100, 220, alpha)
        r_draw.ellipse([
            planet_cx - curr_rx, planet_cy - curr_ry,
            planet_cx + curr_rx, planet_cy + curr_ry
        ], outline=ring_color, width=3)

    img = Image.alpha_composite(img, ring_layer) # under planet
    img = Image.alpha_composite(img, planet_layer)
    
    # Front half of rings overlapping planet (high contrast)
    front_ring_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    fr_draw = ImageDraw.Draw(front_ring_layer)
    for r_offset in range(-16, 17):
        curr_rx = rx_radius + r_offset
        curr_ry = ry_radius + int(r_offset * 0.3)
        alpha = int(255 - abs(r_offset) * 7)
        ring_color = (255, 255, 255, alpha) if r_offset % 3 == 0 else (140, 240, 255, alpha)
        fr_draw.arc([
            planet_cx - curr_rx, planet_cy - curr_ry,
            planet_cx + curr_rx, planet_cy + curr_ry
        ], start=0, end=180, fill=ring_color, width=3)
    
    img = Image.alpha_composite(img, front_ring_layer)
    draw = ImageDraw.Draw(img)

    # 4. Giant Luminous Wave with curling crest and dynamic spray
    wave_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    
    for y in range(250, height):
        wave_edge_x = int(180 + 650 * math.sin((y - 250) / 450 * math.pi * 0.75) + (y - 250) * 0.45)
        wave_edge_x = max(50, min(width - 50, wave_edge_x))
        
        for x in range(0, wave_edge_x):
            progress = x / max(1, wave_edge_x)
            depth_factor = (y - 250) / max(1, height - 250)
            
            wr = int(30 + 120 * progress + 40 * depth_factor)
            wg = int(220 - 70 * progress + 35 * depth_factor)
            wb = int(255 - 30 * progress)
            wa = int(235 + 20 * math.sin(x * 0.06))
            
            wave_layer.putpixel((x, y), (wr, wg, wb, wa))

    # Add curling wave lip / barrel at the top right and sparkling white spray droplets
    crest_glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    c_draw = ImageDraw.Draw(crest_glow)
    
    # Curling lip (hook shape at upper right)
    c_draw.arc([720, 240, 920, 440], start=180, end=360, fill=(150, 255, 255, 240), width=18)
    c_draw.arc([740, 250, 900, 420], start=190, end=350, fill=(255, 255, 255, 255), width=8)

    # White spray droplets flying off the crest
    random.seed(999)
    for _ in range(80):
        dx = random.randint(750, 980)
        dy = random.randint(200, 380)
        ds = random.randint(2, 6)
        c_draw.ellipse([dx, dy, dx + ds, dy + ds], fill=(255, 255, 255, random.randint(180, 255)))

    crest_glow = crest_glow.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, crest_glow)
    img = Image.alpha_composite(img, wave_layer)
    draw = ImageDraw.Draw(img)

    # 5. Code brackets and syntax symbols embedded in the wave and sky
    symbols = ["{ }", "< />", "[ ]", "=>", "&&", "return", "if", "async", "await", "fn()", "::", ">>>", "*"]
    
    try:
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    except:
        font_small = ImageFont.load_default()

    random.seed(1337)
    for _ in range(60):
        sym = random.choice(symbols)
        bx = random.randint(50, 950)
        by = random.randint(280, 980)
        
        approx_edge = int(180 + 650 * math.sin((by - 250) / 450 * math.pi * 0.75) + (by - 250) * 0.45)
        if bx < approx_edge:
            col = random.choice([
                (255, 255, 255, 240),
                (120, 255, 255, 230),
                (255, 120, 240, 230),
                (255, 240, 120, 230)
            ])
            draw.text((bx, by), sym, fill=col, font=font_small)

    # 6. Lone Astronaut on a Surfboard (enlarged by ~1.6x with vivid glowing trail)
    ast_x, ast_y = 650, 310
    
    # Glowing energy trail behind surfboard
    trail_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    t_draw = ImageDraw.Draw(trail_layer)
    t_draw.polygon([
        (ast_x - 70, ast_y + 40),
        (ast_x - 180, ast_y + 140),
        (ast_x - 130, ast_y + 170)
    ], fill=(100, 255, 240, 180))
    t_draw.polygon([
        (ast_x - 60, ast_y + 35),
        (ast_x - 140, ast_y + 110),
        (ast_x - 100, ast_y + 130)
    ], fill=(255, 100, 220, 200))
    trail_layer = trail_layer.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img, trail_layer)
    draw = ImageDraw.Draw(img)

    # Surfboard (enlarged 1.6x)
    board_poly = [
        (ast_x - 72, ast_y + 40),
        (ast_x + 72, ast_y - 40),
        (ast_x + 88, ast_y - 28),
        (ast_x - 56, ast_y + 56)
    ]
    draw.polygon(board_poly, fill=(255, 40, 160, 255))
    draw.polygon(board_poly, outline=(255, 255, 255, 255), width=3)

    # Astronaut body (enlarged 1.6x, crisp proportions)
    # Legs bent
    draw.line([(ast_x - 24, ast_y + 24), (ast_x + 8, ast_y - 8)], fill=(240, 240, 255, 255), width=12)
    # Torso
    draw.rectangle([ast_x - 19, ast_y - 35, ast_x + 19, ast_y - 3], fill=(255, 255, 255, 255))
    # Backpack / Jetpack
    draw.rectangle([ast_x - 29, ast_y - 32, ast_x - 19, ast_y - 8], fill=(110, 120, 140, 255))
    # Helmet (gold glowing visor)
    draw.ellipse([ast_x - 13, ast_y - 60, ast_x + 16, ast_y - 32], fill=(255, 255, 255, 255))
    draw.ellipse([ast_x - 6, ast_y - 54, ast_x + 12, ast_y - 38], fill=(255, 200, 50, 255))

    # Brilliant energy aura around astronaut & board
    aura = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    a_draw = ImageDraw.Draw(aura)
    a_draw.ellipse([ast_x - 80, ast_y - 90, ast_x + 110, ast_y + 80], fill=(120, 255, 255, 100))
    aura = aura.filter(ImageFilter.GaussianBlur(14))
    img = Image.alpha_composite(img, aura)

    # 7. Final polishing: conversion to RGB and saving as entry.png
    final_img = Image.new("RGB", (width, height), (13, 2, 33))
    final_img.paste(img.convert("RGB"), mask=img.split()[3])
    
    # Save as PNG
    final_img.save("entry.png", "PNG", optimize=True)
    print("Successfully generated entry.png (1024x1024)")

if __name__ == "__main__":
    create_entry_image()
