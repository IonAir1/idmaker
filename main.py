from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageColor, ImageChops
import os
import glob


def create_image(size, bgColor, message, font, fontColor):
    W, H = size
    image = Image.new('RGB', size, bgColor)
    draw = ImageDraw.Draw(image)
    _, _, w, h = draw.textbbox((0, 0), message, font=font)
    draw.text(((W-w)/2, (H-h)/2), message, font=font, fill=fontColor)
    return image


def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((1,1)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    return im.crop(bbox)


def generate(template_path, qr_codes, pictures):
    template = Image.open(template_path)

    if not os.path.exists('exports'):
        os.makedirs('exports')

    successful = 0
    skipped = []

    for file in os.listdir(qr_codes):
        id = template.copy()
        qr_image = trim(Image.open(os.path.join(qr_codes, file)))
        id.paste(qr_image.resize((400, 400)), (340, 1421))
        id.paste(template.crop((0, 0, 1080, 1420)))
    
        name = create_image((1080, 70), 'white', file.strip().replace('.png', ''), ImageFont.truetype('Roboto-Regular.ttf', 56), (123, 17, 19))
        id.paste(name, (0, 1100))

        segments_searched = []
        for name_segment in file.strip().replace('.png', '').replace('.', '').replace(',','').split(' '):
            if len(name_segment) > 1:
                modified_name_segment = []
                for l in name_segment:
                    modified_name_segment.append('['+l.upper()+l.lower()+']')

                searched = glob.glob(pictures+'/*'+"".join(modified_name_segment)+'*')
                segments_searched.append(searched)
        matching_pictures = list(set.intersection(*map(set,segments_searched)))

        if not matching_pictures:
            print("Skipping Image. No picture found for \"{}\"".format(file))
            skipped.append(file)
            continue

        picture = Image.open(matching_pictures[0]).resize((648, 648))
        id.paste(picture.crop((0,0,648,617)), (216, 421))

        id.save('exports/{}'.format(file))
        print("Saved \"{}\"".format(file))
        successful += 1
    
    print("Done! "+str(successful)+"/"+str(len(os.listdir(qr_codes)))+" successful!")
    print("Skipped: "+str(skipped))

#generate('template.png', '2ndSemester', 'pics') 