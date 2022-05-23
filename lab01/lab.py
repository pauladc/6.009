#!/usr/bin/env python3

import math

from PIL import Image as Image

# NO ADDITIONAL IMPORTS ALLOWED!


def get_pixel(image, x, y, boundary_behavior=None):
    
    height = image['height']
    width = image['width']

    if x < 0 or x >= width or y < 0 or y >= height:
        #checks for out of bounds cells
        if boundary_behavior == 'zero':
            return 0
        elif boundary_behavior == 'extend':
        #uses value of specified pixel when out of bounds
            if x < 0:
                x = 0
            elif x >= width:
                x = width - 1
            if y < 0:
                y = 0
            elif y >= height:
                y = height - 1
        elif boundary_behavior == 'wrap':
        #uses value of wrapped around pixel when out of bounds
            return image['pixels'][(y%image['height'])*image['width']+ (x%image['width'])]
    return image['pixels'][y*image['width']+x]


def set_pixel(image, x, y, c):
    image['pixels'][y*image['width']+x] = c


def apply_per_pixel(image, func):
    #changes the value of each pixel in an image
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': image['pixels'].copy(),
    }
    for x in range(image['width']):
        for y in range(image['height']):
            color = get_pixel(image, x, y)
            newcolor = func(color)
            set_pixel(result, x, y, newcolor)
    return result


def inverted(image):
    return apply_per_pixel(image, lambda c: (255-c))


# HELPER FUNCTIONS
def create_kernel(kernel_str):
    '''
    Input: a string or list that creates a dictionary
    This is used as a helper function inside subsequent functions
    Output: a dictionary holding location values as tuples in keys and 
    kernel values as values
    '''
        #kernel_str = '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0'
    if type(kernel_str) == str:
        kernel_to_list = kernel_str.split(' ')
    else:
        kernel_to_list = kernel_str
    convert_to_kernel = [float(e) for e in kernel_to_list]
    count = 0
    high, low = int(len(convert_to_kernel)**0.5)//2, int(len(convert_to_kernel)**0.5)//2
    low = -low
    kernel = {}
    for y in range(low,high+1,1):
        for x in range(low,high+1,1):
            kernel[(x, y)] = convert_to_kernel[count]
            count += 1
    return kernel

def correlate(image, boundary_behavior, kernel=None):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will one of the strings 'zero', 'extend', or 'wrap',
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of 'zero', 'extend', or 'wrap', return
    None.

    Otherwise, the output of this function should have the same form as a 6.009
    image (a dictionary with 'height', 'width', and 'pixels' keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    The kernel is created as a dictionary that holds the location of each modification 
    in the kernel with respect to the center point (0,0) as a tuple. It's value corresponds
    to the modification that will be performed on each pixel
    """

    def apply_kernel(image, kernel, x, y, boundary_behavior):
        #modifies the value of each pixel according to kernel multiplication of surrounding pixels
        new_pix = 0
        for x_0, y_0 in kernel.keys():
            new_pix += get_pixel(image, x + x_0, y + y_0, boundary_behavior)  * kernel[(x_0, y_0)]
        return new_pix
       
    valid_behaviors = ('zero', 'extend', 'wrap')
    if boundary_behavior not in valid_behaviors:
        #checks for invalid behaviors 
        return None
    else:
        result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': image['pixels'].copy(),
        }
        my_kernel = create_kernel(kernel)
        #changes the values in the image according to kernel
        for y in range(image['height']):
            for x in range(image['width']):
                set_pixel(result, x, y, apply_kernel(image, my_kernel, x, y, boundary_behavior))
        return result

        



def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    toChange = image['pixels']

    for i in range (len(toChange)):
        toChange[i] = int(round(toChange[i]))
        if toChange[i] > 255:
            toChange[i] = 255
        elif toChange[i] < 0:
            toChange[i] = 0
    

# FILTERS

def blurred(image, n):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    value_for_kernel = [1/n**2 for i in range (n**2)]
    
    # then compute the correlation of the input image with that kernel using
    # the 'extend' behavior for out-of-bounds pixels
    new_img = correlate(image, 'extend', value_for_kernel)
    round_and_clip_image(new_img)

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    return new_img

def sharpened(image, n):
    # creates sharpened image depending on blurred and original
    blurred_img = blurred(image, n)
    image_pixels = image['pixels'].copy()
    result = {'height': image['height'],
        'width': image['width'],
        'pixels': image['pixels'].copy(),
        }
    for i in range (len(image_pixels)):
        result['pixels'][i] = image_pixels[i]*2 - blurred_img['pixels'][i]
    #makes sure values are valid
    round_and_clip_image(result)
    return result

def edges(image):
    #creates and implements kernel for o_x
    o_x = correlate(image, 'extend', [-1, 0, 1, -2, 0, 2, -1, 0, 1])
    #creates and implements kernel for o_y
    o_y = correlate(image, 'extend', [-1, -2, -1, 0, 0, 0, 1, 2, 1])
    result = {'height': image['height'],
        'width': image['width'],
        'pixels': [],
        }
    #changes the values of pixels
    for i in range(len(o_x['pixels'])):
        result['pixels'].append(round((o_x['pixels'][i]**2 + o_y['pixels'][i]**2)**0.5))
    #makes sure values are valid
    round_and_clip_image(result)
    return result

        


# COLOR FILTERS

def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """
    def separate_color_values(image):
        #store (r,g,b) values as separate images
        r = [e[0] for e in image['pixels']]
        image_r = {'height': image['height'], 'width': image['width'], 'pixels': r}
        g = [e[1] for e in image['pixels']]
        image_g = {'height': image['height'], 'width': image['width'], 'pixels': g}
        b = [e[2] for e in image['pixels']]
        image_b = {'height': image['height'], 'width': image['width'], 'pixels': b}
        #modififies each image independently
        new_r = filt(image_r)
        new_g = filt(image_g)
        new_b = filt(image_b)
        color_pixels = []
        #creates pixel values based on corresponding values in each image
        for i in range(len(new_r['pixels'])):
            color_pixels.append((new_r['pixels'][i], new_g['pixels'][i], new_b['pixels'][i]))
        return {
        'height': image['height'],
        'width': image['width'],
        'pixels': color_pixels
        }

    return separate_color_values


def make_blur_filter(n):
    #calls a function that blurs image
        def call_blurred(image):
            return blurred(image, n)  
        return call_blurred


def make_sharpen_filter(n):
    #calls a function that sharpens images
        def call_sharpened(image):
            return sharpened(image, n)
        return call_sharpened


def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    def call_filters(image):
        for filter in filters:
            image = filter(image)
        return image
    return call_filters


# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES

def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith('RGB'):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == 'LA':
            pixels = [p[0] for p in img_data]
        elif img.mode == 'L':
            pixels = list(img_data)
        else:
            raise ValueError('Unsupported image mode: %r' % img.mode)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_greyscale_image(image, filename, mode='PNG'):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode='L', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img = img.convert('RGB')  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_color_image(image, filename, mode='PNG'):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode='RGB', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()

def invert_color_values(image):
        #store (r,g,b) values as separate images
        r = [e[0] for e in image['pixels']]
        g = [e[1] for e in image['pixels']]
        b = [e[2] for e in image['pixels']]
        #modififies each image independently
        color_pixels = []
        #creates pixel values based on corresponding values in each image
        for i in range(len(r)):
            color_pixels.append((b[i], r[i], g[i]))
        return {
        'height': image['height'],
        'width': image['width'],
        'pixels': color_pixels
        }


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    #bluegill = load_greyscale_image('test_images/bluegill.png')
    #inv_blue = inverted(bluegill)
    #save_greyscale_image(inv_blue, 'inv_blue.png')
    # bluegill = load_greyscale_image('test_images/bluegill.png')
    # pigbird = load_greyscale_image('test_images/pigbird.png')

    # print(blurred(test_img, 9))

    # new_pigbird_zero = correlate(pigbird, 'zero')
    # round_and_clip_image(new_pigbird_zero)
    # save_greyscale_image(new_pigbird_zero, 'new_pigbird_zero.png')

    # new_pigbird_extend = correlate(pigbird, 'extend')
    # round_and_clip_image(new_pigbird_extend)
    # save_greyscale_image(new_pigbird_extend, 'new_pigbird_extend.png')

    # new_pigbird_wrap = correlate(pigbird, 'wrap')
    # round_and_clip_image(new_pigbird_wrap)
    # save_greyscale_image(new_pigbird_wrap, 'new_pigbird_wrap.png')



    #cat = load_greyscale_image('test_images/cat.png')

    # then the following will create a color version of that filter
    #color_inverted = color_filter_from_greyscale_filter(inverted)

    # that can then be applied to color images to invert them (note that this
    # should make a new color image, rather than mutating its input)
    # color_cat = load_color_image('test_images/cat.png')
    # inverted_color_cat = color_inverted(color_cat)
    # save_color_image(inverted_color_cat, 'inverted_color_cat.png')
    # blurred_cat = blurred(cat, 13)
    # save_greyscale_image(blurred_cat, 'blurred_cat.png')

    # blurred_cat_zero = blurred(cat, 13)
    # save_greyscale_image(blurred_cat_zero, 'blurred_cat_zero.png')

    # blurred_cat_wrap = blurred(cat, 13)
    # save_greyscale_image(blurred_cat_wrap, 'blurred_cat_wrap.png')

    # # python = load_greyscale_image('test_images/python.png')
    # # py_sharpened = sharpened(python, 11)
    # # save_greyscale_image(py_sharpened, 'py_sharpened.png')
    # construct = load_greyscale_image('test_images/construct.png')
    # checking_edge = edges(construct)
    # save_greyscale_image(checking_edge, 'edge_construct.png')

    # blur_filter = color_filter_from_greyscale_filter(make_blur_filter(9))
    # blurry_python = blur_filter(load_color_image('test_images/python.png'))
    # save_color_image(blurry_python, 'blurry_python.png')

    # sharpen_filter = color_filter_from_greyscale_filter(make_sharpen_filter(7))
    # sharpen_sparrow = sharpen_filter(load_color_image('test_images/sparrowchick.png'))
    # save_color_image(sharpen_sparrow, 'sharpen_sparrowchick.png')

    # filter1 = color_filter_from_greyscale_filter(edges)
    # filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    # filt = filter_cascade([filter1, filter1, filter2, filter1])
    # final_image = filt(load_color_image('test_images/frog.png'))
    # save_color_image(final_image, 'final_frog.png')
    tree = load_color_image('test_images/tree.png')
    save_color_image(invert_color_values(tree), 'inverted_color_tree.png')
    pass



