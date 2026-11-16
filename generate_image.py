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

    # 3. Huge ringed gas giant planet rising in the background (top-left)
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
                    # latitude band coloring
                    angle_y = dy / planet_r
                    # color blend: rich pink/orange/purple bands
                    base_r = int(180 + 60 * math.sin(angle_y * 4))
                    base_g = int(80 + 50 * math.cos(angle_y * 3))
                    base_b = int(140 + 70 * math.sin(angle_y * 5))
                    
                    # 3D lighting gradient (light from top-right)
                    light = 0.5 + 0.5 * (dx * 0.7 - dy * 0.7) / planet_r
                    light = max(0.2, min(1.0, light))
                    
                    col = (int(base_r * light), int(base_g * light), int(base_b * light), 255)
                    planet_layer.putpixel((px, py), col)

    # Draw rings behind planet part
    ring_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    r_draw = ImageDraw.Draw(ring_layer)
    
    # Rings ellipse
    rx_radius, ry_radius = 280, 70
    # draw rotated ring segments
    for r_offset in range(-15, 16):
        curr_rx = rx_radius + r_offset
        curr_ry = ry_radius + int(r_offset * 0.3)
        alpha = int(180 - abs(r_offset) * 8)
        ring_color = (255, 180, 220, alpha) if r_offset % 2 == 0 else (100, 220, 255, alpha)
        r_draw.ellipse([
            planet_cx - curr_rx, planet_cy - curr_ry,
            planet_cx + curr_rx, planet_cy + curr_ry
        ], outline=ring_color, width=2)

    # Composite back rings, planet, front rings
    # Split rings into back and front based on y relative to center
    # Actually, simpler way: draw rings, then planet over top half, or draw full rings and mask front
    # Let's do accurate ring clipping:
    # Back rings (where py < planet_cy + some tilt)
    # Let's draw planet and rings nicely:
    img = Image.alpha_composite(img, ring_layer) # under planet
    img = Image.alpha_composite(img, planet_layer)
    
    # Front half of rings overlapping planet
    front_ring_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    fr_draw = ImageDraw.Draw(front_ring_layer)
    for r_offset in range(-12, 13):
        curr_rx = rx_radius + r_offset
        curr_ry = ry_radius + int(r_offset * 0.3)
        alpha = int(200 - abs(r_offset) * 10)
        ring_color = (255, 200, 240, alpha)
        # Draw only lower half of ellipse for foreground ring
        fr_draw.arc([
            planet_cx - curr_rx, planet_cy - curr_ry,
            planet_cx + curr_rx, planet_cy + curr_ry
        ], start=0, end=180, fill=ring_color, width=3)
    
    img = Image.alpha_composite(img, front_ring_layer)
    draw = ImageDraw.Draw(img)

    # 4. Giant Luminous Wave made of code brackets and dynamic shapes
    wave_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    w_draw = ImageDraw.Draw(wave_layer)
    
    # Wave path from bottom left sweeping up across diagonal to upper right
    # Constructing a massive curling wave polygon
    wave_poly = [
        (0, height),
        (0, 650),
        (150, 550),
        (350, 420),
        (600, 320),
        (800, 380),
        (950, 500),
        (1024, 600),
        (1024, height)
    ]
    
    # Make a smooth curving wave crest using bezier-like points or smooth interpolation
    # Let's draw a rich gradient wave body
    for y in range(300, height):
        # horizontal span of wave at this y
        # wave crest curves from left to right
        # simple parametric curve for wave front edge
        wave_edge_x = int(200 + 600 * math.sin((y - 300) / 400 * math.pi * 0.7) + (y - 300) * 0.4)
        wave_edge_x = max(50, min(width - 50, wave_edge_x))
        
        for x in range(0, wave_edge_x):
            # Gradient inside wave: electric teal, cyan, deep violet, bright magenta
            progress = x / max(1, wave_edge_x)
            depth_factor = (y - 300) / max(1, height - 300)
            
            wr = int(20 + 100 * progress + 50 * depth_factor)
            wg = int(200 - 80 * progress + 55 * depth_factor)
            wb = int(240 - 40 * progress)
            wa = int(220 + 35 * math.sin(x * 0.05))
            
            wave_layer.putpixel((x, y), (wr, wg, wb, wa))

    # Add foam / luminous crest along the wave curve
    crest_glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    c_draw = ImageDraw.Draw(crest_glow)
    
    # Draw sweeping glowing crest line
    crest_points = []
    for i in range(100):
        t = i / 99.0
        cx_pt = int(100 + 850 * t)
        cy_pt = int(600 - 320 * math.sin(t * math.pi) - 80 * t)
        crest_points.append((cx_pt, cy_pt))
        # Draw glowing burst at each crest point
        c_draw.ellipse([cx_pt-15, cy_pt-15, cx_pt+15, cy_pt+15], fill=(100, 255, 240, 60))
        c_draw.ellipse([cx_pt-6, cy_pt-6, cx_pt+6, cy_pt+6], fill=(255, 255, 255, 200))

    crest_glow = crest_glow.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, crest_glow)
    img = Image.alpha_composite(img, wave_layer)
    draw = ImageDraw.Draw(img)

    # 5. Code brackets and syntax symbols embedded in the wave and sky
    # Let's draw sharp glowing code symbols ({ }, < >, [ ], &&, =>, //, function, return)
    symbols = ["{ }", "< />", "[ ]", "=>", "&&", "return", "if", "async", "await", "fn()", "::", ">>>", "*"]
    
    try:
        # Try loading a clean monospace or bold font, fallback to default if not available
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    random.seed(1337)
    for _ in range(50):
        sym = random.choice(symbols)
        bx = random.randint(50, 950)
        by = random.randint(320, 980)
        
        # Check if inside wave region roughly
        # Wave x bounds at by
        approx_edge = int(200 + 600 * math.sin((by - 300) / 400 * math.pi * 0.7) + (by - 300) * 0.4)
        if bx < approx_edge:
            col = random.choice([
                (255, 255, 255, 230),
                (100, 255, 255, 220),
                (255, 100, 220, 220),
                (255, 220, 100, 220)
            ])
            draw.text((bx, by), sym, fill=col, font=font_small)

    # 6. Lone Tiny Astronaut on a Surfboard riding the wave crest!
    # Positioned near the peak of the wave (around x=650, y=340)
    ast_x, ast_y = 660, 330
    
    # Surfboard: sleek glowing magenta/cyan board tilted diagonally
    board_poly = [
        (ast_x - 45, ast_y + 25),
        (ast_x + 45, ast_y - 25),
        (ast_x + 55, ast_y - 18),
        (ast_x - 35, ast_y + 35)
    ]
    draw.polygon(board_poly, fill=(255, 40, 150, 255))
    draw.polygon(board_poly, outline=(255, 255, 255, 255), width=2)
    
    # Surfboard energy trail / wake
    wake_poly = [
        (ast_x - 45, ast_y + 25),
        (ast_x - 120, ast_y + 90),
        (ast_x - 90, ast_y + 110)
    ]
    draw.polygon(wake_poly, fill=(100, 255, 240, 160))

    # Astronaut body (crouched surfing pose)
    # Suit: crisp white with cyan/gold accents
    # Legs bent
    draw.line([(ast_x - 15, ast_y + 15), (ast_x + 5, ast_y - 5)], fill=(240, 240, 255, 255), width=8)
    # Torso
    draw.rectangle([ast_x - 12, ast_y - 22, ast_x + 12, ast_y - 2], fill=(255, 255, 255, 255))
    # Backpack / Jetpack
    draw.rectangle([ast_x - 18, ast_y - 20, ast_x - 12, ast_y - 5], fill=(100, 110, 130, 255))
    # Helmet (gold glowing visor)
    draw.ellipse([ast_x - 8, ast_y - 38, ast_x + 10, ast_y - 20], fill=(255, 255, 255, 255))
    draw.ellipse([ast_x - 4, ast_y - 34, ast_x + 8, ast_y - 24], fill=(255, 200, 50, 255)) # gold visor reflection

    # Add a brilliant energy aura around astronaut & board
    aura = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    a_draw = ImageDraw.Draw(aura)
    a_draw.ellipse([ast_x - 50, ast_y - 60, ast_x + 70, ast_y + 50], fill=(100, 255, 255, 80))
    aura = aura.filter(ImageFilter.GaussianBlur(10))
    img = Image.alpha_composite(img, aura)

    # 7. Final polishing: conversion to RGB and saving as entry.png
    final_img = Image.new("RGB", (width, height), (13, 2, 33))
    final_img.paste(img.convert("RGB"), mask=img.split()[3])
    
    # Save as PNG
    final_img.save("entry.png", "PNG", optimize=True)
    print("Successfully generated entry.png (1024x1024)")

if __name__ == "__main__":
    create_entry_image()
