import pandas as pd

from utils.ocr_utils import PaddleOCRUtils

if __name__ == '__main__':
    image_path = "D:/phone_number.png"
    ocr_flag, ocr_data = PaddleOCRUtils.image_ocr2(image_path)
    print(ocr_flag)
    print(ocr_data)

    df = pd.DataFrame(ocr_data)

    # 设置列顺序（可选）
    column_order = ['name', 'phone_number', 'money']
    df = df[column_order]
    header = {
        "name": "姓名",
        "phone_number": "手机号码",
        "money": "金额"
    }
    df.rename(columns=header, inplace=True)

    excel_file_path = "D:/user_data.xlsx"


    # 导出到Excel文件
    df.to_excel(excel_file_path,
                index=False,
                engine='openpyxl')

    print("Excel文件导出完成！")