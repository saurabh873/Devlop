import chardet
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from django.shortcuts import render, redirect
from .forms import FileUploadForm
from .models import FileUpload
from django.core.mail import EmailMessage
from django.conf import settings
from .utilis import send_email_to_client
import os



def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save()
            return redirect('generate_report', file_id=uploaded_file.id)
    else:
        form = FileUploadForm()
    return render(request, 'upload.html', {'form': form})

def generate_report(request, file_id):
    file = FileUpload.objects.get(id=file_id)
    file_path = os.path.join(settings.MEDIA_ROOT, file.file.name)

    # Detect the encoding of the file
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    encoding = result['encoding']

    # Load the CSV file into a DataFrame with the detected encoding
    try:
        df = pd.read_csv(file_path, encoding=encoding, on_bad_lines='skip', engine='python')
    except UnicodeDecodeError as e:
        return render(request, 'error.html', {'message': f'Error decoding file: {e}'})
    except pd.errors.ParserError as e:
        return render(request, 'error.html', {'message': f'Error parsing file: {e}'})

    

    report = df.describe()

    # Plotting the summary statistics as a table
    fig, ax = plt.subplots(figsize=(10, 4))  # Set figure size
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(cellText=report.values, colLabels=report.columns, rowLabels=report.index, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)

    # Save the plot as a PNG image
    image_file_path = os.path.join(settings.MEDIA_ROOT, 'report.png')
    plt.savefig(image_file_path, bbox_inches='tight', pad_inches=0.1)
    plt.close()

    # Convert PNG to JPG
    jpg_image_path = os.path.join(settings.MEDIA_ROOT, 'report.jpg')
    with Image.open(image_file_path) as img:
        rgb_im = img.convert('RGB')
        rgb_im.save(jpg_image_path)

    # Send the report via email as a JPG attachment
    send_email(jpg_image_path)

    # Optionally, render the report in a template (as HTML or image)
    return render(request, 'report.html', {'image_path': jpg_image_path})





def send_email(jpg_image_path):
    send_email_to_client()
    return redirect('/') 

