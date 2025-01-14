import os
import cv2

class Convert2COCO():
    def __init__(self, 
                imgpath=None,
                annopath=None,
                image_format='.jpg',
                anno_format='.txt',
                data_categories=None,
                data_info=None,
                data_licenses=None,
                data_type="instances",
                groundtruth=True,
                small_object_area=0):
        super(Convert2COCO, self).__init__()

        self.imgpath = imgpath
        self.annopath = annopath
        self.image_format = image_format
        self.anno_format = anno_format

        self.categories = data_categories
        self.info = data_info
        self.licenses = data_licenses
        self.type = data_type
        self.small_object_area = small_object_area
        self.small_object_idx = 0
        self.groundtruth = groundtruth

        self.imlist = []
        for img_name in os.listdir(self.imgpath):
            img_name = img_name.split(self.image_format)[0]
            self.imlist.append(img_name)
        
    def get_image_annotation_pairs(self):
        images = []
        annotations = []
        index = 0
        for imId, name in enumerate(self.imlist):
            imgpath = os.path.join(self.imgpath, name + self.image_format)
            annotpath = os.path.join(self.annopath, name + self.anno_format)

            annotations_coco = self.__generate_coco_annotation__(annotpath, imgpath)

            # if annotation is empty, skip this annotation
            if annotations_coco != [] or self.groundtruth == False:
                img = cv2.imread(imgpath)
                height, width, channels = img.shape
                images.append({"date_captured": "2019",
                                "file_name": name + self.image_format,
                                "id": imId + 1,
                                "license": 1,
                                "url": "http://jwwangchn.cn",
                                "height": height,
                                "width": width})

                for annotation in annotations_coco:
                    index = index + 1
                    annotation["iscrowd"] = 0
                    annotation["image_id"] = imId + 1
                    annotation["id"] = index
                    annotations.append(annotation)

                    print("Image ID: {}, Instance ID: {}, Small Object Counter: {}".format(imId, index, self.small_object_idx))

        return images, annotations

    def __generate_coco_annotation__(self, annotpath, imgpath):
        """
        docstring here
            :param self: 
            :param annotpath: the path of each annotation
            :param return: dict()  
        """   
        raise NotImplementedError