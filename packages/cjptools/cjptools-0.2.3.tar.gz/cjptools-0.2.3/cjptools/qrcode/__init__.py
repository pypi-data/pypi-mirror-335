
import warnings
import argparse

reqs = ['Pillow', 'qrcode']
try:
    import qrcode


    def gen(data, filename='qrcode.png', **params):
        # Create a QR code instance
        qr = qrcode.QRCode(**params)

        # Add the URL data to the QR code
        qr.add_data(data)
        qr.make(fit=True)

        # Create an image from the QR code instance
        img = qr.make_image(fill='black', back_color='white')
        # Save the image to a file
        img.save(filename)
        print(f"QR code generated and saved as {filename}")


    def gen_main():

        parser = argparse.ArgumentParser(description='生成二维码.')
        parser.add_argument('data', type=str, help='输入文本文件的路径')
        parser.add_argument('-o', '--output_file', type=str, required=True, help='输出文本文件的路径')

        args = parser.parse_args()

        gen(args.data, args.output_file)
        print(f"二维码生成完成！已将文本 `{args.data}` 生成二维码并保存至 {args.output_file}")

except ImportError:
    warnings.warn(
        "qrcode 未安装。请使用以下命令安装：\n"
        "pip install qrcode\n",
        UserWarning
    )
