import argparse
import os
import cv2
from remover import WatermarkRemover

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="图片去水印工具（CLI版）")
    parser.add_argument("-i", "--input", required=True, help="输入图片路径（如：examples/test.jpg）")
    parser.add_argument("-o", "--output", default="output.jpg", help="输出图片路径（默认：output.jpg）")
    parser.add_argument("-m", "--mask", help="水印掩码路径（可选，自动检测时无需填写）")
    parser.add_argument("--manual", action="store_true", help="手动框选水印区域（优先级高于自动检测）")
    args = parser.parse_args()

    # 执行去水印
    remover = WatermarkRemover()
    # 优先处理批量文件夹
    if args.dir:
        # 校验文件夹是否存在
        if not os.path.isdir(args.dir):
            print(f"错误：文件夹 {args.dir} 不存在！")
            return
        
        # 定义支持的图片格式
        supported_formats = ('.jpg', '.jpeg', '.png', '.bmp')
        # 遍历文件夹内所有文件
        file_list = [f for f in os.listdir(args.dir) if f.lower().endswith(supported_formats)]
        
        if not file_list:
            print(f"警告：文件夹 {args.dir} 内无支持的图片文件（仅支持{supported_formats}）！")
            return
        
        # 批量处理每个图片
        print(f"开始批量处理，共 {len(file_list)} 张图片...")
        for idx, fname in enumerate(file_list):
            # 拼接完整的输入/输出路径
            img_path = os.path.join(args.dir, fname)
            # 输出文件名：原文件名前加"processed_"
            output_fname = f"processed_{fname}"
            output_path = os.path.join(args.dir, output_fname)
            
            try:
                if args.manual:
                    # 手动框选模式（批量时每张图都需要手动框选）
                    mask = remover.select_watermark_by_mouse(img_path)
                    temp_mask_path = "temp_mask.png"
                    cv2.imwrite(temp_mask_path, mask)
                    success = remover.remove_watermark(img_path, output_path, temp_mask_path)
                    os.remove(temp_mask_path)
                else:
                    # 自动检测模式
                    success = remover.remove_watermark(img_path, output_path, args.mask)
                
                if success:
                    print(f"[{idx+1}/{len(file_list)}] 成功：{fname} → {output_fname}")
                else:
                    print(f"[{idx+1}/{len(file_list)}] 失败：{fname}")
            except Exception as e:
                print(f"[{idx+1}/{len(file_list)}] 异常：{fname} → {str(e)}")
        
        print("批量处理完成！结果已保存至原文件夹，文件名前缀为processed_")
        return  # 批量处理完成后，直接退出，不执行后续单文件逻辑
    # ====================== 批量逻辑插入位置 END ======================

    # 单文件处理逻辑（仅当未传-d参数时执行）
    if not args.input:
        print("错误：未传入输入图片！批量处理请用 -d 文件夹路径，单文件请用 -i 图片路径")
        return
    try:
        if args.manual:
            # 手动框选水印生成掩码
            mask = remover.select_watermark_by_mouse(args.input)
            # 用手动生成的掩码去水印
            success = remover.remove_watermark(args.input, args.output, watermark_mask_path=None)
            # 注意：这里直接传入生成的mask会报错，需要临时保存掩码文件
            # 补充：修复手动框选的调用逻辑（保存临时掩码）
            temp_mask_path = "temp_mask.png"
            cv2.imwrite(temp_mask_path, mask)
            success = remover.remove_watermark(args.input, args.output, temp_mask_path)
            # 删除临时掩码文件
            os.remove(temp_mask_path)
        else:
            # 自动检测/手动传入掩码
            success = remover.remove_watermark(args.input, args.output, args.mask)
        
        if success:
            print(f"成功！结果已保存至：{args.output}")
        else:
            print("失败！请检查输入参数或图片路径。")
    except Exception as e:
        print(f"操作失败：{str(e)}")

if __name__ == "__main__":
    main()