import os
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image

#stamp_image = 'C:\\Users\\erradi\\Dropbox\\_Import-Export\\PanadoorDocs\\Panadoor-Stamp2.png'
stamp_image = 'C:\\Users\\erradi\\Dropbox\\_Import-Export\\PanadoorDocs\\Stamps\panadoor_stamp.png'

def add_stamp_to_pdf(input_pdf, output_pdf, stamp_image):
    # Create a temporary PDF with the stamp image
    temp_pdf_path = "temp_stamp.pdf"
    packet = canvas.Canvas(temp_pdf_path, pagesize=letter)
    
    # Open the stamp image
    image = Image.open(stamp_image)
    
    # Define the desired size for the stamp (e.g., 180x100 pixels)
    stamp_width, stamp_height = 160, 100
    
    # Get the dimensions of the page
    page_width, page_height = letter

    # Calculate the position to place the image in the middle of the page
    x = ((page_width - stamp_width) / 2) - 100
    y = (page_height - stamp_height) / 2

    # Draw the image on the canvas
    packet.drawImage(stamp_image, x, y, width=stamp_width, height=stamp_height, mask='auto')
    packet.showPage()
    packet.save()

    # Read the existing PDF
    with open(input_pdf, "rb") as input_file:
        existing_pdf = PdfReader(input_file)
        output = PdfWriter()

        # Read the temporary PDF with the stamp
        with open(temp_pdf_path, "rb") as stamp_file:
            stamp_pdf = PdfReader(stamp_file)
            stamp_page = stamp_pdf.pages[0]

            # Merge the stamp page with each page of the original PDF
            for i in range(len(existing_pdf.pages)):
                page = existing_pdf.pages[i]
                page.merge_page(stamp_page)
                output.add_page(page)

        # Write the result to the output PDF
        with open(output_pdf, "wb") as outputStream:
            output.write(outputStream)

    # Clean up temporary file
    os.remove(temp_pdf_path)

# Function to process all PDF files in a directory
def add_stamp(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            input_pdf = os.path.join(directory, filename)
            output_pdf = os.path.join(directory, filename) #f"stamped_{filename}")
            add_stamp_to_pdf(input_pdf, output_pdf, stamp_image)
            print(f"Stamped: {filename}")