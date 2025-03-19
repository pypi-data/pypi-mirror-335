import torchvision.transforms
import torch
from PIL import Image
from typing import List
from ultralytics import YOLO
from torch.utils.data import Dataset
import torch.nn.functional as F
import cv2 as cv
import numpy as np

class MultiTransform():
    """
    MultiTransform is an extension to keep the same transformation over a sequence of images instead of initializing a new transformation for every single image. It is inspired by `torchvision.transforms` and could be used for video augmentation. Use `rsp.ml.multi_transforms.Compose`to combine multiple image sequence transformations.
    
    > **Note** `rsp.ml.multi_transforms.MultiTransform` is a base class and should be inherited.
    """
    def __init__(self):
        """
        Initializes a new instance.
        """
        pass

    def __call__(self, input):
        """
        Call self as a function.

        Parameters
        -----------
        input : torch.Tensor<br>List[PIL.Image]<br>List[numpy.array]
            Sequence of images
        """
        raise NotImplementedError()
    
    def __get_size__(self, imgs):
        if not hasattr(self, 'size'):
            if isinstance(imgs[0], torch.Tensor):
                self.size = (imgs[0].shape[1], imgs[0].shape[2])
            else:
                self.size = (imgs[0].size[1], imgs[0].size[0])
    
    def __reset__(self):
        raise NotImplementedError()

#__example__ import rsp.ml.multi_transforms as t\n
#__example__ transforms = t.Compose([
#__example__ \tt.BGR2GRAY(),
#__example__ \tt.Scale(0.5)
#__example__ ])
class Compose():
    """
    Composes several MultiTransforms together.
    """
    def __init__(self, children:List[MultiTransform]):
        """
        Initializes a new instance.

        Parameters
        ----------
        children : List[MultiTransform]
            List of MultiTransforms to compose.
        """
        self.children = children
        pass

    def __call__(self, input):
        result = input
        for c in self.children:
            result = c(result)
        for c in self.children:
            c.__reset__()
        return result
    
    def __reset__(self):
        pass

class Normalize(MultiTransform):
    """
    Normalize images with mean and standard deviation. Given mean: (mean[1],...,mean[n]) and std: (std[1],..,std[n]) for n channels, this transform will normalize each channel of the input torch.*Tensor i.e., output[channel] = (input[channel] - mean[channel]) / std[channel]
    
    > Based on torchvision.transforms.Normalize
    """
    def __init__(self, mean, std, inplace = False):
        """
        Initializes a new instance.

        Parameters
        ----------
        mean : List[float]
            Sequence of means for each channel.
        std : List[float]
            Sequence of standard deviations for each channel.
        inplace : bool
            Set to True make this operation in-place.
        """
        super().__init__()

        assert len(mean) == len(std), f'Expected mean and std to have the same dimension, but got len(mean) = {len(mean)} and len(std) = {len(std)}'

        self.normalize = torchvision.transforms.Normalize(mean, std, inplace)
        self.__toTensor__ = ToTensor()
        self.__toPILImage__ = ToPILImage()
        self.__reset__()

    def __call__(self, inputs):
        is_tensor = isinstance(inputs[0], torch.Tensor)
        if not is_tensor:
            inputs = self.__toTensor__(inputs)
            inputs = torch.stack(inputs)

        input_channels = inputs.shape[1]
        transform_channels = len(self.normalize.mean)

        assert input_channels == transform_channels, f'Expected input channels == transform channels, but got input channels = {input_channels} and len(mean) = {len(self.normalize.mean)}'

        results = []
        for res in self.normalize(inputs):
            results.append(res)

        if not is_tensor:
            results = self.__toPILImage__(results)
        return results
    
    def __reset__(self):
        pass

class RemoveBackgroundAI(MultiTransform):
    def __init__(
            self,
            p:float = 1.,
            removed_color = (0, 0, 0),
            target_classes_yolo = [0],
            yolo_model = "yolo11m-seg.pt"
    ):
        super().__init__()

        self.p = p
        self.removed_color = removed_color
        self.target_classes_yolo = target_classes_yolo

        self.__toTensor__ = ToTensor()
        self.__toPILImage__ = ToPILImage()
        self.__toCVImage__ = ToCVImage()
        self.__segmentation_model__ = YOLO(yolo_model, verbose=False)

        self.__reset__()

    def __remove_background__(self, img, bg, mask):
        """
        Changes the background of the input image.

        Parameters
        ----------
        img : np.array
            Input image
        bg : np.array
            Background image
        mask : np.array
            Mask
        """
        w, h = img.shape[1], img.shape[0]
        bg_w, bg_h = bg.shape[1], bg.shape[0]
        scale = np.min([w / bg_w, h / bg_h])
        new_w, new_h = int(np.round(scale * bg_w)), int(np.round(scale * bg_h))

        bg = cv.resize(bg, (new_w, new_h))

        img[mask > 0] = bg[mask > 0]

        return img
    
    def __get_segmentation_mask__(self, img):
        results = self.__segmentation_model__(img, conf=0.3, iou=0.45, verbose=False)
        segmentation_mask = np.zeros((img.shape[0], img.shape[1]))
        if results and results[0].masks:
            masks = results[0].masks.data.cpu().numpy()
            class_ids = results[0].boxes.cls.cpu().numpy().astype(int) 

            for class_id, mask in zip(class_ids, masks):
                if class_id not in self.target_classes_yolo:
                    continue
                mask = cv.resize(mask, (img.shape[1], img.shape[0]))
                segmentation_mask = np.logical_or(segmentation_mask, mask)
 
        segmentation_mask = np.stack([segmentation_mask] * 3, axis=-1)
        return segmentation_mask == False

    def __call__(self, inputs):
        self.__get_size__(inputs)
        self.__reset__()

        if self.__should_remove_background__:
            is_tensor = isinstance(inputs[0], torch.Tensor)
            if not is_tensor:
                inputs = self.__toTensor__(inputs)

            is_color_image = inputs[0].shape[0] == 3
            is_depth_image = inputs[0].shape[0] == 4

            if is_color_image:
                self.__masks__ = []

            # backgrounds
            bg_color = np.zeros((self.size[0], self.size[1], 3), dtype=np.float32)
            bg_color[:, :, 0] = self.removed_color[0] / 255
            bg_color[:, :, 1] = self.removed_color[1] / 255
            bg_color[:, :, 2] = self.removed_color[2] / 255

            bg = bg_color

            if is_depth_image:
                bg_depth = np.zeros((self.size[0], self.size[1], 1), dtype=np.float32)
                bg_depth = np.concatenate([bg_depth, bg_depth, bg_depth], axis = 2)

                bg_depth = np.expand_dims(bg_depth, 2)

            results = []
            for i, input in enumerate(self.__toCVImage__(inputs)):
                img = np.asarray(input * 255, dtype=np.uint8)
                img_rgb = img[:, :, 0:3]

                mask = self.__get_segmentation_mask__(img_rgb)
                #frame[mask == 0] = 0

                mask = np.asarray(mask, dtype=np.uint8)
                
                if is_depth_image:
                    bg = np.concatenate([bg_color, bg_depth], axis = 2)

                result = self.__remove_background__(input, bg, mask)

                results.append(result)

            results = self.__toTensor__(results)

            if not is_tensor:
                results = self.__toPILImage__(results)
        else:
            results = inputs
        return results

    def __reset__(self):
        self.__should_remove_background__ = np.random.random() < self.p

#__example__ from rsp.nl.dataset import TUCRID
#__example__ import rsp.ml.multi_transforms as multi_transforms
#__example__ 
#__example__ USE_DEPTH_DATA = False
#__example__ backgrounds = TUCRID.load_backgrounds(USE_DEPTH_DATA)
#__example__ tranforms_train = multi_transforms.Compose([
#__example__     multi_transforms.ReplaceBackground(
#__example__         backgrounds = backgrounds,
#__example__         hsv_filter=[(69, 87, 139, 255, 52, 255)],
#__example__         p = 0.8
#__example__     ),
#__example__     multi_transforms.Stack()
#__example__ ])
#__example__ tucrid = TUCRID('train', load_depth_data=USE_DEPTH_DATA, transforms=tranforms_train)
#__example__ 
#__example__ for X, T in tucrid:
#__example__     for x in X:
#__example__         img = x.permute(1, 2, 0).numpy()
#__example__ 
#__example__         cv.imshow('img', img)
#__example__         cv.waitKey(30)
class ReplaceBackground(MultiTransform):
    """
        Transformation for background replacement based on HSV values. Supports depth background replacement. backgrounds have to be passed as list of tuples of rgb and depth images.
    """
    def __init__(
            self,
            backgrounds:List[np.array],
            hsv_filter:List[tuple[int, int, int, int, int, int]] = [(69, 87, 139, 255, 52, 255)],
            p:float = 1.,
            rotate:float = 5,
            max_scale:float = 2,
            max_noise:float = 0.002
        ):
        """
        Transformation for background replacement based on HSV values. Supports depth background replacement. backgrounds have to be passed as list of tuples of rgb and depth images.

        Parameters
        ----------
        backgrounds : List[np.array]
            List of background images
        hsv_filter : List[tuple[int, int, int, int, int, int]]
            List of HSV filters
        p : float, default = 1.
            Probability of applying the transformation
        rotate : float, default = 5
            Maximum rotation angle
        max_scale : float, default = 2
            Maximum scaling factor
        max_noise : float, default = 0.002
            Maximum noise level
        """
        super().__init__()
        self.backgrounds = backgrounds
        self.hsv_filter = hsv_filter
        self.p = p

        self.__toTensor__ = ToTensor()
        self.__toPILImage__ = ToPILImage()
        self.__toCVImage__ = ToCVImage()

        self.transforms:List[MultiTransform] = [
            ToTensor(),
            Rotate(rotate),
            RandomCrop(max_scale = max_scale),
            RandomHorizontalFlip(),
            RandomVerticalFlip(),
            GaussianNoise(max_noise_level=max_noise),
            ToCVImage()
        ]

    def __hsv_filter__(self, img, hmin, hmax, smin, smax, vmin, vmax, inverted):
        """
        Filters the input image based on HSV values.

        Parameters
        ----------
        img : np.array
            Input image
        hmin : int
            Minimum hue value
        hmax : int
            Maximum hue value
        smin : int
            Minimum saturation value
        smax : int
            Maximum saturation value
        vmin : int
            Minimum value value
        vmax : int
            Maximum value value
        inverted : bool
            Invert the mask
        """
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        lower = (hmin, smin, vmin)
        upper = (hmax, smax, vmax)
        mask = cv.inRange(hsv, lower, upper)
        mask = cv.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)

        if inverted:
            mask = 255 - mask
        return mask

    def __change_background__(self, img, bg, mask):
        """
        Changes the background of the input image.

        Parameters
        ----------
        img : np.array
            Input image
        bg : np.array
            Background image
        mask : np.array
            Mask
        """
        w, h = img.shape[1], img.shape[0]
        bg_w, bg_h = bg.shape[1], bg.shape[0]
        scale = np.min([w / bg_w, h / bg_h])
        new_w, new_h = int(np.round(scale * bg_w)), int(np.round(scale * bg_h))

        bg = cv.resize(bg, (new_w, new_h))

        img[mask > 0] = bg[mask > 0]

        return img

    def __call__(self, inputs):
        self.__get_size__(inputs)
        self.__reset__()

        if self.__replace_background__:
            is_tensor = isinstance(inputs[0], torch.Tensor)
            if not is_tensor:
                inputs = self.__toTensor__(inputs)

            is_color_image = inputs[0].shape[0] == 3
            is_depth_image = inputs[0].shape[0] == 4

            if is_color_image:
                self.__masks__ = []

            # backgrounds
            bg_color = np.asarray(self.__background__[0] / 255, dtype=np.float32)

            bg_color = [bg_color]
            for t in self.transforms:
                bg_color = t(bg_color)
            bg_color = bg_color[0]
            bg = bg_color

            if is_depth_image and self.__background__[1]:
                bg_depth = np.asarray(self.__background__[1] / 255, dtype=np.float32)
                bg_depth = np.expand_dims(bg_depth, 2)
                bg_depth = np.concatenate([bg_depth, bg_depth, bg_depth], axis = 2)

                bg_depth = [bg_depth]
                for t in self.transforms:
                    bg_depth = t(bg_depth)
                bg_depth = bg_depth[0][:,:, 0]
                bg_depth = np.expand_dims(bg_depth, 2)

            results = []
            for i, input in enumerate(self.__toCVImage__(inputs)):
                img = np.asarray(input * 255, dtype=np.uint8)
                img_rgb = img[:, :, 0:3]

                mask = np.ones((input.shape[0], input.shape[1]))
                for f in self.hsv_filter:
                    hsv_mask = self.__hsv_filter__(img_rgb.copy(), f[0], f[1], f[2], f[3], f[4], f[5], inverted = False)
                    hsv_mask = hsv_mask / 255

                    mask = cv.bitwise_and(mask, hsv_mask)

                mask = np.asarray(mask, dtype=np.uint8)
                
                if is_depth_image:
                    if self.__background__[1]:
                        bg = np.concatenate([bg_color, bg_depth], axis = 2)
                    else:
                        bg = np.concatenate([bg_color, input[:, :, 3:4]], axis = 2)

                result = self.__change_background__(input, bg, mask)

                results.append(result)

            results = self.__toTensor__(results)

            for t in self.transforms:
                t.__reset__()

            if not is_tensor:
                results = self.__toPILImage__(results)
        else:
            results = inputs
        return results

    def __reset__(self):
        self.__replace_background__ = np.random.random() < self.p
        idx = np.random.randint(0, len(self.backgrounds))

        if isinstance(self.backgrounds, Dataset):
            self.__background__ = self.backgrounds[idx][0]  # avoid sampling target
        else:
            self.__background__ = self.backgrounds[idx]     # sample from list of backgrounds

        if not isinstance(self.__background__, tuple):
            self.__background__ = (self.__background__, None)

class ToTensor(MultiTransform):
    """
    Converts a sequence of images to torch.Tensor.
    """
    def __init__(self):
        super().__init__()

        self.toTensor = torchvision.transforms.ToTensor()
        self.__reset__()

    def __call__(self, images) -> List[torch.Tensor]:
        results = []
        for img in images:
            result = self.toTensor(img).float()
            results.append(result)
        return results
    
    def __reset__(self):
        pass

#__image__ ![](documentation/image/multi_transforms.CenterCrop.png)
class CenterCrop(MultiTransform):
    """
    Crops Images at the center after upscaling them. Dimensions kept the same.
    """
    def __init__(self, max_scale = 2):
        """
        Initializes a new instance.

        Parameters
        ----------
        max_scale : float
            Images are scaled randomly between 1. and max_scale before cropping to original size.
        """
        super().__init__()

        if max_scale < 1:
            raise Exception(f'max_scale expected to be greater than 1. Actual value is {max_scale})')
        self.max_scale = max_scale

        self.__toTensor__ = ToTensor()
        self.__toPILImage__ = ToPILImage()

        self.__reset__()

    def __call__(self, imgs):
        self.__get_size__(imgs)
    
        results = []

        is_tensor = isinstance(imgs[0], torch.Tensor)
        if not is_tensor:
            imgs = self.__toTensor__(imgs)
        
        for img in imgs:
            img_before = img.permute(1, 2, 0).numpy()

            w, h = self.size[1], self.size[0]
            new_w, new_h = int(np.round(w * self.__scale__)), int(np.round(h * self.__scale__))
            img_after = cv.resize(img_before, (new_w, new_h))

            cx, cy = new_w // 2, new_h // 2
            result = img_after[cy - h // 2: cy + h // 2, cx - w // 2: cx + w // 2]
            result = torch.tensor(result, dtype=img.dtype).permute(2, 0, 1)

            results.append(result)

        if not is_tensor:
            results = self.__toPILImage__(results)
            
        return results
    
    def __reset__(self):
        self.__scale__ = 1. + np.random.random() * (self.max_scale - 1.)

#__image__ ![](documentation/image/multi_transforms.RandomCrop.png)
class RandomCrop(MultiTransform):
    """
    Crops Images at a random location after upscaling them. Dimensions kept the same.
    """
    def __init__(self, max_scale = 2):
        """
        Initializes a new instance.

        Parameters
        ----------
        max_scale : float
            Images are scaled randomly between 1. and max_scale before cropping to original size.
        """
        super().__init__()

        if max_scale < 1:
            raise Exception(f'max_scale expected to be greater than 1. Actual value is {max_scale})')
        self.max_scale = max_scale

        self.__toCVImage__ = ToCVImage()
        self.__toTensor__ = ToTensor()
        self.__toPILImage__ = ToPILImage()

    def __call__(self, imgs):
        self.__get_size__(imgs)
        if not hasattr(self, '__scale__'):
            self.__reset__()
    
        results = []

        is_tensor = isinstance(imgs[0], torch.Tensor)
        if not is_tensor:
            imgs = self.__toTensor__(imgs)
        
        #imgs = self.__toCVImage__(imgs)

        for img in imgs:
            img_before = img.permute(1, 2, 0).numpy()

            w, h = self.size[1], self.size[0]
            new_w, new_h = int(np.round(w * self.__scale__)), int(np.round(h * self.__scale__))
            img_after = cv.resize(img_before, (new_w, new_h))

            img_after = torch.tensor(img_after, dtype=img.dtype).permute(2, 0, 1)
            result = img_after[:, self.__sy__:self.__sy__ + h, self.__sx__:self.__sx__ + w]

            results.append(result)

        if not is_tensor:
            results = self.__toPILImage__(results)
            
        return results
    
    def __reset__(self):
        self.__scale__ = 1. + np.random.random() * (self.max_scale - 1.)
        if not hasattr(self, 'size'):
            self.__sx__ = 0
            self.__sy__ = 0
        else:
            w, h = self.size[1], self.size[0]
            new_w, new_h = self.__scale__ * self.size[1], self.__scale__ * self.size[0]
            self.__sx__ = int(np.round(np.random.random() * (new_w - w)))
            self.__sy__ = int(np.round(np.random.random () * (new_h - h)))

#__image__ ![](documentation/image/multi_transforms.Rotate.png)
#__equation__ $angle = -max\_angle + 2 \cdot random() \cdot max\_angle$
class Rotate(MultiTransform):
    """
    Randomly rotates images.
    """
    def __init__(self, max_angle = 180, auto_scale:bool = True):
        """
        Iitializes a new instance.

        Parameters
        ----------
        max_angle : float
            Maximal rotation in degrees | -max_angle <= rotate <= max_angle
        auto_scale : bool, default = True
            Image will be resized when auto scale is activated to avoid black margins.
        """
        super().__init__()

        self.max_angle = max_angle
        self.auto_scale = auto_scale

        self.__toTensor__ = ToTensor()
        self.__toPILImage__ = ToPILImage()

    def __call__(self, imgs):
        self.__get_size__(imgs)
        if not hasattr(self, '__angle__'):
            self.__reset__()
    
        results = []

        is_tensor = isinstance(imgs[0], torch.Tensor)
        if not is_tensor:
            imgs = self.__toTensor__(imgs)

        for img in imgs:
            img_before = img.permute(1, 2, 0).numpy()

            w, h = self.size[1], self.size[0]
            mat = cv.getRotationMatrix2D((w // 2, h // 2), self.__angle__, self.__scale__)
            img_after = cv.warpAffine(img_before, mat, (w, h))

            if len(img_after.shape) == 2:   # grayscale image
                img_after = np.expand_dims(img_after, 2)

            result = torch.tensor(img_after, dtype=img.dtype).permute(2, 0, 1)

            results.append(result)

        if not is_tensor:
            results = self.__toPILImage__(results)
            
        return results
    
    def __reset__(self):
        self.__angle__ = -self.max_angle + 2 * np.random.random() * self.max_angle

        w, h = self.size[1], self.size[0]
        new_w = w + np.abs(np.sin(self.__angle__ / 180 * np.pi) * w)
        new_h = h + np.abs(np.sin(self.__angle__ / 180 * np.pi) * h)

        self.__scale__ = 1.03 * np.max([new_w / w, new_h / h]) if self.auto_scale else 1.

class ToNumpy(MultiTransform):
    """
    Converts a `torch.Tensor`to `numpy`
    """
    def __init__(self):
        super().__init__()

        self.__reset__()

    def __call__(self, tensor:torch.Tensor):
        result = tensor.numpy()
        return result
    
    def __reset__(self):
        pass

class ToCVImage(MultiTransform):
    """
    Converts a `torch.Tensor`to Open CV image by changing dimensions (d0, d1, d2) -> (d1, d2, d0) and converting `torch.Tensor` to `numpy`.
    """
    def __init__(self):
        super().__init__()

        self.__toTensor__ = ToTensor()

        self.__reset__()

    def __call__(self, inputs) -> List[np.array]:
        is_tensor = isinstance(inputs[0], torch.Tensor)
        if not is_tensor:
            inputs = self.__toTensor__(inputs)
        results = []
        for img in inputs:
            result = np.asarray(img.permute(1, 2, 0), dtype = np.float32)
            results.append(result)
        return results
    
    def __reset__(self):
        pass

class ToPILImage(MultiTransform):
    """
    Converts sequence of images to sequence of `PIL.Image`.
    """
    def __init__(self):
        super().__init__()

        self.__toPILImage__ = torchvision.transforms.ToPILImage()

        self.__reset__()

    def __call__(self, tensor:torch.Tensor):
        results = []
        for img in tensor:
            result = self.__toPILImage__(img)
            results.append(result)
        return results
    
    def __reset__(self):
        pass

class BGR2RGB(MultiTransform):
    """
    Converts sequence of BGR images to RGB images.
    """
    def __init__(self):
        super().__init__()

        self.__toTensor__ = ToTensor()
        self.__toPILImage__ = ToPILImage()

        self.__reset__()

    def __call__(self, inputs):
        is_tensor = isinstance(inputs[0], torch.Tensor)
        if not is_tensor:
            inputs = self.__toTensor__(inputs)

        results = []
        for input in inputs:
            result = input.clone()
            result[0:3] = torch.flip(input[0:3], (0,))
            results.append(result)

        if not is_tensor:
            results = self.__toPILImage__(results)
        return results
    
    def __reset__(self):
        pass

class RGB2BGR(BGR2RGB):
    """
    Converts sequence of RGB images to BGR images.
    """
    pass

class Scale(MultiTransform):
    def __init__(self, scale):
        super().__init__()

        self.__toTensor__ = ToTensor()
        self.__toPILImage__ = ToPILImage()

        self.scale = scale

        self.__toCVImage__ = ToCVImage()

        self.__reset__()

    def __call__(self, inputs):
        self.__get_size__(inputs)

        is_tensor = isinstance(inputs[0], torch.Tensor)
        if not is_tensor:
            inputs = self.__toTensor__(inputs)

        results = []
        for input in self.__toCVImage__(inputs):
            w, h = self.size[1], self.size[0]
            new_w, new_h = int(np.round(self.scale * w)), int(np.round(self.scale * h))
            result = cv.resize(input, (new_w, new_h))
            results.append(result)

        results = self.__toTensor__(results)

        if not is_tensor:
            results = self.__toPILImage__(results)
        return results
    
    def __reset__(self):
        pass

class Resize(MultiTransform):
    def __init__(self, target_size:tuple[int, int], auto_crop:bool = True):
        super().__init__()

        self.__toTensor__ = ToTensor()
        self.__toPILImage__ = ToPILImage()
        self.__toCVImage__ = ToCVImage()

        self.target_size = target_size
        self.auto_crop = auto_crop

        self.__reset__()

    def __call__(self, inputs):
        self.__get_size__(inputs)

        is_tensor = isinstance(inputs[0], torch.Tensor)
        if not is_tensor:
            inputs = self.__toTensor__(inputs)

        results = []
        for input in self.__toCVImage__(inputs):
            w, h = self.size[1], self.size[0]
            if self.auto_crop:
                scale = np.max([self.target_size[0] / self.size[0], self.target_size[1] / self.size[1]])
                new_w, new_h = int(np.round(scale * w)), int(np.round(scale * h))
                result = cv.resize(input, (new_w, new_h))

                cx, cy = result.shape[1] // 2, result.shape[0] // 2
                result = result[cy-self.target_size[0]//2:cy+self.target_size[0]//2, cx-self.target_size[1]//2:cx+self.target_size[1]//2]
            else:
                new_w, new_h = self.target_size[1], self.target_size[0]
                result = cv.resize(input, (new_w, new_h))
            results.append(result)

        results = self.__toTensor__(results)

        if not is_tensor:
            results = self.__toPILImage__(results)
        return results
    
    def __reset__(self):
        pass

class Brightness(MultiTransform):
    def __init__(self, min_rel:float, max_rel:float):
        super().__init__()

        if min_rel < 0 or max_rel < 0 or min_rel > max_rel:
            raise Exception(f'min_rel and max_rel expected to be greater or equal 0. min_rel expected to be less or equal max_rel')

        self.__toTensor__ = ToTensor()
        self.__toPILImage__ = ToPILImage()

        self.min_rel = min_rel
        self.max_rel = max_rel

        self.__toCVImage__ = ToCVImage()

        self.__reset__()

    def __call__(self, inputs):
        assert inputs[0].shape[2] >= 3, f'Expected input channels >= 3 but got input[0].shape = {input[0].shape}'

        self.__get_size__(inputs)
        is_tensor = isinstance(inputs[0], torch.Tensor)
        if not is_tensor:
            inputs = self.__toTensor__(inputs)

        results = []
        for input in self.__toCVImage__(inputs):
            hsv = cv.cvtColor(input, cv.COLOR_BGR2HSV)
            h, s, v = cv.split(hsv)

            v *= self.rel
            v[v > 1] = 1
            v[v < 0] = 0
            hsv = cv.merge((h, s, v))
            result = np.copy(input)
            result[:, :, 0:3] = cv.cvtColor(hsv, cv.COLOR_HSV2BGR)

            results.append(result)
        
        results = self.__toTensor__(results)
        
        if not is_tensor:
            results = self.__toPILImage__(results)
        return results
    
    def __reset__(self):
        self.rel = self.min_rel + np.random.random() * (self.max_rel - self.min_rel)

class Satturation(MultiTransform):
    def __init__(self, min_rel:float, max_rel:float):
        super().__init__()

        if min_rel < 0 or max_rel < 0 or min_rel > max_rel:
            raise Exception(f'min_rel and max_rel expected to be greater or equal 0. min_rel expected to be less or equal max_rel')

        self.__toTensor__ = ToTensor()
        self.__toPILImage__ = ToPILImage()

        self.min_rel = min_rel
        self.max_rel = max_rel

        self.__toCVImage__ = ToCVImage()

        self.__reset__()

    def __call__(self, inputs):
        assert inputs[0].shape[2] >= 3, f'Expected input channels >= 3 but got input[0].shape = {input[0].shape}'

        self.__get_size__(inputs)
        is_tensor = isinstance(inputs[0], torch.Tensor)
        if not is_tensor:
            inputs = self.__toTensor__(inputs)

        results = []
        for input in self.__toCVImage__(inputs):
            hsv = cv.cvtColor(input, cv.COLOR_BGR2HSV)
            h, s, v = cv.split(hsv)

            s *= self.rel
            s[s > 1] = 1
            s[s < 0] = 0
            hsv = cv.merge((h, s, v))
            result = np.copy(input)
            result[:, :, 0:3] = cv.cvtColor(hsv, cv.COLOR_HSV2BGR)

            results.append(result)

        results = self.__toTensor__(results)

        if not is_tensor:
            results = self.__toPILImage__(results)
        return results
    
    def __reset__(self):
        self.rel = self.min_rel + np.random.random() * (self.max_rel - self.min_rel)

class Color(MultiTransform):
    def __init__(self, max_rel:float, p = 1.):
        super().__init__()

        if max_rel < 0. or max_rel > 1.:
            raise Exception(f'Expected 0 <= max_rel <= 1, but got max_rel = {max_rel}')

        assert p >= 0. and p <= 1., f'Expected 0 <= p <= 1, but got p = {p}'
        self.p = p

        self.__toTensor__ = ToTensor()
        self.__toPILImage__ = ToPILImage()

        self.max_rel = max_rel

        self.__toCVImage__ = ToCVImage()

        self.__reset__()

    def __call__(self, inputs):
        is_tensor = isinstance(inputs[0], torch.Tensor)
        if is_tensor:
            assert inputs[0].shape[2] >= 3, f'Expected input channels >= 3 but got input[0].shape = {input[0].shape}'
        elif isinstance(inputs[0], Image.Image):
            assert inputs[0].mode in ['RGB', 'RGBA', 'CMYK'], f'Expected input channels >= 3 but got input[0].shape = {input[0].shape}'
        
        self.__get_size__(inputs)
        
        if not is_tensor:
            inputs = self.__toTensor__(inputs)
        
        results = []
        for input in self.__toCVImage__(inputs):
            hsv = cv.cvtColor(input, cv.COLOR_BGR2HSV)
            h, s, v = cv.split(hsv)

            h += self.offset_h
            h[h > 360] = h[h > 360] - 360
            hsv = cv.merge((h, s, v))
            result = np.copy(input)
            result[:, :, 0:3] = cv.cvtColor(hsv, cv.COLOR_HSV2BGR)

            results.append(result)
        
        results = self.__toTensor__(results)

        if not is_tensor:
            results = self.__toPILImage__(results)
        return results
    
    def __reset__(self):
        if np.random.random() < self.p:
            rel = -self.max_rel + 2 * np.random.random() * self.max_rel
            self.offset_h = rel * 360
        else:
            self.offset_h = 0

class GaussianNoise(MultiTransform):
    def __init__(self, min_noise_level = 0., max_noise_level:float = 0.005):
        super().__init__()

        self.__toTensor__ = ToTensor()
        self.__toPILImage__ = ToPILImage()

        self.min_noise_level = min_noise_level
        self.max_noise_level = max_noise_level

        self.__toCVImage__ = ToCVImage()

        self.__reset__()

    def __call__(self, inputs):
        self.__get_size__(inputs)
        is_tensor = isinstance(inputs[0], torch.Tensor)
        if not is_tensor:
            inputs = self.__toTensor__(inputs)

        results = []
        for input in self.__toCVImage__(inputs):
            noise = -self.__noise_level__ + 2 * np.random.random(input.shape) * self.__noise_level__
            result = input + noise

            results.append(result)

        results = self.__toTensor__(results)

        if not is_tensor:
            results = self.__toPILImage__(results)
        return results
    
    def __reset__(self):
        self.__noise_level__ = self.min_noise_level + np.random.random() * (self.max_noise_level - self.min_noise_level)

class Stack(MultiTransform):
    def __init__(self):
        super().__init__()

        self.__toTensor__ = ToTensor()
        self.__toPILImage__ = ToPILImage()

        self.__reset__()

    def __call__(self, inputs):
        self.__get_size__(inputs)
        is_tensor = isinstance(inputs[0], torch.Tensor)
        if not is_tensor:
            inputs = self.__toTensor__(inputs)

        results = torch.stack(inputs)
        
        return results
    
    def __reset__(self):
        pass

class BGR2GRAY(MultiTransform):
    """
    Converts a sequence of BGR images to grayscale images.
    """
    def __init__(self):
        super().__init__()

        self.__toTensor__ = ToTensor()
        self.__toCVImage__ = ToCVImage()
        self.__toPILImage__ = ToPILImage()

        self.__reset__()

    def __call__(self, inputs):
        self.__get_size__(inputs)
        is_tensor = isinstance(inputs[0], torch.Tensor)
        if not is_tensor:
            inputs = self.__toTensor__(inputs)

        results = []
        for input in self.__toCVImage__(inputs):
            result = cv.cvtColor(input, cv.COLOR_BGR2GRAY)

            results.append(result)
        
        results = self.__toTensor__(results)
        
        if not is_tensor:
            results = self.__toPILImage__(results)
        return results
    
    def __reset__(self):
        pass

class RandomHorizontalFlip(MultiTransform):
    def __init__(self):
        super().__init__()

        self.__toTensor__ = ToTensor()
        self.__toCVImage__ = ToCVImage()
        self.__toPILImage__ = ToPILImage()

        self.__reset__()

    def __call__(self, inputs):
        self.__get_size__(inputs)
        is_tensor = isinstance(inputs[0], torch.Tensor)
        if not is_tensor:
            inputs = self.__toTensor__(inputs)

        results = []
        for input in self.__toCVImage__(inputs):
            if self.__should_flip__:
                result = cv.flip(input, 1)
            else:
                result = input

            results.append(result)
        
        results = self.__toTensor__(results)
        
        if not is_tensor:
            results = self.__toPILImage__(results)
        return results
    
    def __reset__(self):
        self.__should_flip__ = np.random.random() > 0.5

class RandomVerticalFlip(MultiTransform):
    def __init__(self):
        super().__init__()

        self.__toTensor__ = ToTensor()
        self.__toCVImage__ = ToCVImage()
        self.__toPILImage__ = ToPILImage()

        self.__reset__()

    def __call__(self, inputs):
        self.__get_size__(inputs)
        is_tensor = isinstance(inputs[0], torch.Tensor)
        if not is_tensor:
            inputs = self.__toTensor__(inputs)

        results = []
        for input in self.__toCVImage__(inputs):
            if self.__should_flip__:
                result = cv.flip(input, 0)
            else:
                result = input

            results.append(result)
        
        results = self.__toTensor__(results)
        
        if not is_tensor:
            results = self.__toPILImage__(results)
        return results
    
    def __reset__(self):
        self.__should_flip__ = np.random.random() > 0.5

if __name__ == '__main__':
    from rsp.ml.dataset import TUCRID
    
    USE_DEPTH_DATA = True

    backgrounds = TUCRID.load_backgrounds(USE_DEPTH_DATA)
    tranforms_train = Compose([
        ReplaceBackground(
            backgrounds = backgrounds,
            hsv_filter=[(69, 87, 139, 255, 52, 255)],
            p = 0.8,
            rotate=0,
            max_scale=2,
            max_noise=0.002
        ),
        Resize((400, 400), auto_crop=False),
        Color(0.1, p = 0.2),
        Brightness(0.7, 1.3),
        Satturation(0.7, 1.3),
        RandomHorizontalFlip(),
        GaussianNoise(0.002),
        Rotate(max_angle=3),
        Stack()
    ])
    tucreid = TUCRID('train', load_depth_data=USE_DEPTH_DATA, transforms=tranforms_train)

    for X, T in tucreid:
        for x in X:
            img_color = x[0:3].permute(1, 2, 0).numpy()
            img_depth = np.expand_dims(x[3].numpy(), 2)
            #img_depth = np.concatenate([img_depth, img_depth, img_depth], axis = 2)

            img_color = np.array(img_color * 255, dtype=np.uint8)
            img_depth = np.array(img_depth * 255, dtype=np.uint8)

            img_depth = cv.applyColorMap(img_depth, cv.COLORMAP_JET)

            img = np.hstack([img_color, img_depth])

            cv.imshow('img', img)
            cv.waitKey()
    
    pass