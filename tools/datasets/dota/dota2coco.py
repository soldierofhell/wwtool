import argparse

import os
import cv2
import json
import numpy as np

from wwtool.datasets import Convert2COCO
from wwtool.transforms import thetaobb2hobb, pointobb2thetaobb, pointobb2sampleobb, pointobb_extreme_sort, pointobb_best_point_sort

class DOTA2COCO(Convert2COCO):
    def __generate_coco_annotation__(self, annotpath, imgpath):
        """
        docstring here
            :param self: 
            :param annotpath: the path of each annotation
            :param return: dict()  
        """
        objects = self.__dota_parse__(annotpath, imgpath)
        
        coco_annotations = []
        
        for object_struct in objects:
            bbox = object_struct['bbox']
            label = object_struct['label']
            segmentation = object_struct['segmentation']
            pointobb = object_struct['pointobb']
            thetaobb = object_struct['thetaobb']
            hobb = object_struct['hobb']
            keypoint = object_struct['keypoints']

            width = bbox[2]
            height = bbox[3]
            area = height * width

            if area <= self.small_object_area and self.groundtruth:
                self.small_object_idx += 1
                continue

            coco_annotation = {}
            coco_annotation['bbox'] = bbox
            coco_annotation['category_id'] = label
            coco_annotation['area'] = np.float(area)
            coco_annotation['segmentation'] = [segmentation]
            coco_annotation['pointobb'] = pointobb
            coco_annotation['thetaobb'] = thetaobb
            coco_annotation['hobb'] = hobb
            coco_annotation['keypoints'] = keypoint
            coco_annotation['num_keypoints'] = 4

            coco_annotations.append(coco_annotation)
            
        return coco_annotations
    
    def __dota_parse__(self, dota_label_file, dota_image_file):
        objects = []
        if self.groundtruth:
            dota_labels = open(dota_label_file, 'r').readlines()
            for dota_label in dota_labels:
                # only save single category
                if single_category is not None:
                    if dota_label.split(' ')[8] != single_category:
                        continue
                obj_struct = {}

                pointobb = [float(xy) for xy in dota_label.split(' ')[:8]]
                obj_struct['segmentation'] = pointobb2sampleobb(pointobb, rate=0.0)
                obj_struct['pointobb'] = pointobb_sort_function[pointobb_sort_method](pointobb)
                obj_struct['thetaobb'] = pointobb2thetaobb(pointobb)
                obj_struct['hobb'] = thetaobb2hobb(obj_struct['thetaobb'], pointobb_sort_function[pointobb_sort_method])

                obj_struct['keypoints'] = obj_struct['pointobb'][:]
                for idx in [2, 5, 8, 11]:
                    obj_struct['keypoints'].insert(idx, 2)

                xmin = min(pointobb[0::2])
                ymin = min(pointobb[1::2])
                xmax = max(pointobb[0::2])
                ymax = max(pointobb[1::2])
                bbox_w = xmax - xmin
                bbox_h = ymax - ymin
                obj_struct['bbox'] = [xmin, ymin, bbox_w, bbox_h]
                obj_struct['label'] = original_dota_class[dota_label.split(' ')[8]]

                objects.append(obj_struct)
        else:
            obj_struct = {}
            obj_struct['segmentation'] = [0, 0, 0, 0, 0, 0, 0, 0]
            obj_struct['keypoints'] = [0, 0, 0, 0, 0, 0, 0, 0]
            obj_struct['pointobb'] = [0, 0, 0, 0, 0, 0, 0, 0]
            obj_struct['thetaobb'] = [0, 0, 0, 0, 0]
            obj_struct['hobb'] = [0, 0, 0, 0, 0]
            obj_struct['bbox'] = [0, 0, 0, 0]
            obj_struct['label'] = 0

            objects.append(obj_struct)
        return objects

def parse_args():
    parser = argparse.ArgumentParser(description='MMDet test detector')
    parser.add_argument(
        '--imagesets',
        type=str,
        nargs='+',
        choices=['trainval', 'test'])
    parser.add_argument(
        '--release_version', default='v1', type=str)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()

    # basic dataset information
    info = {"year" : 2019,
                "version" : "1.5",
                "description" : "DOTA-COCO",
                "contributor" : "Jinwang Wang",
                "url" : "jwwangchn.cn",
                "date_created" : "2019"
            }
    
    licenses = [{"id": 1,
                    "name": "Attribution-NonCommercial",
                    "url": "http://creativecommons.org/licenses/by-nc-sa/2.0/"
                }]

    # DOTA dataset's information
    image_format='.png'
    anno_format='.txt'

    original_dota_class = {'harbor': 1, 'ship': 2, 'small-vehicle': 3, 'large-vehicle': 4, 'storage-tank': 5, 'plane': 6, 'soccer-ball-field': 7, 'bridge': 8, 'baseball-diamond': 9, 'tennis-court': 10, 'helicopter': 11, 'roundabout': 12, 'swimming-pool': 13, 'ground-track-field': 14, 'basketball-court': 15}

    converted_dota_class = [{'supercategory': 'none', 'id': 1,  'name': 'harbor',                },
                            {'supercategory': 'none', 'id': 2,  'name': 'ship',                  }, 
                            {'supercategory': 'none', 'id': 3,  'name': 'small-vehicle',         },
                            {'supercategory': 'none', 'id': 4,  'name': 'large-vehicle',         },
                            {'supercategory': 'none', 'id': 5,  'name': 'storage-tank',          },
                            {'supercategory': 'none', 'id': 6,  'name': 'plane',                 },
                            {'supercategory': 'none', 'id': 7,  'name': 'soccer-ball-field',     },
                            {'supercategory': 'none', 'id': 8,  'name': 'bridge',                },
                            {'supercategory': 'none', 'id': 9,  'name': 'baseball-diamond',      },
                            {'supercategory': 'none', 'id': 10, 'name': 'tennis-court',          },
                            {'supercategory': 'none', 'id': 11, 'name': 'helicopter',            },
                            {'supercategory': 'none', 'id': 12, 'name': 'roundabout',            },
                            {'supercategory': 'none', 'id': 13, 'name': 'swimming-pool',         },
                            {'supercategory': 'none', 'id': 14, 'name': 'ground-track-field',    },
                            {'supercategory': 'none', 'id': 15, 'name': 'basketball-court',      },]

    imagesets = ['test']
    dota_version = 'v1.0'
    release_version = 'v4'
    rate = '1.0_0.5'
    groundtruth = False
    single_category = None
    keypoint = True

    extra_info = ''
    if keypoint:
        for idx in range(len(converted_dota_class)):
            converted_dota_class[idx]["keypoints"] = ['top', 'right', 'bottom', 'left']
            converted_dota_class[idx]["skeleton"] = [[1,2], [2,3], [3,4], [4,1]]
        extra_info += 'keypoint'
    
    if groundtruth == False:
        extra_info += '_no_ground_truth'

    # only save single category
    if single_category is not None:
        extra_info += single_category
        original_dota_class = {single_category: 1}
        converted_dota_class = [{'supercategory': 'none', 'id': 1,  'name': single_category,                }]

    # pointobb sort method
    pointobb_sort_method = 'best' # or "extreme"
    pointobb_sort_function = {"best": pointobb_best_point_sort,
                            "extreme": pointobb_extreme_sort}

    if dota_version == 'v1.5':
        extra_class = [{'supercategory': 'none', 'id': 16,  'name': 'container-crane'}]
        converted_dota_class += extra_class
        original_dota_class['container-crane'] = 16

    for imageset in imagesets:
        
        imgpath = '/data/dota/{}/{}/images'.format(release_version, imageset)
        annopath = '/data/dota/{}/{}/labels'.format(release_version, imageset)
        save_path = '/data/dota/{}/coco/annotations'.format(release_version)
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        dota = DOTA2COCO(imgpath=imgpath,
                        annopath=annopath,
                        image_format=image_format,
                        anno_format=anno_format,
                        data_categories=converted_dota_class,
                        data_info=info,
                        data_licenses=licenses,
                        data_type="instances",
                        groundtruth=groundtruth,
                        small_object_area=0)

        images, annotations = dota.get_image_annotation_pairs()

        json_data = {"info" : dota.info,
                    "images" : images,
                    "licenses" : dota.licenses,
                    "type" : dota.type,
                    "annotations" : annotations,
                    "categories" : dota.categories}

        with open(os.path.join(save_path, "dota_" + imageset + "_" + release_version + "_" + rate + "_" + pointobb_sort_method + "_" + extra_info + ".json"), "w") as jsonfile:
            json.dump(json_data, jsonfile, sort_keys=True, indent=4)