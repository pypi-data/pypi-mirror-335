import re
import argparse


def clean_html(html_path):
    with open(html_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    match = re.search(r'<meta property="og:url" content="(https://ar5iv\.labs\.arxiv\.org/html/\d+\.\d+)">',
                      html_content)
    if match:
        arxiv_url = match.group(1)
    else:
        # 如果没有找到meta标签，尝试查找<base>标签
        base_match = re.search(r'<base href="/html/(\d+\.\d+v\d+)/">', html_content)
        if base_match:
            base_href = base_match.group(1)
            arxiv_url = f"https://arxiv.org/html/{base_href}"
        else:
            print("Neither 'og:url' nor 'base href' were found in the HTML.")
            return
    # 替换 HTML 中的特定 URL 部分
    new_html_content = html_content.replace('<base href=".">', "") \
        .replace(f"{arxiv_url}?_immersive_translate_auto_translate=1#", f"#") \
        .replace(f"{arxiv_url}#", f"#")

    # 将修改后的 HTML 内容写回文件
    with open(html_path, 'w', encoding='utf-8') as file:
        file.write(new_html_content)

    print("HTML processing completed.")


def clean_html_main():
    parser = argparse.ArgumentParser(description='清洗arxiv的html代码，使其中的链接保持正确.')
    parser.add_argument('input_file', type=str, help='Path to the input file')
    args = parser.parse_args()
    clean_html(args.input_file)
    print(f"清洗完成！已将arxiv的html代码保存至 {args.input_file}")
