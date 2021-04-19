import subprocess
import sys
import os
subprocess.check_call([sys.executable, "-m", "pip", "install", 'PySimpleGUI'])
subprocess.check_call([sys.executable, "-m", "pip", "install", 'Pillow'])
subprocess.check_call([sys.executable, "-m", "pip", "install", 'opencv-python'])
import PySimpleGUI as sg
from PIL import Image
import cv2




'''
This function will split a larger image into serveral smaller equal-sized images.
This function is fully coded by myself using basic functions provided by PIL module, such as crop and paste.
There are three input parameter:
1. image path: it is a string that contains the path of the image stored.
2. horizontal_number: it is an integer that represents the number of splitting on the horizontal side. (e.g. 2 means splitting the image into left and right)
3. vertical_number: it is an integer that represents the number of splitting on the vertical side. (e.g. 2 means splitting the image into up and down)
The output will be the smaller images saved on the local storage.
Note that this function is different from other functions, this function will not open the processed images after processing since the number of images processed may be large.
'''
def split_image(image_path, horizontal_number, vertical_number):
    # Updating status widget
    status_widget("Status: Splitting image")

    # Open the larger image that stored in the image path
    larger_image=Image.open(image_path)
    # Print the number of pixels on horizontal side and vertical side respectively
    print("Size of larger image:", larger_image.size[0], "x", larger_image.size[1])

    # Determine the number of pixels on horizontal side of smaller image
    # It can only be an integer so floor division is used
    horizontal_length=larger_image.size[0]//horizontal_number
    print("Horizontal length of smaller image:", horizontal_length)

    # Determine the number of pixels on vertical side of smaller image
    # It can only be an integer so floor division is used
    vertical_length=larger_image.size[1]//vertical_number
    print("Vertical length of smaller image:", vertical_length)

    # The horizontal position to crop the larger image which is the position of 'left edge'
    horizontal_position=0
    # The vertical position to crop the larger image which is the position of 'top edge'
    vertical_position=0

    # The order to crop the larger image (let the image be 2 pixels x 2 pixels):
    # 1 2
    # 3 4
    for i in range(vertical_number):
        for o in range(horizontal_number):
            # loop counter that start from 1
            counter=i*horizontal_number+o+1
            print('\nLooping',counter,'/',vertical_number*horizontal_number,':')
            
            # Create smaller image so that part of larger image can be pasted into it
            # Size of smaller image: horizontal_length x vertical_length
            # Color space: RGB
            # Color: White (250, 250, 250)
            smaller_image=Image.new('RGB', (horizontal_length, vertical_length), (250,250,250))

            # Cropping the image with the position of 'left edge', 'top edge', 'right edge', 'bottom edge'
            print('Cropping larger image at position:',(horizontal_position, vertical_position, horizontal_position + horizontal_length, vertical_position + vertical_length),"(left, top, right, bottom)")
            cropped_image=larger_image.crop((horizontal_position, vertical_position, horizontal_position + horizontal_length, vertical_position + vertical_length))

            # Paste the cropped image onto the smaller image created at position (0,0) (fully cover the smaller image)
            smaller_image.paste(cropped_image,(0,0))

            # Save the smaller image as jpg
            smaller_image.save('cropped image '+str(counter)+'.jpg',"JPEG")

            # Update the progress bar
            progress_widget( int( counter/(vertical_number*horizontal_number)*10000 ) ) 

            # Update horizontal position to crop the next image in the same row
            horizontal_position+=horizontal_length

        # Update vertical position to crop the next row 
        vertical_position+=vertical_length
        # Update hoizontal position to crop the leftest image in the next row
        horizontal_position=0

    # End of splitting images
    print('\nImage splitted successfully at path', os.getcwd())
    # Initialize the progress bar to zero
    progress_widget(0)
    # Update the status widget
    status_widget(str(vertical_number*horizontal_number)+' images saved at path: '+os.getcwd())
    return



'''
This function will cartooning an image.
This function is referenced from the url: https://www.geeksforgeeks.org/cartooning-an-image-using-opencv-python/
Changes of code:
1. Usability: the code from url allows fixed path of image only while this program allows selection of path of image with graphical user interface.
2. Customization: the code from url has fixed setting of processing while this program allows customized setting, such as the level of image smoothing.
3. Speed: many unused lines are removed to enhance speed, such as image resizing.
4. Comment: many comment lines are added for explaination.
5. Reactivity: progress bar and status widget are provided to report the progress.
There are four input parameters:
1. image path: it is a string that contains the path of the image stored.
2. numDownSamples: it is an integer that determines the number of downsampling to process using Guassian pyramid.
3. numBilateralFilters: it is an integer that determines the number of bilateral filter to apply.
4. thickness: it is an integer that determines the number of nearest neighbour pixels used in adaptive threshold.
The output will be the cartoon version of image saved on the local storage.
'''
def cartooning_image(image_path, numDownSamples, numBilateralFilters, thickness):
    # Updating status widget
    status_widget('Start cartooning image')
    # Initialized as zero to used for updating progress bar
    current_progress=0
    # Used for updating progress bar, it is the number of processing steps
    total_progress=numDownSamples*2+numBilateralFilters+7

    print('\nReading image that stored in the image path')
    img_rgb = cv2.imread(image_path)
    
    print('Duplicating image for later processing')
    img_color = img_rgb
    
    # Downsampling image for faster processing speed
    # More downsampling will lead to lower quality
    # Default number of downsampling is 1
    for i in range(numDownSamples):
        print('Downsampling image using Gaussian pyramid',i+1,'/',numDownSamples)
        img_color = cv2.pyrDown(img_color)
        
        # Update progress bar
        current_progress+=1
        progress_widget(int(current_progress/total_progress*10000))
        
    # Applying bilateral filter to smoothing image
    # Bilateral filter replaces the intensity of each pixel with a weighted average of intensity values from nearby pixels
    # Default number of applying is 50.
    for i in range(numBilateralFilters):
        print('Applying bilateral filter to reduce noise',i+1,'/',numBilateralFilters)
        img_color = cv2.bilateralFilter(img_color, 9, 9, 7)

        # Update progress bar
        current_progress+=1
        progress_widget(int(current_progress/total_progress*10000))

    # Upsampling image to restore it
    # Number of upscaling = number of downscaling
    for i in range(numDownSamples):
        print('Upsampling image to the original size',i+1,'/',numDownSamples)
        img_color = cv2.pyrUp(img_color)

        # Update progress bar
        current_progress+=1
        progress_widget(int(current_progress/total_progress*10000))


    # Convert the image to grayscale so that the edges can be detected later
    print('Converting image to grayscale to enhancing edges')
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    # Update progress bar
    current_progress+=1
    progress_widget(int(current_progress/total_progress*10000))

    print('Applying median blur to make the edges sharper')
    img_blur = cv2.medianBlur(img_gray, 3)
    # Update progress bar
    current_progress+=1
    progress_widget(int(current_progress/total_progress*10000))
    

    print('Applying adaptiveThreshold to detect and enhance edges')
    # Adaptive threshold using 'thickness' nearest neighbour pixels
    # Default setting of 'thickness' is 4
    # The number can only be odd number and larger than 1
    thickness=2*thickness+1 # Make the number be odd and larger than 1
    img_edge = cv2.adaptiveThreshold(img_blur, 255,  
                                    cv2.ADAPTIVE_THRESH_MEAN_C,  
                                    cv2.THRESH_BINARY, thickness, 2)
    # Update progress bar
    current_progress+=1
    progress_widget(int(current_progress/total_progress*10000))


    print('Obtaining the shape detail of the colored image')
    # x, y, z are the number of rows, columns, and channels
    (x,y,z) = img_color.shape
    # Update progress bar
    current_progress+=1
    progress_widget(int(current_progress/total_progress*10000))

    print('Resizing the edged image to fit the shape of colored image')
    img_edge = cv2.resize(img_edge,(y,x))
    # Update progress bar
    current_progress+=1
    progress_widget(int(current_progress/total_progress*10000))

    print("Converting the image from grayscale to color so that it can be bit-ANDed with colored image")
    img_edge = cv2.cvtColor(img_edge, cv2.COLOR_GRAY2RGB)
    # Update progress bar
    current_progress+=1
    progress_widget(int(current_progress/total_progress*10000))


    print("Merging the edged image and colored image to form the cartoon version of image")
    res=cv2.bitwise_and(img_color, img_edge) # bit-ANDed two images
    # Update progress bar
    current_progress+=1
    progress_widget(int(current_progress/total_progress*10000))

    # Saving the cartoon version of the image with the filename 'Cartoon version.jpg'
    cv2.imwrite("Cartoon version.jpg", res)

    # Showing the cartoon version of the image for viewing
    cv2.imshow("Cartoon version", res)

    # Update the status widget
    status_widget('Image cartooned successfully saved at path: '+os.getcwd())
    # Initialize the progress bar to zero
    progress_widget(0)

    # Make the showing of image not disappeared immediately
    cv2.waitKey(0)  
    cv2.destroyAllWindows()
    return
    


'''
This function will draw the edges of an image.
This function is referenced from the url: https://www.geeksforgeeks.org/cartooning-an-image-using-opencv-python/ (the same link as above)
Changes of code:
1. Usability: the code from url allows fixed path of image only while this program allows selection of path of image with graphical user interface.
2. Customization: the code from url has fixed setting of processing while this program allows customized setting, such as the level of image smoothing.
3. Speed: many unused lines are removed to enhance speed, such as image resizing.
4. Comment: many comment lines are added for explaination.
5. Reactivity: progress bar and status widget are provided to report the progress.
There are four input parameters:
1. image path: it is a string that contains the path of the image stored.
2. numDownSamples: it is an integer that determines the number of downsampling to process using Guassian pyramid.
3. numBilateralFilters: it is an integer that determines the number of bilateral filter to apply.
4. thickness: it is an integer that determines the number of nearest neighbour pixels used in adaptive threshold.
The output will be the edges version of the image saved on the local storage.
'''
def edging_image(image_path, numDownSamples, numBilateralFilters, thickness):
    # Updating status widget
    status_widget('Start edging image')
    # Initialized as zero to used for updating progress bar
    current_progress=0
    # Used for updating progress bar, it is the number of processing steps
    total_progress=numDownSamples*2+numBilateralFilters+3

    print('\nReading image that stored in the image path')
    img_rgb = cv2.imread(image_path)

    # Downsampling image for faster processing speed
    # More downsampling will lead to lower quality
    # Default number of downsampling is 1
    for i in range(numDownSamples):
        print('Downsampling image using Gaussian pyramid',i+1,'/',numDownSamples)
        img_rgb = cv2.pyrDown(img_rgb)
        
        # Update progress bar
        current_progress+=1
        progress_widget(int(current_progress/total_progress*10000))
        
    # Applying bilateral filter to smoothing image
    # Bilateral filter replaces the intensity of each pixel with a weighted average of intensity values from nearby pixels
    # Default number of applying is 50.
    for i in range(numBilateralFilters):
        print('Applying bilateral filter to reduce noise',i+1,'/',numBilateralFilters)
        img_rgb = cv2.bilateralFilter(img_rgb, 9, 9, 7)

        # Update progress bar
        current_progress+=1
        progress_widget(int(current_progress/total_progress*10000))

    # Upsampling image to restore it
    # Number of upscaling = number of downscaling
    for i in range(numDownSamples):
        print('Upsampling image to the original size',i+1,'/',numDownSamples)
        img_rgb = cv2.pyrUp(img_rgb)

        # Update progress bar
        current_progress+=1
        progress_widget(int(current_progress/total_progress*10000))


    # Convert the image to grayscale so that the edges can be detected later
    print('Converting image to grayscale to enhancing edges')
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    # Update progress bar
    current_progress+=1
    progress_widget(int(current_progress/total_progress*10000))

    print('Applying median blur to make the edges sharper')
    img_blur = cv2.medianBlur(img_gray, 3)
    # Update progress bar
    current_progress+=1
    progress_widget(int(current_progress/total_progress*10000))
    

    print('Applying adaptiveThreshold to detect and enhance edges')
    # Adaptive threshold using 'thickness' nearest neighbour pixels
    # Default setting of 'thickness' is 4
    # The number can only be odd number and larger than 1
    thickness=2*thickness+1 # Make the number be odd and larger than 1
    img_edge = cv2.adaptiveThreshold(img_blur, 255,  
                                    cv2.ADAPTIVE_THRESH_MEAN_C,  
                                    cv2.THRESH_BINARY, thickness, 2)
    # Update progress bar
    current_progress+=1
    progress_widget(int(current_progress/total_progress*10000))


    # Saving the edges version of the image with the filename 'Edge version.jpg'
    cv2.imwrite("Edges version.jpg", img_edge)

    # Showing the edges version of the image for viewing
    cv2.imshow("Edges version", img_edge)

    # Update the status widget
    status_widget('Edges of image successfully saved at path: '+os.getcwd())
    # Initialize the progress bar to zero
    progress_widget(0)

    # Make the showing of image not disappeared immediately
    cv2.waitKey(0)  
    cv2.destroyAllWindows()
    return
  


'''
This function will grayscale an image.
This function is referenced from the url: https://www.geeksforgeeks.org/cartooning-an-image-using-opencv-python/ (the same link as above)
Changes of code:
1. Usability: the code from url allows fixed path of image only while this program allows selection of path of image with graphical user interface.
2. Customization: the code from url has fixed setting of processing while this program allows customized setting, such as the level of image smoothing.
3. Speed: many unused lines are removed to enhance speed, such as image resizing.
4. Comment: many comment lines are added for explaination.
5. Reactivity: progress bar and status widget are provided to report the progress.
There are three input parameters:
1. image path: it is a string that contains the path of the image stored.
2. numDownSamples: it is an integer that determines the number of downsampling to process using Guassian pyramid.
3. numBilateralFilters: it is an integer that determines the number of bilateral filter to apply.
The output will be the grayscale version of the image.
Note that the variable 'thickness' is not related to this function as the edge version of image will not be generated in this function.
'''
def grayscaling_image(image_path, numDownSamples, numBilateralFilters):
    # Updating status widget
    status_widget('Start grayscaling image')
    # Initialized as zero to used for updating progress bar
    current_progress=0
    # Used for updating progress bar, it is the number of processing steps
    total_progress=numDownSamples*2+numBilateralFilters+1

    print('\nReading image that stored in the image path')
    img_rgb = cv2.imread(image_path)


    # Downsampling image for faster processing speed
    # More downsampling will lead to lower quality
    # Default number of downsampling is 1
    for i in range(numDownSamples):
        print('Downsampling image using Gaussian pyramid',i+1,'/',numDownSamples)
        img_rgb = cv2.pyrDown(img_rgb)
        
        # Update progress bar
        current_progress+=1
        progress_widget(int(current_progress/total_progress*10000))
        
    # Applying bilateral filter to smoothing image
    # Bilateral filter replaces the intensity of each pixel with a weighted average of intensity values from nearby pixels
    # Default number of applying is 50.
    for i in range(numBilateralFilters):
        print('Applying bilateral filter to reduce noise',i+1,'/',numBilateralFilters)
        img_rgb = cv2.bilateralFilter(img_rgb, 9, 9, 7)

        # Update progress bar
        current_progress+=1
        progress_widget(int(current_progress/total_progress*10000))

    # Upsampling image to restore it
    # Number of upscaling = number of downscaling
    for i in range(numDownSamples):
        print('Upsampling image to the original size',i+1,'/',numDownSamples)
        img_rgb = cv2.pyrUp(img_rgb)

        # Update progress bar
        current_progress+=1
        progress_widget(int(current_progress/total_progress*10000))

    # Convert the image to grayscale
    print('Converting image to grayscale')
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    # Update progress bar
    current_progress+=1
    progress_widget(int(current_progress/total_progress*10000))

    # Saving the grayscale version of the image with the filename 'Grayscale version.jpg'
    cv2.imwrite("Grayscale version.jpg", img_gray)

    # Showing the Grayscale version of the image for viewing
    cv2.imshow("Grayscale version", img_gray)

    # Update the status widget
    status_widget('Grayscale version of image successfully saved at path: '+os.getcwd())
    # Initialize the progress bar to zero
    progress_widget(0)

    # Make the showing of image not disappeared immediately
    cv2.waitKey(0)  
    cv2.destroyAllWindows()
    return



'''
This function will blur an image.
This function is referenced from the url: https://www.geeksforgeeks.org/python-image-blurring-using-opencv/
Changes of code:
1. Usability: the code from url allows fixed path of image only while this program allows selection of path of image with graphical user interface.
2. Customization: the code from url has fixed level of blurring while this program allows customized level of blurring.
3. Speed: many unused lines are removed to enhance speed, including two other blurring methods. Only Gaussian Blur is adapted in this function.
4. Comment: comment lines are added for explaination.
5. Reactivity: progress bar and status widget are provided to report the progress.
There are two input parameters:
1. image path: it is a string that contains the path of the image stored.
2. blur_level: it is an integer that determines the level of blurring.
The output will be the blurred version of the image.
'''
def blurring_image(image_path, blur_level):
    # Updating status widget
    status_widget('Start blurring image')
    # Update progress bar
    progress_widget(int(1/3*10000))

    print('\nReading image that stored in the image path')
    image = cv2.imread(image_path)
    # Update progress bar
    progress_widget(int(2/3*10000))
      
    # Perform Gaussian Blur
    # The blur level can only be odd number and larger than 1
    # Default setting of the blurring level is 4
    blur_level=2*blur_level+1 # Make the number be odd and larger than 1
    print('Performing Gaussian Blur')
    Gaussian = cv2.GaussianBlur(image, (blur_level, blur_level), 0)
    # Update progress bar
    progress_widget(int(3/3*10000))


    # Saving the blurred version of the image with the filename 'Blurred version.jpg'
    cv2.imwrite("Blurred version.jpg", Gaussian)

    # Showing the Blurred version of the image for viewing
    cv2.imshow("Blurred version", Gaussian)

    # Update the status widget
    status_widget('Blurred version of image successfully saved at path: '+os.getcwd())
    # Initialize the progress bar to zero
    progress_widget(0)

    # Make the showing of image not disappeared immediately
    cv2.waitKey(0)  
    cv2.destroyAllWindows()
    return



'''
This function will denoise an image.
This function is referenced from the url: https://www.geeksforgeeks.org/python-denoising-of-colored-images-using-opencv/
Changes of code:
1. Usability: the code from url allows fixed path of image only while this program allows selection of path of image with graphical user interface.
2. Customization: the code from url has fixed level of setting while this program allows customized setting, such as filter strength.
3. Comment: Comment lines are added for explaination.
4. Reactivity: progress bar and status widget are provided to report the progress.
There are three input parameters:
1. image path: it is a string that contains the path of the image stored.
2. performance: it is an integer that determines the performance. Larger values will consume more time.
3. filter_strength: it is an interger that determines the filter strength. Larger values may lead to loss of image details.
The output will be the denoised version of the image.
'''
def denoising_image(image_path, performance, filter_strength):
    # Updating status widget
    status_widget('Start denoising image')
    # Update progress bar
    progress_widget(int(1/3*10000))

    print('\nReading image that stored in the image path')
    image = cv2.imread(image_path)
    # Update progress bar
    progress_widget(int(2/3*10000))


    # Perform Denoising
    # Default setting of the performance is 10.
    # Default setting of the filter strength is 15.
    print('Performing Denoising')
    img_denoised= cv2.fastNlMeansDenoisingColored(image, None, 10, 10, performance, filter_strength)
    # Update progress bar
    progress_widget(int(3/3*10000))

    # Saving the Denoised version of the image with the filename 'Denoised version.jpg'
    cv2.imwrite("Denoised version.jpg", img_denoised)

    # Showing the Denoised version of the image for viewing
    cv2.imshow("Denoised version", img_denoised)

    # Update the status widget
    status_widget('Denoised version of image successfully saved at path: '+os.getcwd())
    # Initialize the progress bar to zero
    progress_widget(0)

    # Make the showing of image not disappeared immediately
    cv2.waitKey(0)  
    cv2.destroyAllWindows()
    return


    
# Declare some commonly used elements in order to update them easily
# Showing path of image
# have '\t' to reserve space as the length of initialized string will be the maxium length
path_widget=sg.Text('Image not selected\t\t\t\t\t\t\t\t\t\t')
# Showing status of program
# have '\t' to reserve space as the length of initialized string will be the maxium length
status_widget=sg.Text('Status: Pending\t\t\t\t\t\t\t\t\t\t')
# Showing progress of program
progress_widget=sg.ProgressBar(10000, orientation='h')


# Declare some layouts that will be included in frames
path_layout=[[path_widget, sg.FileBrowse('Browse an image', key='file')]]
split_layout=[[sg.Text('Number of photos on horizontal side:'), sg.Input(key='h', size=(5,5)), sg.Text('Number of photos on vertical side:'), sg.Input(key='v', size=(5,5)), sg.Button('Split the image')]]
cartoon_layout=[[sg.Text('Processing speed \n(may sacrifice quality):'), sg.Slider( range=(1,3), default_value = 1, orientation='horizontal', key='downsample', size=(5,20) ), sg.Text('Image smoothing:'), sg.Slider( range=(25,75), default_value = 50, orientation='horizontal', key='bilateral', size=(10,20) ), sg.Text('Thickness of edge\n(Not related to grayscaling):'), sg.Slider( range=(1,7), default_value = 4, orientation='horizontal', key='thickness', size=(10,20) )]
        ,[sg.Button('Cartooning the image'), sg.Button('Draw Edges of the image'), sg.Button('Grayscaling the image')]]
blur_layout=[[sg.Text('\nBlurring level:'), sg.Slider( range=(1,100), default_value = 4, orientation='horizontal', key='blur', size=(40,20) ), sg.Button('Blurring the image')]]
denoise_layout=[[sg.Text('Performance\n(consume more time):'), sg.Slider( range=(1,20), default_value = 10, orientation='horizontal', key='performance', size=(10,20) ), sg.Text('Filter strength\n(may sacrifice detail of image):'), sg.Slider( range=(15,30), default_value = 10, orientation='horizontal', key='filter', size=(10,20) ), sg.Button('Denoising the image')]]


# Declare layout of the main gui window
layout=[[sg.Text('Please pick an image first. Then choose the image processing function(s).\nYou are recommended to use default settings but you are still free to change the settings.')]
        ,[sg.Frame(layout=path_layout, title='Path of image')]
        ,[sg.Text('\nImage Processing Functions:\n')]
        ,[sg.Frame(layout=split_layout, title='1. Split the photo into equal-sized smaller photos which can be posted on Instagram.')]
        ,[sg.Text('')]
        ,[sg.Frame(layout=cartoon_layout, title='2. Cartoon the image to look more entertaining. 3. Draw the edges of the image to focus the shape. 4. Grayscaling the image to focus the detail.')]
        ,[sg.Text('')]
        ,[sg.Frame(layout=blur_layout, title='5. Blur the image for products that not announced yet.')]
        ,[sg.Text('')]
        ,[sg.Frame(layout=denoise_layout, title='6. Denoise the image to restore the true image.')]
        ,[sg.Text('')]
        ,[status_widget, sg.Button('Open folder of processed images')]
        ,[progress_widget]]


# Declare a window with the layout aforementioned
window=sg.Window("Image Processing",layout)


while True:
    event, values=window.read(timeout=20) # gui window refresh every 20 ms
    

    # Error may occur if user closes the window but the program is still reading the value of 'file'
    try:
        # Read the values of input field with key 'file'
        image_path=values['file']
        # Users have chosen the path of image
        if len(image_path)>0:
            # Update the path widget to show the path of image
            path_widget(image_path) 
    except:
        pass
        

    # User closes the gui window
    if event==sg.WIN_CLOSED:
        break


    # User presses the button 'Split the image'
    if event=='Split the image':
        # Check if image path is empty
        if len(image_path)==0:
            sg.popup('Please browse a image first.')
            continue

        # Try to read the number of smaller images on horizontal and vertical sides
        try:
            horizontal_number=int(values['h'])
            vertical_number=int(values['v'])
            print('There will be',horizontal_number,'images per row and',vertical_number,'images per column.')
        except:
            status_widget('Status: Error! Please confirm the two numbers you entered are integers')
            sg.popup('Error! Please confirm the two numbers you entered are integers')
            print('Error! Please confirm the two numbers you entered are integers')
            continue
        
        split_image(image_path, horizontal_number, vertical_number)


    # User presses the button 'Cartooning the image'
    if event=='Cartooning the image':
        # Check if image path is empty
        if len(image_path)==0:
            sg.popup('Please browse a image first.')
            continue

        # Read the values of three sliders       
        numDownSamples=int(values['downsample'])
        numBilateralFilters=int(values['bilateral'])
        thickness=int(values['thickness'])
        cartooning_image(image_path, numDownSamples, numBilateralFilters, thickness)
    

    # User presses the button 'Draw Edges of the image'
    if event=='Draw Edges of the image':
        # Check if image path is empty
        if len(image_path)==0:
            sg.popup('Please browse a image first.')
            continue

        # Read the values of three sliders 
        numDownSamples=int(values['downsample'])
        numBilateralFilters=int(values['bilateral'])
        thickness=int(values['thickness'])
        edging_image(image_path, numDownSamples, numBilateralFilters, thickness)


    # User presses the button 'Grayscaling the image'
    if event=='Grayscaling the image':
        # Check if image path is empty
        if len(image_path)==0:
            sg.popup('Please browse a image first.')
            continue

        # Read the values of two sliders 
        numDownSamples=int(values['downsample'])
        numBilateralFilters=int(values['bilateral'])
        grayscaling_image(image_path, numDownSamples, numBilateralFilters)


    # User presses the button 'Blurring the image'
    if event=='Blurring the image':
        # Check if image path is empty
        if len(image_path)==0:
            sg.popup('Please browse a image first.')
            continue

        # Read the value of blur level in the slider
        blur_level=int(values['blur'])
        blurring_image(image_path, blur_level)


    # User presses the button 'Denoising the image'
    if event=='Denoising the image':
        # Check if image path is empty
        if len(image_path)==0:
            sg.popup('Please browse a image first.')
            continue

        # Read the values of two sliders 
        performance=int(values['performance'])
        filter_strength=int(values['filter'])
        denoising_image(image_path, performance, filter_strength)


    # User presses the button 'Open folder of processed images'
    if event=='Open folder of processed images':
        subprocess.Popen('explorer '+os.getcwd())
        
window.close()
