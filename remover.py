import cv2
import numpy as np

class WatermarkRemover:
    def __init__(self):
        self.inpaint_radius = 3  # 修复半径，可根据水印大小调整

    # ====================== 新方法插入位置 START ======================
    def select_watermark_by_mouse(self, img_path):
        """
        鼠标框选水印区域，生成对应的掩码
        :param img_path: 输入图片路径
        :return: 水印掩码（numpy数组）
        """
        # 读取图片
        img = cv2.imread(img_path)
        if img is None:
            raise FileNotFoundError(f"无法读取图片：{img_path}")
        img_copy = img.copy()  # 复制原图用于绘制框选区域
        roi = []  # 存储鼠标框选的坐标：[x1, y1, x2, y2]

        # 定义鼠标回调函数（处理框选逻辑）
        def mouse_callback(event, x, y, flags, param):
            nonlocal roi  # 引用外部的roi变量
            if event == cv2.EVENT_LBUTTONDOWN:
                # 鼠标左键按下：记录起始坐标
                roi[:] = [x, y]
            elif event == cv2.EVENT_LBUTTONUP:
                # 鼠标左键松开：记录结束坐标，并绘制矩形
                cv2.rectangle(img_copy, (roi[0], roi[1]), (x, y), (0, 255, 0), 2)
                cv2.imshow("Select Watermark (Press ESC to confirm)", img_copy)
                roi.extend([x, y])  # 补充结束坐标

        # 显示图片并绑定鼠标事件
        cv2.namedWindow("Select Watermark (Press ESC to confirm)", cv2.WINDOW_NORMAL)
        cv2.imshow("Select Watermark (Press ESC to confirm)", img_copy)
        cv2.setMouseCallback("Select Watermark (Press ESC to confirm)", mouse_callback)
        
        # 等待用户操作（按ESC键确认）
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC键
                break
        
        # 关闭窗口
        cv2.destroyAllWindows()

        # 校验框选坐标（防止用户未框选）
        if len(roi) != 4:
            raise ValueError("未框选水印区域，请重新操作！")
        
        # 生成掩码：框选区域设为白色（255），其余为黑色（0）
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        cv2.rectangle(mask, (roi[0], roi[1]), (roi[2], roi[3]), 255, -1)
        
        return mask
    # ====================== 新方法插入位置 END ======================

    def remove_watermark(self, img_path: str, output_path: str, watermark_mask_path: str = None) -> bool:
        """
        去除图片水印
        :param img_path: 输入图片路径
        :param output_path: 输出图片路径
        :param watermark_mask_path: 水印掩码路径（若为None，自动检测文字水印）
        :return: 成功返回True，失败返回False
        """
        try:
            # 1. 读取图片
            img = cv2.imread(img_path)
            if img is None:
                raise FileNotFoundError(f"无法读取图片：{img_path}")
            img_copy = img.copy()

            # 2. 生成水印掩码（两种模式：手动掩码/自动检测）
            if watermark_mask_path:
                mask = cv2.imread(watermark_mask_path, 0)  # 灰度图读取掩码
            else:
                # 优化后的自动检测逻辑（效果更好）
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (5, 5), 0)  # 高斯模糊降噪
                # 自适应阈值二值化（突出文字水印）
                mask = cv2.adaptiveThreshold(
                    gray, 255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY_INV,
                    blockSize=15,
                    C=3
                )
                # 膨胀操作：让水印区域更完整
                kernel = np.ones((3, 3), np.uint8)
                mask = cv2.dilate(mask, kernel, iterations=2)

            # 3. 图像修复（核心步骤：调用OpenCV的inpaint算法）
            result = cv2.inpaint(img_copy, mask, self.inpaint_radius, cv2.INPAINT_TELEA)

            # 4. 保存结果
            cv2.imwrite(output_path, result)
            return True
        except Exception as e:
            print(f"去水印失败：{str(e)}")
            return False