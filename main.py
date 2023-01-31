from collections import Counter
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
    used_pictures = {}
    counter = 0
    total = len(os.listdir(qr_codes))

    for file in os.listdir(qr_codes):
        counter += 1
        id = template.copy()
        qr_image = trim(Image.open(os.path.join(qr_codes, file)))
        id.paste(qr_image.resize((400, 400)), (340, 1421))
        id.paste(template.crop((0, 0, 1080, 1420)))
    
        name = create_image((1080, 70), 'white', file.strip().replace('.png', ''), ImageFont.truetype('Roboto-Regular.ttf', 56), (123, 17, 19))
        id.paste(name, (0, 1100))

        matching_pictures = []
        segments_searched = 0
        for name_segment in file.strip().replace('.png', '').replace('.', '').replace(',','').split(' '):
            if len(name_segment) > 1: #dont count middle initials

                modified_name_segment = []
                for l in name_segment: #make search case insensitive
                    modified_name_segment.append('['+l.upper()+l.lower()+']')

                searched = glob.glob(pictures+'/*'+"".join(modified_name_segment)+'*')
                if searched:
                    matching_pictures = matching_pictures + searched
                segments_searched += 1

        if not matching_pictures: #no image found
            print('('+str(counter)+'/'+str(total)+') '+"0Skipping Image. No picture found for \"{}\"".format(file))
            skipped.append(file)
            continue
    
        sorted_matching_pictures = [item for items, c in Counter(matching_pictures).most_common() for item in [items] * c]

        picture_similarity = sorted_matching_pictures.count(sorted_matching_pictures[0]) / segments_searched

        if used_pictures.get(sorted_matching_pictures[0]) is not None: #if picture is already used
            if picture_similarity <=  used_pictures[sorted_matching_pictures[0]][0]: #picture is less similar
                print('('+str(counter)+'/'+str(total)+') '+str(picture_similarity)+"Skipping Image. No picture found for \"{}\"".format(file))
                skipped.append(file)
                continue
            else: #picture is more similar here than the other picture
                os.remove('exports/'+used_pictures[sorted_matching_pictures[0]][1])
                print("removed \""+used_pictures[sorted_matching_pictures[0]][1]+"\" with "+str(used_pictures[sorted_matching_pictures[0]][0])+". Found more matching name \""+file+"\" with "+str(picture_similarity))
                successful -= 1
                skipped.append(used_pictures[sorted_matching_pictures[0]][1])


        used_pictures[sorted_matching_pictures[0]] = [picture_similarity, file]
        picture = Image.open(sorted_matching_pictures[0]).resize((648, 648))
        id.paste(picture.crop((0,0,648,617)), (216, 421))

        id.save('exports/{}'.format(file))
        print('('+str(counter)+'/'+str(total)+') '+"Saved \"{}\"".format(file))
        successful += 1
    
    print("Done! "+str(successful)+"/"+str(len(os.listdir(qr_codes)))+" successful!")
    print("Skipped: "+"\n".join(skipped))

generate('template.png', 'qrcodes', 'pics') 