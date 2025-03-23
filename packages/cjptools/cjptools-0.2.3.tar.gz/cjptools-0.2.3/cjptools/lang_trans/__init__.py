import warnings
import argparse

reqs = ['opencc-python-reimplemented']
try:
    import opencc


    def simple2tradition(input_file, output_file):
        converter = opencc.OpenCC('s2t')

        # 读取文件内容
        with open(input_file, 'r', encoding='utf-8') as fin:
            content = fin.read()

        # 转换简体到繁体
        converted_content = converter.convert(content)

        # 写入转换后的内容到文件
        with open(output_file, 'w', encoding='utf-8') as fout:
            fout.write(converted_content)


    def simple2tradition_main():
        parser = argparse.ArgumentParser(description='Convert Simplified Chinese text to Traditional Chinese.')
        parser.add_argument('input_file', type=str, help='Path to the input file')
        args = parser.parse_args()
        simple2tradition(args.input_file, args.input_file)
        print(f"转换完成！已将简体字转换为繁体字并保存到 {args.input_file}")


except ImportError:
    warnings.warn(
        "opencc 未安装。请使用以下命令安装：\n"
        "pip install opencc-python-reimplemented\n",
        UserWarning
    )
