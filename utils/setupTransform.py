# Import standard libraries
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import json


def get_h_matrices(poly_curve, x, y, orientation=0):
    """
    get H-matrix for detected orientation
    :param poly_curve: the approximate poly curve yielded by approxPolyDP
    :param x: no. of rows in the image frame
    :param y: no. of columns in the image frame
    :param orientation: orientation of the tag represented using integers 0 to 3
    :return: the homogeneous or inverse-homogeneous transform matrix
    """
    orientations = {'bottom_right': 0, 'bottom_left': 1, 'top_right': 2, 'top_left': 3}
    x_width = np.zeros(4, dtype=int)
    y_width = np.zeros(4, dtype=int)
    x_center = np.array([0, x, x, 0])
    y_center = np.array([0, 0, y, y])

    # Define width to perform homogeneous transforms
    if orientation == orientations['bottom_right']:
        x_width[0], y_width[0] = poly_curve[0][0][0], poly_curve[0][0][1]
        x_width[1], y_width[1] = poly_curve[1][0][0], poly_curve[1][0][1]
        x_width[2], y_width[2] = poly_curve[2][0][0], poly_curve[2][0][1]
        x_width[3], y_width[3] = poly_curve[3][0][0], poly_curve[3][0][1]
    elif orientation == orientations['bottom_left']:
        x_width[0], y_width[0] = poly_curve[1][0][0], poly_curve[1][0][1]
        x_width[1], y_width[1] = poly_curve[2][0][0], poly_curve[2][0][1]
        x_width[2], y_width[2] = poly_curve[3][0][0], poly_curve[3][0][1]
        x_width[3], y_width[3] = poly_curve[0][0][0], poly_curve[0][0][1]
    elif orientation == orientations['top_right']:
        x_width[0], y_width[0] = poly_curve[2][0][0], poly_curve[2][0][1]
        x_width[1], y_width[1] = poly_curve[3][0][0], poly_curve[3][0][1]
        x_width[2], y_width[2] = poly_curve[0][0][0], poly_curve[0][0][1]
        x_width[3], y_width[3] = poly_curve[1][0][0], poly_curve[1][0][1]
    elif orientation == orientations['top_left']:
        x_width[0], y_width[0] = poly_curve[3][0][0], poly_curve[3][0][1]
        x_width[1], y_width[1] = poly_curve[0][0][0], poly_curve[0][0][1]
        x_width[2], y_width[2] = poly_curve[1][0][0], poly_curve[1][0][1]
        x_width[3], y_width[3] = poly_curve[2][0][0], poly_curve[2][0][1]
    else:
        print('Incorrect Orientation!!')
        quit()

    # Evaluate the A matrix
    a_mat = [[x_width[0], y_width[0], 1, 0, 0, 0, -x_center[0] * x_width[0], -x_center[0] * y_width[0], -x_center[0]],
             [0, 0, 0, x_width[0], y_width[0], 1, -y_center[0] * x_width[0], -y_center[0] * y_width[0], -y_center[0]],
             [x_width[1], y_width[1], 1, 0, 0, 0, -x_center[1] * x_width[1], -x_center[1] * y_width[1], -x_center[1]],
             [0, 0, 0, x_width[1], y_width[1], 1, -y_center[1] * x_width[1], -y_center[1] * y_width[1], -y_center[1]],
             [x_width[2], y_width[2], 1, 0, 0, 0, -x_center[2] * x_width[2], -x_center[2] * y_width[2], -x_center[2]],
             [0, 0, 0, x_width[2], y_width[2], 1, -y_center[2] * x_width[2], -y_center[2] * y_width[2], -y_center[2]],
             [x_width[3], y_width[3], 1, 0, 0, 0, -x_center[3] * x_width[3], -x_center[3] * y_width[3], -x_center[3]],
             [0, 0, 0, x_width[3], y_width[3], 1, -y_center[3] * x_width[3], -y_center[3] * y_width[3], -y_center[3]]]
    # Get inverse homogeneous transform using svd
    _, _, v_h = np.linalg.svd(a_mat, full_matrices=True)
    h_mat = np.array(v_h[8, :] / v_h[8, 8]).reshape((-1, 3))
    inv_h = np.linalg.inv(h_mat)
    # Return inverse homogeneous transform
    return h_mat, inv_h




if __name__ == '__main__':
    cols, rows = 2304, 1536
    new_col = rows*10/9
    img = cv.imread("./sample.png")
    mask = cv.imread("./PerspectiveMask.png")
    i = 0
    _, thresh = cv.threshold(cv.cvtColor(mask, cv.COLOR_BGR2GRAY),127,255,cv.THRESH_BINARY)
    contours, _ = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        i = i + 1
        contour_poly_curve = cv.approxPolyDP(contour, 0.01 * cv.arcLength(contour, closed=True), closed=True)
        if len(contour_poly_curve) == 4:
            h_mat, inv_h = get_h_matrices(contour_poly_curve, rows, new_col)
            np.save("h_mat",h_mat)
            np.save("inv_h",inv_h)
            img_warped = cv.warpPerspective(img, h_mat, (rows, rows))
            img_warped = cv.transpose(img_warped)
            cv.imwrite("testeWarp" + str(i) + ".png", img_warped)
            cv.drawContours(img, [contour], 0, (0, 0, 225), 1)
            print(h_mat)
