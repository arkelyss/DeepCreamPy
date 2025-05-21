#!/usr/bin/env python3

import os
import sys
import numpy as np
from PIL import Image
import logging
from copy import deepcopy
import tensorflow as tf
from PySide6 import QtCore

import config
import file
from model import InpaintNN
from libs.utils import *

class Decensor(QtCore.QThread):
    def __init__(self, text_edit=None, text_cursor=None, ui_mode=None):
        super().__init__()
        args = config.get_args()
        self.is_mosaic = args.is_mosaic
        self.variations = args.variations
        self.mask_color = [args.mask_color_red / 255.0, args.mask_color_green / 255.0, args.mask_color_blue / 255.0]
        self.decensor_input_path = args.decensor_input_path
        self.decensor_input_original_path = args.decensor_input_original_path
        self.decensor_output_path = args.decensor_output_path

        self.signals = None  # Signals class will be given by progressWindow

        if ui_mode is not None:
            self.ui_mode = ui_mode
        else:
            self.ui_mode = args.ui_mode

        if not os.path.exists(self.decensor_output_path):
            os.makedirs(self.decensor_output_path)

        if self.ui_mode:
            self.text_edit = text_edit
            self.text_cursor = text_cursor
            self.ui_mode = True

    def run(self):
        self.decensor_all_images_in_folder()

    def stop(self):
        self.terminate()

    def find_mask(self, colored):
        mask = np.ones(colored.shape, np.uint8)
        i, j = np.where(np.all(colored[0] == self.mask_color, axis=-1))
        mask[0, i, j] = 0
        return mask

    def load_model(self):
        self.signals.update_progress_LABEL.emit("load_model()", "Loading neural network. This may take a while.")
        self.model = InpaintNN(bar_model_name="./models/bar/Train_775000.meta",
                               bar_checkpoint_name="./models/bar/",
                               mosaic_model_name="./models/mosaic/Train_290000.meta",
                               mosaic_checkpoint_name="./models/mosaic/",
                               is_mosaic=self.is_mosaic)

    def decensor_all_images_in_folder(self):
        self.load_model()

        input_color_dir = self.decensor_input_path
        file_names = os.listdir(input_color_dir)

        input_dir = self.decensor_input_path
        output_dir = self.decensor_output_path

        self.signals.update_progress_LABEL.emit("file.check_file()", "Checking image files and directory...")
        file_names, self.files_removed = file.check_file(input_dir, output_dir, False)
        self.signals.total_ProgressBar_update_MAX_VALUE.emit("set total progress bar MaxValue : " + str(len(file_names)), len(file_names))

        for n, file_name in enumerate(file_names, start=1):
            self.signals.total_ProgressBar_update_VALUE.emit(f"Decensoring {n} / {len(file_names)}", n)
            self.signals.signal_ProgressBar_update_VALUE.emit("reset value", 0)
            self.signals.update_progress_LABEL.emit("for-loop, \"for file_name in file_names:\"", "Decensoring : " + str(file_name))

            color_file_path = os.path.join(input_color_dir, file_name)
            color_basename, color_ext = os.path.splitext(file_name)
            if os.path.isfile(color_file_path) and color_ext.casefold() == ".png":
                self.custom_print("--------------------------------------------------------------------------")
                self.custom_print(f"Decensoring the image {color_file_path}")
                try:
                    colored_img = Image.open(color_file_path)
                except:
                    self.custom_print("Cannot identify image file (" + str(color_file_path) + ")")
                    self.files_removed.append((color_file_path, 3))
                    continue

                if self.is_mosaic:
                    ori_dir = self.decensor_input_original_path
                    test_file_names = os.listdir(ori_dir)
                    valid_formats = {".png", ".jpg", ".jpeg"}
                    for test_file_name in test_file_names:
                        test_basename, test_ext = os.path.splitext(test_file_name)
                        if (test_basename == color_basename) and (test_ext.casefold() in valid_formats):
                            ori_file_path = os.path.join(ori_dir, test_file_name)
                            ori_img = Image.open(ori_file_path)
                            self.decensor_image_variations(ori_img, colored_img, file_name)
                            break
                    else:
                        self.custom_print(f"Corresponding original, uncolored image not found in {color_file_path}")
                        self.custom_print("Check if it exists and is in the PNG or JPG format.")
                else:
                    self.decensor_image_variations(colored_img, colored_img, file_name)
            else:
                self.custom_print("--------------------------------------------------------------------------")
                self.custom_print("Image can't be found: " + str(color_file_path))

        self.custom_print("--------------------------------------------------------------------------")
        if self.files_removed is not None:
            file.error_messages(None, self.files_removed)
        self.custom_print("\nDecensoring complete!")

        self.signals.update_progress_LABEL.emit("finished", "Decensoring complete! Close this window and reopen DCP to start a new session.")

    def custom_print(self, text):
        print(text)
