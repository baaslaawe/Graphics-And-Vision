__author__ = 'tbeltramelli'

from EpipolarGeometry import *
from StereoCameraCalibrator import *
from DepthMap import *
from Filtering import *


class StereoVision:
    _result = None
    _calibrator = None
    _depth = None

    media_path = None
    output_path = None

    def __init__(self, media_path, output_path):
        self.media_path = media_path
        self.output_path = output_path

    def epipolar_geometry(self, left_video_path, right_video_path, frame_for_epipolar_geometry=15):
        left_img = UMedia.get_frame_from_video(self.media_path + left_video_path, frame_for_epipolar_geometry)
        right_img = UMedia.get_frame_from_video(self.media_path + right_video_path, frame_for_epipolar_geometry)

        epipole = EpipolarGeometry(UGraphics.get_combined_image(left_img, right_img, 0.5))

    def stereo_vision(self, left_video_path, right_video_path, calibration_images=None):
        self._calibrator = StereoCameraCalibrator()
        self._depth = DepthMap(self.output_path)

        if calibration_images is None:
            UMedia.load_videos([self.media_path + left_video_path, self.media_path + right_video_path], self.process)
        else:
            for index in calibration_images:
                left_img = cv2.imread(self.media_path + "l" + str(index) + ".jpg")
                right_img = cv2.imread(self.media_path + "r" + str(index) + ".jpg")

                if self._calibrator.calibrate(left_img, right_img, False):
                    epipole = EpipolarGeometry(UGraphics.get_combined_image(left_img, right_img), False)

                    left_points = self._calibrator.left_points[len(self._calibrator.left_points) - 1]
                    right_points = self._calibrator.right_points[len(self._calibrator.right_points) - 1]

                    left_points = np.array([[px, py, 1] for [px, py] in left_points])
                    right_points = np.array([[px, py, 1] for [px, py] in right_points])

                    epipole.show_lines(left_points, right_points, self._calibrator.fundamental_matrix)
                    UMedia.show(self.get_calibration_img(left_img, right_img))
                    UInteractive.pause()

    def process(self, images):
        if self._calibrator.is_calibrated:
            calibration_img = self.get_calibration_img(images[0], images[1])
            disparity_map = self._depth.compute(images[0], images[1])

            self._depth.save_point_cloud(disparity_map, self._calibrator.disparity_to_depth_matrix)

            UMedia.show(calibration_img, disparity_map)
            UInteractive.pause()
        else:
            self._calibrator.calibrate(images[0], images[1], True)

    def get_calibration_img(self, left_img, right_img):
        original_img = UGraphics.get_combined_image(left_img, right_img, 0.5)
        left_img, right_img = self._calibrator.get_undistorted_rectified_images(left_img, right_img)
        rectified_img = UGraphics.get_combined_image(left_img, right_img, 0.5)

        return UGraphics.get_combined_image(original_img, rectified_img, 0.75, False)

    def disparity(self):
        self._depth = DepthMap(self.output_path)

        left_img = UMedia.get_image(self.media_path + "left_sample.png")
        right_img = UMedia.get_image(self.media_path + "right_sample.png")

        disparity_map = self._depth.compute(left_img, right_img)
        self._depth.save_point_cloud(disparity_map)
