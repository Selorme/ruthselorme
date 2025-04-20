import os
from bs4 import BeautifulSoup

html_folder = r"C:\Users\Ruth Selorme\Desktop\PycharmProjects\postgresql portfolio\templates"


# Function to add WebP support to an image tag
def add_webp_support(html_content):
    print("Checking HTML Content for Image Tags")

    # Parse HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all <img> tags
    img_tags = soup.find_all('img')

    print(f"Found {len(img_tags)} img tags.")

    for img_tag in img_tags:
        img_src = img_tag.get('src', '')

        # Check if the image source contains the Flask URL structure for static files
        if 'url_for' in img_src:  # Check if it's a Jinja2 template url_for
            # Extract the part of the URL after the 'filename=' part
            filename_part = img_src.split('filename=')[-1].strip(" '}")

            # Check if the file is of type jpg, jpeg, or png
            if filename_part.lower().endswith(('jpg', 'jpeg', 'png')):
                # Create the WebP file name by changing the extension
                webp_src = filename_part.rsplit('.', 1)[0] + '.webp'

                # Create a <picture> tag with the WebP source and the original image tag
                picture_tag = soup.new_tag('picture')
                webp_tag = soup.new_tag('source', srcset="{{ url_for('static', filename='" + webp_src + "') }}",
                                        type="image/webp")
                picture_tag.append(webp_tag)
                picture_tag.append(img_tag.extract())  # Add the original <img> inside <picture>

                # Replace the original <img> tag with the new <picture> tag
                img_tag.insert_before(picture_tag)
                img_tag.decompose()  # Remove the original <img> tag

    return str(soup)


# Function to process all HTML files in a folder and its subfolders
def process_html_files():
    for root, dirs, files in os.walk(html_folder):
        for filename in files:
            if filename.endswith('.html'):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    html_content = file.read()

                modified_html = add_webp_support(html_content)

                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(modified_html)

                print(f"Processed: {file_path}")


# Run the script
if __name__ == "__main__":
    process_html_files()
