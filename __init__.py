from typing import Tuple
import numpy
from PIL import Image
from time import perf_counter as current_time
import numba

# Modes for encoding
class Calculate:
    class Modes:

        @staticmethod
        @numba.njit
        def linear(width: int, height: int, input_length: int, read_input: bytes, channels: int) -> numpy.ndarray:
            """   index - 1 2 3 4 5 6 7 8 9 10 11 12
                channel - R G B R G B R G B R  G  B
                pixel - 1 1 1 2 2 2 3 3 3 4  4  4
            """
            
            # Main iterator
            current_index = 0

            # Creating empty array
            raw = numpy.zeros((width, height, channels), numpy.int8)

            # Case for pre-compile
            if not channels: return raw
        
            # Fill array
            for i in numpy.arange(width):
                for j in numpy.arange(height):
                    for q in numpy.arange(channels):
        
                        current_index += 1

                        # Exit if out of bounds
                        if current_index + 1 > input_length:
                            break
        
                        # Set color
                        raw[i][j][q] = read_input[current_index]

            return raw

        @staticmethod
        @numba.njit
        def channel(width: int, height: int, input_length: int, read_input: bytes, channels: int) -> numpy.ndarray:
            """   index - 1 2 3 4 5 6 7 8 9 10 11 12
                channel - R R R R G G G G B B  B  B 
                pixel - 1 2 3 4 1 2 3 4 1 2  3  4
            """
            
            # Main iterator
            current_index = 0
            
            # Creating empty array
            raw = numpy.zeros((width, height, channels), numpy.int8)

            # Case for pre-compile
            if not channels: return raw
            
            # Fill array
            for q in numpy.arange(channels):
                for i in numpy.arange(width):
                    for j in numpy.arange(height):
                        
                        current_index += 1

                        # Exit if out of bounds
                        if current_index + 1 > input_length:
                            break
                        
                        # Set color
                        raw[i][j][q] = read_input[current_index]

            return raw

        @staticmethod
        @numba.njit
        def single(width: int, height: int, input_length: int, read_input: bytes, channels: int) -> numpy.ndarray:
            """   index - 1 2 3 4 5 6 7 8 9 10 11 12
                channel - A A A A A A A A A A  A  A 
                pixel - 1 2 3 4 5 6 7 8 9 10 11 12
            """
            
            sqrt3 = numpy.sqrt(channels)

            # Changing the size of image. Shut up
            nwidth = int(width*sqrt3)+1
            nheight = int(height*sqrt3)
            
            # Creating empty array
            raw = numpy.zeros((nheight, nwidth), numpy.int8)

            # Case for pre-compile
            if not channels: return raw
            
            for i in numpy.arange(input_length):
                
                # Calculating position of the pixel
                x = i % nwidth
                y = i // nwidth

                # Set color
                raw[y][x] = read_input[i]

            return raw

    @staticmethod
    @numba.njit
    def get_resolution(length: int):
        "Calculates the size of an image from length of the info"

        # Best size of edge of the image
        closest = numpy.sqrt(length)

        # If it works perfectly return it
        if closest - int(closest) == 0.0:
            width = int(closest)
            height = int(closest)

        # Otherwise convert it to the best possible result
        else:
            width = int(closest) + ( int(numpy.round(closest)) - int(closest) )
            height = int(closest)+1

        return width, height


    @staticmethod
    def parse_info(obj: bytes, channels: int) -> Tuple[int, int, int, bytes]:

        # Length of input of the file
        input_length = len(obj)

        # Count of pixels will be used
        pixels_count = input_length//channels + (1 if input_length % channels != 0 else 0)

        # The size of out image
        width, height = Calculate.get_resolution(pixels_count)

        return width, height, input_length, obj

    @staticmethod
    def array_to_image(array, mode, encoder_mode):
        if mode == "single":
            image = Image.fromarray(array, "L")
        else:
            image = Image.fromarray(array, encoder_mode)

        return image

def run(mode: str) -> None:
    print(f"Calculating with mode '{mode}'")
    print("Sorting to array...")
    
    # Start stopwatch
    time1 = current_time()

    # Generation out image as an array
    if hasattr(Calculate.Modes, mode):
        raw = getattr(Calculate.Modes, mode)(*Calculate.parse_info(read_input, CHANNELS), CHANNELS)
    else:
        raise ValueError(f"Unknown mode '{mode}'")

    print("Converting into the image...")
    
    # Converting array into the image
    image = Calculate.array_to_image(raw, mode, DEFAULT_ENCODER_MODE)
        
    print("Saving...")
    
    # Saving result image
    image.save(f"output-{mode}.png")
    
    print(f"Done in {current_time()-time1}s\n")

def fast_image(obj: bytes, mode = "linear", channels = 3, encoder_more = "RGB") -> Image.Image:
    return Calculate.array_to_image(getattr(Calculate.Modes, mode)(*Calculate.parse_info(obj, channels), channels), mode, encoder_more)

# Defalut modes (Exclude 'all')
DEFAULTMODELIST = ["linear", "channel", "single"]

# Pre-compile
for mode in DEFAULTMODELIST:
    getattr(Calculate.Modes, mode)(*Calculate.parse_info(b" ", 1), 0)
Calculate.get_resolution(0)

if __name__ == "__main__":

    # Mods are 'linear', 'channel' and 'single', 'all' (All 3)
    MODE = 'all'
    CHANNELS = 3
    DEFAULT_ENCODER_MODE = "RGB"

    # Taking user input
    input_file_path = input("File path: ")

    # Start stopwatch
    time1 = current_time()
    print("Loading file...")

    # Reading a file
    try:
        with open(input_file_path, "rb") as input_file:
            read_input = input_file.read()
    except:
        raise OSError("Can't open/read the file")

    print("Calculating default values...")

    print(f"Done in {current_time()-time1}s\n")
    
    # Run
    if MODE == "all":
        for mode in DEFAULTMODELIST:
            run(mode)
    else:
        run(MODE)
