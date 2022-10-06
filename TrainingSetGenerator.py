from polygon_pascalvoc_writer import VocWriter
import cv2
import numpy as np
import glob
import os
import pandas as pd
import xml.etree.ElementTree as ET


def xml_to_csv(path):
    xml_list = []
    for xml_file in glob.glob(path + '/*.xml'):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for member in root.findall('object'):
            value = (root.find('filename').text,
                     int(root.find('size')[0].text),
                     int(root.find('size')[1].text),
                     member[0].text,
                     int(member[4][0].text),
                     int(member[4][1].text),
                     int(member[4][2].text),
                     int(member[4][3].text)
                     )
            xml_list.append(value)
    column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
    xml_df = pd.DataFrame(xml_list, columns=column_name)
    return xml_df



def get_polygon(image):
    blue = image[:,:,0]
    contours, hier = cv2.findContours(blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        epsilon = 0.01 * cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, epsilon, True)
        return approx
    return None


def main():
    images_dir = "TestData/"
    annotations_dir = "Annotations/"
    writer = VocWriter(images_dir, annotations_dir, "")
    img_count = len(glob.glob(images_dir + "render*"))
    for img_id in range(img_count):
        writer.nextImage("render_{0}.png".format(img_id))

        polygons = np.squeeze(get_polygon(cv2.imread("{0}/unlit_{1}.png".format(images_dir, img_id)))).tolist()
        print(polygons)
        writer.addPolygon("polygon_name", polygons)

        writer.save()
    print("Done!")


if __name__ == "__main__":
    main()
